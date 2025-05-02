from selenium.webdriver.chrome.options import Options
from requests import get, RequestException
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import json
import csv

class WorkWithScv:
    '''Класс для работы с csv файлами во время парсинга'''

    def __init__(self, newline:str='', encoding:str='cp1251', delimiter:str=';'):
        '''Конструктор'''
        self.newline = newline
        self.encoding = encoding
        self.delimiter = delimiter
    
    def writerow(self, file_path:str, mode:str, row:list):
        '''Записываем строку в csv файл'''
        with open(file_path, mode=mode, newline=self.newline, encoding=self.encoding) as file:
            writer = csv.writer(file, delimiter=self.delimiter)
            writer.writerow(row)
    
    def writerows(self, file_path:str, mode:str, row:list):
        '''Записываем строки в csv файл'''
        with open(file_path, mode=mode, newline=self.newline, encoding=self.encoding) as file:
            writer = csv.writer(file, delimiter=self.delimiter)
            writer.writerows(row)

    def getRows(self, file_path:str):
        '''Возвращает строки файла'''
        userRows = []

        with open(file_path, mode='r', newline=self.newline, encoding=self.encoding) as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=self.delimiter)
        
            for row in csv_reader:
                userRows.append(row)
        
        return userRows

class WorkWithJson:
    '''Модуль для работы с json файлами'''

    def __init__(self, encoding:str='utf8'):
        self.encoding = encoding

    def load(self, pathToJsonFile:str):
        """Получаем данные из json файла"""
        with open(pathToJsonFile, encoding=self.encoding) as jsonFile:
            src = json.load(jsonFile)
        return src 


    def dump(self, pathToJsonFile:str, data:any):
        """Записываем данные в json файл"""
        with open(pathToJsonFile, 'w', encoding=self.encoding) as jsonFile:
            json.dump(data, jsonFile, indent=4, ensure_ascii=0)


class Pars:
    '''Модуль для работы с запросами и HTML файлами во время парсинга'''

    def returnBs4Object(self, pathToFile, myEncoding:str='utf8', parser:str='lxml'):
        """Возвращаем объект beautifulsoup"""
        with open(pathToFile, encoding=myEncoding) as file:
            src = file.read()
        soup = BeautifulSoup(src, parser)
        return soup


    def get_static_page(self, pathToSaveFile, url, writeMethod='w', headers:dict='')-> int():
        '''Получаем статическую страницу'''

        if headers == '':
            headers ={
                "Accept": "*/*",
                "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
                }

        try:
            # Отправляем запрос
            req = get(url, headers=headers)
            req.raise_for_status()  # Проверка на ошибки HTTP

            # Записываем данные
            if writeMethod == 'w':
                src = req.text
                with open(pathToSaveFile, 'w', encoding='utf-8') as file:
                    file.write(src)
            elif writeMethod == 'wb':
                src = req.content
                with open(pathToSaveFile, 'wb') as file:
                    file.write(src)
            else:
                raise ValueError(f"Неподдерживаемый метод записи: {writeMethod}")

        # Обрабатываем ошибки
        except RequestException as e:
            return req.status_code
        except IOError as e:
            print(f"Ошибка при записи в файл: {e}")
        except Exception as e:
            return e
        
        # Если всё выполнилось хорошо, то возвращаем статус 200
        return 200


    def get_dinamic_page(self, url, pathToSaveFile, closeWindow:bool=1) -> None:
        '''Получаем динамическую страницу'''

        # Устанавливаем опции для Chrome WebDriver
        options = Options()
        if closeWindow:
            options.add_argument('--headless')

        # открываем браузер
        with webdriver.Chrome(options=options) as driver:
            driver.get(url)
            # Прокручиваем страницу до самого низа
            last_height = driver.execute_script("return document.body.scrollHeight")
            while True:
                # Прокручиваем до низа страницы
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Ждем загрузки страницы
                sleep(2)
                # Вычисляем новую высоту страницы
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            # Получаем HTML-код страницы
            html_content = driver.page_source
            # Сохраняем HTML-код в файл
            with open(pathToSaveFile, "w", encoding="utf-8") as file:
                file.write(html_content)
