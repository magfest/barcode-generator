from generator import BarcodeNumberGenerator

if __name__ == '__main__':
    generator = BarcodeNumberGenerator("badges.yaml")
    generator.generate_csv()