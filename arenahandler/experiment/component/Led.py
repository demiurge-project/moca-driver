import json


class Led(object):
    """ 
    """

    def __init__(self, data):
        """ 
        """
        self.index = []
        self.color = ""
        self.__dict__ = json.loads(data)
