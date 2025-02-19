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
        self.funct7 = {"add": "0000000", "sub": "0100000", "slt": "0000000",
                        "srl": "0000000", "or": "0000000", "and": "0000000"}
        self.labels={}
        self.current=0
    def get_labels(self):
        return self.labels
    def update_labels(self, instructions):
        for address, line in enumerate(instructions):
            if ":" in line:
                label = line.split(":")[0].strip()
                self.labels[label] = (address+1) * 4
    def encode_r_type(self, instr, rd, rs1, rs2):
        opcode = format(self.opcodes[instr], '07b')
        funct3 = self.funct3[instr]
        funct7 = self.funct7[instr]
        return f"{funct7}{self.registers[rs2]}{self.registers[rs1]}{funct3}{self.registers[rd]}{opcode}"
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
    def encode_b_type(self, instr, rs1, rs2, label, pc):
        opcode = format(self.opcodes[instr], '07b')
        funct3 = self.funct3[instr]
        if label in self.labels:
            offset = self.labels[label] - pc
        elif label.lstrip('-').isdigit():
            offset = int(label)
        else:
            raise ValueError(f"Unknown label or invalid offset: {label}")
        if offset < 0:
            offset = (1 << 13) + offset      
        imm = format(offset, '013b') 
        imm12 = imm[0]      
        imm10_5 = imm[2:8]      
        imm4_1 = imm[8:12]    
        imm11 = imm[1]          
        return f"{imm12}{imm10_5}{self.registers[rs2]}{self.registers[rs1]}{funct3}{imm4_1}{imm11}{opcode}"
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
        if ":" in instruction:
            instruction=instruction.split(":")[1].strip()
        parts = instruction.split()
        instr = parts[0]
        operands = [op.strip() for op in " ".join(parts[1:]).split(",")]
        if instr in ["add", "sub", "slt", "srl", "or", "and"]:
            return self.encode_r_type(instr, operands[0], operands[1], operands[2])
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
        elif instr in ["beq", "bne"]:
            return self.encode_b_type(instr, operands[0], operands[1], operands[2], self.current)

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
# instructions = [
#     "addi t0,zero,1",
#     "addi s0,s0,1",
#     "beq s0,s1,label1",
#     "label4e:beq zero,zero,label4b",
#     "label1: bne s0,s1,8",
#     "addi t0,zero,3",
#     "addi s1,s1,1",
#     "bne s0,s1,label4e",
#     "addi s1,s1,1",
#     "addi t0,zero,4",
#     "label2: addi s0,s0,1",
#     "label4b: bne s0,s1,8",
#     "addi t0,zero,5",
#     "addi s1,s1,1",
#     "addi s1,s1,1",
#     "addi t0,zero,6",
#     "addi t0,zero,7",
#     "beq zero,zero,0"
# ]
# riscv.update_labels(instructions)
# binary_output = riscv.assembler(instructions)
# for line in binary_output:
#      print(line)
