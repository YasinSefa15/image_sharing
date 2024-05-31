import socket
import threading
import pickle

# Define server address and port
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65432

# Dictionary to store user information and their public keys
users = {}
# Dictionary to store images
images = {}


def handle_client(client_socket, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    while connected:
        try:
            message = client_socket.recv(4096)
            if not message:
                break

            data = pickle.loads(message)
            command = data['command']

            if command == 'REGISTER':
                username = data['username']
                public_key = data['public_key']
                # The server would sign this key and create a certificate
                certificate = f"cert-{username}"  # Placeholder for the actual certificate
                users[username] = {'public_key': public_key, 'certificate': certificate}
                response = {'status': 'REGISTERED', 'certificate': certificate}
                client_socket.send(pickle.dumps(response))
            elif command == 'POST_IMAGE':
                image_name = data['image_name']
                owner = data['owner']
                encrypted_image = data['encrypted_image']
                digital_signature = data['digital_signature']
                encrypted_aes_key = data['encrypted_aes_key']
                iv = data['iv']

                images[image_name] = {
                    'owner': owner,
                    'encrypted_image': encrypted_image,
                    'digital_signature': digital_signature,
                    'encrypted_aes_key': encrypted_aes_key,
                    'iv': iv
                }

                notification = {'command': 'NEW_IMAGE', 'image_name': image_name, 'owner': owner}
                broadcast(notification)
            elif command == 'DOWNLOAD':
                image_name = data['image_name']
                if image_name in images:
                    image_data = images[image_name]
                    response = {
                        'status': 'IMAGE_FOUND',
                        'image_data': image_data,
                        'certificate': users[image_data['owner']]['certificate']
                    }
                    client_socket.send(pickle.dumps(response))
                else:
                    response = {'status': 'IMAGE_NOT_FOUND'}
                    client_socket.send(pickle.dumps(response))

        except Exception as e:
            print(f"Error: {e}")
            connected = False

    client_socket.close()
    print(f"[DISCONNECTED] {addr} disconnected.")


def broadcast(message):
    for client in clients:
        try:
            client.send(pickle.dumps(message))
        except Exception as e:
            print(f"Error sending broadcast: {e}")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_HOST, SERVER_PORT))
server.listen()
print(f"[LISTENING] Server is listening on {SERVER_HOST}:{SERVER_PORT}")

clients = []


def start():
    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


start()
