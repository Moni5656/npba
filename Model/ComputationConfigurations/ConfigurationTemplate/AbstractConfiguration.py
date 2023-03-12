import uuid

from Model.Subject import Subject


class AbstractConfiguration(Subject):

    def __init__(self, group_id, model, associated_component, uid=None):
        super().__init__()
        if uid is None:
            uid = uuid.uuid4()
        self.id = uid
        self.group_id = group_id
        self.model = model
        self.associated_component = associated_component

    def make_parameter_dict(self) -> dict:
        """
        Returns a dictionary of the configuration parameters to display in the application.

        :return: configuration parameter dictionary
        """
        return {"id": str(self.id), "group id": str(self.group_id)}

    def update_parameter_dict(self, dictionary: dict):
        """
        Updates the configuration parameter values using the same keys as in make_parameter_dict

        :param dictionary: configuration parameter dictionary
        """
        pass

    def to_serializable_dict(self) -> dict:
        """
        Returns a serializable configuration dictionary.

        :return: configuration dictionary
        """
        return {"id": str(self.id), "group_id": str(self.group_id)}

    @staticmethod
    def to_constructor_dict(json_dict: dict, model, associated_component) -> dict:
        """
        Creates a dictionary that has the same keys as the constructor. Counterpart of to_serializable_dict.

        :param json_dict: a dictionary created by to_serializable_dict()
        :param model: model object
        :param associated_component: the network component, the configuration is associated to
        :return: a dictionary which can be passed to the constructor of a configuration class
        """
        group_id = uuid.UUID(json_dict["group_id"])
        uid = uuid.UUID(json_dict["id"])
        return {"group_id": group_id, "uid": uid, "model": model,
                "associated_component": associated_component}
