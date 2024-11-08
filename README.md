# Control-de-calidad-en-el-envasado-de-productos-alimenticios-con-IA
Este proyecto busca desarrollar un sistema automático que permita automatizar el proceso de detección de fallas en el envasado de productos alimenticios, particularmente de aceitunas verdes en salmuera. 

Dicho sistema se divide en 3 partes principales, un modelo basado en aprendizaje automático mediante redes neuronales convolucionales que recibe imágenes de los frascos en tiempo real a medida que pasan por una cinta transportadora y determina si están aptos para ser empaquetados o, en caso de poseer alguna falla de envasado, de cuál se trata. Posteriormente, un segundo módulo compuesto por una etapa de clasificación, implementado mediante un conjunto electromecánico controlado por un microcontrolador, se encarga de recibir información del primer módulo y separar de la línea de producción todos los frascos defectuosos, permitiendo solo el paso de los aprobados. Finalmente, como tercer módulo, se hace uso de un subsistema de empaquetado por medio de un brazo robot, cuya función es empacar los frascos aprobados en las cajas correspondientes para su transporte. 

Además, el sistema cuenta con una interfaz gráfica que le permite al usuario observar en detalle el funcionamiento de este proceso, a la vez que dispone de una serie de métricas que le permiten evaluar el rendimiento del proceso y detectar posibles patrones de fallas. 
De esta manera, la finalidad del proyecto es que este sistema disminuya al máximo posible la interacción humana durante todo este proceso de control de calidad, permitiendo que solo se requiera de un usuario ocasional para iniciar el sistema y evaluar el rendimiento del proceso productivo cuando se desee. Con estos cambios, se espera agilizar el trabajo de las industrias que utilicen el sistema, minimizar el esfuerzo humano y reducir los costos destinados a estas actividades.  

Dentro de este repositorio es posible encontrar los siguientes documentos: 
## Modelo_neuronal_preentrenado_para_deteccion_de_fallas_en_el_envasado_de_frascos.ipynb
Formado por una notebook de google colab que contiene el código de Python necesario para entrenar el modelo neuronal en su versión más completa para todas las clases propuestas, partiendo de un modelo preentrenado.

## Modelo_neuronal_entrenado_localmente_para_deteccion_de_fallas_en_el_envasado_de_frascos.ipynb
Formado por una notebook de google colab que contiene el código de Python necesario para entrenar el modelo neuronal en su versión más completa para todas las clases propuestas. El entrenamiento se realiza completamente de forma local, sin utilizar un modelo preentrenado. 

## Modelo_neuronal_de_dos_clases_para_clasificar_fallas.ipynb
Formado por una notebook de google colab que contiene el código de Python necesario para entrenar el modelo neuronal en una versión de destinada a clasificar solo entre 2 clases. El entrenamiento se realiza completamente de forma local. 

## app_clasificacion_aceitunas.py
Este script de Python contiene la aplicación requerida para ejecutar el modelo neuronal en tiempo real para la detección de fallas en el envasado de frascos de aceitunas. 

## Bottle_packing_robot_arm
Esta carpeta posee el conjunto de códigos fuentes utilizados para controlar el brazo robot del sistema de empaquetado automático de frascos. Estos códigos están desarrollados en lenguaje C para ser impactados sobre un microcontrolador Arduino uno. Es posible utilizarlos sobre otras plataformas, sin embargo es posible que sea necesario realizar algunas modificaciones correspondientes a las características técnicas de ese dispositivo y a las liberías utilizadas. 


## Control_classification_system
Esta carpeta posee el conjunto de códigos fuentes utilizados para controlar el sistema de clasificación de frascos constituido por una barrera mecánica montada sobre la cinta transportadora. Estos códigos están desarrollados en lenguaje C para ser impactados sobre un microcontrolador Arduino uno. Es posible utilizarlos sobre otras plataformas, sin embargo es posible que sea necesario realizar algunas modificaciones correspondientes a las características técnicas de ese dispositivo y a las liberías utilizadas. 


