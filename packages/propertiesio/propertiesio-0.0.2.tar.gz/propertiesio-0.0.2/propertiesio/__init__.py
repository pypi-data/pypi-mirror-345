import propertiesIO
import os
def new(filepath):
    """
    Create a new properties
    """
    return propertiesIO.parse(filepath)
def get(properties, key):
    """
    Get a property value
    """
    return properties.get(properties, key)
def put(properties, key, value):
    properties.put(key, value)
def has(properties, key):
    return properties.has_key(key)
def new_properties(filepath):
    """
    Create a new properties file
    """
    os.mknod(filepath)
def is_properties(filepath):
    """
    Check if a file is a properties file
    """
    return os.path.isfile(filepath) and filepath.endswith('.properties')
