from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import requests
import threading
from queue import Queue
from itertools import cycle
import time

class rLogin:
    """Handles login functionality using Selenium WebDriver."""

    def __init__(self, driver: WebDriver):
        """
        Initialize with a Selenium WebDriver instance.
        
        Args:
            driver (WebDriver): Active Selenium WebDriver (Chrome/Firefox/etc.)
        """
        self.driver = driver

    def login(self, username: str, password: str) -> None:
        """
        Logs in using the provided credentials.
        
        Args:
            username (str): Username to input.
            password (str): Password to input.
        """
        
        self.driver.get("https://ruarua.ru/login/")
        
        # Find elements
        login_box = self.driver.find_element(By.ID, "nam")
        psw_box = self.driver.find_element(By.ID, "pass")

        # Input credentials
        login_box.send_keys(username)
        psw_box.send_keys(password)
        
        login_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary[onclick*='initcaptcha']")))
        login_button.click()
        
        while True:
            time.sleep(2)
            try: slider_btn = self.driver.find_element(By.CSS_SELECTOR, "div.control-btn.slideDragBtn")
            except:
                print("Login success!")
                break

            # Drag the slider horizontally
            actions = ActionChains(self.driver)
            actions.click_and_hold(slider_btn).move_by_offset(70, 0).release().perform()

            # Optional: Verify success (e.g., check for post-slider elements)
            # print("Slider dragged successfully!")
            
class rRua:
    """Handles Ruarua functionality using Selenium WebDriver."""

    def __init__(self, driver: WebDriver):
        """
        Initialize with a Selenium WebDriver instance.
        
        Args:
            driver (WebDriver): Active Selenium WebDriver (Chrome/Firefox/etc.)
        """
        self.driver = driver

    def rua(self, ruaid: str | list [str], capacity = 5) -> None:
        """
        Ruas players using provided ruaid.
        
        Args:
            ruaid (str): Username to input.
        """
        if type(ruaid) is str: ruaid = [ruaid]
        if len(ruaid) > capacity: ruaid = ruaid[0:capacity]
        for id in ruaid:
            self.driver.get(f"https://ruarua.ru/user/?rua={id}")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof doit === "function");'))
            self.driver.execute_script("doit();")
            time.sleep(0.5)
        self.driver.get("https://ruarua.ru/")
        print("Ruarua finished!")
        
class rSign:
    """Handles Sign-in functionality using Selenium WebDriver."""

    def __init__(self, driver: WebDriver):
        """
        Initialize with a Selenium WebDriver instance.
        
        Args:
            driver (WebDriver): Active Selenium WebDriver (Chrome/Firefox/etc.)
        """
        self.driver = driver

    def dailycard(self) -> None:
        """
        Get the dailycard for the player.
        """
        self.driver.get("https://ruarua.ru/dailycard/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof dailycard === "function");'))
        self.driver.execute_script("dailycard();")
        print("Dailycard done!")
    def sign(self) -> None:
        """
        Sign in for the player.
        """
        try:
            self.driver.get("https://ruarua.ru/sign/")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof doit === "function");'))
            self.driver.execute_script("doit();")
        except Exception as e: print(f"Error: {e}")
        print("Signing done!")
    def tree(self) -> None:
        """
        Sign in for the player.
        """
        self.driver.get("https://ruarua.ru/power/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof doit === "function");'))
        self.driver.execute_script("doit();")
        print("Tree energy collected!")
        
class rRedeemCode:
    """Handles Code Redemption functionality using Selenium WebDriver."""

    def __init__(self, driver: WebDriver):
        """
        Initialize with a Selenium WebDriver instance.
        
        Args:
            driver (WebDriver): Active Selenium WebDriver (Chrome/Firefox/etc.)
        """
        self.driver = driver

    def RedeemCode(self, ListOfCode: str | list [str]) -> None:
        """
        Redeem Code using provided ruaid.
        
        Args:
            ListOfCode (str): Username to input.
        """
        self.driver.get("https://ruarua.ru/code/")
        
        if type(ListOfCode) is str: ListOfCode = [ListOfCode]
        
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof initcaptcha === "function");'))
        
        for code in ListOfCode:
            code_box = self.driver.find_element(By.ID, "codee")
            code_box.send_keys(code)
            self.driver.execute_script("initcaptcha();")
            while True:
                time.sleep(2)
                try: slider_btn = self.driver.find_element(By.CSS_SELECTOR, "div.control-btn.slideDragBtn")
                except:
                    print("Redeem success!")
                    break

                # Drag the slider horizontally
                actions = ActionChains(self.driver)
                actions.click_and_hold(slider_btn).move_by_offset(70, 0).release().perform()

                # Optional: Verify success (e.g., check for post-slider elements)
                # print("Slider dragged successfully!")
    
    
    
class ProxyRotator:
    def __init__(self, proxy_list, max_threads=5):
        self.proxy_list = proxy_list
        self.max_threads = max_threads
        self.timeout = 5
        self.result_queue = Queue()
        self.lock = threading.Lock()
        
    def _is_proxy_working(self, proxy):
        """Check if proxy is reachable."""
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        try:
            test_url = "http://httpbin.org/ip"
            response = requests.get(test_url, proxies=proxies, timeout=self.timeout)
            return response.status_code == 200
        except:
            return False
    
    def _test_proxy_in_browser(self, proxy):
        """Test proxy in actual browser and return driver if successful."""
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument(f"--proxy-server={proxy}")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.get("http://httpbin.org/ip")
            time.sleep(1)
            if proxy.split(":")[0] in driver.page_source:
                with self.lock:
                    if self.result_queue.empty():  # Only keep first successful driver
                        print(f"Found working proxy: {proxy}")
                        self.result_queue.put(driver)
                        return
            driver.quit()
        except Exception as e:
            print(f"Proxy {proxy} failed in browser: {str(e)}")
    
    def get_proxied_driver(self):
        """Returns a Chrome driver with the next working proxy using multithreading."""
        threads = []
        
        # Create and start threads for each proxy
        for proxy in self.proxy_list:
            print(1)
            if not self.result_queue.empty():
                break  # Stop if we already found a working proxy
                
            if not self._is_proxy_working(proxy):
                continue  # Skip proxies that fail basic connectivity check
                
            t = threading.Thread(
                target=self._test_proxy_in_browser,
                args=(proxy,)
            )
            threads.append(t)
            t.start()
            
            # Limit number of concurrent threads
            while len(threads) >= self.max_threads:
                for t in threads[:]:
                    if not t.is_alive():
                        threads.remove(t)
                time.sleep(0.1)
        
        # Wait for remaining threads to complete
        for t in threads:
            t.join()
        
        if not self.result_queue.empty():
            return self.result_queue.get()
        
        raise Exception("No working proxies available")