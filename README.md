# Projekt ETL

## Instalacja

### Wymagane biblioteki

- `beautifulsoup4`
- `mysql-connector-python`
- `configparser`

### Połączenie z bazą danych

W systemie MariaDB/MySQL neleży utworzyć bazę danych oraz użytkownika z dostępem do niej:

```sql
CREATE DATABASE baza_danych;
CREATE USER 'nazwa_uzytkownika'@'localhost' IDENTIFIED BY 'haslo';
GRANT ALL PRIVILEGES ON baza_danych.* TO 'nazwa_uzytkownika'@'localhost';
FLUSH PRIVILEGES;
```

Następnie należy utworzyć w głównym katalogu projektu plik `config.ini` z danymi dostępowymi do bazy.
Struktura pliku:

```ini
[mysql]
user=nazwa_uzytkownika
password=haslo
db=baza_danych
```

Połączenie jest nawiązywane pod domyślnym adresem `localhost:3306`.
