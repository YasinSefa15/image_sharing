from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import logging
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(message)s')

class Server:
    def __init__(self):
        self.users = {}
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()
        self.image_store = {}
        self.online_users = set()

    def store_image(self, owner_username, image_name, encrypted_image, digital_signature, encrypted_aes_key, iv):
        # Resmi sunucuya kaydetme
        if owner_username not in self.users:
            raise ValueError("User must be registered to store images.")

            # Store image details (log message, exclude large image data)
        logging.info(f"STORE_IMAGE - Owner: {owner_username}, Image: {image_name}")

        # Store image
        self.image_store[image_name] = {
            'owner': owner_username,
            'encrypted_image': encrypted_image,
            'encrypted_aes_key': encrypted_aes_key,
            'iv': iv
        }
        self.notify_all_users(image_name, owner_username)

    def get_public_key_pem(self):
        # Sunucu açık anahtarını PEM formatında döndürme (simülasyon amaçlı)
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def register_user(self, username, public_key_pem):
        # Kullanıcıyı kaydetme ve sertifika oluşturma
        public_key = serialization.load_pem_public_key(public_key_pem)

        self.users[username] = public_key
        return public_key

    def notify_all_users(self, image_name, owner_username):
        # Tüm çevrimiçi kullanıcılara yeni resim bildirimi gönderme
        message = f"NEW_IMAGE {image_name} {owner_username}"
        for user in self.online_users:
            # Bildirimi göndermek için bir mekanizma eklenebilir (ör. websocket, e-posta, vb.)
            print(f"Sending notification to {user}: {message}")

    def add_online_user(self, username):
        # Kullanıcıyı çevrimiçi kullanıcılar listesine ekleme
        self.online_users.add(username)

    def remove_online_user(self, username):
        # Kullanıcıyı çevrimdışı kullanıcılar listesine ekleme
        self.online_users.remove(username)

    def download_image(self, image_name, requesting_user):
        # Resim indirme işlemi
        if image_name not in self.image_store:
            print(f"Error: Image '{image_name}' not found on the server.")
            return None

        image_data = self.image_store[image_name]
        owner_username = image_data['owner']
        encrypted_image = image_data['encrypted_image']
        digital_signature = image_data['digital_signature']
        encrypted_aes_key = image_data['encrypted_aes_key']
        iv = image_data['iv']

        # Kullanıcının sertifika ile doğrulanmış genel anahtarını al
        owner_public_key = self.users.get(owner_username, None)
        if not owner_public_key:
            print(f"Error: Owner's public key not found for user '{owner_username}'.")
            return None

        # Kullanıcı için AES anahtarını sunucu tarafından şifrele
        encrypted_requesting_user_aes_key = owner_public_key.encrypt(
            requesting_user.aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return {
            'encrypted_image': encrypted_image,
            'digital_signature': digital_signature,
            'owner_public_key': owner_public_key,
            'encrypted_requesting_user_aes_key': encrypted_requesting_user_aes_key,
            'iv': iv
        }
