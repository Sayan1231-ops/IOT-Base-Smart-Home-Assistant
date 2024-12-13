#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <DHT.h>

const char* ssid = "@@@@@@@@@";        
const char* password = "..........";        

ESP8266WebServer server(80);

// GPIO pins for relays and motion sensor
const int fanRelayPin = D8;
const int lightRelayPin = D5;
const int motionSensorPin = D6;

// DHT11 sensor setup
const int DHTPin = D4;
DHT dht(DHTPin, DHT11);

// State variables
bool isFanOn = false;
bool isLightOn = false;

void setup() {
  Serial.begin(115200);

  // Initialize GPIO pins
  pinMode(fanRelayPin, OUTPUT);
  pinMode(lightRelayPin, OUTPUT);
  pinMode(motionSensorPin, INPUT);

  // Turn off relays initially
  digitalWrite(fanRelayPin, HIGH);  // Relay off (assuming LOW triggers the relay)
  digitalWrite(lightRelayPin, HIGH);

  // Start DHT sensor
  dht.begin();

  // Connect to Wi-Fi
  connectToWiFi();

  // Setup server routes
  server.on("/fan/on", handleFanOn);
  server.on("/fan/off", handleFanOff);
  server.on("/light/on", handleLightOn);
  server.on("/light/off", handleLightOff);
  server.on("/motion", handleMotionDetected);
  server.on("/temperature", handleTemperature);

  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}

void connectToWiFi() {
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(ssid);
  Serial.print("MAC Address: ");
  Serial.println(WiFi.macAddress());

  WiFi.begin(ssid, password);

  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    attempt++;

    if (attempt > 20) {  // Retry for ~10 seconds
      Serial.println("\nFailed to connect to Wi-Fi. Restarting...");
      ESP.restart();
    }
  }

  Serial.println("\nConnected to Wi-Fi!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void handleFanOn() {
  digitalWrite(fanRelayPin, LOW);  // LOW to turn relay on
  isFanOn = true;
  server.send(200, "text/plain", "Fan turned on");
}

void handleFanOff() {
  digitalWrite(fanRelayPin, HIGH);  // HIGH to turn relay off
  isFanOn = false;
  server.send(200, "text/plain", "Fan turned off");
}

void handleLightOn() {
  digitalWrite(lightRelayPin, LOW);  // LOW to turn relay on
  isLightOn = true;
  server.send(200, "text/plain", "Light turned on");
}

void handleLightOff() {
  digitalWrite(lightRelayPin, HIGH);  // HIGH to turn relay off
  isLightOn = false;
  server.send(200, "text/plain", "Light turned off");
}

void handleMotionDetected() {
  int motionState = digitalRead(motionSensorPin);
  
  if (motionState == HIGH) {  // Motion detected
    digitalWrite(fanRelayPin, LOW);   // Turn fan on
    digitalWrite(lightRelayPin, LOW); // Turn light on
    isFanOn = true;
    isLightOn = true;
    server.send(200, "text/plain", "Motion detected: Light and fan are now on.");
  } else {
    server.send(200, "text/plain", "No motion detected.");
  }
}

void handleTemperature() {
  float temp = dht.readTemperature();  // Read temperature in Celsius
  if (isnan(temp)) {
    server.send(500, "text/plain", "Error reading temperature.");
    Serial.println("Failed to read temperature!");
  } else {
    // Encode degree symbol for UTF-8
    String tempStr = "Temperature: " + String(temp) + " \u00B0C"; // Unicode for degree symbol
    server.send(200, "text/plain", tempStr); // For web response
    Serial.println(tempStr);                // For Serial Monitor
  }
}

