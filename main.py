'''
Estructura del proyecto:

Clases:
- Message
- PDU header
- Client
- PDUPayload
- ReceiverSimulator

'''
import socket
import struct
import time
import random

class PDU_Header():
    def __init__(self, protocol, operation, message_id, source_ip, dest_ip, priority, timestamp, version):
        self.protocol = protocol
        self.operation = operation
        self.message_id = message_id
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.priority = priority
        self.timestamp = timestamp
        self.version = version
        self.payload_length = 0

# "!HBI4s4sBI BH" es el formato del struct.pack y struct.unpack
# https://docs.python.org/3/library/struct.html#format-characters

    def pack(self):
        print("[PACK] source_ip:", self.source_ip)
        print("[PACK] dest_ip:", self.dest_ip)
        packed_header = struct.pack(
            "!HBI4s4sBIIH",
            self.protocol,
            self.version,
            self.operation,
            self.source_ip,
            self.dest_ip,
            self.priority,
            self.timestamp,
            self.message_id,
            self.payload_length
        )
        print("[PACK] header bytes:", packed_header)
        return packed_header
    
    @staticmethod
    # el struct.unpack nos devuelve la info en tupla
    def unpack(data):
        print("[UNPACK] raw data:", data)
        unpacked = struct.unpack("!HBI4s4sBIIH", data)
        print("[UNPACK] tuple:", unpacked)
        hdr = PDU_Header(
            protocol=unpacked[0],
            version=unpacked[1],
            operation=unpacked[2],
            source_ip=socket.inet_ntoa(unpacked[3]),  
            dest_ip=socket.inet_ntoa(unpacked[4]),
            priority=unpacked[5],
            timestamp=unpacked[6],
            message_id=unpacked[7]
        )
        print("[UNPACK] source_ip (decoded):", socket.inet_ntoa(unpacked[3]))
        hdr.payload_length = unpacked[8]
        return hdr

class PDU_Payload():
    def __init__(self, content):
        self.content = content
    
    def encode(self):
        return self.content.encode('utf-8')

    def decode(self):
        return self.content.decode('utf-8')

class Client():
    def __init__(self, ip, sck):
        self.ip = ip
        self.sck = sck


class Transmitter(Client):
    def __init__(self, ip, socket):
        super().__init__(ip, socket)

    
    def send_message():
        return


class Reciever(Client):
    def __init__(self, ip, socket):
        super().__init__(ip, socket)

    
    def receive_message():
        return

class Message():
    def __init__(self, header, payload):
        self.header = header
        self.payload = payload # siempre objeto de tipo PDU_payload
    
    def to_bytes(self): # poner 
        payload_encoded = self.payload.encode() # siempre objeto de tipo PDU_payload
        print("[TO_BYTES] Payload:", payload_encoded)
        self.header.payload_length = len(payload_encoded)
        print("[TO_BYTES] Payload length:", self.header.payload_length)
        header_bytes = self.header.pack()
        print("[TO_BYTES] Header + Payload size:", len(header_bytes + payload_encoded))

        return header_bytes  + payload_encoded

    @staticmethod
    def from_bytes(data):
        print("[FROM_BYTES] Total bytes:", len(data))
        size_header = struct.calcsize("!HBI4s4sBIIH") # tamaño bytes del header según el formato !HBI4s4sBI BH

        print("[FROM_BYTES] Header size:", size_header)
        header_data = data[:size_header]
        payload_data = data[size_header:]

        print("[FROM_BYTES] Payload raw:", payload_data)
        header = PDU_Header.unpack(header_data)
        payload = PDU_Payload(payload_data.decode('utf-8'))
    
        return Message(header, payload)

if __name__ == "__main__":
    header = PDU_Header(
        protocol=0x1E54,
        operation=1,
        message_id=123,
        source_ip=socket.inet_aton("192.168.1.1"),
        dest_ip=socket.inet_aton("192.168.1.2"),
        priority=5,
        timestamp=int(time.time()),
        version=1
    )
    payload = PDU_Payload("Hola receptor")
    msg = Message(header, payload)

    data = msg.to_bytes()
    msg_reconstruido = Message.from_bytes(data)

    print("Mensaje original:", payload.content)
    print("Mensaje recibido:", msg_reconstruido.payload.content)
