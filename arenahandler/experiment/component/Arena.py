import json


class Arena(object):
    """ 
    """

    def __init__(self, data):
        """ 
        """
        self.edges = 0
        self.blocks = 0
        self.leds = 0
        self.color = ''
        self.brightness = 0
        self.edge = []
        self.block = []
        self.led = []
        self.__dict__ = json.loads(data)
