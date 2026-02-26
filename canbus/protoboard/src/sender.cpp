//===============================================================================//
#include <Wire.h>
#include <CAN.h>
#include <Adafruit_ADS1X15.h>

#define I2C_SDA 21
#define I2C_SCL 22
#define TX_GPIO_NUM 5
#define RX_GPIO_NUM 4

Adafruit_ADS1115 ads;
const float m = 0.00054707F;
const float b = -0.00792761F;

//==============================================================================//

void setup()
{
  Serial.begin(115200);
  while (!Serial)
    ;
  delay(1000);

  // Configuración ADS1115
  Wire.begin(I2C_SDA, I2C_SCL);
  ads.setGain(GAIN_EIGHT);

  if (!ads.begin())
  {
    Serial.println("Error: No se encontró el ADS1115. Revisa conexiones.");
    while (1)
      ;
  }

  Serial.println("ADS1115 Iniciado correctamente");
  Serial.println("CAN Receiver/Receiver");

  CAN.setPins(RX_GPIO_NUM, TX_GPIO_NUM);

  // start the CAN bus at 500 kbps
  if (!CAN.begin(500E3))
  {
    Serial.println("Starting CAN failed!");
    while (1)
      ;
  }
  else
  {
    Serial.println("CAN Initialized");
  }
}

//==================================================================================//

void loop()
{
  canSender();
  // canReceiver();
}

//==================================================================================//

void canSender()
{
  int16_t adc0 = ads.readADC_SingleEnded(0);
  float voltage = abs((adc0 * m) + b);

  // send packet: id is 11 bits, packet can contain up to 8 bytes of data
  Serial.print("Sending voltage: ");
  Serial.print(voltage);

  CAN.beginPacket(0x12); // sets the ID and clears the transmit buffer
  // CAN.beginExtendedPacket(0xabcdef);
  // CAN.write('1');  //write data to buffer. data is not sent until endPacket() is called.
  // CAN.write('2');
  // CAN.write('3');
  // CAN.write('4');
  // CAN.write('5');
  // CAN.write('6');
  // CAN.write('7');
  // CAN.write('8');
  CAN.write((uint8_t *)&voltage, sizeof(voltage));
  CAN.endPacket();

  // RTR packet with a requested data length
  CAN.beginPacket(0x12, 3, true);
  CAN.endPacket();

  Serial.println(" [done]");

  delay(1000);
}

//==================================================================================//

void canReceiver()
{
  // try to parse packet
  int packetSize = CAN.parsePacket();

  if (packetSize)
  {
    // received a packet
    Serial.print("Received ");

    if (CAN.packetExtended())
    {
      Serial.print("extended ");
    }

    if (CAN.packetRtr())
    {
      // Remote transmission request, packet contains no data
      Serial.print("RTR ");
    }

    Serial.print("packet with id 0x");
    Serial.print(CAN.packetId(), HEX);

    if (CAN.packetRtr())
    {
      Serial.print(" and requested length ");
      Serial.println(CAN.packetDlc());
    }
    else
    {
      Serial.print(" and length ");
      Serial.println(packetSize);

      // only print packet data for non-RTR packets
      while (CAN.available())
      {
        Serial.print((char)CAN.read());
      }
      Serial.println();
    }

    Serial.println();
  }
}

//==================================================================================//
