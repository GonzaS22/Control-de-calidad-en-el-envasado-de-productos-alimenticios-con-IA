#Importación de paquetes
import cv2
import torch
from torchvision import transforms
from PIL import Image
import torchvision
import torchvision.transforms as transforms
from torchvision.datasets import ImageFolder
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
import torch as tr
import torch.optim as optim
import serial, time
import argparse
import threading


##########################################################
# CONSTRUCCIÓN EL PARSER PARA LOS ARGUMENTOS "POR CONSOLA"
##########################################################
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--cam", type=int, default=0, help="Índice de la cámara utilizada.")
args = vars(ap.parse_args())



#Función para realizar inferencia en una imagen
def inference(model, image):
    #Definición de una transformación para ajustar el tamao de las imágenes y convertirla a tensor
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        #transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    #Se cambia la configuración de color de la imagen a de BGR a RGB
    frame_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    #Conversión del frame de la imagen a una imagen PIL
    pil_image = Image.fromarray(frame_rgb)
    #Aplicación de la transformación definida anteriormente a la imagen
    input_tensor = preprocess(pil_image)
    #Obtención de un tensor unidimencional a partir del tensor de la imagen
    input_batch = input_tensor.unsqueeze(0)

    #Sin recalcular los gradientes
    with torch.no_grad():
        #Se obtiene la salida del modelo para esta imagen
        output = model(input_batch)

    #Aplicación de una función no lineal (sigmoidea) a la salida de la red
    sigmoid_output = torch.sigmoid(output)

    #Obtención la clase predicha para esta imagen 
    _, predicted_idx = torch.max(sigmoid_output, 1)
    predicted_class = predicted_idx.item()

    #La función retorna la clase predicha
    return predicted_class




#Creación del modelo neuronal
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        #Importación de un modelo preentrenado
        self.model = tr.hub.load('pytorch/vision:v0.10.0', 'mobilenet_v2', pretrained=True) 
        #Se agrega una capa lineal para obtener a la salida de la red las 6 clases deseas
        self.model.classifier[1] = nn.Linear(1280, 6)
        

    def forward(self, x):
        return self.model(x)

#Inicialización de la red
net = Net()

##################################################################################################################


#Función para agregar informción sobre las imágenes de los frascos en tiempo real 
def show_information(image, packaged_bottles_counter, bottle_counter_f, packaged_box_counter_f):

    #Definición de una lista con los valores RGB de un color
    color = (228,170,0)

    #Gráfico de una caja en la esquina inferior izquierda de la imágen
    cv2.putText(image, f'Estado de la caja', (10, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2) #(255, 0, 0)
    cv2.rectangle(image, (170,400), (240,470), color, 2)
    cv2.line(image, (205,400), (205,470), color, 2)
    cv2.line(image, (170,435), (240,435), color, 2)

    
    #Si el contador de botellas empacadas es 1
    if packaged_bottles_counter == 1:
        #Se dibuja 1 círculo dentro de la caja
        cv2.circle(image, (188,417), 12, (0,0,255), -1)

    #Si el contador de botellas empacadas es 2
    elif packaged_bottles_counter == 2:
        #Se dibujan 2 círculos dentro de la caja
        cv2.circle(image, (188,417), 12, (0,0,255), -1)
        cv2.circle(image, (223,417), 12, (0,0,255), -1)

    #Si el contador de botellas empacadas es 3
    elif packaged_bottles_counter == 3:
        #Se dibujan 3 círculos dentro de la caja
        cv2.circle(image, (188,417), 12, (0,0,255), -1)
        cv2.circle(image, (223,417), 12, (0,0,255), -1)
        cv2.circle(image, (188,453), 12, (0,0,255), -1)

    #Si el contador de botellas empacadas es 4
    elif packaged_bottles_counter == 4:
        #Se dibujan 4 círculos dentro de la caja
        cv2.circle(image, (188,417), 12, (0,255,0), -1)
        cv2.circle(image, (223,417), 12, (0,255,0), -1)
        cv2.circle(image, (188,453), 12, (0,255,0), -1)
        cv2.circle(image, (223,453), 12, (0,255,0), -1)
        

    #Se imprimen en pantalla las estadísticas de funcionamiento del sistema desde su encendido
    cv2.putText(image, f'Estadisticas: ', (250, 410), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.putText(image, f'Cajas listas: {int(np.trunc(packaged_box_counter_f))}', (250, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.putText(image, f'Frascos listos: {bottle_counter_f[0]}', (250, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.putText(image, f'Frascos vacios: {bottle_counter_f[1]}', (250, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.putText(image, f'Falta etiqueta: {bottle_counter_f[2]}', (425, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.putText(image, f'Etiqueta defectuosa: {bottle_counter_f[3]}', (425, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    cv2.putText(image, f'Frascos sin tapa: {bottle_counter_f[4]}', (425, 470), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
####################################################################################################################


#serial_port = serial.Serial("COM3", 9600)
#time.sleep(2)

#Inicialización en 0 de variables para contar frascos y cajas empaquetadas
bottles_cont = 0
packaged_box_counter = 0

#Función para leer datos del puerto serial en segundo plano
def read_serial():
    #Especificación de variables como globales para tener acceso a ellas en el resto del código
    global bottles_cont
    global packaged_box_counter

    #Configuración de un puerto serial
    serial_port = serial.Serial("COM3", 9600)
    
    while True:
        #Si hay algún dato disponible
        if serial_port.in_waiting > 0:
            #Lee los datos del puerto serial
            data = serial_port.readline().decode().strip()
            #Muestra los datos recibidos y el tipo de esos datos
            print("Datos recibidos desde Arduino:", data)
            print(type(data))

            #Si se recibe la palabra clave
            if data == "Box":
                #Aumenta el contador de frascos empaquetadas en 1
                bottles_cont += 1

                #Si el contador de frascos es mayor a 4
                if bottles_cont > 4:
                    #Se reinicia a 1 el contador de frascos
                    bottles_cont = 1
                    #Se aumenta el contador de cajas en 1
                    packaged_box_counter += 1

            #Se imprime en la consola la cantidad de frascos colocadas en a caja
            print("Bottle:", bottles_cont) 

        #Se agrega un retardo para evitar el uso excesivo de la CPU
        time.sleep(0.1)  

#Creación de un hilo para ejecutar la función read_serial en segundo plano
serial_thread = threading.Thread(target=read_serial)
#El hilo se detendrá cuando se cierre el programa principal
serial_thread.daemon = True
#Inicialización del hilo
serial_thread.start()

###################################################################################################################
#Creación de un arreglo de numpy para guardar la cantidad de frascos de cada clase 
bottle_class_counter = np.zeros(6, np.int8)
#DEfinición de una variable para guardar la última clase detectada
last_class = 5

#Se carga el modelo ya entrenado
net.load_state_dict(torch.load("best_model.pth", map_location='cpu'))
#Se lo configura en modo de evaluzación para aseguro que no se volverá a
#entrenar ni se modificará el modelo
net.eval()


#Inicialización de la webcam
cap = cv2.VideoCapture(args["cam"], cv2.CAP_DSHOW) 

#Obtención de las imagenes o cuadros de forma constante hasta que se detenga el proceso
while True:
    ret, frame = cap.read()   #Obtención de un cuadro de la imagen
    if not ret:
        break

    #Realización de inferencia para la imagen obtenida
    predicted_class = inference(net, frame)

    #Según la clase detectada se muestra un mensaje sobre la imagen del frasco
    if predicted_class == 0:
        cv2.putText(frame, f'Envasado correcto', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    elif predicted_class == 1:
        cv2.putText(frame, f'Error: Frasco vacio', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    elif predicted_class == 2:
        cv2.putText(frame, f'Error: Falta etiqueta', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    elif predicted_class == 3:
        cv2.putText(frame, f'Error: Etiqueta defectuosa', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    elif predicted_class == 4:
        cv2.putText(frame, f'Error: Frasco sin tapa', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    elif predicted_class == 5:
        cv2.putText(frame, f'Esperando el siguiente frasco...', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (45, 245, 255), 2)


    #Si la clase predicha es diferente a la clase predicha anterior
    if predicted_class != last_class:
        #Se aumenta en uno el contador de esa clase de frascos
        bottle_class_counter[predicted_class] += 1
        #Actualización de la clase predicha anterior
        last_class = predicted_class

    #Utilización de una función para mostrar información sobre la imagen del frasco en tiempo real
    show_information(frame, bottles_cont, bottle_class_counter, packaged_box_counter)

    #Se imprime en la consola el listado de clases con la cantidad de frascos de cada una
    #print(bottle_class_counter)

    #Se envia por un puerto serial la clase predicha al microcontrolador que controla la cinta
    #serial_port.write(str(predicted_class).encode())

    #Se muestra la imagen de los frascos acondicionada en la pantalla
    cv2.imshow('Webcam', frame)

    #Si se preciona la letra q se detiene el proceso
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

#Cierre las ventanas de video utilizadas
#serial_port.close()
cap.release()
cv2.destroyAllWindows()
