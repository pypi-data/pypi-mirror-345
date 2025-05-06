from module import JsonManager, CsvManager
from pprint import pprint
j = JsonManager()
c = CsvManager()
data = j.load('./data.json')

# j.pprint(data)
c.pprint(data)
# pprint(data)