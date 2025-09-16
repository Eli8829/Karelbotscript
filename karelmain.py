from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import base64

#https://sites.google.com/chromium.org/driver/
#https://googlechromelabs.github.io/chrome-for-testing/

class karelmain():
    driver = None

    urlproblema = "https://plataforma.karelogic.net/resolver/"
    numerodeproblema = None
    xpath_img_base = "/html/body/div/div[2]/div/div[1]/div[1]/div[2]/p"
    nombredeproblema = ["input.png", "output.png"]
    
    def descargar_imagen(self):
        parrafos = self.driver.find_elements(By.XPATH, self.xpath_img_base)
        contador = 0
        self.crear_directorio()
        # Itera sobre cada párrafo
        for i, parrafo in enumerate(parrafos):
            try:
                # Intenta encontrar la imagen dentro del párrafo actual.
                # El punto '.' al inicio del XPath indica que la búsqueda se realice
                # desde el contexto del elemento `parrafo` actual, no desde la raíz de la página.
                imagen_elemento = parrafo.find_element(By.XPATH, './/span/span/img')

                # Si la encuentra, obtiene el URL y comienza el proceso de decodificacion base 64
                data_url = imagen_elemento.get_attribute('src')
                
                
                # Verifica si la URL de datos es válida y contiene Base64
                if data_url.startswith("data:image/png;base64,"):
                    print(f"Imagen encontrada en el párrafo {i+1}. Decodificando Base64...")
                    
                    # Elimina el prefijo "data:image/png;base64," para quedarte solo con la cadena Base64
                    cadena_base64 = data_url.replace("data:image/png;base64,", "")
                    
                    # Decodifica la cadena Base64 a bytes
                    imagen_bytes = base64.b64decode(cadena_base64)
                    
                    # Guarda los bytes decodificados en un archivo
                    with open("KarelAssets/" + str(self.numerodeproblema) + "/" + str(self.numerodeproblema) + self.nombredeproblema[contador], 'wb') as f:
                        f.write(imagen_bytes)
                    print("Imagen decodificada y guardada exitosamente como: " + str(self.numerodeproblema) + self.nombredeproblema[contador])
                    contador = contador + 1
                else:
                    print("La imagen no tiene un formato Base64 reconocido en su 'src'.")
            except Exception as e:
                # Si la imagen no se encuentra en el párrafo actual, continúa con el siguiente
                print(f"Imagen no encontrada en el párrafo {i+1}. Revisando el siguiente.")
                continue

    def crear_directorio(self):
        nuevo_directorio = "KarelAssets/" + str(self.numerodeproblema)
        if not os.path.exists(nuevo_directorio):
            os.makedirs(nuevo_directorio)

    def iniciar_sesion(self, correo, contrasena):
        self.driver.get("https://plataforma.karelogic.net/login")
        htmlEmail = self.driver.find_element(By.ID, "email")
        htmlEmail.send_keys(correo)
        htmlPass = self.driver.find_element(By.ID, "password")
        htmlPass.send_keys(contrasena + Keys.ENTER)

    def contestar_problemas(self):
        self.driver.get(self.urlproblema + str(self.numerodeproblema))
        # htmlBtnEnviarProblema = self.driver.find_element(By.XPATH, "/html/body/div/div[1]/div/button[7]")
        # htmlBtnEnviarProblema.click()
        self.descargar_imagen()
    
    def terminar(self):
        self.driver.quit()

    #Metodo constructor
    def __init__(self, correo, contrasena):
        service = Service(executable_path="C:/chromedriver.exe")
        driver = webdriver.Chrome(service = service)
        self.driver = driver
        self.iniciar_sesion(correo, contrasena)

correo = "l22480942@nuevoleon.tecnm.mx"
contrasena = 'GjzcSX*Z"t3K^S6'
inicio_de_problema = 16
terminar_problemas_en = 20

main = karelmain(correo, contrasena)
for ejercicio in range (inicio_de_problema, terminar_problemas_en):
    try:
        
        print(ejercicio)
        main.numerodeproblema = ejercicio
        main.contestar_problemas()
        print("Ejercicio " + str(main.numerodeproblema) + ": " + str(main.urlproblema) + " Resuelto")
    except Exception as e:
        print("Ejercicio " + str(main.numerodeproblema) + ": " + str(main.urlproblema) + " no encontrado o no se puede acceder")
        print(e)

a = input("TERMINADO, PRESIONE ENTER PARA CONTINUAR")
main.terminar()
