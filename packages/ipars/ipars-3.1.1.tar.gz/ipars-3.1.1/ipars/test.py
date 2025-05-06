from ipars import Pars
p = Pars()

# Получаем картинку
p.get_static_page(
    pathToSaveFile="./logo.png",
    url="https://cdn.sstatic.net/Sites/stackoverflow/Img/icon-48.png?v=b7e36f88ff92",
    writeMethod='wb'
)