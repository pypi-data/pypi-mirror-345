from bs4 import BeautifulSoup
import requests
import pandas as pd

class RecipeScraper:
    def __init__(self) -> None:
        self.soup = None
        self.data_frame = None

    def scrape_url(self, url: str) -> None:
        response = requests.get(url)
        response.encoding = 'utf-8'
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def get_tables_data(self) -> pd.DataFrame:
        tables = self.soup.find_all('table')[1:]
        headers = self.soup.find_all('h2')
        data_tables = []
        for i, table in enumerate(tables):
            table_rows = table.find_all('tr')[1:]
            data_tables.append({'table_name': headers[i].text,
                                'table_data': []})

            for row in table_rows:
                cells = row.find_all('td')
                data_tables[i]["table_data"].append({
                    'name': cells[0].text,
                    'ingradients': cells[1].text,
                    'image': cells[2].find('img')['src'],
                    'description': cells[3].text
                })
        self.data_frame = pd.DataFrame(data_tables)
        return self.data_frame