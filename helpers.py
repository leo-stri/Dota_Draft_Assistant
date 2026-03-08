import sqlite3
from sqlite3 import Error
import requests
from requests.exceptions import HTTPError, Timeout, ConnectionError
import os


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
    except Error as e:
        print(f"Error occurred trying to connect to database {path}: {e}")
    return connection

def execute_query(cursor, query, *args):
    cursor.execute(query, args)
    cursor.connection.commit()
    

def execute_read_query(cursor, query, *args):
    result = None
    cursor.execute(query, args)
    result = cursor.fetchall()
    return result

        
def fetch_response(url, headers=''):
    try:
        if headers:
            response = requests.get(url, headers=headers, timeout=20)
        else:
            response = requests.get(url, timeout=20)    
        response.raise_for_status()
        return response
    except HTTPError as err:
        print(f"\nError occured fetching response from {url}: {err}")
    except Timeout as err:
        print(f"\nTimed out fetching response from {url}: {err}")
    except ConnectionError as err:
        print(f"\nConnection error occurred fetching results from {url}: {err}")
        
def confirm(message):
    while True:
        answer = input(message)
        if answer.lower() in ('y', 'yes'):
            return True
        elif answer.lower() in ('n', 'no'):
            return False
        
def shutdown():
    return os.system("shutdown /s /t 1")