/*
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleServer.cpp
    Ported to Arduino ESP32 by Evandro Copercini
    updates by chegewara
*/

#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <string.h>
// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define pCHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
#define uS_TO_MS_FACTOR 1000ULL /* Conversion factor for micro seconds to mili seconds */

BLECharacteristic *pCharacteristic; // Write
RTC_DATA_ATTR int data_size = 1;
RTC_DATA_ATTR int period_length = 1000;
bool deviceConnected = false;
bool gotosleep = false;
class MyCallbacks : public BLECharacteristicCallbacks
{
  void onWrite(BLECharacteristic *pCharacteristic)
  {
    std::string value1 = pCharacteristic->getValue();
    String *pvalue = new String(value1.c_str());
    String value = *pvalue;
    if (value.length() > 0)
    {
      if (value.indexOf('#') == -1)
      {
        int index = value.indexOf(';');
        String data_string = value.substring(0, index);
        String period_string = value.substring(index);
        if (data_string.toInt() > 0)
          data_size = data_string.toInt();
        if (period_string.toInt() > 0)
          period_length = period_string.toInt();
      }
    }
    gotosleep = true;
  }
};

class MyServerCallbacks : public BLEServerCallbacks
{
  void onConnect(BLEServer *pServer)
  {
    deviceConnected = true;
  };

  void onDisconnect(BLEServer *pServer)
  {
    deviceConnected = false;
  }
};

void setup()
{
  Serial.begin(115200);
  Serial.println("Starting BLE work!");

  BLEDevice::init("ohneKamera");
  BLEServer *pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
      pCHARACTERISTIC_UUID,
      BLECharacteristic::PROPERTY_READ |
          BLECharacteristic::PROPERTY_WRITE);

  //  pServer->setCallbacks(new MyServerCallbacks());
  // pCharacteristic->setCallbacks(new MyCallbacks());

  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising(); // this still is working for backward compatibility
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x0); // set value to 0x00 to not advertise this parameter
  BLEDevice::startAdvertising();
  delay(2000);
  // if(deviceConnected)
  //{
  pCharacteristic->setValue("ssdf");
  pCharacteristic->notify();
  delay(3000);
  //}
  esp_sleep_enable_timer_wakeup(period_length * uS_TO_MS_FACTOR);
  esp_deep_sleep_start();
}

void loop()
{
  // put your main code here, to run repeatedly:
}