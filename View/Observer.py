from abc import ABC, abstractmethod

from Model import Subject


class Observer(ABC):

    def __init__(self, observed_subject: Subject):
        self.observed_subject = observed_subject
        self.observed_subject.subscribe(self)

    @abstractmethod
    def update_(self, updated_component):
        """
        Triggered when the observed component is updated in the model. Handles any resulting changes.

        :param updated_component: information about the updated component. Tuple consisting of the component and an
         update message.
        """
        pass
