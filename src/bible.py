import json
import requests
from src.utilities import Utilities

BIBLE_ENDPOINT = "https://bible.helloao.org/api"

class Bible:

    @staticmethod
    def get_all_versions():
        response = requests.get(
            f"{BIBLE_ENDPOINT}/available_translations.json"
        )
        return response.json()

    @staticmethod
    def get_version(version: str):
        all_versions = Bible.get_all_versions()

        for translation in all_versions["translations"]: 
            if translation["id"] == version:
                return translation
            else:
                continue

        return None

    @staticmethod
    def get_all_books(version: str):
        response = requests.get(
            f"{BIBLE_ENDPOINT}/{version}/books.json"
        )
        return response.json()

    @staticmethod
    def get_book(version: str, book: str):
        books = Bible.get_all_books(version)
        for book in books:
            if book["commonName"] == book:
                return book
            else:
                continue
        return None

    @staticmethod
    def get_chapter(version_id: str, book_object: dict, chapter: int):
        response = requests.get(
            f"{BIBLE_ENDPOINT}/{version_id}/{book_object['id']}/{chapter}.json"
        )
        return response.json()
