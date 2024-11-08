//Se incluyen la libería general de arduino y las librerías para el control 
//de los servomotores
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

//Encabezados de las funciones de control del motor paso a paso y del servomotor
void SetDirection();
void setStepper(int step_count, bool dir);
void setServo(uint8_t n_servo, int starting_ang, int finish_ang, int smoothing_time = 10);

//Se inicia un objeto de tipo Adafruit_PWMServoDriver para controlar los servos
Adafruit_PWMServoDriver servos = Adafruit_PWMServoDriver(0x40);

unsigned int pos0 = 150;   //Ancho de pulso en cuentas para pocicion 0°   
unsigned int pos180 = 650; //Ancho de pulso en cuentas para la pocicion 180°   

int time = 1500;           //Tiempo de espera para un retardo en ms
int bottle_counter = 0;    //Definición de un contador temporal de frascos


// #######################################################################################
//Definición de la secuencia de pasos para un motor paso a paso de 4 fases
int Paso[8][4] =
    {{1, 0, 0, 0},
     {1, 1, 0, 0},
     {0, 1, 0, 0},
     {0, 1, 1, 0},
     {0, 0, 1, 0},
     {0, 0, 1, 1},
     {0, 0, 0, 1},
     {1, 0, 0, 1}};

//Definición de los pines de salida utilizados para el controlador del motor paso a paso
#define IN1 12
#define IN2 11
#define IN3 10
#define IN4 9

//Variable para ajustar la dirección de movimiento del servo (true = adelante, false = atrás)
boolean Direction = true;   
//Variable para definir el paso actual de la secuencia
int Steps = 0; 

// ####################################################################################
//Definición del pin utilizado para recibir información de la barrera infrarroja
int infrared_barrier = 2; 


void setup()
{
  servos.begin();        //Inicialización del controlador de servos
  servos.setPWMFreq(60); //Configuración de la frecuecia PWM a 60Hz o T=16,66ms

  // Configuración de los pines del motor paso a paso como salidas
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  //Configuración del pin asociado a la barrera infrarroja como entrada
  pinMode(infrared_barrier, INPUT); 

  //Inicio de la comunicación serie a una velocidad de 9600 baudios
  Serial.begin(9600);

}


void loop()
{
  //Si se detecta que ha llegado un frasco para empaquetar
  if (digitalRead(infrared_barrier) == HIGH)
  {
    //Baja el brazo robot
    setServo(4, 180, 0);

    //Cierra la abrazadera
    setStepper(4095, true);

    //Levanta el frasco
    setServo(4, 0, 180);

    //Dependiendo de cual frasco se desea empaquetar el brazo robot se desplada a 
    //una determinada posición
    switch (bottle_counter)
    {
    //Si se trata del primer frasco
    case 0:
      //El brazo se desplaza a la posición 1
      setServo(0, 180, 0);
      //Baja a la altura necesaria para depositar el frasco
      setServo(4, 180, 30);
      break;

    //Si se trata del segundo frasco
    case 1:
      //El brazo se desplaza a la posición 2
      setServo(0, 180, 30);
      //Baja a la altura necesaria para depositar el frasco
      setServo(4, 180, 30);
      break;

    //Si se trata del tercer frasco
    case 2:
      //El brazo se desplaza a la posición 3
      setServo(0, 180, 0);
      //Baja a la altura necesaria para depositar el frasco
      setServo(4, 180, 0);
      break;

    //Si se trata del cuarto frasco
    case 3:
      //El brazo se desplaza a la posición 3
      setServo(0, 180, 30);
      //Baja a la altura necesaria para depositar el frasco
      setServo(4, 180, 0);
      break;

    //En caso de default el brazo robot no se desplaza
    default:
      break;
    }

    //Se abre la abrazadera depositando el frasco
    setStepper(4095, false);

    //El brazo robot se eleva 
    setServo(4, 0, 180);

    //Se envia un mensaje por medio de la comunicación serial indicando que
    //se ha depositado correctamente un frasco en la caja 
    Serial.println("Box");

    //Se incrementa el contador de frascos empaquetados
    bottle_counter++;

    //Si el contador es mayor a 3 implica que se ha completado una caja y
    //se reinicia dicho contador 
    if (bottle_counter > 3)
    {
      bottle_counter = 0;
    }

    //El brazo robot regresa a su posición de reposo a la espera del próximo frasco
    setServo(0, 0, 180);
  }

  //En caso de que no se detecte ningún frasco para empaquetar
  else
  {
    //El brazo robot permanece en su posición de reposo
    setServo(0, 0, 180);
    setServo(4, 0, 180);
  }

}

//===========================================================================================

/*Función para controlar los servos
  Parámetros: n_servo = Número de servo que se desea controlar
              starting_ang = Ángulo inicial del servo
              finish_ang = Ángulo final del servo
              smoothing_time = Tiempo de suavizado en ms
*/
void setServo(uint8_t n_servo, int starting_ang, int finish_ang, int smoothing_time)
{
  int duty;  //Variable para almacenar el valor del ancho de pulso (duty cycle)

  //Si el ángulo inicial es menor que el ángulo final, el servo se moverá hacia adelante
  if (starting_ang < finish_ang)
  {
    //Itera desde el ángulo inicial hasta el ángulo final, aumentando 1 grado en cada paso
    for (int ang = starting_ang; ang < finish_ang; ang++)
    {
      //Calcula el valor de ancho de pulso correspondiente al ángulo actual
      duty = map(ang, 0, 180, pos0, pos180);
      
      //Envía el valor de ancho de pulso calculado al canal del servo (n_servo)
      servos.setPWM(n_servo, 0, duty);
      
      //Espera el tiempo de suavizado (smoothing_time) antes de pasar al siguiente ángulo
      delay(smoothing_time);
    }
  }

  //Si el ángulo inicial es mayor que el ángulo final, el servo se moverá en dirección inversa
  else
  {
    //Itera desde el ángulo inicial hasta el ángulo final, disminuyendo 1 grado en cada paso
    for (int ang = starting_ang; ang > finish_ang; ang--)
    {
      //Calcula el valor de ancho de pulso correspondiente al ángulo actual
      duty = map(ang, 0, 180, pos0, pos180);
      
      //Envía el valor de ancho de pulso calculado al canal del servo (n_servo)
      servos.setPWM(n_servo, 0, duty);
      
      //Espera el tiempo de suavizado (smoothing_time) antes de pasar al siguiente ángulo
      delay(smoothing_time);
    }
  }

  // Espera un tiempo adicional después de completar el movimiento, definido en la variable 'time'
  delay(time);
}

//===========================================================================================

//Función utilizada para que el motor paso a paso avance un paso
void stepper()
{
  //Configura el estado de los pines según el valor en la matriz 'Paso' para el paso actual
  digitalWrite(IN1, Paso[Steps][0]);
  digitalWrite(IN2, Paso[Steps][1]);
  digitalWrite(IN3, Paso[Steps][2]);
  digitalWrite(IN4, Paso[Steps][3]);

  //Llama a la función SetDirection() para ajustar el índice 'Steps' al siguiente paso,
  //actualizando la dirección según la configuración
  SetDirection();
}

//===========================================================================================

//Función para configurar la dirección de giro del motor paso a paso
void SetDirection()
{
  //Verifica la dirección del movimiento. Si 'Direction' es verdadero, incrementa 'Steps'
  if (Direction)
    Steps++; //Avanza al siguiente paso en la secuencia de pasos

  //Si 'Direction' es falso, decrementa 'Steps' para ir en la dirección opuesta
  else
    Steps--; //Retrocede al paso anterior en la secuencia de pasos

  // Ajusta 'Steps' para que siempre esté dentro del rango de 0 a 7 (total de pasos en la secuencia)
  Steps = (Steps + 8) % 8; // Esto permite que 'Steps' "rebote" de 7 a 0 o de 0 a 7
}

//===========================================================================================

/*Función para controlar el movimiento del motor paso a paso
  Parámetros: step_count = Contador que almacena la cantidad de pasos restantes
              dir = Dirección de giro del motor paso a paso
*/
void setStepper(int step_count, bool dir)
{
  //Bucle que continúa hasta que se hayan completado todos los pasos especificados
  while (step_count > 0)
  {
    stepper();    //Llama a la función 'stepper()' para avanzar un paso en la secuencia
    step_count--; //Disminuye el contador de pasos restantes en 1
    delay(1);     //Pausa de 1 milisegundo entre pasos para controlar la velocidad del motor
  }

  //Establece la dirección del movimiento para la próxima vez que se llame a 'stepper()'
  Direction = dir;
}


