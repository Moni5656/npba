from abc import ABC

from View import Observer


class Subject(ABC):

    def __init__(self):
        self.subscribers = list()

    def subscribe(self, observer: Observer):
        """
        Can be used to subscribe to a subject.

        :param observer: object wanting to subscribe to the subject
        """
        self.subscribers.append(observer)

    def unsubscribe(self, observer: Observer):
        """
        Can be used to unsubscribe from a subject.

        :param observer: object wanting to unsubscribe from a subject
        """
        self.subscribers.remove(observer)

    def notify(self, updated_component):
        """
        Notifies all subscribers about a change.

        :param updated_component: updated component
        """
        for subscriber in list(self.subscribers):
            subscriber.update_(updated_component)

    def __getstate__(self):
        """
        Used to pickle the object for process communication.

        :return: a dictionary of the subject without the subscribers
        """
        attributes = self.__dict__.copy()
        if "subscribers" in attributes:
            del attributes["subscribers"]
        return attributes
