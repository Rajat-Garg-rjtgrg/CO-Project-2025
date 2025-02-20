class riscV:
    def __init__(self):
        self.opcodes={
            "add":0b0110011,"sub":0b0110011, "slt":0b0110011,
            "srl":0b0110011,"or":0b0110011,  "and":0b0110011,
            "lw":0b0000011, "addi":0b0010011,"jalr":0b1100111,
            "sw":0b0100011, "beq":0b1100011, "bne":0b1100011,
            "jal":0b1101111, "mul":0b0110011
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
            "jalr": "000", "sw": "010", "beq": "000", "bne": "001",
            "mul": "000"
        }
        self.funct7 = {
            "add": "0000000", "sub": "0100000", "slt": "0000000",
            "srl": "0000000", "or": "0000000", "and": "0000000",
            "mul": "0000001"
        }
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

        if instr in ["add", "sub", "slt", "srl", "or", "and", "mul"]:
            return self.encode_r_type(instr, operands[0], operands[1], operands[2])

        if instr == "sw":
            if len(operands) != 2 or "(" not in operands[1] or ")" not in operands[1]:
                print(f"Error: Invalid sw format in {instruction}")
                return None
            try:
                offset, base = operands[1].split("(")
                base = base.strip(")")
                return self.encode_s_type(instr, operands[0], base, operands[1])
            except ValueError:
                print(f"Error: Invalid sw operand format at line {lineno}")
                return None

        if instr in ["addi", "lw", "jalr"]:
            try:
                return self.encode_i_type(instr, operands[0], operands[1], operands[2])
            except ValueError as e:
                print(f"Error in {instr} operands at line {lineno}: {e}")
                return None

        elif instr in ["beq", "bne"]:
            return self.encode_b_type(instr, operands[0], operands[1], operands[2], self.current)
    
    def error_checker(rs: dict, file, labels: dict):

        isa = {
            "R": ["add","sub","stl","srl","or","and"],
            "I": ["lw","addi","jalr"],
            "S": ["sw"],
            "J": ["jal"],
            "B": ["beq", "bne","blt"],
            "bonus": ["mul", "halt", "rst", "rvrs"]
        }
    
        with open(file,"r") as f:
            l = 1
            for i in f:
    
                se = f"Syntax Error line {l}"
                wr = f"Syntax error: Wrong register name line {l}"
    
                i = i.strip()
                if not i:
                    l+=1
                    continue
                if ":" in i:
                    label,i = i.split(":")
                    i = i.strip()
    
                try:
                    ins, r = i.split()
                except:
                    if i == "halt" or i == "rst":
                        l+=1
                        continue
                    else:
                        return se
                r = r.split(",")
                itype = "x"
    
                for t,lst in isa.items():
                    if ins in lst:
                        itype = t
                        break
                
                
    
                if itype == "x":
                    return se
                elif itype == "R":
                    if len(r)!=3:
                        return se
                    for j in r:
                        if j not in rs:
                            return wr
                        
                elif itype == "I":
                    if ins == "lw":
                        if len(r) != 2:
                            return se
                        
                        if r[0] not in rs:
                            return wr
    
                        if "(" not in r[1] or ")" not in r[1] or r[1].index("(")>r[1].index(")") or r[1][0] == "(" or r[1][-1] != ")":
                            return se
                        
                        if not r[1][:r[1].index["("]].lstrip("-").isdigit() and r[1][:r[1].index["("]] not in labels:
                            return se
                        
                        if r[1][r[1].index["("]+1:-1] not in rs:
                            return wr
                        
                    else:
                        if len(r)!=3:
                            return se
                        for j in r[:-1]:
                            if j not in rs:
                                return wr
                            
                        if not r[-1].lstrip("-").isdigit() and r[-1] not in labels:
                            return se
                            
                elif itype == "S":
                    if len(r) != 2:
                        return se
                    
                    if r[0] not in rs:
                        return wr
    
                    if "(" not in r[1] or ")" not in r[1] or r[1].index("(")>r[1].index(")") or r[1][0] == "(" or r[1][-1] != ")":
                        return se
                    
                    if not r[1][:r[1].index["("]].lstrip("-").isdigit() and  r[1][:r[1].index["("]] not in labels:
                        return se
                    
                    if r[1][r[1].index["("]+1:-1] not in rs:
                        return wr
                    
                elif itype == "B":
                    if len(r)!=3:
                        return se
                    for j in r[:-1]:
                        if j not in rs:
                            return wr
                        
                    if not r[-1].lstrip("-").isdigit() and r[-1] not in labels:
                        return se
                        
                elif itype == "J":
                    if len(r)!=2:
                        return se
    
                    if r[0] not in rs:
                        return wr
                    
                    if not r[1].lstrip("-").isdigit() and r[1] not in labels:
                        return se
                        
                else:
                    if ins == "halt" or ins == "rst":
                        return se
                    elif ins == "mul":
                        if len(r)!=3:
                            return se
                        for j in r:
                            if j not in rs:
                                return wr
                            
                    elif ins == "rvrs":
                        if len(r)!=2:
                            return se
                        for j in r:
                            if j not in rs:
                                return wr
    
        return "pass"
