# Diploma-Verification-With-Steganography

This project provides a robust method for securing diplomas using steganography techniques combined with cryptographic functions. The primary focus is to hide a message within an image (the diploma) using wavelet transformation and to ensure data integrity and security through encryption and error correction.

--------------------------------------------------------------

# Requirements

* Python 3.6+
* OpenCV (cv2)
* NumPy (numpy)
* Pandas
* Hashlib
* PyWavelets (pywt)
* Cryptography (cryptography)
* ReedSolomon (reedsolo)
* tkinter
* PIL
* pypyodbc

-----------------------------------------------------

# Usage

* Login:

* Enter the username and password to log in.
* Depending on the user's effect value, access to the steganography process may be restricted.
* Main Menu:

* After a successful login, the main menu is displayed with options to perform steganography, verification, and * view help.
* Steganography Process:

* Select either "Individual" or "Department".
* Enter the required ID or department name.
* Click "Start" to perform the steganography process.
* The application will hide the data in the diploma image and store the necessary keys and hashes in the database.
* Verification Process:

* Click the "Verification Process" button.
* Select the diploma image file to verify.
* The application will check the hidden data and verify the authenticity of the diploma.

----------------------------------------------------

# dvwstool.py
* convert_to_binary: Converts text to binary format.
* sha256_hash: Generates a SHA-256 hash of the data.
* aes_encrypt: Encrypts data using AES algorithm.
* aes_decrypt: Decrypts data encrypted with AES.
* reed_solomon_encode: Encodes data using Reed-Solomon coding.
* reed_solomon_decode: Decodes Reed-Solomon encoded data.
* wavelet_transform: Embeds a message into an image using wavelet transform.
* wavelet_steganaliz: Performs steganalysis on an image using wavelet transform.

---------------------------------------------------

# DVWS.py
* Contains additional functions for processing and verifying diplomas.
* wavelet_steganaliz: Performs steganalysis on an image using wavelet transform.
* reed_solomon_decode: Decodes Reed-Solomon encoded data.
* aes_decrypt: Decrypts AES-encrypted data.

-------------------------------------------------------

# Developer Notes

When you run the application, you will first encounter a login screen. Enter the necessary information to login successfully. Then, you can choose among the options presented on the screen. If you choose steganography, after entering the student ID or faculty name for bulk encryption, it will extract the corresponding image from the diploma file. If you select security, you can search the database for the document you select for security processing.

---------------------------------------------------------




