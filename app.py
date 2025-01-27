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
def get_version(version_id: str) -> dict:
    """
    Retrieve the entire index_verse_map for a given version ID.
    """
    try:
        result = index_verse_maps[version_id]
        return result
    except KeyError:
        return f"Version {version_id} not found", 404
    except Exception:
        return "Server error", 500


@app.route("/version/<version_id>/verse/random_id")
def get_random_verse_id(version_id: str) -> dict:
    """
    Obtain a random verse ID between two optional query parameters, lower_bound and upper_bound.
    """
    # Get relevant scripture map, if it exists
    try:
        scripture = index_verse_maps[version_id]
    except KeyError:
        return f"Version {version_id} not found", 404
    except Exception:
        return "Server error", 500

    # Determine the version's global minimum and maximum
    scripture_keys = list(scripture.keys())
    lowest_index = int(min(scripture_keys, key=lambda k: int(scripture_keys[int(k)])))
    highest_index = int(max(scripture_keys, key=lambda k: int(scripture_keys[int(k)])))

    # Find min and max params, if they exist
    lower_bound = int(request.args.get('lower_bound'))
    upper_bound = int(request.args.get('upper_bound'))

    # Bad requests for bounds
    if lower_bound and lower_bound < lowest_index:
        return "Invalid lower bound", 400

    if upper_bound and upper_bound > highest_index:
        return "Invalid upper bound", 400

    if lower_bound and upper_bound and lower_bound > upper_bound:
        return "Lower bound is higher than upper bound", 400

    # Choose a random integer
    r = str(random.randint(lower_bound, upper_bound))
    return {
        "index": r,
        "verse": index_verse_maps[version_id][r]
    }


@app.route("/version/<version_id>/verse/<verse_id>")
def get_verse_reference(version_id: str, verse_id: str) -> str:
    """
    Given a verse index, return the full verse name.
    E.g., 0 => Genesis 1:1
    """
    try:
        result = index_verse_maps[version_id][verse_id]
        return result
    except KeyError:
        return f"Verse reference for version {version_id} and verse {verse_id} not found", 404
    except Exception:
        return "Server error", 500
