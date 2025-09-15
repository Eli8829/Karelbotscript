from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import os
import requests
import time

#https://sites.google.com/chromium.org/driver/
#https://googlechromelabs.github.io/chrome-for-testing/

class karelmain():
    driver = None

    urlproblema = "https://plataforma.karelogic.net/resolver/"
    numerodeproblema = None
    xpath_img_base = "/html/body/div/div[2]/div/div[1]/div[1]/div[2]/p"
    
    def descargar_imagen(self):
        parrafos = self.driver.find_elements(By.XPATH, self.xpath_img_base)

        # Itera sobre cada párrafo
        for i, parrafo in enumerate(parrafos):
            try:
                # Intenta encontrar la imagen dentro del párrafo actual.
                # El punto '.' al inicio del XPath indica que la búsqueda se realice
                # desde el contexto del elemento `parrafo` actual, no desde la raíz de la página.
                imagen_elemento = parrafo.find_element(By.XPATH, './/span/span/img')

                # Si la encuentra, obtiene el URL y la descarga
                url_imagen = imagen_elemento.get_attribute('src')
                if url_imagen:
                    print(f"Imagen encontrada en el párrafo {i+1}. Descargando...")
                    respuesta = requests.get(url_imagen)
                    if respuesta.status_code == 200:
                        with open(f"imagen_parrafo_{i+1}.png", 'wb') as f:
                            f.write(respuesta.content)
                        print("Imagen descargada exitosamente.")
                        #break   Opcional: si solo necesitas la primera, sales del bucle
                    else:
                        print(f"No se pudo descargar la imagen en el párrafo {i+1}.")
                else:
                    print(f"El elemento en el párrafo {i+1} no tiene un atributo 'src' válido.")

            except Exception as e:
                # Si la imagen no se encuentra en el párrafo actual, continúa con el siguiente
                print(f"Imagen no encontrada en el párrafo {i+1}. Revisando el siguiente.")
                continue

    def crear_directorio(self, directorio):
        nuevo_directorio = "KarelAssets/" + self.numerodeproblema
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
inicio_de_problema = 12
terminar_problemas_en = 15

main = karelmain(correo, contrasena)
for ejercicio in range (inicio_de_problema, terminar_problemas_en):
    try:
        
        print(ejercicio)
        main.numerodeproblema = ejercicio
        main.contestar_problemas()
        print("Ejercicio " + str(karelmain.numerodeproblema) + ": " + str(karelmain.urlproblema) + " Resuelto")
    except Exception as e:
        print("Ejercicio " + str(karelmain.numerodeproblema) + ": " + str(karelmain.urlproblema) + " no encontrado o no se puede acceder")
        print(e)

a = input("TERMINADO, PRESIONE ENTER PARA CONTINUAR")
main.terminar()
