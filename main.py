import argparse
import csv
import os
from collections import Counter
from pathlib import Path
from random import choice

import requests


def year_link_dic():
    path = requests.get(
        "https://ckan.opendata.swiss/api/3/action/package_show?id=hundenamen-aus-dem-hundebestand-der-stadt-zurich2")

    # TODO: CATCH ERRORS
    year_and_link = {}
    list_of_available_years = path.json()['result']['resources']
    for item in list_of_available_years:
        year = int(item['display_name']['de'][:4])
        year_and_link[year] = item['download_url']
    return max(year_and_link.keys()), year_and_link


def get_yearly_data(link):
    data = requests.get(link).content.decode("utf-8-sig").splitlines()
    data_reader = csv.DictReader(data)
    # TODO: CATCH ERROR ->CONNECTION, DATA FORMAT
    dog_list = list(data_reader)
    dog_list_upper_keys = [{key.upper(): value for (key, value) in dog.items()} for dog in dog_list]
    return dog_list_upper_keys


def find(dog_name, all_dog_info):
    dogs_found = [dog for dog in all_dog_info if (dog_name == dog['HUNDENAME'])]
    if not dogs_found:
        print("No match found")
    for dog in dogs_found:
        print(dog['HUNDENAME'], dog['GEBURTSJAHR_HUND'], dog['GESCHLECHT_HUND'])


def create(save_img_dest, all_dog_info):
    dog_name = choice([dog['HUNDENAME'] for dog in all_dog_info])
    dog_birth = choice([dog['GESCHLECHT_HUND'] for dog in all_dog_info])
    dog_gender = choice(['m', 'w'])
    dog_image = ''

    is_image = False
    while not is_image:
        response = requests.get('https://random.dog/woof.json')
        # TODO: ERROR HANDLING

        media = response.json()['url']
        media_extension = media[-4:].lower()
        if media_extension in ['.jpg', '.png']:
            is_image = True
            image_name = f'{dog_name}_{dog_birth}{media_extension}'
            current_directory = os.getcwd()
            save_img_dest = Path(current_directory, save_img_dest)
            if not save_img_dest.exists():
                save_img_dest.mkdir()

            os.chdir(save_img_dest)
            dog_image = Path(os.getcwd(), image_name)

            with open(dog_image, 'wb') as handle:
                response = requests.get(media, stream=True)

                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

    print(
        "Here's your new dog!\nName : {}\nBirth year : {}\nSex : {}\nThe image of the new dog can be found here: {}\n"
        "".format(dog_name, dog_birth, dog_gender, dog_image))


def stats(all_dog_info):
    all_names = [dog['HUNDENAME'] for dog in all_dog_info]
    all_genders = [dog['GESCHLECHT_HUND'] for dog in all_dog_info]
    count_gender = Counter(all_genders)
    longest_name = max(all_names, key=len)
    shortest_name = min(all_names, key=len)
    top_10_dogs = {k: v for k, v in sorted(Counter(all_names).items(), key=lambda item: item[1], reverse=True)[:10]}

    print(
        "Longest Name:{}, shortest:{},male:{}, female:{}, popular:{}".format(longest_name, shortest_name,
                                                                             count_gender['m'], count_gender['w'],
                                                                             top_10_dogs))


def parsers(latest_year):
    parser = argparse.ArgumentParser(description="Your input options: ")
    parser.add_argument('-y', '--year', type=int, help='Specify the data year', default=latest_year)
    sub_parser = parser.add_subparsers(dest="sub_cmd")

    find_dog = sub_parser.add_parser("find")
    find_dog.add_argument('name', type=str, help='the dog name you want to search')

    sub_parser.add_parser("stats")

    create_dog = sub_parser.add_parser("create")
    create_dog.add_argument('-o', '--output-dir',
                            help='Specify a location to save the image of a new dog, default is current directory',
                            type=str, default='.')
    return parser.parse_args()


def main(args=None):
    latest_year, links = year_link_dic()
    args_parsed = parsers(latest_year)
    link = links[args_parsed.year]
    all_dog_info_list = get_yearly_data(link)

    if args_parsed.sub_cmd == "find":
        find(args_parsed.name, all_dog_info_list)
    elif args_parsed.sub_cmd == "stats":
        stats(all_dog_info_list)
    elif args_parsed.sub_cmd == "create":
        create(args_parsed.output_dir, all_dog_info_list)


if __name__ == "__main__":
    main()
