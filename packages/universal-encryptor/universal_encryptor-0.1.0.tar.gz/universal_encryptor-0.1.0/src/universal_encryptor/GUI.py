import customtkinter as ctk  # Import customtkinter (ctk): modern tkinter with dark mode and styled widgets
from tkinter import filedialog  # Import file dialog to allow users to browse files
from PIL import Image  # Import PIL (Pillow) for image handling
from customtkinter import CTkImage  # CTkImage is used to render images inside the GUI
import os  # Import os for file path and system interaction

from file_detection import detect_file_type  # Detects file type by reading binary signature
from crypt import encrypt_file, decrypt_file  # Functions to encrypt and decrypt files
from key_file import create_and_store_key, retrieve_key  # Functions to generate and load keys
from log import log_action  # Logs file actions like encryption and decryption

ctk.set_appearance_mode("dark")  # Set the GUI appearance mode to dark
ctk.set_default_color_theme("blue")  # Set the accent color theme to blue

class EncryptorApp(ctk.CTk):  # Define the main app class that extends from CTk window
    def __init__(self):  # Constructor for setting up the GUI
        super().__init__()  # Call the constructor of the CTk parent class
        self.title("Universal File Encryptor")  # Set the window title
        self.geometry("700x600")  # Set fixed size for the GUI window
        self.resizable(False, False)  # Disable window resizing

        self.file_path = None  # Store the selected file path
        self.image_widget = None  # Store the CTkImage widget
        self.image_label = None  # Label that will display the image

        self.title_label = ctk.CTkLabel(self, text="Universal File Encryptor + Decryptor", font=("Helvetica Neue", 22, "bold"))  # Main heading
        self.title_label.pack(pady=20)  # Add spacing below the label

        self.select_button = ctk.CTkButton(self, text="Browse File", command=self.browse_file)  # Button to select a file
        self.select_button.pack(pady=10)  # Add vertical spacing

        self.file_type_label = ctk.CTkLabel(self, text="No file selected", font=("Arial", 14))  # Label to display file type
        self.file_type_label.pack(pady=4)  # Add vertical spacing

        self.preview_label = ctk.CTkLabel(self, text="File Preview", font=("Arial", 14, "bold"))  # Label for the preview area
        self.preview_label.pack(pady=10)  # Add spacing

        self.preview_area = ctk.CTkTextbox(self, height=120, width=500)  # Create a textbox for showing file preview
        self.preview_area.pack(pady=5)  # Add spacing
        self.preview_area.insert("0.0", "Preview will appear here...\n")  # Insert initial text
        self.preview_area.configure(state="disabled")  # Make textbox read-only

        self.encrypt_button = ctk.CTkButton(self, text="Encrypt", command=self.encrypt, fg_color="green", hover_color="#006400")  # Create Encrypt button
        self.encrypt_button.pack(pady=10)  # Add spacing

        self.decrypt_button = ctk.CTkButton(self, text="Decrypt", command=self.decrypt, fg_color="red", hover_color="#8B0000")  # Create Decrypt button
        self.decrypt_button.pack(pady=10)  # Add spacing

    def clear_preview(self):  # Clear the preview area and image
        self.preview_area.configure(state="normal")  # Enable editing
        self.preview_area.delete("0.0", "end")  # Clear the content
        self.preview_area.configure(state="disabled")  # Disable editing again
        if self.image_label:  # If an image is displayed, remove it
            self.image_label.destroy()  # Destroy the image label
            self.image_label = None  # Reset the image label variable

    def display_preview(self, file_path, mime, ext):  # Show file preview based on type
        self.clear_preview()  # Clear any previous preview

        if mime.startswith("image"):  # If file is an image
            try:
                image = Image.open(file_path)  # Open the image
                image = image.resize((200, 200))  # Resize image
                self.image_widget = CTkImage(light_image=image, dark_image=image, size=(200, 200))  # Wrap in CTkImage
                self.image_label = ctk.CTkLabel(self, image=self.image_widget, text="")  # Create label to hold image
                self.image_label.pack(pady=5)  # Show the image in the GUI
            except Exception as e:  # If error occurs, show message
                self.log_status(f"Could not load image: {e}", error=True)

        elif mime.startswith("text") or ext == "txt":  # If file is text
            try:
                with open(file_path, 'r') as f:  # Open the text file
                    content = f.read(300)  # Read up to 300 characters
                    self.preview_area.configure(state="normal")  # Enable textbox
                    self.preview_area.insert("0.0", content)  # Insert text
                    self.preview_area.configure(state="disabled")  # Disable editing again
            except:  # If error reading text file
                self.log_status("Cannot preview this file.", error=True)

    def browse_file(self):  # Open file dialog and show preview
        file_path = filedialog.askopenfilename()  # Show file explorer
        if file_path:  # If user selects a file
            self.file_path = file_path  # Store the file path
            mime, ext = detect_file_type(file_path)  # Get file type info
            self.file_type_label.configure(text=f"Detected Type: {mime} ({ext})")  # Display type in label

            if file_path.endswith(".encrypted"):  # If file is encrypted
                self.clear_preview()  # Clear preview area
                self.preview_area.configure(state="normal")  # Enable editing
                self.preview_area.insert("0.0", "Encrypted file cannot be previewed.\n")  # Show warning
                self.preview_area.configure(state="disabled")  # Disable editing
            else:  # If file is not encrypted
                self.display_preview(file_path, mime, ext)  # Try to preview it

    def encrypt(self):  # Encrypt the selected file
        if not self.file_path:  # If no file selected
            self.log_status("Please select a file first.", error=True)  # Show error
            return

        output_file = self.file_path + ".encrypted"  # Name of output encrypted file

        try:
            key = create_and_store_key(output_file)  # Generate and store key
            encrypt_file(self.file_path, output_file, key)  # Encrypt the file
            log_action("ENCRYPT", os.path.basename(self.file_path), status="SUCCESS", details=f"Output: {output_file}")  # Log success
            self.log_status(f"File encrypted successfully.\nSaved as: {output_file}")  # Show success message
        except Exception as e:  # If error occurs
            log_action("ENCRYPT", os.path.basename(self.file_path), status="FAILURE", details=str(e))  # Log error
            self.log_status(f"Encryption failed: {e}", error=True)  # Show error

    def decrypt(self):  # Decrypt the selected file
        if not self.file_path:  # If no file selected
            self.log_status("Please select a file first.", error=True)  # Show error
            return

        output_file = self.file_path.replace(".encrypted", ".decrypted")  # Set output filename

        try:
            key = retrieve_key(self.file_path)  # Load the key
            decrypt_file(self.file_path, output_file, key)  # Decrypt file
            log_action("DECRYPT", os.path.basename(self.file_path), status="SUCCESS", details=f"Output: {output_file}")  # Log success
            self.log_status(f"File decrypted successfully.\nSaved as: {output_file}")  # Show success message
        except Exception as e:  # If error occurs
            log_action("DECRYPT", os.path.basename(self.file_path), status="FAILURE", details=str(e))  # Log error
            self.log_status(f"Decryption failed: {e}", error=True)  # Show error

    def log_status(self, message, error=False):  # Show messages in preview area
        self.preview_area.configure(state="normal")  # Enable textbox
        prefix = "Error: " if error else ""  # Add prefix if error
        self.preview_area.insert("end", prefix + message + "\n")  # Insert message
        self.preview_area.see("end")  # Scroll to bottom
        self.preview_area.configure(state="disabled")  # Disable textbox

if __name__ == "__main__":  # Run only if this file is the main program
    app = EncryptorApp()  # Create the GUI window
    app.mainloop()  # Run the GUI application