from selenium import webdriver
from selenium.webdriver.common.by import By
import threading
import time
from pynput import keyboard 

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

driver.get("https://orteil.dashnet.org/experiments/cookie/")
cookie = driver.find_element(By.ID, "cookie")

clicking = False

# Auto-click function
def auto_click():
    global clicking
    while True:
        if clicking:
            cookie.click()
        time.sleep(0.01)  

# Start auto-clicker thread
clicker_thread = threading.Thread(target=auto_click, daemon=True)
clicker_thread.start()

# Key listener function
def on_press(key):
    global clicking
    try:
        if key.char == "s": 
            clicking = True
            print("Auto-clicking started.")
        elif key.char == "p": 
            clicking = False
            print("Auto-clicking paused.")
        elif key.char == "q": 
            clicking = False
            print("Exiting script.")
            driver.quit()
            return False  
    except AttributeError:
        pass 

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()  
