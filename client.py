from protocol import PDU_Header, PDU_Payload, Message, HEADER_SIZE
import socket
import time
import random

# valores constantes 
PROTOCOL_ID = 0x1E54
VERSION = 1
OP_SEND_MSG = 0x00      
OP_RCV_ACK = 0x01       
OP_ERROR = 0x02        
OP_READ_ACK = 0x03      

# clase cliente con la IP y el socket
class Client():
    def __init__(self, ip, sck):
        self.ip = ip
        self.sck = sck

# clase Transmitter (hereda de client)
class Transmitter(Client):
    
    def __init__(self, ip, sck):
        super().__init__(ip, sck)

    # enviar mensaje
    def send_message(self, dest_ip_str, message_text, msg_id, priority=1):
        """
        Ensambla la PDU para el envío del mensaje (OP_SEND_MSG) y la envía por el socket.
        Luego espera y procesa la llegada de ACK/error.
        """
        src_ip_bytes = socket.inet_aton(self.ip) # ip de emisor
        dest_ip_bytes = socket.inet_aton(dest_ip_str) # ip de destino
        current_time = int(time.time()) # timestamp

        payload = PDU_Payload(message_text) # llamada a metodo PDU_Payload de protocol.py
        payload_length = len(payload.encode()) # metodo encode de PDU_Payload

        # construir la cabecera
        header = PDU_Header(
            protocol=PROTOCOL_ID,
            version=VERSION,
            operation=OP_SEND_MSG,
            source_ip=src_ip_bytes,
            dest_ip=dest_ip_bytes,
            priority=priority,
            timestamp=current_time,
            message_id=msg_id,
            payload_length=payload_length
        )
        
        # construir el mensaje (archivo protocol.py)
        message = Message(header, payload)
        data_to_send = message.to_bytes()
        self.sck.sendall(data_to_send)
        print(f"[Transmitter] Msg ID {msg_id} ({OP_SEND_MSG:X}) enviado a {dest_ip_str}. Tamaño: {len(data_to_send)} bytes.")

        # Esperar respuesta
        self.wait_for_ack()

    # método de espera de respuesta
    def wait_for_ack(self):
        try:
            header_bytes = self.sck.recv(HEADER_SIZE)
            if not header_bytes:
                print("[Transmitter] No ACK recibido (desconexión/timeout).")
                return
        except Exception as e:
            print(f"[Transmitter] Error recibiendo ACK: {e}")
            return

        header = PDU_Header.unpack(header_bytes)

        # identificar el tipo de mensaje
        if header.operation == OP_RCV_ACK:
            print(f"[Transmitter] ACK recibido para mensaje {header.message_id}")
        elif header.operation == OP_ERROR:
            print(f"[Transmitter] ERROR recibido para mensaje {header.message_id}")
        elif header.operation == OP_READ_ACK:
            print(f"[Transmitter] READ_ACK recibido para mensaje {header.message_id}")
        else:
            print(f"[Transmitter] Mensaje inesperado con opcode {header.operation}")


class Reciever(Client):
    def __init__(self, ip, sck):
        super().__init__(ip, sck)

    # receptor
    def receive_message(self):
        """
        Recibe el paquete completo (Header + Payload), interpreta el opcode y envía ACK si corresponde.
        """
        try:
            header_bytes = self.sck.recv(HEADER_SIZE)
        except Exception:
            return None

        if not header_bytes or len(header_bytes) != HEADER_SIZE:
            return None

        # desempaquetar el mensaje
        header = PDU_Header.unpack(header_bytes)
        payload_length = header.payload_length

        payload_bytes = b''
        while len(payload_bytes) < payload_length:
            chunk = self.sck.recv(payload_length - len(payload_bytes))
            if not chunk:
                return None
            payload_bytes += chunk

        full_data = header_bytes + payload_bytes
        message_recibido = Message.from_bytes(full_data)

        op = message_recibido.header.operation

        # interpretar el tipo de mensaje
        if op == OP_SEND_MSG:
            print(f"[Receiver] -> Opcode = SEND_MSG (0x00). Msg ID: {message_recibido.header.message_id}")
            print(f"[Receiver] Contenido: {message_recibido.payload.content}")
            # Enviar ACK
            src_ip_str = message_recibido.header.source_ip
            self.send_ack(src_ip_str, message_recibido.header.message_id)

        elif op == OP_RCV_ACK:
            print(f"[Receiver] -> Opcode = RCV_ACK (0x01). Msg ID: {message_recibido.header.message_id}")

        elif op == OP_ERROR:
            print(f"[Receiver] -> Opcode = ERROR (0x02). Msg ID: {message_recibido.header.message_id}")

        elif op == OP_READ_ACK:
            print(f"[Receiver] -> Opcode = READ_ACK (0x03). Msg ID: {message_recibido.header.message_id}")

        else:
            print(f"[Receiver] -> Opcode desconocido ({op}). Msg ID: {message_recibido.header.message_id}")

        return message_recibido

    # enviar ack
    def send_ack(self, dest_ip, msg_id):
        # sacar IP
        src_ip_bytes = socket.inet_aton(self.ip)
        dest_ip_bytes = socket.inet_aton(dest_ip)

        # construir la cabecera del ack
        header = PDU_Header(
            protocol=PROTOCOL_ID,
            version=VERSION,
            operation=OP_RCV_ACK,
            source_ip=src_ip_bytes,
            dest_ip=dest_ip_bytes,
            priority=1,
            timestamp=int(time.time()),
            message_id=msg_id,
            payload_length=0
        )

        payload = PDU_Payload("")
        message = Message(header, payload)
        data = message.to_bytes()
        self.sck.sendall(data)

        print(f"[Receiver] ACK enviado al emisor ({dest_ip}).")


class ReceiverSimulator:
    def __init__(self, receiver: Reciever):
        self.receiver = receiver

    def simulate_read_delay(self, message, min_delay=1, max_delay=5):
        """
        Simula que el receptor lee el mensaje tras un retraso aleatorio
        y envía un READ_ACK (0x03) al emisor.
        """
        import time, random

        delay = random.uniform(min_delay, max_delay)
        print(f"[Simulator] Simulando lectura de mensaje {message.header.message_id} en {delay:.2f}s...")
        time.sleep(delay)

        # Construir READ_ACK
        src_ip_bytes = socket.inet_aton(self.receiver.ip)
        dest_ip_bytes = socket.inet_aton(message.header.source_ip)

        header = PDU_Header(
            protocol=PROTOCOL_ID,
            version=VERSION,
            operation=OP_READ_ACK,
            source_ip=src_ip_bytes,
            dest_ip=dest_ip_bytes,
            priority=1,
            timestamp=int(time.time()),
            message_id=message.header.message_id,
            payload_length=0
        )

        payload = PDU_Payload("")  # Sin contenido
        read_ack_msg = Message(header, payload)
        data = read_ack_msg.to_bytes()
        self.receiver.sck.sendall(data)

        print(f"[Simulator] READ_ACK enviado para mensaje {message.header.message_id}.")
