from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import mysql.connector as mariadb
import configparser

my_url = 'https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20card'

# open connection
u_client = uReq(my_url)
page_html = u_client.read()
u_client.close()

# html parsing
page_soup = soup(page_html, "html.parser")

# grabs each product
containers = page_soup.find_all("div", {"class": "item-container"})

# open config file and assign variables
config = configparser.ConfigParser()
config.read("config.ini")
db = config['mysql']['db']
db_user = config['mysql']['user']
db_password = config['mysql']['password']

# connect to MariaDB
mariadb_connection = mariadb.connect(user=db_user, password=db_password, database=db)
cursor = mariadb_connection.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS etl ("
               "brand varchar(225),"
               "product_name varchar(225),"
               "shipping varchar(255)"
               ");")

# get info for each product
for container in containers:
    brand_container = container.findAll("div", {"class": "item-info"})
    brand = brand_container[0].div.a.img["title"]

    title_container = container.findAll("a", {"class": "item-title"})
    product_name = title_container[0].text

    shipping_container = container.findAll("li", {"class": "price-ship"})
    shipping = shipping_container[0].text.strip()

    cursor.execute("INSERT INTO etl (brand, product_name, shipping) VALUES (%s,%s,%s)",
                   (brand, product_name.replace(",", "|"), shipping))
    mariadb_connection.commit()
