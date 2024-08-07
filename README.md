# Programas utilizados para TTM-2023/2-02
(Spanish)<br>
<p>
Los archivos presentados en este repositorio, fueron utilizados para el desarrollo e implementación del Trabajo Terminal (TT) de clave <strong><em>TTM-2023/2-02</em></strong> y título “<strong><em>Robot autónomo para limpiar paneles fotovoltaicos en zonas urbanas</em></strong>”. Para la implementación del TT se utilizaron tarjetas de desarrollo ESP32-WROOM de 38 y 30 pines y el lenguaje utilizado para el desarrollo de los programas fue MicroPython 2.1.22 con la versión 3.10.11 de Python; los programas fueron desarrollados y subidos por medio del software Thonny 4.1.4. <br>
Los componentes utilizados se enlistan a continuación con las numeraciones de los productos.
  <ul>
    <li>Motores para los rieles: <strong>5203-2402-0051</strong>.</li>
    <li>Motores para cepillo: <strong>5203-2402-0019</strong>.</li>
    <li>Motores para el carro: <strong>5203-2402-0139</strong>.</li>
    <li>Motor para el arnés: <strong>5203-2402-0005</strong>.</li>
    <li>Drivers: <strong>DC5-12V ZH-30A</strong>.</li>
    <li>Drivers: <strong>BTS7960B 43A SN-BTS</strong>.</li>
    <li>Botones de 4 pines.</li>
    <li>Sensor para final de carrera: <strong>AEM2G4120Z11-3R</strong>.</li>
  </ul>
</p>

<h3>Commication between ESP32</h3>
<p>
En esta carpeta contiene el programa base para realizar la comunicación entre las tarjetas ESP32, además de que fue utilizado para verificar dicha comunicación. Cabe mencionar que la comunicación entre las tarjetas fue por medio de ESP-NOW, ESP-NOW es un protocolo de comunicación inalámbrica desarrollada por Espressif, esta comunicación es un protocolo de comunicación Peer to Peer, el cual realiza la comunicación por medio de las direcciones MAC de cada tarjeta.
  <ul>
    <li>El archivo <strong><em>find_mac_addr.py</em></strong> es un programa que muestra la dirección MAC de la tarjeta activa, la tarjeta debe estar conectado al puerto USB de la computadora. </li>
    <li>El archivo <strong><em>esp3_remote_control.py</em></strong> es un programa que envía mensajes, por medio de botones, a la tarjeta deseada. Dentro del programa se debe colocar la dirección o direcciones MAC de la o las tarjetas a recibir.</li>
    <li>El archivo Button.py es un módulo que realiza la lectura del botón que está conectado la tarjeta que envía el mensaje.</li>
    <li>El archivo <strong><em>test_recive.py</em></strong> es un programa de prueba para verificar que la comunicación entre tarjetas fue la adecuada. El mensaje enviado desde <strong><em>esp3_remote_control</em></strong> se debe ver reflejado en la tarjeta que tiene cargado <strong><em>test_recive.py</em></strong></li>
  </ul>
</p>

<h3>Identify TF</h3>
<p>
En esta carpeta contiene archivos para la identificación de la planta o función de transferencia de los motores a lazo abierto. En la carpeta Simulink 2022b, contiene el programa para medir la velocidad del motor a lazo abierto por medio de una comunicación serial entre la tarjeta y la computadora, la versión utilizada fue MATLAB® Academic Simulink® 2022b.<br><br>
En la carpeta Python Serial Communication contiene programa para realiza la identificación a lazo abierto por medio de una comunicación serial entre la tarjeta de desarrollo y la computadora, al realizar esta identificación se debe correr primero el programa <strong><em>open_loop.py</em></strong> (ESP32) en el que pide la tensión que se desea inyectar al motor y después se corre el archivo <strong><em>store_speed.py</em></strong> (Computadora) para guardar la velocidad obtenida en un archivo Excel. <br><br>
En ambos casos, después de obtener la velocidad a lazo abierto, se utiliza MATLAB® Academic 2022b con los toolbox <em>System Identificacion</em> y <em>PID Turner</em> para la identificación de la planta y la sintonizcion del control PID respectivamente.
</p>



<h3>Speed control</h3>
<p>
En esta carpeta contiene los programas base para un control de velocidad PID de lazo cerrado para un motor. Cabe mencionar que cada motor tiene su resolución y ganancias PID, por lo que es importante revisar en la hoja de datos del motor y sintonizar previamente el motor. Aquellos archivos que contiene la clase Motor son para los dirvers <strong>DC5-12V ZH-30A</strong> y los que contiene la clase Arnes son para los drivers <strong>BTS7960B 43A SN-BTS</strong>.
</p>
<h3>Position control</h3>
<p>
En esta carpeta contiene los programas base para un control de posición PID de lazo cerrado para un motor, además, contiene un programa (cilincro.py) para mover el actuador a cierta distancia para meter o sacar el embolo. El setpoint del control de posición para estos archivos esta en cm, por lo que esto desplaza a cierta distancia lineal al subsistema. Aquellos archivos que contiene la clase Motor son para los dirvers <strong>DC5-12V ZH-30A</strong> y los que contiene la clase Arnes son para los drivers <strong>BTS7960B 43A SN-BTS</strong>.
</p>

<h3>ESP32 Robot Porgrams</h3>
<p>
En esta carpeta contiene los programas principales de cada una de las tarjetas para mover el Sistema Mecatrónico. La manera en que se distribuyeron cada una de las tarjetas se presenta en la Figura 1 y para subir los programas de manera adecuada se basó en lo siguiente: 
  <ul>
    <li>Los archivos <strong><em>Motor.py</em></strong> y <strong><em>PinMotor.py</em></strong> son dos módulos para los motores que son controlados por medio del driver <strong>DC5-12V ZH-30A</strong> y para trabajar con los pines de la ESP32 respectiva.</li>
    <li>Los archivos <strong><em>Arnes.py</em></strong> y <strong><em>PinMotorArnes.py</em></strong> son dos módulos para los motores que son controlados por medio del driver <strong>BTS7960B 43A SN-BTS</strong> y para trabajar con los pines de la ESP32 respectiva.</li>
    <li>El archivo <strong><em>LimitSensor.py</em></strong> es un módulo que realiza la lectura del limit switch <strong>AEM2G4120Z11-3R</strong>.</li>
    <li>El archivo <strong><em>Button.py</em></strong> es un módulo que realiza la lectura de los botones del control remoto (ESP32 3).</li>
    <li>Los archivos <strong><em>espN_XXXX.py</em></strong>, son los programas principales para manipular el sistema mecatrónico. N es la numeración de la tarjeta asignada y XXXX son palabras clave para identificar en que parte va colocada la tarjeta.</li>
  </ul>
</p>
<img src="Sistema de informacion.png" alt="Figura 1. Comunicación de las tarjetas ESP32 en el Sistema Mecatrónico.">
<p>Figura 1. Comunicación de las tarjetas ESP32 en el Sistema Mecatrónico.</p>

# Programs used for TTM-2023/2-02
(Enlgish)<br>
