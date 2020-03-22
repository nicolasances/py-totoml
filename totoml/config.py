
class ControllerConfig: 
    """
    This class holds the Model Controller configurations
    """
    def __init__(self, enable_batch_predictions_events=True, enable_single_prediction_events=True, listen_to_promotions=True): 
        """
        Initializes the Configuration

        Parameters
        ----------
        enable_batch_predictions_events (bool, default True)
            Listens to events for a request of batch prediction

        enable_single_prediction_events (bool, default True)
            Listens to events for a request of single prediction

        listen_to_promotions (bool, default True)
            Listens to a retrained model being upgraded to champion

        """
        self.enable_batch_predictions_events = enable_batch_predictions_events
        self.enable_single_prediction_events = enable_single_prediction_events
        self.listen_to_promotions = listen_to_promotions
