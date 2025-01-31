from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
from src.utilities import Utilities
import src.constants as constants
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
    Returns a dictionary with keys "index" and "verse".
    """
    # Get relevant scripture map, if it exists
    try:
        scripture = index_verse_maps[version_id]
    except KeyError:
        return f"Version {version_id} not found", 404
    except Exception:
        return "Server error", 500

    # Determine the version's global minimum and maximum
    scripture_indices = Utilities.describe_indices(scripture)
    lowest_index = scripture_indices["lowest_index"]
    highest_index = scripture_indices["highest_index"]

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
    Given a version ID and a verse index, return the full verse name.
    E.g., 0 => Genesis 1:1
    """
    # Get relevant scripture map, if it exists
    try:
        scripture = index_verse_maps[version_id]
    except KeyError:
        return f"Version {version_id} not found", 404
    except Exception:
        return "Server error", 500

    # Get relevant verse reference, if it exists
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
    Body: (Required unless denoted otherwise) 
        - index: verse index
        - verse: verse reference
        - game_room (optional): multiplayer game room
        - username (optional): user playing the game
    Optional query parameters: lower_bound and upper_bound
    """
    # Get relevant scripture map, if it exists
    try:
        scripture = index_verse_maps[version_id]
    except KeyError:
        return f"Version {version_id} not found", 404
    except Exception:
        return "Server error", 500

    # Get selected verse
    try:
        body = request.get_json()
        selected_verse_index = body["index"]
        selected_verse = body["verse"]
    except KeyError:
        return "No selected verse", 400
    except Exception:
        return "Server error", 500

    # Determine the version's global minimum and maximum
    scripture_indices = Utilities.describe_indices(scripture)
    lowest_index = scripture_indices["lowest_index"]
    highest_index = scripture_indices["highest_index"]

    # Find min and max params, if they exist
    lower_bound = int(request.args.get("lower_bound", lowest_index))
    upper_bound = int(request.args.get("upper_bound", highest_index))

    # Bad requests for bounds
    if lower_bound and lower_bound < lowest_index:
        return "Invalid lower bound", 400

    if upper_bound and upper_bound > highest_index:
        return "Invalid upper bound", 400

    if lower_bound and upper_bound and lower_bound > upper_bound:
        return "Lower bound is higher than upper bound", 400
    
    game_id = str(uuid.uuid4())
    midpoint_lower = (upper_bound + lower_bound) // 2
    midpoint_upper = midpoint_lower + 1
    game_log[game_id] = {
            "uuid": game_id,
            "version": version_id,
            "game_room": None,
            "username": None,
            "selected_verse_index": selected_verse_index,
            "selected_verse_reference": selected_verse,
            "start_time": time.time(),
            "end_time": None, 
            "global_lower_bound": lower_bound,
            "global_upper_bound": upper_bound,
            "events": [
                {
                    "type": "init",
                    "start_time": time.time(),
                    "current_time": time.time(),
                    "lower_bound": {
                        "id": lower_bound,
                        "verse": scripture[str(lower_bound)]
                    },
                    "midpoint_lower": {
                        "id": midpoint_lower,
                        "verse": scripture[str(midpoint_lower)]
                    },
                    "midpoint_upper": {
                        "id": midpoint_upper,
                        "verse": scripture[str(midpoint_upper)]
                    },
                    "upper_bound": {
                        "id": upper_bound,
                        "verse": scripture[str(upper_bound)]
                    }
                }
            ]
        }
    return game_log[game_id]


@app.route("/version/<version_id>/game/<game_id>")
@cross_origin(origin="*")
def get_game_state(version_id: str, game_id: str) -> dict:
    try:
        result = game_log[game_id]
    except KeyError:
        return f"Invalid game ID: {game_id}", 404
    except Exception:
        return "Server error", 500
    return game_log[game_id]


@app.route("/version/<version_id>/game/<game_id>/event", methods=["POST"])
@cross_origin(origin="*")
def set_game_event(version_id: str, game_id: str) -> dict:
    """
    Create a new game event.
    Body:
        - event_type: One of (lower, upper, back, complete)
        - verse_id (required ONLY if event_type == complete): The verse ID of the verse to find
    """
    # Get relevant scripture map, if it exists
    try:
        scripture = index_verse_maps[version_id]
    except KeyError:
        return f"Version {version_id} not found", 404
    except Exception:
        return "Server error", 500
    
    # Check for game ID
    if game_id not in list(game_log.keys()):
        return "Game not found", 404

    game = game_log[game_id]

    # Validate request body
    try:
        body = request.get_json()
        event_type = body["event_type"]
        if event_type not in constants.VALID_EVENT_TYPES:
            print(f"Invalid event type: {event_type}")
            return f"Invalid event type: {event_type}", 400
    except Exception as e:
        print(e)
        print("Body is either missing or has the wrong key")
        return "Body is either missing or has the wrong key", 400

    # Handle each event type
    if event_type == constants.EVENT_TYPE_LOWER:
        
        # Select the lower half
        lower_bound = game["events"][len(game["events"]) - 1]["lower_bound"]["id"] # Same as before
        upper_bound = game["events"][len(game["events"]) - 1]["midpoint_lower"]["id"] # Previous midpoint lower

        midpoint_lower = (lower_bound + upper_bound) // 2
        midpoint_upper = midpoint_lower + 1
    
    elif event_type == constants.EVENT_TYPE_UPPER:

        # Select the upper half
        lower_bound = game["events"][len(game["events"]) - 1]["midpoint_upper"]["id"] # Previous midpoint upper
        upper_bound = game["events"][len(game["events"]) - 1]["upper_bound"]["id"] # Same as before

        midpoint_lower = (lower_bound + upper_bound) // 2
        midpoint_upper = midpoint_lower + 1

    elif event_type == constants.EVENT_TYPE_BACK:

        # Determine new spacing
        previous_event = game["events"][len(game["events"]) - 1]
        prev_lower_gap = int(previous_event["midpoint_lower"]["id"]) - int(previous_event["lower_bound"]["id"])
        prev_upper_gap = int(previous_event["upper_bound"]["id"]) - int(previous_event["midpoint_upper"]["id"])
        new_gap = max(prev_lower_gap * 2, prev_upper_gap * 2, 10)

        lower_bound = max(
            int(previous_event["midpoint_lower"]["id"]) - new_gap, 
            game["global_lower_bound"]
        )
        upper_bound = min(
            int(previous_event["midpoint_upper"]["id"]) + new_gap, 
            game["global_upper_bound"]
        )

        midpoint_lower = (lower_bound + upper_bound) // 2
        midpoint_upper = midpoint_lower + 1

    else:
        return f"Invalid event type: {event_type}", 400

    new_event = {
        "lower_bound": {
            "id": lower_bound,
            "verse": scripture[str(lower_bound)]
        },
        "midpoint_lower": {
            "id": midpoint_lower,
            "verse": scripture[str(midpoint_lower)]
        },
        "midpoint_upper": {
            "id": min(midpoint_upper, upper_bound),
            "verse": scripture[str(min(midpoint_upper, upper_bound))]
        },
        "upper_bound": {
            "id": upper_bound,
            "verse": scripture[str(upper_bound)]
        },
        "type": event_type,
        "start_time": game["start_time"],
        "current_time": time.time()
    }

    # Check for victory conditions
    # Two same-side values match AND one of those values matches the goal
    if \
    (new_event["midpoint_lower"]["id"] == new_event["lower_bound"]["id"] and \
    new_event["midpoint_lower"]["id"] == int(game["selected_verse_index"])) \
    or \
    (new_event["midpoint_upper"]["id"] == new_event["upper_bound"]["id"] and \
    new_event["midpoint_upper"]["id"] == int(game["selected_verse_index"])):
        game["end_time"] = time.time()
        new_event["type"] = constants.EVENT_TYPE_COMPLETE

    game_log[game_id]["events"].append(new_event)
    return new_event
