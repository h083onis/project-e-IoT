#include <M5Stack.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <ArduinoJson.h>

#include <time.h>

#define M5NUMBER 1
#define JST (3600L * 9)

const char* ssid = "";
const char* password = "";

const char* host = "";  // サーバーのIPアドレス
const int port = 8888;              // サーバーのポート番号
const char* endpoint = "/";
int scanTime = 5;                   // スキャン時間（秒）
BLEScan* pBLEScan;

struct tm time1, time2; 

void setup() {
  // M5Stackの初期化
  M5.begin();
  Serial.begin(115200);
  while (!Serial) {
    ; // シリアルポートが接続されるのを待つ（必要に応じて）
  }
  // Serial.println("BLE Scan");

  // BLEの初期化
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(true); // アクティブスキャンを設定

  WiFi.begin(ssid, password);

  // Wi-Fi接続待機
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  //Serial.println("");
  //Serial.println("WiFi connected");
  //Serial.println("IP address: ");
  //Serial.println(WiFi.localIP());
  getLocalTime(&time1);
}

void loop() {

  char buffer[80];
  configTime(JST, 0, "ntp.nict.jp", "time.google.com", "ntp.jst.mfeed.ad.jp");

  while(1){
    configTime(JST, 0, "ntp.nict.jp", "time.google.com", "ntp.jst.mfeed.ad.jp");
    if(getLocalTime(&time2)){
      if( difftime(mktime(&time2), mktime(&time1)) >= 10 ){
        time1 = time2;
        break;
      } 
    }
  }

  //Serial.println("Scanning...");
  BLEScanResults foundDevices = pBLEScan->start(scanTime, false);

  //Serial.printf("Devices found: %d\n", foundDevices.getCount());

  StaticJsonDocument<4096> jsonDoc;  // メモリサイズを拡張
  JsonArray jsonArray = jsonDoc.createNestedArray("devices");

  for (int i = 0; i < foundDevices.getCount(); i++) {
    BLEAdvertisedDevice device = foundDevices.getDevice(i);
    
    JsonObject deviceObj = jsonArray.createNestedObject();
    String name = device.getName().c_str();
    String address = device.getAddress().toString().c_str();
    int rssi = device.getRSSI();
    
    if (name.length() == 0) {
      name = "Unknown";
    }
    
    deviceObj["name"] = name;
    deviceObj["address"] = address;
    deviceObj["rssi"] = rssi;
    
    //Serial.printf("Name: %s, Address: %s, RSSI: %d\n", name.c_str(), address.c_str(), rssi);
  }
  
  //時間情報を文字列にして，JSONに入れる
  strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", &time2);
  jsonDoc["time"] = buffer;
  jsonDoc["M5-number"] = M5NUMBER;

  //Serial.printf("JSON Data\n");
  serializeJsonPretty(jsonDoc, Serial);

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    String url = String("http://") + host + ":" + port + endpoint;
    http.begin(url);

    http.addHeader("Content-Type", "application/json");

    String jsonString;
    serializeJson(jsonDoc, jsonString);

    int httpResponseCode = http.POST(jsonString);

    if (httpResponseCode > 0) {
      String response = http.getString();
      //Serial.println("Response:");
      //Serial.println(response);
    } else {
      //Serial.print("Error on sending POST: ");
      //Serial.println(httpResponseCode);
    }

    http.end();
  }

}