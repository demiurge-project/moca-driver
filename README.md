# Dynamic lighting arena for swarm robotics

This project was developed as a handler of dynamic lighting polygonal arena 
which is compounded of blocks of leds built with the APA102 LED strip connected 
to an Arduino. The project consists in :

1. The Arduino firmware
2. An inteferface between the handler and the arduino
3. The arena handler 

## Getting Started

### Folder structure
```
├── firmwarearduino
│   ├── ledstriphandler.ino
├── arenahandler
│   ├── config
│   │   ├── config.json
│   ├── logs
│   │   ├── apiserver.log
│   │   ├── arduinocomm.log
│   │   ├── experimentctrl.log
│   ├── experiment
│   │   ├── arduinointf
│   │   │   │   ├── ArduinoInstruction.py
│   │   ├── component
│   │   │   │   ├── Arena.py
│   │   │   │   ├── Block.py
│   │   │   │   ├── BlockInstruction.py
│   │   │   │   ├── Color.py
│   │   │   │   ├── Edge.py
│   │   │   │   ├── Experiment.py
│   │   │   │   ├── Led.py
│   │   │   │   ├── State.py
│   │   ├── utils
│   │   │   │   ├── logger.py
│   │   │   │   ├── readconfig.py
│   │   ├── experimentctrl.py
│   ├── apiserver.py
├── README.md
```

### Prerequisites

- Python 3.6.4

#### Arduino libraries
- FastLED 3.1.6
- ArduinoJson 5.13.1

#### Python libraries

- aiohttp 3.2.1
- pyserial 3.4


### Installing

Python libraries intallation

aiohttp

```bash
sudo python3.5 -m pip install aiohttp
```

pyserial

```bash
sudo python3.5 -m pip install pyserial
```

## Deployment

There is configuration file `config.json` in which necessary to put the following parameters:

```json
{
    "serialport": "/dev/ttyS5",
    "baudrate": 57600,
    "loglevel": "INFO",
    "logformat": "%(asctime)s %(name)s [%(levelname)s] %(message)s"
}
``` 

The `serialport` depends on the operating system and port you are using to connect
the Arduino so it is necessary to change it before deploying the web server.

The base command is:

```bash
apiserver.py [--port] [--host]
```
`host` means the host where you want to bind the web server  
`port` means the port where you want to bind the web server  

Go to the `arenahandler` directory and execute the following command:

### Linux
```bash
./apiserver.py --port=8080 --host=localhost
```
### Windows
```bash
python apiserver.py --port=8080 --host=localhost
```
`note`: By default the host and port are `0.0.0.0`, `8080` respectively, however
 it is possible to change it using
the port and host argument at the time of execute the command.

## Built With

* [Anaconda](https://www.anaconda.com/download/) - The web framework used
* [Visual Studio Code](https://code.visualstudio.com/) - Dependency Management
* [Arduino IDE](https://www.arduino.cc/en/Main/Software?) - Upload firmware to Arduino

## How to use

This application essentially starts a HTTP API in which your are able to make
two type of requests: `execute a state` that will change the color of the arena
and `execute an experiment` that consists in a group of states and its time during
the experiment. So there are two services that can be consumed one for `state`
and one for `experiment` which are going to be described below.

### Color list

This is the avialable colors to use in the API.

| Color  | RGB Representation |
|--------|--------------------|
| NONE   | 0,0,0              |
| RED    | 255,0,0            |
| GREEN  | 0,255,0            |
| BLUE   | 0,0,255            |
| YELLOW | 255,255,0          |
| WHITE  | 255,255,255        |
| OMIT   | -1,-1,-1           |

`note`: the `omit` color simply omit this instruction while the `none` set the
LEDs into black which is equivalent to turn off the LEDs.

### State

The url to execute the change of state is the following:

| Name         | Execute State                                      |
|--------------|----------------------------------------------------|
| URL          | http://localhost:8080/arena-handler/api/v1.0/state |
| Method       | POST                                               |
| Content type | application/json                                   |
| Response     | application/json                                   |


##### Examples

In each request the information of the arena composition is required. Basically
an arena is compounded by:  
`edges`: number of edges  
`blocks`: number of blocks per edge  
`leds`: number of LEDs per block  
`brightness`: LEDs brightness, this apply to every LED. Is not possible to manage
it individually.  
`color`: When this tag is found at the arena level means that the whole arena 
has to be colored with that color.

Below it is the minimum configuration that an arena can have.

```json
{
    "arena": {
        "edges": 3,
        "blocks": 2,
        "leds": 2,
        "color": "red",
        "brightness": 5
    }
}
```
This configuration represents a triangle formed by 2 blocks per edge and 2 LEDs
per block. The birghtness is set to 5 and the color of the aren will be red.

Is it possible to control the arena pointing at its edges.

```json
{
    "arena": {
        "edges": 3,
        "blocks": 2,
        "leds": 2,
        "color": "omit",
        "brightness": 5,
        "edge": [
            {
                "color": "yellow",
                "index": [ 2 ]
            }
        ]
}
```

`edge` is represented as an array of objects where each object represents an edge
of the arena and can have 2 values:
- `color`: the same meaning as in the arena level
- `index`: since the goal is to be able to control the arena very flexibly this
            tag allow us to identify an specific edge of the arena and give it a
            specific color.

Is important to mention that `index` is represented as an array because you can 
to extend the functionality one can indicate range of edges associated to one 
color. So index `index` can actually take three different values:
- [ _first edge of the range_, _final edge of the range_, _steps to generate the range_ ]  

With this functionality one can really make different patterns in few lines of 
code. For instance if one has something like this:  
```json
{
    "arena": {
        "edges": 3,
        "blocks": 2,
        "leds": 2,
        "color": "omit",
        "brightness": 5,
        "edge": [
            {
                "color": "yellow",
                "index": [ 1 ]
            },
            {
                "color": "yellow",
                "index": [ 2 ]
            }
        ]
}
```
It can be shortened as this:
```json
{
    "arena": {
        "edges": 3,
        "blocks": 2,
        "leds": 2,
        "color": "omit",
        "brightness": 5,
        "edge": [
            {
                "color": "yellow",
                "index": [ 1,2 ]
            }
        ]
}
```  
One more important remark is the use of `negative` values to identify edges
```json
{
    "arena": {
        "edges": 3,
        "blocks": 2,
        "leds": 2,
        "color": "omit",
        "brightness": 5,
        "edge": [
            {
                "color": "yellow",
                "index": [ -1,2 ]
            }
        ]
}
```  
Where `-1` represents the last edge of the arena, so this means that the `3,1,2`
edges are going to be colored in that order. Regarded to the `negative` indexes
is important to mention that if you want to go from a greater negative number to 
a less negative number like `[-3,-1]` it is totally necessary to indicate the 
third parameter, the step, which in this case could be `-1` so you will end up 
with the following statement: `[-3,-1,-1]` which will change the edges `1,2,3` 
respectivelly.

Logically an edge is compounded by blocks as well as an arena is compounded by
edges. so we can make this analogy and extend this concept as follows:

```json
{
    "arena": {
        "edges": 3,
        "blocks": 2,
        "leds": 2,
        "color": "omit",
        "brightness": 5,
        "edge": [
            {
                "color": "yellow",
                "index": [ 2 ],
                "block": [
                    {
                        "color": "blue",
                        "index": [ 2 ]
                    }
                ]
            }
        ]
    }
}
```
The block inside the edge its pointing at the second block of the second edge. 
So when a block tag is used inside an edge the block takes as a reference the
index of the parent edge. It is important to mention that `negative` values
are sitll useful in this scenario but it is important to really understand 
what this means. For instance if we change the index block to `-1` this will 
point at the last block of the previous edge, in this case this is would point
at the last block of the first edge since the parent index edge is 2.   
There is an even more complex scenario which is when the parent index of the 
block is a range of edges.

```json
"edge": [
            {
                "color": "yellow",
                "index": [ 1,2 ],
                "block": [
                    {
                        "color": "blue",
                        "index": [ -2 ]
                    }
                ]
            }
        ]
```

For this scenario the first edge of the range is taken as a reference for the
block inside the edge. In this case the reference index is `1` and the index 
block `-2` is pointing at the first block of the last edge taking into account that
we have a triangle arena compounded of 2 blocks per edge.

It is possible to extend the functionality even further pointing not only to 
blocks inside edges but LEDs inside blocks which at the same time are inside an 
edge.

```json
{
    "arena": {
        "edges": 3,
        "blocks": 2,
        "leds": 2,
        "color": "omit",
        "brightness": 5,
        "edge": [
            {
                "color": "yellow",
                "index": [ 2 ],
                "block": [
                    {
                        "color": "blue",
                        "index": [ 2 ],
                        "led": [
                            {
                                "color": "red",
                                "index": [ 1 ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
}
```
The same analogy is done. An edge is compounded by blocks as well as a block is
compunded by LEDs. So all the properties mentioned before apply to this functionality.

Also it is possible to control the arena as a group of blocks and LEDs.

```json
{
    "arena": {
        "edges": 3,
        "blocks": 2,
        "leds": 2,
        "color": "omit",
        "brightness": 5,
        "block": [
            {
                "color": "red",
                "index": [ -1, 1 ]
            }
        ],
        "led": [
            {
                "color": "red",
                "index": [ 1, 2 ]
            }
        ]
    }
}
```

The map shown below summarize the different combinations:

```
├── arena
│   ├── edge
│   │   ├── block
│   │   │   ├── LED
│   ├── block
│   │   │   ├── LED
│   ├── LED
```

`note`: The instructions are executed in document order, so if some instructions are
overlaped the instructions at the end will override the first ones.

### Experiment

The url to execute the change of state is the following:

| Name         | Execute Experiment                                     |
|--------------|--------------------------------------------------------|
| URL          | http://localhost:8080/arena-handler/api/v1.0/experiment|
| Method       | POST                                                   |
| Content type | application/json                                       |
| Response     | application/json                                       |


Since an Experiment is actually an group of states all the properties mentioned
before are still usable in this service.

In order to execute an experiment a new structure has been done:

`experiment`: this object contains the experiment configuration.  
`totalTime`:  this the total amount of seconds the experiment takes.  
`repeat`: this is a boolean variable that allow the experiment to repeat until
the `totalTime` is finished.  
`clean`: this is a boolean variable that is true if the arena has to be cleaned 
at the end of the experiment.  
`states`:  contains the configuration an time for each state.  
`time`:  this is the duration in seconds of the state during the experiment.

`note`: it is important to mention that if the sum of the states time is less than
the `totalTime` the experiment can lasts as much as its last state.

##### Examples

This is a basic example which duration is 30 seconds, since the `repeat` value is 
true the experiment should execute the defined states whose duration is 2 seconds
15 times showing as a result 15 changes from red to green every 2 seconds until 
the `totalTime` is reached.

```json
{
    "experiment": {
        "totalTime": 30,
        "repeat": true,
        "clean": true,
        "states": [
            {
                "time": 2,
                "arena": {
                    "edges": 3,
                    "blocks": 2,
                    "leds": 2,
                    "color": "red",
                    "brightness": 1
                }
            },
            {
                "time": 2,
                "arena": {
                    "edges": 3,
                    "blocks": 2,
                    "leds": 2,
                    "color": "green",
                    "brightness": 1
                }
            }
        ]
    }
}
```

## Authors

* **Keneth Ubeda**
