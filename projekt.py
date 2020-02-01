from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import mysql.connector as mariadb
import configparser

my_url = 'https://www.newegg.com/Video-Cards-Video-Devices/Category/ID-38?Tpk=graphics%20card'
print("""Project "ETL"
Type 1 to extract data from website.
Type 2 to Transform data.
Type 3 to load data to database.
Type 4 to do all steps in once except step 5.
Type 5 to erase data from database.
""")


# ask for choice
def ask_for_choice():
    try:
        choice = int(input('Type your choice: '))
        return choice
    except ValueError:
        print("This is not a number.")


def ask_for_continue():
    input_continue = input('Want to continue Y/N?: ').upper()
    if input_continue == 'Y':
        switch_case()
    elif input_continue == 'N':
        pass
    else:
        print('Invalid choice.')
        ask_for_continue()


containers = set()
brand = []
product_name = []
shipping = []


def open_db_connection():
    # open config file and assign variables
    config = configparser.ConfigParser()
    config.read("config.ini")
    db = config['mysql']['db']
    db_user = config['mysql']['user']
    db_password = config['mysql']['password']

    # connect to MariaDB
    mariadb_connection = mariadb.connect(user=db_user, password=db_password, database=db)
    cursor = mariadb_connection.cursor()
    return mariadb_connection, cursor


def extract():
    global containers

    # open connection
    u_client = uReq(my_url)
    page_html = u_client.read()
    u_client.close()

    # html parsing
    page_soup = soup(page_html, "html.parser")

    # grabs each product
    containers = page_soup.find_all("div", {"class": "item-container"})


def transform():
    # get info for each product
    for index, container in enumerate(containers, start=0):
        brand_container = container.findAll("div", {"class": "item-info"})
        brand.append(brand_container[0].div.a.img["title"])

        title_container = container.findAll("a", {"class": "item-title"})
        product_name.append(title_container[0].text)

        shipping_container = container.findAll("li", {"class": "price-ship"})
        shipping.append(shipping_container[0].text.strip())


def load():
    mariadb_connection, cursor = open_db_connection()

    cursor.execute("CREATE TABLE IF NOT EXISTS etl ("
                   "brand varchar(225),"
                   "product_name varchar(225),"
                   "shipping varchar(255)"
                   ");")

    for index, container in enumerate(containers, start=0):
        cursor.execute("INSERT INTO etl (brand, product_name, shipping) VALUES (%s,%s,%s)",
                       (brand[index], product_name[index].replace(",", "|"), shipping[index]))
        mariadb_connection.commit()

    brand.clear()
    product_name.clear()
    shipping.clear()


def switch_case():
    global containers
    global brand
    global product_name
    global shipping
    input_choice = ask_for_choice()

    # Extract
    if input_choice == 1:
        extract()
        print('Data extracted.')
        ask_for_continue()

    # Transform
    elif input_choice == 2:
        if containers != set():
            try:
                transform()
                print('Data transformed.')
                ask_for_continue()
            except NameError:
                print('First u need to run step 1.')
                switch_case()
        else:
            print('First u need run step 1.')
            switch_case()

    # Load
    elif input_choice == 3:
        if brand == [] or shipping == [] or product_name == []:
            print('First u need step 1 next 2 to enter this step (3)')
            switch_case()
        else:
            try:
                load()
                print('Data loaded to database.')
                ask_for_continue()
            except NameError:
                print('First u need to run step 1 and step 2.')
                switch_case()

    # do all etl
    elif input_choice == 4:
        extract()
        print('Data extracted.')
        transform()
        print('Data transformed.')
        load()
        print('Data loaded to database.')
        ask_for_continue()

    # erase data
    elif input_choice == 5:
        mariadb_connection, cursor = open_db_connection()

        cursor.execute("DROP TABLE IF EXISTS etl;")
        mariadb_connection.commit()
        print('Data erased.')
        ask_for_continue()

    else:
        print('U can only choose from options 1 to 5.')
        switch_case()


# run
switch_case()
