# Standard library imports
from abc import ABC, abstractmethod

# Third-party imports

# Local application imports
from .utils import *
from .project import BaseProject


# Define an abstract class
class AbstractExchange(ABC):

    def __init__(self):
        """ """

    @abstractmethod
    def open_exchange(self):
        """Open existing or create new {Exchange}"""

    @abstractmethod
    def close_exchange(self):
        """Safely close the current {Exchange}"""

    @abstractmethod
    def create_project(self):
        """Create new {Project}"""

    @abstractmethod
    def open_project(self):
        """Return an existing {Project}"""

    @abstractmethod
    def delete_project(self):
        """Delete an existing {Project}"""

    @abstractmethod
    def create_store(self):
        """Create a new {Store}"""

    @abstractmethod
    def delete_store(self):
        """Delete an existing {Store}"""


class Exchange(AbstractExchange):
    """
    Manages high level administrative tasks for the system. It creates / delete folders
    and json files that identify and index the data stored within.

    ABC Required methods:
        open_exchange
        close_exchange
        create_project
        open_project
        delete_project
        create_store
        delete_store

    Attributes:
        home_directory:     Directory where {Exchange} will be stored.
        exchange_name:      A user specified name to identify this {Exchange}
        available_stores:   Which types of stores are available in this {Exchange}
        projects_dict:      Dictionary mapping {project_name} to {project creation date}

    Methods:
        create_stores                   Create directories for all {available_stores}
        list_project__directories       Return list of existing {Project} directories
        list_store__directories         Return list of existing {Store} directories

        read_projects_file      Read in projects.json into {projects_dict}
        save_projects_file      Save {projects_dict} to projects.json

        get_exchange_directory  {home_directory}/{exchange_name}
        get_projects_file_path  {home_directory}/projects.json
        get_store_directory     {home_directory}/{exchange_name}/{store_name}
        get_project_directory   {home_directory}/{exchange_name}/{store_name}/{project_name}
    """

    def __init__(self, home_directory: str = "", settings: dict = {}):

        # instance attributes
        self.home_directory = home_directory
        self.exchange_name = ""
        self.available_stores = []
        self.projects_dict = {}

        self.update_settings(settings)

    # ABC Methods
    # ----------------------------------------
    def open_exchange(self):
        """
        Steps:
          1. Create {Exchange} folder inside {home_directory}
          2. Create {Stores} is they don't already exist
        """

        # set instance attributes

        # Step 1:
        exchange_directory = self.get_exchange_directory()
        os.makedirs(exchange_directory, exist_ok=True)

        # Step 2:
        self.create_stores()

        # Step 3:
        projects_file_path = self.get_projects_file_path()

        if os.path.isfile(projects_file_path):
            self.read_projects_file()
        else:
            self.save_projects_file()

    def close_exchange(self):

        # make sure the projects_dict file is saved
        self.save_projects_file()

        # make sure all of it's {Projects} are closed

    def create_project(self, project_name: str) -> None:

        self.projects_dict[project_name.upper()] = get_timestamp()

        self.save_projects_file()

    def open_project(self, project_name: str = ""):

        exchange_home = self.get_exchange_directory()

        return BaseProject(exchange_home, project_name, self.available_stores)

    def delete_project(self):
        pass

    def create_store(self, store_name: str = ""):

        store_path = self.get_store_directory(store_name)
        os.makedirs(store_path, exist_ok=True)

    def delete_store(self, store_name: str = ""):

        store_path = self.get_store_directory(store_name)
        shutil.rmtree(store_path)

    # Directory Methods
    # ----------------------------------------
    def get_exchange_directory(self) -> str:

        return f"{self.home_directory}/{self.exchange_name}"

    def get_store_directory(self, store_name: str = "") -> str:

        return f"{self.home_directory}/{self.exchange_name}/{store_name}"

    def get_project_directory(
        self, store_name: str = "", project_name: str = ""
    ) -> str:

        return f"{self.home_directory}/{self.exchange_name}/{store_name}/{project_name}"

    def get_projects_file_path(self) -> str:

        return f"{self.home_directory}/{self.exchange_name}/projects.json"

    # File Methods
    # ----------------------------------------
    def read_projects_file(self) -> None:

        projects_file_path = self.get_projects_file_path()

        self.projects_dict = read_json(projects_file_path)

    def save_projects_file(self) -> None:

        projects_file_path = self.get_projects_file_path()

        save_json(self.projects_dict, projects_file_path)

    # Methods
    # ----------------------------------------
    def create_stores(self) -> None:

        for store_name in self.available_stores:
            self.create_store(store_name)

    def list_project_directories(self):

        projects = []

        for store_name in self.available_stores:

            store_directory = self.get_store_directory(store_name)
            project_folders = list_subfolders(store_directory)
            projects.extend(project_folders)

        return projects

    def list_store_directories(self):

        exchange_directory = self.get_exchange_directory()

        return list_subfolders(exchange_directory)

    def update_settings(self, settings: dict = {}):

        if len(settings) > 0:
            for key, value in settings.items():
                print([key, value])
                setattr(self, key, value)
