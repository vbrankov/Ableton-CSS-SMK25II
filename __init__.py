from .MyController import MyController

def create_instance(c_instance):
    """
    This is the function Ableton calls to 
    instantiate your script.
    """
    return MyController(c_instance)