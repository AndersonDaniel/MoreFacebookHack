/*
 *  This sketch demonstrates how to set up a simple HTTP-like server.
 *  The server will set a GPIO pin depending on the request
 *    http://server_ip/gpio/0 will set the GPIO2 low,
 *    http://server_ip/gpio/1 will set the GPIO2 high
 *  server_ip is the IP address of the ESP8266 module, will be 
 *  printed to Serial when the module is connected.
 */

#include <ESP8266WiFi.h>

const char* ssid = "fbguest";
const char* password = "m0vefast";
String s;

// Create an instance of the server
// specify the port to listen on as an argument
WiFiServer server(80);

void setup() {
  // init water pump
  pinMode(D1, OUTPUT); // PHASE  -A
  pinMode(D2, OUTPUT); // ENBL   -A
  pinMode(D3, OUTPUT); // PHASE  -B
  pinMode(D4, OUTPUT); // ENBL   -B
  
  analogWrite(D4, 0);
  analogWrite(D2, 0);
  
  Serial.begin(115200);
  delay(10);

  // prepare GPIO2
  pinMode(2, OUTPUT);
  digitalWrite(2, 0);
  
  // Connect to WiFi network
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  
  // Start the server
  server.begin();
  Serial.println("Server started");

  // Print the IP address
  Serial.println(WiFi.localIP());
}

void loop() {
  analogWrite(D2, 0);
  analogWrite(D4, 0);
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    return;
  }
  
  // Wait until the client sends some data
  Serial.println("new client");
  while(!client.available()){
    delay(1);
  }
  
  // Read the first line of the request
  String req = client.readStringUntil('\r');
  Serial.println(req);
  client.flush();
  
  // Match the request
  int val;
  if (req.indexOf("/cmd/0") != -1)
  {
    Serial.println("front");
    val = 0;
    digitalWrite(D1, HIGH);
    digitalWrite(D3, HIGH);
    analogWrite(D2, 800);
    analogWrite(D4, 800);
    delay(1000);
    analogWrite(D2, 0);
    analogWrite(D4, 0);
  }
  else if (req.indexOf("/cmd/1") != -1)
    {
      Serial.println("back");
      val = 1;
     digitalWrite(D1, LOW);
    digitalWrite(D3, LOW);
    analogWrite(D2, 800);
    analogWrite(D4, 800);
    delay(1000);  
    analogWrite(D2, 0);
    analogWrite(D4, 0);
  }
  else if (req.indexOf("/favicon.ico") != -1) {
    Serial.println("fav");
    val = 2;
  }
  else {
    Serial.println("err");
    val = 3;
//    client.stop();
//    return;
  }
  
  client.flush();

  // Prepare the response
  s = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<!DOCTYPE HTML>\r\n<html>\r\n";
  switch (val) {
    case 0:
      s+= "Direction is now front";
      break;
    case 1:
      s+= "Direction is now back";
      break;
     case 2:
      s+= "fav";
      break;
     case 3:
      s+= "error 3";
      break;
    default: 
      s+= "general error";
      // default is optional
    break;
  }
  
  s += "</html>\n";

  // Send the response to the client
  client.print(s);
  delay(1);
  Serial.println("Client disonnected");
  analogWrite(D2, 0);
  analogWrite(D4, 0);
//  return;
  // The client will actually be disconnected 
  // when the function returns and 'client' object is detroyed
}

