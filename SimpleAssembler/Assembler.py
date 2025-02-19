from binary_encoder_1 import riscV
from error_checker import error_checker

inputFile, outputfile = input().split()

encoder = riscV()

with open(inputFile, 'r') as f:
    lines = f.readlines()
labels = {}

adr = 0

for line in lines:
    
    line = line.strip()
    if not line:
        continue
    if ":" not in line:
        adr+=4
        continue
    label, value = line.split(":")
    if label in labels:
        with open(outputfile, "w") as g:
            g.write("repeated lables")
            quit()
    labels[label] = adr
    adr+=1

encoder.labels = labels

error_checker(encoder.registers, lines, labels)


instructions = []
adr = 0

for line in lines:
    line = line.strip()
    if not line:
        continue
    if ":" in line:
         l, ins = line.split(":")

    # call appropriate conversion

    instructions.append(ins)

#check virtual halt

with open(outputfile, "w") as o:
    o.write("\n".join(instructions))

binary = encoder.assembler(lines)

virtualHalt = "0"*25 + "0110011"

if virtualHalt in binary:
    if binary[-1]!=virtualHalt:
        with open(outputfile, "w") as g:
            g.write("Last line is not virtual halt")
            quit()
else:
    with open(outputfile, "w") as g:
        g.write("Virtual Halt not present")
        quit()

with open(outputfile, "w") as g:
    g.write("\n".join(binary))