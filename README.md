# TotoML Python SDK
This library is an SDK for Toto ML

This library provides the following key components: 

**Model Controller**: the Model Controller is a wrapper for your models. It provides:
 * REST APIs to trigger the training, scoring and predictions
 * Event-based access to the same (training, scoring, predicting)

## How to use it
In your main python file (e.g. app.py), import the `ModelController` and `ControllerConfig` classes, create a Flask app, instantiate your model (in this example `ERCBOD()`) and pass it to the ModelController constructor. 
```
from totoml.controller import ModelController
from totoml.config import ControllerConfig

app = Flask(__name__)

model_controller = ModelController(ERCBOD(), app, ControllerConfig(enable_batch_predictions_events=False, enable_single_prediction_events=False))

```

In order for the Model Controller to work, you have to provide to it your model (in the example `ERBOCD()`): that's called here a Model Delegate. <br/>

`ModelDelegate` is an **abstract class** provided by this SDK (`delegate.ModelDelegate`). Your model has to implement its methods. <br/>
Those methods are: 
> `get_name()` <br/>
This method has to return the name of the model. This is very important because the name of the model is used for everything in TotoML (internal folders, registry, file storage, etc..), so the name **has to be unique**. 

> `get_model_type()` <br/>
Not very used for now. Should return the type of model: sklearn, tf, etc.. <br/>
Has to be an instance of ModelType

> `predict()` and `predict_batch()` <br>
These methods perform predictions.

> `score()` <br>
This method scores the current champion model: it has to recalculate the metrics for the model and return them 

> `train()` <br>
This method performs the training of the model and returns the trained model and all the associated files.<br/>
It's important to note that also any file containing training data or built features should be returned, so that Toto ML can grant the persistence of those files and make sure there is lineage.





