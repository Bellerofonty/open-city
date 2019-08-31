'''Мониторинг появления мероприятий интересующих типов на сайте'''
import sys
import re
import time

import requests
from bs4 import BeautifulSoup
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
import winsound

import open_city_widget


class EventsScan(QThread):
    '''Циклический поиск мероприятий (отдельный поток)'''

    HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '\
                'AppleWebKit/537.36 (KHTML, like Gecko) '\
                'Chrome/69.0.3497.100 Safari/537.36'}

    result_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    success_signal = pyqtSignal()

    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        self.delay = 5
        self.wanted_types = []
        self.stored_wanted_found = []
        self.ignored_events_urls = []
        self.URL = self.read_from_file('wanted_event_url.txt')

    def run(self):
        while True:
            html = self.get_html()
            bs = BeautifulSoup(html, 'html.parser')
            status = bs.find('div', {'class': 'status'}).getText()
            status = ' '.join(status.split())
            if 'Запись открыта' in status:
                self.result_signal.emit('ЗАПИСЬ ОТКРЫТА\n')
                self.success_signal.emit()
                import open_city_selen
                open_city_selen.main()
            else:
                self.result_signal.emit(status + '\n')

            # Обновление индикатора времени ожидания
            for i in range(1, 101):
                time.sleep(0.01 * self.delay)
                self.progress_signal.emit(i)

    def get_ignored_events(self):
        '''Получает из файла список url мероприятий, которые нужно игнорировать;
        не добавляет пустые строки, если они есть в файле'''
        with open('ignored_events.txt', 'r') as f:
            ignored_events = []
            for line in f:
                if line.strip():
                    ignored_events.append(line.strip())
            return ignored_events

    def get_html(self):
        '''Запрос страницы доступных мероприятий'''
        return requests.get(self.URL, self.HEADERS).text

    def get_events(self, html):
        '''Получение списка блоков-мероприятий из html'''
        bs = BeautifulSoup(html, 'html.parser')
        return bs.find('div', {'class': 'products'}).ul.find_all('li',
                                                        {'class': 'product'})
    def clr_spaces(self, string):
        '''Очистка информации от лишних пробелов и прочего'''
        string = re.sub('[ \n]{2,}', '', string)
        string = re.sub('Посмотреть', '', string)
        return string

    def search_wanted(self, events_found):
        '''Поиск желаемых типов мероприятий в списке, возвращает их описание'''
        wanted_found = []
        for event in events_found:
            event_url = event.find('div', {'class': 'info_right'}).find('a',
                    {'class': 'button'})['href']
##            print(event_url)
            if event_url in self.ignored_events_urls:
                print('ignored:', event_url)
            if event_url not in self.ignored_events_urls:
                found_event_type = event.find('div', {'class': 'type'}).getText()
                for wanted_type in self.wanted_types:
                    if wanted_type in found_event_type:
                        event_title = event.find('div', {'class': 'title'}).getText()
                        event_desc = event.find('div', {'class': 'info_right'}).getText()
                        wanted_found.append([self.clr_spaces(event_title) +
                                self.clr_spaces(found_event_type) + '\n' +
                                self.clr_spaces(event_desc) + '\n', event_url])
        if wanted_found:
            return wanted_found
        return ['Не найдено\n']

    def read_from_file(self, file):
        """Чтение ссылки на мероприятие из файла"""
        with open(file) as f:
            return f.readline()


class OpenCityApp(QtWidgets.QWidget, open_city_widget.Ui_Form):
    '''GUI и управление потоком поиска'''

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btn_start.clicked.connect(self.start_scan)
        self.btn_stop.clicked.connect(self.stop_scan)
        self.btn_reset.clicked.connect(self.reset_color)
        self.thread = EventsScan() # Поиск в отдельном потоке
        self.thread.result_signal.connect(self.show_result)
        self.thread.started.connect(self.on_started)
        self.thread.finished.connect(self.on_finished)
        self.thread.progress_signal.connect(self.show_progress)
        self.thread.success_signal.connect(self.success_alarm)

        self.reset_color()

    def start_scan(self):
        '''Нажата кнопка "Старт"'''
        self.thread.delay = self.choose_delay()
        self.thread.wanted_types = self.choose_wanted_types()
        self.btn_stop.setEnabled(True)
        self.thread.start()

    def stop_scan(self):
        '''Нажата кнопка "Стоп"'''
        self.thread.terminate()

    def show_result(self, result):
        '''Добавляет запись в лог и проматывает его вниз'''
##        if len(result) > 1:
##            print(result)
##        self.log.textCursor().insertText('--'*32 + '\n') # Разделитель запросов
        self.log.textCursor().insertText(result)
        self.log.ensureCursorVisible()

    def on_started(self):
        '''Поток поиска начался'''
        self.btn_start.setDisabled(True)

    def on_finished(self):
        '''Поток поиска закончился'''
        self.reset_color()
        self.btn_start.setDisabled(False)
        self.btn_stop.setDisabled(True)
        self.progressBar.reset()

    def show_progress(self, progress):
        '''Обновление индикатора ожидания'''
        self.progressBar.setValue(progress)

    def success_alarm(self):
        '''Окно меняет цвет фона, разворачивается, всплывает'''
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Window, QtGui.QColor('#9ACD32'))
        self.setPalette(pal)
        self.showNormal()
        self.activateWindow()

        winsound.PlaySound('bell-ringing.wav', winsound.SND_FILENAME)

    def reset_color(self):
        '''Исходный цвет фона. Нажата кнопка "Сброс цвета",
        или поток поиска закончен'''
        pal = self.palette()
        pal.setColor(QtGui.QPalette.Window, QtGui.QColor('#CCCCCC'))
        self.setPalette(pal)

    def choose_wanted_types(self):
        '''Выбор типов мероприятий для поиска'''
        wanted_types = []
        if self.checkBox_ped.isChecked():
            wanted_types.append('ешеходн')
        if self.checkBox_auto.isChecked():
            wanted_types.append('втобусн')
        if self.checkBox_tram.isChecked():
            wanted_types.append('рамвайн')
        if self.checkBox_troll.isChecked():
            wanted_types.append('роллейбусн')
        if self.checkBox_bike.isChecked():
            wanted_types.append('елосипедн')
        if self.checkBox_spec.isChecked():
            wanted_types.append('пециальн')
        if self.checkBox_scooter.isChecked():
            wanted_types.append('самокатах')
        return wanted_types

    def choose_delay(self):
        '''Выбор задержки между запросами в секундах'''
        if self.radioButton_3.isChecked():
            delay = 180
        elif self.radioButton_5.isChecked():
            delay = 300
        elif self.radioButton_10.isChecked():
            delay = 600
        return delay

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = OpenCityApp()
    window.show()
    app.exec_()

if __name__=='__main__':
    main()
