import os
import time

from flask import Flask, jsonify, request, Response

from toto_pubsub.consumer import TotoEventConsumer
from toto_pubsub.publisher import TotoEventPublisher
from toto_logger.logger import TotoLogger

from totoml.remote.totoml_registry import TotoMLRegistry
from totoml.remote.gcpstorage import GCPStorage
from totoml.model import Model
from totoml.context import ModelExecutionContext
from totoml.cid import cid
from totoml.concurrent import ConcurrencyHelper

logger = TotoLogger()

class ModelController: 
    """
    This class controls a model and acts as a proxy for all operations 
    regarding a model 
    """

    def __init__(self, model_delegate, flask_app, config): 
        """
        Initializes the controller

        Parameters
        ----------
        flask_app (Flask)
            The flask app
        
        model_delegate (ModelDelegate)
            A instance of delegate.ModelDelegate that provides the implementation of the 
            needed functions (predict, etc... )

        config (ControllerConfig)
            A configuration object 
            Must be an instance of config.ControllerConfig
                
        """
        # Variable initializations
        self.model_delegate = model_delegate
        self.ms_name = 'model-{}'.format(self.model_delegate.get_name())

        # Generate a correlation ID for all init operations
        correlation_id = cid()
        
        ctx = ModelExecutionContext(correlation_id, 'INIT')

        # Make sure that the folder structure is there
        self.model_folder = "{bf}/{model}".format(bf=os.environ['TOTO_TMP_FOLDER'], model=self.model_delegate.get_name())
        self.champion_folder = "{model_folder}/champion".format(model_folder=self.model_folder)
        os.makedirs(name=self.champion_folder, exist_ok=True)

        # Load the model information from Toto ML Registry API
        # Check if the model exists on the registry. 
        # If it does not, create it.
        registry = TotoMLRegistry(ctx)

        model_info = registry.get_model_info(self.model_delegate.get_name())

        if model_info is None: 
            model_info = registry.create_model(self.model_delegate.get_name())

        # Check if there's a champion model (pickle file, other files, ...) published on GCP Storage
        # If there's no model, upload the default model (local)
        # If there's no local model, train the model and upload the files
        storage = GCPStorage(ctx)

        model_files = storage.load_champion_model(model_info, self.champion_folder)

        if model_files is None: 

            lock = ConcurrencyHelper(self.model_folder)

            # Make sure there's not another python process doing the training
            # Check for the semaphore
            if lock.lock():
                # Train
                trained_model = self.model_delegate.train(model_info, ctx)

                # Upload 
                storage.save_champion_model(model_info, trained_model)

                # Update the champion model metrics
                registry.put_champion_metrics(model_info['name'], trained_model.score)
                
                # Delete all the files : trained_model_files and trainining_data_files
                trained_model.delete_files(ctx)

                # Release the lock
                lock.release()

            else: 
                # Wait till there is no lock file
                while not lock.lock(): 
                    logger.compute(ctx.correlation_id, '[ {context} ] - Waiting 30 seconds for other process to complete'.format(context=ctx.process), 'info')
                    time.sleep(30)

                lock.release()

                logger.compute(ctx.correlation_id, '[ {context} ] - Waiting complete: loading champion model files'.format(context=ctx.process), 'info')

            # Reload the files
            model_files = storage.load_champion_model(model_info, self.champion_folder)
 
        # Build the model object
        self.model = Model(model_info, model_files)

        # Event Consumers
        listen_topics = [ '{model}-train'.format(model=model_info['name']) ]
        listeners = [ self.train ]
        
        # Listen to Batch prediction events
        if config.enable_batch_predictions_events: 
            listen_topics.append('{model}-predict-batch'.format(model=model_info['name']))
            listeners.append(self.predict_batch)

        # Listen to Single prediction events
        if config.enable_single_prediction_events: 
            listen_topics.append('{model}-predict-single'.format(model=model_info['name']))
            listeners.append(self.predict)

        # Listen to Model Promotions
        if config.listen_to_promotions:
            listen_topics.append('toto-ml-model-promoted'.format(model=model_info['name']))
            listeners.append(self.promote)

        TotoEventConsumer(self.ms_name, listen_topics, listeners)

        # Event Publishers
        self.publisher_model_train = TotoEventPublisher(microservice=self.ms_name, topics=['{model}-train'.format(model=model_info['name'])])

        # APIs
        @flask_app.route('/')
        def smoke():
            return jsonify({ "api": self.ms_name, "status": "running" })

        @flask_app.route('/train', methods=['POST'])
        def train(): 

            # Topic to which the train message will be pushed
            topic = '{model}-train'.format(model=model_info['name'])
            event = {"correlationId": request.headers['x-correlation-id']}

            # Start the training
            self.publisher_model_train.publish(topic=topic, event=event)

            # Answer
            resp = jsonify({"message": "Training process started"})
            resp.status_code = 200
            resp.headers['Content-Type'] = 'application/json'

            return resp

        @flask_app.route('/score', methods=['GET'])
        def score(): 

            resp = jsonify(self.score(request))
            resp.status_code = 200
            resp.headers['Content-Type'] = 'application/json'

            return resp

        @flask_app.route('/predict', methods=['POST'])
        def predict(): 

            data = request.json
            correlation_id = request.headers['x-correlation-id']

            resp = jsonify(self.predict(data, correlation_id, online=True))
            resp.status_code = 200
            resp.headers['Content-Type'] = 'application/json'

            return resp


    def train(self, request=None): 
        """
        Retrains the model 
        """
        correlation_id = cid()

        if request is not None and 'correlationId' in request: 
            correlation_id = request['correlationId']

        ctx = ModelExecutionContext(correlation_id, 'TRAINING')

        # Trigger the training process
        retrained_model = self.model_delegate.train(self.model.info, ctx)

        # Save all the trained model files
        GCPStorage(ctx).save_retrained_model(self.model.info, retrained_model)

        # Publish the trained model on the Toto ML Registry
        TotoMLRegistry(ctx).post_retrained_model(self.model.info['name'], retrained_model.score)

        # Delete all the files : trained_model_files and trainining_data_files
        retrained_model.delete_files(ctx)

        return {"success": True, "message": "Model {} trained successfully".format(self.model.info['name'])}

    def score(self, request=None): 
        """
        Calculate the accuracy (metrics) of the champion model
        """
        correlation_id = cid()

        if request is not None and 'x-correlation-id' in request.headers: 
            correlation_id = request.headers['x-correlation-id']

        ctx = ModelExecutionContext(correlation_id, 'SCORING')
        
        score = self.model_delegate.score(self.model, ctx)

        # Post the updated metrics
        TotoMLRegistry(ctx).put_champion_metrics(self.model.info['name'], score.score)

        # Delete files
        score.delete_files(ctx)
        
        return {"metrics": score.score}

    def predict(self, data, correlation_id=None, online=False):
        """
        Predicts on a single item
        """
        if correlation_id is None and 'correlationId' in data: 
            correlation_id = data['correlationId']
        else: 
            correlation_id = cid()

        return self.model_delegate.predict(self.model, ModelExecutionContext(correlation_id, 'PREDICT', online=online), data)
    
    def predict_batch(self, data=None):
        """
        Predicts on a batch of items
        """
        if data is not None and 'correlationId' in data: 
            correlation_id = data['correlationId']
        else: 
            correlation_id = cid()

        self.model_delegate.predict_batch(self.model, ModelExecutionContext(correlation_id, 'PREDICT BATCH'), data=data)

    def promote(self, request=None): 
        """
        Promotes the last retrained model to Champion!
        """
        # 1. Check that the promote event is actually for this model
        if request['modelName'] != self.model_delegate.get_name(): 
            return

        correlation_id = cid()

        if request is not None and 'correlationId' in request: 
            correlation_id = request['correlationId']

        ctx = ModelExecutionContext(correlation_id, 'PROMOTE')

        logger.compute(correlation_id, '[ {c} ] - Model {m} has been promoted. Reloading the model.'.format(c=ctx.process, m=request['modelName']), 'info')

        # 2. Get the updated model info
        model_info = TotoMLRegistry(ctx).get_model_info(self.model_delegate.get_name())

        # 3. Reload the model
        model_files = GCPStorage(ctx).load_champion_model(model_info, self.champion_folder)

        self.model = Model(model_info, model_files)

        logger.compute(correlation_id, '[ {c} ] - Model {m} has been reloaded after promotion. New version: {mod}.v{v}'.format(c=ctx.process, m=request['modelName'], mod=self.model.info['name'], v=self.model.info['version']), 'info')

        

