import json

class Utilities:

    @staticmethod
    def write_file(filepath: str, filename: str, data: str) -> None:
        with open(f"{filepath}/{filename}", "w+") as f:
            f.write(data)
            f.close()

    @staticmethod
    def read_file(filepath: str, filename: str) -> dict:
        with open(f"{filepath}/{filename}", "r") as f:
            result = json.loads(f.read())
            f.close()
        return result

    @staticmethod
    def describe_indices(scripture: dict) -> dict:
        # Determine the version's global minimum and maximum
        scripture_keys = list(scripture.keys())
        lowest_index = int(min(scripture_keys, key=lambda k: int(scripture_keys[int(k)])))
        highest_index = int(max(scripture_keys, key=lambda k: int(scripture_keys[int(k)])))
        return {
            "lowest_index": lowest_index,
            "highest_index": highest_index
        }
