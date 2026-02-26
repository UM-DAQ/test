//==================================================================================//

#include <CAN.h>

#define TX_GPIO_NUM 5
#define RX_GPIO_NUM 4

//==================================================================================//

void setup()
{
    Serial.begin(115200);
    while (!Serial)
        ;
    delay(1000);

    Serial.println("CAN Receiver/Receiver");

    // Set the pins
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
    // canSender();
    canReceiver();
}

//==================================================================================//

void canSender()
{
    // send packet: id is 11 bits, packet can contain up to 8 bytes of data
    Serial.print("Sending packet ... ");

    CAN.beginPacket(0x12); // sets the ID and clears the transmit buffer
    // CAN.beginExtendedPacket(0xabcdef);
    CAN.write('1'); // write data to buffer. data is not sent until endPacket() is called.
    CAN.write('2');
    CAN.write('3');
    CAN.write('4');
    CAN.write('5');
    CAN.write('6');
    CAN.write('7');
    CAN.write('8');
    CAN.endPacket();

    // RTR packet with a requested data length
    CAN.beginPacket(0x12, 3, true);
    CAN.endPacket();

    Serial.println("done");

    delay(1000);
}

//==================================================================================//

void canReceiver()
{
    // Intentar parsear el paquete
    int packetSize = CAN.parsePacket();

    if (packetSize)
    {
        // Solo procesamos si NO es un paquete RTR y si tiene datos
        if (!CAN.packetRtr() && packetSize > 0)
        {
            Serial.print("Recibido ID 0x");
            Serial.print(CAN.packetId(), HEX);
            Serial.print(" | Longitud: ");
            Serial.println(packetSize);

            // CASO 1: Si esperamos un float (el voltaje son 4 bytes)
            if (packetSize == sizeof(float))
            {
                float voltajeRecibido;

                // Leemos los bytes directamente en la dirección de memoria de la variable float
                CAN.readBytes((char *)&voltajeRecibido, sizeof(voltajeRecibido));

                Serial.print("-> Voltaje decodificado: ");
                Serial.println(voltajeRecibido, 4); // 4 decimales
            }
            // CASO 2: Si es texto u otra cosa (para depuración)
            else
            {
                Serial.print("-> Datos raw: ");
                while (CAN.available())
                {
                    Serial.print((char)CAN.read());
                }
                Serial.println();
            }
        }

        // Si es una petición remota (RTR)
        else if (CAN.packetRtr())
        {
            Serial.print("Petición RTR recibida en ID 0x");
            Serial.println(CAN.packetId(), HEX);
        }

        Serial.println("-----------------------------");
    }
}
//==================================================================================//