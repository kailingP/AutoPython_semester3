#
import argparse

import requests


def data_dic():
    """
        request data from https://ckan.opendata.swiss/api/3/action/package_show?id=hundenamen-aus-dem-hundebestand-der-stadt-zurich2
        ,loop throungh result/resources[0,5]
        return a dic like:
       {
        year= file:name[0:4] : link
        2021: https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/20151001_hundenamen.csv"
        2020: https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/20151001_hundenamen.csv"
        2019: https://data.stadt-zuerich.ch/dataset/sid_stapo_hundenamen/download/20151001_hundenamen.csv"
        }
        and latest_year = 201

    """
    path = requests.get(
        "https://ckan.opendata.swiss/api/3/action/package_show?id=hundenamen-aus-dem-hundebestand-der-stadt-zurich2")

    # TODO: CATCH ERRORS

    list_of_available_years = path.json()['result']['resources']



def get_yearly_data(link):
    # TODO: get data dictionary with year which
    """
    path = requests.get("data from year XXX")
    return {all_names, all_years,all_genders}
    like [
        {
            geschlecht_hund: 'f',
            hundename: 'Bella',
            geburtsjahr_hund: 2020,
        }
        {
            geschlecht_hund: 'm',
            hundename: 'Bello',
            geburtsjahr_hund: 2015,
        }
    ]

    """
    pass


# Search dog by {dog_name} from the latest year and output to console
def find(dog_name, all_dog_info):
    """
    all_names, all years, all_genders = get_yearly_data(year)

    TODO: Search dog name from data
    TODO: Print dog's name, birthyear, sex
     """


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
    year_link_dic, latest_year = data_dic()
    args_parsed = parsers(latest_year)
    link = year_link_dic[args_parsed.year]
    all_dog_info_list = get_yearly_data(link)

    if args_parsed.sub_cmd == "find":
        find(args_parsed.name, all_dog_info_list)
    elif args_parsed.sub_cmd == "stats":
        stats(all_dog_info_list)
    elif args_parsed.sub_cmd == "create":
        create(args_parsed.output_dir, all_dog_info_list)


if __name__ == "__main__":
    main()
