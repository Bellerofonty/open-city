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
            data.append(line.strip().split())
    return data


def set_driver():
    """Создание драйвера"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Браузер без gui
    chrome_options.add_argument('log-level=3')
    driver = webdriver.Chrome(
        executable_path=r'C:\Py files\web-scraping\chromedriver.exe',  # TODO getcwd
        options=chrome_options)
    return driver


def login(driver, username, password):
    """Авторизация"""
    login_url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/vxod.html'
    try:
        driver.get(login_url)
        time.sleep(3)
        form_username = driver.find_element_by_name('username')
        form_password = driver.find_element_by_name('password')
        form_username.send_keys(username)
        form_password.send_keys(password)
        driver.find_element_by_name('Login').click()
    except Exception as ex:
        print('Ошибка авторизации:', ex)
        time.sleep(60)


def try_to_enroll(driver, wanted_event_url):
    """Попытка записи на мероприятие"""
    driver.get(wanted_event_url)
    # Ждать, пока не обнаружена нужная кнопка или не вышло время (15 сек)
    try:
        try:
            tour_name = driver.find_element_by_tag_name('h1')
            tour_quantity = driver.find_element_by_id('tour_quantity')
            tour_quantity_balls = driver.find_element_by_id('tour_quantity_balls')
            tour_date = driver.find_element_by_id('tour_date')
            user_name = driver.find_element_by_xpath("//a[@href='lichnyij-kabinet/']")
            print('\n{} ({})'.format(tour_name.text, tour_date.text))
            print('{}/{} мест. {}'.format(tour_quantity.text, tour_quantity_balls.text, user_name.text.strip()))
        except NoSuchElementException as ex:
            print(ex)

        enroll_button = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
            (By.XPATH, '//button[contains(text(), "Записаться")]')))
        # enroll_button = driver.find_element_by_xpath('//button[contains(text(), "Записаться")]')
        if 'loading' in enroll_button.get_attribute("class"):
            while 'loading' in enroll_button.get_attribute("class"):
                print('loading')
                time.sleep(60)
            enroll_button = driver.find_element_by_xpath('//button[contains(text(), "Записаться")]')
        print(enroll_button.text)

        # Исключить текст 'ЗАПИСАТЬСЯ НЕЛЬЗЯ' и 'ЗАПИСАТЬСЯ ЗА БАЛЛЫ'
        if enroll_button.text == 'ЗАПИСАТЬСЯ':
            print(enroll_button.get_attribute("class"))

            btn_img = enroll_button.screenshot_as_png
            with open('btn_img.png', 'wb') as file:
                file.write(btn_img)

            enroll_button.click()
            return 1
    except TimeoutException:
        print('timeout')
        try:
            enroll_button = driver.find_element_by_xpath('//button[contains(text(), "Запись не началась")]')
            print(enroll_button.text)
        except NoSuchElementException as ex:
            print(ex)
        return 0
    except NoSuchElementException as ex:
            print(ex)

def main():
    try:
        users_data = read_from_file('login_data.txt')
        event_urls = read_from_file('wanted_event_url.txt')
        log_out_url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/vxod.html?service=logout'
        driver = set_driver()

        for user_data in users_data:
            login(driver, user_data[0], user_data[1])

            while True:
                for event_url in event_urls:
                    try:
                        result = try_to_enroll(driver, event_url[0])
                        if result:
                            print('Успешно', time.asctime())
                            break
                        else:
                            print('Активная кнопка не обнаружена', time.asctime())
                    except Exception as ex:
                        print('Ошибка:', ex)
                    time.sleep(3)
                if result:
                    break
                time.sleep(randint(120, 240))  # Для имитации человека
            driver.get(log_out_url)

    except KeyboardInterrupt as ex:
        print(ex)
    except:
        import traceback
        traceback.print_exc()
    finally:
        driver.close()


if __name__ == '__main__':
    main()
