#include <Arduino.h>         // required before wiring_private.h
#include "wiring_private.h"  // pinPeripheral() function
#include <TinyGPSPlus.h>
#include <SparkFun_Bio_Sensor_Hub_Library.h>
#include <Wire.h>
#include <SPI.h>
#include <WiFi101.h>


// Define pins
#define gpsRX 10
#define gpsTX 11
#define resPin 12
#define mfioPin 13
#define tempPin A3
#define rl 6
#define ol 5
#define yl A1
#define gl A2


// Initialize classes
Uart gpsSerial(&sercom1, gpsRX, gpsTX, SERCOM_RX_PAD_2, UART_TX_PAD_0);
SparkFun_Bio_Sensor_Hub bioHub(resPin, mfioPin);
WiFiServer server(80);
TinyGPSPlus gps;


// Averaging variables
const int A_max = 10;
float celciusvalues[A_max];
int arraysize = 0;
float celcius_average;
int j = 0;
float celcius_sum;


//Timer variables
unsigned long sensorPrintMillis;
const unsigned long SENSOR_PRINT_PERIOD = 1000;


// Bio-sensor
bioData body;
char buffer[4];  // for the format function
char* formatForPrint(int foo) {
  sprintf(buffer, "%03d", foo);
  return buffer;
}


// GPS
float latitude_float;  // Variables for storing location and speed
float longitude_float;
float mps_float;
float DISASTER_NSEW[4] = { 56.1723, 56.1722, 10.1915, 10.1913 };  // Boundaries for the disaster and evacuation area
float EVACUATION_NSEW[4] = { 56.1723, 56.1722, 10.1916, 10.1915 };
float D35_NSEW[4] = { 56.1698, 56.1696, 10.1974, 10.1968 };  // Secondary boundaries
float E31_NSEW[4] = { 56.1696, 56.1693, 10.1975, 10.1970 };
bool inDisaster;  // Bools for storing location and movement flags
bool inEvac;
bool moving;
bool inArea(float NSEW[4]) {  // Returns true if current location is within arbitrary bounding box
  bool inNS = (latitude_float < NSEW[0]) && (latitude_float > NSEW[1]);
  bool inEW = (longitude_float < NSEW[2]) && (longitude_float > NSEW[3]);
  return inNS && inEW;
}
// Functions for handling data on the UART port
void SERCOM1_0_Handler() {
  gpsSerial.IrqHandler();
}
void SERCOM1_1_Handler() {
  gpsSerial.IrqHandler();
}
void SERCOM1_2_Handler() {
  gpsSerial.IrqHandler();

  // This code ensures the gps class always has the newest data from the gps module
  while (gpsSerial.available() > 0) {
    gps.encode(gpsSerial.read());
    if (gps.location.isUpdated()) {
      latitude_float = gps.location.lat();
      longitude_float = gps.location.lng();
      mps_float = gps.speed.mps();
    }
  }
}
void SERCOM1_3_Handler() {
  gpsSerial.IrqHandler();
}


// Temp sensor
float temp;
float getTemp() {
  long input;
  float val;

  input = analogRead(tempPin);
  val = input * (3.43 / 1023.0);
  val = (val - 0.5) * 100;
  return val;
}
void SendInfo() {
  celciusvalues[j] = temp;
  j += 1;
  arraysize += 1;
  if (arraysize == A_max) {
    for (int i = 0; i < A_max; i++) {
      celcius_sum += celciusvalues[i];
    }
    celcius_average = celcius_sum / A_max;
    celcius_sum = 0;
    j = 0;
    arraysize = 0;
  }
}


// Triage
int triageStatus;
int previouscolor;
bool led_on = false;
int triage() {
  if ((body.status == 3) && (body.confidence > 0)) {
    if (body.oxygen < 80)
      return 1;  // Red = 1

    if (body.heartRate > 140)
      return 1;

    if (celcius_average < 32)
      return 1;

    if (body.oxygen < 90)
      return 2;  // Orange = 2

    if ((body.heartRate < 40) || (body.heartRate > 120))
      return 2;

    if ((celcius_average < 34) || (temp > 40))
      return 2;

    if (body.oxygen < 95)
      return 3;  // Yellow = 3

    if ((body.heartRate < 50) || (body.heartRate > 110))
      return 3;

    if ((celcius_average < 35) || (temp > 38))
      return 3;

    return 4;  // Green = 4
  }
}
void Blink(int i) {
  if (led_on) {
    digitalWrite(i, LOW);
    led_on = false;
  } else {
    digitalWrite(i, HIGH);
    led_on = true;
  }
}


// WiFi
char ssid[] = "TriageArmband";  // network name
char pass[] = "WakeMeUp";       // network password
int status = WL_IDLE_STATUS;
void printWiFiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your WiFi shield's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
  // print where to go in a browser:
  Serial.print("To see this page in action, open a browser to http://");
  Serial.println(ip);
}
void printMacAddress(byte mac[]) {
  for (int i = 5; i >= 0; i--) {
    if (mac[i] < 16) {
      Serial.print("0");
    }
    Serial.print(mac[i], HEX);
    if (i > 0) {
      Serial.print(":");
    }
  }
  Serial.println();
}


void setup() {
  Serial.begin(9600);

  Wire.begin();  // Initiate wire


  // GPS
  gpsSerial.begin(9600);
  pinPeripheral(gpsRX, PIO_SERCOM);
  pinPeripheral(gpsTX, PIO_SERCOM);


  // Bio-sensor
  int result = bioHub.begin();
  if (result == 0)  // Zero errors!
    Serial.println("Bio-sensor started!");
  else
    Serial.println("Could not communicate with the Bio-sensor!");

  Serial.println("Configuring Bio-sensor....");
  int error = bioHub.configBpm(MODE_ONE);  // MODE_ONE or MODE_TWO
  if (error == 0) {                        // Zero errors?
    Serial.println("Bio-sensor configured.");
  } else {
    Serial.println("Error configuring Bio-sensor.");
    Serial.print("Error: ");
    Serial.println(error);
  }
  // Serial.println("Bio-sensor: Loading up the buffer with data....");
  // delay(4000);


  // Temperature sensor
  pinMode(tempPin, INPUT);


  // Triage
  pinMode(rl, OUTPUT);
  pinMode(ol, OUTPUT);
  pinMode(yl, OUTPUT);
  pinMode(gl, OUTPUT);


  // WiFI
  WiFi.setPins(0, 1, 9, 4);
  Serial.println("WiFi: Access Point Web Server");
  // check for the presence of the WiFi module:
  if (WiFi.status() == WL_NO_SHIELD) {
    Serial.println("WiFi shield not present");
    while (true) {}
  }
  Serial.print("Creating access point named: ");
  Serial.println(ssid);
  status = WiFi.beginAP(ssid, pass);
  if (status != WL_AP_LISTENING) {
    Serial.println("Creating access point failed");
    // don't continue
    while (true) {}
  }
  server.begin();  // start the web server on port 80
  printWiFiStatus();
  delay(10000);  // wait 10 seconds for connection
}


void loop() {
  if (millis() - sensorPrintMillis >= SENSOR_PRINT_PERIOD) {
    // Get values from sensors
    body = bioHub.readBpm();
    temp = getTemp();
    SendInfo();
    // Is patient in either disaster or evacuation area?
    inDisaster = inArea(DISASTER_NSEW);
    inEvac = inArea(EVACUATION_NSEW);
    // inDisaster = inArea(D35_NSEW);
    // inEvac = inArea(E31_NSEW);

    moving = mps_float > 1;  // Is the patient moving?
    triageStatus = triage();


    // Print sensor data on the serial port
    Serial.println();
    Serial.print("Heartrate: ");
    Serial.print(formatForPrint(body.heartRate));
    Serial.print("  Oxygen: ");
    Serial.print(formatForPrint(body.oxygen));
    Serial.print("  Confidence: ");
    Serial.print(formatForPrint(body.confidence));
    Serial.print("  Status: ");
    Serial.println(formatForPrint(body.status));
    Serial.print("Temp: ");
    Serial.print(celcius_average);
    Serial.println(" C");

    Serial.print("Location: ");
    Serial.print(latitude_float, 5);
    Serial.print(", ");
    Serial.println(longitude_float, 5);
    if (inDisaster) {
      Serial.println("Patient is in disaster area.");
    } else if (inEvac) {
      Serial.println("Patient is in evacuation area.");
      Serial.println("Please remove vital sensors from the patient.");
    }
    if (moving) {
      Serial.println("Patient is moving.");
    }

    Serial.print("Triage Status: ");
    switch (triageStatus) {
      case 1:
        Serial.println("RED");
        digitalWrite(rl, HIGH);  //Red
        digitalWrite(ol, LOW);   //Orange
        digitalWrite(yl, LOW);   //Yellow
        digitalWrite(gl, LOW);   //Green
        previouscolor = rl;
        break;
      case 2:
        Serial.println("ORANGE");
        digitalWrite(rl, LOW);   //Red
        digitalWrite(ol, HIGH);  //Orange
        digitalWrite(yl, LOW);   //Yellow
        digitalWrite(gl, LOW);   //Green
        previouscolor = ol;
        break;
      case 3:
        Serial.println("YELLOW");
        digitalWrite(rl, LOW);   //Red
        digitalWrite(ol, LOW);   //Orange
        digitalWrite(yl, HIGH);  //Yellow
        digitalWrite(gl, LOW);   //Green
        previouscolor = yl;
        break;
      case 4:
        Serial.println("GREEN");
        digitalWrite(rl, LOW);   //Red
        digitalWrite(ol, LOW);   //Orange
        digitalWrite(yl, LOW);   //Yellow
        digitalWrite(gl, HIGH);  //Green
        previouscolor = gl;
        break;
      default:
        Serial.println("UNKNOWN/ERROR");
        digitalWrite(rl, LOW);  //Red
        digitalWrite(ol, LOW);  //Orange
        digitalWrite(yl, LOW);  //Yellow
        digitalWrite(gl, LOW);  //Yellow
        Blink(previouscolor);
        break;
    }
    sensorPrintMillis = millis();
  }

  // WiFi
  if (status != WiFi.status()) {  // compare the previous status to the current status
    status = WiFi.status();       // it has changed update the variable
    if (status == WL_AP_CONNECTED) {
      byte remoteMac[6];

      // a device has connected to the AP
      Serial.print("Device connected to AP, MAC address: ");
      WiFi.APClientMacAddress(remoteMac);
      printMacAddress(remoteMac);
    } else {
      // a device has disconnected from the AP, and we are back in listening mode
      Serial.println("Device disconnected from AP");
    }
  }

  WiFiClient client = server.available();  // listen for incoming clients

  if (client) {                    // if you get a client,
    Serial.println("new client");  // print a message out the serial port
    String currentLine = "";       // make a String to hold incoming data from the client
    while (client.connected()) {   // loop while the client's connected
      if (client.available()) {    // if there's bytes to read from the client,
        char c = client.read();    // read a byte, then
        Serial.write(c);           // print it out the serial monitor
        if (c == '\n') {           // if the byte is a newline character

          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            // client.println("Refresh: 5");  // Refresh webpage in browser every 5 secs
            client.println();

            //Sending the data
            client.print("<p>");
            client.print(latitude_float, 5);
            client.print("</p><p>");
            client.print(longitude_float, 5);
            client.print("</p><p>");
            client.print(celcius_average);
            client.print("</p><p>");
            client.print(body.oxygen);
            client.print("</p><p>");
            client.print(body.heartRate);
            client.print("</p>");
            switch (triageStatus) {
              case 1:
                client.print("<p>Immediate Evacuation</p>");
                client.print("<p>red</p>");
                break;
              case 2:
                client.print("<p>Urgent Evacuation</p>");
                client.print("<p>orange</p>");
                break;
              case 3:
                client.print("<p>Soon Evacuation</p>");
                client.print("<p>yellow</p>");
                break;
              case 4:
                client.print("<p>Can wait</p>");
                client.print("<p>green</p>");
                break;
              default:
                client.print("<p>Status Unknown</p>");
                client.print("<p>grey</p>");
                break;
            }
            if (inDisaster) {  // Is patient in disaster area?
              client.print("<p>Patient is in disaster area.</p>");
            } else if (inEvac) {  // Is patient in evacuation area?
              client.print("<p>Patient is in evacuation area!</p>");
            } else {
              client.print("<p>Patient is unaccounted for</p>");
            }
            if (moving) {  // Is patient moving?
              client.print("<p>PATIENT IS MOVING.</p>");
            } else {
              client.print("<p>Patient awaiting rescue</p>");
            }
            client.print("<p>");
            client.print(body.confidence);
            client.print("</p><p>");
            client.print(body.status);
            client.print("</p>");


            // The HTTP response ends with another blank line:
            client.println();
            // break out of the while loop:
            break;

          } else {  // if you got a newline, then clear currentLine:
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    // close the connection:
    client.stop();
    Serial.println("client disconnected");
  }
}