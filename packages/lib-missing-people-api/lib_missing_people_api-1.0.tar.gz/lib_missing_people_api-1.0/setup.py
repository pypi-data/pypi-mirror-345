from setuptools import setup, find_packages

setup(
	name='lib_missing_people_api',
	version='1.0',
	packages=find_packages(),
	install_requires=[
		'requests',
		'beautifulsoup4',
		'fake_useragent',
	],
	description='Library-api for scrapping missing people',
	long_description=open('README.md', encoding='utf-8').read(),
	long_description_content_type="text/markdown",
	author='Yurij',
	author_email='yuran.ignatenko@yander.ru',
	url='https://github.com/YuranIgnatenko/lib_missing_people_api',
)