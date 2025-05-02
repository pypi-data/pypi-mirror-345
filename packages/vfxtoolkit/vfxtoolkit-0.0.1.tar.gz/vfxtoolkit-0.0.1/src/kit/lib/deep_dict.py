# SPDX-License-Identifier: Apache-2.0

""" Helper class to deal with nested dictionnaries. """

from typing import Iterable


class MissingKey:
    """ Sentinel to mark missing keys. """
    pass


class DeepDict:
    """ Wrapper around dict to access and set nested keys using dot syntax.

    Also provide a conveninent "type" argument to most methods allowing basic
    data validation or conversion.
    
    Args:
        dict: reference dict to modify/access.
    """

    def __init__(self, dict: dict|None=None):
        self._dict = {} if dict is None else dict

    def dict(self) -> dict:
        """ Returns dict live container """
        return self._dict
    
    def get(self, key: str, default: any=None, type: type|None=None) -> any:
        """ Return the value for key if key is in the dictionary, else default.

        Args:
            key: Key which may contain dot (.) to address nested dict
            default: Default value to return if key does not exists
            type: Optional python type, ensure the returned value is
                an instance of this type. If it is not, a conversion will be
                attempted using type(value) without catching exceptions.
                Note the default value is always returned as is.
            
        Returns:
            Key value, or default value.
        """
        data = self.dict()
        try:
            for key in key.split("."):
                data = data[key]
            return type(data) if type and not isinstance(data, type) else data
        except KeyError:
            return default

    def set(self, key:str, value:any):
        """ Sets the value of the given key, possiblity nested.

        Args:
            key: Key which may contain dot (.) to address nested dict.
                Any missing dictionnaries along the path are created, non-dict
                values are overwritten with dictionnaries.
            value: The leaf value to set.
        """
        data = self.dict()
        keys = key.split(".")
        for key in keys[:-1]:
            if isinstance(data.get(key), dict):
                data = data[key]
            else:
                data[key] = {}
                data = data[key]
        data[keys[-1]] = value

    def setdefault(self, key: str, value: any=None, type: type|None=None) -> any:
        """ Sets value for key if key is not in dict, else returns key value.

        Args:
            key: Key which may contain dot (.) to address nested dict
            value: Default value to set if key does not exists
            type: Optional python type, ensure the returned value is
                an instance of this type. If it is not, a conversion will be
                attempted using type(value) without catching exceptions.
                Note the default value is always returned as is.

        Returns:
            Key value, or default value.
        """
        cur_value = self.get(key, MissingKey, type=type)
        if cur_value is MissingKey:
            self.set(key, value)
            return value
        else:
            return cur_value
        
    def update(self, other:dict):
        """ Recursively merge another dict into this one. """
        deep_merge(self.dict(), other)

    def pop(self, key: str, default: any=MissingKey, type: type|None=None) -> any:
        """ Remove and returns key value.
        
        Args:
            key: Key which may contain dot (.) to address nested dict
            default: Default value to return if key is not found.
                If set to MissingKey, KeyError will be raised if missing
            type: Optional python type, ensure the returned value is
                an instance of this type. If it is not, a conversion will be
                attempted using type(value) without catching exceptions.
                Note the default value is always returned as is.
        
        Returns:
            Removed key value, or default.
        
        Raises:
            KeyError if key is not found and no default value is specified.
        """

        # Locate parent key container dict
        data = self.dict()
        keys = key.split(".")
        for key in keys[:-1]:
            if isinstance(data.get(key), dict):
                data = data[key]
            elif default is MissingKey:
                raise KeyError(key)
            else:
                return default

        # Read value
        if default is MissingKey:
            value = data.pop(keys[-1])
        else:
            value = data.pop(keys[-1], default)

        # Return value, cast if nescessary
        if type and not isinstance(value, type):
            return type(value)
        else:
            return value

    def keys(self) -> Iterable[str]:
        """ Returns iterator over first-level dict keys """
        return self.dict().keys()
    
    def values(self) -> Iterable[any]:
        """ Returns iterator over first-level dict values """
        return self.dict().values()
    
    def items(self) -> Iterable[tuple[str, any]]:
        """ Returns iterator over first-level dict (key, value) tuples """
        return self.dict().items()

    def clear(self):
        """ Clear internal dict """
        self.dict().clear()

    # -- Dictionnary-like accessors -- #

    def __setitem__(self, key, value):
        self.set(key, value)
    
    def __getitem__(self, key):
        value = self.get(key, MissingKey)
        if value is MissingKey:
            raise KeyError(key)
        return value
    
    def __delitem__(self, key):
        self.pop(key)

    def __contains__(self, key):
        return self.get(key, MissingKey) is not MissingKey

    def __iter__(self):
        return self.dict().keys()

    def __str__(self):
        return self.dict().__str__()

    def __repr__(self):
        return self.dict().__repr__()
    

def deep_merge(dst, src):
    """ Recursively merge src dict into dst.
    
    Args:
        dst (dict): Destination dict, will be updated in-place
        src (dict): Source dict to merge into dst (won't be modified)
    """
    for k,v in src.items():
        if isinstance(v, dict):
            if k not in dst or not isinstance(dst[k], dict):
                dst[k] = {}
            deep_merge(dst[k], v)
        else:
            dst[k] = v
