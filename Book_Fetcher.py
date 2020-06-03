import sqlite3
import requests
from bs4 import BeautifulSoup
from time import sleep
all_books = []
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
    category_dict = dict(zip(category,cat_url))
    print("CATEGORIES LIST CREATED")
    
    # 2nd get books from each category
    for item in category_dict.items():
        base_url = "http://books.toscrape.com/"
        url = item[1]
        response = requests.get(base_url+url)
        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.find_all("article")
        print(f"Currently fetching {item[0]} Category")
        for book in books:
            book_data = (get_title(book),get_price(book),item[0],get_rating(book),)
            all_books.append(book_data)
        
        



def save_books(all_books):
	connection = sqlite3.connect("books.db")
	c = connection.cursor()
	c.execute('''CREATE TABLE books 
		(title TEXT,price REAL,category TEXT,rating INTEGER)''')
	c.executemany("INSERT INTO books VALUES (?,?,?,?)", all_books)
	connection.commit()
	connection.close()

def get_title(book):
	return book.find("h3").find("a")["title"]

def get_price(book):
	price = book.select(".price_color")[0].get_text()
	return float(price.replace("£","").replace("Â",""))

def get_rating(book):
	ratings = {"Zero": 0, "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
	paragraph = book.select(".star-rating")[0]
	word = paragraph.get_attribute_list("class")[-1]
	return ratings[word]

Scrape_Books()
print("Connecting To Database....")
save_books(all_books)
print("Writing To Database completed")