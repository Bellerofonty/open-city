# Запись на мероприятие на открытыйгород.рф с помощью Selenium

import time
from random import randint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


def read_from_file(file):
    """Чтение логина и пароля, либо ссылки на мероприятие из файла"""
    with open(file) as f:
        data = []
        for line in f:
            data.append(line.strip().split())
    return data


def set_driver():
    """Создание драйвера"""
    chrome_options = Options()
##    chrome_options.add_argument("--headless")  # Браузер без gui
    chrome_options.add_argument('log-level=3')
    driver = webdriver.Chrome(
        executable_path=r'C:\Py files\web-scraping\chromedriver.exe',  # TODO getcwd
        options=chrome_options)
    return driver


def login(driver, username, password):
    """Авторизация"""
    login_url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/kabinet/'
    try:
        driver.get(login_url)
        # TODO если нет соединения, повторить
        time.sleep(5)
        form_username = driver.find_element_by_name('USER_LOGIN')
        form_password = driver.find_element_by_name('USER_PASSWORD')
        form_username.send_keys(username)
        form_password.send_keys(password)
        driver.find_element_by_name('Login').click()
    except Exception as ex:
        print('Ошибка авторизации:', ex)
        time.sleep(60)


def try_to_enroll(driver, wanted_event_url):
    """Попытка записи на мероприятие"""
    driver.get(wanted_event_url)
    # Ждать, пока не обнаружена нужная кнопка или не вышло время (7 сек)
    try:
##        try:
##            tour_name = driver.find_element_by_tag_name('h1')
##            tour_quantity = driver.find_element_by_id('tour_quantity')
##            tour_quantity_balls = driver.find_element_by_id('tour_quantity_balls')
##            tour_date = driver.find_element_by_id('tour_date')
##            user_name = driver.find_element_by_xpath("//a[@href='lichnyij-kabinet/']")
##            print('\n{} ({})'.format(tour_name.text, tour_date.text))
##            print('{}/{} мест. {}'.format(tour_quantity.text, tour_quantity_balls.text, user_name.text.strip()))
##        except NoSuchElementException as ex:
##            print(ex)

        enroll_button = WebDriverWait(driver, 7).until(EC.presence_of_element_located(
                (By.XPATH, '//a[contains(text(), "Записаться")]')))
        # enroll_button = driver.find_element_by_xpath('//button[contains(text(), "Записаться")]')
        driver.execute_script("window.scrollTo(0, 900)")
        btn_img = enroll_button.screenshot_as_png
        with open('btn_img1.png', 'wb') as file:
            file.write(btn_img)
        enroll_button.click()

        time.sleep(3)
        ordinary_enroll_button = driver.find_element_by_xpath('//a[contains(text(), "Обычная запись")]')
        btn_img = ordinary_enroll_button.screenshot_as_png
        with open('btn_img2.png', 'wb') as file:
            file.write(btn_img)
        ordinary_enroll_button.click()

        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 1500)")
        finally_enroll_button = driver.find_element_by_xpath('//button[contains(@class, "m-top-big")]')
        btn_img = finally_enroll_button.screenshot_as_png
        with open('btn_img3.png', 'wb') as file:
            file.write(btn_img)
        finally_enroll_button.click()

        return 1
    except TimeoutException:
        print('timeout')
        """
        TODO
        check network by ping
        if connection:
            driver.close()
            restart script with sys.exec*
        """
        return 0
    except NoSuchElementException as ex:
            print(ex)

def main():
    try:
        users_data = read_from_file('login_data.txt')
        event_urls = read_from_file('wanted_event_url.txt')
        log_out_url = 'https://xn--c1acndtdamdoc1ib.xn--p1ai/kabinet/?logout=yes'
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
                        result = False
                    time.sleep(3)
                if result:
                    break
                # TODO restart script every hour
                time.sleep(randint(120, 240))  # Для имитации человека
            time.sleep(5)
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
