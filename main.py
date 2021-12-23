import argparse
import csv
import os
from collections import Counter
from pathlib import Path
from random import choice

import requests
import rich
from rich import print
import rich.table


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

    results_table = rich.table.Table()
    results_table.add_column("Name", style="red bold")
    results_table.add_column("Birth Year")
    results_table.add_column("Sex")
    for dog in dogs_found:
        results_table.add_row(dog['HUNDENAME'], dog['GEBURTSJAHR_HUND'], dog['GESCHLECHT_HUND'])
    print(results_table)


def create(save_img_dest, all_dog_info):
    dog_name = choice([dog['HUNDENAME'] for dog in all_dog_info])
    dog_birth = choice([dog['GEBURTSJAHR_HUND'] for dog in all_dog_info])
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
            dog_name = '_'.join(dog_name.split())
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

    new_dog_table = rich.table.Table(title="Here's your new dog!", show_header=False)

    new_dog_table.add_row("Name", dog_name)
    new_dog_table.add_row("Birth Year", dog_birth)
    new_dog_table.add_row("Sex", dog_gender)
    new_dog_table.add_row("Image", str(dog_image))

    print(new_dog_table)


def stats(all_dog_info):
    all_names = [dog['HUNDENAME'] for dog in all_dog_info]
    all_genders = [dog['GESCHLECHT_HUND'] for dog in all_dog_info]
    count_gender = Counter(all_genders)
    longest_name = max(all_names, key=len)
    shortest_name = min(all_names, key=len)
    top_10_dogs = {k: v for k, v in sorted(Counter(all_names).items(), key=lambda item: item[1], reverse=True)[:10]}

    top_10_table = rich.table.Table(title="Most common name - TOP 10", width=50)
    top_10_table.add_column("Name", style="red bold")
    top_10_table.add_column("Counts")

    for name, counts in top_10_dogs.items():
        top_10_table.add_row(str(name), str(counts))

    stats_table = rich.table.Table(title="Interesting Statistic", show_header=False)

    stats_table.add_row("Longest Name", str(longest_name))
    stats_table.add_row("Shortest Name", str(shortest_name))
    stats_table.add_row("Males", str(count_gender['m']))
    stats_table.add_row("Females", str(count_gender['w']))

    print(stats_table)
    print(top_10_table)


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
