from enum import Enum


class Color(Enum):
    NONE = "0,0,0" # Black
    RED = "255,0,0"
    GREEN = "0,255,0"
    BLUE = "0,0,255"
    YELLOW = "255,255,0"
    MAGENTA = "255,0,255"
    CYAN = "0,255,255"
    WHITE = "255,255,255"
    OMIT = "-1,-1,-1" # NULL
    LR = "17,0,7"
    LG = "7,12,0"
    LB = "10,0,12"
    LY = "200,120,0"
    LC = "0,200,50"
    LM = "150,0,60"
    EXPR = "242,94,139"
    EXPG = "100,227,121"
    EXPB = "77,107,227"
    EXPY = "204,139,82"
    EXPC = "65,183,196"
    EXPM = "196,73,227"
    ZOMBIE = "27,165,44"
    PUMP = "241,88,2"
    PURPLE = "124,16,173"
