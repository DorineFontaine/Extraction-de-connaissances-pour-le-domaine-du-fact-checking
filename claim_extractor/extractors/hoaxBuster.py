import re
from typing import List, Set
from bs4 import BeautifulSoup
from dateparser.search import search_dates
from tqdm import tqdm

from claim_extractor import Claim, Configuration
from claim_extractor.extractors import FactCheckingSiteExtractor, caching


class HoaxBusterFactCheckingSiteExtractor(FactCheckingSiteExtractor):

    def __init__(self, configuration: Configuration):
        super().__init__(configuration)

    def retrieve_listing_page_urls(self) -> List[str]:
        return ['https://hoaxbuster.com']

    def find_page_count(self, parsed_listing_page: BeautifulSoup) -> int:
        return 7

    def extract_urls(self, parsed_listing_page: BeautifulSoup) \
            -> List[str]:
        urls = []
        listing_container = parsed_listing_page.findAll("div", {"class": "title_article"})
        for article in listing_container:
            anchor = article.find("a")
            url = anchor['href']
            urls = urls + [URL + "" + url]
        return urls

    def retrieve_urls(self, parsed_listing_page: BeautifulSoup, listing_page_url: str, number_of_pages: int) \
            -> List[str]:
        urls = list()
        pages_names = ['covid19', 'medias-et-techno', 'politique', 'environnement', 'societe', 'sciences', 'sante']
        for name in pages_names:
            url = listing_page_url + "/" + name
            page = getUrl(url)
            if page:
                current_parsed_listing_page = BeautifulSoup(page, "lxml")
                urls = urls + (self.extract_urls(current_parsed_listing_page))
        return urls

    def extract_claim_and_review(parsed_claim_review_page: BeautifulSoup, url: str) -> List[Claim]:
        claim = Claim()
        claim.set_url(url)
        claim.set_source("hoaxBuster")
        title = parsed_claim_review_page.find('h1', {"class": "title_article_page"})
        claim.title = title.text
        print(claim.title)

        claimm = parsed_claim_review_page.find("h2", {"class": "description_article_page"})
        claim.set_claim(claimm.text)
        print(claim.claim)

        truth_section = parsed_claim_review_page.find("div", {"class": "info_article_page_top"})
        truth_name = truth_section.contents[1]['title']
        if translate_rating_value(truth_name) != "":
            claim.rating = translate_rating_value(truth_name)
        else:
            claim.rating = truth_name
        print(claim.rating)
        date = parsed_claim_review_page.find("div", {"class": "info_article_page_top"}).contents[4]
        if date:
            date_str = search_dates(date)[0][1].strftime("%Y-%m-%d")
            claim.set_date(date_str)
        print(claim.date)

        author_meta = parsed_claim_review_page.find("div", {"class": "info_article_page_top"})
        if author_meta:
            author = author_meta.find("a").text
            claim.set_author(author)
            author_url = author_meta.find("a")
            if author_url.attrs["href"] != "":
                claim.author_url = 'https://hoaxbuster.com/' + author_url.attrs["href"]
        print(claim.author)
        print(claim.author_url)

        text = ""
        div_text = parsed_claim_review_page.find("div", {"class:", "contenu_page"})
        if div_text:
            paragraphs = div_text.findAll("p")
            for p in paragraphs:
                text += p.text
            body_description = text.strip()
            claim.body = str(body_description).strip()
            print(claim.body)

        tags = []
        div_tag = parsed_claim_review_page.find("div", {"class", "keyword_section"})
        for link in div_tag.findAll("a", href=True):
            tags.append(link.text)
        claim.set_tags(tags)
        print(claim.tags)

        div_tag = parsed_claim_review_page.find("div", {"class:", "contenu_page"})
        related_links = []
        for link in div_tag.find_all('a', href=True):
            if (link['href'][0] == "/"):
                related_links.append("https://www.hoaxbuster.com" + link['href'])
            else:
                related_links.append(link['href'])
        claim.set_refered_links(related_links)
        print(claim.referred_links)

        related_div = parsed_claim_review_page.findAll("div", {"class:", "partenaire"})
        if related_div:

            for div in related_div:
                link = div.find("a", href=True)
                try:
                    if hasattr(link, 'href'):
                        if 'http' in link['href']:
                            related_links.append(link['href'])
                        else:
                            related_links.append(
                                "https://hoaxbuster.com" + link['href'])
                except KeyError as e:
                    print("->KeyError: " + str(e))
                    continue
                except IndexError as e:
                    print("->IndexError: " + str(e))
                    continue
        if related_links:
            claim.related_links = related_links
        print(claim.related_links)

        return [claim]

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
