# Библиотека для работы с файлами во время парсинга

Во время работы часто приходится скачивать html-страницы, работать с json- и csv-файлами. Эта библиотека призвана облегчить написание кода для такого рода задач.

В библиотеке есть три класса для отдельных работ: Pars для получения данных из Интернета, WorkWithJson для работы с json и WorkWithCsv для работы с csv.

Установить библиотеку:
```bash
pip install ipars
```

## Работа с Pars
Класс Pars не принимает никаких данных для конструкторов
```python
# Импортируем библиотеку
from ipars import Pars
# Создаём объект класса
p = Pars()
```

### Коротко о методах
1. Функция **get_static_page** принимает url страницы, путь, по которому сохранится страница, метод записи и заголовки запроса. Метод записи «wb» используется для сохранения картинок, по умолчанию writeMethod установлен как «w», что используется для html-страниц. Если заголовки запросов не указаны, то будут использоваться встроенные, но при желании можно указать свои. Функция возвращает статус ответа сайта, что должно использоваться для введения проверок
```python
from ipars import Pars
p = Pars()
# Заголовки для запроса
headers ={
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1"
    }

# Делаем запрос к сайту и записываем статус ответа в переменную
status_response = p.get_static_page('https://google.com', './index.html', headers=headers)
if status_response == 404:
    print('Страница не найдена')
```

2. Функция **get_dynamic_page** с помощью библиотеки Selenium получает динамически обновляемую страницу. Это помогает, когда контент на странице подгружается динамически. Принимает url страницы, путь сохранения и closeWindow. По умолчанию браузер Selenium открывается в фоновом режиме, и работу браузера не видно, но если closeWindow указать как False, то будет виден процесс выполнения кода

3. Функция **returnBs4Object** возвращает объект beautifulsoup4. Принимает путь до html-страницы, содержимое которой преобразует в объект beautifulsoup, кодировку открытия файла (по умолчанию UTF-8) и тип парсера (по умолчанию lxml)
```py
from ipars import Pars
p = Pars()
p.get_static_page('./index.html', 'https://google.com')
# Получаем объект beautifulsoup из полученной страницы
soup = p.returnBs4Object('./index.html')
# Используем методы beautifulsoup
allImage = soup.find_all('img')
```

## Работа с WorkWithJson
Так же как и Pars, WorkWithJson не принимает данных для конструктора

```py
# Импортируем библиотеку
from module import WorkWithJson
# Создаём объект класса
p = WorkWithJson()
```
### Коротко о методах

1. Метод **load** используется для получения данных из json-файла по указанному пути

2. Метод **dump** используется для записи данных в json-файл. Принимает путь до файла и данные для записи

```py
from module import WorkWithJson
w = WorkWithJson()
# Записываем данные
w.dump('./data.json',[1,2,3,4,5,6,7])
# Получаем данные
data = w.load('./data.json') 
print(data) # [1,2,3,4,5,6,7]
```

## Работа с WorkWithScv
По умолчанию класс WorkWithScv принимает два аргумента: символ переноса на новую строку "newline" (по умолчанию — это пустая строка), кодировку открываемых файлов "encoding" (по умолчанию cp1251) и разделитель который используется в csv файле "delimiter" (по умолчанию ";")

```py
# Импортируем библиотеку
from ipars import WorkWithScv
# Создаём объект класса
c = WorkWithScv()
```

### Коротко о методах

1. Метод **writerow** записывает строку с csv файл. Метод принимает путь до csv файла, метод записи и список данных которые будут записанн в строку файла

2. Метод **writerows** принимает теже самые аргументы что и writerow, только row должен быть двойным списком с данными для записи. Разница между этими методами в том что writerow записывает одну, а writerows столько сколько есть в двойном списке

3. Метод **getRows** используется для получения списка строк в csv файле. Метод принимает путь до файла откуда будут получены строки

```py
from ipars import WorkWithScv

c = WorkWithScv()
writer = c.writerow('./data.csv', 'w', ['Цена', 'Количество', 'Итог'])

writer = myCsv.writerows('./data.csv', 'a', [
    ["5", "5", "25"],
    ["6", "6", "36"],
    ["7", "7", "49"],
])

rows = myCsv.getRows('./data.csv')
print(rows)
for row in rows:
    print(row)
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.
