from cryptography.fernet import Fernet  # Importing Fernet from cryptography to use AES encryption (symmetric key encryption)

def generate_key():
    return Fernet.generate_key()  # Generate a new AES key

def save_key(key, key_path):
    with open(key_path, 'wb') as key_file:  # Open a file in write binary mode to store the key
        key_file.write(key)  # Write the key to the file

def load_key(key_path):
    with open(key_path, 'rb') as key_file:  # Open a key file in read binary mode
        return key_file.read()  # Read and return the encryption key

def encrypt_file(input_path, output_path, key):
    fernet = Fernet(key)  # Use the Fernet class with the key to create an encryptor
    with open(input_path, 'rb') as file:  # Open the original file in binary read mode
        original_data = file.read()  # Read all data from the file
    encrypted_data = fernet.encrypt(original_data)  # Encrypt the data
    with open(output_path, 'wb') as file:  # Open the destination file in binary write mode
        file.write(encrypted_data)  # Write the encrypted data to the new file

def decrypt_file(input_path, output_path, key):
    fernet = Fernet(key)  # Create a decryptor using the same key
    with open(input_path, 'rb') as file:  # Open the encrypted file
        encrypted_data = file.read()  # Read the encrypted content
    decrypted_data = fernet.decrypt(encrypted_data)  # Decrypt the data
    with open(output_path, 'wb') as file:  # Open the destination file
        file.write(decrypted_data)  # Write the decrypted data back to disk