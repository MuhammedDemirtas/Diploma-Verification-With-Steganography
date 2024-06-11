import reedsolo
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import numpy as np
import pywt
import cv2
import os

def convert_to_binary(data):

    """
    Converts the given data to binary representation.

    :param data: Data to be converted to binary.
    :return: Binary representation of the data as bytes.
    """

    # Convert each character in the data to its ASCII value and then to its binary representation.
    binary_data = ''.join(format(ord(char), '08b') for char in data)

    # Convert the binary string to bytes by grouping every 8 bits and converting to integer and then converting the integers to bytes.
    return bytes(int(binary_data[i:i+8], 2) for i in range(0, len(binary_data), 8))

def sha256_hash(data):

    """
    Computes the SHA-256 hash of the given data.

    :param data: Data to be hashed.
    :return: SHA-256 hash value as bytes.
    """

    # Create a SHA-256 hash object.
    hash_object = hashlib.sha256()

    # Update the hash object with the data.
    hash_object.update(data)

    # Return the digest (hash) value as bytes.
    return hash_object.digest()

def aes_encrypt(data):

    """
    Encrypts the given data using AES encryption in ECB mode.

    :param data: Data to be encrypted.
    :return: Encrypted data.
    """

    # AES encryption key
    key = b".M2K5C_78_C3T5O."

    # Define the backend for the encryption.
    backend = default_backend() # Use the default backend for cryptography operations

    # Create a cipher with AES algorithm and ECB mode.
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend) #ECB mode is an AES encryption mode where each block is individually encrypted with the same key.

    # Create an encryptor object.
    encryptor = cipher.encryptor()

    # Apply PKCS7 padding to the data.
    padder = padding.PKCS7(128).padder()

    # Perform encryption by passing the padded data to the encryptor's update method and then finalizing the encryption process to obtain the encrypted data.
    padded_data = padder.update(data) + padder.finalize()

    # Perform encryption.
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data

def aes_decrypt(data):

    """
    Decrypts the given data using AES decryption.

    :param data: Data to be decrypted.
    :return: Decrypted data.
    """

    key = b".M2K5C_78_C3T5O." # AES encryption key.

    # Define the backend for the encryption.
    backend = default_backend() # Use the default backend for cryptography operations

    # Create a cipher with AES algorithm and ECB mode.
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend) #ECB mode is an AES encryption mode where each block is individually encrypted with the same key.

    # Create a decryptor object.
    decryptor = cipher.decryptor()

    # Perform decryption.
    decrypted_data = decryptor.update(data) + decryptor.finalize()

    # Perform unpadding using PKCS7 padding scheme.
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()
    return unpadded_data

def reed_solomon_encode(data):

    """
    Encodes the given data using Reed-Solomon encoding.

    :param data: Data to be encoded.
    :return: Encoded data.
    """

    n = 16  # Total number of symbols.
    k = 8   # Number of data symbols.

    # Create a Reed-Solomon codec with the appropriate parameters.
    rsc = reedsolo.RSCodec(n - k)

    # Encode the data.
    encoded = rsc.encode(data)

    return encoded

def reed_solomon_decode(encoded):

    """
    Decodes a Reed-Solomon encoded data.

    :param encoded: Encoded data to be decoded.
    :return: Decoded data.
    """

    n = 16 # Total number of symbols
    k = 8  # Number of data symbols

    # Create a Reed-Solomon codec with the appropriate parameters.
    rsc = reedsolo.RSCodec(n - k)

    # Decode the encoded data.
    decoded_tuple = rsc.decode(encoded)

    # Extract the decoded data from the tuple.
    decoded = decoded_tuple[0]

    return decoded

def wavelet_transform(image_path, message, output_dir):

    """
    Embeds a message into an image using wavelet transformation steganography.

    :param image_path: Path to the input image.
    :param message: Message to be hidden in the image.
    :param output_dir: Directory to save the output image.
    """

    # Load the image.
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Resim yüklenemedi.") # Image could not be loaded.

    # Extract the blue channel.
    blue_channel = image[:, :, 0]

    # Convert the message to a binary string and add an end marker.
    bits = ''.join(format(ord(i), '08b') for i in message) + '00000000'

    # Get the dimensions of the blue channel.
    height, width = blue_channel.shape

    # Define the size of pieces to be processed.
    piece_size = 512

    # Create a new blue channel to store the modified data.
    new_blue_channel = np.zeros_like(blue_channel)
    for y in range(0, height, piece_size):
        for x in range(0, width, piece_size):

            # Extract a piece of the blue channel.
            piece = blue_channel[y:y+piece_size, x:x+piece_size]

            # Get the dimensions of the current piece.
            piece_height, piece_width = piece.shape

            # Perform a 2D discrete wavelet transform.
            coeffs = pywt.dwt2(piece, 'haar') # Reconstruct the piece using inverse discrete wavelet transform.
            LL, (LH, HL, HH) = coeffs # Retrieve the wavelet coefficients from the result of the wavelet transform.

            # Modify the HH sub-band with the message bits.
            HH = HH.astype(np.int64)
            for i, bit in enumerate(bits):
                if i < HH.size:
                    HH.flat[i] = (HH.flat[i] & ~1) | int(bit)
                else:
                    break

            # Perform an inverse 2D wavelet transform.
            new_coeffs = LL, (LH, HL, HH)
            new_piece = pywt.idwt2(new_coeffs, 'haar') # Reconstruct the piece using inverse discrete wavelet transform.

            # Place the modified piece back into the new blue channel.
            new_piece = new_piece[:piece_height, :piece_width]

            # Place the reconstructed piece back into the new blue channel at the appropriate position.
            new_blue_channel[y:y+piece_height, x:x+piece_width] = new_piece

    # Replace the blue channel in the original image with the modified blue channel.
    image[:, :, 0] = new_blue_channel

    # Generate the output file path.
    filename = os.path.basename(image_path)
    name_without_extension, extension = os.path.splitext(filename)
    output_filename = f"{name_without_extension}.png"
    output_path = os.path.join(output_dir, output_filename)

    # Save the modified image.
    if not cv2.imwrite(output_path, np.clip(image, 0, 255).astype(np.uint8), [cv2.IMWRITE_PNG_COMPRESSION, 0]):
        raise ValueError("Resim kaydedilemedi.")

def wavelet_steganaliz(image_path):

    """
    Extracts a hidden message from an image using wavelet transformation steganography.

    :param image_path: Path to the input image.
    :return: The hidden message.
    """

    # Load the image (Diploma).
    image = cv2.imread(image_path, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Resim yüklenemedi.") # Image could not be loaded.

    # Extract the blue channel.
    blue_channel = image[241:614, 854:1154, 0]
    #[241:614, 854:1154, 0]

    # Get the dimensions of the blue channel.
    height, width = blue_channel.shape

    # Define the size of pieces to be processed.
    piece_size = 512

    bits = ''
    for y in range(0, height, piece_size):
        for x in range(0, width, piece_size):

            # Extract a piece of the blue channel.
            piece = blue_channel[y:y+piece_size, x:x+piece_size]

            # Get the dimensions of the current piece.
            piece_height, piece_width = piece.shape

            # Perform a 2D discrete wavelet transform.
            coeffs = pywt.dwt2(piece, 'haar') # Reconstruct the piece using inverse discrete wavelet transform.
            LL, (LH, HL, HH) = coeffs # Retrieve the wavelet coefficients from the result of the wavelet transform.

            # Extract the message bits from the HH sub-band.
            HH = HH.astype(np.int64)
            for val in HH.flat:
                bits += str(val & 1)

    # Find the end marker.
    end_marker = '00000000'
    end_index = bits.find(end_marker)
    if end_index == -1:
        raise ValueError("Mesajın sonu bulunamadı.") # End of the message not found.

    # Convert the binary string back to a readable message.
    message = ''.join(chr(int(bits[i:i+8], 2)) for i in range(0, end_index, 8))

    return message.strip() # Return the hidden message.


##cozulen_mesaj = wavelet_steganaliz(os.path.join("Gizlenenler", f"DiplomaOrnek1.png"))
##print("Çözülen mesaj:", cozulen_mesaj)
