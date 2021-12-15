import csv
from collections import Counter
import random
import requests
import argparse


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


def generate_dog():
    dog_name = allNames[random.randint(0, len(allNames))]
    dog_birth = allAges[random.randint(0, len(allAges))]
    dog_gender = genders[random.randint(0, 2)]
    print("A new dog is generated\nname : {}\nbirth year : {}\ngender : {}".format(dog_name, dog_birth, dog_gender))
    with Image.open('path/to/file.jpg') as img:
        img.show()


def main(args=None):
    find(dogName=get_parser().name)
    get_stats()
    generate_dog()


if __name__ == "__main__":
    main()
