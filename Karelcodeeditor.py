Karel_CodigoBase = []
with open("Karel_Codigobase.txt", "r") as file:
    numero_de_linea = 0
    for line in file:
        numero_de_linea += 1
        print(f"{numero_de_linea}: {line}")
        Karel_CodigoBase.append(line)
code = []
with open("KarelAssets/357/357code.txt", "r") as file:
    for line in file:
        print(line)
        code.append(line)

codeSolved = []
for i in range(3):
    codeSolved.append(Karel_CodigoBase[i])

for sentencia in code357:
    codeSolved.append("        " + sentencia)

for i in range(3,6):
    codeSolved.append(Karel_CodigoBase[i])

print("codeSolved: -----------------")
for sentencia in codeSolved:
    print(sentencia)
