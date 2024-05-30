from ImageUploader import ImageUploader
from Server import Server
from User import User

# Sunucu örneği oluşturma
server = Server()

# Kullanıcı örneği oluşturma
alice = User("Alice",b'mac_key')

# Alice'in kayıt işlemi
alice.register(server)

# Sertifika doğrulama
server_public_key_pem = server.get_public_key_pem()
alice.verify_certificate(server_public_key_pem)

# Kullanıcı için özel anahtarı yükleme
alice.load_private_key('alice_private_key.pem')

# ImageUploader örneği oluşturma
uploader = ImageUploader(server.get_public_key_pem())

# Resmi yükleme işlemi
image_path = 'my_image.jpg'
image_name = 'my_image.jpg'
uploader.upload_image(alice, image_path, image_name)

# Simüle edilmiş bir NEW_IMAGE mesajı alındığını varsayalım
image_name_received = 'my_image.jpg'
owner_name_received = 'Alice'
print(f"Received NEW_IMAGE message: image_name='{image_name_received}', owner_name='{owner_name_received}'")

# Kullanıcı için DOWNLOAD işlemi
downloader = User("Bob")  # Bob kullanıcı olarak düşünelim
download_result = downloader.download_image(server, image_name_received)
if download_result:
    print("Image download successful.")
else:
    print("Image download failed.")