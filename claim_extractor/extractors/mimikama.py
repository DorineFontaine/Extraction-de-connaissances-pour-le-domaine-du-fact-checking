import requests
from typing import List

from bs4 import BeautifulSoup
from claim_extractor import Claim, Configuration
from claim_extractor.extractors import FactCheckingSiteExtractor, caching


class MimikamaFactchecking(FactCheckingSiteExtractor):

    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def retrieve_listing_page_urls(self) -> List[str]:
        return ["https://www.mimikama.at/faktencheck/"]

    # redefining the  abstract methods of the Factchecking class


    # find the number of page of the site
    def find_page_count(self,parsed_listing_page: BeautifulSoup) -> int:
        max = 0
        soup = parsed_listing_page.find_all('a', {'class': 'page-numbers'})
        soup.pop()
        for i in soup:
            m = int(i.text)
            if max < m:
                max = m
        return m

    # extraction of url of article of one page of the site
    def extract_urls(self,parsed_listing_page: BeautifulSoup):
        s = parsed_listing_page.select('h2.entry-title > a')
        url = list()
        for link in s:
            if link['href'] in url:
                break
            else:
                url.append(link['href'])

        return url

    # peut on remplacer cette methode par une autre ??? catching.get(...)
    def getUrl(url):
        requete = requests.get(url)
        page = requete.content
        return page

    # extraction of all the url of article in the site
    def retrieve_urls(self, parsed_listing_page: BeautifulSoup, number_of_pages: int) \
            -> List[str]:
        urls = self.extract_urls(parsed_listing_page)

        for page_number in range(1, number_of_pages):
            url = "https://www.mimikama.at/faktencheck/page/" + str(page_number) + '/'
            page = self.getUrl(url)
            if page:
                # on stocke le résultat de la page dans la variable current_parsed_listing_page
                current_parsed_listing_page = BeautifulSoup(page, "lxml")
                # on ajoute les urls de toutes les pages
                urls += self.extract_urls(current_parsed_listing_page)
            else:
                break

            return urls

    def extract_claim_and_review(self, parsed_claim_review_page: BeautifulSoup, url: str) -> List[Claim]:
        claim = Claim()
        claim.set_url(url)
        claim.set_source("mimikama")

        # title
        title = parsed_claim_review_page.find('h1').text
        claim.set_title(title)

        # author & author_url
        date_author = date_author = parsed_claim_review_page.find('div', {"class": "wp-block-kadence-advancedheading"}).text.split()
        claim.set_author(date_author[0] + " " + date_author[1])
        claim.set_date(date_author[3] + " " + date_author[4])

        # rating
        # machine learning

        # body_link
        body_link = parsed_claim_review_page.find("link", {"rel": "canonical"})["href"]

        # url
        url = parsed_claim_review_page.find("link", {"rel": "canonical"})["href"]

        return claim
