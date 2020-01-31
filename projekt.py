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


containers = set()
brand = []
product_name = []
shipping = []


def switch_case():
    global containers
    global brand
    global product_name
    global shipping
    input_choice = ask_for_choice()

    # Extract
    if input_choice == 1:
        # open connection
        u_client = uReq(my_url)
        page_html = u_client.read()
        u_client.close()

        # html parsing
        page_soup = soup(page_html, "html.parser")

        # grabs each product
        containers = page_soup.find_all("div", {"class": "item-container"})

        # ask for continue
        input_continue = input('Data Exctracted, want to continue Y/N?: ').upper()
        if input_continue == 'Y':
            switch_case()

    # Transform
    elif input_choice == 2:
        if containers != set():
            try:
                # get info for each product
                for index, container in enumerate(containers, start=0):
                    brand_container = container.findAll("div", {"class": "item-info"})
                    brand.append(brand_container[0].div.a.img["title"])

                    title_container = container.findAll("a", {"class": "item-title"})
                    product_name.append(title_container[0].text)

                    shipping_container = container.findAll("li", {"class": "price-ship"})
                    shipping.append(shipping_container[0].text.strip())

                # ask for continue
                input_continue = input('want to continue Y/N?: ').upper()
                if input_continue == 'Y':
                    switch_case()
            except NameError:
                print('First u need to run step 1.')
                input_choice = ask_for_choice()
        else:
            print('First u need run step 1.')

    # Load
    elif input_choice == 3:
        if (brand == [] or shipping == [] or product_name == []):
            print('First u need step 1 next 2 to enter this step (3)')
        else:
            try:
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

                for index, container in enumerate(containers, start=0):
                    cursor.execute("INSERT INTO etl (brand, product_name, shipping) VALUES (%s,%s,%s)",
                                   (brand[index], product_name[index].replace(",", "|"), shipping[index]))
                    mariadb_connection.commit()

                brand.clear()
                product_name.clear()
                shipping.clear()
                print("Data was loaded.")
            except NameError:
                print('First u need to run step 1 and step 2.')
                switch_case()

    # do all etl
    elif input_choice == 4:
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
        for index, container in enumerate(containers, start=0):
            brand_container = container.findAll("div", {"class": "item-info"})
            brand.append(brand_container[0].div.a.img["title"])

            title_container = container.findAll("a", {"class": "item-title"})
            product_name.append(title_container[0].text)

            shipping_container = container.findAll("li", {"class": "price-ship"})
            shipping.append(shipping_container[0].text.strip())

        for index, container in enumerate(containers, start=0):
            cursor.execute("INSERT INTO etl (brand, product_name, shipping) VALUES (%s,%s,%s)",
                           (brand[index], product_name[index].replace(",", "|"), shipping[index]))
            mariadb_connection.commit()

        brand.clear()
        product_name.clear()
        shipping.clear()
        print("Data was loaded.")

    # erase data
    elif input_choice == 5:
        # open config file and assign variables
        config = configparser.ConfigParser()
        config.read("config.ini")
        db = config['mysql']['db']
        db_user = config['mysql']['user']
        db_password = config['mysql']['password']

        # connect to MariaDB
        mariadb_connection = mariadb.connect(user=db_user, password=db_password, database=db)
        cursor = mariadb_connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS etl;")
        mariadb_connection.commit()
        print('Data Erased.')

        # ask for continue
        input_continue = input('want to continue Y/N?: ').upper()
        if input_continue == 'Y':
            switch_case()

    else:
        print('U can only choose from options 1 to 5.')


# run
switch_case()
