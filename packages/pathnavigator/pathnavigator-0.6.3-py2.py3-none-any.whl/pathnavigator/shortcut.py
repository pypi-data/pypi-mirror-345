import json
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from itertools import chain
from .att_name_convertor import AttributeNameConverter
from .utils import Base

__all__ = ['Shortcut']

"""
    Methods
    -------
    add(name, path, overwrite=False)
        Adds a new shortcut as an attribute. 
    add_all(directory, overwrite=False, prefix="",
                only_include=[], only_exclude=[],
                only_folders=False, only_files=False)
        Adds all files in a given directory as shortcuts.
    get(name)
        Retrieves the path of a shortcut.
    get_str(name)
        Retrieves the path of a shortcut as a string.
    remove(name)
        Removes an existing shortcut by name and deletes the attribute.
    clear()
        Removes all shortcuts.
    ls()
        Lists all shortcuts (attributes).
    to_dict()
        Returns all shortcuts as a dictionary.
    to_json(filename)
        Returns all shortcuts as a JSON string and saves it to a file.
    to_yaml(filename)
        Returns all shortcuts as a YAML string and saves it to a file.
    load_dict(data, overwrite=False)
        Loads shortcuts from a dictionary.
    load_json(filename, overwrite=False)
        Loads shortcuts from a JSON file.
    load_yaml(filename, overwrite=False)
        Loads shortcuts from a YAML file.
"""

@dataclass
class Shortcut(Base):
    """
    A class to manage shortcuts to specific paths and access them as attributes.
    """
    _pn_invalid_name_list = [
    "add", "add_all", "get", "get_str", "remove", "clear", "ls",
    "to_json", "to_yaml", "to_dict",
    "load_dict", "load_json", "load_yaml"
    ]
    
    _pn_converter: object = field(init=False)
    
    def __post_init__(self):
        object.__setattr__(self, "_pn_converter", AttributeNameConverter(_pn_invalid_name_list=self._pn_invalid_name_list))

    def __setattr__(self, name: str, value: str|Path, overwrite: bool = False):
        """
        Dynamically add shortcut as an attribute.

        Parameters
        ----------
        name : str
            The name of the shortcut.
        value : str or Path
            The path that the shortcut refers to.
        overwrite : bool, optional
            Whether to overwrite an existing shortcut. Default is False.
        """
        # Allow special attributes to be set normally
        if name=="_pn_converter":
            object.__setattr__(self, name, value)
            return
        
        if name in self.__dict__ and not overwrite:
            raise AttributeError(f"Cannot add shortcut '{name}' as it conflicts with an existing attribute.")
        super().__setattr__(name, Path(value))
        #print(f"Shortcut '{name}' added for path '{value}'")

    def __getattr__(self, name: str) -> str:
        """
        Retrieve the path of a shortcut.

        Parameters
        ----------
        name : str
            The name of the shortcut.

        Returns
        -------
        str
            The path associated with the shortcut.

        Raises
        ------
        AttributeError
            If the shortcut does not exist.
        """
        if name not in self.__dict__:
            raise AttributeError(f"No shortcut found for '{name}'")
        return self.__dict__[name]

    def __delattr__(self, name: str):
        """
        Remove a shortcut by name.

        Parameters
        ----------
        name : str
            The name of the shortcut to remove.

        Raises
        ------
        AttributeError
            If the shortcut does not exist.
        """
        if name not in self.__dict__:
            raise AttributeError(f"No shortcut found for '{name}'")
        super().__delattr__(name)
        #print(f"Shortcut '{name}' removed")

    def add(self, name: str, path: str, overwrite: bool = False):
        """
        Add a new shortcut as an attribute. automatically converts the name to a valid attribute name.

        Parameters
        ----------
        name : str
            The name of the shortcut.
        path : str
            The path that the shortcut refers to.
        overwrite : bool, optional
            Whether to overwrite an existing shortcut. Default is False.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.my_folder
        '/path/to/folder'
        """
        
        valid_name = self._pn_converter.to_valid_name(name)
        self.__setattr__(valid_name, path, overwrite=overwrite)

    def add_all(self, directory: str|Path, overwrite: bool = False, prefix: str = "", 
                only_include: list = [], only_exclude: list = [],
                only_folders: bool = False, only_files: bool = False):
            """
            Add all files in a given directory as shortcuts.

            Parameters
            ----------
            directory : str or Path
                The directory containing the files to add as shortcuts.
            overwrite : bool, optional
                Whether to overwrite existing shortcuts. Default is False.
            prefix : str, optional
                The prefix to add to the shortcut names. Default is "".
            only_include : list, optional
                A list of  patterns to include only files or folders that match the patterns.
                No `**` wildcard is allowed, only `*` is allowed.
            only_exclude : list, optional
                A list of patterns to exclude files or folders that match the patterns.
                No `**` wildcard is allowed, only `*` is allowed.
            only_folders : bool, optional
                Whether to scan only subfolders. Default is False.
            only_files : bool, optional
                Whether to scan only files. Default is False.
            Examples
            --------
            >>> shortcut = Shortcut()
            >>> shortcut.add_all("/path/to/directory")
            """
            p = Path(directory).absolute()
            if not p.is_dir():
                raise NotADirectoryError(f"{directory} is not a valid directory")
        
            if only_include != []:
                generator = chain.from_iterable(p.glob(pattern) for pattern in only_include)
            elif only_exclude != []:
                generator = (entry for entry in p.iterdir() if not any(entry.match(pattern) for pattern in only_exclude))
            else:
                generator = p.iterdir()

            for entry in generator:
                entry_name = entry.name
                if entry.is_dir() and not only_files:
                    shortcut_name = prefix + entry_name
                    self.add(shortcut_name, str(entry), overwrite=overwrite)
                elif entry.is_file() and not only_folders:
                    shortcut_name = prefix + entry_name
                    self.add(shortcut_name, str(entry), overwrite=overwrite)

    def get(self, name: str) -> str:
        """
        Retrieve the path of a shortcut.

        Parameters
        ----------
        name : str
            The name of the shortcut.

        Returns
        -------
        str
            The path associated with the shortcut.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.get("my_folder")
        '/path/to/folder'
        """
        valid_name = self._pn_converter.get_valid(name)
        return self.__getattr__(valid_name)
    
    def get_str(self, name: str) -> str:
        """
        Retrieve the path of a shortcut.

        Parameters
        ----------
        name : str
            The name of the shortcut.

        Returns
        -------
        str
            The path associated with the shortcut.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.get("my_folder")
        '/path/to/folder'
        """
        return str(self.get(name))
    
    def remove(self, name: str):
        """
        Remove a shortcut by name and delete its attribute.

        Parameters
        ----------
        name : str
            The name of the shortcut to remove.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.remove("my_folder")
        >>> hasattr(shortcut, "my_folder")
        False
        """
        valid_name = self._pn_converter.get_valid(name)
        self._pn_converter.remove(name)  # Remove from the converter's mapping
        self.__delattr__(valid_name)

    def clear(self):
        """
        Remove all shortcuts.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.clear()
        >>> hasattr(shortcut, "my_folder")
        False
        """
        for key in list(self.__dict__.keys()):
            if not key.startswith("_pn_"):
                self.__delattr__(key)
                
    def ls(self):
        """
        List all shortcuts and their paths.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.ls()
        Shortcuts:
        my_folder -> /path/to/folder
        """
        attributes = {self._pn_converter.get_org(key): value for key, value in self.__dict__.items() if not key.startswith("_pn_")}
        if not attributes:
            print("No shortcuts available.")
        else:
            print("Shortcuts:")
            for name, path in attributes.items():
                print(f"{name} -> {path}")

    def to_dict(self, to_str=False) -> dict:
        """
        Return all shortcuts as a dictionary. 

        Parameters
        ----------
        to_str : bool, optional
            Whether to convert all Path objects to strings. Default is False.

        Returns
        -------
        dict
            A dictionary representation of all shortcuts.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.to_dict()
        {'my_folder': '/path/to/folder'}
        """
        _pn_converter = self._pn_converter
        if to_str:
            return {_pn_converter.get_org(k): str(v) for k, v in self.__dict__.items() if not k.startswith("_pn_")}
        else:
            return {_pn_converter.get_org(k): v for k, v in self.__dict__.items() if not k.startswith("_pn_")}
        
    def to_json(self, filename: str = "shortcuts.json") -> str:
        """
        Return all shortcuts as a JSON string and save it to a file.

        Parameters
        ----------
        filename : str
            The name of the file where the JSON string will be saved.

        Returns
        -------
        str
            A JSON string representation of all shortcuts.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.to_json("shortcuts.json")
        '{"my_folder": "/path/to/folder"}'
        """
        json_data = json.dumps(self.to_dict(to_str=True), indent=4)  
        with open(filename, 'w') as f:
            f.write(json_data)  # Writing the JSON data to the file
    
        return json_data  # Returning the JSON string as well

    def to_yaml(self, filename: str = "shortcuts.yml") -> str:
        """
        Return all shortcuts as a YAML string and save it to a file.

        Parameters
        ----------
        filename : str
            The name of the file where the YAML string will be saved.

        Returns
        -------
        str
            A YAML string representation of all shortcuts.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.add("my_folder", "/path/to/folder")
        >>> shortcut.to_yaml("shortcuts.yml")
        my_folder: /path/to/folder
        """
        yaml_data = yaml.dump(self.to_dict(to_str=True), default_flow_style=False)

        with open(filename, 'w') as f:
            f.write(yaml_data)  # Writing the YAML data to the file

        return yaml_data  # Returning the YAML string as well

    def load_dict(self, data: dict, overwrite: bool = False):
        """
        Load shortcuts from a dictionary.

        Parameters
        ----------
        data : dict
            A dictionary where keys are shortcut names and values are paths.
        overwrite : bool, optional
            Whether to overwrite existing shortcuts. Default is False.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.load_dict({"project": "/path/to/project", "data": "/path/to/data"})
        """
        _pn_converter = self._pn_converter
        for name, path in data.items():
            valid_name = _pn_converter.to_valid_name(name)
            self.add(valid_name, Path(path), overwrite=overwrite)

    def load_json(self, filename: str, overwrite: bool = False):
        """
        Load shortcuts from a JSON file.

        Parameters
        ----------
        filename : str
            The name of the file containing the shortcuts in JSON format.
        overwrite : bool, optional
            Whether to overwrite existing shortcuts. Default is False.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.load_json("shortcuts.json")
        """
        with open(filename, 'r') as f:
            data = json.load(f)  # Load the JSON data into a dictionary
            self.load_dict(data, overwrite=overwrite)  # Load the shortcuts using the load_dict method

    def load_yaml(self, filename: str, overwrite: bool = False):
        """
        Load shortcuts from a YAML file.

        Parameters
        ----------
        filename : str
            The name of the file containing the shortcuts in YAML format.
        overwrite : bool, optional
            Whether to overwrite existing shortcuts. Default is False.

        Examples
        --------
        >>> shortcut = Shortcut()
        >>> shortcut.load_yaml("shortcuts.yml")
        """
        with open(filename, 'r') as f:
            data = yaml.safe_load(f)  # Load the YAML data into a dictionary
            self.load_dict(data, overwrite=overwrite)  # Load the shortcuts using the load_dict method