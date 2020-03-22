
class ModelExecutionContext: 
    """ 
    This class represents the execution context of a model. 
    It will contain information like correlation id, etc... that the model might need to use during 
    execution.
    """
    
    def __init__(self, correlation_id, process, online=False):
        """
        Initializes the context

        Parameters
        ----------
        correlation_id (str)
            The correlation id of the execution

        process (str)
            A label specifying which process it is. 
            Typical labels would be: 'TRAINING', 'PREDICT', 'SCORE', 'INIT'
            This information is typically attached to the logs for better readability

        online (bool, default False)
            Specifies if the execution of this model is part of an "online" context, 
            meaning that the caller is waiting for a response from the model. 
            Default to False, which means that the caller will not wait for the model to 
            perform its task
        """
        self.correlation_id = correlation_id
        self.online = online
        self.process = process
