import logging
import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re


logging.basicConfig(
    format='%(asctime)s %(levelname)s:%(message)s',
    level=logging.INFO)

class Crawler:
    #apo ton web crawler xreiazomaste to 1o/start url kai meta ta urls pou episkeptomaste oso trexei o kwdikas
    def __init__(self, start_url):
        self.start_url = start_url
        self.visited_urls = set()

    #kanei fetch ta html dedomena apo kathe url
    def download_url(self, url):
        return requests.get(url).text
    
    #kanei fetch ta onomata twn epistimonon apo to arxiko url kai krataei mono to epitheto apo ton titlo tou kathe url
    def parse_scientists_list(self, html):
        soup = BeautifulSoup(html, 'html.parser') #me to soup pairno data apo to kathe html
        scientists = []
        main_content = soup.find(id="mw-content-text") #contents se kathe wikipedia
        if main_content:
            list_items = main_content.find_all('li')
            for li in list_items:
                first_link = li.find('a')
                #an vrethei url gia enan episthmona, pairnei ton titlo apo to url kai ton xwrizei me tropo wste to epitheto na apomonothei
                #epitheto theoroume ean h "leksi" ksekinaei me to 1o gramma kefalaio
                #telos to epitheto prostithetai sto scientist list
                if first_link and first_link.get('href').startswith('/wiki/'):
                    scientist_url = urljoin(self.start_url, first_link.get('href'))#gia na sindethoun 2 urls
                    url_parts = scientist_url.split('/')[-1].split('_')
                    potential_surname = url_parts[-1] #to teleftaio part apo to fullname einai to epitheto
                    if potential_surname[0].isupper() and potential_surname.isalpha():
                        scientists.append({'url': scientist_url, 'surname': potential_surname})
        return scientists

    def parse_scientist_page(self, url):
        try:
            html = self.download_url(url)
            soup = BeautifulSoup(html, 'html.parser')
            awards_count = 0
            awards_text = ""

            #psakse gia ta sections pou periexoun to 'award'
            for heading in soup.find_all(['h2', 'h3']):#gia sections kai subsections
                if 'award' in heading.text.lower():
                    next_node = heading.find_next_sibling()
                    while next_node and next_node.name not in ['h2', 'h3']:
                        if next_node.name in ['ul', 'ol']:
                            awards_count += len(next_node.find_all('li'))
                        else:
                            awards_text += " " + next_node.get_text(" ", strip=True)
                        next_node = next_node.find_next_sibling()

            if awards_count == 0 and awards_text:
                awards_count = len(re.findall(r'\b\d{4}\b', awards_text))

            #EDUCATION
            education_info = "Null"
            search_terms = ["univers", "institut", "school"] #einai i lista pou checkarei tous orous me proteraiothta ston 1o oro stin lista etc.

            for term in search_terms:
                if education_info != "Null":
                    break #molis vrethei to 1o,stop thn anazitisi
                links = soup.find_all('a', href=True)
                for link in links:
                    if term in link.text.lower() and link.text.strip() and not any(char.isdigit() for char in link.text):
                        education_info = link.text.strip()
                        break

            return awards_count, education_info
        except Exception as e:
            logging.exception(f'Error parsing scientist page: {url}')
            return None, None


    #dimiourgeitai to csv kai fortonei tis listes pou dimiourghthikan parapano
    def run(self):
        with open('computer_scientists.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Surname', 'Awards', 'Education'])
            html = self.download_url(self.start_url)
            scientists = self.parse_scientists_list(html)
            for scientist in scientists:
                if scientist['url'] not in self.visited_urls:
                    try:
                        awards, education = self.parse_scientist_page(scientist['url'])
                        writer.writerow([scientist['surname'], awards, education])
                    except Exception as e:
                        logging.exception(f'Failed to parse page: {scientist["url"]}')
                    finally:
                        self.visited_urls.add(scientist['url'])

#i main pou kalei ton crawler gia to url pou dinetai sthn ekfonisi
if __name__ == '__main__':
    Crawler(start_url='https://en.wikipedia.org/wiki/List_of_computer_scientists').run()
