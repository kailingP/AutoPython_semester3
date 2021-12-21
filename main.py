import csv
import json
import os
from collections import Counter
import random
from pathlib import Path

import requests
import argparse
from random import choice

allNames = []
allAges = []
genders = ['m', 'w']

available_data = {
    2021: 20210103,
    2020: 20210306,
    2019: 20190304,
    2018: 20180305,
    2017: 20170308,
    2016: 20160307,
    2015: 20151001,
}


def find(dogName, dataYear):
    path = requests.get(
        f'https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/{available_data[dataYear]}_hundenamen.csv')
    print(path)
    content = path.content.decode("utf-8-sig").splitlines()
    reader = csv.DictReader(content)
    for line in reader:
        if dogName == line['HUNDENAME']:
            print(line["GEBURTSJAHR_HUND"], line["GESCHLECHT_HUND"])


def get_parser():
    myparse = argparse.ArgumentParser(description="There are your input options: ")
    myparse.add_argument('-n', '--name', help='search by name', type=str)  # positional arguments are mandatory
    myparse.add_argument('-s', '--statistics', help="to read the statistics")  # with hyphens are optional
    myparse.add_argument('-active', help='is active by default',
                         action='store_true')  # optional boolean parameter with default value of true
    myparse.add_argument('-y', '--year', help='specify the data year, default data from 2021', default=2021)
    myparse.add_argument('-o', '--output',
                         help='specify a file path to save the dog image, default is current working directory',
                         type=str, default='.')
    return myparse.parse_args()


def get_stats(dataYear):
    path = requests.get(
        f'https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/{available_data[dataYear]}_hundenamen.csv')
    content = path.content.decode("utf-8-sig").splitlines()
    reader = csv.DictReader(content)
    allGender = []

    for value in reader:
        allGender.append(value['GESCHLECHT_HUND'])
        allNames.append(value['HUNDENAME'])
        allAges.append(value['GEBURTSJAHR_HUND'])

    male, female = Counter(allGender).values()
    top10Names = {k: v for k, v in sorted(Counter(allNames).items(), key=lambda item: item[1], reverse=True)[:10]}
    topNames = ''
    for i in top10Names.keys():
        topNames = topNames + " " + i

    print(
        "Shortest Name: {}\nLongest Name: {}\nTotal male dogs: {}\nTotal Female dogs: {}\nTop 10 Names: {}".format(
            min(allNames, key=len),
            max(allNames, key=len),
            male,
            female, topNames))


def generate_dog(target_directory):
    dog_name = choice(allNames)
    dog_birth = choice(allAges)
    dog_gender = choice(['m', 'w'])
    dog_image = ''

    # -o /--output-dir argument which allows specifying a directory where the file should be put

    is_image = False
    while not is_image:
        response = requests.get('https://random.dog/woof.json')
        media = response.json()['url']

        if response.status_code != 200:
            print(response)

        if media.endswith('.jpg'):
            is_image = True
            print("It is an image")
            image_name = '{}_{}.jpg'.format(dog_name, dog_birth)
            current_directory = os.getcwd()
            print('current_directory:', current_directory)
            target_directory = Path(current_directory, target_directory)
            if not target_directory.exists():
                target_directory.mkdir()

            os.chdir(target_directory)
            dog_image = Path(os.getcwd(), image_name)
            print(dog_image)

            with open(dog_image, 'wb') as handle:
                response = requests.get(media, stream=True)

                for block in response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

    print("A new dog is generated\nname : {}\nbirth year : {}\ngender : {}".format(dog_name, dog_birth, dog_gender))
    print('the image of dog is saved here: ', dog_image)


def main(args=None):
    parser = get_parser()
    find(dogName=parser.name, dataYear=parser.year)
    get_stats(dataYear=parser.year)
    generate_dog(target_directory= parser.output)


if __name__ == "__main__":
    main()
