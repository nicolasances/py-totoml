import shutil

from enum import Enum

class ModelType(Enum):
    sklearn = 1
    tensorflow = 2

class Model: 
    """
    This class contains the typical attributes of a model. 
    It includes metadata about the model (name, version, metrics, ...)
    It also includes model files (pickle, scaler, vectorizers, ...)

    Parameters
    ----------
    info (dict)
        Metadata on the model 
        This will be the JSON object returned by Toto ML Registry APIs
        The info dict will have to at least contain the keys "name" and "version"

    files (dict, default None)
        A dictionnary of files that might be usefull for the model
        Example: the parameters file (pickle with predict), saclers, vectorizers, etc..
        The dictionnary must be structured in the following way: 
        {
            "obj_name": <filepath>
        }
        These files will be stored under Storage with a naming convention of "obj_name.v<version>" 
        where version is the version of the model
    """
    def __init__(self, info, files=None): 
        
        # Validations
        # Info validation
        if "name" not in info: raise KeyError('Model constructor : the "info" dict requires a "name" key')
        if "version" not in info: raise KeyError('Model constructor : the "info" dict requires a "version" key')

        # Assignments
        self.info = info
        self.files = files

class TrainedModel:
    """
    This class describes a trained model. 
    It contains all the files related to the trained model (pickle, etc.. ). 
    It also contains a reference to the data that has been used to train the model. 
    It also contains the training score. IMPORTANT: this is the training score, not a test score.
    """

    def __init__(self, trained_model_files, training_data_files, score):
        """
        Initializes the trained model

        Parameters
        ----------
        trained_model_files (dict)
            A dict of objects representing the trained model. 
            For example: pickle of the trained model, vectorizers, scalers, etc.. 
            The dictionnary must be structured in the following way: 
            {
                "obj_name": <filepath>
            }
        
        training_data_files (ist)
            A list of the files used to train the model 
            That list could contain the history files but also the features files

        score (list)
            A list containing the score metrics
            Each metric is a dict {"name": <name of metric>, "value": <value>}
        
        """
        self.trained_model_files = trained_model_files
        self.training_data_files = training_data_files
        self.score = score

    def delete_files(self, context): 
        """
        Deletes all the files of this trained model
        """
        # 1. Get the root directory
        (name, filepath) = next(iter(self.trained_model_files.items()))

        folder = filepath[:filepath.rfind('/')]

        # 2. Remove the whole directory
        shutil.rmtree(folder)

class ModelScore: 
    """
    This class defines the score of a model
    """
    def __init__(self, score, files=None): 
        """
        Initializes this score

        Parmeters
        ---------
        score (list)
            A list of metrics
            Each metric is a dict formed like this {"name": <metric name>, "value": <metric value>}

        files (list, default None)
            A list of files used in the scoring process
            It's important to provide these files, in any, in order for them to be deleted 
            by the controller when the scoring process is completed
        
        """
        self.score = score
        self.files = files

    def delete_files(self, context):
        """
        Delete all the files associated with the scoring process
        """
        if self.files is None: return

        filepath = self.files[0]

        folder = filepath[:filepath.rfind('/')]

        # Delete the whole folder
        shutil.rmtree(folder)
