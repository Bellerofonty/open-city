# Запись на мероприятие на открытыйгород.рф с помощью Selenium

import time
from random import randint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def read_login_data(file):
    """Чтение логина и пароля из файла"""
    with open(file) as f:
        username = f.readline().strip()
        password = f.readline().strip()
    return username, password


def set_driver():
    """Создание драйвера"""
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Браузер без gui
    driver = webdriver.Chrome(
        executable_path=r'C:\Py files\web-scraping\chromedriver.exe',
        options=chrome_options)
    return driver


def login(driver, username, password):
    """Авторизация"""
    login_url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/vxod.html'
    driver.get(login_url)
    form_username = driver.find_element_by_name('username')
    form_password = driver.find_element_by_name('password')
    form_username.send_keys(username)
    form_password.send_keys(password)
    driver.find_element_by_name('Login').click()


def try_to_enroll(driver, wanted_event_url):
    """Попытка записи на мероприятие"""
    driver.get(wanted_event_url)
    # Ждать, пока не обнаружена нужная кнопка или не вышло время (15 сек)
    try:
        enroll_button = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
            (By.XPATH, '//button[contains(text(), "Записаться")]')))
        if enroll_button.text == 'ЗАПИСАТЬСЯ': # Исключить текст 'ЗАПИСАТЬСЯ НЕЛЬЗЯ'
            enroll_button.click()
            return 1
    except TimeoutException:
        return 0


def main():
    wanted_event_url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/ekskursii/chto-rozhdaetsya-v-nedrax-zemli/?date=2018-12-05%2012:00:00'
    username, password = read_login_data('login_data.txt')
    driver = set_driver()
    login(driver, username, password)
    while True:
        result = try_to_enroll(driver, wanted_event_url)
        if result:
            print('Успешно', time.asctime())
            break
        else:
            print('Активная кнопка не обнаружена', time.asctime())
        time.sleep(randint(250, 450)) # Для имитации человека
##    input()
    driver.close()


if __name__ == '__main__':
    main()