import requests, aiohttp, random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

URL_LUDI = "https://world79.spcs.bio/sz/foto-i-kartinki/ljudi/"
URL_ANIME = "https://world79.spcs.bio/sz/foto-i-kartinki/anime/"
URL_ZNAMENITOSTI = "https://world79.spcs.bio/sz/foto-i-kartinki/znamenitosti/"
URL_GAME = "https://world79.spcs.bio/sz/foto-i-kartinki/iz-igr/"
URL_WALLPAPERS_PC = "https://world79.spcs.bio/sz/foto-i-kartinki/oboi-dlja-pk/"
URL_HUMOR_I_PRICOLY = "https://world79.spcs.bio/sz/foto-i-kartinki/jumor-prikoly/"
URL_ABSTRAKT = "https://world79.spcs.bio/sz/foto-i-kartinki/abstraktnye/"
URL_PICTURE_ANEKTODY = "https://world79.spcs.bio/sz/foto-i-kartinki/anekdoty/"
URL_ANIMALS = "https://world79.spcs.bio/sz/foto-i-kartinki/zhivotnyj-mir/"
URL_ISCUSSTVO_DRAWING = "https://world79.spcs.bio/sz/foto-i-kartinki/iskusstvo-risunki/"
URL_AI_ART = "https://world79.spcs.bio/sz/foto-i-kartinki/ai-art/"
URL_KLIP_ART = "https://world79.spcs.bio/sz/foto-i-kartinki/klipart/"
URL_COSMOS = "https://world79.spcs.bio/sz/foto-i-kartinki/kosmos/"
URL_COMICS = "https://world79.spcs.bio/sz/foto-i-kartinki/komiksy/"
URL_RECEPTY = "https://world79.spcs.bio/sz/foto-i-kartinki/kulinarija/"
URL_LUBOV = "https://world79.spcs.bio/sz/foto-i-kartinki/ljubov/"
URL_MEMY = "https://world79.spcs.bio/sz/foto-i-kartinki/memy/"
URL_MOTIVATORS = "https://world79.spcs.bio/sz/foto-i-kartinki/motivatory/"
URL_CITATY = "https://world79.spcs.bio/sz/foto-i-kartinki/citaty-aforizmy/"

class Parser():
	def __init__(self, url:str) -> None:	
		self._user_agent = UserAgent().random
		self._headers = {'User-Agent':self._user_agent}	
		self._cookies = {}
		self.URL_SRC = url
		self.COUNT_FILES_IN_ONCE_PAGE = 25

	def _build_url_page(self, number_page:int) -> str:
		return f"{self.URL_SRC}p{number_page}/"
	
	def _get_soup(self, url:str) -> BeautifulSoup:
		response = requests.get(url, headers=self._headers)
		soup = BeautifulSoup(response.text, 'html.parser')
		# TODO: for parsing 18+ content
		# if "Если вам менее 18 лет - нажмите НЕТ." in f"{soup}":
		# 	hrefs = [link.get('href') for link in soup.find_all("a")]
		# 	for href in hrefs:
		# 		if href and href.startswith('http'):
		# 			if "settings/safe_mode" in href:
		# 				result = self._get_soup(url)
		# 				return result
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


	def get_files_iterator(self, start_page=1, stop_page:int=2):
		for number_page in range(start_page,stop_page):
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
										yield href.replace("jpg","png")

	async def get_random_file(self) -> str:
		number_page = random.randint(1, self.get_count_pages()-1)
		url = self._build_url_page(number_page)
		async with aiohttp.ClientSession() as session:
			async with session.get(url, headers=self._headers) as response:
				html = await response.text()
				response = requests.get(url, headers=self._headers)
				soup = BeautifulSoup(response.text, 'html.parser')
				for link in soup.find_all('a'):
					href = link.get('href')
					if href and href.startswith('http'):
						if href.find('/view') != -1:
							soup = self._get_soup(href)
							for link in soup.find_all('a'):
								href = link.get('href')
								if href and href.startswith('http'):
									if href.find("download") != -1:
										return href.replace("jpg","png")

