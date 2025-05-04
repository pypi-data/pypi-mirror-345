class MissingPeople():
	def __init__(self, title:str, url_image:str, date_create:str, url_html_page:str, description:str, id:str) -> None:
		self.url_image = url_image
		self.date_create = date_create 
		self.url_html_page = url_html_page
		self.description =  description
		self.title = title
		self.id = id
	def get_id(self):
		return self.url_html_page.split("/")[-2]

