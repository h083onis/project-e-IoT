#include <M5Stack.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>
#include <ArduinoJson.h>

int scanTime = 5; // スキャン時間（秒）
BLEScan* pBLEScan;

void setup() {
  // M5Stackの初期化
  M5.begin();
  M5.Lcd.setTextSize(2);
  M5.Lcd.println("BLE Scan");

  // シリアル通信の初期化
  Serial.begin(115200);
  while (!Serial) {
    ; // シリアルポートが接続されるのを待つ（必要に応じて）
  }
  Serial.println("BLE Scan");

  // BLEの初期化
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(true); // アクティブスキャンを設定
}

void loop() {
  M5.Lcd.clearDisplay();
  M5.Lcd.setCursor(0, 0);

  // スキャンを開始
  M5.Lcd.println("Scanning...");
  Serial.println("Scanning...");
  BLEScanResults foundDevices = pBLEScan->start(scanTime, false);

  // 見つかったデバイスの情報を表示
  M5.Lcd.printf("Devices found: %d\n", foundDevices.getCount());
  Serial.printf("Devices found: %d\n", foundDevices.getCount());

  JsonDocument jsonDoc;
  JsonArray jsonArray = jsonDoc.to<JsonArray>();

  for (int i = 0; i < foundDevices.getCount(); i++) {
    BLEAdvertisedDevice device = foundDevices.getDevice(i);
    Serial.printf("%s\n", device.toString().c_str());
    M5.Lcd.printf("%s\n", device.toString().c_str());
    jsonArray.add(device.toString().c_str());
  }

  M5.Lcd.printf("JSON Data");
  Serial.printf("JSON Data");
  serializeJsonPretty(jsonDoc, M5.Lcd);
  serializeJsonPretty(jsonDoc, Serial);
  M5.Lcd.printf("\n");
  Serial.printf("\n");

  // 一定時間待機
  delay(10000);
}