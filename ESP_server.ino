#define BLYNK_TEMPLATE_ID "TMPL3AsaGNlI4"
#define BLYNK_TEMPLATE_NAME "Quickstart Template"

#include <WiFi.h>
#include <WebServer.h>
#include <BlynkSimpleEsp32.h>


// WiFi Credentials
const char* ssid = "Chandrahaas's WIFI";
const char* password = "12345678";

// Blynk Credentials
#define BLYNK_AUTH_TOKEN "pNePuOq_dqNIv0DTtzd1-AYQpdNpzAKX"

// Web Server
WebServer server(80);

// Global Status
String statusMessage = "System Ready";
unsigned long lastUpdateTime = 0;
const unsigned long resetInterval = 5000;  // Reset after 5 seconds
bool intruderDetected = false;  // Prevent duplicate notifications

void handleRoot() {
  String html = "<html><head>";
  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<style>";
  html += "body { font-family: Arial, sans-serif; text-align: center; background-color: #121212; color: white; }";
  html += ".container { margin-top: 50px; }";
  html += ".status-box { padding: 20px; border-radius: 10px; font-size: 24px; font-weight: bold; }";

  if (statusMessage.startsWith("Authorized")) {
    html += ".status-box { background-color: #4CAF50; color: white; }";  // Green
  } else if (statusMessage == "Intruder") {
    html += ".status-box { background-color: #FF5733; color: white; }";  // Red
  } else {
    html += ".status-box { background-color: #2196F3; color: white; }";  // Blue
  }

  html += "</style>";
  html += "<script>";
  html += "setInterval(() => { fetch('/status').then(response => response.text()).then(data => { document.getElementById('status').innerHTML = data; }); }, 1000);";  // Auto-refresh
  html += "</script>";
  html += "</head><body>";
  html += "<div class='container'>";
  html += "<h1>ESP32 Security System</h1>";
  html += "<div class='status-box' id='status'>Status: " + statusMessage + "</div>";
  html += "</div></body></html>";

  server.send(200, "text/html", html);
}

void handleStatus() {
  server.send(200, "text/plain", "Status: " + statusMessage);
}

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWiFi Connected!");
  Serial.println(WiFi.localIP());

  // Blynk Setup
  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, password);

  // Web Server Setup
  server.on("/", handleRoot);
  server.on("/status", handleStatus);
  server.begin();
}

void loop() {
  server.handleClient();
  Blynk.run();

  // Read Serial Data
  while (Serial.available() > 0) {
    String incoming = Serial.readStringUntil('\n');
    incoming.trim();

    if (incoming.length() > 0) {
      statusMessage = incoming;  // Update Web UI
      lastUpdateTime = millis(); // Reset timeout

      if (incoming.startsWith("Authorized")) {
        Blynk.virtualWrite(V1, 0);  // Turn OFF intruder LED
        intruderDetected = false;   // Reset flag
      } else if (incoming == "Intruder") {
        if (!intruderDetected) {
          Blynk.logEvent("intruder_alert", "🚨 Intruder Detected! 🚨");
          Blynk.virtualWrite(V1, 255); // Turn ON Virtual LED
          intruderDetected = true; // Prevent multiple notifications
        }
      }
      Serial.println("Received: " + incoming);
    }
  }

  // Auto-reset to "System Ready" if no update in 5 seconds
  if (millis() - lastUpdateTime > resetInterval) {
    if (statusMessage != "System Ready") {
      statusMessage = "System Ready";
      Blynk.virtualWrite(V1, 0);  // Reset Virtual LED
      intruderDetected = false;  // Reset flag
    }
  }
}
