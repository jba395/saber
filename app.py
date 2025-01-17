from flask import Flask
from flask import request
from src.utilities import Utilities
import random

app = Flask(__name__)

SUPPORTED_VERSIONS = ["eng_kjv"]
index_verse_maps = {}

# Load scripture maps on startup
for version in SUPPORTED_VERSIONS:
    index_verse_maps[version] = Utilities.read_file(
        filepath=f"resources/index_verse_maps",
        filename=f"{version}.json"
    )


@app.route("/version/<version_id>")
def get_version(version_id: str):
    return index_verse_maps[version_id]

@app.route("/version/<version_id>/verse/random_id")
def get_random_verse_id(version_id) -> dict:

    # Get relevant scripture map
    scripture = index_verse_maps[version_id]
    scripture_keys = list(scripture.keys())
    lowest_index = int(min(scripture_keys, key=lambda k: int(scripture_keys[int(k)])))
    highest_index = int(max(scripture_keys, key=lambda k: int(scripture_keys[int(k)])))

    # Find min and max params, if they exist
    lower_bound = int(request.args.get('lower_bound'))
    upper_bound = int(request.args.get('upper_bound'))

    if not lower_bound or lower_bound < lowest_index:
        lower_bound = lowest_index
    
    if not upper_bound or upper_bound > highest_index:
        upper_bound = highest_index

    # Choose a random integer
    r = str(random.randint(lower_bound, upper_bound))
    return {
        "index": r,
        "verse": index_verse_maps[version_id][r]
    }


@app.route("/version/<version_id>/verse/<verse_id>")
def get_verse_reference(version_id: str, verse_id: str):
    return index_verse_maps[version_id][verse_id]
