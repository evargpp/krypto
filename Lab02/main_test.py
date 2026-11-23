from secrets import choice
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import time
import matplotlib.pyplot as plt

MODES = {
    "ECB": AES.MODE_ECB,
    "CBC": AES.MODE_CBC,
    "CFB": AES.MODE_CFB,
    "OFB": AES.MODE_OFB,
    "CTR": AES.MODE_CTR
}

for mode_name, mode in MODES.items():
    print("MODE_NAME:", mode_name)
    print("MODE:", mode)

print(type(MODES))
