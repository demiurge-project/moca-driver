"""
This is the fundamental module which parses and interprets the states and expe-
riments that are comming from the http requests. This module utilises an sched-
uler in order schedule the different states within an experiment. If there are
task scheduled but an simple state execution is received then all the scheduled
task are canceled. The module contains the implementation for the differente 
level of control offered by the language definiton. 
"""
import json
import copy
import sched
import time
import asyncio
import threading

from .arduinointf.ArduinoInstruction import ArduinoInstruction
from .component.Arena import Arena
from .component.Edge import Edge
from .component.Block import Block
from .component.Led import Led
from .component.BlockInstruction import BlockInstruction
from .component.Color import Color
from .component.Experiment import Experiment
from .utils.readconfig import config
import experiment.utils.logger as my_logger

SERIALPORT = config["serialport"]
BAUDRATE = config["baudrate"]
logger = my_logger.get_logger('experimentctrl')
scheduler = sched.scheduler(time.time, time.sleep)


async def runState(state):
    """ 
        runState service controller.
        ----------
        state : Dict
            Dictionary containing the state configuration.
        Returns
        -------
    """
    jsonArena = json.dumps(state['arena'])
    arena = Arena(jsonArena)
    if not scheduler.empty():
        list(map(scheduler.cancel, scheduler.queue))
    generateArdInsForArena(arena)


async def runExperiment(experiment):
    """ 
        runExperiment service controller.
        ----------
        experiment : Dict
            Dictionary containing the experiment configuration.
        Returns
        -------
    """
    delay = 0
    jsonExperiment = json.dumps(experiment['experiment'])
    exp = Experiment(jsonExperiment)
    exp.parseStates()
    if not scheduler.empty():
        list(map(scheduler.cancel, scheduler.queue))
    for t in range(exp.repeatTimes):
        for state in exp.states:
            scheduler.enter(delay, 1, generateArdInsForArena, (state.arena,))
            if delay > exp.totalTime and exp.repeat:
                break
            delay += state.time
    if exp.clean:
        cleanconf = copy.copy(exp.states[-1].arena)
        cleanconf.color = "none"
        cleanconf.edge = []
        cleanconf.block = []
        cleanconf.led = []
        scheduler.enter(
            delay +
            exp.states[-1].time, 1, generateArdInsForArena, (cleanconf,)
        )
    # Start a thread to run the events
    t = threading.Thread(target=scheduler.run)
    t.start()


def generateArdInsForArena(arena):
    """
    This function executes the arena configuration and its Edge, Block and lEDs
    instructions.
    ----------
    arena : Object
        The arena object which contains the color configuration.

    Returns
    -------

    """
    logger.info(
        "Arena: %d, %d, %d, %s"
        % (arena.edges, arena.blocks, arena.leds, arena.color)
    )
    aIns = ArduinoInstruction(SERIALPORT, BAUDRATE)
    aIns.start_connection()
    for i in range(0, (arena.blocks * arena.edges)):
        bIns = BlockInstruction()
        bIns.brightness = arena.brightness
        bIns.block = \
            str(i) + "," \
            + str(arena.leds) + "," \
            + Color[arena.color.upper()].value
        logger.info(aIns.send_instrunction(str(bIns.toJSON())))
    # Edges in arena Individually
    if hasattr(arena, 'edge'):
        rangeOrSingleEdge(arena.edge, arena, aIns, True)
    # Blocks in arena Indvidually
    if hasattr(arena, 'block'):
        rangeOrSingleBlock(arena.block, arena, aIns, True)
    # Leds in arena Indvidually
    if hasattr(arena, 'led'):
        rangeOrSingleLed(arena.led, arena, aIns, True)

    aIns.close_connection()


def generateArdInsForEdge(edge, arena, aIns):
    """
    This function executes the Edge configration and its Block and lEDs
    instructions.
    ----------
    edge : Object
        The edge object which contains the color configuration.

    arena : Object
        The arena object which contains the general configuration.

    aIns : Object
        The serial connection to send the instructions to Arduino.

    Returns
    -------

    """
    # Converting from negative to equivalent positive
    edgeIndex = edge.index[0]
    edgeIndex = \
        fromNegToPosEq(arena.edges, edgeIndex) \
        if (edgeIndex < 0) else edgeIndex
    logger.info("Edge: %s, %d" % (edge.color, edgeIndex))
    for i in range(-1, (arena.blocks - 1)):
        bIns = BlockInstruction()
        bIns.brightness = arena.brightness
        ardIdx = str((edgeIndex * arena.blocks + i) - 1) \
            if arena.blocks > 1 else str(edgeIndex * arena.blocks + i)
        bIns.block = \
            ardIdx + "," \
            + str(arena.leds) + "," \
            + Color[edge.color.upper()].value
        aIns.send_instrunction(str(bIns.toJSON()))
    # If there are some blocks, execute them.
    if hasattr(edge, 'block'):
        for jsonBlock in edge.block:
            space = arena.edges * arena.blocks
            jsonBlock['index'] = rangeToList(jsonBlock['index'])
            newBlockRange = []
            for rBlock in jsonBlock['index']:
                newBlockRange.append(
                    fromRelPosToAbsPos(
                        # -1 means last index
                        edgeIndex, arena.blocks, rBlock, space
                    )
                )
            jsonBlock['index'] = newBlockRange
        rangeOrSingleBlock(edge.block, arena, aIns, False)
    # If there are some leds, execute them.
    if hasattr(edge, 'led'):
        for jsonLed in edge.led:
            ledsPerEdge = arena.blocks * arena.leds
            space = arena.edges * arena.blocks * arena.leds
            jsonLed['index'] = rangeToList(jsonLed['index'])
            newLedRange = []
            for rled in jsonLed['index']:
                newLedRange.append(
                    fromRelPosToAbsPos(edgeIndex, ledsPerEdge, rled, space)
                )
            jsonLed['index'] = newLedRange
        rangeOrSingleLed(edge.led, arena, aIns, False)


def generateArdInsForBlock(block, arena, aIns):
    """
    This function executes the Block configuration and its lEDs instructions.
    ----------
    block : Object
        The block object which contains the color configuration.

    arena : Object
        The arena object which contains the general configuration.

    aIns : Object
        The serial connection to send the instructions to Arduino.

    Returns
    -------

    """
    ledsOutOfRange = []
    blockIndex = block.index[0]
    # Converting from negative to equivalent positive
    blockIndex = \
        fromNegToPosEq(arena.blocks * arena.edges, blockIndex)\
        if (blockIndex < 0) else blockIndex
    #
    logger.info("Block: %s, %d" % (block.color, blockIndex))
    bIns = BlockInstruction()
    bIns.brightness = arena.brightness
    bIns.block = \
        str(blockIndex - 1) + "," \
        + str(arena.leds) + "," \
        + Color[block.color.upper()].value
    # If there are some leds, add them to the block instruction. # si algo sale mal segurament es aqui
    if hasattr(block, 'led'):
        for jsonLed in block.led:
            led = Led(json.dumps(jsonLed))
            led.index = rangeToList(led.index)
            if len(led.index) > 1:
                lRange = led.index
                for index in lRange:
                    if index != 0:
                        tmpLed = copy.copy(led)
                        tmpLed.index = [index]
                        if not (tmpLed.index[0] < 0 or tmpLed.index[0] > arena.leds):
                            bIns.led.append(
                                str(tmpLed.index[0] - 1) + "," +
                                Color[led.color.upper()].value
                            )
                        else:  # This is for the leds out of range
                            space = arena.edges * arena.blocks * arena.leds
                            orIndex = fromRelPosToAbsPos(  # outOfRangIndex
                                blockIndex, arena.leds, tmpLed.index[0], space
                            )
                            ledsOutOfRange.append(
                                {'index': [orIndex], 'color': led.color}
                            )
            else:
                if not (led.index[0] < 0 or led.index[0] > arena.leds):
                    bIns.led.append(
                        str(led.index[0] - 1) + "," +
                        Color[led.color.upper()].value
                    )
                else:  # This is for the leds out of range
                    space = arena.edges * arena.blocks * arena.leds
                    orIndex = fromRelPosToAbsPos(  # outOfRangIndex
                        blockIndex, arena.leds, led.index[0], space
                    )
                    ledsOutOfRange.append(
                        {'index': [orIndex], 'color': led.color}
                    )
    logger.info(bIns.toJSON())
    aIns.send_instrunction(str(bIns.toJSON()))
    rangeOrSingleLed(ledsOutOfRange, arena, aIns, False)


def generateArdInsForLed(led, arena, aIns):
    """
    This function executes the LEDs configuration.
    ----------
    Led : Object
        The Led object which contains the color configuration.

    arena : Object
        The arena object which contains the general configuration.

    aIns : Object
        The serial connection to send the instructions to Arduino.

    Returns
    -------

    """
    ledBlockRelPos = None
    ledIndex = led.index[0]
    if ledIndex < 0:
        ledIndex = fromNegToPosEq(
            arena.edges * arena.blocks * arena.leds, ledIndex
        )
    # convert the absolut led position to block relative
    # In which edge is the led
    for edgeIndex in range(1, arena.edges + 1):
        lastLedInEdge = arena.blocks * arena.leds * edgeIndex
        logger.info(
            "last led in edge %d, edge index %d" % (lastLedInEdge, edgeIndex)
        )
        if ledIndex <= lastLedInEdge:
            logger.info("led in Edge: %d" % (edgeIndex))
            # In which block is the led
            for blockIndex in range(-1, (arena.blocks - 1)):
                blockAbsPos = arena.blocks * edgeIndex + blockIndex
                logger.info("Block index: %d" % (blockAbsPos))
                if ledIndex <= (blockAbsPos * arena.leds):
                    # In which block position is the led
                    ledBlockRelPos = ledIndex % arena.leds
                    if ledBlockRelPos == 0:
                        ledBlockRelPos = arena.leds
                        break
                    break
            break
    logger.info("LED: %s, %d" % (led.color, ledIndex))
    bIns = BlockInstruction()
    bIns.brightness = arena.brightness
    ardIdx = str((ledIndex - 1) %
                 arena.leds) if ledBlockRelPos is None else str(ledBlockRelPos - 1)
    ardBlIdx = str(blockAbsPos - 1) if arena.blocks > 1 else str(blockAbsPos)
    bIns.block = \
        ardBlIdx + "," \
        + str(arena.leds) + "," \
        + Color['OMIT'].value
    bIns.led.append(
        ardIdx + "," + Color[led.color.upper()].value
    )
    logger.info(bIns.toJSON())
    aIns.send_instrunction(str(bIns.toJSON()))


def fromRelPosToAbsPos(edIdx, bckPerEd, bckIdx, space):  # edgeBlock->Block
    """
    This function transform the relative position of an index using the 
    relative index, the number of blocks per edge, the index block and the space
    in which this index should be. The function accepts negative indexes.
    ----------
    edIdx : Object
        Index of edge in which the idnex to transform is.

    bckPerEd : Object
        Number of blocks that form an edge.

    bckIdx : Object
        Index to transform.

    space : Object
        The space within the index should be.

    Returns
    -------

    """
    if bckPerEd == 1:
        return bckIdx
    elif bckIdx < 0:
        return (((edIdx * bckPerEd) - ((bckPerEd - bckIdx))) % space) + 1
    else:
        newIndex = ((edIdx * bckPerEd) - ((bckPerEd - bckIdx))) % space
        return newIndex if (newIndex > 0) else space


def fromNegToPosEq(space, number):
    """
    This function transform a negative number to its positive equivalent.
    ----------
    numnber : Object
        The negative number to transform.

    space : Object
        The space within the index should be.

    Returns
    -------

    """
    if space == 1:
        return abs(number)
    else:
        return (number % space) + 1


def rangeOrSingleEdge(edges, arena, aIns, fromArena):
    """
    This function execute a range of Edges or a single Edge.
    ----------
    edges : Object
        An array of edges which lenght can be 0, 1 or more.

    arena : Object
        The arena object which contains the general configuration.

    aIns : Object
        The serial connection to send the instructions to Arduino.

    fromArena : Boolean
        Specify if the range or single edge comes from the arena enviroment.

    Returns
    -------

    """
    for jsonEdge in edges:
        edge = Edge(json.dumps(jsonEdge))
        if len(edge.index) > 1:
            eRange = rangeToList(edge.index) \
                if(fromArena)else edge.index
            # to-do change to reverse order reversed()
            for index in reversed(eRange):
                orIndex = index
                index = fromRelPosToAbsPos(
                    index, arena.edges, index, arena.edges
                )
                if index != 0:
                    tmpEdge = copy.copy(edge)
                    tmpEdge.index = [index]
                    # to-do change from last to first
                    if not(orIndex == eRange[0]):
                        tmpEdge.block = []
                        tmpEdge.led = []
                        generateArdInsForEdge(tmpEdge, arena, aIns)
                    else:
                        generateArdInsForEdge(tmpEdge, arena, aIns)

        else:
            generateArdInsForEdge(edge, arena, aIns)


def rangeOrSingleBlock(blocks, arena, aIns, fromArena):
    """
    This function execute a range of Blocks or a single one.
    ----------
    blocks : Object
        An array of blocks which lenght can be 0, 1 or more.

    arena : Object
        The arena object which contains the general configuration.

    aIns : Object
        The serial connection to send the instructions to Arduino.

    fromArena : Boolean
        Specify if the range or single edge comes from the arena enviroment.

    Returns
    -------

    """
    for jsonBlock in blocks:
        block = Block(json.dumps(jsonBlock))
        if len(block.index) > 1:
            bRange = rangeToList(block.index) if (fromArena) else block.index
            # to-do change to reverse order reversed()
            for index in reversed(bRange):
                if index != 0:
                    tmpBlock = copy.copy(block)
                    tmpBlock.index = [index]
                    # to-do change from last to first
                    if not(index == bRange[0]):
                        tmpBlock.led = []
                        generateArdInsForBlock(tmpBlock, arena, aIns)
                    else:
                        generateArdInsForBlock(tmpBlock, arena, aIns)
        else:
            generateArdInsForBlock(block, arena, aIns)


def rangeOrSingleLed(leds, arena, aIns, fromArena):
    """
    This function execute a range of Leds instructions or a single one.
    ----------
    Leds : Object
        An array of leds which lenght can be 0, 1 or more.

    arena : Object
        The arena object which contains the general configuration.

    aIns : Object
        The serial connection to send the instructions to Arduino.

    fromArena : Boolean
        Specify if the range or single edge comes from the arena enviroment.

    Returns
    -------

    """
    for jsonLed in leds:
        led = Led(json.dumps(jsonLed))
        if len(led.index) > 1:
            lRange = rangeToList(led.index)\
                if (fromArena) else led.index
            for index in lRange:
                if index != 0:
                    tmpLed = copy.copy(led)
                    tmpLed.index = [index]
                    generateArdInsForLed(tmpLed, arena, aIns)
        else:
            generateArdInsForLed(led, arena, aIns)


def rangeToList(rng):
    """
    This function transform a python range to a list of values.
    ----------
    range : Object
        A python range.

    Returns
    -------
    List which contains the respective range values.

    """
    list = []
    if len(rng) == 3:
        list = range(rng[0], rng[1] - 1, rng[2]) \
            if (rng[0] > rng[1]) else range(rng[0], rng[1] + 1, rng[2])
        return list
    elif len(rng) == 2:
        list = range(rng[0], rng[1] - 1)\
            if (rng[0] > rng[1]) else range(rng[0], rng[1] + 1)
        return list
    elif len(rng) == 1:
        return rng
