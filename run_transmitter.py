from client import Transmitter
import socket
import time

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345

if __name__ == "__main__":
    try:
        # Crear el socket cliente y conectar al servidor
        sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sck.connect((SERVER_IP, SERVER_PORT))
        print(f"[Transmitter] Conectado a {SERVER_IP}:{SERVER_PORT}")
        
        # Crear instancia del Transmitter
        transmitter_app = Transmitter(SERVER_IP, sck)
        
        # Enviamos un mensaje de prueba
        mensajes = [
            "¡Mensaje de prueba 1!"
        ]

        for i, texto in enumerate(mensajes, start=101):
            transmitter_app.send_message(
                dest_ip_str="127.0.0.1",
                message_text=texto,
                msg_id=i
            )
            time.sleep(1)  # Simula tiempo entre envíos
        
    except ConnectionRefusedError:
        print("[Transmitter] ERROR: Ejecuta primero el receptor (run_receiver.py).")
    except Exception as e:
        print(f"[Transmitter] Ocurrió un error: {e}")
    finally:
        sck.close()
