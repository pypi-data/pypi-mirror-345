import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent 
from  models import MissingPeople 

URL_SITE_SLEDCOM = "https://moscow.sledcom.ru/"
URL_SITE_MVD = "https://мвд.рф/wanted"
URL_SITE_LIZAALERT = "https://lizaalert.org/forum/viewforum.php?f=276"
URL_SITE_LIZAALERT_FORUM = "https://lizaalert.org/forum/"

KEY_SLEDCOM_DETI = "ДЕТИ"
KEY_SLEDCOM_POGIBSHIE = "ПОГИБШИЕ"
KEY_SLEDCOM_PODOZREVAEMIE = "ПОДОЗРЕВАЕМЫЕ"
KEY_SLEDCOM_BEZ_VESTI = "БЕЗ ВЕСТИ"

DICT_URLS_SLEDCOM = {
	KEY_SLEDCOM_DETI:"https://moscow.sledcom.ru/attention/Vnimanie_Propal_rebenok",
	KEY_SLEDCOM_POGIBSHIE:"https://moscow.sledcom.ru/attention/Neopoznannye-trupy",
	KEY_SLEDCOM_PODOZREVAEMIE:"https://moscow.sledcom.ru/attention/Podozrevaemie_v_sovershenii_prestuplenij",
	KEY_SLEDCOM_BEZ_VESTI:"https://moscow.sledcom.ru/folder/918943",
}



def MissingPeopleFromSoup(soup_section:BeautifulSoup) -> MissingPeople:

	try:
		temp_title = soup_section.find("div", class_="bl-item-holder").find("div", class_="bl-item-title").find("a").text
	except:
		temp_title = soup_section.find("div", class_="bl-item-holder").find("div", class_="bl-item-title").find("a").text

	try:
		url_image = URL_SITE_SLEDCOM+soup_section.find("div", class_="bl-item-image").find("a").find("img").get("src")
	except:
		url_image = "/static/img/alert.jpg"

	try:
		description = soup_section.find("div", class_="bl-item-holder").find("div", class_="bl-item-text")
		description = "\n".join([t.find("span").text for t in description.find_all("p")])
	except:
		description = soup_section.find("div", class_="bl-item-holder").find("div", class_="bl-item-text")
		description = "\n".join([t.text for t in description.find_all("p")])

	try:
		url_html_page = soup_section.find("div", class_="bl-item-title").find("a").get("href")
	except:
		url_html_page = soup_section.find("div", class_="bl-item-title").find("a").get("href")


	id = f"{url_html_page.split("/")[-2]}"

	return MissingPeople(temp_title, url_image,temp_title,url_html_page,description, id)


class ParserSledcom():
	def __init__(self) -> None:
		self.headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
		self.cookies  = {
			"bh" : "EkwiTm90IEEoQnJhbmQiO3Y9IjgiLCJDaHJvbWl1bSI7dj0iMTMyIiwiWWFCcm93c2VyIjt2PSIyNS4yIiwiWW93c2VyIjt2PSIyLjUiGgN4ODYiCjI1LjIuMS44ODcqAj8wOgdXaW5kb3dzQgYxMC4wLjBKAjY0UmMiTm90IEEoQnJhbmQiO3Y9IjguMC4wLjAiLCJDaHJvbWl1bSI7dj0iMTMyLjAuNjgzNC44ODciLCJZYUJyb3dzZXIiO3Y9IjI1LjIuMS44ODciLCJZb3dzZXIiO3Y9IjIuNSJaAj8wYKzMkb4G",
			"Session_id":"3:1740876007.5.0.1724784552353:BagZXg:b90d.1.2:1|306336913.-1.2.2:14232801.3:1739017353|3:10303801.65629.QO_tI8IucN_7U7GEGmXGoNfWDZ4",
			"yandex_login":"Yuran.Ignatenko",
			"yandexuid":"2083661171724784397"
		}

	def get_profile_people(self, html_page_url:str) -> MissingPeople:
		response = requests.get(URL_SITE_SLEDCOM+html_page_url, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')

		soup_section = soup.find('section', class_="b-container-center")

		
		temp_title = soup_section.find("h1", class_="b-topic").text

		try:
			url_image = URL_SITE_SLEDCOM+soup_section.find("article", class_="c-detail").find("img", class_="img_left").get("src")
		except:
			url_image = "/static/img/alert.jpg"

		try:
			description = soup_section.find("article", class_="c-detail")
			description = "\n".join([t.find("span").text for t in description.find_all("p")])
		except:
			description = soup_section.find("article", class_="c-detail")
			description = "\n".join([t.text for t in description.find_all("p")])

		temp_url_page = URL_SITE_SLEDCOM+html_page_url


		id = f"{temp_url_page.split("/")[-2]}"

		return MissingPeople(temp_title, url_image,temp_title,temp_url_page,description, id)

	def get_array_people(self, url_directory:str) -> list[MissingPeople]:
		url_clean_web_site = URL_SITE_SLEDCOM
		temp_array_missing_people = []
		for html_page_url in self.get_url_pages(url_directory):
			html_page_url = "/".join(list(dict.fromkeys(html_page_url.split("/"))))+"/"
			response = requests.get(html_page_url, headers=self.headers, cookies=self.cookies)
			soup = BeautifulSoup(response.text, 'html.parser')

			for item_people in soup.find('section', class_="b-container-center").find_all("div", class_="bl-item clearfix"):
				temp_array_missing_people.append(MissingPeopleFromSoup(URL_SITE_SLEDCOM, item_people))

	
		return temp_array_missing_people

	def get_number_count_html_pages(self, url:str) -> int:
		response = requests.get(url, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')
		temp_array_peoples = []
		for divs in soup.find_all('div', class_="b-pagination"):
			for div in divs:
				div_str = str(div)
				if div_str.startswith(r'<a href="/folder/'):
					temp_array_peoples.append(div_str)
		last_item = temp_array_peoples[-1]
		count_number_page = int(last_item.split("/")[3])
		return count_number_page

	def get_url_pages(self, url:str) -> list[str]:
		response = requests.get(url, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')
		temp_array_peoples = []
		for divs in soup.find_all('div', class_="b-pagination"):
			for div in divs:
				div_str = str(div)
				if div_str.startswith(r'<a href="/'):
					temp_url_page = url+div_str.split('="')[1].split('">')[0]
					temp_array_peoples.append(temp_url_page)
		if len(temp_array_peoples) == 0:
			temp_array_peoples.append(url)
		return temp_array_peoples


class ParserMvd():
	def __init__(self) -> None:
		self._user_agent = UserAgent().random
		self.headers = {'User-Agent':self._user_agent}
		self.cookies  = {}

	def get_array_people(self, url:str) -> list[str]:
		self._user_agent = UserAgent().random
		self.headers = {'User-Agent':self._user_agent}
		try:
			response = requests.get(url, headers=self.headers, cookies=self.cookies)
		except requests.exceptions.ConnectionError:
			return []
		except ArithmeticError:
			print(self.headers)
			return []
		soup = BeautifulSoup(response.text, 'html.parser')
		
		temp_array_peoples = []

		for div in soup.find('div', class_="section-list type-10 m-t3 m-b2").find("div", class_="sl-holder").find_all("div", class_="sl-item"):
			url_image =  "http:"+div.find("div", class_="sl-item-image").find("a", class_="e-popup_html").find("img").get("src")
			name = div.find("div", class_="sl-item-title").find("a", class_="e-popup_html").text
			temp_array_peoples.append(MissingPeople(name, url_image,"no",url, "Розыск !", name.replace(" ", "")))

		return temp_array_peoples


class ParserLizaAlert():
	def __init__(self) -> None:
		self.headers = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}
		self.cookies  = {}

	def get_people(self, url_html_page:str) -> MissingPeople:
		response = requests.get(url_html_page, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')

		title = soup.find("div", class_="postbody").find("h3", class_="first").find("a").text
		try:
			url_image = soup.find("div", class_="postbody").find("div", class_="content").find("img", class_="postimage").get('src')
		except:
			url_image = "/static/img/alert.jpg"
		date_create = soup.find("div", class_="postbody").find("p", class_="author").find("time").text
		description = soup.find("div", class_="content").text

		id = url_html_page.split("sid=")[-1]
		return MissingPeople(title, url_image, date_create, url_html_page,description,id)

	def get_array_people(self, url:str) -> list[str]:
		response = requests.get(url, headers=self.headers, cookies=self.cookies)
		soup = BeautifulSoup(response.text, 'html.parser')
		
		temp_array_peoples = []

		for div in soup.find("div", class_="forumbg").find('ul', class_="topiclist topics").find_all("li", class_="row bg1"):
			url_html_page = URL_SITE_LIZAALERT_FORUM + div.find("a").get("href")[2:]
			people = self.get_people(url_html_page)
			temp_array_peoples.append(people)
		return temp_array_peoples


