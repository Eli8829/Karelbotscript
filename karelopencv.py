import os
import cv2
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class karelopencv():
    # ATRIBUTOS
    numero_ejercicio = None
    nombre_de_imagen = ""
    preimagen = None
    img = None
    img_numeros = None
    hsv = None   
    contours_green = None
    contours_blue = None
    contours_gray = None
    contours_lightgray = None
    x_Karel_pixeles = None
    y_Karel_pixeles = None
    x_Karel = None
    y_Karel = None
    x_cells_unique = None
    y_cells_unique = None
    cell_size_x = None
    cell_size_y = None
    numeros_verdes = {}
    numeros_grises = {}

    # Pagina recomendada para convertir rgb a hsv (rango de 0 a 255)
    # https://www.peko-step.com/es/tool/hsvrgb.html
    # Ojo se utiliza hsv para detectar colores y rgb para pintar los contornos

    #Cargar imagen y convertir a hsv
    def cargarImagen(self, imgpath, numero_de_ejericio, nombre_de_imagen):
        preimagen = cv2.imread(imgpath)
        self.preimagen = preimagen
        self.numero_ejercicio = numero_de_ejericio
        self.nombre_de_imagen = nombre_de_imagen
        self.numeros_verdes = {}
        self.numeros_grises = {}
        self.beepers = {}

    def obtenertablero(self):
        gray = cv2.cvtColor(self.preimagen, cv2.COLOR_BGR2GRAY)
        # Umbral para detectar negro
        _, mask_black = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

        # Encontrar contornos
        contours, _ = cv2.findContours(mask_black, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Buscar el contorno más grande (que será el borde negro del tablero)
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)

        # Recortar la imagen al área del tablero
        board = self.preimagen[y:y+h, x:x+w]
        self.img = board
        hsv = cv2.cvtColor(board, cv2.COLOR_BGR2HSV)
        self.hsv = hsv
        #cv2.imshow("TABLERO", board)

    # --- Detectar verde (números) ---
    # Calcula mask y contours green (coordenadas en pixeles)
    def detectarVerde(self):
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        mask_green = cv2.inRange(self.hsv, lower_green, upper_green)
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.contours_green = contours_green

    # --- Encontrar contornos verdes (números) ---
    # Pinta la imagen (cuadro rojo) con las coordenadas de contours_green
    def encontrarVerde(self):
        print("Coordenadas de números verdes (pixeles) en imagen " + self.nombre_de_imagen + ": ")
        for cnt in self.contours_green:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 5 and h > 5:  # filtrar ruido
                cx, cy = x + w//2, y + h//2
                print(f"Número en (x={cx}, y={cy})")
                print("w: " + str(w) + " h: " + str(h))
                cv2.rectangle(self.img, (x, y), (x+w, y+h), (0,0,255), 1)
                #PRUEBA

    # --- Detectar azul (flecha) ---
    # Calcula mask y contours blue (coordenadas en pixeles)
    def detectarAzul(self):
        # Colores en BGR, Blue Green Red
        lower_blue = np.array([100, 80, 50])
        upper_blue = np.array([140, 255, 255])
        mask_blue = cv2.inRange(self.hsv, lower_blue, upper_blue)
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.contours_blue = contours_blue
    
    # --- Encontrar contornos azules (flecha) ---
    # Pinta la imagen (cuadro azul) con las coordenadas de contours_blue
    def encontrarAzul(self):
        print("Coordenadas de la flecha azul (pixeles):")
        for cnt in self.contours_blue:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 10 and h > 10:  # filtrar ruido
                cx, cy = x + w//2, y + h//2
                self.x_Karel_pixeles = cx
                self.y_Karel_pixeles = cy
                print(f"Flecha en (x={cx}, y={cy})")
                cv2.rectangle(self.img, (x, y), (x+w, y+h), (255,0,0), 1)

    # Coordenada de la flecha azul (Karel) 
    def obtenerposicionKarelxy(self):
        ref_x = self.x_cells_unique[0]
        ref_y = self.y_cells_unique[-1]
        
        print("ref_x")
        print(ref_x)
        print("ref_y")
        print(ref_y)

        self.x_Karel = 1
        self.y_Karel = 1
        while(ref_x < self.x_Karel_pixeles):
            self.x_Karel = self.x_Karel + 1
            ref_x = ref_x + self.cell_size_x
        while(ref_y > self.y_Karel_pixeles):
            self.y_Karel = self.y_Karel + 1
            ref_y = ref_y - self.cell_size_y

        print("Coordenadas de karel: x: " + str(self.x_Karel) + " y: " + str(self.y_Karel))

    # --- Detectar cuadrados grises ---
    # Calcula mask y contours gray (coordenadas en pixeles)
    def detectarGris(self):
        lower_gray = np.array([0, 0, 129])
        upper_gray = np.array([0, 0, 129])
        mask_gray = cv2.inRange(self.hsv, lower_gray, upper_gray)
        #INEXACTO: No encuentra la ubicacion exacta de los cuadros grises (solo en algunos problemas)
        contours_gray, _ = cv2.findContours(mask_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.contours_gray = contours_gray 
        # print("contours_gray 'INEXACTO'")
        # print(contours_gray)
        
        # Proceso para obtener el contorno gris exacto
        self.encontrarGris()
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        # Va a volver a buscar los contornos grises que ahora son contornos rosas
        # Pero en la imagen hsv cambian los colores, entonces
        # La busqueda de color cambia a otro color parecido al rosa 
        lower_purple = np.array([150,116,238]) # Es el color que va a buscar (BGR)
        upper_purple = np.array([150,116,238]) 
        mask_purple = cv2.inRange(hsv, lower_purple, upper_purple)
        contours_gray, _ = cv2.findContours(mask_purple, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.hsv = hsv
        self.contours_gray = contours_gray
        # print("contours_gray 'EXACTO'")

    # --- Encontrar contornos grises (cuadricula de karel) ---
    # Pinta la imagen (cuadro rosa) con las coordenadas de contours_gray
    def encontrarGris(self):
        for cnt in self.contours_gray:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 4 and h > 4:  # filtrar ruido
                cv2.rectangle(self.img, (x, y), (x+w, y+h), (238,130,238), 2)
        #print(contours_gray)

    # Obtener promedio de distancia entre cuadros grises en X y en Y
    def obtenerCellSize(self):
        xs = []
        ys = []
        for cnt in self.contours_gray:
            x, y, w, h = cv2.boundingRect(cnt)
            xs.append(x)
            ys.append(y)

        xs = sorted(xs)
        ys = sorted(ys)

        # print("xs")
        # print(xs)
        # print("ys")
        # print(ys)

        # Valores únicos en X y Y
        xs_unique = np.unique(xs)
        ys_unique = np.unique(ys)
        self.x_cells_unique = xs_unique
        self.y_cells_unique = ys_unique


        # print("xs_unique")
        # print(xs_unique)
        # print("ys_unique")
        # print(ys_unique)

        # Calcular diferencia entre cuadros consecutivos
        dx = np.diff(xs_unique)
        dy = np.diff(ys_unique)

        # print("dx")
        # print(dx)
        # print("dy")
        # print(dy)

        # Tomar la mediana como tamaño de celda
        cell_size_x = int(np.median(dx)) if len(dx) > 0 else 40
        cell_size_y = int(np.median(dy)) if len(dy) > 0 else 40
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        print("cell_size_x")
        print(cell_size_x)
        print("cell_size_y")
        print(cell_size_y)
    
    # Obtener lista final de coordenadas de los numeros verdes
    def obtenerNumerosVerdes(self):
        print("Reconocimiento de numeros verdes en imagen " + self.nombre_de_imagen)
        for cnt in self.contours_green:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 0 and h > 0:  # filtrar ruido
                roi = self.img[y:y+h, x:x+w]

                # Preprocesar ROI (Region of interest)
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                #cv2.imshow("NUMEROVERDE", gray)
                #cv2.waitKey(0)
                #cv2.destroyAllWindows()

                # OCR
                text = pytesseract.image_to_string(
                    thresh, 
                    config="--psm 10 -c tessedit_char_whitelist=0123456789"
                ).strip()

                if text.isdigit():
                    print("Numero reconocido: ", text)
                    numero = int(text)

                    ref_x = self.x_cells_unique[0]
                    ref_y = self.y_cells_unique[-1]

                    x_beeper = 1
                    y_beeper = 1
                    while(ref_x < x):
                        x_beeper = x_beeper + 1
                        ref_x = ref_x + self.cell_size_x
                    while(ref_y > y):
                        y_beeper = y_beeper + 1
                        ref_y = ref_y - self.cell_size_y
                    print("Beeper en: (" + str(x_beeper) + ", " + str(y_beeper) + ")")
                    self.numeros_verdes[(x_beeper, y_beeper)] = numero
                    #print(self.numeros_verdes[(grid_x, grid_y)])
                else:
                    print("Numero no reconocido (?)")

    # --- Detectar gris claro (números de fondo gris) ---
    # Calcula mask y contours lightgray (coordenadas en pixeles)
    def detectarGrisClaro(self):
        self.contours_lightgray = None
        lower_gray = np.array([0, 0, 224])
        upper_gray = np.array([0, 0, 224])
        mask_lightgray = cv2.inRange(self.hsv, lower_gray, upper_gray)
        contours_lightgray, _ = cv2.findContours(mask_lightgray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.mask_lightgray = mask_lightgray
        self.contours_lightgray = contours_lightgray
        # print("||| mask_lightgray |||")
        # print(mask_lightgray)
        print("||| contours_lightgray |||")
        print(self.contours_lightgray)

    # Pinta la imagen (cuadro rojo) con las coordenadas de contours_lightgray
    def encontrarGrisClaro(self):
        print("Coordenadas de números grises (pixeles):")
        for cnt in self.contours_lightgray:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 5 and h > 5:  # filtrar ruido
                cx, cy = x + w//2, y + h//2
                print(f"Número en (x={cx}, y={cy})")
                print("w: " + str(w) + " h: " + str(h))
                cv2.rectangle(self.img, (x, y), (x+w, y+h), (0,0,255), 1)
                #PRUEBA

    def obtenerNumerosGrises(self):
        print("Reconocimiento de numeros grises en imagen " + self.nombre_de_imagen)
        numeros_grises = cv2.imread("KarelAssets/" + self.numero_ejercicio + "/" + self.numero_ejercicio + self.nombre_de_imagen + " numerosgrises.png")
        #cv2.imwrite("prueba.png", numeros_grises_hsv)
        #cv2.imshow("NUMEROSGRISES", numeros_grises)
        for cnt in self.contours_lightgray:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 0 and h > 0:  # filtrar ruido
                roi = numeros_grises[y:y+h, x:x+w]

                # Preprocesar ROI (Region of interest)
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                # cv2.imshow("NUMEROGRIS", gray)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

                # OCR
                text = pytesseract.image_to_string(
                    thresh, 
                    config="--psm 10 -c tessedit_char_whitelist=0123456789"
                ).strip()

                if text.isdigit():
                    numero = int(text)
                    ref_x = self.x_cells_unique[0]
                    ref_y = self.y_cells_unique[-1]

                    x_beeper = 1
                    y_beeper = 1
                    while(ref_x < x):
                        x_beeper = x_beeper + 1
                        ref_x = ref_x + self.cell_size_x
                    while(ref_y > y):
                        y_beeper = y_beeper + 1
                        ref_y = ref_y - self.cell_size_y
                    print("Beeper en: (" + str(x_beeper) + ", " + str(y_beeper) + ")")
                    self.numeros_verdes[(x_beeper, y_beeper)] = numero
                else:
                    print("Numero no reconocido (?): " + text)
    
    #Mostrar lista de numeros grises
    def mostrarNumerosBeepers(self):
        print("numeros_verdes = {")
        for k, v in sorted(self.numeros_verdes.items()):
            print(f"    {k}: {v},")
        print("}")

        print("numeros_grises = {")
        for k, v in sorted(self.numeros_grises.items()):
            print(f"    {k}: {v},")
        print("}")

        # Mostrar Resultado
        #cv2.imshow("imgnumeros", self.img_numeros)
        cv2.imshow("Karel", self.img)
        #cv2.imshow("Karelhsv", self.hsv)

    def guardarResultados(self):
        #Junta los numeros para obtener todos los beepers
        beepers = self.numeros_grises | self.numeros_verdes
        print("beepers: ")
        print(beepers)

        nuevo_directorio = "KarelAssets/" + self.numero_ejercicio
        if not os.path.exists(nuevo_directorio):
            os.makedirs(nuevo_directorio)
        # with crea un nuevo archivo si el archivo no existe
        # es mas seguro porque cierra automaticamente el archivo
        with open(nuevo_directorio + "/" + self.numero_ejercicio + self.nombre_de_imagen + " beepers.txt", 'w') as file:
            file.write(str(beepers))
    
        cv2.imwrite(nuevo_directorio + "/" + self.numero_ejercicio + self.nombre_de_imagen + " opencv hsv.png", self.hsv)
        cv2.imwrite(nuevo_directorio + "/" + self.numero_ejercicio + self.nombre_de_imagen + " opencv.png", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    # Algoritmo completo
    def iniciar(self):
        self.obtenertablero()
        # Imagen para el procesado de numeros grises
        img_numeros = self.img
        cv2.imwrite("KarelAssets/"+ self.numero_ejercicio + "/" + self.numero_ejercicio + self.nombre_de_imagen + " numerosgrises.png", img_numeros)
        self.detectarVerde()
        self.encontrarVerde()
        self.detectarGrisClaro()
        self.encontrarGrisClaro()
        self.detectarAzul()
        self.encontrarAzul()
        self.detectarGris()
        self.encontrarGris()
        self.obtenerCellSize()
        self.obtenerposicionKarelxy()
        self.obtenerNumerosVerdes()
        self.obtenerNumerosGrises()
        self.mostrarNumerosBeepers() # Opcional
        self.guardarResultados()
        #return self.numeros_verdes()
    
    # Constructor
    def __init__(self, imgpath, numero_de_ejericio, nombre_de_imagen):
        self.cargarImagen(imgpath, numero_de_ejericio, nombre_de_imagen)

numero_ejercicio = "357"
nombre_de_imagen = "input"
nombre_de_imagen2 = "output"
imgpath = "KarelAssets/" + numero_ejercicio + "/" + numero_ejercicio + nombre_de_imagen + ".png"
imgpath2 = "KarelAssets/" + numero_ejercicio + "/" + numero_ejercicio + nombre_de_imagen2 + ".png"
karelopencv(imgpath, numero_ejercicio, nombre_de_imagen).iniciar()
karelopencv(imgpath2, numero_ejercicio, nombre_de_imagen2).iniciar()
