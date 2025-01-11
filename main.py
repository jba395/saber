from src.bible import Bible
from src.processor import Processor
from src.utilities import Utilities
import json

if __name__ == "__main__":
    Processor.process(version_id="eng_kjv")
