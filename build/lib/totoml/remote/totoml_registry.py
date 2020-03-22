import os 
import requests
import datetime
from toto_logger.logger import TotoLogger
from random import randint

toto_auth = os.environ['TOTO_API_AUTH']
toto_host = os.environ['TOTO_HOST']

logger = TotoLogger()

class TotoMLRegistry: 

    def __init__(self, context): 
        self.correlation_id = context.correlation_id
        self.context = context

    def get_model_info(self, model_name): 
        """
        Retrieves the meta information on the model and returns it. 

        Parameters
        ----------
        model_name : str
            The name of the model

        Returns
        -------
        dict
            a dictionnary representing the model's meta information, among which "name" (str), "version" (int), "date" (str) and "metrics" (list)
        """
        logger.compute(self.correlation_id, '[ {process} ] - Retrieving model [{model}] from Toto ML Model Registry'.format(process=self.context.process, model=model_name), 'info')
        
        response = requests.get(
            'https://{host}/apis/totoml/registry/models/{name}'.format(host=toto_host, name=model_name),
            headers={
                'Accept': 'application/json',
                'Authorization': toto_auth,
                'x-correlation-id': self.correlation_id
            }
        )

        model = response.json()

        if not model: 
            return None

        return model

    def create_model(self, model_name): 
        """
        Creates a new model on the TotoML Registry

        Parameters
        ----------
        model_name : str
            The name of the model

        Returns
        -------
        dict
            a dictionnary representing the created model's meta information, among which "name" (str), "version" (int), "date" (str) and "metrics" (list)
        """
        model = {
            "name": model_name
        }

        logger.compute(self.correlation_id, '[ {process} ] - Creating model [{model}] in Toto ML Model Registry'.format(process=self.context.process, model=model_name), 'info')

        response = requests.post(
            'https://{host}/apis/totoml/registry/models'.format(host=toto_host),
            headers={
                'Accept': 'application/json',
                'Authorization': toto_auth,
                'x-correlation-id': self.correlation_id
            }, 
            json=model
        )

        if response.status_code != 201: 
            logger.compute(self.correlation_id, '[ {process} ] - Something went wrong when creating a new model on Toto ML Model Registry. Response: {content}'.format(process=self.context.process, content=response.content), 'error')
        else: 
            logger.compute(self.correlation_id, '[ {process} ] - Model [{model}] created in Toto ML Model Registry'.format(process=self.context.process, model=model_name), 'info')
            return response.json()

    def post_retrained_model(self, model_name, metrics): 
        """
        Posts a new retrained model to Toto ML Registry for a given model

        Parameters
        ----------
        model_name (str)
            The name of the model

        metrics (list)
            List of metrics
            Each metric is a dict {"name": <name of metric>, "value": <value>}

        """
        response = requests.post(
            'https://{host}/apis/totoml/registry/models/{model}/retrained'.format(host=toto_host, model=model_name),
            headers={
                'Accept': 'application/json',
                'Authorization': toto_auth,
                'x-correlation-id': self.correlation_id
            }, 
            json={
                "metrics": metrics
            }
        )

        if response.status_code != 201: 
            logger.compute(self.correlation_id, '[ {process} ] - [ POSTING ] - Something went wrong when creating a new retrained model on Toto ML Model Registry for model {model}. Response: {content}'.format(process=self.context.process, model=model_name, content=response.content), 'error')

        logger.compute(self.correlation_id, '[ {process} ] - [ POSTING ] - Posted retrained model'.format(process=self.context.process), 'info')

        return

    def put_champion_metrics(self, model_name, metrics): 
        """
        Updates the metrics of the chamption model 

        Parameters
        ----------
        model_name (string)
            The name of the models

        metrics (list)
            A list [] of metrics object. 
            Each metric is a {name: <name>, value: <value>} object
        """
        response = requests.post(
            'https://{host}/apis/totoml/registry/models/{model}/metrics'.format(host=toto_host, model=model_name),
            headers={
                'Accept': 'application/json',
                'Authorization': toto_auth,
                'x-correlation-id': self.correlation_id
            }, 
            json={
                "metrics": metrics
            }
        )

        if response.status_code != 201: 
            logger.compute(self.correlation_id, '[ {process} ] - [ POSTING ] - Something went wrong when updating the metrics on Toto ML Model Registry for model {model}. Response: {content}'.format(process=self.context.process, model=model_name, content=response.content), 'error')

        logger.compute(self.correlation_id, '[ {process} ] - [ POSTING ] - Updated metrics of champion model'.format(process=self.context.process), 'info')

        return 
