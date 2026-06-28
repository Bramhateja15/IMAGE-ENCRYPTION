import os
import secrets
import hashlib
import pickle
import base64
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from tinyec import registry, ec

curve = registry.get_curve('brainpoolP256r1')


def serialize_point(point):
    coords = (point.x, point.y)
    return base64.b64encode(pickle.dumps(coords)).decode('utf-8')


def deserialize_point(serialized_point):
    coords = pickle.loads(base64.b64decode(serialized_point.encode('utf-8')))
    return ec.Point(curve, coords[0], coords[1])


def encrypt_AES_key_with_ECC(pubKey, aes_key):
    ephemeral_key = secrets.randbelow(curve.field.n)
    shared_point = ephemeral_key * pubKey
    shared_secret = hashlib.sha256(int.to_bytes(shared_point.x, 32, 'big')).digest()

    encrypted_key = bytes([_a ^ _b for _a, _b in zip(aes_key, shared_secret)])
    c1 = ephemeral_key * curve.g
    return encrypted_key, c1


def decrypt_AES_key_with_ECC(privKey, encrypted_key, c1):
    shared_point = privKey * c1
    shared_secret = hashlib.sha256(int.to_bytes(shared_point.x, 32, 'big')).digest()
    return bytes([_a ^ _b for _a, _b in zip(encrypted_key, shared_secret)])


def encrypt_image(image_path, pubKey):
    aes_key = os.urandom(16)
    cipher = AES.new(aes_key, AES.MODE_CBC)
    iv = cipher.iv

    img = Image.open(image_path).convert('RGB')
    img_data = img.tobytes()
    encrypted_data = cipher.encrypt(pad(img_data, AES.block_size))

    encrypted_key, c1 = encrypt_AES_key_with_ECC(pubKey, aes_key)
    return encrypted_data, iv, encrypted_key, serialize_point(c1), img.size


def decrypt_image(encrypted_data, iv, encrypted_key, serialized_c1, img_size, privKey):
    c1 = deserialize_point(serialized_c1)
    aes_key = decrypt_AES_key_with_ECC(privKey, encrypted_key, c1)
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    return Image.frombytes('RGB', img_size, decrypted_data)


# from crypto_utils import encrypt_image, decrypt_image, curve
import secrets

if __name__ == "__main__":
    # Generate ECC key pair
    privKey = secrets.randbelow(curve.field.n)
    pubKey = privKey * curve.g
    print(type(privKey))
    # Encrypt image
    encrypted_data, iv, encrypted_key, serialized_c1, img_size = encrypt_image("hero-carousel-2.jpg", pubKey)
    print("[✓] Image Encrypted.")
    print(type(img_size))

    # Decrypt image
    decrypted_img = decrypt_image(encrypted_data, iv, encrypted_key, serialized_c1, img_size, privKey)
    decrypted_img.save("decrypted_output.png")
    print("[✓] Image Decrypted. Saved as 'decrypted_output.png'")
