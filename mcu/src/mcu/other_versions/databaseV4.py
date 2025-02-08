"""
Version 4 of the database script
This script is responsible for creating the database and adding entries to it.

The database is a hierarchical structure that contains containers and entries.
Each container can contain multiple entries, and each entry has a unique ID to identify it.

The database can be serialized to a file and deserialized from a file.
The file format is a npy file that contains a dictionary with the database structure.

This application follows the SOLID principles, specifically the Single Responsibility Principle.
Polymorphism is used to create different types of entries, such as StringEntry, IntEntry, and FileEntry.

The database is designed to be extensible, allowing new entry types to be added easily.
The database is also thread-safe, allowing multiple threads to access it concurrently.

The database is designed to be user-friendly, with a ConfigAPI class that provides a simple interface for interacting with the database.
"""

# Standard library imports
import logging
import pathlib
import pickle
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from threading import Lock, Thread
from typing import Any, Callable, Dict, List, Type

# Third party imports
from PyQt6.QtWidgets import (
    QLineEdit,
    QWidget,
)

####################################################################################################

# Logger
logger = logging.getLogger(__name__)

####################################################################################################
# Database Hierarchical Structure


class EntryType(ABC):
    """Base class for all database types"""

    @abstractmethod
    def validate(cls, value: Any) -> bool:
        """Validate input value against type constraints"""
        pass

    @abstractmethod
    def default_widget(cls) -> QWidget:
        """Return default UI widget for this type"""
        pass


@dataclass
class EntryDefinition:
    """Definition of an entry in the database"""

    id: str
    name: str
    description: str
    data_type: Type[EntryType]
    default_value: Dict[str, Any] = field(default_factory=dict)
    attributes: Dict[str, Any] = field(default_factory=dict)


class DatabaseEntry:
    """Runtime instance of a configuration entry"""

    def __init__(self, definition: EntryDefinition):
        self.definition = definition
        for key, value in {"hidden": False, "editable": True}.items():
            if key not in self.definition.attributes:
                self.definition.attributes[key] = value

        self._value = definition.default_value.copy()
        self._lock = Lock()

        self._callbacks: Dict[str, Callable] = {}
        self._callbacks_running = False
        self._print_on_trigger = False

    ### Value access ###

    def set_value(self, value: Dict[str, Any], trigger_callbacks: bool = True) -> None:
        """Thread-safe value update with validation"""
        with self._lock:
            # Validate value
            if not self.definition.data_type.validate(value):
                logger.error(
                    f"Invalid value {value} for type {self.definition.data_type}"
                )
                raise ValueError("Invalid value type")

            # Update values
            for key, val in value.items():
                self._value[key] = val

        # Trigger callbacks
        if trigger_callbacks:
            self.run_callbacks()

    @property
    def value(self) -> Dict[str, Any]:
        """Safe Return value"""
        with self._lock:
            return self._value.copy()

    ### Callbacks ###

    def add_callback(self, callback_id: str, fn: Callable) -> None:
        """Add value change listener"""
        with self._lock:
            self._callbacks[callback_id] = fn

    def add_async_callback(self, callback_id: str, fn: Callable) -> None:
        """Add value change listener with a separate thread (a new thread is created for each callback)"""
        with self._lock:
            self._callbacks[callback_id] = lambda: Thread(target=fn).start()

    def remove_callback(self, callback_id: str) -> None:
        """Remove value change listener"""
        with self._lock:
            self._callbacks.pop(callback_id, None)

    def run_callbacks(self) -> None:
        """Run all registered callbacks"""
        with self._lock:
            if self._print_on_trigger:
                logger.debug(
                    f"Running {len(self._callbacks)} callbacks for {self.definition.id}"
                )
            self._callbacks_running = True
            for callback in self._callbacks.values():
                callback()
            self._callbacks_running = False

    @property
    def callback_ids(self) -> List[str]:
        """Return list of callback IDs"""
        return list(self._callbacks.keys())

    @property
    def callbacks_running(self) -> bool:
        """Return True if any callbacks are running"""
        return any(self._callbacks.values())

    def debug_callback_trigger(self, print_debug_messages: bool) -> None:
        """Print debug message when callbacks are triggered"""
        self._print_on_trigger = print_debug_messages

    ### String representation ###

    def __repr__(self) -> str:
        return f"DatabaseEntry({self.definition.id}) -> {self._value}"

    def __str__(self) -> str:
        message = f"Entry ID: {self.definition.id}, Name: {self.definition.name}\n"
        message += f"> Description: {self.definition.description}\n"
        message += f"> Value: {self._value}"
        return message


@dataclass
class ContainerDefinition:
    """Definition of a container in the database"""

    id: str
    name: str
    description: str
    attributes: Dict[str, Any] = field(default_factory=dict)


class EntryContainer:
    """Base class for organizing entries, it can contain other containers and entries"""

    def __init__(self, definition: ContainerDefinition):
        self.definition = definition
        for key, value in {"hidden": False, "editable": True}.items():
            if key not in self.definition.attributes:
                self.definition.attributes[key] = value

        self.entries: Dict[str, DatabaseEntry] = {}
        self.containers: Dict[str, EntryContainer] = {}
        self._lock = Lock()

    def add_entry(self, entry: DatabaseEntry) -> None:
        """Add an entry to the container"""
        with self._lock:
            self.entries[entry.definition.id] = entry

    def add_container(self, container: "EntryContainer") -> None:
        """Add a sub-container to the container"""
        with self._lock:
            self.containers[container.definition.id] = container

    def get_entry(self, entry_id: str) -> DatabaseEntry:
        """Get an entry from the container"""
        with self._lock:
            return self.entries[entry_id]

    def get_container(self, container_id: str) -> "EntryContainer":
        """Get a sub-container from the container"""
        with self._lock:
            return self.containers[container_id]

    def remove_entry(self, entry_id: str) -> None:
        """Remove an entry from the container"""
        with self._lock:
            self.entries.pop(entry_id, None)

    def remove_container(self, container_id: str) -> None:
        """Remove a sub-container from the container"""
        with self._lock:
            self.containers.pop(container_id, None)

    def __repr__(self) -> str:
        return f"EntryContainer({self.definition.id}) -> {self.entries.keys()}, {self.containers.keys()}"

    def __str__(self) -> str:
        message = f"Container ID: {self.definition.id}, Name: {self.definition.name}\n"
        message += f"> Description: {self.definition.description}\n"
        message += (
            f"> Entries: {[entry.definition.id for entry in self.entries.values()]}\n"
        )
        message += f"> Sub-containers: {[container.definition.id for container in self.containers.values()]}"
        return message


class Database:
    """Main class for the database, it contains the root container and manages serialization/deserialization"""

    def __init__(self):
        self.root_container = EntryContainer(
            ContainerDefinition("root", "Root", "Root container")
        )

    ### Container Management ###

    def _decode_container_path(self, container_path: str) -> List[str]:
        """Decode container path string to list of container IDs"""
        path_elements = container_path.split("/")
        # Remove the root element if it is present (to make it simple)
        if "root" in path_elements[0]:
            path_elements = path_elements[1:]
        # Strip and remove empty elements
        path_elements = [
            element.strip() for element in path_elements if element.strip()
        ]
        return path_elements

    def get_container(self, container_path: str) -> EntryContainer:
        """
        Get a container by its path of IDs

        Example:
            get_container("root/subcontainer1/subcontainer2")
            get_container("subcontainer1")

        """
        container_ids = self._decode_container_path(container_path)
        current_container = self.root_container
        for container_id in container_ids:
            current_container = current_container.get_container(container_id)
        return current_container

    def add_container(
        self, container_path: str, definition: ContainerDefinition
    ) -> EntryContainer:
        """
        Add a new container to the database

        Args:
            container_path: Path to the container
            definition: Container definition

        Example:
            add_container("subcontainer1", ContainerDefinition(
                id="subcontainer2",
                name="Subcontainer 2",
                description="This is a subcontainer"
            ))

        """
        current_container = self.get_container(container_path)
        new_container = EntryContainer(definition)
        current_container.add_container(new_container)
        return new_container

    def remove_container(self, container_path: str) -> None:
        """
        Remove a container from the database

        Args:
            container_path: Path to the container

        Example:
            remove_container("subcontainer1/subcontainer2")

        """
        container_ids = self._decode_container_path(container_path)
        container_id = container_ids[-1]
        parent_container = self.get_container("/".join(container_ids[:-1]))
        parent_container.remove_container(container_id)

    ### Entry Management ###

    def add_entry(
        self, container_path: str, definition: EntryDefinition
    ) -> DatabaseEntry:
        """
        Add a new entry to the database

        Args:
            container_path: Path to the container
            definition: Entry definition

        Example:
            add_entry("root/subcontainer1", EntryDefinition(
                id="entry1",
                name="Entry 1",
                description="This is an entry",
                data_type=StringEntry
            ))

        """
        current_container = self.get_container(container_path)
        new_entry = DatabaseEntry(definition)
        current_container.add_entry(new_entry)
        return new_entry

    def remove_entry(self, entry_path: str) -> None:
        """
        Remove an entry from the database

        Args:
            entry_path: Path to the entry

        Example:
            remove_entry("root/subcontainer1/entry1")

        """
        entry_ids = self._decode_container_path(entry_path)
        entry_id = entry_ids[-1]
        parent_container = self.get_container("/".join(entry_ids[:-1]))
        parent_container.remove_entry(entry_id)

    ### Import/export ###

    def export(self, folder_path: pathlib.Path, file_name: str) -> bool:
        """
        Export the database to a file

        Args:
            folder_path: Folder path to save the file
            file_name: File name without extension

        """
        file_path = str(folder_path / file_name) + ".dbpckl"
        try:
            with open(file_path, "wb") as file:
                pickle.dump(self.root_container, file)
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return False

        return True

    def import_file(self, file_path: pathlib.Path) -> bool:
        """
        Import the database from a file

        Args:
            file_path: Path to the file

        """
        if not file_path.suffix == ".dbpckl":
            logger.warning("Database file is not a .dbpckl file")
            return False

        try:
            with open(file_path, "rb") as file:
                self.root_container = pickle.load(file)
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            return False

        return True

    ### String representation ###

    def __repr__(self) -> str:
        return f"Database -> {self.root_container}"

    def __str__(self) -> str:
        """Returns a Tree representation of the database"""

        def print_container(container: EntryContainer, level: int) -> str:
            SPACER = "\t"
            message = f"{SPACER*level}Container ID: {container.definition.id}, Name: {container.definition.name}\n"
            message += (
                f"{SPACER*level}> Description: {container.definition.description}\n"
            )
            for entry in container.entries.values():
                message += f"{SPACER*(level+1)}Entry ID: {entry.definition.id}, Name: {entry.definition.name}\n"
            for subcontainer in container.containers.values():
                message += print_container(subcontainer, level + 1)
            return message

        final_message = "Database Structure :\n"
        final_message += print_container(self.root_container, 1)
        return final_message


####################################################################################################
# Simplified Database API


class ConfigAPI:
    """User-friendly API surface for interacting with the database"""

    def __init__(self, database: Database):
        self._db = database

    ### Container Management ###

    def create_container(
        self, container_id: str, name: str, description: str
    ) -> EntryContainer:
        """Create a new container"""
        return self._db.root_container.add_container(
            EntryContainer(ContainerDefinition(container_id, name, description))
        )

    def get_container(self, container_id: str) -> EntryContainer:
        """Get an existing container"""
        return self._db.root_container.get_container(container_id)

    def remove_container(self, container_id: str) -> None:
        """Remove an existing container"""
        self._db.root_container.remove_container(container_id)

    ### Entry Management ###


####################################################################################################
# Entry Types


class StringEntry(EntryType):
    """Entry type for string values"""

    @classmethod
    def validate(cls, value: Any) -> bool:
        return isinstance(value, str)

    @classmethod
    def default_widget(cls) -> QWidget:
        return QLineEdit()


####################################################################################################
# Demo


def main():
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)

    # Create the database
    database = Database()

    # Create a container
    hidden_class = database.add_container(
        "root",
        ContainerDefinition(
            id="hidden_class",
            name="Hidden Class",
            description="This class is hidden from the user and is used for internal purposes.",
            attributes={
                "hidden": True,
                "editable": False,
            },
        ),
    )

    # Add entries to the container
    hidden_class.add_entry(
        DatabaseEntry(
            EntryDefinition(
                id="app_version",
                name="Application Version",
                description="The version of the application.",
                data_type=StringEntry,
                default_value={"value": "5.0.0"},
            )
        )
    )

    hidden_class.add_entry(
        DatabaseEntry(
            EntryDefinition(
                id="app_name",
                name="Application Name",
                description="This application reads data from a UART port and displays it.",
                data_type=StringEntry,
                default_value={"value": "UART Reader for LELEC210x"},
            )
        )
    )

    hidden_class.add_entry(
        DatabaseEntry(
            EntryDefinition(
                id="author",
                name="Author",
                description="The author of the application.",
                data_type=StringEntry,
                default_value={"value": "Group E 2024-2025"},
            )
        )
    )

    if False:  # TODO : Fix this properly, as i can't pickle the locks or threads or callable stuff
        # Export the database
        database.export(pathlib.Path(__file__).parent, "database")

        # Import the database
        new_database = Database()
        new_database.import_file(pathlib.Path(__file__).parent / "database.dbpckl")

        print(new_database)

    # Print the database
    print(database)


if __name__ == "__main__":
    main()
