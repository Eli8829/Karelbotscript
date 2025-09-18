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
    xpath_textarea_codigo = "/html/body/div/div[2]/div/div[2]/div/div/div[2]/div[1]/div/div[1]/textarea"
    xpath_btn_enviarproblema = "/html/body/div/div[1]/div/button[7]"
    xpath_btn_ejecutarproblema = "ejecutar"
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
                #print(f"Imagen no encontrada en el párrafo {i+1}. Revisando el siguiente.")
                continue

    def editar_codigo(self, codigo):
        try:
            self.driver.execute_script("""
                var editor = document.querySelector('.CodeMirror').CodeMirror;
                editor.setValue(arguments[0]);
            """, codigo)
            print("Codigo editado correctamente")
        except Exception as e:
            print("--------------MENSAJE DE ERROR---------------")
            print("editar_codigo()")
            print(e)
            print("OCURRIO UN ERROR")

    def obtener_codigo(self):
        try:
            codigo = self.driver.execute_script("""return document.getElementById("editor").value""")
            return codigo
        except Exception as e:
            print("--------------MENSAJE DE ERROR---------------")
            print("obtener_codigo()")
            print(e)
            print("OCURRIO UN ERROR")

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
        #self.descargar_imagen()
        #self.editar_codigo("asdfasdf")
        codigo = self.obtener_codigo()
        print(codigo)
        with open("Karel_Codigobase.txt", "w") as file:
            file.write(codigo)
        self.ejecutar_problema()
    
    def enviar_problema(self):
        htmlBtnEnviarProblema = self.driver.find_element(By.XPATH, self.xpath_btn_enviarproblema)
        htmlBtnEnviarProblema.click()

    def ejecutar_problema(self):
        htmlBtnEjecutarProblema = self.driver.find_element(By.ID, self.xpath_btn_ejecutarproblema)
        htmlBtnEjecutarProblema.click()
    
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
terminar_problemas_en = 17

main = karelmain(correo, contrasena)
for ejercicio in range (inicio_de_problema, terminar_problemas_en):
    try:
        
        print("Contestando ejercicio: " + str(ejercicio))
        main.numerodeproblema = ejercicio
        main.contestar_problemas()
        print("Ejercicio " + str(main.numerodeproblema) + ": " + str(main.urlproblema) + " Resuelto")
    except Exception as e:
        print("Ejercicio " + str(main.numerodeproblema) + ": " + str(main.urlproblema) + " no encontrado o no se puede acceder")
        print(e)

a = input("TERMINADO, PRESIONE ENTER PARA CONTINUAR")
main.terminar()
