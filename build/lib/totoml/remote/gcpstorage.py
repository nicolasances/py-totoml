import os
import uuid

from google.cloud import storage
from google.api_core.exceptions import NotFound

from toto_logger.logger import TotoLogger

client = storage.Client()

toto_env = os.environ['TOTO_ENV']

bucket_name = 'toto-{env}-model-storage'.format(env=toto_env)

logger = TotoLogger()

class GCPStorage: 
    """
    This class is a proxy to GCP Storage
    """
    def __init__(self, context): 
        self.correlation_id = context.correlation_id
        self.context = context

    def load_champion_model(self, model_info, champion_folder): 
        """ 
        Loads the champion model files from the bucket

        Parameters
        ----------
        model_info (dict)
            Contains the "name" and "version" of the model
            Used to look for the model pickle file

        Returns
        -------
        model_files (dict)
            A dictionnary that contains all the files for the champion model
            Files can be the trained model file, scalers, vectorizers, etc.
            The structure of this dict follows the spec from model.Model (see the __ini__() method)

        champion_folder (str)
            The path of the local folder where the champion model's files have to be stored

        """
        try:
            bucket = client.get_bucket(bucket_name)
        except NotFound: 
            logger.compute(self.correlation_id, '[ {ctx} ] - Bucket {b} not found. Please create it first'.format(ctx=self.context.process, b=bucket_name), 'error')
            return

        model_files = {}

        # Iterate over all elements in the 
        bucket_folder = "{model}/champion/v{version}/".format(model=model_info['name'], version=model_info['version'])

        for blob in list(bucket.list_blobs(prefix=bucket_folder)): 

            # Skipping files in the "training-data" folder
            if "/training-data/" in blob.name: continue
            
            filename = blob.name[blob.name.rfind('/')+1:]

            logger.compute(self.correlation_id, '[ {ctx} ] - Loading model file from bucket: {blob}'.format(ctx=self.context.process, blob=blob.name), 'info')

            target_file = "{folder}/{file}".format(folder=champion_folder, file=filename)

            blob.download_to_filename(target_file)

            model_files[blob.name[len(bucket_folder):]] = target_file

        if model_files: return model_files
            
        return None

    def save_champion_model(self, model_info, trained_model):
        """
        Save the model champion's files on Storage
        Files can typically be: 
        - trained model, for example the pickle file deriving from the fitting 
        - vectorizers or scalers fit on the data used for training
        - categorical data, saved to be used in the prediction 
        - training data, saved for reference 
        
        Parameters
        ----------
        model_info (dict)
            Contains the "name" and "version" of the model
            Used to look for the model pickle file

        trained_model (model.TrainedModel)
            A trained model to save as the champion model
            See model.TrainedModel for the spec

        """
        try:
            bucket = client.get_bucket(bucket_name)
        except NotFound: 
            logger.compute(correlation_id, '[ {ctx} ] - Bucket {b} not found. Please create it first'.format(ctx=self.context.process, b=bucket_name), 'error')
            return

        # Define the path of where to save the files 
        path = "{model}/champion/v{version}".format(model=model_info['name'], version=model_info['version'])

        # Save the files
        self.__save_model_files(trained_model, bucket, path)

    def save_retrained_model(self, model_info, trained_model):
        """
        Save the retrained model's files on Storage
        Files can typically be: 
        - trained model, for example the pickle file deriving from the fitting 
        - vectorizers or scalers fit on the data used for training
        - categorical data, saved to be used in the prediction 
        - training data, saved for reference 
        
        Parameters
        ----------
        model_info (dict)
            Contains the "name" and "version" of the model
            Used to look for the model pickle file

        trained_model (model.TrainedModel)
            A trained model to save as the champion model
            See model.TrainedModel for the spec

        """
        try:
            bucket = client.get_bucket(bucket_name)
        except NotFound: 
            logger.compute(correlation_id, '[ {ctx} ] - Bucket {b} not found. Please create it first'.format(ctx=self.context.process, b=bucket_name), 'error')
            return

        # Define the path of where to save the files 
        path = "{model}/retrained".format(model=model_info['name'])

        # Save the files
        self.__save_model_files(trained_model, bucket, path)

            
    def __save_model_files(self, trained_model, bucket, base_gcp_path):
        """
        This private method holds the common logic of saving a model's files to GCP Storage buckets.
        It holds the logic of the structure of the folders. 

        Parameters
        ----------
        trained_model (model.TrainedModel)
            A trained model to save as the champion model
            See model.TrainedModel for the spec

        bucket (GCP bucket)
            The GCP bucket where the files need to be stored

        base_gcp_path (str)
            The path where the files should be stored. 
            E.g. champion files would be stored under {model}/champion/v{version}/
            E.g. retrained model files would be under {model}/retrained/

        """
        # Save the objects
        for obj_name, obj_filepath in trained_model.trained_model_files.items(): 

            # Create the object
            bucket_objname = "{base_gcp_path}/{obj_name}".format(base_gcp_path=base_gcp_path, obj_name=obj_name)
            bucket_obj = bucket.blob(bucket_objname)

            # Upload the file to the bucket
            bucket_obj.upload_from_filename(obj_filepath)

            logger.compute(self.correlation_id, '[ {ctx} ] - File uploaded under [ {path} ]: {obj_name}'.format(ctx=self.context.process, path=base_gcp_path, obj_name=obj_name), 'info')

        # Save the training data files
        for filepath in trained_model.training_data_files: 
            # Get the name of the file
            filename = filepath[filepath.rfind('/')+1:]

            # Create the object
            bucket_objname = "{base_gcp_path}/training-data/{filename}".format(base_gcp_path=base_gcp_path, filename=filename)
            bucket_obj = bucket.blob(bucket_objname)

            # Upload the file
            bucket_obj.upload_from_filename(filepath)

            logger.compute(self.correlation_id, '[ {ctx} ] - Training data file uploaded under [ {path}/training-data ]: {obj_name}'.format(ctx=self.context.process, path=base_gcp_path, obj_name=filename), 'info')


