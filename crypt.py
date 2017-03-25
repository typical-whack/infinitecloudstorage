import hashlib
import base64
from cryptography.fernet import Fernet


KEY = "PASSWORD"


class FernetCipher(object):

    def __init__(self, key):
        # turns the password into a 32char long key
        b64 = base64.urlsafe_b64encode(hashlib.sha256(key).digest())

        # make sure keys are repeatable
        with open("keys.txt", 'a') as ko:
            ko.write(b64)
            ko.write('\n')
        self.key = Fernet(b64)

    def encrypt(self, plaintext):
        token = self.key.encrypt(plaintext)
        return token

    # decrypts ciphertext
    def decrypt(self, ciphertext):
        return self.key.decrypt(ciphertext)

    # encrypts a file and returns a cell to be written
    def encrypt_file(self, file_path):
        with open(file_path, 'rb') as fo:
            plaintext = fo.read()
        enc = self.encrypt(plaintext)
        sheet_value = base64.b64encode(enc)
        return sheet_value

    # takes in cell contents and decrypts it into a file
    def decrypt_file(self, cell_contents, file_path):
        ciphertext = base64.b64decode(cell_contents)
        dec = self.decrypt(ciphertext)
        with open(file_path, 'wb') as fo:
            fo.write(dec)

if __name__ == "__main__":
    f = FernetCipher(KEY)
    to_be_written = f.encrypt_file("unlimited.jpg")
    f.decrypt_file(to_be_written, "unlimited-too.jpg")
