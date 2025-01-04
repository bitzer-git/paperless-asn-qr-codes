import argparse
import re

from reportlab.lib.units import mm
from reportlab_qrcode import QRCodeImage

import avery_labels


def render(c, x, y):
    global startASN
    global digits
    barcode_value = f"ASN{startASN:0{digits}d}"
#    print(startASN, x / mm, y / mm)
    c.rotate(90)
    qr = QRCodeImage(barcode_value, size= 0.85 * y , border=0 )
    qr.drawOn(c, + 0.7 * mm, - y - 1 * mm)
    c.setFont("Helvetica", 3 * mm)
    c.drawString( ( 1.7 if startASN<10000 else 0.7 ) * mm, - y - 5 * mm,  f"{startASN:0{digits}d}")
    c.rotate(-90)
    startASN = startASN + 1

def main():
    # Match the starting position parameter. Allow x:y or n
    def _start_position(arg):
        if mat := re.match(r"^(\d{1,2}):(\d{1,2})$", arg):
            return (int(mat.group(1)), int(mat.group(2)))
        elif mat := re.match(r"^\d+$", arg):
            return int(arg)
        else:
            raise argparse.ArgumentTypeError("invalid value")

    parser = argparse.ArgumentParser(
        prog="paperless-asn-qr-codes",
        description="CLI Tool for generating paperless ASN labels with QR codes",
    )
    parser.add_argument("start_asn", type=int, help="The value of the first ASN")
    parser.add_argument(
        "output_file",
        type=str,
        default="labels.pdf",
        help="The output file to write to (default: labels.pdf)",
    )
    parser.add_argument(
        "--format", "-f", choices=avery_labels.labelInfo.keys(), default="herma10000"
    )
    parser.add_argument(
        "--digits",
        "-d",
        default=4,
        help="Number of digits in the ASN (default: 7, produces 'ASN0000001')",
        type=int,
    )
    parser.add_argument(
        "--border",
        "-b",
        action="store_true",
        help="Display borders around labels, useful for debugging the printer alignment",
    )
    parser.add_argument(
        "--row-wise",
        "-r",
        action="store_true",
        help="Increment the ASNs row-wise, go from left to right",
    )
    parser.add_argument(
        "--num-labels",
        "-n",
        type=int,
        help="Number of labels to be printed on the sheet",
    )
    parser.add_argument(
        "--pages",
        "-p",
        type=int,
        default=1,
        help="Number of pages to be printed, ignored if NUM_LABELS is set (default: 1)",
    )
    parser.add_argument(
        "--start-position",
        "-s",
        type=_start_position,
        help="Define the starting position on the sheet, eighter as ROW:COLUMN or COUNT, both starting from 1 (default: 1:1 or 1)",
    )

    args = parser.parse_args()
    global startASN
    global digits
    startASN = int(args.start_asn)
    digits = int(args.digits)
    label = avery_labels.AveryLabel(
        args.format, args.border, topDown=args.row_wise, start_pos=args.start_position
    )
    label.open(args.output_file)

    # If defined use parameter for number of labels
    if args.num_labels:
        count = args.num_labels
    else:
        # Otherwise number of pages*labels - offset
        count = args.pages * label.across * label.down - label.position
    label.render(render, count)
    label.close()

if __name__ == "__main__":
    main()

# python3 ./main.py 0 -b -p 1 labels.pdf