from generator import BarcodeNumberGenerator

if __name__ == '__main__':
    generator = BarcodeNumberGenerator("badges.yaml")

    # todo: don't harcode these, obviously.
    generator.secret_key = bytes('JK65*&5Ba|','ascii') # must be 10 bytes
    generator.salt = 87
    generator.event_id = 255

    generator.generate_csv()