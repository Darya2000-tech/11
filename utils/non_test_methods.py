import csv, random
from datetime import datetime, timedelta
from urllib.parse import quote_plus

def open_csv_file(filepath=str):
    with open(filepath, "r") as file:
        reader = csv.DictReader (file)
        return list(reader)


def generateFlightsDates ():
    dates_list = {}

    dates_list ["depart_date"] = quote_plus((datetime.now() + timedelta (days=random.randint(3,10))).strftime("%m/%d/%Y"))
    dates_list ["return_date"] = quote_plus ((datetime.now() + timedelta (days=random.randint(15,30))).strftime("%m/%d/%Y"))

    return dates_list

def generateRandomCardNumber ():
    return random.randrange(10**15, 10**16)
   
def processCancelRequestBody(ids_list=list, names_list=list):

    pattern = "&flightID=201220833-808-MM&flightID=3612585259-15539-DD&flightID=2514444-23-JB"
    cgi_part = ".cgifields=" + "&.cgifields=".join(names_list)
    static_part = "&removeFlights.x=70&removeFlights.y=6&"
    flight_part = "flightID=" + " &flightID" .join(ids_list)
    todelete_part = f"{names_list[random.randrange(0, len(names_list))]}=on"

    result = f"{todelete_part}&{flight_part}&{cgi_part}&{static_part}"
    return result
