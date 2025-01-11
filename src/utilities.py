import json

class Utilities:

    @staticmethod
    def write_file(filepath: str, filename: str, data: str) -> None:
        with open(f"{filepath}/{filename}", "w+") as f:
            f.write(data)
            f.close()
