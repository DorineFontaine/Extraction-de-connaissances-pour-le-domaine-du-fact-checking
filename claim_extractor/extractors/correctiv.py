import requests
from typing import List

from bs4 import BeautifulSoup
from claim_extractor import Claim, Configuration
from claim_extractor.extractors import FactCheckingSiteExtractor


class CorrectivFactcheking(FactCheckingSiteExtractor):

    def find_page_count(self, parsed_listing_page: BeautifulSoup) -> int:
        pass

    def retrieve_urls(self, parsed_listing_page: BeautifulSoup, listing_page_url: str, number_of_pages: int) -> List[
        str]:
        pass

    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def retrieve_listing_page_urls(self) -> List[str]:
        return ["https://correctiv.org/faktencheck/"]

    def extract_urls(self, parsed_listing_page: BeautifulSoup):
        s = parsed_listing_page.find_all('div', {'class':'widget-post size--6 size--m-12'})
        url = list()
        for i in s:
            for link in i.find_all('a', href=True):
                if link['href'] in url:
                    break
                else:
                    url.append(link['href'])

        return url

    def extract_claim_and_review(self, parsed_claim_review_page: BeautifulSoup, url: str) -> List[Claim]:
        claim = Claim()
        claim.set_url(url)
        claim.set_source("correctiv")

        # title
        title = parsed_claim_review_page.find('h1', {"class": "secondary-title"}).text
        claim.set_title(title)

        # rating
        rating = parsed_claim_review_page.find('div', {'class': 'elementor-heading-title elementor-size-default'}).text
        claim.set_rating(rating)

        # Auteur peut ne pas etre présent
        if parsed_claim_review_page.find('a', {'class': 'detail__authors-link'}):
            author = parsed_claim_review_page.find('a', {'class': 'detail__authors-link'}).text
            author_url = parsed_claim_review_page.find('a', {'class': 'detail__authors-link'}, href=True)
            author_url = author_url['href']

        claim.set_author(author)

        date = parsed_claim_review_page.find('time', {"class": "detail__date"}).text
        claim.set_date(date)

        return claim
