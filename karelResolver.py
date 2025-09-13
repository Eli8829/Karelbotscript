# Funciones de movimiento de Karel

def avanzar():
    if Karel["dir"] == "ESTE":
        Karel["x"] += 1
    elif Karel["dir"] == "OESTE":
        Karel["x"] -= 1
    elif Karel["dir"] == "NORTE":
        Karel["y"] += 1
    elif Karel["dir"] == "SUR":
        Karel["y"] -= 1
    print("Avanzar a", Karel)
    Codigo.append("move();")


def girar_izquierda():
    dirs = ["NORTE", "OESTE", "SUR", "ESTE"]
    idx = dirs.index(Karel["dir"])
    Karel["dir"] = dirs[(idx+1)%4]
    print("Girar izquierda →", Karel["dir"])
    Codigo.append("turnleft();")
    
# KAREL NO PUEDE GIRAR A LA DERECHA (Ignorar codigo)
def girar_derecha():
    dirs = ["NORTE", "ESTE", "SUR", "OESTE"]
    idx = dirs.index(Karel["dir"])
    Karel["dir"] = dirs[(idx+1)%4]
    print("Girar derecha →", Karel["dir"])

def recoger():
    print("Recoger número en", (Karel["x"], Karel["y"]))
    Codigo.append("pickbeeper();")

def soltar():
    print("Soltar número en", (Karel["x"], Karel["y"]))
    Codigo.append("putbeeper();")

# Algoritmo para ir a una coordenada

def ir_a(x_dest, y_dest):
    # Mover en X
    while Karel["x"] != x_dest:
        if Karel["x"] < x_dest:
            orientar("ESTE")
        else:
            orientar("OESTE")
        avanzar()

    # Mover en Y
    while Karel["y"] != y_dest:
        if Karel["y"] < y_dest:
            orientar("NORTE")
        else:
            orientar("SUR")
        avanzar()

# Nueva implementacion para el algoritmo de pathfinding bfs

def seguir_ruta(ruta):
    for direccion in ruta:
        orientar(direccion)
        avanzar()


# Orientacion de Karel

def orientar(d):
    while Karel["dir"] != d:
        girar_izquierda()

def puede_avanzar(x, y, dir):
    # Verificar bloqueo desde la celda actual
    if (x, y) in caminos_bloqueados and dir in caminos_bloqueados[(x, y)]:
        return False

    # Calcular destino
    if dir == "NORTE": destino = (x, y+1); opuesto = "SUR"
    elif dir == "SUR": destino = (x, y-1); opuesto = "NORTE"
    elif dir == "ESTE": destino = (x+1, y); opuesto = "OESTE"
    elif dir == "OESTE": destino = (x-1, y); opuesto = "ESTE"

    # Verificar bloqueo desde la celda destino hacia atrás
    if (destino in caminos_bloqueados and 
        opuesto in caminos_bloqueados[destino]):
        return False

    return True

from collections import deque

dirs = {
    "NORTE": (0, 1),
    "SUR": (0, -1),
    "ESTE": (1, 0),
    "OESTE": (-1, 0)
}

# ALGORITMO DE PATHFINDING BFS (Breadth-First Search)
# Busqueda en Amplitud
def bfs(inicio, destino):
    cola = deque([(inicio, [])])
    visitados = set()

    while cola:
        (x, y), camino = cola.popleft()
        if (x, y) == destino:
            return camino  # ruta encontrada

        if (x, y) in visitados:
            continue
        visitados.add((x, y))

        for d, (dx, dy) in dirs.items():
            if puede_avanzar(x, y, d):
                nx, ny = x + dx, y + dy
                cola.append(((nx, ny), camino + [d]))
    return None


# MAIN

# Estado inicial
Karel = {"x": 1, "y": 1, "dir": "ESTE"}  # empieza mirando a la derecha (este)
Codigo = []

numeros_verdes = {
    
}

numeros_verdes_destino = {
    (3, 2): 1,
    (4, 2): 1,
    (6, 1): 2,
    (8, 1): 2,
    (9, 2): 1,
    (11, 1): 2,
    (12, 2): 1
}

caminos_bloqueados = {
    (4,4): {"OESTE", "SUR", "ESTE"},
    (3,3): {"ESTE"},
    (3,4): {"ESTE"},
    (5,3): {"OESTE"},
    (5,4): {"OESTE"},
    (4,3): {"OESTE", "NORTE", "ESTE"}
}

Karel_destino = {"x": 1, "y": 1, "dir": "ESTE"}

# Va a recorrer la lista numeros verdes en cuanto a las coordenadas de
# los beepers (origen) y la cantidad que hay (cantidad)
print("RECOGIENDO BEEPERS")
for origen, cantidad in numeros_verdes.items():
    for i in range(cantidad):  # repetir según el número verde
        #ir_a(origen[0], origen[1])
        ruta = bfs(origen[0], origen[1])
        seguir_ruta(ruta)
        recoger()

print("DEJANDO BEEPERS EN SU LUGAR")
for destino, cantidad in numeros_verdes_destino.items():
    for i in range(cantidad):
        #ir_a(destino[0], destino[1])
        ruta = bfs(destino[0], destino[1])
        seguir_ruta(ruta)
        soltar()

print("TAREA TERMINADA, LLEGANDO AL DESTINO FINAL")

ruta = bfs(Karel_destino["x"], Karel_destino["y"])
seguir_ruta(ruta)
# ir_a(Karel_destino["x"], Karel_destino["y"])
# orientar(Karel_destino["dir"])
print(Karel)

file = open("KarelAssets/357/357code.txt", "w")

for sentencia in Codigo:
    file.write(sentencia + "\n")
print("CODIGO ESCRITO")

file.close
