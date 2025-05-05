# Standard library imports
from abc import ABC, abstractmethod

# Third-party imports

# Local application imports
from .utils import *
from .store import BaseStore


# Define an abstract class
class AbstractProject(ABC):

    def __init__(self):
        """ """

    # @abstractmethod
    # def open_project(self):
    #    """ Open an existing {Project} """

    @abstractmethod
    def close_project(self):
        """Close the current {Project}"""

    @abstractmethod
    def create_trial(self):
        """Create a new {Trial} for this {Project}"""

    @abstractmethod
    def delete_trial(self):
        """Delete an existing {Trial} from this {Project}"""

    @abstractmethod
    def open_trial(self):
        """Open an existing {Trial} from this {Project}"""

    @abstractmethod
    def close_trial(self):
        """Close the current {Trial} from this {Project}"""


class BaseProject(AbstractProject):
    """
    Manages high level administrative tasks for a Project.

    ABC Required methods:
        close_project
        open_store
        create_trial
        open_trial
        close_trial
        delete_trial

    Attributes:
        project_stores:     Dictionary mapping {store-name} to {Store} object.
        instance_id:        Currently active {instance_id}

    Methods:

    """

    def __init__(self, exchange_home, project_name, available_stores):

        # instance attributes
        self.project_stores = {}
        self.trials_dict = {}
        self.instance_id = ""

        self.prefix_dict = {"prefix-instance": "TRIAL", "prefix-object": "OBJECT"}

        # (THESE ARE SET BY {PROJECT} WHEN CREATING NEW STORE OBJECT)
        self.exchange_home = exchange_home
        self.project_name = project_name
        self.available_stores = available_stores

        self.add_stores(self.available_stores)

    # ABC Methods
    # ----------------------------------------
    def close_project(self) -> bool:

        # make sure all of it's {Stores} are closed
        # make sure all of it's {Trials} are saved

        # Retrun True so that Exchange knows its closed and can destroy the {Projec} object
        return True

    def open_store(self, store_name):

        pass

    def create_trial(self):

        instance_id = create_unique_name("TRIAL")
        self.trials_dict[instance_id] = {}
        self.instance_id = instance_id

    def open_trial(self, instance_id):
        self.instance_id = instance_id

    def close_trial(self):
        self.instance_id = None

    def delete_trial(self, instance_id):
        del self.trials_dict[instance_id]

    # Methods
    # ----------------------------------------
    def add_stores(self, store_name_list):

        for store_name in store_name_list:

            store_directory = self.get_store_directory(store_name)
            settings = self.prefix_dict

            new_store = BaseStore()
            new_store.open_store(store_directory, self.project_name, settings)

            self.project_stores[store_name] = new_store

    # Directory Methods
    # ----------------------------------------
    def get_store_directory(self, store_name: str = "") -> str:

        return f"{self.exchange_home}/{store_name}"

    def store_objects(self, store_name, object_dict):

        project_store = self.project_stores[store_name]
        project_store.store_objects(self.instance_id, object_dict)
