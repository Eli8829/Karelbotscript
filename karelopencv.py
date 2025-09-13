import os
import cv2
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class karelopencv():
    # ATRIBUTOS
    numero_ejercicio = None
    nombre_de_imagen = ""
    img = None
    hsv = None
    mask_green = None
    mask_blue = None
    mask_gray = None
    contours_green = None
    contours_blue = None
    contours_gray = None
    contours_lightgray = None
    x_Karelref = None
    y_Karelref = None
    cell_size_x = None
    cell_size_y = None
    numeros_verdes = {}

    #Cargar imagen y convertir a hsv
    def cargarImagen(self, imgpath, numero_de_ejericio, nombre_de_imagen):
        img = cv2.imread(imgpath)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        self.img = img
        self.hsv = hsv
        self.numero_ejercicio = numero_de_ejericio
        self.nombre_de_imagen = nombre_de_imagen

    # --- Detectar verde (números) ---
    # Calcula mask y contours green (coordenadas en pixeles)
    def detectarVerde(self):
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        mask_green = cv2.inRange(self.hsv, lower_green, upper_green)
        contours_green, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.mask_green = mask_green
        self.contours_green = contours_green

    # --- Encontrar contornos verdes (números) ---
    # Pinta la imagen (cuadro rojo) con las coordenadas de contours_green
    def encontrarVerde(self):
        print("Coordenadas de números verdes (pixeles):")
        for cnt in self.contours_green:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 5 and h > 5:  # filtrar ruido
                cx, cy = x + w//2, y + h//2
                print(f"Número en (x={cx}, y={cy})")
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
        self.mask_blue = mask_blue
        self.contours_blue = contours_blue
    
    # --- Encontrar contornos azules (flecha) ---
    # Pinta la imagen (cuadro azul) con las coordenadas de contours_blue
    def encontrarAzul(self):
        print("Coordenadas de la flecha azul (pixeles):")
        for cnt in self.contours_blue:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 10 and h > 10:  # filtrar ruido
                cx, cy = x + w//2, y + h//2
                print(f"Flecha en (x={cx}, y={cy})")
                cv2.rectangle(self.img, (x, y), (x+w, y+h), (255,0,0), 1)

    # Coordenada de la flecha azul (Karel) como punto de referencia
    def obtenerposicionKarelxy(self):
        for cnt in self.contours_blue:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 10 and h > 10:
                x_ref, y_ref = x, y   # esquina superior izquierda de la flecha
                self.x_Karelref = x_ref
                self.y_Karelref = y_ref
                #PRUEBA
                print("xref: ", x_ref,"yref: ",y_ref)
                break

    # --- Detectar cuadrados grises ---
    # Calcula mask y contours gray (coordenadas en pixeles)
    def detectarGris(self):
        lower_gray = np.array([0, 0, 129])
        upper_gray = np.array([0, 0, 129])
        mask_gray = cv2.inRange(self.hsv, lower_gray, upper_gray)
        #INEXACTO: No encuentra la ubicacion exacta de los cuadros grises
        contours_gray, _ = cv2.findContours(mask_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.contours_gray = contours_gray 
        
        # Proceso para obtener el contorno gris exacto
        self.encontrarGris()
        hsv = cv2.cvtColor(self.hsv, cv2.COLOR_BGR2HSV)
        lower_purple = np.array([150,116,238]) # Es el color que va a buscar
        upper_purple = np.array([150,116,238]) # Porque cambia cuando se convierte a hsv
        mask_purple = cv2.inRange(hsv, lower_purple, upper_purple)
        contours_gray, _ = cv2.findContours(mask_purple, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.hsv = hsv
        self.mask_gray = mask_gray
        self.contours_gray = contours_gray 

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

        #print(xs)
        #print(ys)

        # Valores únicos en X y Y
        xs_unique = np.unique(xs)
        ys_unique = np.unique(ys)

        print(xs_unique)
        print(ys_unique)

        # Calcular diferencia entre cuadros consecutivos
        dx = np.diff(xs_unique)
        dy = np.diff(ys_unique)

        print(dx)
        print(dy)

        # Tomar la mediana como tamaño de celda
        cell_size_x = int(np.median(dx)) if len(dx) > 0 else 40
        cell_size_y = int(np.median(dy)) if len(dy) > 0 else 40
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        print(cell_size_x)
        print(cell_size_y)
    
    # Obtener lista final de coordenadas de los numeros verdes
    def obtenerNumerosVerdes(self):
        for cnt in self.contours_green:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 0 and h > 0:  # filtrar ruido
                roi = self.img[y:y+h, x:x+w]

                # Preprocesar ROI (Region of interest)
                gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                # OCR
                text = pytesseract.image_to_string(
                    thresh, 
                    config="--psm 10 -c tessedit_char_whitelist=0123456789"
                ).strip()

                if text.isdigit():
                    numero = int(text)

                    # Convertir a coordenadas de grilla
                    grid_x = round(abs(x - self.x_Karelref) / self.cell_size_x) + 1
                    grid_y = round(abs(y - self.y_Karelref) / self.cell_size_y) + 1

                    print(x)
                    print(abs(x - self.x_Karelref) / self.cell_size_x)
                    print(y)
                    print(abs(y - self.y_Karelref) / self.cell_size_y)
                    self.numeros_verdes[(grid_x, grid_y)] = numero
                else:
                    print("Numero no reconocido (?)")

    # --- Detectar gris claro (números de fondo gris) ---
    # Calcula mask y contours lightgray (coordenadas en pixeles)
    def detectarGrisclaro(self):
        lower_gray = np.array([0, 255, 190])
        upper_gray = np.array([0, 255, 190])
        mask_lightgray = cv2.inRange(self.img, lower_gray, upper_gray)
        contours_lightgray, _ = cv2.findContours(mask_lightgray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.mask_lightgray = mask_lightgray
        self.contours_lightgray = contours_lightgray
        print("||| mask_lightgray |||")
        print(mask_lightgray)
        print("||| contours_lightgray |||")
        print(contours_lightgray)
        
    
    def encontrarGrisclaro(self):
        for cnt in self.contours_lightgray:
            x, y, w, h = cv2.boundingRect(cnt)
            if w > 4 and h > 4:  # filtrar ruido
                cv2.rectangle(self.img, (x, y), (x+w, y+h), (238,130,238), 2)
        # print("NUMEROS GRISES")
        # print(self.contours_lightgray)

    #Mostrar lista de numeros verdes
    def mostrarNumerosVerdes(self):
        print("numeros_verdes = {")
        for k, v in sorted(self.numeros_verdes.items()):
            print(f"    {k}: {v},")
        print("}")
        # Mostrar Resultado
        cv2.imshow("Karel", self.img)
        cv2.imshow("Karelhsv", self.hsv)

    def guardarResultados(self):
        nuevo_directorio = "KarelAssets/" + self.numero_ejercicio
        if not os.path.exists(nuevo_directorio):
            os.makedirs(nuevo_directorio)
        with open(nuevo_directorio + "/" + self.numero_ejercicio + self.nombre_de_imagen + " numerosverdes.txt", 'a') as file:
            file.write(str(self.numeros_verdes))
        
        cv2.imwrite(nuevo_directorio + "/" + self.numero_ejercicio + self.nombre_de_imagen + " opencv hsv.png", self.hsv)
        cv2.imwrite(nuevo_directorio + "/" + self.numero_ejercicio + self.nombre_de_imagen + " opencv.png", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    # Algoritmo completo
    def iniciar(self):
        self.detectarVerde()
        self.encontrarVerde()
        self.detectarAzul()
        self.encontrarAzul()
        self.obtenerposicionKarelxy()
        self.detectarGris()
        self.encontrarGris()
        self.obtenerCellSize()
        self.obtenerNumerosVerdes()
        self.detectarGrisclaro()
        self.encontrarGrisclaro()
        self.mostrarNumerosVerdes() # Opcional
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
