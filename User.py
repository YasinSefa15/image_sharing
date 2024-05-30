import os

from cryptography.hazmat.primitives import serialization, hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding, rsa


class User:
    def __init__(self, username, mac_key):
        self.username = username
        self.private_key = None
        self.public_key = None
        self.certificate = None
        self.mac_key = mac_key  # MAC anahtarı

    def generate_key_pair(self):
        # Anahtar çifti oluşturma
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()

    def get_public_key_pem(self):
        # Açık anahtarı PEM formatında alma
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def get_private_key_pem(self):
        # Özel anahtarı PEM formatında alma
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def register(self, server):
        # Sunucuya kayıt olma
        self.generate_key_pair()
        self.certificate = server.register_user(self.username, self.get_public_key_pem())

    def verify_certificate(self, server_public_key_pem):
        # Sertifikayı doğrulama
        server_public_key = serialization.load_pem_public_key(server_public_key_pem)
        try:
            server_public_key.verify(
                self.certificate.signature,
                self.certificate.tbs_certificate_bytes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            print("Certificate verified successfully.")
        except Exception as e:
            print(f"Certificate verification failed: {e}")

    def load_private_key(self, private_key_path):
        # Özel anahtarı dosyadan yükleme
        with open(private_key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )

    def generate_aes_key(self):
        # AES anahtar ve IV oluşturma
        aes_key = os.urandom(32)  # 256-bit (32 byte) anahtar
        iv = os.urandom(16)       # 128-bit (16 byte) IV
        return aes_key, iv

    def sign_data(self, data):
        # Veriyi özel anahtarıyla imzalama (SHA256)
        signature = self.private_key.sign(
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return signature

    def create_mac(self, message):
        # MAC oluşturma
        h = hmac.HMAC(self.mac_key, hashes.SHA256(), backend=default_backend())
        h.update(message.encode('utf-8'))
        return h.finalize()

    def verify_mac(self, message, received_mac):
        # MAC doğrulama
        expected_mac = self.create_mac(message)
        return hmac.compare_digest(expected_mac, received_mac)
