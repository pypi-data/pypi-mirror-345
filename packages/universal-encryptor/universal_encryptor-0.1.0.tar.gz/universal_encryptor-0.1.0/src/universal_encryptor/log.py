import datetime  # Used to get the current timestamp for logging

LOG_FILE = "activity_log.txt"  # Define the log file name

def log_action(action, filename, status="SUCCESS", details=""):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current time formatted
    with open(LOG_FILE, 'a') as log_file:  # Open the log file in append mode
        log_file.write(f"[{timestamp}] [{action}] File: {filename} | Status: {status} | {details}\n")  # Write log entry