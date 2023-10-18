import csv
import random
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64
import os


# Function to generate random check data
def generate_check_data():
    check_number = random.randint(1000, 9999)
    payee = "Company " + str(random.randint(1, 10))
    amount = round(random.uniform(100.0, 1000.0), 2)
    issue_date = datetime.now() - timedelta(days=random.randint(1, 30))
    return check_number, payee, amount, issue_date


# Generate a positive pay file
def generate_positive_pay_file(file_path, num_checks):
    with open(file_path, mode='w', newline='') as file:
        fieldnames = ['CheckNumber', 'Payee', 'Amount', 'IssueDate']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()

        for _ in range(num_checks):
            check_number, payee, amount, issue_date = generate_check_data()
            writer.writerow({
                'CheckNumber': check_number,
                'Payee': payee,
                'Amount': amount,
                'IssueDate': issue_date.strftime('%Y-%m-%d')
            })


def password_to_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet key from a given password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def encrypt_file(file_path: str, password: str) -> None:
    """Encrypt a file in place using a password."""
    salt = os.urandom(16)
    key = password_to_key(password, salt)

    with open(file_path, 'rb') as file:
        data = file.read()

    f = Fernet(key)
    encrypted_data = f.encrypt(data)

    with open(file_path, 'wb') as file:
        file.write(salt + encrypted_data)


def generate_and_encrypt_positive_pay_file(output_file_path, password, num_checks):
    # Temporary file path for the positive pay file before encryption
    temp_file_path = "temp_positive_pay_file.csv"

    # Generate the positive pay file
    generate_positive_pay_file(temp_file_path, num_checks)

    # Encrypt the temporary file and save it to the desired output path
    encrypt_file(temp_file_path, password)

    # Rename (or move) the encrypted temporary file to the specified output location
    os.rename(temp_file_path, output_file_path)


# Define your password and number of checks to generate
password = "YourStrongPasswordHere"  # Change this to your desired password
num_checks_to_generate = 10

# Define where you want the encrypted file to be saved
encrypted_file_path = "encrypted_positive_pay_file.csv"

# Generate and encrypt the positive pay file
generate_and_encrypt_positive_pay_file(encrypted_file_path, password, num_checks_to_generate)
