#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_ADS1X15.h>
#include <max6675.h>

// Voltage sensor vars
Adafruit_ADS1115 ads;
const float multiplier = 0.03125F;
const float m = 36.639683818368326;
const float b = 0.0025398659284849856;
float voltm;

// Temperature sensors vars
int ktcSO = 19;  // MISO
int ktcCLK = 18; // SCK
int csPins[6] = {5, 17, 16, 4, 2};
MAX6675 thermocouple1(ktcCLK, csPins[0], ktcSO);
MAX6675 thermocouple2(ktcCLK, csPins[1], ktcSO);
MAX6675 thermocouple3(ktcCLK, csPins[2], ktcSO);
MAX6675 thermocouple4(ktcCLK, csPins[3], ktcSO);
MAX6675 thermocouple5(ktcCLK, csPins[4], ktcSO);

void setup(void)
{
  Serial.begin(115200);
  ads.setGain(GAIN_FOUR); // +/- 1.024V  1 bit = 0.03125mV
  ads.begin();

  delay(1000);
}
void loop(void)
{
  int16_t adc0;
  double temps[6];

  adc0 = ads.readADC_SingleEnded(0);
  voltm = adc0 * multiplier / 1000.0; // x

  temps[0] = thermocouple1.readCelsius();
  temps[1] = thermocouple2.readCelsius();
  temps[2] = thermocouple3.readCelsius();
  temps[3] = thermocouple4.readCelsius();
  temps[4] = thermocouple5.readCelsius();

  for (int i = 0; i < 6; i++)
  {

    Serial.print(temps[i]);
    Serial.print(",");
  }

  Serial.println(abs((voltm * m) + b));
  delay(1000); 
}