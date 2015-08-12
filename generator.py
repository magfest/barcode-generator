import yaml
import base64
import os
import random
import struct
from ctypes import create_string_buffer
import skip32
import base58

class BarcodeNumberGenerator:
    def __init__(self, yaml_file):
        with open(yaml_file, 'r') as stream:
            self.badge_types = yaml.load(stream)
            self.secret_key = bytes('JK65*&5Ba|','ascii') # must be 10 bytes
            self.salt = 87
            self.event_id = 255

    def generate_csv(self):
        badge_types = self.badge_types['badge_types']

        lines = []
        for badge_type, ranges in badge_types.items():
            range_start = int(ranges['range_start'])
            range_end = int(ranges['range_end'])
            lines = lines + self.generate_barcode_nums(range_start, range_end)

        for line in lines:
            print(line)

    def generate_barcode_nums(self, range_start, range_end):
        generate_lines = []
        for badge_num in range(range_start, range_end+1):
            barcode_num = self.generate_barcode_from_badge_num(int(badge_num), event_id=self.event_id, salt=self.salt, key=self.secret_key)

            line = "{badge_num},{barcode_num},{l}".format(
                badge_num=badge_num,
                barcode_num=barcode_num,
                l=len(barcode_num)
            )
            generate_lines.append(line)

        return generate_lines

    def generate_barcode_from_badge_num(self, badge_num, event_id, salt, key):
        # packed data going to be encrypted is:
        # byte 1 - 8bit event ID, usually 1 char
        # byte 2,3,4 - 24bit badge number

        salted_val = badge_num + (0 if not salt else salt)

        if salted_val > 0xFFFFFF:
            raise Exception("badge_number is too high " + badge_num)

        data_to_encrypt = struct.pack('>BI', event_id, salted_val)

        # remove the highest byte in that integer (2nd byte)
        data_to_encrypt = bytearray([data_to_encrypt[0], data_to_encrypt[2], data_to_encrypt[3], data_to_encrypt[4]])

        if len(data_to_encrypt) != 4:
            raise Exception("data to encrypt should be 4 bytes")

        if len(self.secret_key) != 10:
            raise Exception("key length should be exactly 10 bytes")

        encrypted_string = encrypt(data_to_encrypt, key=self.secret_key)
        #ds = bytes(encrypted_string, 'ascii')
        #test = decrypt(ds, key=self.secret_key)

        decrypted = self.get_badge_num_from_barcode(encrypted_string, salt, key)

        if decrypted['badge_num'] != badge_num or decrypted['event_id'] != event_id:
            raise Exception("didn't encode correctly")

        return encrypted_string

    def get_badge_num_from_barcode(self, barcode_num, salt, key):
        decrypted = decrypt(bytes(barcode_num, 'ascii'), key=key)

        result = dict()

        tmp = bytearray([decrypted[0]])
        result['event_id'] = struct.unpack('>B', tmp)[0]

        badge_bytes = bytearray(bytes([0, decrypted[1], decrypted[2], decrypted[3]]))
        result['badge_num'] = struct.unpack('>I', badge_bytes)[0] - salt

        return result


def hexx(str):
    return ''.join(format(x, '02x') for x in str)

def encrypt(value, key):
    # buffer = bytearray(4)

    # struct.pack_into(">I", buffer, 0, value)

    # skip32 generates 4 bytes output from 4 bytes input
    _encrypt = True
    print("unencrypted = " + hexx(value))
    skip32.skip32(key, value, _encrypt)

    # raw bytes aren't suitable for a Code 128 barcode though,
    # so convert it to base58 encoding
    # which is just some alphanumeric and numeric chars and is
    # designed to be vaguely human.  this takes our 4 bytes and turns it into 11ish bytes
    print("encrytped = " + hexx(value))
    encrypted_value = base58.b58encode_check(value)

    print("encrytped+encoded = " + encrypted_value)
    return encrypted_value


def decrypt(value, key):

    # raw bytes aren't suitable for a Code 128 barcode though,
    # so convert it to base58 encoding
    # which is just some alphanumeric and numeric chars and is
    # designed to be vaguely human.  this takes our 4 bytes and turns it into 11ish bytes
    print("d: encrytped+encoded = " + str(value))
    decoded = base58.b58decode_check(value)

    print("d: encrytped = " + hexx(decoded))
    # skip32 generates 4 bytes output from 4 bytes input
    _encrypt = False
    decrytped = bytearray(decoded)
    skip32.skip32(key, decrytped, _encrypt)

    print("d: unencrypted = " + hexx(decrytped))
    return decrytped

