from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import logging

# Configure logging to write to a file
logging.basicConfig(filename='image_sharing.log', level=logging.INFO, format='%(asctime)s - %(message)s')


class ImageUploader:
    def __init__(self, server_public_key_pem):
        self.server_public_key_pem = server_public_key_pem

    def encrypt_image(self, image_path, aes_key, iv):
        # Resmi AES anahtarıyla şifreleme (CBC modu)
        with open(image_path, 'rb') as f:
            plaintext = f.read()

        # Veriyi blok boyutuna tamamlayacak şekilde dolgu yapın
        block_size = algorithms.AES.block_size // 8  # AES blok boyutunu byte cinsinden alın
        padded_plaintext = self.pad_data(plaintext, block_size)

        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        return ciphertext

    def encrypt_aes_key(self, aes_key):
        # AES anahtarını sunucu açık anahtarıyla şifreleme
        server_public_key = serialization.load_pem_public_key(self.server_public_key_pem)
        encrypted_aes_key = server_public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return encrypted_aes_key

    def upload_image(self, user, image_path, image_name):
        if not user.is_registered():
            raise ValueError("User must be registered to upload images.")

            # Generate AES key and IV
        aes_key, iv = user.generate_aes_key()

        # Encrypt image (log message, but exclude large image data)
        logging.info(f"UPLOAD_IMAGE - User: {user.username}, Image: {image_name}")

        # Encrypt image
        encrypted_image = self.encrypt_image(image_path, aes_key, iv)

        # Encrypt AES key with server's public key
        encrypted_aes_key = self.encrypt_aes_key(aes_key)

        # Store image on server (log message, exclude large image data)
        server.store_image(user.username, image_name, encrypted_image, encrypted_aes_key, iv)

def pad_data(self, data, block_size):
    padding_length = block_size - (len(data) % block_size)
    padded_data = data + bytes([padding_length]) * padding_length
    return padded_data