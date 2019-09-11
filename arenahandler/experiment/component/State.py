import json


class State(object):
    """ 
    """

    def __init__(self, data):
        """ 
        """
        self.time = 0
        self.arena = None
        self.__dict__ = json.loads(data)