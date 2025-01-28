from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
from src.utilities import Utilities
import time
import random
import uuid

app = Flask(__name__)

SUPPORTED_VERSIONS = ["eng_kjv"]
index_verse_maps = {}
game_log = {}

# Load scripture maps on startup
for version in SUPPORTED_VERSIONS:
    index_verse_maps[version] = Utilities.read_file(
        filepath=f"resources/index_verse_maps",
        filename=f"{version}.json"
    )


@app.route("/version/<version_id>")
@cross_origin(origin='*')
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
@cross_origin(origin='*')
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
    lower_bound = int(request.args.get('lower_bound', lowest_index))
    upper_bound = int(request.args.get('upper_bound', highest_index))

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
@cross_origin(origin='*')
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


@app.route("/version/<version_id>/game/begin", methods=["POST"])
@cross_origin(origin="*")
def begin_game(version_id: str) -> str:
    """
    Initiate the beginning of the game and receive the threshold indices.
    Required query parameter: selected_verse (dictionary with "index" and "verse" keys)
    Optional query parameters: lower_bound and upper_bound
    """
    # Get selected verse
    try:
        selected_verse = request.args["selected_verse"]
    except KeyError:
        return "No selected verse", 400
    except Exception:
        return "Server error", 500

    # Find min and max params, if they exist
    lower_bound = int(request.args.get('lower_bound', lowest_index))
    upper_bound = int(request.args.get('upper_bound', highest_index))

    # Bad requests for bounds
    if lower_bound and lower_bound < lowest_index:
        return "Invalid lower bound", 400

    if upper_bound and upper_bound > highest_index:
        return "Invalid upper bound", 400

    if lower_bound and upper_bound and lower_bound > upper_bound:
        return "Lower bound is higher than upper bound", 400
    
    game_id = uuid.uuid4()
    game_log = {
        game_id: {
            "version": version_id,
            "selected_verse": selected_verse,
            "start_time": time.time(),
            "end_time": None, 
            "global_lower_bound": lower_bound,
            "global_upper_bound": upper_bound,
            "events": [
                {
                    "type": "init",
                    "lower_bound": lower_bound,
                    "midpoint": (upper_bound + lower_bound) // 2
                    "upper_bound": upper_bound,
                    "timestamp": time.time()
                }
            ]
        }
    }
    return game_log[game_id]


@app.route("/version/<version_id>/game/<game_id>")
@cross_origin(origin="*")
def get_game_state(version_id: str, game_id: str) -> dict:
    return game_log[game_id]


@app.route("/version/<version_id>/game/<game_id>/lower", methods=["POST"])
@cross_origin(origin="*")
def set_game_event_lower():
    pass


@app.route("/version/<version_id>/game/<game_id>/upper", methods=["POST"])
@cross_origin(origin="*")
def set_game_event_upper():
    pass
