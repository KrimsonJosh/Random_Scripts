from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
import time
from dotenv import load_dotenv 
import os 

load_dotenv()
myemail = os.getenv('my_username')
pwd = os.getenv('password')
url = "https://www.linkedin.com/jobs/search/?currentJobId=4157348114&f_LF=f_AL&geoId=102257491&keywords=python%20developer&location=London%2C%20England%2C%20United%20Kingdom"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

driver.get(url)


time.sleep(2)
signin = driver.find_element(By.XPATH, value = '//*[@id="base-contextual-sign-in-modal"]/div/section/div/div/div/div[2]/button')
signin.click()

time.sleep(1)

email = driver.find_element(By.XPATH, value = '//*[@id="base-sign-in-modal_session_key"]')
password = driver.find_element(By.XPATH, value = '//*[@id="base-sign-in-modal_session_password"]')
enter = driver.find_element(By.XPATH, value = '//*[@id="base-sign-in-modal"]/div/section/div/div/form/div[2]/button')

email.send_keys(myemail)
password.send_keys(pwd)
enter.click()




input = input("Waiting to close...")
driver.quit()