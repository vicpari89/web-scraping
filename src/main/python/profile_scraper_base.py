import requests
from bs4 import BeautifulSoup
import os
import pandas as pd

URL_SCRAP = 'https://profile.es/blog'
CSV_PATH = '../resources/'
CSV_NAME = 'profile_scrap.csv'


class ProfileScraperBase:

    def __init__(self, url_scrap):
        self.articles = []
        self.url_scrap = url_scrap
        self.i = 1

    def scrap(self):
        self.extract_page(URL_SCRAP)
        self.export_data()

    def extract_page(self, url):
        response = requests.get(url)

        if response.status_code == 200:
            print("Extrayendo pagina " + str(self.i))
            bs_response = BeautifulSoup(response.content, features="html.parser")
            self.extract_articles(bs_response)
            div_next_page = bs_response.find("div", {"class": "e-load-more-anchor"})
            if div_next_page:
                self.i = self.i + 1
                next_page = div_next_page['data-next-page']
                if next_page:
                    self.extract_page(next_page)

    def extract_articles(self, bs_response):
        div_post_container = bs_response.find("div", {"class": "elementor-posts-container"})
        if div_post_container:
            for article in div_post_container.find_all('article'):
                self.articles.append(self.extract_article(article))

    @staticmethod
    def extract_article(article):
        article_data = {
            'image': article.find("div", {"class": "elementor-post__thumbnail"}).img['src'],
            'category': article.find("div", {"class": "elementor-post__badge"}).text.strip(),
            'title': article.find("h3", {"class": "elementor-post__title"}).a.text.strip(),
            'extract': article.find("div", {"class": "elementor-post__excerpt"}).p.text.strip(),
            'detail_url': article.find("a", {"class": "elementor-post__read-more"})['href'],
            'date': article.find("span", {"class": "elementor-post-date"}).text.strip()
        }
        return article_data

    def export_data(self):
        dir_path = os.getcwd()
        df_articles = pd.DataFrame(self.articles)
        header = self.articles[0].keys()
        df_articles.to_csv(CSV_PATH + CSV_NAME, sep=";", header=header)


if __name__ == "__main__":
    ProfileScraperBase(URL_SCRAP).scrap()
