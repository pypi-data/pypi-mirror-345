# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.firefox.service import Service as FirefoxService
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
# from selenium.webdriver.edge.service import Service as EdgeService
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, ElementClickInterceptedException
# from lxml import etree
# from io import StringIO
# import pandas as pd
# import re
# import os
# import time
# from difflib import SequenceMatcher
# from datetime import datetime
# import os
# import pandas as pd
# from selenium.webdriver.firefox.options import Options

# from selenium.webdriver.firefox.service import Service
# from selenium.webdriver.common.keys import Keys
# from datetime import datetime
# from PIL import Image
# import mss
# import time
# from selenium import webdriver

# from webdriver_manager.chrome import ChromeDriverManager

# Standard Library
import os
import time
import base64
import warnings
import tempfile
from datetime import datetime
from io import StringIO
import re

# Third-Party Libraries
import pandas as pd
import numpy as np
import requests
from lxml import etree
from difflib import SequenceMatcher
from PIL import Image
import mss
import shutil
import pyautogui




# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    UnexpectedAlertPresentException,
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException,
)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from webdriver_manager.microsoft import EdgeChromiumDriverManager





# Google API
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Tkinter
import tkinter as tk
from tkinter import ttk, messagebox


# # Set display options for pandas
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_colwidth', None)
# pd.set_option('display.width', None)



def Generate_File_name(Service_name,trial,directory='performance_logs_'):

    
    todays_date = datetime.today().strftime('%Y-%m-%d')  # Generates today's date in 'YYYY-MM-DD' format
    trial=4
    file_path = f"{directory}{Service_name}_{trial}_{todays_date}.csv"
    print('file_Generate',file_path)
    return file_path


# def FireFox_Driver_info(maximize=False):
#         firefox_options.set_preference("dom.speechrecognition.enabled", False)
#         firefox_options.set_preference("dom.webspeech.synth.enabled", False)

#         firefox_path = r"C:\Users\mohamed.elhajabdou\AppData\Local\Mozilla Firefox\firefox.exe"
#         driver_path = r'C:\Users\mohamed.elhajabdou\TensorFlow\ELMS_Automation\geckodriver.exe'
            
#         # Setup Firefox options and binary location
#         options = Options()
#         binary = FirefoxBinary(firefox_path)
#         options.binary = binary

#         # Setup WebDriver with the specified GeckoDriver and Firefox binary
#         service = Service(executable_path=driver_path)
#         driver = webdriver.Firefox(service=service, options=options)
#         if maximize==True:
#             driver.maximize_window()

#         return driver



# def Chrome_Driver_info(maximize=False,driver_path_data = 'chromedriver.exe'):
#     # Define Chrome options
#     options = Options()
#     options.add_argument("--disable-notifications")  # Disable browser notifications
#     options.add_argument("--start-maximized")  # Start maximized
#     options.add_argument("--disable-infobars")  # Disable "Chrome is being controlled by automated test software"
#     options.add_argument("--disable-extensions")  # Disable extensions

#     # Specify the path to ChromeDriver executable
    

#     # Set up Chrome WebDriver service
#     service = Service(executable_path=driver_path_data)

#     # Initialize Chrome WebDriver
#     driver = webdriver.Chrome(service=service, options=options)

#     # Maximize the window if requested
#     if maximize:
#         driver.maximize_window()

#     return driver




def Chrome_Driver_info(maximize=False, headless=False):
    # Define Chrome options
    options = ChromeOptions()
    options.add_argument("--disable-notifications")  # Disable browser notifications
    options.add_argument("--disable-infobars")  # Disable "Chrome is being controlled by automated test software"
    options.add_argument("--disable-extensions")  # Disable extensions

    if headless:
        options.add_argument("--headless")  # Run in headless mode (no UI)
    if maximize:
        options.add_argument("--start-maximized")  # Start maximized

    # Use webdriver-manager to get the ChromeDriver automatically
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def FireFox_Driver_info(maximize=False):
    # Define Firefox options
    options = FirefoxOptions()
    
    # Disable Speech Recognition
    options.set_preference("dom.speechrecognition.enabled", False)
    options.set_preference("dom.webspeech.synth.enabled", False)

    # Set the paths for Firefox binary and GeckoDriver
    firefox_path = r"C:\Users\mohamed.elhajabdou\AppData\Local\Mozilla Firefox\firefox.exe"
    driver_path = r'C:\Users\mohamed.elhajabdou\TensorFlow\ELMS_Automation\geckodriver.exe'
    
    # Setup Firefox binary
    binary = FirefoxBinary(firefox_path)
    options.binary = binary

    # Setup WebDriver with the specified GeckoDriver and Firefox binary
    service = FirefoxService(executable_path=driver_path)
    driver = webdriver.Firefox(service=service, options=options)
    
    # Maximize the window if requested
    if maximize:
        driver.maximize_window()

    return driver


def Edge_Driver_info(maximize=False, headless=False):
    """
    Initialize and return the Edge WebDriver.

    Parameters:
        maximize (bool): Whether to maximize the browser window.
        headless (bool): Whether to run the browser in headless mode.

    Returns:
        WebDriver: Edge WebDriver instance.
    """
    # Define Edge options
    options = EdgeOptions()
    options.add_argument("--disable-notifications")  # Disable browser notifications
    options.add_argument("--disable-infobars")  # Disable "Edge is being controlled by automated test software"
    options.add_argument("--disable-extensions")  # Disable extensions
    
    # Configure headless mode and maximize window
    if headless:
        options.add_argument("--headless")  # Run in headless mode
    if maximize:
        options.add_argument("--start-maximized")  # Start browser maximized
    
    # Automatically install and set up EdgeDriver using webdriver-manager
    service = EdgeService(EdgeChromiumDriverManager().install())

    # Initialize Edge WebDriver
    driver = webdriver.Edge(service=service, options=options)
    
    return driver



def Navigating_into_service_name_SH(driver,Service_name,loading_xpath):
    Service_tab_home_page=['/html/body/div[3]/div[1]/div[1]/ul/li[2]','/html/body/div[3]/div[1]/div[1]/ul/li[2]/a']
    ELMS_tab_home_page=['//*[@id="sidebar"]/ul/li[16]/a','//*[@id="sidebar"]/ul/li[16]/a/span','//*[@id="sidebar"]/ul/li[16]/a/i[2]','//*[@id="sidebar"]/ul/li[16]/a']
    ELMS_tab_home_page_text=['ELMS']
    Service_tab_text=['Services']
    clicking_on_element_by_all_option(driver, Service_tab_home_page, Service_tab_text, max_retries=4, scroll=False, timeout=4)

    time.sleep(2)
    capture_screenshot(screen_number=1, service_name=Service_name, step_name="After clicking service tab")


    Services_search_field=['//*[@id="fontawsome-search"]',
                           '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[1]/div/div/span']

    

    # Wait for the page to load
    wait_for_page_to_load(driver, loading_xpath)
    time.sleep(2)

    # Input the service name in the search bar
    input_data_by_all_option(driver, Services_search_field, [''], [Service_name], calender_date=None,
                                  max_attempts=3, timeout=10, scroll=False, input_delay=2, field_type='Text_field')
    time.sleep(2)
    capture_screenshot(screen_number=1, service_name=Service_name, step_name="Input service name")

    Service_card_xpath=['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div/a/span',
                       '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div/a/div',
                       '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div/a']

    clicking_on_element_by_all_option(driver, Service_card_xpath, [Service_name], max_retries=4, scroll=False, timeout=4)
    time.sleep(2)




def capture_screenshot(base_path='Screenshots',screen_number=0, service_name="default_service", step_name="default_step", use_webdriver=False, driver=None):
    """
    Takes a screenshot using either Selenium WebDriver or the default screen capture method (MSS).
    Saves the screenshot in a structured directory for each service.

    Parameters:
    screen_number (int): The number of the screen to capture (0 for primary screen, only for MSS).
    service_name (str): Name of the service for organizing screenshots.
    step_name (str): Description of the step to include in the screenshot filename.
    use_webdriver (bool): Whether to use Selenium WebDriver for capturing the screenshot.
    driver (WebDriver): Selenium WebDriver instance, required if use_webdriver=True.
    """
    # Define the directory path for the screenshots of the service
    directory_path = f"{base_path}/{service_name}"
    filename = f"{step_name.replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.png"
    save_path = os.path.join(directory_path, filename)
    print('save_path======>',save_path)
    # Create directories if they don't exist
    os.makedirs(directory_path, exist_ok=True)

    if use_webdriver:
        if driver is None:
            raise ValueError("WebDriver instance must be provided when use_webdriver=True.")

        print("Capturing screenshot using Selenium WebDriver...")
        driver.save_screenshot(save_path)
        print(f"Screenshot saved to {save_path}")
    else:
        with mss.mss() as sct:
            # Get list of connected screens
            monitors = sct.monitors
            if screen_number >= len(monitors):
                print(f"Screen number {screen_number} does not exist. Total screens detected: {len(monitors) - 1}")
                return

            # Select the specified screen's monitor information
            monitor = monitors[screen_number]
            print(f"Capturing screenshot of screen {screen_number}...")

            # Take screenshot of the specified screen
            screenshot = sct.grab(monitor)

            # Save the screenshot to the specified path
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            img.save(save_path)
            print(f"Screenshot saved to {save_path}")






# def capture_screenshot(original_path=1,directory_path='Screenshots',screen_number=0, service_name="default_service", step_name="default_step"):
#     """
#     Takes a screenshot of the specified screen and saves it in a single file under a structured directory for each service.

#     Parameters:
#     screen_number (int): The number of the screen to capture (0 for primary screen).
#     service_name (str): Name of the service for organizing screenshots.
#     step_name (str): Description of the step to include in the screenshot filename.
#     """

#     if len ( step_name)>50:
#         step_name=step_name[0:30]

#     if original_path:

#     # Define the directory path for the screenshots of the service
#         directory_path = f"Screenshots/{service_name}"
#     else:
#         directory_path=directory_path
#     filename = f"{step_name.replace(' ', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.png"
#     save_path = os.path.join(directory_path, filename)

#     # Create directories if they don't exist
#     os.makedirs(directory_path, exist_ok=True)

#     with mss.mss() as sct:
#         # Get list of connected screens
#         monitors = sct.monitors
#         if screen_number >= len(monitors):
#             print(f"Screen number {screen_number} does not exist. Total screens detected: {len(monitors) - 1}")
#             return

#         # Select the specified screen's monitor information
#         monitor = monitors[screen_number]
#         print(f"Capturing screenshot of screen {screen_number}...")

#         # Take screenshot of the specified screen
#         screenshot = sct.grab(monitor)

#         # Save the screenshot to the specified path
#         img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
#         img.save(save_path)
#         print(f"Screenshot saved to {save_path}")





def clicking_on_element_by_all_option(driver, x_paths_input, text_input_list, max_retries=4, scroll=False, timeout=20):
    retry_count = 0

    # Scroll to the element if required
    if scroll:
        try:
            for text_input in text_input_list:
                element = driver.find_element(By.XPATH, f"//*[text()='{text_input}']")
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                print(f"Scrolled to element with text: {text_input}")
        except Exception as e:
            print(f"Failed to scroll to element:")

    # First case: Try clicking using the provided XPaths
    while retry_count < max_retries:
        for xpath in x_paths_input:
            try:
                print(f"Attempt {retry_count + 1} to click element with XPath: '{xpath}'")
                element = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                try:
                    element.click()
                    # time.sleep(0.5)  # Short pause to observe the first click
                    # element.click()
                    print(f"Clicked successfully on element with XPath: {xpath}")
                    return True
                except Exception as click_exception:
                    print(f"Failed to click using element.click(): {click_exception}")
                    # Attempt to click via JavaScript
                    try:
                        driver.execute_script("arguments[0].click();", element)
                        print("Clicked using JavaScript as a fallback.")
                        return True
                    except Exception as js_click_exception:
                        print(f"JavaScript click also failed: {js_click_exception}")
                        continue
            except Exception as e:
                print(f"Could not find/click element with XPath '{xpath}', trying next XPath:")
                continue
        retry_count += 1

    # If XPath fails, proceed to the second case: Clicking by visible text
    print("Failed to click using XPaths, trying to click based on text.")
    retry_count = 0

    while retry_count < max_retries:
        for text_input in text_input_list:
            try:
                print(f"Attempt {retry_count + 1} to click element with text: '{text_input}'")

                # Option 1: Exact text match using XPath
                try:
                    element = WebDriverWait(driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, f"//*[text()='{text_input}']"))
                    )
                    try:
                        element.click()
                        print(f"Clicked element with exact text '{text_input}' (XPath exact match).")
                        return True
                    except Exception as click_exception:
                        print(f"Failed to click using element.click(): {click_exception}")
                        # Attempt to click via JavaScript
                        try:
                            driver.execute_script("arguments[0].click();", element)
                            print("Clicked using JavaScript as a fallback.")
                            return True
                        except Exception as js_click_exception:
                            print(f"JavaScript click also failed: {js_click_exception}")
                            continue
                except TimeoutException:
                    print(f"Could not find element with exact text '{text_input}', trying other methods.")
                    continue

                # Additional options (using contains, span elements, parent elements, etc.) follow the same pattern
                # Wrap each click attempt in a try-except block without returning on exception
            except Exception as e:
                print(f"An error occurred while trying to click element with text '{text_input}': ")
                continue
        
        # Exponential backoff before retrying
        retry_count += 1
        time.sleep(1 * retry_count)

    # If all retries are exhausted, indicate failure by returning False
    print(f"Failed to click element with provided text inputs after {max_retries} attempts.")
    return False






# Function to check if a page is fully loaded
def page_is_completed(driver):
    return driver.execute_script("return document.readyState") == "complete"



def similar(a, b):
    """Returns the similarity ratio between two strings."""
    return SequenceMatcher(None, a, b).ratio()

# Initialize match flags
first_column_match = 0
second_column_match = 0
third_column_match = 0
fourth_column_match = 0
fifth_column_match = 0

# # Function to find the index where all flags are 1
# def find_matching_row(result_df, test_data):
#     for i in range(0, len(result_df)):
#         try:
            
#             # Check if all columns match with a similarity greater than 90%
#             if (
#                 similar(result_df['Land Use'].iloc[i], test_data['Land Use']) > 0.9 and
#                 similar(result_df['District'].iloc[i], test_data['District']) > 0.9 and
#                 similar(result_df['Community'].iloc[i], test_data['Community']) > 0.9 and
#                 similar(result_df['Road'].iloc[i], test_data['Road']) > 0.9 and
#                 similar(result_df['Plot Number'].iloc[i], test_data['Plot Number']) > 0.9 
#             ):
#                 return i  # Return the index if all conditions are satisfied
#         except:
#             pass
    
#     return 'None'  # Return None if no row matches all criteria


# def click_checkbox_by_row(driver, row_number):
#     """
#     Clicks the checkbox at the specified row number in the table dynamically.
    
#     :param driver: WebDriver instance
#     :param row_number: The row number of the checkbox to click (1-based index)
#     """
#     # Dynamic XPath for the checkbox based on the row number
#     checkbox_xpath_1 = f"//tbody/tr[{row_number}]/td[1]/label/input"
#     checkbox_xpath_2 = f"//tbody/tr[{row_number}]/td[1]/label/span"

#     try:
#         # Attempt to click the first checkbox XPath
#         checkbox_element = WebDriverWait(driver, 10).until(
#             EC.element_to_be_clickable((By.XPATH, checkbox_xpath_1))
#         )
#         checkbox_element.click()
#         print(f"Clicked checkbox at row {row_number} using first XPath.")
#     except:
#         try:
#             # If the first XPath fails, attempt to click the second one
#             checkbox_element = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.XPATH, checkbox_xpath_2))
#             )
#             checkbox_element.click()
#             print(f"Clicked checkbox at row {row_number} using second XPath.")
#         except:
#             print(f"Failed to click checkbox at row {row_number}")




def extract_performance_logs_and_append_to_csv(driver, file_path, step_type, action_type):
    """
    Extract performance logs from the Selenium WebDriver, append the results to a CSV file, 
    and include 'Step Type', 'Action Type', and 'time_date' columns.

    :param driver: Selenium WebDriver instance
    :param file_path: Path to the CSV file where data should be saved
    :param step_type: The step type to be added in the CSV
    :param action_type: The action type to be added in the CSV
    """
    # Extract Performance Logs from window.performance
    WebDriverWait(driver, 20).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, 'body'))
)

    try:
        # Simplified JavaScript for performance logs
        test = driver.execute_script(
            """
            var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {};
            return performance.getEntriesByType('resource');
            """
        )
    except Exception as e:
        print(f"Error fetching performance logs: ")
        return None


    # Get current timestamp for the time_date column
    current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Convert the logs into a list of dictionaries
    logs = []
    for item in test:
        logs.append({
            'name': item.get('name'),
            'initiatorType': item.get('initiatorType'),
            'duration': item.get('duration'),
            'decodedBodySize': item.get('decodedBodySize', 0),
            'transferSize': item.get('transferSize', 0),
            'responseStatus': item.get('responseStatus', 'N/A'),
            'startTime': item.get('startTime'),
            'responseEnd': item.get('responseEnd'),
            'connectEnd': item.get('connectEnd', 'N/A'),
            'connectStart': item.get('connectStart', 'N/A'),
            'contentType': item.get('contentType', 'N/A'),
            'domainLookupEnd': item.get('domainLookupEnd', 'N/A'),
            'domainLookupStart': item.get('domainLookupStart', 'N/A'),
            'fetchStart': item.get('fetchStart', 'N/A'),
            'nextHopProtocol': item.get('nextHopProtocol', 'N/A'),
            'requestStart': item.get('requestStart', 'N/A'),
            'responseStart': item.get('responseStart', 'N/A'),
            'secureConnectionStart': item.get('secureConnectionStart', 'N/A'),
            'serverTiming': item.get('serverTiming', 'N/A'),
            'unloadEventEnd': item.get('unloadEventEnd', 'N/A'),
            'unloadEventStart': item.get('unloadEventStart', 'N/A'),
            'workerStart': item.get('workerStart', 'N/A'),
            'Step Type': step_type,  # Add Step Type column
            'Action Type': action_type,  # Add Action Type column
            'time_date': current_timestamp  # Add time_date column with current timestamp
        })

    # Convert the logs into a pandas DataFrame
    df = pd.DataFrame(logs)

    # Calculate total response time (assuming 'downloadTime' and 'ttfb' are part of your logs)
    if 'downloadTime' in df.columns and 'ttfb' in df.columns:
        df['Total_Response_time'] = df['downloadTime'] + df['ttfb']
    else:
        df['Total_Response_time'] = df['duration']  # If downloadTime and ttfb are missing, use 'duration'

    # Check if the file exists, if not, create it; otherwise, append
    if not os.path.exists(file_path):
        df.to_csv(file_path, mode='w', index=False, header=True)
    else:
        df.to_csv(file_path, mode='a', index=False, header=False)

    print(f"Data appended to {file_path}")
    return df





def wait_for_page_to_load(driver, loading_xpath, timeout=20):
    """
    Waits for the page to finish loading by checking the 'Loading' text and returns once the page has loaded.
    
    Args:
        driver: Selenium WebDriver instance.
        loading_xpath: XPath of the element where 'Loading' text appears.
        timeout: Maximum time to wait for the page to load (default is 20 seconds).
    
    Returns:
        None
    """
    try:
        # Extract the 'Loading' text
        loading_text = driver.find_element(By.XPATH, loading_xpath).text

        # Check if 'Loading' is present in the extracted text
        if 'Loading' in loading_text:
            print('Waiting for the page to load...')

            # Wait until the 'Loading' text disappears or until timeout
            WebDriverWait(driver, timeout).until_not(
                EC.text_to_be_present_in_element((By.XPATH, loading_xpath), 'Loading')
            )
        print("Page has loaded.")
    except Exception as e:
        print(f"An error occurred while waiting for the page to load:")
        
        


# Function to click on an element by its visible text
def click_element_by_text(driver, text, max_retries=4, timeout=20):
    """Waits for an element containing the specified text to be clickable and clicks it."""
    retry_count = 0
    while retry_count < max_retries:
        try:
            print(f"Attempt {retry_count + 1} to click element with text: '{text}'")

            # Option 1: Try locating the element using `contains(text())`
            clickable_element = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{text}')]"))
            )

            # Click the element if found
            clickable_element.click()
            print(f"Element with text '{text}' clicked successfully (using contains).")
            return True  # Success

        except TimeoutException:
            retry_count += 1
            print(f"Retry {retry_count}/{max_retries}: Could not click element with contains text '{text}'. Trying other methods...")

            # Option 2: Try locating the element using exact text match
            try:
                element = driver.find_element(By.XPATH, f"//*[text()='{text}']")
                element.click()
                print(f"Element with text '{text}' clicked successfully (using exact text match).")
                return True  # Success
            except Exception as e:
                print(f"Failed to click element by exact match:")

            # Option 3: Try locating a span element with exact text match
            try:
                element = driver.find_element(By.XPATH, f"//span[text()='{text}']")
                element.click()
                print(f"Element with span text '{text}' clicked successfully (using span exact match).")
                return True  # Success
            except Exception as e:
                print(f"Failed to click element by span match: ")

            # Option 4: Try clicking the parent of the element with the text
            try:
                element = driver.find_element(By.XPATH, f"//*[text()='{text}']/parent::*")
                element.click()
                print(f"Clicked parent of element with text '{text}'.")
                return True  # Success
            except Exception as e:
                print(f"Failed to click parent element: ")

            # Exponential backoff to give the page more time to load
            time.sleep(1 * retry_count)

    # If all retries are exhausted, return False and log the issue
    print(f"Failed to click element with text '{text}' after {max_retries} attempts.")
    return False






def input_data_by_all_option(driver, x_paths_input, text_input_list, data, calender_date,max_attempts=3, timeout=10, scroll=False,input_delay=2,field_type='Text_field'):
    """
    Attempts to input data into elements located by multiple XPaths or text values, trying up to max_attempts times.
    Adds delay before input to ensure the frontend registers the action.

    Args:
        driver: The Selenium WebDriver instance.
        x_paths_input: A list of possible XPaths to try inputting data into.
        text_input_list: A list of text values to try if XPaths fail.
        data: The data to input into the field.
        max_attempts: Maximum number of attempts to input the data.
        timeout: Timeout for waiting for each element to be interactable.
        scroll: Boolean flag to scroll to the element before inputting data.
        input_delay: Delay time in seconds before inputting data (default is 2 seconds).
        
    Returns:
        True if successful, False if all attempts fail.
    
    
    """
        
    retry_count = 0
    waiter = 0.2  # Initial wait time between retries

    # Scroll to the element if required
    if scroll:
        for text_input in text_input_list:
            try:
                element = driver.find_element(By.XPATH, f"//*[text()='{text_input}']")
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                print(f"Scrolled to element with text: {text_input}")
            except Exception as e:
                print(f"Failed to scroll to element:")

    # First case: Try inputting data using the provided XPaths
    while retry_count < max_attempts:
        for xpath in x_paths_input:
            try:
                print(f"Attempt {retry_count + 1} to input data using XPath: '{xpath}'")
                input_field = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                # Adding delay before inputting data


                if field_type=='Text_field':

                    try :

                        time.sleep(input_delay)
                        input_field.clear()
                        print(data)
                        input_field.send_keys(data)

                        print(f"Data input successfullysssssssssssssssssssss using XPath: '{xpath}'")
                        return True  # Exit after successful input
                    except Exception as e:
                        print(f"Error inputting data in Text field: ")
                        continue 

                elif field_type=='Calender':

                    try :
                        element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                        element.click()
                        # Locate the day in the calendar and click it
                        day_xpath = f"//td[normalize-space()='{calender_date}' and contains(@class, 'day')]"
                        day_element = WebDriverWait(driver, timeout).until(
                            EC.element_to_be_clickable((By.XPATH, day_xpath))
                        )

                        day_element.click()
                    except Exception as e:
                        print(f"Error inputting data in Text field: ")
                        continue
                    
                elif field_type=='others':
                    try:
                        time.sleep(input_delay)
                        input_field.send_keys(data)

                        print(f"Data input successfullysssssssssssssssssssss using XPath: '{xpath}'")
                        return True  # Exit after successful input
                    except Exception as e:
                        print(f"Error inputting data in Text field: ")
                        continue 
            



                    
                
                print(f"Data input successfully using XPathsssssssssssssssssssssssss: '{xpath}'")
                return True  # Exit after successful input
            
            except (TimeoutException, ElementNotInteractableException):
                print(f"Could not find/interact with element using XPath '{xpath}', retrying.")
                continue
        
        retry_count += 1

    # If XPath fails, proceed to the second case: Inputting based on visible text
    print("Failed to input using XPaths, trying to input based on text.")
    retry_count = 0

    # Loop through each text_input and try to input data
    while retry_count < max_attempts:
        for text_input in text_input_list:
            try:
                print(f"Attempt {retry_count + 1} to input data using text: '{text_input}'")

                # Option 1: Input data based on exact text match using XPath
                try:
                    
                    print('# Option 1: Input data based on text')
                    input_field = WebDriverWait(driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, f"//*[text()='{text_input}']")))
                    
                    
                    if field_type=='Text_field':
                        
                        try :
                            
                            time.sleep(input_delay)
                            input_field.clear()
                            input_field.send_keys(data)
                            
                            print(f"Data input successfully using XPath: '{xpath}'")
                            return True  # Exit after successful input
                        except Exception as e:
                            print(f"Error inputting data in Text field: ")
                        
                    elif field_type=='Calender':

                        try :


                            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            element.click()
                            # Locate the day in the calendar and click it
                            day_xpath = f"//td[normalize-space()='{calender_date}' and contains(@class, 'day')]"
                            day_element = WebDriverWait(driver, timeout).until(
                                EC.element_to_be_clickable((By.XPATH, day_xpath))
                            )

                            day_element.click()
                        
                        except Exception as e:
                            print(f"Error inputting data in Text field: ")
                            continue
                        
                        
                        

                    
                    
                    print(f"Data input successfully using text: '{text_input}'")
                    return True
                except TimeoutException:
                    print(f"Could not find element with exact text '{text_input}', trying other methods.")
                    continue

                # Option 2: Input data based on contains text using XPath
                try:
                    
                    print('# Option 2: Input data based on text')
                    input_field = WebDriverWait(driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{text_input}')]")))
                    
                    
                    if field_type=='Text_field':
                        
                        try :
                            
                            time.sleep(input_delay)
                            input_field.clear()
                            input_field.send_keys(data)
                            
                            print(f"Data input successfully using XPath: '{xpath}'")
                            return True  # Exit after successful input
                        except Exception as e:
                            print(f"Error inputting data in Text field:")
                            continue
                            
                            
                            
                        
                        
                    elif field_type=='Calender':

                        try :


                            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            element.click()
                            # Locate the day in the calendar and click it
                            day_xpath = f"//td[normalize-space()='{calender_date}' and contains(@class, 'day')]"
                            day_element = WebDriverWait(driver, timeout).until(
                                EC.element_to_be_clickable((By.XPATH, day_xpath))
                            )

                            day_element.click()
                        
                        except Exception as e:
                            print(f"Error inputting data in Text field: ")
                            continue
                        
                        

                    
                    print(f"Data input successfully using contains text: '{text_input}'")
                    return True
                except TimeoutException:
                    print(f"Could not find element with contains text '{text_input}', trying other methods.")
                    continue

                # Option 3: Attempt to find and input data in <span> elements
                try:
                    
                    print('# Option 3: Input data based on text')
                    input_field = WebDriverWait(driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, f"//span[text()='{text_input}']"))
                    )
                    # Adding delay before inputting data
                    
                    
                    if field_type=='Text_field':
                        
                        try :
                            
                            time.sleep(input_delay)
                            input_field.clear()
                            input_field.send_keys(data)
                            
                            print(f"Data input successfully using XPath: '{xpath}'")
                            return True  # Exit after successful input
                        except Exception as e:
                            print(f"Error inputting data in Text field:")
                            continue
                        
                    elif field_type=='Calender':

                        try :


                            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            element.click()
                            # Locate the day in the calendar and click it
                            day_xpath = f"//td[normalize-space()='{calender_date}' and contains(@class, 'day')]"
                            day_element = WebDriverWait(driver, timeout).until(
                                EC.element_to_be_clickable((By.XPATH, day_xpath))
                            )

                            day_element.click()
                        
                        except Exception as e:
                            print(f"Error inputting data in Text field:")
                            continue

                    
                    print(f"Data input successfully in span element with text: '{text_input}'")
                    return True
                except TimeoutException:
                    print(f"Could not find span element with text '{text_input}', trying other methods.")
                    continue

                # Option 4: Try to input data in the parent element of the text-containing element
                try:
                    
                    print('# Option 4: Input data based on text')
                    
                    
                    input_field = WebDriverWait(driver, timeout).until(
                        EC.element_to_be_clickable((By.XPATH, f"//*[text()='{text_input}']/parent::*"))
                    )
                    
                    if field_type=='Text_field':
                        
                        try :
                            
                            time.sleep(input_delay)
                            input_field.clear()
                            input_field.send_keys(data)
                            
                            print(f"Data input successfully using XPath: '{xpath}'")
                            return True  # Exit after successful input
                        except Exception as e:
                            print(f"Error inputting data in Text field:")
                            continue
                        
                    elif field_type=='Calender':

                        try :


                            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            element.click()
                            # Locate the day in the calendar and click it
                            day_xpath = f"//td[normalize-space()='{calender_date}' and contains(@class, 'day')]"
                            day_element = WebDriverWait(driver, timeout).until(
                                EC.element_to_be_clickable((By.XPATH, day_xpath))
                            )

                            day_element.click()
                        
                        except Exception as e:
                            print(f"Error inputting data in Text field:")
                            continue
                        
                        
                    
                    print(f"Data input successfully in parent element with text: '{text_input}'")
                    return True
                except TimeoutException:
                    print(f"Could not find parent element for text '{text_input}', trying other methods.")
                    continue

                # Option 5: Attempt to use JavaScript to input data if it's still not interactable
                try:
                    
                    print('# Option 5: Input data based on text')
                    input_field = driver.execute_script(
                        f"return document.evaluate(\"//*[text()='{text_input}']\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;"
                    )
                    
                    
                    
                    if field_type=='Text_field':
                        
                        try :
                            
                            time.sleep(input_delay)
                            input_field.clear()
                            input_field.send_keys(data)
                            
                            print(f"Data input successfully using XPath: '{xpath}'")
                            return True  # Exit after successful input
                        except Exception as e:
                            print(f"Error inputting data in Text field:")
                            continue
                            
                            
                            

                        
                        
                    elif field_type=='Calender':

                        try :


                            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
                            element.click()
                            # Locate the day in the calendar and click it
                            day_xpath = f"//td[normalize-space()='{calender_date}' and contains(@class, 'day')]"
                            day_element = WebDriverWait(driver, timeout).until(
                                EC.element_to_be_clickable((By.XPATH, day_xpath))
                            )

                            day_element.click()
                        
                        except Exception as e:
                            print(f"Error inputting data in Text field:")
                            
                            
                        print(f"Data input successfully using JavaScript for text: '{text_input}'")
                        return True
                except Exception as e:
                    print(f"Could not input data using JavaScript: ")
                    continue

            except Exception as e:
                print(f"An error occurred while trying to input data for text '{text_input}':")
                continue
                

        # Exponential backoff before retrying
        retry_count += 1
        time.sleep(1 * retry_count)

    #bbb If all retries are exhausted, return False
    print(f"Failed to input data for provided text inputs after {max_attempts} attempts.")
    return False


def wait_for_element_to_appear(driver, x_paths_list, max_retries=20, polling_interval=1, consecutive_exists=3, scroll=False, timeout=10):
    """
    Waits for an element to appear on the page with polling and consecutive existence check.

    :param driver: Selenium WebDriver instance.
    :param x_paths_list: List of possible XPaths for the element.
    :param max_retries: Maximum number of polling attempts.
    :param polling_interval: Time interval (seconds) between each check.
    :param consecutive_exists: Number of consecutive confirmations before confirming presence.
    :param scroll: Whether to scroll to the element before checking.
    :param timeout: Maximum wait time for an element to appear (used in explicit waits).
    :return: True if the element appears consecutively, False if timeout occurs.
    """

    retry_count = 0
    exists_count = 0  # Counter for consecutive existence checks

    # Scroll to the element if enabled
    if scroll:
        try:
            for xpath in x_paths_list:
                element = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                print(f"Scrolled to element with XPath: {xpath}")
                break  # Stop after first successful scroll
        except Exception as e:
            print(f"Failed to scroll to element")

    while retry_count < max_retries:
        for xpath in x_paths_list:
            try:
                elements = driver.find_elements(By.XPATH, xpath)
                if elements:
                    exists_count += 1
                    print(f"Element found ({exists_count}/{consecutive_exists}) with XPath")

                    # If element exists consecutively for required checks, return True
                    if exists_count >= consecutive_exists:
                        print(f"Element confirmed existing for {consecutive_exists} consecutive checks.")
                        return True
                else:
                    exists_count = 0  # Reset the counter if element not found
                    print(f"Element not found. Waiting... (Retry {retry_count + 1}/{max_retries})")

            except Exception as e:
                print(f"Error finding element with XPath")

        # Increment elapsed time and wait before retrying
        retry_count += 1
        time.sleep(polling_interval)

    print(f"Timeout reached. Element not found after {max_retries} attempts.")
    return False


# def click_and_check_url_change(driver, x_paths, text_inputs, trial, timeout=4, scroll=True, max_attempts=3):
#     """
#     Tries to click elements using multiple XPaths or text inputs, and checks if the URL has changed.
#     If the URL hasn't changed, it will retry each click up to 'max_attempts' times on all provided XPaths.
#     """
#     # Store the initial URL
#     prv_url = driver.current_url
#     print(f"Initial URL: {prv_url}")
    
#     for attempt in range(1, max_attempts + 1):
#         print(f"Attempt {attempt}/{max_attempts} to click element.")

#         # Iterate over all XPaths and try clicking each one per attempt
#         for xpath in x_paths:
#             print(f"Trying to click element with XPath: {xpath}")
#             clicked = clicking_on_element_by_all_option(driver, [xpath], text_inputs, max_retries=1, timeout=timeout, scroll=scroll)
            
#             # If a click was successful, check if the URL has changed
#             if clicked:
#                 new_url = driver.current_url
#                 print(f"New URL: {new_url}")

#                 # If the URL has changed, exit the function as successful
#                 if new_url != prv_url:
#                     print("URL has changed successfully.")
#                     return True

#                 # If the URL has not changed, try the next XPath or retry
#                 print(f"URL has not changed after clicking XPath: {xpath}. Trying next XPath...")

#         # Retry using all available text inputs after trying all XPaths
#         for text_input in text_inputs:
#             print(f"Trying to click element with text: '{text_input}'")
#             clicked = clicking_on_element_by_all_option(driver, [], [text_input], max_retries=1, timeout=timeout, scroll=scroll)

#             # If a click was successful, check if the URL has changed
#             if clicked:
#                 new_url = driver.current_url
#                 print(f"New URL: {new_url}")

#                 # If the URL has changed, exit the function as successful
#                 if new_url != prv_url:
#                     print("URL has changed successfully.")
#                     return True

#                 # If the URL has not changed, print message and continue
#                 print(f"URL has not changed after clicking text: '{text_input}'. Trying next option...")

#     # If all attempts are exhausted without success, return False
#     print(f"Failed to change URL after {max_attempts} attempts.")
#     return False


def click_and_check_url_change(driver, x_paths, text_inputs, trial, timeout=4, scroll=True, max_attempts=3):
    """
    Tries to click elements using multiple XPaths or text inputs, and checks if the URL has changed.
    If the URL hasn't changed, it will retry each click up to 'max_attempts' times on all provided XPaths.
    """
    # Store the initial URL
    prv_url = driver.current_url
    print(f"Initial URL: {prv_url}")
    
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt}/{max_attempts} to click element.")

        # Iterate over all XPaths and try clicking each one per attempt
        for xpath in x_paths:
            print(f"Trying to click element with XPath: {xpath}")
            clicked = clicking_on_element_by_all_option(driver, [xpath], text_inputs, max_retries=1, timeout=timeout, scroll=scroll)
            
            # If a click was successful, check if the URL has changed
            if clicked:
                new_url = driver.current_url
                print(f"New URL: {new_url}")

                # If the URL has changed, exit the function as successful
                if new_url != prv_url:
                    print("URL has changed successfully.")
                    return True  # Exit immediately after success

                # If the URL has not changed, try the next XPath or retry
                print(f"URL has not changed after clicking XPath: {xpath}. Trying next XPath...")

        # Retry using all available text inputs after trying all XPaths
        for text_input in text_inputs:
            print(f"Trying to click element with text: '{text_input}'")
            clicked = clicking_on_element_by_all_option(driver, [], [text_input], max_retries=1, timeout=timeout, scroll=scroll)

            # If a click was successful, check if the URL has changed
            if clicked:
                new_url = driver.current_url
                print(f"New URL: {new_url}")

                # If the URL has changed, exit the function as successful
                if new_url != prv_url:
                    print("URL has changed successfully.")
                    return True  # Exit immediately after success

                # If the URL has not changed, print message and continue
                print(f"URL has not changed after clicking text: '{text_input}'. Trying next option...")

    # If all attempts are exhausted without success, return False
    print(f"Failed to change URL after {max_attempts} attempts.")
    return False




# # Define find_matching_row function if it's not already defined
# def find_matching_row(df, criteria):
#     """
#     Finds the row index in df that matches all key-value pairs in criteria.
#     Returns -1 if no match is found.
#     """
#     for index, row in df.iterrows():
#         if all(row[key] == value for key, value in criteria.items()):
#             return index
#     return -1  # Return -1 if no matching row is found

# # Define the function to click a checkbox by row index using the provided base XPath pattern
# def click_checkbox_by_row(driver, row_index):
#     """
#     Clicks the checkbox in the specified row index of the table.
#     Assumes the row index is 1-based (for XPath purposes).
#     """
#     # Define the base XPath pattern with a placeholder for the row index
#     base_xpath = "/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/app-form/form/div[2]/div[2]/div/div[1]/app-list/div/div[3]/table/tbody/tr[{}]/td[1]/label/span"
#     # Format the XPath to include the current row index
#     checkbox_xpath = base_xpath.format(row_index)

#     # Locate and click the checkbox
#     checkbox = driver.find_element(By.XPATH, checkbox_xpath)
#     checkbox.click()



# Define the function to find a matching row based on given criteria
def find_matching_row(df, criteria, match_threshold=0.5):
    """
    Finds the row index in df that matches most of the key-value pairs in criteria.
    Compares column names in a case-insensitive and whitespace-insensitive manner.
    Returns -1 if no match is found.
    
    Parameters:
    - df (DataFrame): DataFrame to search within.
    - criteria (dict): Dictionary of criteria with column-value pairs.
    - match_threshold (float): Minimum proportion of criteria that must match (default is 0.5 for 50%).

    Returns:
    - index (int): The index of the matching row or -1 if no match is found.
    """
    # Standardize the column names by applying lower() and strip()
    df.columns = df.columns.str.lower().str.strip()
    criteria = {key.lower().strip(): value for key, value in criteria.items()}
    
    # Iterate over each row and check if it matches the criteria
    for index, row in df.iterrows():
        match_count = 0
        total_criteria = len(criteria)
        
        for key, value in criteria.items():
            # Check if the column exists in the row and matches the criteria
            if key in row and row[key] == value:
                match_count += 1

        # Calculate the match ratio
        match_ratio = match_count / total_criteria

        # Check if match ratio meets the threshold
        if match_ratio >= match_threshold:
            return index

    return -1  # Return -1 if no matching row is found



# Define the function to click a checkbox by row index using multiple base XPath patterns
def click_checkbox_by_row(driver, row_index):
    """
    Clicks the checkbox in the specified row index of the table.
    Tries multiple base XPath patterns until successful.
    Assumes the row index is 1-based (for XPath purposes).
    """
    base_xpaths = [
        "/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/app-form/form/div[2]/div[2]/div/div[1]/app-list/div/div[3]/table/tbody/tr[{}]/td[1]/label/span",
        "/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/app-list/div/div[3]/table/tbody/tr[{}]/td[1]/label/span"
    ]

    for base_xpath in base_xpaths:
        checkbox_xpath = base_xpath.format(row_index)
        try:
            checkbox = driver.find_element(By.XPATH, checkbox_xpath)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
            checkbox.click()
            print(f"Successfully clicked checkbox at row {row_index} using XPath: {checkbox_xpath}")
            time.sleep(2)
            return  # Exit function once clicked successfully
        except (NoSuchElementException, ElementNotInteractableException) as e:
            print(f"Could not click checkbox at row {row_index} using XPath: {checkbox_xpath}. Error:")
    print(f"Failed to click checkbox at row {row_index} after trying all base XPaths.")
    
    
def extract_text(driver, xpaths, max_retries=3, retry_delay=1, waittime=3):
    """
    Attempts to extract text from the first successfully located element among a list of XPaths.
    
    Parameters:
    driver (WebDriver): The Selenium WebDriver instance.
    xpaths (list): List of XPath strings to attempt.
    max_retries (int): Maximum number of retries if element is not found.
    retry_delay (int): Delay in seconds between retries.
    
    Returns:
    str or bool: Text of the first located element, or False if none are found.
    """
    for xpath in xpaths:
        attempts = 0
        while attempts < max_retries:
            try:
                element = WebDriverWait(driver, waittime).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                print(f"Successfully extracted text from XPath {xpath}")
                return element.text
            except Exception as e:
                attempts += 1
                print(f"Attempt {attempts}: Error extracting text for XPath {xpath} -")
                if attempts < max_retries:
                    print(f"Retrying XPath {xpath} in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to extract text for XPath {xpath} after {max_retries} attempts.")
                    
    print("All XPaths failed after max retries.")
    return False





def get_all_xpaths(driver):
    # Use JavaScript to get all elements' XPaths on the page
    xpaths = driver.execute_script("""
        let elements = document.querySelectorAll('*');
        let paths = [];
        elements.forEach((el) => {
            let path = '';
            for (; el && el.nodeType === 1; el = el.parentNode) {
                let index = 0;
                for (let sibling = el.previousSibling; sibling; sibling = sibling.previousSibling) {
                    if (sibling.nodeType === 1 && sibling.tagName === el.tagName) {
                        index++;
                    }
                }
                let tagName = el.tagName.toLowerCase();
                path = '/' + tagName + (index ? '[' + (index + 1) + ']' : '') + path;
            }
            paths.push(path);
        });
        return paths;
    """)
    return xpaths









def is_arabic(text):
    # Check if any character in the text falls within the Arabic Unicode range
    return any('\u0600' <= char <= '\u06FF' for char in text)



def application_details_formatting(text):
       
    # Check if text extraction was successful
    if not text:
        print("Failed to extract application details text.")
        return pd.DataFrame()  # Return an empty DataFrame if text extraction fails

    # Define regex patterns to extract each part of the details
    details_pattern = {
        'Service': r'Service\s+(.+)',
        'Application Number': r'Application Number\s+(\d+)',
        'Application Start Date': r'Application Start Date\s+([0-9\-:, ]+)',
        'On Behalf Of': r'On Behalf Of\s+(.+)',
        'Submit Date': r'Submit Date\s+([0-9\-:, ]+)',
        'Current Inbox': r'Current Inbox\s+(.+)'
    }

    # Extract details using regex patterns
    details = {}
    for key, pattern in details_pattern.items():
        match = re.search(pattern, text)
        details[key] = match.group(1) if match else None

    # Convert extracted details into a DataFrame
    details_df = pd.DataFrame([details])
    return details_df



def Getting_Application_Detials(driver,Services_category='ELMS'):

    if Services_category=='ELMS':

        xpath=['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[7]/div[2]/div[1]',
            '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[5]/div[2]/div[1]',
            '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[3]/div[2]/div[1]']
        
    elif Services_category=='Reservation':
        xpath=[
            '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[5]/div[2]/div[2]/div[2]',
            '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[5]/div[2]/div[2]']
    
        
    # Attempt to extract text using the provided XPaths
    text = extract_text(driver, xpath, max_retries=3, retry_delay=1, waittime=3)
    
    # Check if text extraction was successful
    if not text:
        print("Failed to extract application details text.")
        return pd.DataFrame()  # Return an empty DataFrame if text extraction fails

    # Define regex patterns to extract each part of the details
    details_pattern = {
        'Service': r'Service\s+(.+)',
        'Application Number': r'Application Number\s+(\d+)',
        'Application Start Date': r'Application Start Date\s+([0-9\-:, ]+)',
        'On Behalf Of': r'On Behalf Of\s+(.+)',
        'Submit Date': r'Submit Date\s+([0-9\-:, ]+)',
        'Current Inbox': r'Current Inbox\s+(.+)'
    }

    # Extract details using regex patterns
    details = {}
    for key, pattern in details_pattern.items():
        match = re.search(pattern, text)
        details[key] = match.group(1) if match else None

    # Convert extracted details into a DataFrame
    details_df = pd.DataFrame([details])
    return details_df







# def Getting_Application_From_Inbox(driver,application_number,tab_name,Dashbord_URL='https://shelmstest.adm.gov.ae/private#dashboard'):

#     completed_tab_xpath=['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[4]/div[2]/application-list/div/div[1]/div/a[4]']
#     completed_tab_text=['Completed']

#     INbox_tab_xpath=['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[4]/div[2]/application-list/div/div[1]/div/a[2]']
#     INbox_tab_text=['My Inbox']

#     Pending_tab_xpath=['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[4]/div[2]/application-list/div/div[1]/div/a[3]']
#     Pending_tab_text=['Pending']

#     loading_xpath = '/html/body/div[3]/div[1]/div[2]/div[3]'

#     application_field_searchxpath=['//html/body/div[3]/div[1]/div[2]/div[4]/div/div/div[1]/div/div[2]/div/form/div[1]/div',
#                                   '//*[@id="inbox_filters_1"]']
    

#     Search_button_xpath=[
#                         '//*[@id="inbox_filters"]/div[8]/div/button',
#                         '/html/body/div[3]/div[1]/div[2]/div[4]/div/div/div[1]/div/div[2]/div/form/div[7]/div/button',
#                         '/html/body/div[3]/div[1]/div[2]/div[4]/div/div/div[1]/div/div[2]/app-form/form/div[2]/div/div/button/span',
#                         '/html/body/div[3]/div[1]/div[2]/div[4]/div/div/div[1]/div/div[2]/app-form/form/div[2]/div/div/button',
#                         '/html/body/div[3]/div[1]/div[2]/div[4]/div/div/div[1]/div/div[2]/app-form/form/div[2]/div/div/button/i',
#                         '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[4]/div[1]/div/div[2]/div/form/div[5]/div/button',
#                         '']




#     driver.get(Dashbord_URL)


#     wait_for_page_to_load(driver, loading_xpath)




#     if tab_name =='completed':
#         clicking_on_element_by_all_option(driver, completed_tab_xpath, completed_tab_text, max_retries=1, timeout=5, scroll=True)




#     if tab_name =='pending':
#         clicking_on_element_by_all_option(driver, Pending_tab_xpath, Pending_tab_text, max_retries=1, timeout=5, scroll=True)

#     if tab_name =='Inbox':
#         clicking_on_element_by_all_option(driver, INbox_tab_xpath, INbox_tab_text, max_retries=1, timeout=5, scroll=True)


    

#     time.sleep(3)
#     Input_text_data='Testing from automation'

#     input_data_by_all_option(driver, application_field_searchxpath, [''], application_number,

#                              'test',max_attempts=3, timeout=10, scroll=False,input_delay=2)

#     wait_for_page_to_load(driver, loading_xpath)



#     clicking_on_element_by_all_option(driver, Search_button_xpath, [' Search ','Seearch','search','SEARCH'], max_retries=4, timeout=5, scroll=True)
#     time.sleep(3)
#     wait_for_page_to_load(driver, loading_xpath)

#     clicking_on_element_by_all_option(driver, [''], [application_number], max_retries=4, timeout=5, scroll=True)

#     time.sleep(3)


def Getting_Application_From_Inbox(driver, application_number, tab_name, environment='default', Dashbord_URL='https://shelmstest.adm.gov.ae/private#dashboard'):
    """
    Function to retrieve an application from the inbox with environment-specific handling.

    Args:
        driver: Selenium WebDriver instance.
        application_number: Application number to search.
        tab_name: Name of the tab to select (e.g., 'completed', 'pending', 'Inbox').
        environment: Specifies the environment ('ELMS' or 'default'). Default is 'default'.
        Dashbord_URL: URL for the dashboard. Default is provided.

    """
    # Common XPaths
    completed_tab_xpath = ['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[4]/div[2]/application-list/div/div[1]/div/a[4]']
    completed_tab_text = ['Completed']
    
    INbox_tab_xpath = ['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[4]/div[2]/application-list/div/div[1]/div/a[2]']
    INbox_tab_text = ['My Inbox']
    
    Pending_tab_xpath = ['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[4]/div[2]/application-list/div/div[1]/div/a[3]']
    Pending_tab_text = ['Pending']
    
    loading_xpath = '/html/body/div[3]/div[1]/div[2]/div[3]'
    
    application_field_searchxpath = [
        '//html/body/div[3]/div[1]/div[2]/div[4]/div/div/div[1]/div/div[2]/div/form/div[1]/div',
        '//*[@id="inbox_filters_1"]'
    ]
    
    Search_button_xpath = [
        '//*[@id="inbox_filters"]/div[8]/div/button',
        '/html/body/div[3]/div[1]/div[2]/div[4]/div/div/div[1]/div/div[2]/div/form/div[7]/div/button',
        '/html/body/div[3]/div[1]/div[2]/div[4]/div/div/div[1]/div/div[2]/app-form/form/div[2]/div/div/button/span',
        '/html/body/div[3]/div[1]/div[2]/div[4]/div/div/div[1]/div/div[2]/app-form/form/div[2]/div/div/button',
        '/html/body/div[3]/div[1]/div[2]/div[4]/div/div/div[1]/div/div[2]/app-form/form/div[2]/div/div/button/i',
        '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[4]/div[1]/div/div[2]/div/form/div[5]/div/button',
        ''
    ]
    
    # Environment-specific logic
    if environment == 'ELMS':
        application_number_field_xpath = ['//*[@id="applicationNumber_input"]']
        Search_button_xpath = [
            '//*[@id="datatable_filters"]/app-form/form/div[2]/div/div/button',
            '//*[@id="datatable_filters"]/app-form/form/div[2]/div/div/button/i'
        ]
        search_button_text = [' Search']
        
        # Navigate to the ELMS inbox
        driver.get(Dashbord_URL)
        wait_for_page_to_load(driver, loading_xpath)
        
        # Input application number
        input_data_by_all_option(
            driver, application_number_field_xpath, [''], application_number,
            'test', max_attempts=3, timeout=10, scroll=False, input_delay=2
        )
        
        # Click the search button
        clicking_on_element_by_all_option(
            driver, Search_button_xpath, search_button_text, max_retries=5
        )

        wait_for_page_to_load(driver, loading_xpath)


        clicking_on_element_by_all_option(driver, [''], [application_number], max_retries=4, timeout=5, scroll=True)


    else:
        # Default environment flow
        driver.get(Dashbord_URL)
        wait_for_page_to_load(driver, loading_xpath)
        
        if tab_name == 'completed':
            clicking_on_element_by_all_option(driver, completed_tab_xpath, completed_tab_text, max_retries=1, timeout=5, scroll=True)
        elif tab_name == 'pending':
            clicking_on_element_by_all_option(driver, Pending_tab_xpath, Pending_tab_text, max_retries=1, timeout=5, scroll=True)
        elif tab_name == 'Inbox':
            clicking_on_element_by_all_option(driver, INbox_tab_xpath, INbox_tab_text, max_retries=1, timeout=5, scroll=True)
        
        time.sleep(3)
        
        input_data_by_all_option(
            driver, application_field_searchxpath, [''], application_number,
            'test', max_attempts=3, timeout=10, scroll=False, input_delay=2
        )
        
        wait_for_page_to_load(driver, loading_xpath)
        
        clicking_on_element_by_all_option(
            driver, Search_button_xpath, [' Search ', 'Seearch', 'search', 'SEARCH'], max_retries=4, timeout=5, scroll=True
        )
        time.sleep(3)
        wait_for_page_to_load(driver, loading_xpath)
        
        clicking_on_element_by_all_option(
            driver, [''], [application_number], max_retries=4, timeout=5, scroll=True
        )
        time.sleep(3)



def create_vertical_snake_text(text, wave_length=3):
    """
    Creates a vertical "snake" or wave pattern for the given text, one character per line.
    
    Parameters:
    - text: The original text to be transformed.
    - wave_length: Number of spaces to increase and decrease to form the wave shape.
    
    Returns:
    - A string with a vertical "snake" pattern.
    """
    snake_text = ""
    space_count = 0
    increasing = True

    for char in text:
        # Add spaces before the character to create the wave effect
        snake_text += " " * space_count + char + "\n"
        
        # Adjust space count for the wave pattern
        if increasing:
            space_count += 1
            if space_count == wave_length:
                increasing = False
        else:
            space_count -= 1
            if space_count == 0:
                increasing = True

    return snake_text





def GCS_payment(driver,application_number):
    # application_number=str(application_number)

    # Assuming you have a driver instance created with Selenium
    step_type = "payment with GCS"  # Replace with the actual step type
    action_type = "click"  # Replace with the actual action type
    GCS_local_URL='http://10.24.16.86:7001/ords/f?p=100'
    username=['c.mohammed.alia']
    password= ['1']

    driver.get(GCS_local_URL)




    Username_xpath=['//*[@id="P101_USERNAME"]']
    PASSWORD_xpath=['//*[@id="P101_PASSWORD"]']

    input_data_by_all_option(driver, Username_xpath, [''], username,

                             'test',max_attempts=3, timeout=10, scroll=False,input_delay=2)


    input_data_by_all_option(driver, PASSWORD_xpath, [''], password,

                             'test',max_attempts=3, timeout=10, scroll=False,input_delay=2)




    login_xpath=['/html/body/form/div[2]/main/div/div/div/div/div[3]/button/span',
                '/html/body/form/div[2]/main/div/div/div/div/div[3]',
                '//*[@id="B106346667283935699"]',
                '']

    clicking_on_element_by_all_option(driver, login_xpath, ['Login','login','LOGIN'], max_retries=4, timeout=5, scroll=True)



    clicking_on_element_by_all_option(driver, [], ['التحصيل العام GCS'], max_retries=4, timeout=5, scroll=True)





    time.sleep(3)
    clicking_on_element_by_all_option(driver, [], ['الصندوق (دفع المعاملات)'], max_retries=4, timeout=5, scroll=True)




    Application_Input_GCS_for_pay=['//*[@id="P18_APLC_NO"]',
                                  '/html/body/form/div[1]/div/div[2]/main/div[2]/div/div/div/div[2]/div/div[2]/div[2]/div/div/div[1]/div/div[2]/div']


    input_data_by_all_option(driver, Application_Input_GCS_for_pay, [''], application_number,

                             'test',max_attempts=3, timeout=10, scroll=False,input_delay=2)


    GCS_application_search_buttonxpath=['//*[@id="B121349173117055956"]',
                                       '/html/body/form/div[1]/div/div[2]/main/div[2]/div/div/div/div[2]/div/div[3]/button[1]/span',
                                       '']

    clicking_on_element_by_all_option(driver, GCS_application_search_buttonxpath, ['بحث '], max_retries=4, timeout=5, scroll=True)

    # Locate the table body and get all rows
    table_rows = driver.find_elements(By.XPATH, "/html/body/form/div[1]/div/div[2]/main/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div/div[1]/table/tbody/tr")

    # List to store each row's data
    data = []

    # Iterate over each row and parse the text into structured data
    for i, row in enumerate(table_rows, start=1):
        row_text = row.text.strip()

        # Split text based on common patterns found in the sample output
        if "الدفع الجديد" in row_text:
            parts = row_text.split()
            data.append({
                "Row": i,
                "Target": parts[0],
                "Application Number": parts[1],
                "Transaction Date": parts[2],
                "Payee Name": " ".join(parts[3:7]),  # Payee Name spans multiple words
                "Amount": parts[7],
                "Fee Description": parts[8],
                "Receipt Type": parts[9],
                "Payment Term": parts[10]
            })
        elif len(row_text.split()) == 1:  # For rows like Row 3
            data.append({
                "Row": i,
                "Target": row_text,
                "Application Number": None,
                "Transaction Date": None,
                "Payee Name": None,
                "Amount": None,
                "Fee Description": None,
                "Receipt Type": None,
                "Payment Term": None
            })

    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=["Row", "Target", "Application Number", "Transaction Date",
                                     "Payee Name", "Amount", "Fee Description", "Receipt Type", "Payment Term"])



    # Populate payment_xpath_buttons list with dynamically found XPaths
    payment_xpath_buttons = []
    i = 1  # Starting index
    while True:
        try:
            # Define the dynamic XPath with the current index `i`
            xpath = f'/html/body/form/div[1]/div/div[2]/main/div[2]/div/div/div/div[3]/div[2]/div[2]/div/div/div/div[1]/table/tbody/tr[{i}]/td[1]/h3/a'

            # Try to find the element by XPath
            element = driver.find_element(By.XPATH, xpath)

            # Add the found element's XPath to the list
            payment_xpath_buttons.append(xpath)

            # Print the XPath or any desired information
            print(f"Found element at XPath: {xpath}")

            # Increment to check the next row
            i += 1
        except:
            # Break the loop if the element does not exist
            print(f"No element found at index {i}. Ending loop.")
            break

    # Loop through each payment button's XPath
    for xpath in payment_xpath_buttons:
        print('---------------------------------------------------------------------------------------')
        # Attempt to click the payment button to open the pop-up
        print("Clicking payment button at XPath:", xpath)
        clicking_on_element_by_all_option(driver, [xpath], [''], max_retries=4, timeout=5, scroll=True)
        time.sleep(2)  # Wait for the pop-up to open

        # Get XPaths before and after clicking to detect new elements
        xpaths_before =  get_all_xpaths(driver)
        xpaths_after =  get_all_xpaths(driver)
        new_xpaths = set(xpaths_after) - set(xpaths_before)
        print("New XPaths after popup:", new_xpaths)

        # Check for iframes in the pop-up
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframe(s) after popup opened.")

        target_found = False
        for i, iframe in enumerate(iframes):
            driver.switch_to.frame(iframe)
            print(f"Switched to iframe {i + 1}.")

            # Check if the target element is in the iframe
            try:
                target_element = driver.find_element(By.ID, "P40008_PAYMENT_METHOD")
                print("Target element found in iframe!")
                target_element.click()
                target_found = True
                break
            except Exception as e:
                print(f"Target element not found in iframe {i + 1}:")

            # Switch back to main content before checking next iframe
            driver.switch_to.default_content()

        if not target_found:
            print("Target element not found in any iframe.")

        # Interact with elements in the pop-up
        clicking_on_element_by_all_option(driver, [], ['نقدي'], max_retries=4, timeout=5, scroll=False)
        time.sleep(0.4)
        clicking_on_element_by_all_option(driver, [], ['دفع'], max_retries=4, timeout=5, scroll=False)
        time.sleep(0.4)

        # Define the XPath for the element to check if it's already paid
        already_paid_flagxpath = ['/html/body/form/div/div[2]/div/div/span[2]/div/div/div/div[2]/div']
        already_paid_status = extract_text(driver, already_paid_flagxpath, max_retries=2, retry_delay=0.5)

        successfully_flagxpath = [
            '/html/body/form/div/div[2]/div/div/span[1]/div/div/div/div[2]/div/h2',
            '/html/body/form/div/div[2]/div/div/span[1]/div/div/div/div[2]/div'
        ]
        successfully_paid_status = extract_text(driver, successfully_flagxpath, max_retries=2, retry_delay=0.5)

        popup_back = [
            '//*[@id="B173701938953932846"]',
            '/html/body/form/div/div[2]/div/div/div/div[2]/div/div/div[2]/div[3]/div[1]/button/span'
        ]
        time.sleep(3)

        # Check if the text indicates that the transaction is already paid
        if already_paid_status:
            print("Already paid, clicking on back...")
            # Click the 'Back' button to close the popup and return to the main content
            clicking_on_element_by_all_option(driver, popup_back, ['رجوع'], max_retries=4, timeout=2, scroll=True)
            time.sleep(1)
            driver.switch_to.default_content()  # Return to main content
            time.sleep(1)

        elif successfully_paid_status:
            print("Payment Successful, clicking on back...")
            time.sleep(3)
            clicking_on_element_by_all_option(driver, popup_back, ['رجوع'], max_retries=4, timeout=2, scroll=True)
            driver.switch_to.default_content()  # Return to main content

        else:
            # In case neither already paid nor successful flag is found, click back
            time.sleep(3)
            clicking_on_element_by_all_option(driver, popup_back, ['رجوع'], max_retries=4, timeout=2, scroll=True)
            driver.switch_to.default_content()

    print("Finished processing all payment buttons.")






# Define the individual steps as separate functions

def enter_municipality(driver, municipality_xpath, municipality_name, Land_use_Input_xpath, first_option_dropdownlist):
    print('=======Enter municipality')
    clicking_on_element_by_all_option(driver, municipality_xpath, [''], max_retries=5)
    input_data_by_all_option(driver, Land_use_Input_xpath, [''], municipality_name, 
                                  calender_date=None, max_attempts=3, timeout=10, scroll=False, input_delay=2, field_type='others')
    clicking_on_element_by_all_option(driver, first_option_dropdownlist, [''], max_retries=5)
    time.sleep(2)

def enter_plot_number(driver, plot_number_xpath, plot_number):
    print('=======Enter Plot Number')
    input_data_by_all_option(driver, plot_number_xpath, [''], plot_number, 
                                  calender_date=None, max_attempts=3, timeout=10, scroll=False, input_delay=2, field_type='Text_field')
    time.sleep(4)

def enter_district_or_zone(driver, districtId_zone_xpath, District_zone_input, Land_use_Input_xpath, first_option_dropdownlist):
    print('=======Enter district or zone')
    clicking_on_element_by_all_option(driver, districtId_zone_xpath, [''], max_retries=5)
    input_data_by_all_option(driver, Land_use_Input_xpath, [''], [District_zone_input], 
                                  calender_date=None, max_attempts=3, timeout=10, scroll=False, input_delay=2, field_type='others')
    clicking_on_element_by_all_option(driver, first_option_dropdownlist, [''], max_retries=5)
    time.sleep(1)

def enter_land_use(driver, land_use_xpath, Land_use_Input_xpath, Land_use, first_option_dropdownlist):
    print('=======Enter Land Use')
    clicking_on_element_by_all_option(driver, land_use_xpath, [''], max_retries=5)
    time.sleep(2)
    input_data_by_all_option(driver, Land_use_Input_xpath, [''], [Land_use], 
                                  calender_date=None, max_attempts=3, timeout=10, scroll=False, input_delay=2, field_type='others')
    time.sleep(2)
    clicking_on_element_by_all_option(driver, first_option_dropdownlist, [''], max_retries=5)

# Main function to execute the sequence of steps
def Search_by_plot(driver, plot_number, District_zone_input, Land_use,double_click_option=False):
    # Define XPaths and input variables
    plot_tab_xpath = ['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/div[2]/ul/li[3]/a',
                      '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/div[2]/ul/li[3]',
                      '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/app-form/form/div[2]/div[2]/ul/li[3]',
                      '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/app-form/form/div[2]/div[2]/ul/li[3]/a']
    municipality_xpath = ['//*[@id="select2-municipalityId_input-container"]','//*[@id="select2-municipalityId_input-container"]']
    municipality_name = ['Abu Dhabi']
    plot_number_xpath = ['//*[@id="plotNumber_input"]']
    districtId_zone_xpath = ['//*[@id="select2-districtId_input-container"]']
    land_use_xpath = ['//*[@id="select2-landuseId_input-container"]']
    Land_use_Input_xpath = ['/html/body/span/span/span[1]/input', '/html/body/span/span/span[1]']
    first_option_dropdownlist = ['/html/body/span/span/span[2]/ul/li[1]']

    # Click on "Search By Plot" tab
    clicking_on_element_by_all_option(driver, plot_tab_xpath, ['Search By Plot'], max_retries=5)

    # Execute each entry step in sequence
    enter_municipality(driver, municipality_xpath, municipality_name, Land_use_Input_xpath, first_option_dropdownlist)
    enter_plot_number(driver, plot_number_xpath, plot_number)
    enter_district_or_zone(driver, districtId_zone_xpath, District_zone_input, Land_use_Input_xpath, first_option_dropdownlist)
    enter_land_use(driver, land_use_xpath, Land_use_Input_xpath, Land_use, first_option_dropdownlist)

    Search_button_xpath=['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/div[2]/div/div[3]/app-list/app-form/form/div[2]/div[2]/div/button[2]',
                    '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/div[2]/div/div[3]/app-list/app-form/form/div[2]/div[2]/div/button[2]/i',
                    '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/app-form/form/div[2]/div[2]/div/div[3]/app-list/app-form/form/div[2]/div[2]/div/button[2]',
                    '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/app-form/form/div[2]/div[2]/div/div[3]/app-list/app-form/form/div[2]/div[2]/div/button[2]/i']

    Search_text=['Search']
    if double_click_option:
        clicking_on_element_by_all_option(driver, Search_button_xpath,Search_text, max_retries=5)
        clicking_on_element_by_all_option(driver, Search_button_xpath,Search_text, max_retries=5)
    else:
        
        clicking_on_element_by_all_option(driver, Search_button_xpath,Search_text, max_retries=5)







def search_by_owner(driver, EID_persona):
    # Define XPaths and other variables
    loading_xpath = '/html/body/div[3]/div[1]/div[2]/div[3]'
    search_by_owner_xpaths = [
        '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div[1]/div[2]/ul/li[1]/a',
        '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/app-form/form/div[2]/div[2]/ul/li[1]'
    ]
    EID_search_xpath = '//*[@id="nationalNumber_input"]'
    checkbox_xpaths = [
        '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div/app-form/form/div[2]/div[2]/div/div[1]/app-list/div/div[2]/table/tbody/tr/td[1]/label',
        '/html/body/div[3]/div[1]/div[2]/div[4]/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/app-list/div/div[2]/table/tbody/tr/td[1]/label'
    ]

 
    # Click on "Search by Owner" tab
    clicking_on_element_by_all_option(driver, search_by_owner_xpaths, ['Search Owner'], max_retries=5)
    wait_for_page_to_load(driver, loading_xpath)

    # Enter EID in the search field and submit
    input_data_by_all_option(driver, [EID_search_xpath], [''], [EID_persona], 
                                  calender_date=None, max_attempts=3, timeout=10, scroll=False, input_delay=2, field_type='Text_field')
    input_field = driver.find_element(By.XPATH, EID_search_xpath)
    input_field.send_keys(Keys.ENTER)
    time.sleep(2)

    # Select the first checkbox
    clicking_on_element_by_all_option(driver, checkbox_xpaths, [' '], max_retries=5, timeout=5, scroll=True)
    wait_for_page_to_load(driver, loading_xpath)


    return (True)





def Getting_data_from_Owner_search(driver):
        # Example usage
    xpaths = {
        "Land Use": [
            "//table[@class='table table-striped table-bordered table-hover']//td[@data-bind='text: landUseName']",
            "//table[@class='table table-hover']//td[@data-bind='text: landUseName']"
        ],
        "District": [
            "//table[@class='table table-striped table-bordered table-hover']//td[@data-bind='text: districtName']",
            "//table[@class='table table-hover']//td[@data-bind='text: districtName']"
        ],
        "Community": [
            "//table[@class='table table-striped table-bordered table-hover']//td[@data-bind='text: communityName']",
            "//table[@class='table table-hover']//td[@data-bind='text: communityName']"
        ],
        "Road": [
            "//table[@class='table table-striped table-bordered table-hover']//td[@data-bind='text: roadName']",
            "//table[@class='table table-hover']//td[@data-bind='text: roadName']"
        ],
        "Plot Number": [
            "//table[@class='table table-striped table-bordered table-hover']//td[@data-bind='text: plotNumber']",
            "//table[@class='table table-hover']//td[@data-bind='text: plotNumber']"
        ],
        "Status Block": [
            "//table[@class='table table-striped table-bordered table-hover']//span[@data-bind='if: hasBlock']",
            "//table[@class='table table-hover']//span[@data-bind='if: hasBlock']"
        ],
        "Status Mortgage": [
            "//table[@class='table table-striped table-bordered table-hover']//span[@data-bind='if: hasMortgage']",
            "//table[@class='table table-hover']//span[@data-bind='if: hasMortgage']"
        ],
        "Checkbox": [
            "//table[@class='table table-striped table-bordered table-hover']//input[@type='checkbox']",
            "//table[@class='table table-hover']//input[@type='checkbox']"
        ]
    }

    # Initialize data dictionary for each column
    table_data = {column: [] for column in xpaths}
    max_rows = 0  # To ensure consistent DataFrame length

    # Loop through each column and fetch data
    for column, paths in xpaths.items():
        elements = []
        for path in paths:
            elements = driver.find_elements(By.XPATH, path)
            if elements:
                break

        max_rows = max(max_rows, len(elements))

        # Collect data based on element type
        if column == "Checkbox":
            table_data[column] = [element.is_selected() for element in elements]
        elif column in ["Status Block", "Status Mortgage"]:
            table_data[column] = ["Has Status" if element.is_displayed() else "No Status" for element in elements]
        else:
            table_data[column] = [element.text for element in elements]

    # Fill missing rows for consistent DataFrame structure
    for column in table_data:
        while len(table_data[column]) < max_rows:
            table_data[column].append(None)

    # Convert to DataFrame and filter for "Industrial Land"
    df_SH_ELMS = pd.DataFrame(table_data)
# industrial_lands = df_SH_ELMS[df_SH_ELMS['Land Use'] == 'Industrial Land']

    return df_SH_ELMS




def get_element_with_retries(row, xpath, max_retries=3, delay=1):
    """
    Attempts to find an element with retries.
    
    Parameters:
    - row: Selenium WebElement representing the row
    - xpath: XPath string to locate the element within the row
    - max_retries: Maximum number of retries to locate the element
    - delay: Delay between retries (in seconds)
    
    Returns:
    - element.text if element is found, else an empty string
    """
    for attempt in range(max_retries):
        try:
            element = row.find_element(By.XPATH, xpath)
            return element.text if element else ""
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print(f"Failed to locate element with XPath '{xpath}' after {max_retries} attempts.")
                return ""

def Getting_data_from_plot_search(driver):
    # Define the XPath for each row in the table
    table_rows_xpath = "//tr[contains(@data-bind, 'item')]"  # Adjust if necessary

    # Initialize an empty list to store row data
    table_data = []

    # Find each row of the table and extract the relevant information
    rows = driver.find_elements(By.XPATH, table_rows_xpath)
    for row in rows:
        try:
            # Extract data for each column in the row, including the checkbox status
            row_data = {
                "checkbox_selected": row.find_element(By.XPATH, "./td[1]/label/input").is_selected(),
                "municipalityName": get_element_with_retries(row, "./td[2]"),
                "districtName": get_element_with_retries(row, "./td[3]"),
                "communityName": get_element_with_retries(row, "./td[4]"),
                "roadName": get_element_with_retries(row, "./td[5]"),
                "plotNumber": get_element_with_retries(row, "./td[6]"),
                "landUseName": get_element_with_retries(row, "./td[7]"),
                "hasBlock": "Yes" if row.find_element(By.XPATH, "./td[8]/span").is_displayed() else "No",
                "hasMortgage": "Yes" if row.find_element(By.XPATH, "./td[9]/span").is_displayed() else "No"
            }
            table_data.append(row_data)
        except Exception as e:
            print(f"Error extracting data from row:")

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(table_data)

    # Adjust column names by removing 'Name' and renaming columns for clarity
    df.columns = df.columns.str.replace('Name', '', regex=False)
    df.columns = ['checkbox_selected', 'municipality', 'district', 'community', 'road', 'plot Number', 'Land Use', 'has Block', 'has Mortgage']

    return df






def send_post_requests_for_payloads(df, url, headers, delay=8):
    """
    Iterates over the rows of a DataFrame, sending POST requests with the 'request_payload' 
    field for each row and printing the response.

    Parameters:
    - df (DataFrame): The DataFrame containing 'request_payload' for each request.
    - url (str): The URL to send the POST request to.
    - headers (dict): Headers to include in each POST request.
    - delay (int): Delay in seconds between requests.
    """
    for i in range(len(df['request_payload'])):
        request_payload = df['request_payload'].iloc[i]
        print(f"Request Payload Data ({i+1}/{len(df)}):", request_payload)
        
        # Send the POST request with UTF-8 encoding
        response = requests.post(url, headers=headers, data=request_payload.encode('utf-8'))
        
        # Process and print the response
        response_data = response.text.split(',')
        print("Response Data:", response_data)
        
        # Wait before the next request
        time.sleep(delay)
        print('\n-------------------------------------------------------------\n')




def wait_for_error_to_disappear(driver, maxtrial=20, polling_interval=1, consecutive_not_exists=3):
    """
    Wait for the error message to disappear from the specified XPaths, refreshing the page if the error persists.

    Parameters:
    - driver: Selenium WebDriver instance.
    - xpaths: List of XPaths to check for error message presence.
    - maxtrial: Maximum time (in seconds) to keep checking.
    - polling_interval: Time (in seconds) between checks.
    - consecutive_not_exists: Number of consecutive checks where the error should not exist to confirm disappearance.

    Returns:
    - True if the error disappears within the time limit.
    - False if the error persists or timeout is reached.
    """
            # Define parameters
    xpaths = [
            '//*[@id="app"]/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div',
            '//*[@id="app"]/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div[2]'
        ]

    elapsed_time = 0
    not_exists_count = 0  # Counter for consecutive "not exists"

    while elapsed_time < maxtrial:
        error_found = False

        for xpath in xpaths:
            try:
                # Check if the error message exists
                driver.find_element(By.XPATH, xpath)
                print(f"Error message still exists at: {xpath}. Refreshing the page...")
                error_found = True  # Error still exists
                not_exists_count = 0  # Reset the counter if any error is found
                break  # Exit the loop to avoid unnecessary checks
            except:
                # If the error message is not found, continue checking other XPaths
                pass

        if not error_found:
            not_exists_count += 1
            print(f"Error message not found ({not_exists_count}/{consecutive_not_exists}).")

            # Exit if the error does not exist for the required number of consecutive checks
            if not_exists_count >= consecutive_not_exists:
                print(f"Error message disappeared for {consecutive_not_exists} consecutive checks.")
                return True
        else:
            # Refresh the page if error still exists
            driver.refresh()
            print("Page refreshed to attempt resolving the error.")
            time.sleep(polling_interval)  # Wait after refresh for page reload

        # Increment elapsed time
        elapsed_time += polling_interval

    print(f"Timeout reached. Error message still exists.")
    return False  # Timeout reached and error still exists



########################################################################################################
# def check_data_error_retrieving(driver, retry_params):
#     """
#     Check if there's a data retrieval error by extracting text from the specified elements,
#     retrying with delays after each refresh if an error is detected.

#     Parameters:
#     - driver: Selenium WebDriver instance.
#     - retry_params: Dictionary with retry settings (e.g., {'max_retries': 2, 'retry_delay': 0.5}).

#     Returns:
#     - str: Message indicating whether the error was resolved or persisted.
#     """
#     loading_circle_xpath = '//*[@class="ui-lib-spinner ui-lib-spinner_circle-image"]'

#     # Define parameters
#     dataerror_retriving_xpath = [
#         '//*[@id="app"]/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div[2]/div',
#         '//*[@id="app"]/div/div/div/div[2]/div/div/div/div/div/div/div/div/div/div[2]'
#     ]
#     # Extract text from the specified section
#     dataerror_retriving_xpath=['//*[@id="app"]']


    

    

#     Error_messages= [ 'an error occurred while retrieving the data' ,
#                      "sorry, the page you're looking for can't be found",
#                      "something went wrong",
#                      "حدث خطأ أثناء استرجاع البيانات"]

#     max_retries = retry_params.get('max_retries', 2)
#     retry_delay = retry_params.get('retry_delay', 0.5)

#     print('-----------------------Checking for Data Retrieval Errors-----------------------')

#     for attempt in range(1, max_retries + 1):
#         # Extract text from the specified XPaths
#         dataerror_retriving = extract_text(
#             driver,
#             dataerror_retriving_xpath,
#             max_retries=retry_params.get('max_retries', 2),
#             retry_delay=retry_params.get('retry_delay', 0.5)
#         )


#         if not dataerror_retriving:
#             print(f"No significant data retrieval error detected after {attempt} attempt(s).")
#             return "No significant data retrieval error detected." 

#         # Log the error if detected
#         dataerror_retriving=dataerror_retriving.lower().strip().replace('\n',' ')
#         if any(error_message in dataerror_retriving for error_message in Error_messages)   :
#             print(f"Attempt {attempt}: Yes, there is an Issue")
#             # print(dataerror_retriving)
#         # Refresh the page and delay for retry
#             driver.refresh()
#             wait_for_loading_circle_to_disappear(driver, loading_circle_xpath, maxtrial=50, polling_interval=1, consecutive_not_exists=6)

#             print("Page refreshed. Waiting before the next attempt...")
#             time.sleep(retry_delay)

            


#     print(f"Data retrieval error persists after {max_retries} retries.")
#     return "Data retrieval error persists after retries."

###########################################################################################################################

def check_data_error_retrieving(driver, retry_params):
    """
    Check if there's a data retrieval error by extracting text from the specified elements,
    retrying with delays after each refresh if an error is detected.

    Parameters:
    - driver: Selenium WebDriver instance.
    - retry_params: Dictionary with retry settings (e.g., {'max_retries': 2, 'retry_delay': 0.5}).

    Returns:
    - str: Message indicating whether the error was resolved or persisted.
    """
    # Define parameters
    dataerror_retriving_xpath = ['//*[@id="app"]']
    Error_messages = [
        'an error occurred while retrieving the data',
        "sorry, the page you're looking for can't be found",
        "something went wrong",
        "حدث خطأ أثناء استرجاع البيانات",
        'حدث خطأ أثناء استرجاع البيانات.'
    ]
    loading_circle_xpath = '//*[@class="ui-lib-spinner ui-lib-spinner_circle-image"]'

    max_retries = retry_params.get('max_retries', 2)
    retry_delay = retry_params.get('retry_delay', 0.5)
    retry_count = 0

    print('-----------------------Checking for Data Retrieval Errors-----------------------')

    # Retry loop
    while retry_count < max_retries:
        print(f"Attempt {retry_count + 1} of {max_retries}.")

        # Extract text from the specified XPaths
        try:
            dataerror_retriving = extract_text(
                driver,
                dataerror_retriving_xpath,
                max_retries=2,
                retry_delay=0.5
            )
            # Process the extracted text
            dataerror_retriving = dataerror_retriving.lower().strip().replace('\n', ' ')
        except Exception as e:
            print(f"Error extracting text:")
            retry_count += 1
            continue

        # Check if the error matches any of the known error messages
        if any(error_message in dataerror_retriving for error_message in Error_messages):
            print(f"Error detected: '{dataerror_retriving}'. Refreshing the page.")
            driver.refresh()
            wait_for_loading_circle_to_disappear(driver,loading_circle_xpath,maxtrial=50,polling_interval=1,consecutive_not_exists=6)

            print("Page refreshed. Waiting before the next attempt...")
            time.sleep(retry_delay)
        else:
            print(f"No significant data retrieval error detected on attempt {retry_count + 1}.")
            return "No significant data retrieval error detected."

        # Increment retry counter
        retry_count += 1

    # If all retries are exhausted
    print(f"Data retrieval error persists after {max_retries} attempts.")
    return "Data retrieval error persists after retries."

###########################################################################################################################

def wait_for_loading_circle_to_disappear(driver, xpath, maxtrial=20, polling_interval=1, consecutive_not_exists=3):

    elapsed_time = 0
    not_exists_count = 0  # Counter for consecutive "not exists"

    while elapsed_time < maxtrial:
        try:
            # Check if the loading circle exists
            driver.find_element(By.XPATH, xpath)
            print(f"Loading circle still exists. Waiting...")
            not_exists_count = 0  # Reset the counter if the element is found
        except :
            not_exists_count += 1
            print(f"Loading circle not found ({not_exists_count}/{consecutive_not_exists}).")

            # Exit if the element does not exist for the required number of consecutive checks
            if not_exists_count >= consecutive_not_exists:
                print(f"Loading circle disappeared for {consecutive_not_exists} consecutive checks.")
                return True

        # Increment elapsed time and wait
        time.sleep(polling_interval)
        elapsed_time += polling_interval

    print(f"Timeout reached. Loading circle still exists.")
    return False  # Timeout reached and element still exists


def dismiss_alerts(driver):
    """Dismisses any unexpected alerts."""
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert.dismiss()
        print("Unexpected alert dismissed.")
    except TimeoutException:
        pass  # No alert found, continue


def Skipping_intro_part(driver,wait_time=0.5):
    

    time.sleep(wait_time)
    # Additional clicks with retries, handling alerts
    try:
        first_cont_element = ['/html/body/div[1]/div/div/div/div/div[3]/div[2]/div[2]/div[3]/div/div']
        clicking_on_element_by_all_option(driver, first_cont_element, ['Continue'], max_retries=4, timeout=5, scroll=True)
    except :
        dismiss_alerts(driver)
    time.sleep(wait_time)

    try:
        second_cont_element = ['/html/body/div[1]/div/div/div/div/div[3]/div[2]/div[2]/div[2]/div/div']
        clicking_on_element_by_all_option(driver, second_cont_element, ['Continue'], max_retries=4, timeout=5, scroll=True)
    except :
        dismiss_alerts(driver)
    time.sleep(wait_time)

    try:
        finish_element = ['/html/body/div[1]/div/div/div/div/div[3]/div[2]/div[2]/div[2]/div/div/div']
        clicking_on_element_by_all_option(driver, finish_element, ['Finish'], max_retries=4, timeout=5, scroll=True)
    except :
        dismiss_alerts(driver)
    time.sleep(wait_time)

def set_zoom(driver, zoom_level=70):
    """Sets the browser zoom level using JavaScript."""
    driver.execute_script(f"document.body.style.zoom='{zoom_level}%'")



def wait_for_element(by, value, retries=3, delay=2):
    """Attempts to find an element multiple times."""
    for attempt in range(retries):
        try:
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            print(f"Attempt {attempt + 1} - Element not found: {value}. Retrying in {delay} seconds...")
            time.sleep(delay)
    raise TimeoutException(f"Element not found after {retries} attempts: {value}")



# def extract_email_data(email_text):
#     # Normalize line breaks
#     email_text = email_text.replace('\r\n', '\n')

#     data = {
#         'application_number': None,
#         'status': None,
#         'service_name_en': None,
#         'service_name_ar': None,
#         'username_en': None,
#         'username_ar': None,
#         'link_en': None,
#         'link_ar': None
#     }
    
#     # Debugging: Print the first 500 characters to identify patterns

#     # Extract application number
#     app_num_match = re.search(r"Application Number: (\d+)", email_text)
#     if app_num_match:
#         data['application_number'] = app_num_match.group(1)
#     else:
#         print("Application number not found.")

#     # Extract status
#     status_match = re.search(r"Status is ([\w\s]+)", email_text)
#     if status_match:
#         data['status'] = status_match.group(1).strip()
#     else:
#         print("Status not found.")

#     # Extract service name in English and Arabic
#     service_en_match = re.search(r"Service Name: ([^\n]+)", email_text)
#     if service_en_match:
#         data['service_name_en'] = service_en_match.group(1).strip()
#     else:
#         print("Service name (English) not found.")

#     service_ar_match = re.search(r"اسم الخدمة: ([^\n]+)", email_text)
#     if service_ar_match:
#         data['service_name_ar'] = service_ar_match.group(1).strip()
#     else:
#         print("Service name (Arabic) not found.")

#     # Extract username in English and Arabic
#     username_en_match = re.search(r"Hello ([^,]+),", email_text)
#     if username_en_match:
#         data['username_en'] = username_en_match.group(1).strip()
#     else:
#         print("Username (English) not found.")

#     username_ar_match = re.search(r"أهلاً بك ([^،]+)", email_text)
#     if username_ar_match:
#         data['username_ar'] = username_ar_match.group(1).strip()
#     else:
#         print("Username (Arabic) not found.")

#     # Extract links in English
#     link_en_patterns = [
#         r"please click on: (https?://[^\s]+)",
#         r"kindly click on: (https?://[^\s]+)",
#         r"kindly complete the payment (https?://[^\s]+)",
#         r"kindly complete the payment: (https?://[^\s]+)",
#     ]
#     for pattern in link_en_patterns:
#         match = re.search(pattern, email_text)
#         if match:
#             data['link_en'] = match.group(1).strip()
#             break
#     if not data['link_en']:
#         print("English link not found.")

#     # Extract links in Arabic
#     link_ar_patterns = [
#         r"يُرجى زيارة: (https?://[^\s]+)",
#         r"عبر زيارة: (https?://[^\s]+)",
#         r"الدفع عبر الرابط التالي: (https?://[^\s]+)"
#     ]
#     for pattern in link_ar_patterns:
#         match = re.search(pattern, email_text)
#         if match:
#             data['link_ar'] = match.group(1).strip()
#             break
#     if not data['link_ar']:
#         print("Arabic link not found.")

#     # Debugging: Show extracted data
# #     print("Extracted data:", data)

#     return data


# def extract_email_data(email_text):
#     # Normalize line breaks
#     email_text = email_text.replace('\r\n', '\n')

#     data = {
#         'application_number': None,
#         'status': None,
#         'service_name_en': None,
#         'service_name_ar': None,
#         'username_en': None,
#         'username_ar': None,
#         'link_en': None,
#         'link_ar': None,
#         'content_message_en': None,
#         'content_message_ar': None,
#         'complete_application_instruction_en': None,
#         'complete_application_instruction_ar': None,
#         'required_action_en': None,
#         'required_action_ar': None
#     }

#     # required_action_en = "Required Action: You need to complete the application details in order to proceed."
#     # required_action_ar = "الإجراء المطلوب: يُرجى استكمال المعاملة لمتابعة تقديم طلبك."

#     # Extract details from the email text using regular expressions
#     details = {
#         'application_number': re.search(r"Application Number: (\d+)", email_text),
#         'status': re.search(r"Status is ([\w\s]+)", email_text),
#         'service_name_en': re.search(r"Service Name: ([^\n]+)", email_text),
#         'service_name_ar': re.search(r"اسم الخدمة: ([^\n]+)", email_text),
#         'username_en': re.search(r"Hello ([^,]+),", email_text),
#         'username_ar': re.search(r"أهلاً بك\s*([^،,]+)\s*[،,]", email_text),
#     }
#     print(details['username_ar'])

#     # Update data dictionary with extracted information
#     for key, match in details.items():
#         if match:
#             data[key] = match.group(1).strip()

#     # Define patterns to capture links and content messages
#     link_patterns = {
#         'link_en': [
#             r"please click on: (https?://[^\s]+)",
#             r"kindly click on: (https?://[^\s]+)",
#             r"kindly complete the payment (https?://[^\s]+)",
#             r"kindly complete the payment: (https?://[^\s]+)"
#         ],
#         'link_ar': [
#             r"يُرجى زيارة: (https?://[^\s]+)",
#             r"عبر زيارة: (https?://[^\s]+)",
#             r"الدفع عبر الرابط التالي: (https?://[^\s]+)"
#         ]
#     }

#     # Extract links
#     for key, patterns in link_patterns.items():
#         for pattern in patterns:
#             match = re.search(pattern, email_text)
#             if match:
#                 data[key] = match.group(1).strip()
#                 break

#     # Extract content messages
#     if data['username_en']:
#         content_message_en_match = re.search(rf"Hello {data['username_en']},(.+?)Service Name:", email_text, re.DOTALL)
#         if content_message_en_match:
#             data['content_message_en'] = clean_text(content_message_en_match.group(1).strip(),'english')
#             print(data['content_message_en'] )
    
#     if data['username_ar']:
#         print(data['username_ar'])
#         content_message_ar_match = re.search(rf"أهلاً بك {data['username_ar']}،(.+?)اسم الخدمة:", email_text, re.DOTALL)
#         if content_message_ar_match:
#             data['content_message_ar'] = clean_text(content_message_ar_match.group(1).strip(),'arabic')
#             data['content_message_ar'] = re.sub(r'\s+', ' ', data['content_message_ar']).strip()

#             print(data['content_message_ar'] )
            
            
#     # Check for "Pending Action" and add required action with bold text
#     if data['status'] and "Pending Action" in data['status']:
#         data['required_action_en'] = (
#             "<strong>Required Action:</strong> You need to complete the application details in order to proceed."
#         )
#         data['required_action_ar'] = (
#             "<strong>الإجراء المطلوب:</strong> يُرجى استكمال المعاملة لمتابعة تقديم طلبك."
#         )
#     else:
#         data['required_action_en'] = None
#         data['required_action_ar'] = None



#     # Extract complete application instructions for English
#     if data['application_number']:

        
#         instruction_en_match = re.search(
#             r"(To complete your application|For more information)(.+?)http",
#             email_text,
#             re.DOTALL
#         )

#         # Extract Arabic instruction
#         instruction_ar_match = re.search(
#             r"(لمزيد من المعلومات|لاستكمال الطلب)(.+?)http",
#             email_text,
#             re.DOTALL
#         )

    
#     # Clean and store only the English part
#     if instruction_en_match:
#         data['complete_application_instruction_en'] = (
#             instruction_en_match.group(1) + instruction_en_match.group(2)
#         ).strip()

#     # Clean and store only the Arabic part
#     if instruction_ar_match:
#         data['complete_application_instruction_ar'] = (
#             instruction_ar_match.group(1) + instruction_ar_match.group(2)
#         ).strip()
        
#     return data


# def extract_email_data(email_text):
#     # Normalize line breaks
#     email_text = email_text.replace('\r\n', '\n')

#     data = {
#         'application_number': None,
#         'status': None,
#         'service_name_en': None,
#         'service_name_ar': None,
#         'username_en': None,
#         'username_ar': None,
#         'link_en': None,
#         'link_ar': None,
#         'content_message_en': None,
#         'content_message_ar': None,
#         'complete_application_instruction_en': None,
#         'complete_application_instruction_ar': None,
#         'required_action_en': None,
#         'required_action_ar': None
#     }

#     # Extract details from the email text using regular expressions
#     details = {
#         'application_number': re.search(r"Application Number: (\d+)", email_text),
#         'status': re.search(r"Status is ([\w\s]+)", email_text),
#         'service_name_en': re.search(r"Service Name: ([^\n]+)", email_text),
#         'service_name_ar': re.search(r"اسم الخدمة: ([^\n]+)", email_text),
#         'username_en': re.search(r"Hello ([^,]+),", email_text),
#         'username_ar': re.search(r"أهلاً بك\s*([^،,]+)\s*[،,]", email_text),
#     }
#     print(details['username_ar'])

#     # Update data dictionary with extracted information
#     for key, match in details.items():
#         if match:
#             data[key] = match.group(1).strip()

#     # Define patterns to capture links and content messages
#     link_patterns = {
#         'link_en': [
#             r"please click on: (https?://[^\s]+)",
#             r"kindly click on: (https?://[^\s]+)",
#             r"kindly complete the payment (https?://[^\s]+)",
#             r"kindly complete the payment: (https?://[^\s]+)"
#         ],
#         'link_ar': [
#             r"يُرجى زيارة: (https?://[^\s]+)",
#             r"عبر زيارة: (https?://[^\s]+)",
#             r"الدفع عبر الرابط التالي: (https?://[^\s]+)"
#         ]
#     }

#     # Extract links
#     for key, patterns in link_patterns.items():
#         for pattern in patterns:
#             match = re.search(pattern, email_text)
#             if match:
#                 data[key] = match.group(1).strip()
#                 break

#     # Extract content messages
#     if data['username_en']:
#         content_message_en_match = re.search(rf"Hello {data['username_en']},(.+?)Service Name:", email_text, re.DOTALL)
#         if content_message_en_match:
#             data['content_message_en'] = clean_text(content_message_en_match.group(1).strip(),'english')
#             print(data['content_message_en'] )
    
#     if data['username_ar']:
#         print(data['username_ar'])
#         content_message_ar_match = re.search(rf"أهلاً بك {data['username_ar']}،(.+?)اسم الخدمة:", email_text, re.DOTALL)
#         if content_message_ar_match:
#             data['content_message_ar'] = clean_text(content_message_ar_match.group(1).strip(),'arabic')
#             data['content_message_ar'] = re.sub(r'\s+', ' ', data['content_message_ar']).strip()

#             print(data['content_message_ar'])

#     # Check for "Pending Action" and add required action with bold text
#     if data['status'] and "Pending Action" in data['status']:
#         data['required_action_en'] = (
#             "<strong>Required Action:</strong> You need to complete the application details in order to proceed."
#         )
#         data['required_action_ar'] = (
#             "<strong>الإجراء المطلوب:</strong> يُرجى استكمال المعاملة لمتابعة تقديم طلبك."
#         )
#     else:
#         data['required_action_en'] = None
#         data['required_action_ar'] = None

#     # Extract complete application instructions for English
#     if data['application_number']:
#         instruction_en_match = re.search(
#             r"(To complete your application|For more information)(.+?)http",
#             email_text,
#             re.DOTALL
#         )

#         # Extract Arabic instruction
#         instruction_ar_match = re.search(
#             r"(لمزيد من المعلومات|لاستكمال الطلب)(.+?)http",
#             email_text,
#             re.DOTALL
#         )

#     # Clean and store only the English part
#     if instruction_en_match:
#         data['complete_application_instruction_en'] = (
#             instruction_en_match.group(1) + instruction_en_match.group(2)
#         ).strip()

#     # Clean and store only the Arabic part
#     if instruction_ar_match:
#         data['complete_application_instruction_ar'] = (
#             instruction_ar_match.group(1) + instruction_ar_match.group(2)
#         ).strip()
        
#     return data


def extract_email_data(email_text):
    # Normalize line breaks
    email_text = email_text.replace('\r\n', '\n')

    data = {
        'application_number': None,
        'status': None,
        'service_name_en': None,
        'service_name_ar': None,
        'username_en': None,
        'username_ar': None,
        'link_en': None,
        'link_ar': None,
        'content_message_en': None,
        'content_message_ar': None,
        'complete_application_instruction_en': None,
        'complete_application_instruction_ar': None,
        'required_action_en': None,
        'required_action_ar': None
    }

    # Extract details from the email text using regular expressions
    details = {
        'application_number': re.search(r"Application Number: (\d+)", email_text),
        'status': re.search(r"Status is ([\w\s]+)", email_text),
        'service_name_en': re.search(r"Service Name: ([^\n]+)", email_text),
        'service_name_ar': re.search(r"اسم الخدمة: ([^\n]+)", email_text),
        'username_en': re.search(r"Hello ([^,]+),", email_text),
        'username_ar': re.search(r"أهلاً بك\s*([^،,]+)\s*[،,]", email_text),
    }
    print(details['username_ar'])

    # Update data dictionary with extracted information
    for key, match in details.items():
        if match:
            data[key] = match.group(1).strip()

    # Define patterns to capture links and content messages
    link_patterns = {
        'link_en': [
            r"please click on: (https?://[^\s]+)",
            r"kindly click on: (https?://[^\s]+)",
            r"kindly complete the payment (https?://[^\s]+)",
            r"kindly complete the payment: (https?://[^\s]+)"
        ],
        'link_ar': [
            r"يُرجى زيارة: (https?://[^\s]+)",
            r"عبر زيارة: (https?://[^\s]+)",
            r"الدفع عبر الرابط التالي: (https?://[^\s]+)"
        ]
    }

    # Extract links
    for key, patterns in link_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, email_text)
            if match:
                data[key] = match.group(1).strip()
                break

    # Extract content messages
    if data['username_en']:
        content_message_en_match = re.search(rf"Hello {data['username_en']},(.+?)Service Name:", email_text, re.DOTALL)
        if content_message_en_match:
            data['content_message_en'] = clean_text(content_message_en_match.group(1).strip(),'english')
            print(data['content_message_en'] )
    
    if data['username_ar']:
        print(data['username_ar'])
        content_message_ar_match = re.search(rf"أهلاً بك {data['username_ar']}،(.+?)اسم الخدمة:", email_text, re.DOTALL)
        if content_message_ar_match:
            data['content_message_ar'] = clean_text(content_message_ar_match.group(1).strip(),'arabic')
            data['content_message_ar'] = re.sub(r'\s+', ' ', data['content_message_ar']).strip()

            print(data['content_message_ar'])

    if data['status'] and "Pending Action" in data['status']:
        data['required_action_en'] = (
            '<div><strong>Required Action:</strong> You need to complete the application details in order to proceed.</div>'
        )
        data['required_action_ar'] = (
            '<div><strong>الإجراء المطلوب:</strong> يُرجى استكمال المعاملة لمتابعة تقديم طلبك.</div>'
        )
    else:
        data['required_action_en'] = ""
        data['required_action_ar'] = ""

    # Extract complete application instructions for English
    if data['application_number']:
        instruction_en_match = re.search(
            r"(To complete your application|For more information)(.+?)http",
            email_text,
            re.DOTALL
        )

        # Extract Arabic instruction
        instruction_ar_match = re.search(
            r"(لمزيد من المعلومات|لاستكمال الطلب)(.+?)http",
            email_text,
            re.DOTALL
        )

    # Clean and store only the English part
    if instruction_en_match:
        data['complete_application_instruction_en'] = (
            instruction_en_match.group(1) + instruction_en_match.group(2)
        ).strip()

    # Clean and store only the Arabic part
    if instruction_ar_match:
        data['complete_application_instruction_ar'] = (
            instruction_ar_match.group(1) + instruction_ar_match.group(2)
        ).strip()
        
    return data


def clean_text(text, language):
    if language == "arabic":
        # Regex that matches only Arabic letters, Arabic-Indic numerals, common punctuations, and whitespace
        return re.sub(r'[^\u0600-\u06FF\u0660-\u0669\u061B\u061F\u0621-\u064A\s,.،؛!-]', '', text).strip()
    elif language == "english":
        # Regex that matches only English letters, numerals, common punctuations, and whitespace
        return re.sub(r'[^a-zA-Z0-9\s,.?!-]', '', text).strip()
    return text.strip()



# Define the scope for Gmail API access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
import re

def extract_application_number(text):
    """Extracts a 12-digit application number from the given text."""
    match = re.search(r'\b\d{12}\b', text)
    if match:
        return match.group()
    else:
        return "Application number not found"


def extract_service_name(html_content):
    """
    Extracts the service name from the HTML content.
    
    Args:
        html_content (str): The HTML content as a string.
        
    Returns:
        str: The extracted service name, or 'Not Found' if not present.
    """
    # Updated regex pattern to handle spaces and newlines more flexibly
    match = re.search(r'Service Name:\s*</strong>\s*(.*?)\s*<br>', html_content, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else 'Not Found'


def authenticate_gmail():
    """Authenticate and return the Gmail API service."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('Creds.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def list_messages(service, max_results=5):
    """Fetches message IDs from the Gmail inbox."""
    try:
        results = service.users().messages().list(userId='me', maxResults=max_results, labelIds=['INBOX']).execute()
        messages = results.get('messages', [])
        return messages
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def get_message_details(service, msg_id):
    """Retrieves and returns the subject, sender, body, and time of the email."""
    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        headers = message['payload']['headers']
        
        # Extract subject and sender from headers
        subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
        sender = next((header['value'] for header in headers if header['name'] == 'From'), 'No Sender')
        
        # Extract the timestamp and convert to a readable format
        timestamp = int(message['internalDate']) / 1000
        message_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        # Extract email body (assuming plain text for simplicity)
        if 'parts' in message['payload']:
            body = ''
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        else:
            body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

        return {'subject': subject, 'sender': sender, 'body': body, 'time': message_time}

    except HttpError as error:
        print(f'An error occurred: {error}')
        return {'subject': 'Error', 'sender': 'Error', 'body': 'Error', 'time': 'Error'}

    
    # Function to populate the template with extracted data
def populate_email_template(template, data):
    for key, value in data.items():
        placeholder = f"{{{{{key}}}}}"
        template = template.replace(placeholder, value if value else "")
    return template


def fetch_emails_to_dataframe(service, max_results=50):
    """
    Fetches emails using Gmail API, extracts details, and stores them in a DataFrame.
    """
    messages = list_messages(service, max_results)
    email_data = []

    # Retrieve each message's details and add to list
    for msg in messages:
        email_details = get_message_details(service, msg['id'])
        email_data.append(email_details)

    # Convert list of dictionaries to DataFrame
    df_emails = pd.DataFrame(email_data)

    # Add required columns with default values to avoid KeyError
    for col in ['application_number', 'status', 'service_name', 'username_en', 'username_ar',
                'service_name_en', 'service_name_ar', 'link_en', 'link_ar']:
        if col not in df_emails.columns:
            df_emails[col] = 'NAN'

    # Process each email for extracting details
    for i in range(len(df_emails)):
        subject_record = df_emails['subject'].iloc[i].lower()

        # Extract application number and status
        application_number = extract_application_number(subject_record)
        status = subject_record.split('status is')[-1].strip()

        # Assign the extracted values
        df_emails.at[i, 'application_number'] = application_number
        df_emails.at[i, 'status'] = status

        # Extract and assign the service name
        service_name = extract_service_name(df_emails['body'].iloc[i])
        df_emails.at[i, 'service_name'] = service_name

    # Extract additional fields from the email body
    for i in range(len(df_emails)):
        email_content = df_emails['body'].iloc[i]

        # Extract data using the adjusted function
        extracted_data_adjusted = extract_email_data(email_content)

        # Safely assign extracted values to the DataFrame
        df_emails.at[i, 'username_en'] = extracted_data_adjusted.get('username_en', 'NAN')
        df_emails.at[i, 'username_ar'] = extracted_data_adjusted.get('username_ar', 'NAN')
        df_emails.at[i, 'service_name_en'] = extracted_data_adjusted.get('service_name_en', 'NAN')
        df_emails.at[i, 'service_name_ar'] = extracted_data_adjusted.get('service_name_ar', 'NAN')
        df_emails.at[i, 'application_number'] = extracted_data_adjusted.get('application_number', 'NAN')
        df_emails.at[i, 'link_en'] = extracted_data_adjusted.get('link_en', 'NAN')
        df_emails.at[i, 'link_ar'] = extracted_data_adjusted.get('link_ar', 'NAN')

    return df_emails





# Read the HTML content from a file
def read_html_template(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Save the populated email to a file
def save_html_file(content, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"File saved successfully at: {file_path}")

# Write the HTML to a temporary file and return its path
def create_temp_html_file(content):
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as temp_html:
        temp_html.write(content)
        return temp_html.name
    



def copy_and_rename_file(input_dir, output_dir, text_to_include, file_extension):
    """
    Searches for a file in the input directory with a specific text and file extension, 
    then copies it to the output directory with a new name containing today's date.
    
    Args:
        input_dir (str): The directory to search for the file.
        output_dir (str): The directory to copy the file to.
        text_to_include (str): The text to search for in the file name.
        file_extension (str): The file extension to match (e.g., ".xlsx").
    
    Returns:
        None
    """
    # Get today's date
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Search for the file
    file_found = None
    for file_name in os.listdir(input_dir):
        if text_to_include in file_name and file_name.endswith(file_extension):
            file_path = os.path.join(input_dir, file_name)
            file_found = file_name
            break

    # If the file is found, copy and rename it
    if file_found:
        new_file_name = f"{text_to_include} {today_date}{file_extension}"
        destination_path = os.path.join(output_dir, new_file_name)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy and rename the file
        shutil.copy(file_path, destination_path)
        print(f"File '{file_found}' successfully copied and renamed to '{new_file_name}' in '{output_dir}'.")
    else:
        print(f"No file with '{text_to_include}' found in '{input_dir}'.")




def enter_field_data(driver, field_xpath, input_xpath, input_value, dropdown_xpath, field_name="Field"):
    """
    Generalized function to enter data into a field, select the input value, and choose an option from the dropdown.

    Parameters:
    driver: WebDriver instance.
    field_xpath: XPath for the field to click.
    input_xpath: XPath for the input field.
    input_value: The value to input into the field.
    dropdown_xpath: XPath for the first option in the dropdown.
    field_name: Name of the field for logging purposes (default: "Field").
    """
    print(f"======= Entering {field_name}")

    # Click on the field
    clicking_on_element_by_all_option(driver, field_xpath, [''], max_retries=5)

    # Input the data
    input_data_by_all_option(driver, input_xpath, [''], input_value, 
                             calender_date=None, max_attempts=3, timeout=10, scroll=False, input_delay=2, field_type='others')

    # Select the first option from the dropdown
    clicking_on_element_by_all_option(driver, dropdown_xpath, [''], max_retries=5)

    time.sleep(2)




def create_vertical_snake_text(text, wave_length=3):
    """
    Creates a vertical "snake" or wave pattern for the given text, one character per line.
    
    Parameters:
    - text: The original text to be transformed.
    - wave_length: Number of spaces to increase and decrease to form the wave shape.
    
    Returns:
    - A string with a vertical "snake" pattern.
    """
    snake_text = ""
    space_count = 0
    increasing = True

    for char in text:
        # Add spaces before the character to create the wave effect
        snake_text += " " * space_count + char + "\n"
        
        # Adjust space count for the wave pattern
        if increasing:
            space_count += 1
            if space_count == wave_length:
                increasing = False
        else:
            space_count -= 1
            if space_count == 0:
                increasing = True

    return snake_text





def move_mouse_to_second_screen():
    """
    Moves the mouse to a central location on the second screen.
    Adjust the x-coordinate based on the width of the primary screen.
    """
    # Get the screen resolution of both screens
    screen1_width, screen1_height = pyautogui.size()  # Width and height of the primary screen
    # Assuming the second screen is aligned horizontally to the right of the first screen
    # Set the x and y coordinates to move the mouse to the second screen
    x_second_screen = screen1_width - 3000  # Starting position on the second screen (adjust as needed)
    y_position = screen1_height // 2       # Center vertically on the second screen
    
    # Move the mouse to the specified position on the second screen
    pyautogui.moveTo(x_second_screen, y_position)
    print(f"Mouse moved to position on second screen at ({x_second_screen}, {y_position})")

# Call the function







def upload_official_letter(driver, upload_button_xpath, upload_button_text, file_path, target_screen="first"):
    """
    Handles clicking on the upload button, selecting the file in the file upload dialog,
    and confirming the file upload.
    
    Parameters:
    - driver: Selenium WebDriver instance.
    - upload_button_xpath: XPath of the upload button element.
    - upload_button_text: Text associated with the upload button.
    - file_path: Full path to the file to upload.
    - target_screen: "first" or "second" to specify the screen for the file dialog.
    """
    # Click on the upload button
    print("Clicking on the upload button...")
    clicking_on_element_by_all_option(driver, upload_button_xpath, upload_button_text, max_retries=4, timeout=5, scroll=True)
    time.sleep(2)  # Allow time for the file upload dialog to appear

    # Focus on the target screen
    screen_dimensions = pyautogui.size()  # Get screen size
    current_screen_width = screen_dimensions.width

    if target_screen.lower() == "first":
        pyautogui.moveTo(current_screen_width // 4, screen_dimensions.height // 2)
        print("Focusing on the first screen.")
    elif target_screen.lower() == "second":
        pyautogui.moveTo(current_screen_width + current_screen_width // 4, screen_dimensions.height // 2)
        print("Focusing on the second screen.")
    else:
        raise ValueError("Invalid target_screen. Choose 'first' or 'second'.")

    pyautogui.click()  # Bring the file dialog into focus
    time.sleep(2)

    # Input the file path into the file dialog
    print(f"Entering file path: {file_path}")
#     pyautogui.hotkey('alt', 'd')  # Focus on the file path field
    time.sleep(2)
    pyautogui.write(file_path)
    pyautogui.press('enter')  # Confirm the file selection
    print(f"File uploaded successfully: {file_path}")






def scrape_application_number(driver, enviroment,max_retries=3, retry_delay=3):
    """
    Scrape the application number with retry logic.

    Parameters:
    - driver: Selenium WebDriver instance.
    - max_retries: Maximum number of retries if application number is empty.
    - retry_delay: Delay in seconds between retries.

    Returns:
    - application_number: Scraped application number.
    """
    if enviroment=='Eforms_test':
        xpath = [

            "/html/body/div[3]/div[1]/div[2]/div[4]/div/div[4]/div[2]/div[1]/div[2]",
            "//div[@class='widget-body app-application-details']//div[@class='value']/span[@data-bind='text: applicationNumber']"
        ]
    if enviroment=='ELMS':
        xpath=['/html/body/div[3]/div[1]/div[2]/div[4]/div/div[3]/div[2]/div[1]/div']

    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt} of {max_retries}...")

        # Extract text using provided XPaths
        text = extract_text(driver, xpath, max_retries=3, retry_delay=1, waittime=3)

        # Format the details into a DataFrame
        details_df = application_details_formatting(text)

        # Extract the application number
        application_number = details_df['Application Number'][0]

        # Check if application number is not empty
        if application_number.strip():
            print(f"Application number found: {application_number}")
            return application_number

        # If application number is empty, retry after delay
        print("Application number is empty. Retrying...")
        time.sleep(retry_delay)

    # If all retries fail, raise an exception or return a default value
    print("Failed to retrieve application number after maximum retries.")
    return None
