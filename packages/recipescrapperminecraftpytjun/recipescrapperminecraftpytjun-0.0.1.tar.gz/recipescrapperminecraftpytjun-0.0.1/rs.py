import requests
from bs4 import BeautifulSoup
import pandas as pd

class RecipeScrapper:
    """
    Handles web scraping of recipe-related data from given URLs and provides functionalities
    to manipulate and export the scraped data.

    This class is designed to scrape a webpage for tabular recipe data, process the data into
    a structured format, and export it into CSV or Excel files. It also provides functionality
    to display the data directly in the console. It primarily uses `BeautifulSoup` for parsing
    the HTML content and `pandas` for data manipulation.

    :ivar soup: Stores the parsed HTML content of the scraped webpage.
    :type soup: BeautifulSoup
    :ivar data_frame: Stores the structured recipe data in tabular format.
    :type data_frame: pandas.DataFrame
    """
    def __init__(self) -> None:
        self.soup = None
        self.data_frame = None

    def scrape_url(self, url: str) -> None:
        """
        Scrapes the HTML content of a given URL and initializes a BeautifulSoup object with the retrieved content.

        This function sends a GET request to the specified URL to fetch the HTML content. The HTML content
        is then parsed and stored in a BeautifulSoup object, which can be used for web scraping purposes.

        :param url: The URL of the web page to scrape.
        :type url: str
        :return: None
        """
        response = requests.get(url)
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def get_tables_data(self) -> pd.DataFrame:
        """
        Extracts data from tables within an HTML content processed by BeautifulSoup, arranging it into
        a structured pandas DataFrame. It specifically collects data from all tables excluding the first one
        and associates it with the respective section header (h2) text. Each row of the resulting DataFrame
        includes details such as category, name, ingredients, an image source, and description.

        :raises AttributeError: If the BeautifulSoup object does not contain the expected HTML elements.
        :raises KeyError: If the image element does not have a 'src' attribute.

        :return: Structured data in the form of a pandas DataFrame containing extracted table information.
        :rtype: pandas.DataFrame
        """
        tables = self.soup.find_all("table")[1:]
        headers = self.soup.find_all("h2")
        data_tables = []
        for i, table in enumerate(tables):
            table_rows = table.find_all("tr")[1:] if table.find_all("tr") else []
            header_text = headers[i].text if headers[i] else ""
            for row in table_rows:
                cells = row.find_all("td")
                if len(cells) >= 4:
                    image_tag = cells[2].find("img")
                    img_src = image_tag["src"] if image_tag else ""
                    data_tables.append({
                        "category": header_text,
                        "name": cells[0].text,
                        "ingredients": cells[1].text,
                        "image": img_src,
                        "description": cells[3].text,
                    })
        self.data_frame = pd.DataFrame(data_tables)
        return self.data_frame

    def save_to_csv(self, file_name: str) -> None:
        """
        Saves the contents of a pandas DataFrame to a CSV file.

        The method checks if the instance's ``data_frame`` attribute is not None. If valid, it
        saves the DataFrame to the specified file in CSV format using UTF-8 encoding and without
        index columns. If the ``data_frame`` attribute is None, a message is printed to indicate
        that there is no data to save.

        :param file_name: Name of the CSV file where the data will be saved.
        :type file_name: str
        :return: This function does not return any value.
        :rtype: None
        """
        if self.data_frame is not None:
            self.data_frame.to_csv(file_name, index=False, encoding="utf-8")
        else:
            print("No data to save.")

    def save_to_excel(self, file_name: str) -> None:
        """
        Saves the current data frame to an Excel file. If the data frame is not None,
        the method writes its contents to the specified Excel file using the "openpyxl"
        engine without including the index. If the data frame is None, it emits a message
        stating that there is no data to save.

        :param file_name: Name of the Excel file where the data frame will be saved.
        :type file_name: str
        :return: None
        """
        if self.data_frame is not None:
            self.data_frame.to_excel(file_name, index=False, engine="openpyxl")
        else:
            print("No data to save.")

    def show_data(self):
        """
        Displays the contents of the `data_frame` attribute or prints a message if no data is available.

        This method checks if the `data_frame` attribute is not None. If it is present, the data is displayed in
        its entirety without truncation for rows and columns. Otherwise, it notifies the user that there is no data
        to display.

        :raises None: This method does not raise any exceptions.
        :rtype: None
        :return: This method does not return a value.
        """
        if self.data_frame is not None:
            with pd.option_context('display.max_rows', None, 'display.max_columns', None):
                print(self.data_frame.to_string(index=False))
        else:
            print("No data to show.")

