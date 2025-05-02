import json
from pathlib import Path
from typing import List

from rich import print

THIS_DIR = Path(__file__).parent
CITIES_JSON_FPATH = THIS_DIR / "./my_folder/cities.json"


def is_city_capital_of_state(city_name: str, state: str) -> bool:
    cities_json_contents = CITIES_JSON_FPATH.read_text()
    cities: List[dict] = json.loads(cities_json_contents)
    print(cities)
    mcity: List[dict] = [city for city in cities if city["city"] == city_name]
    if len(mcity) == 0:
        return False
    matched_city = mcity[0]
    return matched_city["state"] == state


if __name__ == "__main__":
    is_capital = is_city_capital_of_state(city_name="Boston",
                                          state="Massachusetts")
    print(is_capital)
    print("Hello, 1, 2, 3")
