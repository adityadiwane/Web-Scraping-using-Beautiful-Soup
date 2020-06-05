import sqlite3
import requests
import os
from bs4 import BeautifulSoup
from time import sleep
import pathlib

path = str(pathlib.Path(__file__).parent.absolute())

all_books = []
db = "\\books.db"


def Scrape_Books():
    # 1st run get all categories
    url = "http://books.toscrape.com/index.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find(class_="nav nav-list").find("ul").find_all("li")
    category = []
    cat_url = []
    for book in books:
        category.append(str(book.find("a").get_text()).strip())
        cat_url.append(str(book.find("a")["href"]))
    category_dict = dict(zip(category, cat_url))
    print("CATEGORIES LIST CREATED")

    # 2nd get books from each category
    for item in category_dict.items():
        cnt = 1
        url = item[1]
        while url:
            base_url = "http://books.toscrape.com/"
            response = requests.get(base_url + url)
            soup = BeautifulSoup(response.text, "html.parser")
            books = soup.find_all("article")
            print(f"Currently fetching {item[0]} Category Page - {cnt}")
            for book in books:
                book_data = (get_title(book), get_price(
                    book), item[0], get_rating(book),)
                all_books.append(book_data)
            next_butn = soup.find(class_="next")
            url = next_butn.find("a")["href"] if next_butn else None
            cnt += 1
            sleep(2)


def save_books(all_books):
    run_query(
        '''INSERT OR REPLACE INTO books(title,price,category,rating)
           VALUES (?,?,?,?);''',
        all_books)


def setup_db():
    path = str(pathlib.Path(__file__).parent.absolute())
    path = path + db
    # path = r"L:\\Udemy\\python_bootcamp\\{}".format(db)
    if not os.path.isfile(path):
        print("Creating Database")
        open(db, 'w').close()
        run_query(
            '''CREATE TABLE books(title TEXT,price REAL
            ,category TEXT,rating INTEGER)''')
        run_query("CREATE UNIQUE INDEX idx_title ON books(title)")
        print("Database Sucessfully Created")


def get_title(book):
    return book.find("h3").find("a")["title"]


def get_price(book):
    price = book.select(".price_color")[0].get_text()
    return float(price.replace("£", "").replace("Â", ""))


def get_rating(book):
    ratings = {"Zero": 0, "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    paragraph = book.select(".star-rating")[0]
    word = paragraph.get_attribute_list("class")[-1]
    return ratings[word]


def run_query(query, values=None):
    connection = sqlite3.connect(db)
    c = connection.cursor()
    if values:
        if not isinstance(values, str):
            c.executemany(query, values)
            print(f"Executing MANY:{query}")
        else:
            c.execute(query, values)
            print(f"Executing:{query}")
    else:
        c.execute(query)
        print(f"Executing:{query}")
    connection.commit()
    connection.close()


Scrape_Books()
setup_db()
print("Connecting To Database....")
save_books(all_books)
print("Writing To Database completed")
