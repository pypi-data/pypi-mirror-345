import os  # Used to check if key file exists and to build file paths
from crypt import generate_key, save_key, load_key  # Functions imported for key generation and file-based storage

def get_key_path(filename):
    return f"{filename}.key"  # Create a filename for the key (e.g., "document.txt.encrypted.key")

def create_and_store_key(for_filename):
    key = generate_key()  # Generate a brand new AES encryption key
    key_path = get_key_path(for_filename)  # Get the filename to store the key
    save_key(key, key_path)  # Save the key to disk
    return key  # Return the key to be used for encryption

def retrieve_key(for_filename):
    key_path = get_key_path(for_filename)  # Get the path to the stored key
    if not os.path.exists(key_path):  # Check if the key file exists
        raise FileNotFoundError(f"Key file not found: {key_path}")  # Raise error if missing
    return load_key(key_path)  # Load and return the stored key