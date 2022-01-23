from gensim.models.callbacks import CallbackAny2Vec
import logging

logger = logging.getLogger(__name__)


class MonitorCallback(CallbackAny2Vec):
    def __init__(self):
        self._epoch: int = 0

    def on_epoch_end(self, model):
        self._epoch += 1
        logger.info(f"(Epoch {self._epoch}) Model loss: {model.get_latest_training_loss()}")
