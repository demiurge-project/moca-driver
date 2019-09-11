import json
import math
import copy

from .State import State
from .Arena import Arena


class Experiment(object):
    """ 
    """

    def __init__(self, data):
        """ 
        """
        self.totalTime = 0
        self.repeat = False
        self.clean = True
        self.states = []
        self.sumTimeStates = 0
        self.repeatTimes = 0
        self.__dict__ = json.loads(data)

    def toJSON(self):
        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, indent=4
        )

    def parseStates(self):
        sts = []
        for state in self.states:
            s = State(json.dumps(state))
            a = Arena(json.dumps(s.arena))
            s.arena = copy.copy(a)
            sts.append(s)
        self.states = sts
        self.sumTimeStates = sum(state.time for state in self.states)
        self.repeatTimes = math.ceil(
            self.totalTime / self.sumTimeStates) if (self.repeat) else 1
