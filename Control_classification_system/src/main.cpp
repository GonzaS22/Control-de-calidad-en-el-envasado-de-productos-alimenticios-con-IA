//Se incluye la libería general de arduino y la librería utilizada para controlar el servo
#include <Arduino.h>
#include <Servo.h>

//Se definen los pines de la barrera infrarroja y de un led testigo
const int infrared_barrier = 2;
const int pinLED = 13;

//Se crea un objeto de tipo servo utilizado para controlar el servomotor
Servo servoMotor; 

void setup() 
{
  //Se inicia la comunicación serial a una velocidad de 9600 baudios
  Serial.begin(9600);

  //Se configura el pin de la barrera infrarroja como entrada y el del led como salida
  pinMode(infrared_barrier, INPUT); 
  pinMode(pinLED, OUTPUT);

  //Configura el objeto servoMotor para controlar un servomotor conectado al 
  //pin digital 3 
  servoMotor.attach(3);
}

void loop()
{
  //Si se detecta un dato disponible en la comunicación serial
  if (Serial.available()>0) 
  {
    //Se guarda el dato recibido correspondiente a la clase predicha por la red neuronal
    char predicted_class = Serial.read();

    //Si la clase predicha es diferente de 0 y de 5
    if(predicted_class != '0' && predicted_class != '5')
    {
      //Se baja la barrera mecánica conectada al servo
      servoMotor.write(0);
      //Se enciende el led testigo
      digitalWrite(pinLED, HIGH); 
    }

  }

  //Si se detecta con la barrera infrarroja que el frasco defectuoso a salido de la 
  //cinta transportadora
  if(digitalRead(infrared_barrier) == HIGH)
  {
    //Se eleva la barrera mecánica conectada al servo
    servoMotor.write(90);
    //Se apaga el led testigo 
    digitalWrite(pinLED, LOW);
  }

}