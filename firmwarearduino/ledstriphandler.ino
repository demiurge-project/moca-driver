/*
	LED strip firmware

	This file contains the code to handle a LED strip APA102 using the FastLED 
    library and ArduinoJson. The Arduino essencialy receives a JSON string in
    which the instruction is encoded, via its serial port. Each instruction 
    received represents a block that consits in a fixed amount of LEDs. Using an
    Arduino MEGA is possible to manage up to 960 LED strip where Each LED uses 
    3 bytes of memory.

	The circuit:
    The LED strip APA102 is connected to the Arduino in the follwoing inputs:
	* Data Input => 51
	* Clock Input => 53
    * Ground => GND
    
    The LED strip is connected to an external power supply.

	Created Frebuary 2018
	By Keneth Efrén Ubeda Arriaza

	https://github.com/keua/ledstrip-arena-handler

*/
#include <FastLED.h>
#include <ArduinoJson.h>
#define NUM_LEDS 960
#define DATA_PIN 51
#define CLOCK_PIN 53
#define DEFAULT_BRIGHTNESS 25
#define SRATE 57600

CRGB leds[NUM_LEDS];

/*
    Setting up the baud rate for the serial communication, the input pins,
    brightness and the array of LEDs to handle.
*/
void setup()
{
    Serial.begin(SRATE);
    FastLED.addLeds<APA102, DATA_PIN, CLOCK_PIN, BGR>(leds, NUM_LEDS);
    LEDS.setBrightness(DEFAULT_BRIGHTNESS);
}

void loop() {}

/*
    This is method receives the serial string which is parsed firstly as a 
    JSON to subsequently be interpreted and executed using the FastLED library.
    Each time the method execute the instruction, a messaege to the serial port
    is printed as an aknowledge of the request the same if any error ocurrs.
*/
void serialEvent()
{
    while (Serial.available() > 0)
    {
        StaticJsonBuffer<300> jsonBuffer;
        JsonObject &root = jsonBuffer.parseObject(Serial);

        if (!root.success())
        {
            Serial.println("parseObject() failed");
            return;
        }

        int brightness = root["brightness"];
        const char *block = root["block"];
        int blockIndex;
        int blockSize;
        int blockColor[3];

        int index = 0;
        int comma = 0;
        boolean omit = false;
        String tmp = "";
        do
        {
            if (block[index] == ',')
            {
                comma++;
                index++;
                if (comma == 1)
                {
                    blockIndex = tmp.toInt();
                }
                else if (comma == 2)
                {
                    blockSize = tmp.toInt();
                }
                else if (comma == 3)
                {
                    (tmp.toInt() < 0) ? omit = true : omit = false;
                    blockColor[0] = tmp.toInt();
                }
                else if (comma == 4)
                {
                    blockColor[1] = tmp.toInt();
                }
                tmp = "";
            }
            else
            {
                tmp.concat(block[index]);
                index++;
            }
            if (block[index] == '\0')
            {
                blockColor[2] = tmp.toInt();
                ;
            }
        } while (block[index] != '\0');

        for (int i = blockIndex * blockSize; i < (blockIndex * blockSize) + blockSize && !omit; i++)
        {
            leds[i].setRGB(blockColor[0], blockColor[1], blockColor[2]);
        }

        JsonArray &bLeds = root["led"];
        for (auto &led : bLeds)
        {
            int lIndex;
            int ledColor[3];
            const char *cLed = led;

            int index = 0;
            int comma = 0;
            String tmp = "";

            do
            {
                if (cLed[index] == ',')
                {
                    comma++;
                    index++;
                    if (comma == 1)
                    {
                        lIndex = tmp.toInt();
                    }
                    else if (comma == 2)
                    {
                        ledColor[0] = tmp.toInt();
                    }
                    else if (comma == 3)
                    {
                        ledColor[1] = tmp.toInt();
                    }
                    tmp = "";
                }
                else
                {
                    tmp.concat(cLed[index]);
                    index++;
                }
                if (cLed[index] == '\0')
                {
                    ledColor[2] = tmp.toInt();
                }
            } while (cLed[index] != '\0');
            // This line is in charge to convert the led index from a block 
            // relative postion to an absolute position since each instruction
            // represents a block.
            leds[(blockIndex * blockSize) + lIndex].setRGB(ledColor[0], ledColor[1], ledColor[2]);
        }
        LEDS.setBrightness(brightness);
        FastLED.show();
        Serial.println("Instruction executed successfully!");
    }
}