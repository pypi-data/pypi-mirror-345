# lib_missing_people_api

`lib_missing_people_api` это библиотека Python предоставляет api для получения информации о пропавших без вести и людях, которые в розыске - с сайтов

## Установка из PyPI

```bash
pip install lib_missing_people_api
```

## Использование репозитория GitHub

```bash
git clone https://github.com/YuranIgnatenko/lib_missing_people_api.git
cd lib_missing_people_api
pip install .
```

## Пример использования

```python
from lib_missing_people_api.parser import *

def test_sledkom():
	parser = ParserSledcom()
	ar1 = parser.get_array_people(DICT_URLS_SLEDCOM["БЕЗ ВЕСТИ"])
	for people in ar1:
		print("GET ARRAY PEOPLE",people.date_create, people.url_image, people.description)

def test_mvd():
	parser = ParserMvd()
	ar1 = parser.get_array_people(URL_SITE_MVD)
	for people in ar1:
		print("GET ARRAY PEOPLE",people.date_create, people.url_image, people.description)

def test_liza_alert():
	parser = ParserLizaAlert()
	ar1 = parser.get_array_people(URL_SITE_LIZAALERT)
	for people in ar1:
		print("GET ARRAY PEOPLE",people.date_create, people.url_image, people.description)

test_sledkom()
test_mvd()
test_liza_alert()

```

> using sources from site:

- `https://moscow.sledcom.ru/`
- `https://мвд.рф/wanted`
- `https://lizaalert.org/forum/viewforum.php`
- `https://lizaalert.org/forum/`
