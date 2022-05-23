import requests
from typing import List
import urllib.request as urllib2
from bs4 import BeautifulSoup
from claim_extractor import Claim, Configuration
from claim_extractor.extractors import FactCheckingSiteExtractor, caching


class LogicalyFactChecking(FactCheckingSiteExtractor):

    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def retrieve_listing_page_urls(self) -> List[str]:
        return ["https://www.logically.ai/factchecks/library"]

    def find_page_count(self,parsed_listing_page: BeautifulSoup) -> int:
        count = 0
        a = soup.find('a', {'class': 'blog-pagination__next-link'})['href']
        if a:
            while a:

                count += 1
                url = "https://www.logically.ai/factchecks/library/page/" + str(count)
                if checkURL(url):

                    soupi = BeautifulSoup(getUrl(url))
                    a = soupi.find('a', {'class': 'blog-pagination__next-link'})['href']

                else:

                    break

        return count - 1



    def extract_urls(self, parsed_listing_page: BeautifulSoup):
        s = parsed_listing_page.find_all('article', {'class':'grid-item-4'})
        url = list()
        for i in s:
            for link in i.find_all('a', href=True):
                if link['href'] in url:
                    break
                else:
                    url.append(link['href'])

        return url

    def getUrl(url):
        requete = requests.get(url)
        page = requete.content
        return page

    def checkURL(url):
        req = urllib2.Request(url)
        try:
            handle = urllib2.urlopen(req)
        except IOError:

            return False
        else:

            return True

    def retrieve_urls(self, parsed_listing_page: BeautifulSoup, number_of_pages: int) \
            -> List[str]:

        urls = self.extract_urls(parsed_listing_page)

        for page_number in range(1, number_of_pages):
            url = "https://www.logically.ai/factchecks/page/" + str(page_number)
            # page = caching.get(url, headers=self.headers, timeout=5)

            # a voir pour la methode getUrl
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
            claim.set_source("logically")

            # title
            title = parsed_claim_review_page.find('h1').text
            claim.set_title(title)

            # author & author_url
            if parsed_claim_review_page.select('p.fc-posted-by > a'):
                for author in parsed_claim_review_page.select('p.fc-posted-by > a'):
                    author_str = author.text.split("|")[0].strip().split("\n")[0]  # gerer lorsque il n'y a pas d'auteur ?
                    author_url = author["href"]

            claim.set_author(author_str)

            # rating
            rating = parsed_claim_review_page.find("div", {"class": "hs_cos_wrapper hs_cos_wrapper_widget hs_cos_wrapper_type_module widget-type-text"}).text
            claim.set_rating(rating)

            # body_link
            body_link = parsed_claim_review_page.find("link", {"rel": "canonical"})["href"]



            return claim
