from django.test import TestCase

# Create your tests here.

# from tinyec import registry
# from PIL import Image
# import numpy as np
# import random
# import hashlib

# # ECC curve
# curve = registry.get_curve('brainpoolP256r1')

# # Generate ECC keys
# def generate_keypair():
#     priv_key = random.randint(1, curve.field.n - 1)
#     pub_key = priv_key * curve.g
#     return priv_key, pub_key

# # ECC encryption
# def ecc_encrypt(pub_key, plaintext_int):
#     k = random.randint(1, curve.field.n - 1)
#     c1 = k * curve.g
#     c2 = plaintext_int + (k * pub_key).x
#     return c1, c2

# # ECC decryption
# def ecc_decrypt(priv_key, c1, c2):
#     shared_secret = priv_key * c1
#     plaintext_int = c2 - shared_secret.x
#     return plaintext_int

# # Convert image to encrypted form
# def encrypt_image(image_path, pub_key):
#     img = Image.open(image_path).convert('L')  # Grayscale
#     img_array = np.array(img)
#     encrypted_data = []

#     for row in img_array:
#         encrypted_row = []
#         for pixel in row:
#             c1, c2 = ecc_encrypt(pub_key, int(pixel))
#             encrypted_row.append((c1, c2))
#         encrypted_data.append(encrypted_row)

#     return encrypted_data, img.size

# # Convert encrypted image back to original
# def decrypt_image(encrypted_data, priv_key, image_size):
#     decrypted_array = []

#     for row in encrypted_data:
#         decrypted_row = []
#         for c1, c2 in row:
#             pixel = ecc_decrypt(priv_key, c1, c2)
#             pixel = max(0, min(255, pixel))  # Ensure valid grayscale range
#             decrypted_row.append(pixel)
#         decrypted_array.append(decrypted_row)

#     img_array = np.array(decrypted_array, dtype=np.uint8)
#     decrypted_img = Image.fromarray(img_array, 'L')
#     return decrypted_img

# # Usage
# if __name__ == '__main__':
#     # Image encryption
#     priv_key, pub_key = generate_keypair()
#     encrypted_data, size = encrypt_image("hero-carousel-2.jpg", pub_key)
#     print("Image encrypted successfully.")

#     # Image decryption
#     decrypted_image = decrypt_image(encrypted_data, priv_key, size)
#     decrypted_image.save("decrypted_image.png")
#     print("Decrypted image saved as 'decrypted_image.png'")


# import os
# import hashlib
# from PIL import Image
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad, unpad
# from tinyec import registry
# import secrets

# curve = registry.get_curve('brainpoolP256r1')


# def encrypt_AES_key_with_ECC(pubKey, aes_key):
#     ephemeral_key = secrets.randbelow(curve.field.n)
#     shared_point = ephemeral_key * pubKey
#     shared_secret = hashlib.sha256(int.to_bytes(shared_point.x, 32, 'big')).digest()

#     encrypted_key = bytes([_a ^ _b for _a, _b in zip(aes_key, shared_secret)])
#     c1 = ephemeral_key * curve.g
#     return encrypted_key, c1


# def decrypt_AES_key_with_ECC(privKey, encrypted_key, c1):
#     shared_point = privKey * c1
#     shared_secret = hashlib.sha256(int.to_bytes(shared_point.x, 32, 'big')).digest()
#     aes_key = bytes([_a ^ _b for _a, _b in zip(encrypted_key, shared_secret)])
#     return aes_key


# def encrypt_image(img_path, pubKey):
#     # Generate AES key
#     aes_key = os.urandom(16)
#     cipher = AES.new(aes_key, AES.MODE_CBC)
#     iv = cipher.iv

#     # Open and convert image to RGB bytes
#     img = Image.open(img_path).convert('RGB')
#     img_data = img.tobytes()
#     encrypted_data = cipher.encrypt(pad(img_data, AES.block_size))

#     # Encrypt AES key with ECC
#     encrypted_key, c1 = encrypt_AES_key_with_ECC(pubKey, aes_key)

#     return encrypted_data, iv, encrypted_key, c1, img.size


# def decrypt_image(encrypted_data, iv, encrypted_key, c1, img_size, privKey):
#     # Decrypt AES key
#     aes_key = decrypt_AES_key_with_ECC(privKey, encrypted_key, c1)
#     cipher = AES.new(aes_key, AES.MODE_CBC, iv)
#     decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

#     # Convert back to RGB image
#     img = Image.frombytes('RGB', img_size, decrypted_data)
#     return img


# # Demo
# if __name__ == '__main__':
#     privKey = secrets.randbelow(curve.field.n)
#     pubKey = privKey * curve.g

#     encrypted_data, iv, encrypted_key, c1, img_size = encrypt_image("hero-carousel-2.jpg", pubKey)
#     print("Encryption complete.")
#     print(type(pubKey))
#     print(type(privKey))
#     print(type(encrypted_data))
#     print(type(iv))
#     print(type(encrypted_key))
#     print(type(c1))
#     print(type(img_size))


#     decrypted_img = decrypt_image(encrypted_data, iv, encrypted_key, c1, img_size, privKey)
#     decrypted_img.save("decrypted_sample.png")
#     print("Decryption complete. Saved as 'decrypted_sample.png'")
