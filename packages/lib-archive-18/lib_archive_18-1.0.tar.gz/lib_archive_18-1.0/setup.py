from setuptools import setup, find_packages

setup(
	name='lib_archive_18',
	version='1.0',
	packages=find_packages(),
	install_requires=[
		'requests',
		'beautifulsoup4',
		'fake_useragent',
	],
	description='Library for access files',
	long_description=open('README.md', encoding='utf-8').read(),
	long_description_content_type="text/markdown",
	author='Yurij',
	author_email='yuran.ignatenko@yander.ru',
	url='https://github.com/YuranIgnatenko/lib_archive_18',
)