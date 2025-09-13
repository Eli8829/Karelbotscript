from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

#https://sites.google.com/chromium.org/driver/
#https://googlechromelabs.github.io/chrome-for-testing/

service = Service(executable_path="C:/chromedriver.exe")
driver = webdriver.Chrome(service = service)

correo = "l22480942@nuevoleon.tecnm.mx"
contrasena = 'GjzcSX*Z"t3K^S6'
urlproblema = "https://plataforma.karelogic.net/resolver/"
numerodeproblema = 11

driver.get("https://plataforma.karelogic.net/login")

htmlEmail = driver.find_element(By.ID, "email")
htmlEmail.send_keys(correo)
htmlPass = driver.find_element(By.ID, "password")
htmlPass.send_keys(contrasena + Keys.ENTER)

driver.get(urlproblema + str(numerodeproblema))
htmlBtnEnviarProblema = driver.find_element(By.XPATH, "/html/body/div/div[1]/div/button[7]")
htmlBtnEnviarProblema.click()
for n in range (50):
    try:
        ejercicio = str(numerodeproblema + n)
        karelurl = urlproblema + ejercicio
        driver.get(karelurl)
        htmlBtnEnviarProblema = driver.find_element(By.XPATH, "/html/body/div/div[1]/div/button[7]")
        htmlBtnEnviarProblema.click()
        print("Ejercicio " + ejercicio + ": " + karelurl + " Resuelto")
    except Exception as e:
        print("Ejercicio " + ejercicio + ": " + karelurl + " no encontrado o no se puede acceder")

a = input("TERMINADDO")

driver.quit()