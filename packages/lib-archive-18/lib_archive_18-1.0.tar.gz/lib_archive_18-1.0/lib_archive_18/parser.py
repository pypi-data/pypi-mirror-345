import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

URL_LUDI = "https://world79.spcs.bio/sz/foto-i-kartinki/ljudi"
URL_ANIME = "https://world79.spcs.bio/sz/foto-i-kartinki/anime"
URL_ZNAMENITOSTI = "https://world79.spcs.bio/sz/foto-i-kartinki/znamenitosti"
URL_GAME = "https://world79.spcs.bio/sz/foto-i-kartinki/iz-igr"

class Parser():
	def __init__(self, url:str) -> None:	
		self._user_agent = UserAgent().random
		self._headers = {'User-Agent':self._user_agent}	
		self._cookies = {}
		self.URL_SRC = url
		self.COUNT_FILES_IN_ONCE_PAGE = 25

	def _build_url_page(self, number_page:int) -> str:
		return f"{self.URL_SRC}/p{number_page}/"
	
	def _get_soup(self, url:str) -> BeautifulSoup:
		response = requests.get(url, headers=self._headers, cookies=self._cookies)
		soup = BeautifulSoup(response.text, 'html.parser')
		return soup

	def get_count_pages(self) -> int:
		soup = self._get_soup(self.URL_SRC)
		tmp = []
		for link in soup.find_all('a'):
			href = link.get('href')
			if href and href.startswith('http'):
				if href.find('/p') != -1:
					tmp.append(href)
		t = int(tmp[-1].split('/')[-2][1:])
		return t

	def get_count_all_files(self) -> int:
		return self.COUNT_FILES_IN_ONCE_PAGE * self.get_count_pages()

	def get_files(self, number_page:int) -> list[str]:
		soup = self._get_soup(self._build_url_page(number_page))
		tmp = []
		t = 0
		for link in soup.find_all('a'):
			href = link.get('href')
			if href and href.startswith('http'):
				if href.find('/view') != -1:
					soup = self._get_soup(href)
					tmp_d = []
					for link in soup.find_all('a'):
						href = link.get('href')
						if href and href.startswith('http'):
							if href.find("download") != -1:
								tmp_d.append(href)
					if len(tmp_d) == 0: continue
					t+=1
					tmp.append(tmp_d[-1].replace("jpg","png"))
		return tmp


	def get_files_iterator(self, start_page=1, max_files:int=1):
		'''if max=-1 : run loop with ended
		default max=1'''
		counter_files = 0
		for number_page in range(start_page,self.get_count_pages()-1):
			soup = self._get_soup(self._build_url_page(number_page))
			for link in soup.find_all('a'):
				href = link.get('href')
				if href and href.startswith('http'):
					if href.find('/view') != -1:
						soup = self._get_soup(href)
						for link in soup.find_all('a'):
							href = link.get('href')
							if href and href.startswith('http'):
								if href.find("download") != -1:
									if counter_files < max_files or counter_files == -1:
										counter_files += 1
										yield href.replace("jpg","png")
									elif counter_files == max_files:
										return 
