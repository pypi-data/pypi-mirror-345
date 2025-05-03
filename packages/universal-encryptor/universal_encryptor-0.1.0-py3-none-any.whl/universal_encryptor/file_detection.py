import filetype  # Filetype is a library that detects file type using magic numbers in the file's binary

def detect_file_type(file_path):
    kind = filetype.guess(file_path)  # Guess the file type based on its content, not the extension
    if kind:
        return kind.mime, kind.extension  # Return the mime type and extension (e.g., image/png, txt)
    else:
        return "unknown", None  # If type couldn't be guessed, return unknown