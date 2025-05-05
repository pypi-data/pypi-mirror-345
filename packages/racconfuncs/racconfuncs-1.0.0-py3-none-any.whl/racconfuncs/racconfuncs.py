from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, JavascriptException, InvalidElementStateException
from selenium import webdriver
from urllib.parse import urlparse, urlunparse
from datetime import datetime, timedelta, timezone
import os
import json
import requests
import threading
from queue import Queue
from itertools import cycle
from typing import Optional
import time
import math

class Raccon:
    """Handles Raccon functionalities using Selenium WebDriver."""
    
    def QuietDriver(self, quiet = True):
        chrome_options = webdriver.ChromeOptions()
        if quiet: chrome_options.add_argument("--headless=new")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        chrome_options.add_argument('--log-level=3')  # Only fatal errors
        chrome_options.add_argument('--disable-logging')  # Disables console logging
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-machine-learning-apis')  # Disables ML model execution
        chrome_options.add_argument('--disable-features=MachineLearningModelLoader,Tflite,XNNPACK')
        chrome_options.add_argument('--disable-machine-learning-model-loader')  # Prevents ML model loading
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    
    from urllib.parse import urlparse, urlunparse

    def urls_match(self, driver: webdriver, target_url):
        """
        Compare current URL with target URL.
        
        Args:
            driver: Selenium WebDriver instance
            target_url: The URL to compare against (str)
        
        Returns:
            bool: True if URLs match after normalization
        """
        def normalize_url(url: str):
            """Standardize URL for comparison"""
            return url.replace('e', '').replace('c', '').replace('/', '')

        current = normalize_url(driver.current_url)
        target = normalize_url(target_url)
        
        return current == target
    
    def execute_challenge(self):
        """Complete the hCaptcha cookie challenge"""
        try:
            # 1. Navigate to target URL
            # self.driver.get("https://accounts.hcaptcha.com/verify_email/68184514-b78d-597a-cabd-bc8841c594c3")
            self.driver.get("https://accounts.hcaptcha.com/verify_email/83225347-1ca7-439d-8157-ebdb83252a15")
            
            time.sleep(5)
            # 2. Wait for critical elements to load (with multiple fallbacks)
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script(
                    'return document.readyState === "complete" && '
                    'document.body.innerHTML.includes("Cookie")'
                )
            )

            # 3. Locate the Cookie button with multiple strategies
            cookie_button = None
            strategies = [
                (By.XPATH, "//button[contains(translate(., 'COOKIE', 'cookie'), 'cookie')]"),
                (By.XPATH, "//*[contains(text(), 'Cookie') and not(ancestor::*[contains(@style,'hidden')])]"),
                (By.CSS_SELECTOR, "button:contains('Cookie'), [onclick*='cookie']")
            ]

            for strategy in strategies:
                try:
                    cookie_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable(strategy))
                    break
                except TimeoutException:
                    continue

            if not cookie_button:
                raise NoSuchElementException("Cookie button not found with any strategy")

            # 4. Click using JavaScript to bypass potential overlays
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cookie_button)
            time.sleep(0.5)  # Visual settling time
            self.driver.execute_script("arguments[0].click();", cookie_button)
            print("Successfully clicked Cookie button")

            # 5. Wait for cookies to be set
            time.sleep(2)  # Allow cookie operations to complete

            # 6. Export hcaptcha.com cookies with advanced filtering
            all_cookies = self.driver.get_cookies()
            hcaptcha_cookies = {
                'metadata': {
                    'exported_at': datetime.utcnow().isoformat() + 'Z',  # ISO 8601 format with UTC
                    'source_url': self.driver.current_url,
                    'user_agent': self.driver.execute_script("return navigator.userAgent;")
                },
                'cookies': [
                    {k: v for k, v in cookie.items() 
                    if k in ['name', 'value', 'domain', 'path', 'expiry']}
                    for cookie in all_cookies 
                    if 'hcaptcha.com' in cookie.get('domain', '')
                ]
            }

            # 7. Save with timestamp
            with open('hcaptcha_cookies.json', 'w') as f:
                json.dump(hcaptcha_cookies, f, indent=2, ensure_ascii=False, default=str)

            print(f"Exported {len(hcaptcha_cookies['cookies'])} cookies at {hcaptcha_cookies['metadata']['exported_at']}")
            return True

        except Exception as e:
            print(f"Challenge failed: {str(e)}")
            # Take debugging screenshot
            self.driver.save_screenshot('error_screenshot.png')
            return False
        
    def load_or_refresh_cookies(self, cookie_file='hcaptcha_cookies.json', force_refresh=False):
        """
        Load cookies from JSON file or refresh if stale (>12 hours old)
        
        Args:
            driver: Selenium WebDriver instance
            cookie_file: Path to cookie JSON file
            force_refresh: If True, always refresh cookies regardless of timestamp
        
        Returns:
            bool: True if cookies were loaded successfully
        """
        def is_stale(timestamp_str, hours=12):
            """Check if timestamp is older than specified hours"""
            try:
                # Parse timestamp (handles both 'Z' and timezone offsets)
                record_time = datetime.fromisoformat(
                    timestamp_str.replace('Z', '+00:00')
                ).astimezone(timezone.utc)  # Convert to timezone-aware UTC
                
                # Compare with current time (also timezone-aware)
                return datetime.now(timezone.utc) - record_time > timedelta(hours=hours)
            except (ValueError, TypeError):
                return True  # If timestamp is invalid, treat as stale

        try:
            # Check if we should use cached cookies
            if not force_refresh and os.path.exists(cookie_file):
                with open(cookie_file, 'r') as f:
                    data = json.load(f)
                
                if not is_stale(data.get('metadata', {}).get('exported_at')):
                    # Load valid cookies
                    target_domain = "hcaptcha.com"
                    if not self.driver.current_url.endswith(target_domain):
                        self.driver.get(f"https://www.{target_domain}")
                        try:
                            all_cookies = self.driver.get_cookies()
                            deleted_count = 0
                            
                            for cookie in all_cookies:
                                if 'hcaptcha.com' in cookie.get('domain', ''):
                                    self.driver.delete_cookie(cookie['name'])
                                    deleted_count += 1
                                    
                            print(f"Deleted {deleted_count} hcaptcha.com cookies")
                        except Exception as e:
                            print(f"Error deleting hcaptcha cookies: {str(e)}")
                            return False
                    for cookie in data['cookies']:
                        # Selenium requires 'expiry' as int, not string
                        if 'expiry' in cookie:
                            cookie['expiry'] = int(cookie['expiry'])
                        self.driver.add_cookie(cookie)
                    print("Loaded cookies from cache")
                    return True

            # If we get here, we need fresh cookies
            print("Generating new cookies...")
            if not self.execute_challenge():  # Assuming this is your previous function
                raise RuntimeError("Failed to generate new cookies")
            
            # Verify new cookies exist
            if not os.path.exists(cookie_file):
                raise FileNotFoundError("New cookie file not created")
            
            # Recursively load the fresh cookies
            return self.load_or_refresh_cookies(cookie_file, force_refresh=False)
        
        except Exception as e:
            print(f"Cookie handling failed: {str(e)}")
            return False

    def __init__(self, driver: Optional[WebDriver] = None, quiet = True):
        """
        Initialize with a Selenium WebDriver instance.
        
        Args:
            driver (WebDriver): Active Selenium WebDriver (Chrome/Firefox/etc.)
        """
        if type(driver) is WebDriver: self.driver = driver
        else: self.driver = self.QuietDriver(quiet = quiet)

    def login(self, username: str, password: str) -> None:
        """
        Logs in using the provided credentials.
        
        Args:
            username (str): Username to input.
            password (str): Password to input.
        """
        
        if not self.urls_match(self.driver, "https://ruarua.ru/login/"):
            self.driver.get("https://ruarua.ru/login/")
        
        # Find elements
        login_box = self.driver.find_element(By.ID, "nam")
        psw_box = self.driver.find_element(By.ID, "pass")

        # Input credentials
        login_box.send_keys(username)
        psw_box.send_keys(password)
        
        login_button = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.btn-primary[onclick*='initcaptcha']")))
        login_button.click()
        
        print("Attempting to log in...")
        
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
        
    def logout(self) -> None:
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof logout === "function");'))
        self.driver.execute_script("logout();")
        
    def quit(self) -> None:
        self.driver.quit()

    def rua(self, ruaid: str | list [str], capacity = 5) -> None:
        """
        Ruas players using provided ruaid.
        
        Args:
            ruaid (str): Username to input.
            capacity (int): Max rua capacity for the account.
        """
        print("Ruaruaing...")
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
    def getRuaList(self, ruaid: str) -> list[str]:
        """
        Returns the list of players who ruaed the given player.
        
        Args:
            ruaid (str): Username to input.
        """
        if not self.urls_match(self.driver, f"https://ruarua.ru/user/?rua={ruaid}"):
            self.driver.get(f"https://ruarua.ru/user/?rua={ruaid}")
        try:
            # Locate the header div by exact text
            header_text = "↓ These people ruaruaed him/her today ↓"
            header = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//div[contains(., '{header_text}')]")))
            
            # Find the immediately following table
            table = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//div[contains(., '{header_text}')]/following-sibling::table[1]")))
            
            # Get all rows from tbody
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            hrefs = []
            for row in rows:
                try:
                    # Get first td's anchor href
                    first_td = row.find_element(By.XPATH, "./td[1]")
                    anchor = first_td.find_element(By.TAG_NAME, "a")
                    href = anchor.get_attribute("href")
                    if href:
                        hrefs.append(href)
                except NoSuchElementException:
                    continue  # Skip rows without anchors
            
            for i in range (len(hrefs)): hrefs[i] = hrefs[i].split('=')[1]
            return hrefs
        except TimeoutException:
            print("Timed out waiting for table elements to load")
            raise
        except NoSuchElementException as e:
            print(f"Required element not found: {str(e)}")
            raise
        
    def getFollowList(self) -> tuple:
        """
        Returns the following and follower list of the current player.
        
        Returns:
            folist (tuple (list[str], list[str])): Following and Follower list of the player.
        """
        if not self.urls_match(self.driver, "https://ruarua.ru/folist/"):
            self.driver.get(f"https://ruarua.ru/folist/")
        Following = []
        Follower = []
        try:
            # Locate the header div by exact text
            header_text = "Following List"
            header = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//h5[contains(., '{header_text}')]")))
            
            # Find the immediately following table
            table = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//h5[contains(., '{header_text}')]/following-sibling::table[1]")))
            
            # Get all rows from tbody
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            hrefs = []
            for row in rows:
                try:
                    # Get first td's anchor href
                    first_td = row.find_element(By.XPATH, "./td[1]")
                    anchor = first_td.find_element(By.TAG_NAME, "a")
                    href = anchor.get_attribute("href")
                    if href:
                        hrefs.append(href)
                except NoSuchElementException:
                    continue  # Skip rows without anchors
            
            for i in range (len(hrefs)): hrefs[i] = hrefs[i].split('=')[1]
            Following = hrefs
        except TimeoutException:
            print("Timed out waiting for table elements to load")
            raise
        except NoSuchElementException as e:
            print(f"Required element not found: {str(e)}")
            raise
        try:
            # Locate the header div by exact text
            header_text = "Follower List"
            header = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//h5[contains(., '{header_text}')]")))
            
            # Find the immediately following table
            table = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//h5[contains(., '{header_text}')]/following-sibling::table[1]")))
            
            # Get all rows from tbody
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            hrefs = []
            for row in rows:
                try:
                    # Get first td's anchor href
                    first_td = row.find_element(By.XPATH, "./td[1]")
                    anchor = first_td.find_element(By.TAG_NAME, "a")
                    href = anchor.get_attribute("href")
                    if href:
                        hrefs.append(href)
                except NoSuchElementException:
                    continue  # Skip rows without anchors
            
            for i in range (len(hrefs)): hrefs[i] = hrefs[i].split('=')[1]
            Follower = hrefs
        except TimeoutException:
            print("Timed out waiting for table elements to load")
            raise
        except NoSuchElementException as e:
            print(f"Required element not found: {str(e)}")
            raise
        
        return (Following, Follower)


    def dailycard(self) -> None:
        """
        Get the dailycard for the player.
        """
        print("Getting dailycard...")
        if not self.urls_match(self.driver, "https://ruarua.ru/dailycard/"):
            self.driver.get("https://ruarua.ru/dailycard/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof dailycard === "function");'))
        self.driver.execute_script("dailycard();")
        print("Dailycard done!")
    def sign(self) -> None:
        """
        Sign in for the player.
        """
        print("Signing...")
        try:
            if not self.urls_match(self.driver, "https://ruarua.ru/sign/"):
                self.driver.get("https://ruarua.ru/sign/")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof doit === "function");'))
            self.driver.execute_script("doit();")
        except Exception as e: print(f"Error: {e}")
        print("Signing done!")
    def newsign(self) -> None:
        """
        New-Player Sign in for the player.
        """
        print("Newsigning...")
        try:
            if not self.urls_match(self.driver, "https://ruarua.ru/newsign/"):
                self.driver.get("https://ruarua.ru/newsign/")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof newsign === "function");'))
            self.driver.execute_script("newsign();")
        except Exception as e: print(f"Error: {e}")
        print("Newsigning done!")
    def tree(self) -> None:
        """
        Collect tree power for the player.
        """
        print("Collecting tree power...")
        if not self.urls_match(self.driver, "https://ruarua.ru/power/"):
            self.driver.get("https://ruarua.ru/power/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof doit === "function");'))
        self.driver.execute_script("doit();")
        print("Tree energy collected!")
        
    def chooseWorld(self, world) -> None:
        print("Selecting world...")
        if not self.urls_match(self.driver, "https://ruarua.ru/world/"):
            self.driver.get("https://ruarua.ru/world/")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script('return (document.readyState === "complete") && (typeof chooseworld === "function");'))
        self.driver.execute_script(f"chooseworld('{world}');")
        print(f"World {world} chosen.")
        
    def claimWorldReward(self):
        """
        Claim all world rewards for the player.
        """
        print("Claiming world rewards...")
        success_message = "There are currently no rewards that can be claimed qwq"
        
        if not self.urls_match(self.driver, "https://ruarua.ru/reward/"):
            self.driver.get("https://ruarua.ru/reward/")
        
        for i in range(50):
            try:
                self.driver.execute_script("rewardworld();")
                try:
                    ans_element = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'ans')))
                    if ans_element.text.strip() == success_message: break
                    
                except TimeoutException:
                    print("'ans' element not found within timeout")
                    
                time.sleep(1.1)
                
            except JavascriptException as e:
                break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                break
        print("World reward collected.")
        
        
    def claimAchievement(self) -> None:
        """
        Claim all achievements for the player.
        """
        print("Claiming achievements...")
        if not self.urls_match(self.driver, "https://ruarua.ru/achievement/"):
            self.driver.get("https://ruarua.ru/achievement/")
        locators = [
            (By.XPATH, "//*[text()='Claim']"),  # Exact text match
            (By.CSS_SELECTOR, "[value='Claim']"),  # Input buttons
            (By.CSS_SELECTOR, "button:contains('Claim')")  # jQuery-style (if supported)
        ]   
        clicked_elements = 0
            
        for locator in locators:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(locator)
                )
                elements = self.driver.find_elements(*locator)
                
                for element in elements:
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable(element)
                        )
                        
                        self.driver.execute_script("arguments[0].click();", element)
                        clicked_elements += 1
                        print(f"Clicked Claim element: {element.tag_name}")
                        
                        # Small delay between clicks
                        time.sleep(0.2)
                        
                    except (StaleElementReferenceException, NoSuchElementException):
                        continue
                        
            except TimeoutException:
                continue
        print("Achievement Claimed!")
    
    def claimQuestReward(self):
        """
        Claim all quest rewards for the player.
        """
        print("Claiming quest rewards...")
        success_message = "Today's quest rewards have been collected."
        success_message_2 = "This week's quest rewards have been collected."
        fail_message = "You can't claim the next reward yet"
        
        if not self.urls_match(self.driver, "https://ruarua.ru/quest/"):
            self.driver.get("https://ruarua.ru/quest/")
        
        for i in range(3):
            try:
                self.driver.execute_script("rewardquest(1);")
                try:
                    ans_element = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'ans')))
                    if ans_element.text.strip() == success_message: break
                    if ans_element.text.strip() == fail_message: break
                    
                except TimeoutException:
                    print("'ans' element not found within timeout")
                    
                time.sleep(2)
                
            except JavascriptException as e:
                break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                break
        time.sleep(2)
        for i in range(7):
            try:
                self.driver.execute_script("rewardquest(2);")
                try:
                    ans_element = WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.ID, 'ans')))
                    if ans_element.text.strip() == success_message_2: break
                    if ans_element.text.strip() == fail_message: break
                    
                except TimeoutException:
                    print("'ans' element not found within timeout")
                    
                time.sleep(2)
                
            except JavascriptException as e:
                break
            except Exception as e:
                print(f"Unexpected error: {str(e)}")
                break
        print("Quest reward collected.")
        
    def checkBoss(self, timeout = 10) -> dict:
        """
        Checks boss status.
        
        Note that the method is executed entirely on frontend.
        """
        print("Checking boss status...")
        
        # if not self.urls_match(self.driver, "https://ruarua.ru/boss/"):
        self.driver.get("https://ruarua.ru/boss/")
            
        try:
            # Wait for the element with ID starting with "nowheal"
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[id^='nowheal']"))
            )
            
            bossHpText = str(self.driver.execute_script("return arguments[0].parentNode.innerText;", element))
            print(bossHpText)
            
            bossHealth = int(bossHpText.strip().split("/")[0].strip())
            bossTotalHealth = int(bossHpText.strip().split("/")[1].strip())
            
            countdown_boss = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#countdown_boss"))
            )
            stamex = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#stamex"))
            )
            
            m, s = countdown_boss.text.strip().split(":")
            m = int(m.strip())
            s = int(s.strip())
            stam_time = m * 60 + s
            stamex = stamex.text.replace(' ', '').replace('+', '')
            try: stamex = int(stamex) | 0
            except: stamex = 0
            
            staminaTime = stam_time
            stamina = 6 - math.ceil(stam_time / 60) + stamex
            
            
        except TimeoutException:
            print(f"Error: Timeout when locating boss information.")
        except NoSuchElementException:
            print("Error: Could not locate boss information.")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
        
        return {'bossHealth': bossHealth, 'bossTotalHealth': bossTotalHealth, 'stamina': stamina, 
                'staminaTime': staminaTime}
        
        
    def sendMessage(self, message, timeout=10):
        """
        Sends a message to an element with id="message" after ensuring it's present and interactable.
        
        Args:
            driver: Selenium WebDriver instance
            message: Text to send (str)
            timeout: Maximum wait time in seconds (default: 10)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            message_input = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, "message"))
            )
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.ID, "message"))
            )
            time.sleep(1)
            message_input.send_keys(message)
            self.driver.execute_script("send();")
            
            print(f"Successfully sent message: {message}")
            return True
            
        except TimeoutException:
            print(f"Timeout: Element with id='message' not found within {timeout} seconds")
        except NoSuchElementException:
            print("Element with id='message' does not exist")
        except InvalidElementStateException:
            print("Element with id='message' is not interactable")
        except Exception as e:
            print(f"Unexpected error while sending message: {str(e)}")
        
        return False
    def redeemCode(self, ListOfCode: str | list [str]) -> None:
        """
        Redeem Code using provided ruaid.
        
        Args:
            ListOfCode (str): Username to input.
        """
        print("Redeeming code...")
        if not self.urls_match(self.driver, "https://ruarua.ru/code/"):
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