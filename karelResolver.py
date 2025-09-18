from collections import deque
import ast
# Funciones de movimiento de Karel

class KarelResolver():

    Karel = {"x": 1, "y": 1, "dir": "ESTE"}  # empieza mirando a la derecha (este)
    Karel_destino = {"x": 1, "y": 1, "dir": "ESTE"}
    Codigo = []
    numerodeproblema = 357
    numeros_verdes_inicio =  {}
    numeros_verdes_destino = {}
    caminos_bloqueados = {
    # (4,4): {"OESTE", "SUR", "ESTE"},
    # (3,3): {"ESTE"},
    # (3,4): {"ESTE"},
    # (5,3): {"OESTE"},
    # (5,4): {"OESTE"},
    # (4,3): {"OESTE", "NORTE", "ESTE"}
    }
    dirs = {
        "NORTE": (0, 1),
        "SUR": (0, -1),
        "ESTE": (1, 0),
        "OESTE": (-1, 0)
    }

    def avanzar(self):
        if self.Karel["dir"] == "ESTE":
            self.Karel["x"] += 1
        elif self.Karel["dir"] == "OESTE":
            self.Karel["x"] -= 1
        elif self.Karel["dir"] == "NORTE":
            self.Karel["y"] += 1
        elif self.Karel["dir"] == "SUR":
            self.Karel["y"] -= 1
        print("Avanzar a", self.Karel)
        self.Codigo.append("move();")

    def recoger(self):
        print("Recoger número en", (self.Karel["x"], self.Karel["y"]))
        self.Codigo.append("pickbeeper();")

    def soltar(self):
        print("Soltar número en", (self.Karel["x"], self.Karel["y"]))
        self.Codigo.append("putbeeper();")

    def girar_izquierda(self):
        dirs = ["NORTE", "OESTE", "SUR", "ESTE"]
        idx = dirs.index(self.Karel["dir"])
        self.Karel["dir"] = dirs[(idx+1)%4]
        print("Girar izquierda →", self.Karel["dir"])
        self.Codigo.append("turnleft();")
    
    # Karel NO PUEDE GIRAR A LA DERECHA (Ignorar)
    def girar_derecha(self):
        dirs = ["NORTE", "ESTE", "SUR", "OESTE"]
        idx = dirs.index(self.Karel["dir"])
        self.Karel["dir"] = dirs[(idx+1)%4]
        print("Girar derecha →", self.Karel["dir"])

    # Orientacion de self.Karel
    def orientar(self, d):
        while self.Karel["dir"] != d:
            self.girar_izquierda()

    # # Algoritmo para ir a una coordenada (OBSOLETO, Ignorar)
    def ir_a(self, x_dest, y_dest):
        # Mover en X
        while self.Karel["x"] != x_dest:
            if self.Karel["x"] < x_dest:
                self.orientar("ESTE")
            else:
                self.orientar("OESTE")
            self.avanzar()

        # Mover en Y
        while self.Karel["y"] != y_dest:
            if self.Karel["y"] < y_dest:
                self.orientar("NORTE")
            else:
                self.orientar("SUR")
            self.avanzar()

    # ALGORITMO DE PATHFINDING BFS (Breadth-First Search)
    # Busqueda en Amplitud
    def bfs(self, inicio, destino):
        cola = deque([(inicio, [])])
        visitados = set()

        while cola:
            (x, y), camino = cola.popleft()
            if (x, y) == destino:
                return camino  # ruta encontrada

            if (x, y) in visitados:
                continue
            visitados.add((x, y))

            for d, (dx, dy) in self.dirs.items():
                if self.puede_avanzar(x, y, d):
                    nx, ny = x + dx, y + dy
                    cola.append(((nx, ny), camino + [d]))
        return None

    # Implementacion para el algoritmo de pathfinding BFS
    def recorrer_ruta(self, ruta):
        for direccion in ruta:
            self.orientar(direccion)
            self.avanzar()

    # Verifica si hay pared al avanzar
    def puede_avanzar(self, x, y, dir):
        # Verificar bloqueo desde la celda actual
        if (x, y) in self.caminos_bloqueados and dir in self.caminos_bloqueados[(x, y)]:
            return False

        # Calcular destino
        if dir == "NORTE": destino = (x, y+1); opuesto = "SUR"
        elif dir == "SUR": destino = (x, y-1); opuesto = "NORTE"
        elif dir == "ESTE": destino = (x+1, y); opuesto = "OESTE"
        elif dir == "OESTE": destino = (x-1, y); opuesto = "ESTE"

        # Verificar bloqueo desde la celda destino hacia atrás
        if (destino in self.caminos_bloqueados and 
            opuesto in self.caminos_bloqueados[destino]):
            return False

        return True
    
    def recoger_beepers(self):
        # Va a recorrer la lista numeros verdes en cuanto a las coordenadas de
        # los beepers (origen) y la cantidad que hay (cantidad)
        print("RECOGIENDO BEEPERS")
        for coordenada_beeper, cantidad in self.numeros_verdes_inicio.items():
            for i in range(cantidad):  # repetir según el número verde
                #ir_a(origen[0], origen[1])
                #print(origen[0], origen[1])
                origen = self.Karel["x"], self.Karel["y"]
                print("Llendo a: " + str(coordenada_beeper))
                ruta = self.bfs(origen, coordenada_beeper)
                self.recorrer_ruta(ruta)
                self.recoger()

    def dejar_beepers_ensulugar(self):
        print("DEJANDO BEEPERS EN SU LUGAR")
        for coordenada_beeper, cantidad in self.numeros_verdes_destino.items():
            for i in range(cantidad):
                #ir_a(destino[0], destino[1])
                origen = self.Karel["x"], self.Karel["y"]
                print("Llendo a: " + str(coordenada_beeper))
                ruta = self.bfs(origen, coordenada_beeper)
                self.recorrer_ruta(ruta)
                self.soltar()

    def ir_a_destinofinal(self):
        print("TAREA TERMINADA, LLEGANDO AL DESTINO FINAL")
        origen = self.Karel["x"], self.Karel["y"]
        destino = self.Karel_destino["x"], self.Karel_destino["y"]
        ruta = self.bfs(origen, destino)
        self.recorrer_ruta(ruta)
        self.orientar(self.Karel_destino["dir"])
        # ir_a(self.Karel_destino["x"], self.Karel_destino["y"])
        # orientar(self.Karel_destino["dir"])
        print(self.Karel)

    def guardar_codigo(self):
        Karel_CodigoBase = []
        codeSolved = []
        with open("Karel_Codigobase.txt", "r") as file:
            numero_de_linea = 0
            for line in file:
                numero_de_linea += 1
                #print(f"{numero_de_linea}: {line}")
                Karel_CodigoBase.append(line)

        for i in range(3):
            codeSolved.append(Karel_CodigoBase[i])

        for sentencia in self.Codigo:
            codeSolved.append("        " + sentencia)

        codeSolved.append("")
        for i in range(3,6):
            codeSolved.append(Karel_CodigoBase[i])

        print("codeSolved: -----------------")
        for sentencia in codeSolved:
            print(sentencia)
        
        with open("KarelAssets/" + str(self.numerodeproblema) + "/" + str(self.numerodeproblema) + "code.txt", "w") as file:
            for sentencia in codeSolved:
                file.write(sentencia + "\n")
        
    # Algoritmo completo
    def iniciar(self):
        self.recoger_beepers()
        self.dejar_beepers_ensulugar()
        self.ir_a_destinofinal()
        self.guardar_codigo()

    # METODO CONSTRUCTOR
    def __init__(self, numerodeproblema):
        self.numerodeproblema = numerodeproblema
        with open("KarelAssets/" + str(self.numerodeproblema) + "/" + str(self.numerodeproblema) +  "input beepers.txt", "r") as file:
            self.numeros_verdes_inicio = ast.literal_eval(file.read())

        with open("KarelAssets/" + str(self.numerodeproblema) + "/" + str(self.numerodeproblema) +  "output beepers.txt", "r") as file:
            self.numeros_verdes_destino = ast.literal_eval(file.read())

        #print(type(self.numeros_verdes_inicio))
        print(self.numeros_verdes_inicio)
        #print(type(self.numeros_verdes_destino))
        print(self.numeros_verdes_destino)

numerodeproblema = 12
karelgps = KarelResolver(numerodeproblema)
karelgps.iniciar()
