import yaml
import base64
import os


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
            lines = lines + BarcodeNumberGenerator.generate_barcode_nums(range_start, range_end)

        for line in lines:
            print(line)

    @staticmethod
    def generate_barcode_nums(range_start, range_end):
        generated_nums = []
        generate_lines = []
        for badge_num in range(range_start, range_end+1):
            barcode_num = None

            # ensure we don't ever create duplicate barcode#'s
            while True:
                barcode_num = BarcodeNumberGenerator.generate_barcode_num()
                if barcode_num not in generated_nums:
                    generated_nums.append(barcode_num)
                    break

            line = "{badge_num},{barcode_num}".format(
                badge_num=badge_num,
                barcode_num=barcode_num
            )
            generate_lines.append(line)

        return generate_lines

    @staticmethod
    def generate_barcode_num():
        return str(base64.b64encode(os.urandom(16)))[2:][:-3].upper()
