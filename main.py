import socket
import threading
import pickle

# Define server address and port
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 65432


def listen_for_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(4096)
            if not message:
                break

            data = pickle.loads(message)
            print(f"Received: {data}")

        except Exception as e:
            print(f"Error: {e}")
            break


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    username = input("Enter your username: ")
    # Placeholder for public key generation
    public_key = f"public_key_{username}"

    register_data = {
        'command': 'REGISTER',
        'username': username,
        'public_key': public_key
    }

    client_socket.send(pickle.dumps(register_data))
    response = pickle.loads(client_socket.recv(4096))
    print(f"Server response: {response}")

    if response['status'] == 'REGISTERED':
        certificate = response['certificate']
        print(f"Received certificate: {certificate}")

    thread = threading.Thread(target=listen_for_messages, args=(client_socket,))
    thread.start()

    while True:
        command = input("Enter command (POST_IMAGE/DOWNLOAD/EXIT): ")
        if command == 'POST_IMAGE':
            image_name = input("Enter image name: ")
            encrypted_image = f"encrypted_image_{image_name}"
            digital_signature = f"digital_signature_{image_name}"
            encrypted_aes_key = f"encrypted_aes_key_{image_name}"
            iv = f"iv_{image_name}"

            post_image_data = {
                'command': 'POST_IMAGE',
                'image_name': image_name,
                'owner': username,
                'encrypted_image': encrypted_image,
                'digital_signature': digital_signature,
                'encrypted_aes_key': encrypted_aes_key,
                'iv': iv
            }

            client_socket.send(pickle.dumps(post_image_data))
        elif command == 'DOWNLOAD':
            image_name = input("Enter image name to download: ")
            download_data = {
                'command': 'DOWNLOAD',
                'image_name': image_name
            }
            client_socket.send(pickle.dumps(download_data))
        elif command == 'EXIT':
            break


if __name__ == "__main__":
    main()
