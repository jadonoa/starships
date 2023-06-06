import json
import requests
import pymongo


# adds starships on a single page of the api to a list, also returning a link to the next page of starships
def get_starships(starships: list, url: str) -> tuple:
    req = requests.get(url)

    if req.status_code == 200:
        next_page_url = req.json()["next"]
        results = req.json()["results"]
    else:
        print("Error")
        return [], ""

    for i in range(0, len(results)):
        starships.append(results[i])

    return starships, next_page_url


# returns a list of all the starships across all four pages of the api
def get_all_starships() -> list:
    starships = list()
    url = "https://swapi.dev/api/starships/"

    while url is not None:
        starships, url = get_starships(starships, url)

    return starships


# returns the string name of the pilot through the api
def get_pilot(url: str) -> str:
    req = requests.get(url)
    pilot_name = req.json()["name"]
    return pilot_name


# returns the database id of a pilot
def get_pilot_id(name: str, db: object) -> object:
    result = db.characters.find_one({"name": name}, {"_id": 1})
    db_id = result["_id"]
    return db_id


# returns a list where pilots api links have been changed to their object ids from the database
def pilots_to_id(starships: list, db: object) -> list:

    for starship in starships:
        pilots = starship["pilots"]

        if pilots:
            pilot_ids = list()

            for pilot in pilots:
                name = get_pilot(pilot)
                db_id = get_pilot_id(name, db)
                pilot_ids.append(db_id)

            starship["pilots"] = pilot_ids
        else:
            starship["pilots"] = []

    return starships


if __name__ == "__main__":
    client = pymongo.MongoClient()
    db = client['starwars']

    starships = pilots_to_id(get_all_starships(), db)

    starships_collection = db["starships"]
    starships_collection.insert_many(starships)


