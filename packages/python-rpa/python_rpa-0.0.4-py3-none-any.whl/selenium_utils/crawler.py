"""selenium_utils/crawler.py"""

import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class ChromeBrowser:
    def __init__(self, url, maximiaze_window=True):
        self.driver = create_web_driver(maximiaze_window=maximiaze_window)
        self.driver.get(url)


    def browse(self, url):
        self.driver.get(url)


    def get_element_by_xpath(self, xpath):
        return self.driver.find_element(By.XPATH, xpath)


    def get_elements_by_xpath(self, xpath):
        return self.driver.find_elements(By.XPATH, xpath)


    def get_element_by_xpath_until_rendering(self, xpath, wait_seconds=10):
        try:
            return WebDriverWait(self.driver, wait_seconds).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except TimeoutException:
            return None
        except NoSuchElementException:
            return None


    def get_elements_by_xpath_until_rendering(self, xpath, wait_seconds=10):
        try:
            return WebDriverWait(self.driver, wait_seconds).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
        except TimeoutException:
            return None
        except NoSuchElementException:
            return None


    def swith_to_iframe_by_xpath_until_rendering(self, xpath, wait_seconds=10):
        iframe = self.get_element_by_xpath_until_rendering(xpath, wait_seconds=wait_seconds)

        self.driver.switch_to.frame(iframe)


def get_element_by_xpath(url, xpath, driver=None, sleep_seconds=3):
    """Get element by xpath"""

    if driver is None:
        driver = create_web_driver()

    driver.get(url)

    time.sleep(sleep_seconds)

    return driver.find_element(By.XPATH, xpath)


def get_elements_by_xpath(url, xpath, driver=None, sleep_seconds=3):
    """Get elements by xpath"""

    if driver is None:
        driver = create_web_driver()

    driver.get(url)

    time.sleep(sleep_seconds)

    return driver.find_elements(By.XPATH, xpath)


def create_web_driver(driver_path="/opt/homebrew/bin/chromedriver", maximiaze_window=True):
    """Create web driver"""

    service = Service(driver_path)

    driver = webdriver.Chrome(service=service)

    if maximiaze_window:
        driver.maximize_window()

    return driver


def close_all_popup_windows(driver):
    """ Close all popup windows """

    if driver is None:
        return

    # 현재 열려 있는 모든 창 핸들 가져오기
    main_window = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != main_window:
            driver.switch_to.window(handle)
            driver.close()  # 팝업 창 닫기

    driver.switch_to.window(main_window)  # 메인 창으로 전환
