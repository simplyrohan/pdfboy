#!/usr/bin/env python
import argparse
import os
import base64

# create a parser object
parser = argparse.ArgumentParser(description = "Embed ROM files into code using Base64")
 
# add argument
parser.add_argument("rom", nargs=1, metavar="rom", type=str,  help="Path to ROM file (.gb or .gbc file)")

parser.add_argument("output", nargs=1, metavar="file", type=str, help="Path to file where ROM will be embedded")

parser.add_argument("--tag",nargs=1, metavar="tag", type=str, help="Tag or string to replace with ROM", required=False)

# parse the arguments from standard input
args = parser.parse_args()

if os.path.exists(args.output[0]):
    if os.path.exists(args.rom[0]):
        tag = "__replace_with_rom__"
        if args.tag:
            tag = args.tag[0]
        
        # Base64 encode rom file
        print("Encoding", args.rom[0], "to Base64")
        with open(args.rom[0], "rb") as rom:
            romb64 = base64.b64encode(rom.read()).decode("utf-8")

        print("Embedding into", args.output[0])
        with open(args.output[0], "r") as output:
            output_content = output.read()
        
        output_content = output_content.replace(tag, romb64)

        with open(args.output[0], "w") as output:
            output.write(output_content)

        print("Done!")
        
    else:
        raise FileNotFoundError("Could not find ROM file " + args.rom[0])
else:
    raise FileNotFoundError("Could not find output file " + args.output[0])