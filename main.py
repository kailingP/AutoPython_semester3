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


def find(dogName):
    path = requests.get('https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/20170308_hundenamen.csv')
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
    return myparse.parse_args()


def get_stats():
    path = requests.get('https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/20170308_hundenamen.csv')
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
            print('current_directory:',  current_directory)
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
    print('the image of dog is saved here: ' , dog_image)


def main(args=None):
    find(dogName=get_parser().name)
    get_stats()
    generate_dog('../Download')


if __name__ == "__main__":
    main()
