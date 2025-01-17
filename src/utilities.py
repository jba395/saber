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
