/*
  Reading multiple RFID tags, simultaneously!
  By: Nathan Seidle @ SparkFun Electronics
  Date: October 3rd, 2016
  https://github.com/sparkfun/Simultaneous_RFID_Tag_Reader

  Constantly reads and outputs any tags heard

  If using the Simultaneous RFID Tag Reader (SRTR) shield, make sure the serial slide
  switch is in the 'SW-UART' position

  This code uses a modified version of the SparkFun_UHF_RFID_Reader library.
  Versions downloaded online from SparkFun or the GitHub link above will not work.
*/

// LIBRARIES
#include "SparkFun_UHF_RFID_Reader.h" //Library for controlling the M6E Nano module

#ifdef ENV_ARDUINO_UNO
#include <SoftwareSerial.h>           //If you run into compilation errors regarding this include, see README
#endif

// PINS
#define SERIAL_RX 2
#define SERIAL_TX 3

// CONSTANTS
#define COUNT_MAX 500     // Maximum amount of tags to be scanned before stopping
#define TX_POWER 2700     // Values higher than 500 may damage USB. Max power is 27 dBm (2700) and may cause throttling
#define DEFAULT_FORMAT 0  // Print to serial monitor with all necessary labels
#define CSV_FORMAT 1      // Print to serial monitor as csv and stop when COUNT_MAX tags have been scanned

// GLOBAL VARIABLES
bool formatCheck = 0;     // Determines if data is printed to serial monitor as csv (1) or with labels (0)
int scanCount = 1;        // Tracks amount of tags scanned

SoftwareSerial softSerial(SERIAL_RX, SERIAL_TX); // Serial communication (RX, TX) on digital pins
RFID nano;                       // Create instance



//Prints information from scanned tags to serial monitor with relevant labels
//This will print errors and idle notes as well, this should be used if printing to serial
//monitor in csv format is not necessary.
void printWithLabels() {
  int rssi = nano.getTagRSSI(); //Get the RSSI for this tag read
  long freq = nano.getTagFreq(); //Get the frequency this tag was detected at
  long timeStamp = nano.getTagTimestamp(); //Get the time this was read, (ms) since last keep-alive message
  byte tagEPCBytes = nano.getTagEPCBytes(); //Get the number of bytes of EPC from response
  long phase = nano.getTagPhase();  //Get received tag phase from 0 to 180 degrees

  Serial.print(F(" count["));
  Serial.print(scanCount++);
  Serial.print(F("]"));

  Serial.print(F(" time["));
  Serial.print(millis());
  Serial.print(F("]"));

  Serial.print(F(" rssi["));
  Serial.print(rssi);
  Serial.print(F("]"));

  Serial.print(F(" freq["));
  Serial.print(freq);
  Serial.print(F("]"));

  Serial.print(F(" timestamp["));
  Serial.print(timeStamp);
  Serial.print(F("]"));

  //Print EPC bytes, this is a subsection of bytes from the response/msg array
  Serial.print(F(" epc["));
  for (byte x = 0 ; x < tagEPCBytes ; x++)
  {
    if (nano.msg[31 + x] < 0x10) Serial.print(F("0")); //Pretty print
    Serial.print(nano.msg[31 + x], HEX);
    Serial.print(F(" "));
  }
  Serial.print(F("]"));

  Serial.print(F(" phase["));
  Serial.print(phase);
  Serial.print(F("]"));

  Serial.println();
}

//Prints information from scanned tags to serial monitor in CSV format with header. 
//This will not print errors and will remain idle if no tags are being scanned
void printAsCSV() {
  int rssi = nano.getTagRSSI(); //Get the RSSI for this tag read
  long freq = nano.getTagFreq(); //Get the frequency this tag was detected at
  long timeStamp = nano.getTagTimestamp(); //Get the time this was read, (ms) since last keep-alive message
  byte tagEPCBytes = nano.getTagEPCBytes(); //Get the number of bytes of EPC from response
  long phase = nano.getTagPhase();  //Get received tag phase from 0 to 180 degrees

  Serial.print(scanCount++);
  Serial.print(",");
  Serial.print(millis());
  Serial.print(",");
  Serial.print(rssi);
  Serial.print(",");
  Serial.print(freq);
  Serial.print(",");
  Serial.print(timeStamp);
  Serial.print(",");
  for (byte x = 0 ; x < tagEPCBytes ; x++)
  {
    if (nano.msg[31 + x] < 0x10) Serial.print(F("0")); //Pretty print
    Serial.print(nano.msg[31 + x], HEX);
    Serial.print(F(" "));
  }
  Serial.print(",");
  Serial.print(phase);
  Serial.print("\n");
}

//Gracefully handles a reader that is already configured and already reading continuously. 
//Because Stream does not have a .begin() we have to do this outside the library
boolean setupNano(long baudRate)
{
  nano.begin(softSerial); //Tell the library to communicate over software serial port

  //Test to see if we are already connected to a module
  //This would be the case if the Arduino has been reprogrammed and the module has stayed powered
  softSerial.begin(baudRate); //For this test, assume module is already at our desired baud rate
  while (softSerial.isListening() == false); //Wait for port to open

  //About 200ms from power on the module will send its firmware version at 115200. We need to ignore this.
  while (softSerial.available()) softSerial.read();

  nano.getVersion();

  if (nano.msg[0] == ERROR_WRONG_OPCODE_RESPONSE)
  {
    //This happens if the baud rate is correct but the module is doing a continuous read
    nano.stopReading();

    Serial.println(F("Module continuously reading. Asking it to stop..."));

    delay(1500);
  }
  else
  {
    //The module did not respond so assume it's just been powered on and communicating at 115200bps
    softSerial.begin(115200); //Start software serial at 115200

    nano.setBaud(baudRate); //Tell the module to go to the chosen baud rate. Ignore the response msg

    softSerial.begin(baudRate); //Start the software serial port, this time at user's chosen baud rate

    delay(250);
  }

  //Test the connection
  nano.getVersion();
  if (nano.msg[0] != ALL_GOOD) return (false); //Something is not right

  //The M6E has these settings no matter what
  nano.setTagProtocol(); //Set protocol to GEN2
  nano.setAntennaPort(); //Set TX/RX antenna ports to 1

  return (true); //We are ready to rock
}


// ----------------- LOOPS -----------------

void setup()
{
  Serial.begin(115200);
  while (!Serial); //Wait for the serial port to come online

  if (setupNano(38400) == false) //Configure nano to run at 38400bps
  {
    Serial.println(F("Module failed to respond. Please check wiring."));
    while (1); //Freeze!
  }

  nano.setRegion(REGION_NORTHAMERICA); //Set to North America
  nano.setReadPower(TX_POWER);

  // Wait for user to entire character to continue
  Serial.println(F("If datalogging with PuTTY or other terminal emulator, run it now. Press a key to begin scanning for tags. "));
  while (!Serial.available());
  Serial.read();

  // Print CSV header
  if(formatCheck) {
    Serial.print("Count, Time (ms), RSSI (dBm), Frequency (KHz), Timestamp (ms), EPC, Phase (Degrees)\n"); 
  }

  nano.startReading(); //Begin scanning for tags
}

void loop() {
  if (nano.check() == true) {
    byte responseType = nano.parseResponse();

    switch (responseType) {

      case RESPONSE_IS_KEEPALIVE:
        if (!formatCheck)
        Serial.println(F("Scanning"));
        break;

      case RESPONSE_IS_TAGFOUND:
        if (formatCheck == CSV_FORMAT && scanCount <= COUNT_MAX) {
          printAsCSV();
        }
        // If maximum count has been reached, reset counter and pause scanning until user inputs to serial monitor
        else if (formatCheck == CSV_FORMAT && scanCount > COUNT_MAX) {
          scanCount = 1;
          nano.stopReading();

          while (!Serial.available());      //Wait for user to send a character
          Serial.read();                    //Throw away the user's character

          Serial.print("Count, Time (ms), RSSI (dBm), Frequency (KHz), Timestamp (ms), EPC, Phase (Degrees)\n");
          nano.startReading();
        }
        else if (formatCheck == DEFAULT_FORMAT) {
          printWithLabels();
        }
        break;

      case ERROR_CORRUPT_RESPONSE:
        if (!formatCheck)
        Serial.println("Bad CRC");
        break;

      // I have no idea what the difference between the next two responses are
      case RESPONSE_IS_TEMPTHROTTLE:
        Serial.println("TEMPERATURE THROTTLE");
        break;

      case RESPONSE_IS_TEMPERATURE:
        Serial.println("TEMPERATURE");
        break;

      default:
        if (!formatCheck)
        Serial.println("Unknown Error");

    }
  }
} 