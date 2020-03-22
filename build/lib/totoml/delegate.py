import abc

class ModelDelegate(abc.ABC): 
    """
    This is an interface that has to be extended in order to use Toto Model Controllers
    """

    @abc.abstractmethod
    def get_name(self): 
        """
        Returns the name of the model

        Returns
        -------
        name (str)
            The name of the model
        """
        pass

    @abc.abstractmethod
    def get_model_type(self):
        """
        Returns the type of the model

        Returns 
        -------
        type (model.ModelType)
            The type of model: scikit learn model, tensor flow model, etc... 
            ModelType is an enumerated type (see model.ModelType)
        """
        pass

    @abc.abstractmethod
    def predict(self, model, context, data):
        """
        Generate a single prediction for the provided data

        Parameters
        ----------
        model (Model): 
            The model itself.
            It has to be an instance of model.Model.
            The model is an ensemble of metadata (information on the model like version, name, metrics, ...)
            and model files (pickle, scalers, vectorizers, ..)

        context (ModelExecutionContext):
            The execution context of the model.
            That includes correlation id and other contextual information that might be needed. 
            Must be an instance of context.ModelExecutionContext

        data (any):
            The data can be anything. 
            It will be passed to the model for the prediction

        Returns
        -------
        prediction (any):
            Will return the prediction, in whichever form it is provided by the actual model delegate
        """
        pass

    @abc.abstractmethod
    def predict_batch(self, model, context, data=None):
        """
        Generate a batch prediction for the provided data

        Parameters
        ----------
        model (Model): 
            The model itself.
            It has to be an instance of model.Model.
            The model is an ensemble of metadata (information on the model like version, name, metrics, ...)
            and model files (pickle, scalers, vectorizers, ..)

        context (ModelExecutionContext):
            The execution context of the model.
            That includes correlation id and other contextual information that might be needed. 
            Must be an instance of context.ModelExecutionContext

        data (any):
            The data can be anything. 
            It will be passed to the model for the prediction

        """
        pass

    @abc.abstractmethod
    def score(self, model, context):
        """
        Scores the model by calculating its metrics

        Parameters
        ----------
        model (Model): 
            The model itself.
            It has to be an instance of model.Model.
            The model is an ensemble of metadata (information on the model like version, name, metrics, ...)
            and model files (pickle, scalers, vectorizers, ..)

        context (ModelExecutionContext):
            The execution context of the model.
            That includes correlation id and other contextual information that might be needed. 
            Must be an instance of context.ModelExecutionContext

        """
        pass 

    @abc.abstractmethod
    def train(self, model_info, context):
        """
        Trains the model

        Parameters
        ----------
        model_info (dict): 
            Metadata on the model 
            This will be the JSON object returned by Toto ML Registry APIs
            The info dict will have to at least contain the keys "name" and "version"

        context (ModelExecutionContext):
            The execution context of the model.
            That includes correlation id and other contextual information that might be needed. 
            Must be an instance of context.ModelExecutionContext

        Returns
        -------
        trained_model (TrainedModel)
            An instance of model.TrainedModel
            
        """
        pass