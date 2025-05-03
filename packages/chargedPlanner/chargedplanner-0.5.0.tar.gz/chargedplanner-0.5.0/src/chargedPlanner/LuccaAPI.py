import datetime
from datetime import date
from ratelimit import limits, sleep_and_retry

from chargedPlanner.decorators import singleton
from chargedPlanner.tools import get_config_filePath

@singleton
class LuccaAPI(object) :

    import json
    with open(get_config_filePath(), "r") as f:
        baseUrl = json.load(f)["luccaURL"]
        f.close()

    # On windows, set your token on credential manager with :
    # cmdkey /generic:MyLuccaToken /user:dummy /pass:<TOKEN>

    def __init__(self):

        self.__headers__ = {}

        try :
            import keyring  
            self.__headers__["Authorization"] = "lucca application=" + keyring.get_password("MyLuccaToken", "dummy")

        except Exception as e:

            from colorama import init, Fore

            init(autoreset=True)
            print(
                Fore.RED
                + "Error retrieving token: {e}"
            )
            import sys
            sys.exit(1)

    # =====================================================

    def __post__(self,url : str):

        # Lucca API Token not filled, cannot send the request
        if not len(self.__headers__) :
            return {}

        # Make the GET request
        print("url= ", url)
        import requests
        response = requests.get(LuccaAPI.baseUrl + url, headers=self.__headers__)

        # Check the response
        if response.status_code == 200:
            print("Success 200!")  # If the response is JSON, parse and print it
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

        return response.json()

    def getLeaves(self,lucca_ID : int, start_date : date, end_date = date) -> list[datetime.date] :

        if not isinstance(lucca_ID, int):
            print("lucca ID type : ", type  (lucca_ID))
            raise ValueError("incompatible lucca ID type")
        if not isinstance(start_date, date):
            print("start date type : ", type(start_date))
            raise ValueError("incompatible start_date type")
        if not isinstance(end_date, date):
            print("end_date type : ", type(end_date))
            raise ValueError("incompatible end_date type")

        data = []
        url = ("?leavePeriod.ownerId=" + str(lucca_ID) + "&date=between," +
               str(start_date) + "," + str(end_date) +
               "&fields=date,leaveAccount.name,isam")

        ans = self.__post__(url)

        if ans == None :
            return []

        if not len(ans["data"]):
            return []

        if not len(ans["data"]["items"]) :
            return []

        for leave in ans["data"]["items"] :

            if leave["leaveAccount"]["name"] == 'Télétravail' :
                continue

            from datetime import datetime
            data.append({"date": datetime.strptime(leave["date"], "%Y-%m-%dT%H:%M:%S"),
                         "time_period": "AM" if leave["isAM"] == True else "PM"
                         })

        # in  the case only remote working was defined in the given time span
        # data will be empty
        if not len(data) :
            return []

        # Convert to DataFrame
        from pandas import DataFrame
        df = DataFrame(data)

        # Aggregate by date and duration
        aggregated = df.groupby("date")["time_period"].sum().reset_index()

        # Convert back to a desired format
        d= aggregated.to_dict(orient="records")

        # Return a list of datetime.dates
        return [item['date'].date() for item in d]


