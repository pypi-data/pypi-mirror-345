# Standard library imports
from abc import ABC, abstractmethod

# Third-party imports

# Local application imports
from .utils import *


# Define an abstract class
class AbstractStore(ABC):

    def __init__(self):
        """ """

    @abstractmethod
    def open_store(self):
        """Open an existing {Store}"""

    @abstractmethod
    def close_store(self):
        """Close the current {Store}"""

    @abstractmethod
    def open_database(self):
        """Open / Create database for this {Store}"""

    @abstractmethod
    def close_database(self):
        """Close current database for this {Store}"""

    @abstractmethod
    def put_object(self):
        """Put object into storage"""

    @abstractmethod
    def get_object(self):
        """Get object from storage"""


class BaseStore(AbstractStore):
    """
    Manages high level administrative tasks for a store.

    ABC Required methods:
        open_store
        close_store
        open_database
        close_database
        put_object
        get_object

    Attributes:
        store_db:       TinyDB object
        store_home:     Directory where this {Store} exists


        store_prefix_instance:  prefix used for naming when creating new Instance
        store_prefix_object:    prefix used for naming when creating new Object

    Methods:
        get_database_file_path:     {store_home}/store.db
        get_object_file_path:       Path to specific Object
        get_object_directory:       Directory name of object Group

        create_id_instance:         Return unique id for Instance names
        create_id_object:           Return unique id for Object names

        db_insert_item:             Insert 1 dictionary item into {store_db}

    TODO:
        Add Query methods
    """

    def __init__(self):

        # instance attributes
        self.store_home = ""
        self.store_db = None
        self.project_name = ""

        # (THESE ARE SET BY {PROJECT} WHEN CREATING NEW STORE OBJECT)
        self.store_prefix_instance = ""
        self.store_prefix_object = ""

    # ABC Methods
    # ----------------------------------------
    def open_store(self, store_home, project_name, settings):

        # set instance attributes
        self.store_home = store_home
        self.project_name = project_name
        self.store_prefix_instance = settings.get("prefix-instance")
        self.store_prefix_object = settings.get("prefix-object")

        # open database for use
        self.open_database()

    def close_store(self) -> bool:

        # close open database
        self.close_database()

        # return True so project knows the store is closed (it can then destroy object)
        return True

    def open_database(self):

        # create/open/attach database object
        database_file_path = self.get_database_file_path()
        self.store_db = TinyDB(database_file_path)

    def close_database(self):

        # close/detach database object
        self.store_db.close()
        self.store_db = None

        pass

    def get_object(self):
        pass

    def put_object(self, obj_name, obj, instance_id):

        object_file_path = self.get_object_file_path(instance_id, obj_name)
        save_pickle(obj, object_file_path)

        object_hash = get_file_obj_hash(object_file_path)

        item = {
            "project-name": self.project_name,
            "instance_id": instance_id,
            "object-name": obj_name,
            "hash": object_hash,
        }

        self.db_insert_item(item)

    # Directory Methods
    # ----------------------------------------
    def get_database_file_path(self) -> str:

        return f"{self.store_home}/store.db"

    def get_object_directory(self, instance_id):

        return f"{self.store_home}/{self.project_name}/{instance_id}"

    def get_object_file_path(self, instance_id, object_name):

        return f"{self.store_home}/{self.project_name}/{instance_id}/{object_name}.pkl"

    # File Methods
    # ----------------------------------------

    # Database Methods
    # ----------------------------------------
    def db_insert_item(self, item: dict = {}):

        self.store_db.insert(item)

    # Methods
    # ----------------------------------------

    def create_id_object(self):
        return create_unique_name(self.store_prefix_object)

    def store_objects(self, instance_id, object_dict):

        if len(object_dict) > 0:

            for obj_name, obj in object_dict.items():

                self.put_object(obj_name, obj, instance_id)
