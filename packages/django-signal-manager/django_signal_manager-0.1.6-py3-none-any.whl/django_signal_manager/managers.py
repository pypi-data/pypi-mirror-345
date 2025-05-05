import logging
from typing import Any

from django.db.models import Model
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save

logger = logging.getLogger(__name__)


class SignalManager:
    """
    A base class for managing Django model signals.

    This manager provides structured methods for responding to Django's model signals
    (pre_save, post_save, pre_delete, and post_delete). It distinguishes between
    create and update operations and invokes the corresponding lifecycle methods.
    """

    def run(self, sender: type, instance: Model, **kwargs: Any) -> None:
        """
        Determines the signal type and calls the appropriate manager method.

        Based on the received signal (pre_save, post_save, pre_delete, post_delete),
        this method routes the execution to the appropriate manager method for either
        a new or existing instance.

        Args:
            sender (type): The model class that sent the signal.
            instance (Model): The instance of the model that is being processed.
            **kwargs (dict): Additional keyword arguments from the signal, such as the
                             signal itself and properties like 'created' for post_save.
        """
        signal_obj = kwargs.get("signal")

        if signal_obj == pre_save:
            if instance.pk is None:
                self.on_pre_create(instance, **kwargs)
            else:
                self.on_pre_update(instance, **kwargs)
        elif signal_obj == post_save:
            if kwargs.get("created", False):
                self.on_post_create(instance, **kwargs)
            else:
                self.on_post_update(instance, **kwargs)
        elif signal_obj == pre_delete:
            self.on_pre_delete(instance, **kwargs)
        elif signal_obj == post_delete:
            self.on_post_delete(instance, **kwargs)
        else:
            logger.warning("Unknown or missing signal in kwargs: %s", signal_obj)

    def on_pre_create(self, instance: Model, **kwargs: Any) -> None:
        pass

    def on_post_create(self, instance: Model, **kwargs: Any) -> None:
        pass

    def on_pre_update(self, instance: Model, **kwargs: Any) -> None:
        pass

    def on_post_update(self, instance: Model, **kwargs: Any) -> None:
        pass

    def on_pre_delete(self, instance: Model, **kwargs: Any) -> None:
        pass

    def on_post_delete(self, instance: Model, **kwargs: Any) -> None:
        pass
