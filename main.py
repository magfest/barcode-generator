from generator import BarcodeNumberGenerator

if __name__ == '__main__':
    generator = BarcodeNumberGenerator("badges.yaml")

    # TEST DATA
    # Anyone using this for production, make sure you change this. Obviously.
    # You will want to burn these particular numbers if you're anywhere near production servers.
    # And you will want to guard that secret_key with your goddamned life.
    generator.secret_key = bytes('JK65*&5Ba|','ascii') # must be 10 bytes
    generator.salt = 87
    generator.event_id = 255

    generator.generate_csv(filename='output.csv')