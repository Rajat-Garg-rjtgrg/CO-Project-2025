class riscV:
    def __init__(self):
        self.opcodes={
            "add":0b0110011,"sub":0b0110011, "slt":0b0110011,
            "srl":0b0110011,"or":0b0110011,  "and":0b0110011,
            "lw":0b0000011, "addi":0b0010011,"jalr":0b1100111,
            "sw":0b0100011, "beq":0b1100011, "bne":0b1100011,
            "jal":0b1101111
        }
        self.registers= {
        "zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011",
        "tp": "00100", "t0": "00101", "t1": "00110", "t2": "00111",
        "s0": "01000", "s1": "01001", "a0": "01010", "a1": "01011",
        "a2": "01100", "a3": "01101", "a4": "01110", "a5": "01111",
        "a6": "10000", "a7": "10001", "s2": "10010", "s3": "10011",
        "s4": "10100", "s5": "10101", "s6": "10110", "s7": "10111",
        "s8": "11000", "s9": "11001", "s10": "11010", "s11": "11011",
        "t3": "11100", "t4": "11101", "t5": "11110", "t6": "11111"
        }
        self.funct3 = {
            "add": "000", "sub": "000", "slt": "010", "srl": "101",
            "or": "110", "and": "111", "lw": "010", "addi": "000",
            "jalr": "000", "sw": "010", "beq": "000", "bne": "001"
        }
        self.labels={}
        self.current=0
    def encode_i_type(self, instr, rd, rs1, imm):
        opcode = format(self.opcodes[instr], '07b')
        funct3 = self.funct3[instr]
        imm1 = format(int(imm), '012b')
        return f"{imm1}{self.registers[rs1]}{funct3}{self.registers[rd]}{opcode}"
    def encode_s_type(self, instr, rs1, rs2, offset_base):
        opcode = format(self.opcodes[instr], '07b')
        funct3 = self.funct3[instr]
        offset, base = offset_base.split("(")
        base = base.strip(")")
        offset = int(offset)
        imm = format(offset, '012b')
        
        imm1 = imm[:7]
        imm2 = imm[7:]
        return f"{imm1}{self.registers[rs2]}{self.registers[base]}{funct3}{imm2}{opcode}"

    
    def encode_j_type(self, instr, rd, label, pc):
        opcode = format(self.opcodes[instr], '07b')
        if label in self.labels: imm = self.labels[label] - pc
        elif label.lstrip('-').isdigit(): imm = int(label)
        else: raise ValueError(f"Unknown label or invalid offset: {label}")

        if imm < 0: imm = (1 << 21) + imm

        imm = format(imm, '021b')[-21:]

        imm20 = imm[0]
        imm10_1 = imm[11:21]
        imm11 = imm[10]
        imm19_12 = imm[1:10]

        return f"{imm20}{imm19_12}{imm11}{imm10_1}{self.registers[rd]}{opcode}"
     
    def encode(self, instruction, lineno):
        self.current = (lineno + 1) * 4
        parts = instruction.split()
        instr = parts[0]
        operands = [op.strip() for op in " ".join(parts[1:]).split(",")]

        if instr == "sw":
            if len(operands) != 2 or "(" not in operands[1] or ")" not in operands[1]:
                print(f"Error: Invalid sw format in {instruction}")
                return None
            try:
                offset, base = operands[1].split("(")
                base = base.strip(")")
                print(instr, operands[0], base, offset)
                return self.encode_s_type(instr, operands[0], base, operands[1])  # Passing 4 arguments correctly
            except ValueError:
                print(f"Error: Invalid sw operand format at line {lineno}")
                return None
        if instr in ["addi", "lw", "jalr"]: 
            if len(operands) < 3 and instr != "lw":
                print(f"Error: Missing operands for {instr} at line {lineno}")
                return None

            if instr == "lw":
                if len(operands) != 2 or "(" not in operands[1] or ")" not in operands[1]:
                    print(f"Error: Invalid lw format in {instruction}")
                    return None
                try:
                    offset, base = operands[1].split("(")
                    base = base.strip(")")
                    return self.encode_i_type(instr, operands[0], base, offset)
                except ValueError:
                    print(f"Error: Invalid lw operand format at line {lineno}")
                    return None
            try:
                return self.encode_i_type(instr, operands[0], operands[1], operands[2])
            except ValueError as e:
                print(f"Error in {instr} operands at line {lineno}: {e}")
                return None

    def assembler(self,instructions):
        binary=[]
        asspire=[]
        for i,j in enumerate(instructions):
            a=self.encode(j,i)
            if a:
                asspire.append(a)
        for i,j in enumerate(instructions):
            bina=self.encode(j, i)
            if bina:
                binary.append(bina)
        return binary

riscv = riscV()
# instrctions=[
#     "lw a4,30(s3)",
#     "jalr ra,a4,-03",
#     "addi s4,s3,1",
#     "sw s4,23(s4)"
# ]
# binary_output = riscv.assembler(instrctions)
# for line in binary_output:
#      print(line)
