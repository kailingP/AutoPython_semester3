import csv
import os
import sys
from collections import Counter
from pathlib import Path
import requests
import argparse
from random import choice

genders = ['m', 'w']

available_data = {
    2021: 20210103,
    2020: 20200306,
    2019: 20190304,
    2018: 20180305,
    2017: 20170308,
    2016: 20160307,
    2015: 20151001,
}


def find(dog_name, data_year):
    path = requests.get(
        f'https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/{available_data[data_year]}_hundenamen.csv')
    if not path.ok:
        print(path.status_code, path.reason)
        return None
    results = {}
    content = path.content.decode("utf-8-sig").splitlines()
    reader = csv.DictReader(content)
    for line in reader:
        if dog_name == line['HUNDENAME']:
            results[line["GEBURTSJAHR_HUND"]] = line["GESCHLECHT_HUND"]
    return results


def get_stats(data_year):
    all_names = []
    all_ages = []
    all_genders = []
    top_names = ''
    path = requests.get(
        f'https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/{available_data[data_year]}_hundenamen.csv')

    if not path.ok:
        print(path.status_code, path.reason)
        return None

    content = path.content.decode("utf-8-sig").splitlines()
    reader = csv.DictReader(content)

    if data_year == 2018:
        for value in reader:
            all_genders.append(value['geschlecht_hund'])
            all_names.append(value['hundename'])
            all_ages.append(value['geburtsjahr_hund'])

    for value in reader:
        all_genders.append(value['GESCHLECHT_HUND'])
        all_names.append(value['HUNDENAME'])
        all_ages.append(value['GEBURTSJAHR_HUND'])

    male, female = Counter(all_genders).values()
    top_10_names = {k: v for k, v in sorted(Counter(all_names).items(), key=lambda item: item[1], reverse=True)[:10]}

    for i in top_10_names.keys():
        top_names = top_names + " " + i
    print(
        "longes:{}, shortest:{},male:{}, female:{}, popular:{}".format(max(all_names, key=len), min(all_names, key=len),
                                                                       male, female, top_names))
    return all_names, all_ages


def generate_dog(target_directory):
    global all_names, all_ages
    dog_name = choice(all_names)
    dog_birth = choice(all_ages)
    dog_gender = choice(['m', 'w'])
    dog_image = ''

    is_image = False
    while not is_image:
        response = requests.get('https://random.dog/woof.json')
        if not response.ok:
            print(response.status_code, response.reason)

        media = response.json()['url']
        if media.endswith('.jpg'):
            is_image = True
            image_name = '{}_{}.jpg'.format(dog_name, dog_birth)
            current_directory = os.getcwd()
            target_directory = Path(current_directory, target_directory)
            if not target_directory.exists():
                target_directory.mkdir()

            os.chdir(target_directory)
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


def get_parser():
    parser = argparse.ArgumentParser(description="Your input options: ")
    sub_parser = parser.add_subparsers()

    find_dog = sub_parser.add_parser("find")
    find_dog.add_argument('name', type=str, help='the dog name you want to search')
    find_dog.add_argument('-y', '--year', type=int, help='Specify the data year', default=2021)

    read_stats = sub_parser.add_parser("stats")
    read_stats.add_argument('-y', '--year', type=int, help='Specify the data year', default=2021)

    create_dog = sub_parser.add_parser("create")
    create_dog.add_argument('-o', '--output-dir',
                            help='Specify a location to save the image of a new dog, default is current directory',
                            type=str, default='.')
    return parser.parse_args()


def main(args=None):
    args = get_parser()

    try:
        if sys.argv[1] == "find":
            search_result = find(dog_name=args.name, data_year=args.year).items()
            # TODO: PRINT RESULT NOT FOUND WHEN NO MATCHING
            if not search_result:
                print("NOT FOUND")
            else:
                for year, gender in search_result:
                    print(year, gender)

    except KeyError:
        print("Available date from 2015-2021")

    if sys.argv[1] == "stats":
        get_stats(data_year=args.year)


    if sys.argv[1] == "create":
        names, years = get_stats(data_year=args.year)

        generate_dog(target_directory=args.output_dir, name = names)


if __name__ == "__main__":
    main()
