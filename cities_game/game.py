import random
import re
from typing import Mapping
from urllib.request import urlopen

import pandas


def get_all_cities(target_url: str) -> Mapping[str, str]:
    page = urlopen(target_url)
    content = page.read().decode('utf-8')
    list_of_difs = pandas.read_html(content)
    data_frame = list_of_difs[1]
    city_to_country = {}
    content_list = data_frame.values.tolist()
    for line in content_list:
        capital_name = line[0]
        if re.search('\(.+\)', capital_name) is not None:
            if 'de facto' in capital_name:
                continue
            regex = re.compile("(.+).*?\(.*?\)")
            cleaned_capital_name = re.findall(regex, capital_name)[0]
        else:
            cleaned_capital_name = capital_name
        cleaned_capital_name = cleaned_capital_name.rstrip('.')
        city_to_country[cleaned_capital_name] = line[1]
    print(city_to_country)
    return city_to_country


def game(capital_to_country: Mapping[str, str]):
    initial_mapping: Mapping[str, str] = capital_to_country
    game_mapping: Mapping[str, str] = initial_mapping
    my_capital = random.choice(list(game_mapping.keys()))
    try:
        next_capital = _select_random_following_capital(game_mapping, my_capital)
    except IndexError:
        my_capital = random.choice(list(game_mapping.keys()))
    print(f"{my_capital}. It is the capital of {game_mapping[my_capital]}")
    del game_mapping[my_capital]
    while True:
        player_capital = input("Enter the capital to continue...")
        if player_capital == 'stop':
            break
        if not player_capital.startswith(my_capital[-1].upper()):
            print(f"The capital {player_capital} does not start with {my_capital[-1]}")
            continue
        try:
            player_country = capital_to_country[player_capital]
        except KeyError:
            print("Unknown capital. Please try again.")
            continue
        try:
            player_country = game_mapping[player_capital]
        except KeyError:
            print(f"Already used capital {player_capital}. Please try again.")
            continue
        else:
            input("Good job! My turn...")
            try:
                my_capital = _select_random_following_capital(game_mapping, player_capital)
            except IndexError:
                print(
                    f"You won! "
                    f"There are no more capitals starting with {player_capital[-1].upper()}.")
                break
            del game_mapping[player_capital]
            print(f"{my_capital}. It is the capital of {game_mapping[my_capital]}")
            try:
                next_capital = _select_random_following_capital(game_mapping, my_capital)
            except IndexError:
                print(
                    f"Haha, I won! "
                    f"There are no more capitals starting with {player_capital[-1].upper()}")
                break
            del game_mapping[my_capital]
            continue


def _select_random_following_capital(capital_to_country: Mapping[str, str], player_capital: str) -> str:
    last_letter = player_capital[-1]
    capitals_starting_with_letter = [capital for capital in capital_to_country.keys() if capital.startswith(last_letter.upper())]
    return random.choice(capitals_starting_with_letter)


if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/List_of_national_capitals"
    capitals_cities = get_all_cities(url)
    game(capitals_cities)
