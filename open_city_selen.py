# Запись на мероприятие на открытыйгород.рф с помощью Selenium

import time
from random import randint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def read_from_file(file):
    """Чтение логина и пароля из файла"""
    with open(file) as f:
        data = []
        for line in f:
            data.append(line.strip())
    return data


def set_driver():
    """Создание драйвера"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Браузер без gui
    driver = webdriver.Chrome(
        executable_path=r'C:\Py files\web-scraping\chromedriver.exe',  # TODO getcwd
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
        # enroll_button = driver.find_element_by_xpath('//button[contains(text(), "Записаться")]')
        if 'loading' in enroll_button.get_attribute("class"):
            while 'loading' in enroll_button.get_attribute("class"):
                print('_____loading')
                time.sleep(60)
            enroll_button = driver.find_element_by_xpath('//button[contains(text(), "Записаться")]')
        print('_____', enroll_button.text)

        # Исключить текст 'ЗАПИСАТЬСЯ НЕЛЬЗЯ' и 'ЗАПИСАТЬСЯ ЗА БАЛЛЫ'
        if enroll_button.text == 'ЗАПИСАТЬСЯ':
            # print('_____', enroll_button)
            print('_____', enroll_button.tag_name)
            print('_____', enroll_button.get_attribute("class"))

            btn_img = enroll_button.screenshot_as_png
            with open('btn_img.png', 'wb') as file:
                file.write(btn_img)

            enroll_button.click()
            return 1
    except TimeoutException:
        print('_____timeout')
        try:
            enroll_button = driver.find_element_by_xpath('//button[contains(text(), "Запись не началась")]')
            print('_____',enroll_button.text)
        except NoSuchElementException as ex:
            print(ex)
        return 0
    except NoSuchElementException as ex:
            print(ex)

def main():
    # wanted_event_url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/ekskursii/dvorecz-i.i.-shuvalova.html?date=2018-12-07%2016:00:00'
    username, password = read_from_file('login_data.txt')
    wanted_event_url = read_from_file('wanted_event_url.txt')[0]

    while True:
        try:
            driver = set_driver()
            login(driver, username, password)
            break
        except Exception as ex:
            print('_____Ошибка авторизации:', ex)
            time.sleep(120)

    while True:
        try:
            result = try_to_enroll(driver, wanted_event_url)
            if result:
                print('_____Успешно', time.asctime())
                break
            else:
                print('_____Активная кнопка не обнаружена', time.asctime())
        except Exception as ex:
            print('_____Ошибка:', ex)
        time.sleep(randint(250, 450))  # Для имитации человека
    # input()
    driver.close()


if __name__ == '__main__':
    main()
