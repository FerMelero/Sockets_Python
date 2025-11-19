# Sockets Python
Proyecto realizado por Fernando Melero y Giordano Castilla


Primero en una terminal iniciamos el servidor

Abrimos otra terminal y ejecutamos el emisor

El emisor crea el mensaje, se llama al método send_message(), ahí se crea PDU_Payload y PDU_Header. El emisor llama al método to_bytes(), calcula la longitud de la carga, empaqueta la cabecera y se concatenan. Luego el meisor envía el paquete hacia el receptor.
A la hora de empaquetar y desempaquetar el mensaje, se ha seguido un formato específico para la cabecera !HBI4s4sBIIH. 
Este formato significa:
| Carácter | Bytes | Tipo de dato   | Campo          | Explicación                           |
| -------- | ----- | -------------- | -------------- | ------------------------------------- |
| !        | –     | –              | Orden          | Sirve para que se interprete el orden |
| H        | 2     | Unsigned short | Protocol       | Protocolo usado                       |
| B        | 1     | Unsigned char  | Version        | Versión del protocolo                 |
| I        | 4     | Unsigned int   | Operation      | OPCODE (enviar mensaje, ACK, etc.)    |
| 4s       | 4     | Char(4)        | Source_IP      | IP emisora                            |
| 4s       | 4     | Char(4)        | Dest_IP        | IP receptora                          |
| B        | 1     | Unsigned char  | Priority       | Prioridad                             |
| I        | 4     | Unsigned int   | Timestamp      | Timestamp del mensaje                 |
| I        | 4     | Unsigned int   | Message_ID     | ID del mensaje                        |
| H        | 2     | Unsigned short | Payload_length | Longitud de la carga                  |

Esta información se ha sacado de lás páginas indicadas al final del documento, en la sección de referencias.
El receptor recibe el mensaje, leyendo primero la cabecera del mensaje y desempaquetándola. Luego lee los bytes restantes y se interpreta el tipo de OPCODE. El receptor envía un ACK al emisor original para confirmar la recepción del mensaje, entonces se crea un nuevo mensaje para que el receptor envíe sin payload y el OPCODE correspondiente.
Posteriormente el emisor recibe el ACK del receptor, este espera con wait_for_ack(). Recibe la cabecera del ACK y verifica el OPCODE y espera un segundo. 

En ReceiverSImulator se construye un mensaje con OPCODE = OP_READ_ACK, nos sirve para simular que el receptor lee el mensaje.






Por último termina el bucle y se cierran tanto emisor como receptor.



