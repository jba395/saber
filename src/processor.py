from src.bible import Bible
from src.utilities import Utilities
import json
import requests

class Processor:

    @staticmethod
    def process(version_id: str) -> None:
        index_verse_map = {}
        verse_index_map = {}
        version = Bible.get_version(version_id)

        if version is not None:
            Utilities.write_file(
                filepath="resources/versions",
                filename=f"{version_id}.json",
                data=json.dumps(version_id)
            )
        else:
            print(f"{v} not found")
            exit(0)

        books = Bible.get_all_books(version_id)

        # Global index
        index = 0

        # Parse through each book
        for book in books["books"]:
            print(f"\nProcessing {book['commonName']}")
            book_id=book["id"]
            number_of_chapters = book["numberOfChapters"]

            # Search through all chapters
            for c in range(1, number_of_chapters + 1):
                print(f"Chapter {c}")
                chapter = Bible.get_chapter(
                    version_id=version_id,
                    book_object=book,
                    chapter=c
                )

                # Determine number of verses per chapter and index appropriately
                # number_of_verses = len(chapter["chapter"]["content"])
                verses = chapter["chapter"]["content"]
                for v in verses:
                    if v["type"] == "verse":
                        scripture_reference = f"{book['commonName']} {chapter['chapter']['number']}:{v['number']}"
                        index_verse_map[index] = scripture_reference
                        verse_index_map[scripture_reference] = index
                        index += 1
                    
                # for v in range(1, number_of_verses + 1):
                #     scripture_reference = f"{book['commonName']} {chapter['chapter']['number']}:{v}"
                #     index_verse_map[index] = scripture_reference
                #     verse_index_map[scripture_reference] = index
                #     index += 1

            print(f"{book['commonName']} complete")


        # Write indices
        Utilities.write_file(
            "resources/index_verse_maps",
            f"{version_id}.json",
            json.dumps(index_verse_map)
        )

        Utilities.write_file(
            "resources/verse_index_maps",
            f"{version_id}.json",
            json.dumps(verse_index_map)
        )
        