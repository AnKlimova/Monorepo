import pickle
import random
import re
from pathlib import Path
from typing import Mapping
from urllib.request import urlopen

import pandas


def get_all_cities() -> Mapping[str, str]:
    target_url = "https://en.wikipedia.org/wiki/List_of_national_capitals"
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
        cleaned_capital_name = cleaned_capital_name.rstrip('.').strip()
        city_to_country[cleaned_capital_name] = line[1]
    print(city_to_country)
    return city_to_country


if __name__ == "__main__":
    pickle.dump(get_all_cities(), (Path(__file__).parent / "cities.pickle").open('wb'))
