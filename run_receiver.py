from client import Receiver
import socket

SERVER_IP = '127.0.0.1'  # IP local para pruebas
SERVER_PORT = 12345       # Puerto

if __name__ == "__main__":
    # Crear el socket servidor
    sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sck.bind((SERVER_IP, SERVER_PORT))
    sck.listen(1)  # Escuchar una conexión
    
    print(f"[Receiver] Escuchando en {SERVER_IP}:{SERVER_PORT}...")

    # Aceptar la conexión del emisor
    conn, addr = sck.accept()
    print(f"[Receiver] Conexión aceptada desde {addr}")

    # Crear instancia del Receptor
    receiver_app = Receiver(SERVER_IP, conn)

    # Bucle de recepción de mensajes
    try:
        while True:
            msg = receiver_app.receive_message()
            if msg is None:
                print("[Receiver] Conexión cerrada por el emisor.")
                break
    except KeyboardInterrupt:
        print("[Receiver] Terminando receptor...")
    finally:
        conn.close()
        sck.close()
