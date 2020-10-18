# the Python client for Grakn
# https://github.com/graknlabs/client-python
from grakn.client import GraknClient

# Python's built in module for dealing with .csv files.
# we will use it read data source files.
# https://docs.python.org/3/library/csv.html#dialects-and-formatting-parameters
import csv
import pandas as pd

# city = 

def build_world_graph(inputs, data_path, keyspace_name):
    """
      gets the job done:
      1. creates a Grakn instance
      2. creates a session to the targeted keyspace
      3. for each input:
        - a. constructs the full path to the data file
        - b. loads csv to Grakn
      :param input as list of dictionaties: each dictionary contains details required to parse the data
    """
    with GraknClient(uri="localhost:48555") as client:  # 1
        with client.session(keyspace=keyspace_name) as session:  # 2
            for input in inputs:
                input["file"] = input["file"].replace(data_path, "")  # for testing purposes
                input["file"] = data_path + input["file"]  # 3a
                print("Loading from [" + input["file"] + ".csv] into Grakn ...")
                load_data_into_grakn(input, session)  # 3b


def load_data_into_grakn(input, session):
    """
      loads the csv data into our Grakn phone_calls keyspace:
      1. gets the data items as a list of dictionaries
      2. for each item dictionary
        a. creates a Grakn transaction
        b. constructs the corresponding Graql insert query
        c. runs the query
        d. commits the transaction
      :param input as dictionary: contains details required to parse the data
      :param session: off of which a transaction will be created
    """
    items = parse_data_to_dictionaries(input)  # 1

    for item in items:  # 2
        with session.transaction().write() as transaction:  # a
            graql_insert_query = input["template"](item)  # b
            print("Executing Graql Query: " + graql_insert_query)
            transaction.query(graql_insert_query)  # c
            transaction.commit()  # d

    print("\nInserted " + str(len(items)) +
          " items from [ " + input["file"] + ".csv] into Grakn.\n")


# To migrate the country data, the template code is as follows
def country_template(country):
    # insert country
    graql_insert_query = 'insert $country isa country, has countryname "' + country["Name"] + '"'

    if country["Code"] != "":
        graql_insert_query += ', has countrycode "' + country["Code"] + '"'
    if country["Continent"] != "":
        graql_insert_query += ', has continent "' + country["Continent"] + '"'
    if country["Region"] != "":
        graql_insert_query += ', has region "' + country["Region"] + '"'
    if country["SurfaceArea"] != "":
        graql_insert_query += ', has surfacearea ' + country["SurfaceArea"]
    if country["IndepYear"] != "":
        graql_insert_query += ', has indepyear ' + country["IndepYear"]
    if country["Population"] != "":
        graql_insert_query += ', has population ' + country["Population"]
    if country["LifeExpectancy"] != "":
        graql_insert_query += ', has lifeexpectancy ' + country["LifeExpectancy"]    
    if country["GNP"] != "":
        graql_insert_query += ', has gnp ' + country["GNP"]
    if country["GNPOld"] != "":
        graql_insert_query += ', has gnpold ' + country["GNPOld"]
    if country["LocalName"] != "":
        graql_insert_query += ', has localname "' + country["LocalName"] + '"'
    if country["GovernmentForm"] != "":
        graql_insert_query += ', has governmentform "' + country["GovernmentForm"] + '"'
    if country["HeadOfState"] != "":
        graql_insert_query += ', has headofstate "' + country["HeadOfState"] + '"'
    if country["Capital"] != "":
        graql_insert_query += ', has capital ' + country["Capital"]

    graql_insert_query += ";"

    return graql_insert_query

# language migration template
def language_template(countrylanguage):
    return 'insert $language isa language, has name "' + countrylanguage["Language"] + '";'


# insert a relation between the language and the countries in which it is spoken
def country_lang_template(countrylanguage):
    # match company
    graql_insert_query = 'match $language isa language, has name "' + \
        countrylanguage["Language"] + '";'
    # match person
    graql_insert_query += ' $country isa country, has countrycode "' + \
        countrylanguage["CountryCode"] + '";'
    # insert contract
    graql_insert_query += ' insert $new-speaks (speaks-language: $country, language-spoken: $language) isa speaks; $new-speaks '
    
    if countrylanguage["IsOfficial"] == "F":
        graql_insert_query += ' has isofficial ' + str('false')
    else:
        graql_insert_query += ' has isofficial ' + str('true')

    if countrylanguage["Percentage"] != "":
        graql_insert_query += ', has percentage ' + countrylanguage["Percentage"]

    graql_insert_query += ";"

    return graql_insert_query

# For city migration, the template is as follows
def city_template(city):
    # match country
    graql_insert_query = 'match $country isa country, has countrycode "' + \
        city["CountryCode"] + '";'

    graql_insert_query += ' insert $city isa city, has cityname  "' + \
        city["Name"] + '"'

    if city["ID"] != "":
        graql_insert_query += ', has city-id ' + city["ID"]

    if city["CountryCode"] != "":
        graql_insert_query += ', has countrycode "' + city["CountryCode"] + '"'

    if city["Population"] != "": 
        graql_insert_query += ', has population ' + city["Population"]

    if city["District"] != "":  
        graql_insert_query += ', has district "' + city["District"] + '"'

    graql_insert_query += ";"

    graql_insert_query += ' $relation (contains-city: $country, in-country: $city) isa has-city;'

    return graql_insert_query

# To determine if it is the capital city:
def capital_template(country):
    # match country and city

    # print("capital  is")
    # print(country["Capital"])
    # print(city.loc[city['ID'] == int(country["Capital"])])
    # print(city.loc[city['ID'] == int(country["Capital"])]["Name"].iloc[0])

    if country["Capital"] != "":
        graql_insert_query = 'match $country isa country, has countrycode "' + \
            country["Code"] + '";'

        graql_insert_query += ' $city isa city, has cityname "' +\
            city.loc[city['ID'] == int(country["Capital"])]["Name"].iloc[0] + '";'

        graql_insert_query += ' $rel (in-country: $city, contains-city: $country) isa has-city;'

        graql_insert_query += ' insert $rel has iscapital ' + str('true') + ';'

    return graql_insert_query


def parse_data_to_dictionaries(input):
    """
      1. reads the file through a stream,
      2. adds the dictionary to the list of items
      :param input.file as string: the path to the data file, minus the format
      :returns items as list of dictionaries: each item representing a data item from the file at input.file
    """
    items = []
    with open(input["file"] + ".csv") as data:  # 1
        for row in csv.DictReader(data, skipinitialspace=True):
            item = {key: value for key, value in row.items()}
            items.append(item)  # 2
    return items


Inputs = [
    {
        "file": "country",
        "template": country_template
    },
    {
        "file": "countrylanguage",
        "template": language_template
    },
    {
        "file": "countrylanguage",
        "template": country_lang_template
    },
    {
        "file": "city",
        "template": city_template
    },
    {
        "file": "country",
        "template": capital_template
    }
]

if __name__ == "__main__":

    

    city = pd.read_csv ('data/city.csv')
    # print(city.loc[city['ID'] == 1]["Name"].iloc[0])

    build_world_graph(inputs=Inputs, data_path="data/", keyspace_name = "globe")