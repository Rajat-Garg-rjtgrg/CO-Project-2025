def error_checker(rs: dict, file, labels: dict):

    isa = {
        "R": ["add","sub","stl","srl","or","and"],
        "I": ["lw","addi","jalr"],
        "S": ["sw"],
        "J": ["jal"],
        "B": ["beq", "bne","blt"],
        "bonus": ["mul", "halt", "rst", "rvrs"]
    }

    
    l = 1
    for i in file:

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
                
                if not r[1][:r[1].index("(")].lstrip("-").isdigit() and r[1][:r[1].index("(")] not in labels:
                    return se
                
                if r[1][r[1].index("(")+1:-1] not in rs:
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
            
            if not r[1][:r[1].index("(")].lstrip("-").isdigit() and  r[1][:r[1].index("(")] not in labels:
                return se
            
            if r[1][r[1].index("(")+1:-1] not in rs:
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