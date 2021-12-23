import argparse
import csv

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
    """
    all_names, all_years, all_genders = get_yearly_data(year)
    TODO: create dog_name, birth, gender, img from get_yearly_data
    """


def stats(all_dog_info):
    """
    print(longest_name, shortest_name, total_male, total_female, top_10_names)
    """


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
