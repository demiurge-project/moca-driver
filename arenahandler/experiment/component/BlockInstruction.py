import json


class BlockInstruction:

    def __init__(self):
        self.brightness = 0
        self.block = ''
        self.led = []

    def toJSON(self):
        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, indent=4
        )
