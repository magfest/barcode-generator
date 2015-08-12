import yaml
import base64
import struct
import skip32
import code128


class BarcodeNumberGenerator:
    def __init__(self, yaml_file):
        with open(yaml_file, 'r') as stream:
            self.badge_types = yaml.load(stream)

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
            barcode_num = BarcodeNumberGenerator.generate_barcode_from_badge_num(
                badge_num=int(badge_num),
                event_id=self.event_id,
                salt=self.salt,
                key=self.secret_key
            )

            line = "{badge_num},{barcode_num}".format(
                badge_num=badge_num,
                barcode_num=barcode_num,
            )
            generate_lines.append(line)

        return generate_lines

    @staticmethod
    def generate_barcode_from_badge_num(badge_num, event_id, salt, key):
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

        if len(key) != 10:
            raise Exception("key length should be exactly 10 bytes")

        encrypted_string = encrypt(data_to_encrypt, key=key)

        # check to make sure it worked.
        decrypted = BarcodeNumberGenerator.get_badge_num_from_barcode(encrypted_string, salt, key)
        if decrypted['badge_num'] != badge_num or decrypted['event_id'] != event_id:
            raise Exception("didn't encode correctly")

        # check to make sure this barcode number is valid for Code 128 barcode
        BarcodeNumberGenerator.verify_barcode_is_valid_code128(encrypted_string)

        return encrypted_string

    @staticmethod
    def verify_barcode_is_valid_code128(encrypted_string):
        for c in encrypted_string:
            if c not in code128._charset_b:
                raise Exception("contains a char not valid in a code128 barcode")

    @staticmethod
    def get_badge_num_from_barcode(barcode_num, salt, key):
        decrypted = decrypt(barcode_num, key=key)

        result = dict()

        result['event_id'] = struct.unpack('>B', bytearray([decrypted[0]]))[0]

        badge_bytes = bytearray(bytes([0, decrypted[1], decrypted[2], decrypted[3]]))
        result['badge_num'] = struct.unpack('>I', badge_bytes)[0] - salt

        return result


def hexx(str):
    return ''.join(format(x, '02x') for x in str)


def encrypt(value, key):
    # skip32 generates 4 bytes output from 4 bytes input
    _encrypt = True
    skip32.skip32(key, value, _encrypt)

    # raw bytes aren't suitable for a Code 128 barcode though,
    # so convert it to base58 encoding
    # which is just some alphanumeric and numeric chars and is
    # designed to be vaguely human.  this takes our 4 bytes and turns it into 11ish bytes
    encrypted_value = base64.encodebytes(value).decode('ascii')

    # important note: because we are not an even multiple of 3 bytes, base64 needs to pad
    # the resulting string with equals signs.  we can strip them out knowing that our length is 4 bytes
    # IF YOU CHANGE THE LENGTH OF THE ENCRYPTED DATA FROM 4 BYTES, THIS WILL NO LONGER WORK.
    encrypted_value = encrypted_value.replace('==\n', '')

    return encrypted_value


def decrypt(value, key):
    # raw bytes aren't suitable for a Code 128 barcode though,
    # so convert it to base64 encoding
    # which is just some alphanumeric and numeric chars and is
    # designed to be vaguely human.  this takes our 4 bytes and turns it into 6ish bytes

    # important note: because we are not an even multiple of 3 bytes, base64 needs to pad
    # the resulting string with equals signs.  we can strip them out knowing that our length is 4 bytes
    # IF YOU CHANGE THE LENGTH OF THE ENCRYPTED DATA FROM 4 BYTES, THIS WILL NO LONGER WORK.
    value += '==\n'

    decoded = base64.decodebytes(value.encode('ascii'))

    # skip32 generates 4 bytes output from 4 bytes input
    _encrypt = False
    decrytped = bytearray(decoded)
    skip32.skip32(key, decrytped, _encrypt)

    return decrytped

