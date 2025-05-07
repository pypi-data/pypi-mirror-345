#!/usr/bin/env python3

"""Fix CommBank OFX statements

CommBank's OFX statements omit the FITID field for credit interest
transactions. This violates the specification, and renders the files
unreadable by spec-respecting software such as ofxtools and Zoho Books.

This script replaces the blank FITID fields with the transaction date
and the contents of the 'MEMO' field, with all spaces removed, which
makes the files spec compliant, and enables them to be imported into
ofxtools and Zoho Books.

Note that this tool assumes the specific OFX format produced by
CommBank. It is not guaranteed to work on arbitrary OFX files!
"""

import io
import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from ofxtools import OFXTree, utils
from ofxtools.header import make_header
from ofxtools.models.ofx import OFX


def fix_ofx(input_file):
    """Process OFX file"""

    input_file = Path(input_file).expanduser()
    output_file = input_file.with_stem(f"{input_file.stem}-fixed")

    with open(input_file, "rb") as file:
        input_data = file.read()

    #####################################################################
    #                                                                   #
    #  ofxtools mangles the FITID field when it is empty.               #
    #  We can avoid this by pre-processing it to include a placeholder  #
    #  ID, then process *this* with ofxtools to put the 'correct'       #
    #  date+memo ID.                                                    #
    #                                                                   #
    #####################################################################

    PLACEHOLDER = "PLACEHOLDER"
    processed_input_data = re.sub(
        rb"<FITID>(\s*?<)", rf"<FITID>{PLACEHOLDER}\1".encode("utf-8"), input_data
    )
    processed_input_data = io.BytesIO(processed_input_data)

    parser = OFXTree()
    parser.parse(processed_input_data)

    statements = parser.findall(".//STMTTRN")

    # Complete missing FITID fields
    for statement in statements:
        fitid = statement.find(".//FITID")
        if fitid.text == PLACEHOLDER:
            dtposted = statement.find(".//DTPOSTED").text
            memo = statement.find(".//MEMO").text

            fitid.text = f"{dtposted}{memo}".replace(" ", "")

    ofx = parser.convert()
    return ofx


def save_ofx(ofx: OFX, output_file: Path | str, ofx_version: int = 220):
    """Save OFX model to file"""

    output_file = Path(output_file).expanduser()

    root = ofx.to_etree()
    message = ET.tostring(root).decode()

    header = str(make_header(version=ofx_version))

    output = header + message

    with open(output_file, "w") as file:
        file.write(output)


def main():
    try:
        input_file = Path(sys.argv[1]).expanduser()
    except IndexError:
        print("Please supply an input file!")
        print("Usage: fix-commbank-ofx path/to/file.ofx")
        sys.exit(1)

    ofx = fix_ofx(input_file)
    output_file = input_file.with_stem(f"{input_file.stem}-fixed")

    save_ofx(ofx, output_file)


if __name__ == "__main__":
    main()
