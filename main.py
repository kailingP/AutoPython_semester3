import csv
import os
from collections import Counter
from pathlib import Path
import requests
import argparse
from random import choice

all_names = []
all_ages = []
genders = ['m', 'w']

available_data = {
    '2021': 20210103,
    '2020': 20200306,
    '2019': 20190304,
    '2018': 20180305,
    '2017': 20170308,
    '2016': 20160307,
    '2015': 20151001,
}


def find(dog_name, data_year):
    path = requests.get(
        f'https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/{available_data[data_year]}_hundenamen.csv')
    if not path.ok:
        print(path.status_code, path.reason)
        return None

    content = path.content.decode("utf-8-sig").splitlines()
    reader = csv.DictReader(content)
    for line in reader:
        if dog_name == line['HUNDENAME']:
            print(line["GEBURTSJAHR_HUND"], line["GESCHLECHT_HUND"])


def get_stats(data_year):
    path = requests.get(
        f'https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/{available_data[data_year]}_hundenamen.csv')
    if not path.ok:
        print(path.status_code, path.reason)
        return None

    content = path.content.decode("utf-8-sig").splitlines()
    reader = csv.DictReader(content)
    all_genders = []

    for value in reader:
        all_genders.append(value['GESCHLECHT_HUND'])
        all_names.append(value['HUNDENAME'])
        all_ages.append(value['GEBURTSJAHR_HUND'])

    male, female = Counter(genders).values()
    top_10_names = {k: v for k, v in sorted(Counter(all_names).items(), key=lambda item: item[1], reverse=True)[:10]}
    top_names = ''
    for i in top_10_names.keys():
        top_names = top_names + " " + i

    print("Shortest Name: {}\nLongest Name: {}\nTotal male dogs: {}\nTotal Female dogs: {}\nTop 10 Names: {}".format(
        min(all_names, key=len),
        max(all_names, key=len),
        male,
        female, top_names))


def generate_dog(target_directory):
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


def run(dog_name, year, stats, create, target_directory):
    try:
        if dog_name:
            find(dog_name, year)
        elif stats:
            get_stats(year)
        elif create:
            generate_dog(target_directory)
    except KeyError:
        print('Invalid input!')


def get_parser():
    parser = argparse.ArgumentParser(description="Your input options: ")
    parser.add_argument('-n', '--name', help='Search a dog by name', type=str)
    parser.add_argument('-s', '--statistics', help='Read the statistics report from the year')
    parser.add_argument('-y', '--year', help='Specify the data year', default='2021')
    parser.add_argument('-c', '--create', help='Create a random dog')
    parser.add_argument('-o', '--output-dir',
                        help='Specify a location to save the image of a new dog, default is current directory',
                        type=str, default='.')
    return parser.parse_args()


def main(args=None):
    parser = get_parser()
    run(dog_name=parser.name, year=parser.year, stats=parser.statistics, create=parser.create,
        target_directory=parser.output_dir)


if __name__ == "__main__":
    main()
