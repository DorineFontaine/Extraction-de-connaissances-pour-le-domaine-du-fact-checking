import re
from typing import List, Set
from bs4 import BeautifulSoup
from dateparser.search import search_dates
from tqdm import tqdm
import urllib.request as urllib2
import socket

from claim_extractor import Claim, Configuration
from claim_extractor.extractors import FactCheckingSiteExtractor, caching


class ClimateFeedBackFactCheckingSiteExtractor(FactCheckingSiteExtractor):

    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def retrieve_listing_page_urls(self) -> List[str]:
        return ['https://climatefeedback.org/']

    def find_page_count(self, parsed_listing_page: BeautifulSoup) -> int:
        count = 2
        a = soup.find('a', {'class': 'next'})
        while (a):
            url = "https://climatefeedback.org/claim-reviews/" + str(count) + "/?page=" + str(count + 1)
            if check_url:
                count += 1
                soupi = BeautifulSoup(getUrl(url))
                a = soupi.find('a', {'class': 'next'})
            else:
                break
        return (count)

    def extract_urls(self, parsed_listing_page: BeautifulSoup) \
            -> List[str]:
        urls = []
        listing_container = parsed_listing_page.findAll("a", {"class": "strong"})
        for article in listing_container:
            url = article['href']
            urls = urls + [url]
        return urls

    def retrieve_urls(self, parsed_listing_page: BeautifulSoup, number_of_pages: int) \
            -> List[str]:

        urls = self.extract_urls(parsed_listing_page)
        for page_number in range(2, number_of_pages + 1):
            url = "https://climatefeedback.org/claim-reviews/" + str(page_number) + "/"
            # page = caching.get(url, headers=self.headers, timeout=5)
            page = getUrl(url)
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
        claim.set_source("ClimatFeedback")
        title = parsed_claim_review_page.find('h1', {"class": "entry-title"})
        claim.title = title.text
        print(claim.title)

        claim.url = url
        print(claim.url)

        claimm = parsed_claim_review_page.find("div", {"class": "claimshort"})
        claim.set_claim(claimm.text)
        print(claim.claim)

        truth_section = parsed_claim_review_page.find("img", {"class": "fact-check-card__row__verdict__img"})[
            'src'].split('/')
        truth_name = truth_section[len(truth_section) - 1].split('.')[0].split('_')[1].lower()
        if translate_rating_value(truth_name) != "":
            claim.rating = translate_rating_value(truth_name)
        print(claim.rating)

        date_container = parsed_claim_review_page.find("span",
                                                       {"class": "fact-check-card__details__text small"}).contents
        date = date_container[len(date_container) - 2].split(',')[1]
        if date:
            date_str = search_dates(date)[0][1].strftime("%Y-%m-%d")
            claim.date_published = date_str
        print(claim.date)

        date_container = \
        parsed_claim_review_page.findAll("p", {"class": "small"})[1].contents[0].split(':')[1].split('|')[0]
        claim.date = date_container
        print(claim.date)

        author_meta = parsed_claim_review_page.find("span", {"class": "fact-check-card__details__text small"})
        author_list = ""
        author_url_list = ""
        if author_meta:
            authors = author_meta.findAll("a", href=True)
            for author in authors:
                if author['href'].split('/')[3] == "authors":
                    author_list = author_list + author.text + ","
                    author_url_list = author_url_list + author['href'] + ','
            author_list = author_list[0:len(author_list) - 1]
            author_url_list = author_url_list[0:len(author_url_list) - 1]
            claim.author = author_list
            claim.author_url = author_url_list

        print(claim.author)
        # print(claim.author_url)

        text = ""
        div_text = parsed_claim_review_page.find("div", {"class:", "entry-content"})
        if div_text:
            paragraphs = div_text.findAll("p")
            for p in paragraphs:
                text += p.text
            body_description = text.strip()
            claim.body = str(body_description).strip()
            print(claim.body)

        tags = []
        span_tag = parsed_claim_review_page.findAll("span", {"class", "bot-tag"})
        for item in span_tag:
            tags.append(item.find('a', href=True).text)
        claim.set_tags(tags)
        print(claim.tags)

        div_links = parsed_claim_review_page.find("div", {"class": "entry-content"})
        referred_links = div_links.findAll("a", href=True)
        related_links = []
        for link in referred_links:
            related_links.append(link['href'])
        claim.set_refered_links(related_links)
        print(claim.referred_links)

        related_links = []
        related_div = div_links.findAll("ul")
        for ul in related_div:
            if ul:
                link = ul.findAll("li")
                for li in link:
                    if li:
                        l = li.find("a", href=True)
                        if l:
                            related_links.append(l['href'])
        claim.related_links = related_links
        print(claim.related_links)

        review_authors = ""
        reviewers_div = parsed_claim_review_page.findAll("div", {"class": "wid-body"})
        for div in reviewers_div:
            review_authors += div.find("a", href=True).text + ","
        review_authors = review_authors[0:len(review_authors) - 1]
        claim.review_author = review_authors
        print(claim.review_author)

        return [claim]

    def getUrl(url):
        requete = requests.get(url)
        page = requete.content
        return page


def check_url(url, timeout=5):
    try:
        return urllib2.urlopen(url, timeout=timeout).getcode() == 200
    except urllib2.URLError as e:
        return False
    except socket.timeout as e:
        return False


def translate_rating_value(self, initial_rating_value: str) -> str:
    dictionary = {
        "true": "True",
        "mostly-true": "Mostly True",
        "half-true": "Half False",
        "barely-true": "Mostly False",
        "false": "False",
        "pants-fire": "Pants on Fire"
    }

    if initial_rating_value in dictionary:
        return dictionary[initial_rating_value]
    else:
        return ""