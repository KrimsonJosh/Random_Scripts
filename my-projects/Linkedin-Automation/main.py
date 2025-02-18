from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
from dotenv import load_dotenv 
import os 

'''
This method aborts an application(in linkedin)
if that application doesn't meet the requests 

Requests = must be ez apply
'''

def abort_application():

    close_button = driver.find_element(by=By.CLASS_NAME, value="artdeco-modal__dismiss")
    close_button.click()

    time.sleep(2)
    discard_button = driver.find_elements(by=By.CLASS_NAME, value="artdeco-modal__confirm-dialog-btn")[1]
    discard_button.click()

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

time.sleep(3)
all_listings = driver.find_elements(by=By.CSS_SELECTOR, value=".job-card-container--clickable")
# automate job applying with easy apply
for listing in all_listings:
    listing.click()
    try:
        easy_apply = driver.find_element(By.XPATH, value = '//*[@id="ember154"]')
        easy_apply.click()
        #enter in phone 
    
        phone_enter = driver.find_element(By.XPATH, value = '//*[@id="single-line-text-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-4157348114-9-phoneNumber-nationalNumber"]')
        phone_enter.send_keys('8179752705')

        #enter
        submit_resume = driver.find_element(By.CSS_SELECTOR, value = 'footer button')
        submit_resume.click()
        time.sleep(2)
        close_button = driver.find_element(by=By.CLASS_NAME, value="artdeco-modal__dismiss")
        close_button.click()

    except NoSuchElementException:
        abort_application()
        continue 
    



input = input("Waiting to close...")
driver.quit()