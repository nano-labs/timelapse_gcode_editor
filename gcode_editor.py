import re
import sys
from decimal import Decimal

LAST_POS_RE = re.compile("G0[F0-9\s]* X[0-9\.]+ Y[0-9\.]+\n")
LAST_E_RE = re.compile("G1[F0-9\s]* X[0-9\.]+ Y[0-9\.]+ E([0-9\.]+)\n")

def replacer(lines, new_filename):
    shots = 0
    new_file = open(new_filename, "w")
    last_3 = ["", "", ""]
    last_E = None
    last_pos = ""
    for line in lines:
        if not line:
            continue
        # print(repr(line))
        if LAST_E_RE.match(line):
            last_E = Decimal(LAST_E_RE.match(line).groups()[0])
        last_3 = last_3[1:] + [line]
        if line == ";timelapse_placeholder\n":
            shots += 1
            assert LAST_POS_RE.match(last_3[0])
            assert last_E is not None
            last_pos = last_3[0]
            new_file.write(";TimeLapse Begin\n")
            new_file.write("G1 F1800 E%s; retract 3mm\n" % (last_E - 5))
            new_file.write("G1 F9000 X0 Y190 ;Park print head\n")
            new_file.write("M400 ;Wait for moves to finish\n")
            new_file.write("G4 P3000 ;Wait for camera\n")
            new_file.write(last_pos)
            new_file.write("G1 F1800 E%s\n" % last_E)
            last_E = None
        else:
            new_file.write(line)
    print("%s shots" % shots)





filename = sys.argv[1]
new_filename = "tl_%s" % filename

with open(filename, "r") as origin:
    replacer(origin.readlines(), new_filename)
