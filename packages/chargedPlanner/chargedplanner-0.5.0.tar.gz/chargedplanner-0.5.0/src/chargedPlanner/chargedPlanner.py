from __future__ import annotations

from datetime import date, datetime, timedelta

import numbers
import math
from enum import Enum
from typing import Dict
import json

from pyexpat import features

from chargedPlanner.tools import is_running_under_pytest

import pandas.core.frame

def defaultFilter(feat):
    return True

def prepare_for_gantt(tasks : list) -> [pandas.core.frame.DataFrame, dict] :

    import pandas as pd
    df = pd.DataFrame(tasks)

    # Convert to DataFrame and Reset Index
    df = pd.DataFrame(tasks)
    df.reset_index(drop=True, inplace=True)

    def random_warm_color():
        """Generate a bright RGB color."""
        import random
        return f"rgb({random.randint(100, 255)}, {random.randint(100, 250)}, {random.randint(0, 255)})"

    unique_tasks = df["Task"].unique()
    color_dict = {task: random_warm_color() for task in unique_tasks}

    return [df,color_dict]


class Calendar(object):

    def __init__(self):

        # initial definition; leave this unchanged for passing tests
        self.__holidays__ = [
            datetime(2024, 12, 25).date(),  # Christmas
            datetime(2024, 12, 26).date(),  # Day after Christmas
        ]

        # add the public holidays for the year to come
        import holidays
        current_year = datetime.now().year
        next_year = current_year + 1
        fr_holidays = holidays.France(years=next_year)
        self.__holidays__ += list(fr_holidays.keys())

        self.__holidays__.sort()

        self.__weekends__ = {5, 6}  # Saturday and Sunday

    def add_holiday(self, start_date : date, end_date=None) -> None:

        if not isinstance(start_date, date):
            raise ValueError("incompatible start_date type")

        if end_date is None:
            end_date = start_date

        if not isinstance(end_date, date):
            raise ValueError("incompatible end_date type")

        current_date = start_date
        while current_date <= end_date:
            self.__holidays__.append(current_date)
            current_date += timedelta(days=1)

        self.__holidays__.sort()

    def get_holidays(self,
                     start_date : date = datetime.today().date(),
                     end_date : date = datetime.today().date()+timedelta(days=365)) -> list[date] :

        ret = []
        for i in self.__holidays__:
            if start_date <= i and  i <= end_date :
                ret.append(i)

        return ret

    def count_working_days(self, start_date: date, end_date: date) -> int:

        if not isinstance(start_date, date):
            print("start date type : ", type(start_date))
            raise ValueError("incompatible start_date type")
        if not isinstance(end_date, date):
            print("end_date type : ", type(end_date))
            raise ValueError("incompatible end_date type")

        current_date = start_date
        working_days = 0
        while current_date <= end_date:
            if (current_date.weekday() not in self.__weekends__) and (
                current_date not in self.__holidays__
            ):
                working_days += 1
            current_date += timedelta(days=1)
        # print(f"Number of working days between {start_date.date()} and {end_date.date()}: {working_days}")
        return working_days

    def getDate_after_workDays(self, startDate: date, requiredWorkDays: int) -> date:

        if not isinstance(startDate, date):
            print("start date type : ", type(startDate))
            raise ValueError("incompatible start_date type")
        if not isinstance(requiredWorkDays, int):
            print("requiredWorkDays type : ", type(requiredWorkDays))
            raise ValueError("incompatible start_date type")

        end_date = startDate
        workdays = 0
        while workdays < requiredWorkDays - 1:
            if (end_date.weekday() not in self.__weekends__) and (
                end_date not in self.__holidays__
            ):
                workdays += 1
            end_date += timedelta(days=1)

        # correction: if the loop ended on friday, we have a saturday here,
        # so we need to move to next monday
        def next_monday(date):
            # Calculate how many days to add to get to the next Monday
            days_ahead = 7 - date.weekday()  # Monday is 0, Sunday is 6
            if (
                days_ahead == 0
            ):  # If the given date is already Monday, move to the next Monday
                days_ahead = 7
            return date + timedelta(days=days_ahead)

        if end_date.weekday() in self.__weekends__:
            end_date = next_monday(end_date)

        return end_date

    """ returns a list with the workdays in a given timeframe. Do not include holidays nor weekends"""
    def listWorkDays(self, start_date: date, end_date: date) -> list:

        if not isinstance(start_date, date):
            raise ValueError("incompatible start_date type")
        if not isinstance(end_date, date):
            raise ValueError("incompatible end_date type")
        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")

        workDays = []
        current_date = start_date
        while current_date <= end_date:
            if (current_date.weekday() not in self.__weekends__) and (
                current_date not in self.__holidays__
            ):
                workDays.append(current_date)
            current_date += timedelta(days=1)

        return workDays

    def listWeekEnds(self, start_date: date, end_date: date) -> list:

        if not isinstance(start_date, date):
            raise ValueError("incompatible start_date type")
        if not isinstance(end_date, date):
            raise ValueError("incompatible end_date type")
        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")

        weekEndDays = []
        current_date = start_date
        while current_date <= end_date:
            if (current_date.weekday() in self.__weekends__) and (
                current_date not in self.__holidays__
            ):
                weekEndDays.append(current_date)
            current_date += timedelta(days=1)

        return weekEndDays

    def to_dict(self) -> dict:
        return {"Holidays": [d.isoformat() for d in self.__holidays__]}

    @classmethod
    def from_dict(cls, data):

        tmp = cls()
        for i in data["Holidays"]:
            date = datetime.strptime(i, "%Y-%m-%d").date()
            # do NOT add holidays twice !
            if date not in tmp.__holidays__:
                tmp.add_holiday(date)
        return tmp

    def __eq__(self, other):

        if isinstance(other, Calendar):
            return self.__holidays__ == other.__holidays__

        return False

    def __str__(self) -> None:
        str = "Holiday list : "
        for i in self.__holidays__:
            str += "\n\t" + i.__str__()
        return str

from chargedPlanner.decorators import singleton

@singleton
class DevGroup(object):

    class DevBase(object):

        class ChargedWorkItemDict(dict) :

            def __setitem__(self, key, value):
                if not isinstance(key, Feature):
                    raise TypeError("Keys must be Features")
                if not isinstance(value, numbers.Number):
                    raise TypeError("values must be numbers")
                super().__setitem__(key, value)

            ''' Get the first element of the dictionary, that respects the condition indicated by the filter '''
            def getFirst(self, filter):
                for feat in self :
                    if filter(feat) :
                        return feat
                raise ValueError("item not found!")

        class WorkLoad(object):

            def __init__(self) :
                # Dictionary storing feature ids, and % load as float (range : 0-1)
                self.__chargedWorkItems__ = DevGroup.DevBase.ChargedWorkItemDict()
                self.__calendar__ = Calendar()

            def hasFeatureAssigned(self) -> bool :
                return len( self.__chargedWorkItems__ ) != 0

            def getCalendar(self) -> Calendar:
                return self.__calendar__

            """ 
			Returns a nested dictionary in the shape : {date : {feat , %} }
			For each workDay in the required range, a list with features, workload assigned to this dev  
			"""
            def getCalendarWorkload(
                self, begin: date, end: date
            ) -> Dict[date, Dict[Feature, int]]:

                if not isinstance(begin, date):
                    raise ValueError("begin is not a date!")
                if not isinstance(end, date):
                    raise ValueError("end is not a date!")

                workdays = self.__calendar__.listWorkDays(begin, end)

                # workload is a dictionary
                # {date : {feat , %} }
                calendarWorkLoad = {}
                for iDay in workdays:
                    for feat, purcentage in self.__chargedWorkItems__.items():
                        if iDay >= feat.getStartDate() and iDay <= feat.getEndDate():
                            if iDay not in calendarWorkLoad:
                                calendarWorkLoad[iDay] = {}
                            calendarWorkLoad[iDay][feat] = purcentage

                return calendarWorkLoad

            """ returns a list with the workdays in a given timeframe. Do not include holidays or weekends """
            def listWorkDays(self, start_date: date, end_date: date) -> list :

                return self.__calendar__.listWorkDays(start_date, end_date)

            """percentageLoad is expressed as an int in the range 0-100, but then stored as 0-1"""
            def setWorkLoad(
                self, feature: Feature, percentageLoad: float
            ) -> None:

                if not isinstance(feature, Feature):
                    raise ValueError("incompatible Feature type")

                if not isinstance(percentageLoad, numbers.Number):
                    raise ValueError("incompatible percentageLoad type")

                if feature in self.__chargedWorkItems__:
                    raise ValueError(
                        "Feature "
                        + feature.__name__
                        + " is already assigned to this dev. Cannot assign twice !"
                    )

                if percentageLoad < 1.:
                    raise ValueError(
                        "Cannot assign percentageLoad < 1%. Got " + percentageLoad.__str__()
                    )
                if percentageLoad > 100.:
                    raise ValueError(
                        "Cannot assign percentageLoad > 100%. Got " + percentageLoad.__str__()
                    )

                self.__chargedWorkItems__[feature] = percentageLoad / 100

                self.checkWorkload(feature.getStartDate(), feature.getEndDate())

            def removeWorkLoad(self, feature: Feature) -> None:

                if not isinstance(feature, Feature):
                    raise ValueError("incompatible Feature type")

                del self.__chargedWorkItems__[feature]

            def getWorkloadFor(self, day: date) -> float:

                if not isinstance(day, date):
                    raise ValueError("day is not a date!")

                calendarWorkLoad = self.getCalendarWorkload(day, day)

                purc = 0
                for iDay in calendarWorkLoad.keys():
                    for iPurc in calendarWorkLoad[iDay].values():
                        purc += iPurc
                return purc

            def checkWorkload(self, begin: date, end: date) -> None:

                if not isinstance(begin, date):
                    raise ValueError("begin is not a date!")
                if not isinstance(end, date):
                    raise ValueError("end is not a date!")

                calendarWorkLoad = self.getCalendarWorkload(begin, end)

                for iDay in calendarWorkLoad.keys():
                    purc = self.getWorkloadFor(iDay)
                    if purc > 1:
                        print("Workload " + iDay.__str__() + " = " + str(purc))

            def getEndDateForFeat(self, feature: Feature) -> date:

                if not isinstance(feature, Feature):
                    raise ValueError("incompatible Feature type")

                if not feature in self.__chargedWorkItems__:
                    raise ValueError(
                        "Feature " + feature.__name__ + " is not assigned to this dev"
                    )

                requireChargedDays = int(
                    feature.__remainingEffort__ / self.__chargedWorkItems__[feature]
                )

                # if the startDate is in the future, the shift the end date
                # otherwise, the work is ongoing. Only matters today and the remaining effort
                if (
                    feature.__startDate__ > datetime.now().date()
                    or is_running_under_pytest()
                ):
                    startDate = feature.__startDate__
                else:
                    startDate = datetime.now().date()

                return self.__calendar__.getDate_after_workDays(
                    startDate=startDate, requiredWorkDays=requireChargedDays
                )

            def getStartDateForFirstAssignedFeat(self, filter = defaultFilter) -> date :

                if not len(self.__chargedWorkItems__):
                    raise ValueError("No feature assigned to this dev, cannot infer the start date!")

                startDate = self.__chargedWorkItems__.getFirst(filter).getStartDate()

                for iFeat in self.__chargedWorkItems__:
                    if(filter(iFeat)) :
                        tmp = iFeat.getStartDate()
                        if tmp < startDate:
                            startDate = tmp

                return startDate

            def getEndDateForLatestAssignedFeat(self, filter = defaultFilter ) -> date :

                if not len(self.__chargedWorkItems__):
                    raise ValueError("No feature assigned to this dev, cannot infer the end date!")

                endDate = self.__chargedWorkItems__.getFirst(filter).getEndDate()

                for iFeat in self.__chargedWorkItems__:
                    if(filter(iFeat)) :
                        tmp = iFeat.getEndDate()
                        if tmp > endDate:
                            endDate = tmp

                return endDate

            def getTimeFrame(self):

                if not len(self.__chargedWorkItems__):
                    raise ValueError(
                        "No features assigned to this dev, no schedule can be computed"
                    )

                startDate = list(self.__chargedWorkItems__)[0].getStartDate()
                endDate = list(self.__chargedWorkItems__)[0].getEndDate()
                for feature in self.__chargedWorkItems__:
                    if feature.getStartDate() < startDate:
                        startDate = feature.getStartDate()
                    if feature.getEndDate() > endDate:
                        endDate = feature.getEndDate()
                return {"startDate": startDate, "endDate": endDate}

            def to_dict(self) -> dict:

                return {
                    # ChargedWorkItems cannot be serialised using to_dict as it contains a reference to
                    # Feature, that contains a ref to Dev -> it creates a circular dependency
                    "ChargedWorkItems": {
                        feature.get_identifier(): value
                        for feature, value in self.__chargedWorkItems__.items()
                    },
                    "Calendar": self.__calendar__.to_dict(),
                }

            @classmethod
            def from_dict(cls, data):

                # Note that self.__chargedWorkItems__ is NOT reassigned here;
                # in order to avoid circular dependencies, the mapping is restored at the
                # Feature level
                tmp = cls()
                tmp.__calendar__ = Calendar.from_dict(data["Calendar"])
                return tmp

            def __eq__(self, other):

                if isinstance(other, DevGroup.DevBase.WorkLoad):
                    return self.__calendar__ == other.__calendar__
                """
				Cannot compare the __chargedWorkItems__. This would break the project save and
				reload. In effect, in that case :
				1_ we instanciate the project and assign the feats to dev
				2_ we save the project
				3_ we instanciate and reload a new project
				4_ while reloading, we do assing the same workload to the devs twice !
				5_ the new workload is not consistent with the workload that was saved
				6_ the == operator on the assingnee workload returns False
				"""
                # 	self.__chargedWorkItems__ == other.__chargedWorkItems__
                return False

            def __str__(self) -> str:
                str = "Workload for this dev = \n"
                str += "--------------------------------------\n"
                for feat, purc in self.__chargedWorkItems__.items():
                    str += (
                        feat.__name__
                        + " "
                        + (100 * purc).__str__()
                        + "%, ("
                        + feat.__startDate__.__str__()
                        + " -> "
                        + feat.getEndDate().__str__()
                        + ")\n"
                    )
                str += "--------------------------------------\n"
                return str

        def __init__(self, devName : str ) :

            if not isinstance(devName, str):
                raise ValueError("devName must be a str!!")

            self.__name__ = devName
            self.__workload__ = self.WorkLoad()

        def getCalendar(self) -> Calendar:
            return self.getWorkload().getCalendar()

        def add_holiday(self, start_date: date, end_date: date) -> None:
            self.getCalendar().add_holiday(start_date, end_date)

        def get_holydays(self) -> list[datetime.date]:
            return self.getCalendar().get_holidays()

        def count_workdays(self, start_date: date, end_date: date) -> int:
            return self.getCalendar().count_working_days(start_date, end_date)

        def addWorkLoad(self, feat: Feature, percentageLoad: int) -> None:

            if not isinstance(feat, Feature):
                raise ValueError("incompatible feature type")

            if not isinstance(percentageLoad, numbers.Number):
                raise ValueError("incompatible percentageLoad type")

            if feat.__assignee__ == None:
                feat.__assignee__ = self

            if feat.__assignee__ != self:
                raise ValueError(
                    "Feature "
                    + feat.__name__
                    + " is already assigned to "
                    + feat.__assignee__.__name__
                )

            self.__workload__.setWorkLoad(feat, percentageLoad=percentageLoad)

        def removeWorkLoad(self, feat: Feature) -> None:

            feat.__assignee__ = None
            self.__workload__.removeWorkLoad(feat)

        def getWorkload(self) -> WorkLoad:
            return self.__workload__

        def getWorkloadFor(self, day: date) -> float:
            return self.getWorkload().getWorkloadFor(day)

        """ returns the first start date amongs all the features assigned  """

        def getStartDateForFirstAssignedFeat(self) -> date :
            return self.getWorkload().getStartDateForFirstAssignedFeat()

        """ returns the date of end for a specific feature assigned to this dev"""

        def getEndDateForFeat(self, feature: Feature) -> date:
            return self.getWorkload().getEndDateForFeat(feature)

        """ returns the latest end date amongs all the features assigned  """

        def getEndDateForLatestAssignedFeat(self) -> date :
            return self.getWorkload().getEndDateForLatestAssignedFeat()

        """ What are the dates of the first and the last features scheduled for this dev ?"""

        def getTimeFrame(self):
            return self.getWorkload().getTimeFrame()

        def luccaConnector(self, luccaID : int) -> None :

            startDate = datetime.today().date()
            endDate = startDate + timedelta(days=120)

            from chargedPlanner.LuccaAPI import LuccaAPI
            for i in LuccaAPI().getLeaves(luccaID,startDate,endDate) :
                self.add_holiday(i,i)

        def gantt(self) -> None:

            import plotly.figure_factory as ff

            tasks = []
            for i in self.getCalendar().get_holidays(
                        self.getStartDateForFirstAssignedFeat(),
                        self.getEndDateForLatestAssignedFeat() ):
                tasks.append(
                    dict(
                        Task="Holiday",
                        Start=i.__str__(),
                        Finish=(i + timedelta(days=1)).__str__(),
                        Purcentage=str(100)+"%"
                    )
                )

            timeRange = self.getTimeFrame()
            weekends = self.getCalendar().listWeekEnds(
                timeRange["startDate"], timeRange["endDate"]
            )

            for i in weekends :
                tasks.append(
                    dict(
                        Task="Weekends",
                        Start=i.__str__(),
                        Finish=(i + timedelta(days=1)).__str__(),
                        Purcentage=str(100) + "%"
                    )
                )

            for i in self.getWorkload().__chargedWorkItems__.keys():
                tasks.append(
                    dict(
                        Task=i.__name__,
                        Start=i.getStartDate().__str__(),
                        Finish=i.getEndDate().__str__(),
                        Purcentage=str(i.getPurcentageLoad()*100) + "%",
                    )
                )

            if not len(tasks):
                return

            [df,color_dict] = prepare_for_gantt(tasks)

            fig = ff.create_gantt(df, colors=color_dict, index_col="Task", show_colorbar=False, group_tasks=True,
                                   title="Gantt chart for Developer : " + self.__name__)

            for index, value in enumerate(fig.data[: len(tasks)]):
                taskName = value['name']
                if taskName == "" :
                    continue
                correspondingTaskIndex = next((i for i, task in enumerate(tasks) if task['Task'] == taskName), -1)
                if correspondingTaskIndex == -1:
                    raise ValueError("Index not found !")
                value.update(text= tasks[correspondingTaskIndex]["Task"] + ": " + tasks[correspondingTaskIndex]["Purcentage"], hoverinfo="text")

            current_date = datetime.today().strftime("%Y-%m-%d")

            # Add a vertical line for the current date (Use add_vline for Plotly v5+)
            fig.add_vline(x=current_date, line=dict(color="red", width=2, dash="dash"))

            # Add a vertical line at the end of each weekend
            for index, i in enumerate(weekends) :
                if index % 2 == 0:  # Check if the index is even
                    fig.add_vline(x=i, line=dict(color="grey", width=1, dash="dot"))
                else:
                    fig.add_vline(x=i + timedelta(days=1), line=dict(color="grey", width=1, dash="dot"))

            fig.update_layout(
                plot_bgcolor="lightgrey",  # Set the background color of the plot area
                paper_bgcolor="white",  # Set the background color of the entire figure
                title_font=dict(size=18, color="black", weight=10),  # Customize title appearance
                font=dict(size=12, color="black"),  # Customize font for the entire chart
            )

            fig.show()

        def loadChart(self) -> None:

            # Find the bounds : min and max date for all tasks
            first_feat = next(iter(self.getWorkload().__chargedWorkItems__))
            startDate = first_feat.__startDate__
            endDate = first_feat.getEndDate()
            for i in self.getWorkload().__chargedWorkItems__.keys():
                if i.__startDate__ < startDate:
                    startDate = i.__startDate__
                iEnd = i.getEndDate()
                if iEnd > endDate:
                    endDate = iEnd

            calendarWorkLoad = self.getWorkload().getCalendarWorkload(
                startDate, endDate
            )

            timeRange = self.getTimeFrame()
            weekends = self.getCalendar().listWeekEnds(
                timeRange["startDate"], timeRange["endDate"]
            )

            x_values = []
            y_values = []
            custom_hover_text = []

            for iDay in calendarWorkLoad.keys():
                x_values.append(iDay)
                purc = 0
                hoverText = str(iDay) + ":"

                for index, (key, value) in enumerate(calendarWorkLoad[iDay].items()):
                    purc += value
                    hoverText += key.get_identifier() + ","

                y_values.append(purc*100)
                custom_hover_text.append(hoverText)

            import plotly.graph_objects as go

            colors = ["red" if y > 100 else "blue" for y in y_values]

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode="lines+markers",  # Use 'lines+markers' for both lines and markers
                    name="Load Chart",
                    marker=dict(
                        size=12,
                        color=colors,  # Assign the conditional colors
                    ),
                    hovertext=custom_hover_text,  # Custom hover text
                    hoverinfo='text',  # Use only the text for hover

                )
            )

            fig.update_yaxes(
                range=[0, max(y_values) * 1.1]
            )  # Set y-axis range from 10 to 20

            fig.update_layout(
                title="WorkLoad Plot for developer : " + self.__name__,
                xaxis_title="Date",
                yaxis_title="Workload %",
            )

            current_date = datetime.today().strftime("%Y-%m-%d")

            # Add a vertical line for the current date (Use add_vline for Plotly v5+)
            fig.add_vline(x=current_date, line=dict(color="red", width=2, dash="dash"))

            for index, i in enumerate(weekends) :
                if index % 2 == 0:  # Check if the index is even
                    fig.add_vline(x=i, line=dict(color="grey", width=1, dash="dot"))
                else:
                    fig.add_vline(x=i + timedelta(days=1), line=dict(color="grey", width=1, dash="dot"))

            # Show the plot
            fig.show()

        def to_dict(self) -> dict:

            return {
                "DevName": self.__name__,
                "DevType": self.__class__.__name__,
                "Calendar": self.getCalendar().to_dict(),
                "Workload": self.__workload__.to_dict(),
            }

        @classmethod
        def from_dict(cls, data):

            ret = cls(data["DevName"])
            ret.__workload__ = cls.WorkLoad.from_dict(data["Workload"])
            return ret

        def getIdentifier(self):
            return self.__name__

        def __eq__(self, other):

            if isinstance(other, DevGroup.DevBase):
                return (
                    self.__name__ == other.__name__
                    and self.__workload__ == other.__workload__
                )

            return False

        def __str__(self) -> str:
            str = (
                "Dev info : "
                + "\n\tname= "
                + self.__name__
                + "\n\t"
                + self.__workload__.__str__()
            )
            return str

    class Dev(DevBase) :

        def __init__(self, devName : str ) :

            super().__init__(devName)

            # A dev is supposedly loaded at 20% because of various meetings
            PersistentFeature("Dev Meetings", self, 20)

    class Manager(DevBase) :

        def __init__(self, devName : str ) :

            super().__init__(devName)

            # A manager is supposedly loaded at 40% because of various meetings
            PersistentFeature("Dev Meetings", self, 20)
            PersistentFeature("Management", self, 20)

    def __createDev__(self, jsonEntry : dict):

        dev = None

        # Create the dev
        if jsonEntry["devType"] == DevGroup.Dev.__name__:
            dev = DevGroup.Dev(jsonEntry["name"])

        elif jsonEntry["devType"] == DevGroup.Manager.__name__:
            dev = DevGroup.Manager(jsonEntry["name"])

        else:
            raise ValueError("Dev type " + jsonEntry["devType"] + " not recognised !")

        # Ties to Lucca
        if not  is_running_under_pytest() :
            if "luccaID" in jsonEntry:
                dev.luccaConnector(jsonEntry["luccaID"])

        self.__devs__.append(dev)


    def __init__(self):

        self.__devs__ = []

    # Lazy evaluation to instanciate a dev with its info
    def __getitem__(self, key) -> DevBase:

        dev = next((d for d in self.__devs__ if d.__name__ == key), None)

        if not dev:
            from chargedPlanner.tools import get_config_filePath
            with open(get_config_filePath(), "r") as f:
                devDict = json.load(f)
                f.close()

                for iEntry in devDict["devs"] :
                    if iEntry["name"] == key :
                        self.__createDev__(iEntry)

                dev = next((d for d in self.__devs__ if d.__name__ == key), None)

        return dev


class Feature(object):

    def __init__(
        self,
        featName: str,
        totalEffort: int,
        remainingEffort: int,
        assignee: DevGroup.DevBase = None,
        percentageLoad: numbers.Number = 0,
        startDate: date = datetime.today().date(),
    ):

        if not isinstance(featName, str):
            raise ValueError("featName is not a str!")
        if not isinstance(totalEffort, int):
            raise ValueError("totalEffort is not an int!")
        if not isinstance(remainingEffort, int):
            raise ValueError("remainingEffort is not an int!")
        if not isinstance(startDate, date):
            raise ValueError("startDate is not a date!")

        self.__name__ = featName
        self.__startDate__ = startDate
        self.__totalEffort__ = totalEffort
        self.__remainingEffort__ = remainingEffort
        self.__assignee__ = None

        if assignee is not None:

            if not isinstance(assignee, DevGroup.DevBase):
                raise ValueError("assignee is not a Dev!")
            if not isinstance(percentageLoad, numbers.Number):
                raise ValueError("effort is not a Number!")
            if percentageLoad == 0:
                raise ValueError("The effort for this feature is set to zero !")

            self.__assignee__ = assignee
            self.__assignee__.addWorkLoad(self, percentageLoad)

    def getStartDate(self) -> date:

        return self.__startDate__

    def getEndDate(self) -> date:

        if self.__assignee__ is None:
            raise ValueError("No assingee assigned to feature : " + self.__name__)

        return self.__assignee__.getEndDateForFeat(self)

    # Returns the purcentageload. This is a float in the range 0-1
    def getPurcentageLoad(self) -> float :
        return self.__assignee__.getWorkload().__chargedWorkItems__[self]

    def to_dict(self) -> dict:

        return {
            "FeatureName": self.__name__,
            "StartDate": str(self.__startDate__),
            "TotalEffort": str(self.__totalEffort__),
            "RemainingEffort": str(self.__remainingEffort__),
            "Assignee": self.__assignee__.to_dict(),
            "PercentageLoad": self.getPurcentageLoad(),
        }

    @classmethod
    def from_dict(cls, data):

        devs = DevGroup()

        assignee = DevGroup.DevBase.from_dict(data["Assignee"])

        assignee = devs[assignee.__name__]

        purcLoad = data["PercentageLoad"] * 100

        remainingEffort = int(data["RemainingEffort"])
        totalEffort = int(data["TotalEffort"]) if "TotalEffort" in data else remainingEffort

        tmp = cls(
            featName=data["FeatureName"],
            totalEffort=totalEffort,
            remainingEffort=remainingEffort,
            startDate=datetime.strptime(data["StartDate"], "%Y-%m-%d").date(),
        )

        # Add the workload to this assignee
        assignee.addWorkLoad(tmp, purcLoad)
        tmp.__assignee__ = assignee

        return tmp

    def __dereference__(self):
        self.__assignee__.removeWorkLoad(self)

    def __eq__(self, other):

        if isinstance(other, Feature):
            return (
                self.__name__ == other.__name__
                and self.__remainingEffort__ == other.__remainingEffort__
                and self.__totalEffort__ == other.__totalEffort__
            )
        """Remove the dates : I cannot have two projects with the
        same features and the same schedule (otherwise I am
        assigning twice the same feature to the same dev, which
        is not allowed. Cannot compare the dev either, for the same reason"""
        # 	self.__assignee__ == other.__assignee__	and \
        # 	self.getStartDate() == other.getStartDate() and \
        # self.getEndDate() == other.getEndDate() and \

        return False

    def __hash__(self):
        return hash(self.__name__)

    def get_identifier(self):
        return self.__name__

    def __str__(self) -> None:
        str = (
            "\nFeature : "
            + self.__name__
            + "\n\tAssignee :"
            + self.__assignee__.__str__()
            + "\n\tStart date : "
            + self.__startDate__.__str__()
            + "\n\tTotal effort :"
            + self.__totalEffort__.__str__()
            + "\n\tRemaining effort :"
            + self.__remainingEffort__.__str__()
        )
        return str

class PersistentFeature(Feature) :

        def __init__(
            self,
            featName: str,
            assignee: DevGroup.DevBase,
            percentageLoad: numbers.Number = 0
            ):

            super().__init__(featName=featName,
                             totalEffort = 1,
                             remainingEffort = 1,
                             assignee=assignee,
                             percentageLoad=percentageLoad,
                             startDate=datetime.today().date())

        def getStartDate(self) :

            def filter(feat):
                return not isinstance(feat, PersistentFeature)

            try:
                startDate = self.__assignee__.getWorkload().getStartDateForFirstAssignedFeat(filter)
            except ValueError as e:
                startDate = datetime.today().date()

            return startDate

        def getEndDate(self) :

            def filter(feat):
                return not isinstance(feat, PersistentFeature)

            try:
                endDate = self.__assignee__.getWorkload().getEndDateForLatestAssignedFeat(filter)
            except ValueError as e:
                endDate = datetime.today().date()

            return endDate

''' 
The FixedTimeSpanTrailingFeature is a Feature desinged to describe testing and documentation tasks 
Tis Feature : 
-> Spans on a fixed time interval (ie: this will lasts for 15 days).
-> Is placed after the end of the last Feature of a Version  
-> Has an assignee
-> The effort of the assignee is computed as a % of the sum of the Features of the Version 
    Rational :  when a person tests (or documents) one version, it works on all features at the time
'''
class FixedTimeSpanTrailingFeature(Feature) :

    def __init__(
        self,
        featName: str,
        timespan : timedelta,
        percentageLoad : int = 5,
        version : Version = None,
        assignee : DevGroup.DevBase = None,
    ) :

        if not isinstance(featName, str):
            raise ValueError("featName"+ str(featName) +" is not a str!")
        if not isinstance(version, Version):
            raise ValueError("version is not a Version!")
        if not isinstance(assignee, DevGroup.DevBase):
            raise ValueError("assignee is not a Dev!")

        # this featutre starts at the end of the current version
        startDate = version.getEndDate()

        # How many workdays since the starting ? +1 to fix boundary conditions
        workDays = assignee.count_workdays(startDate, startDate+timespan)

        totalEffort = 0
        for i in version.__features__ :
            if not isinstance(i,FixedTimeSpanTrailingFeature) :
                totalEffort += percentageLoad / 100 * i.__totalEffort__

        # round the value to the highest integer [days]
        totalEffort = math.ceil(totalEffort)

        percentageLoad = 100 * totalEffort / (workDays)

        super().__init__(featName=featName,
                         totalEffort = totalEffort,
                         remainingEffort = totalEffort,
                         assignee=assignee,
                         percentageLoad=percentageLoad,
                         startDate=startDate)


class TestingFeature(FixedTimeSpanTrailingFeature) :

    def __init__(
        self,
        timespan : timedelta,
        version : Version,
        assignee : DevGroup.DevBase = None,
        percentageLoad : int = 5,
    ) :

        featName= version.name() + "_testing"

        super().__init__(
                        featName=featName,
                        timespan= timespan,
                        percentageLoad = percentageLoad,
                        version = version,
                        assignee = assignee)

class DebugFeature(FixedTimeSpanTrailingFeature) :

    def __init__(
        self,
        timespan : timedelta,
        version : Version,
        assignee : DevGroup.DevBase = None,
        percentageLoad : int = 5,
    ) :

        featName= version.name() + "_debug"

        super().__init__(
                        featName=featName,
                        timespan= timespan,
                        percentageLoad = percentageLoad,
                        version = version,
                        assignee = assignee)


class DocumentationFeature(FixedTimeSpanTrailingFeature) :

    def __init__(
        self,
        timespan : timedelta,
        version : Version,
        assignee : DevGroup.DevBase = None,
        percentageLoad : int = 5
    ) :

        featName= version.name() + "_documentation"

        super().__init__(
                        featName=featName,
                        timespan= timespan,
                        percentageLoad = percentageLoad,
                        version = version,
                        assignee = assignee)



class IconeusProduct(Enum):
    IcoStudio = "IcoStudio"
    IcoLab = "IcoLab"
    IcoScan = "IcoScan"


class Version(object):

    def __init__(self, product: IconeusProduct, versionTag: str):

        if not isinstance(product, IconeusProduct):
            raise ValueError("Product should be a value of the enum IconeusProduct !")

        self.__tag__ = versionTag
        self.__features__ = []
        self.__product__ = product

    def getTag(self) -> str:
        return self.__tag__

    def name(self) -> str :
        return str(self.__product__.value + " " + self.getTag())

    def addFeat(self, feat: Feature) -> None :
        self.__features__.append(feat)

    def getStartDate(self) -> date:

        if not len(features):
            raise ValueError(
                "No features assigned to this version : the start date cannot be computed"
            )

        startDate = self.__features__[0].__startDate__
        for i in self.__features__:
            tmp = i.__startDate__
            if tmp < startDate:
                startDate = tmp
        return startDate

    def getEndDate(self) -> date:

        endDate = self.__features__[0].getEndDate()
        for i in self.__features__:
            tmp = i.getEndDate()
            if tmp > endDate:
                endDate = tmp
        return endDate

    def getFeature(self, featureLabel: str) -> Feature:
        ret = next((f for f in self.__features__ if f.__name__ == featureLabel), None)
        if ret is None:
            raise ValueError(
                "Feature " + featureLabel + " not found in Version " + self.getTag()
            )
        return ret

    def gantt(self) -> None:

        import plotly.figure_factory as ff

        tasks = []
        for i in self.__features__:
            tasks.append(
                dict(
                    Task=i.__name__,
                    Start=i.__startDate__.__str__(),
                    Finish=i.getEndDate().__str__(),
                    Assignee=i.__assignee__.__name__,
                )
            )

        if not len(tasks):
            return

        fig = ff.create_gantt(
            tasks,
            group_tasks=True,
            index_col="Task",
            title="Gantt chart for "
            + self.__product__.name.__str__()
            + " version : "
            + self.__tag__,
        )

        fig.update_layout(
            plot_bgcolor="peachpuff",  # Set the background color of the plot area
            paper_bgcolor="white",  # Set the background color of the entire figure
            title_font=dict(size=18, color="black", weight=10),  # Customize title appearance
            font=dict(size=12, color="black"),  # Customize font for the entire chart
        )

        # loop on the figure data to override the hoverInfo. Each task reports its assignee
        for index, value in enumerate(fig.data[: len(tasks)]):
            taskName= value['name']
            correspondingTaskIndex = next((i for i, task in enumerate(tasks) if task['Task'] == taskName), -1)
            # in the plot data there are several objects, some (ie: legends) do not match the taks names so their
            # index is not found
            if correspondingTaskIndex != -1 :
                value.update(text="Assignee: " + tasks[correspondingTaskIndex]["Assignee"], hoverinfo="text")

        current_date = datetime.today().strftime("%Y-%m-%d")

        # Add a vertical line for the current date (Use add_vline for Plotly v5+)
        fig.add_vline(x=current_date, line=dict(color="red", width=2, dash="dash"))

        fig.show()

    def __dereference__(self):
        [feature.__dereference__() for feature in self.__features__]

    def to_dict(self) -> dict:

        return {
            "Product": str(self.__product__.value),
            "VersionTag": str(self.__tag__),
            "Features": [feature.to_dict() for feature in self.__features__],
        }

    def __features_from_dict__(self, data):
        self.__features__ = [Feature.from_dict(feature) for feature in data]

    @classmethod
    def from_dict(cls, data):
        ret = cls(IconeusProduct(data["Product"]), data["VersionTag"])
        ret.__features_from_dict__(data["Features"])
        return ret

    def __eq__(self, other):

        if isinstance(other, Version):
            return (
                self.__product__ == other.__product__
                and self.__tag__ == other.__tag__
                and self.__features__ == other.__features__
            )
        """Remove the dates : I cannot have two projects with the
		same features and the same schedule (otherwise I am
		assigning twice the same feature to the same dev, which
		is not allowed"""
        # 	self.getStartDate() == other.getStartDate() and \
        # self.getEndDate() == other.getEndDate() and \
        return False

    def __str__(self) -> None:

        str = (
            "Version : "
            + self.__tag__
            + " for product : "
            + self.__product__.__str__()
            + "\n"
        )
        for i in self.__features__:
            str += "\t" + i.__str__()
        return str


class IcoStudioVersion(Version):

    def __init__(self, versionTag: str):
        super().__init__(IconeusProduct.IcoStudio, versionTag)

    @classmethod
    def from_dict(cls, data):
        ret = cls(data["VersionTag"])
        ret.__features_from_dict__(data["Features"])
        return ret


class IcoLabVersion(Version):

    def __init__(self, versionTag: str):
        super().__init__(IconeusProduct.IcoLab, versionTag)

    @classmethod
    def from_dict(cls, data):
        ret = cls(data["VersionTag"])
        ret.__features_from_dict__(data["Features"])
        return ret


class IcoScanVersion(Version):

    def __init__(self, versionTag: str):
        super().__init__(IconeusProduct.IcoScan, versionTag)

    @classmethod
    def from_dict(cls, data):
        ret = cls(data["VersionTag"])
        ret.__features_from_dict__(data["Features"])
        return ret


class Project(object):

    version_classes = {
        IconeusProduct.IcoStudio: IcoStudioVersion,
        IconeusProduct.IcoLab: IcoLabVersion,
        IconeusProduct.IcoScan: IcoScanVersion,
    }

    def __init__(self, iconeusProduct: Enum):
        self.__versions__ = []
        self.__product__ = iconeusProduct

    def addVersion(self, version: Version) -> None:
        if not self.__product__ == version.__product__:
            str = (
                "Adding version for product: "
                + version.__product__.__str__()
                + " while in "
                + self.__product__.__str__(),
                "  project.\nA version can be added to a Project "
                + "only for the same product!",
            )
            raise ValueError(str)
        self.__versions__.append(version)

    def getVersion(self, versionTag: str):

        ret = next((v for v in self.__versions__ if v.getTag() == versionTag), None)
        if ret is None:
            raise ValueError("versionTag not found ! ")

        return ret

    def getStartDate(self):

        if not len(self.__versions__):
            raise ValueError(
                "No versions have been instanciated for this Project, thus the starting date cannot be retrieved"
            )

        startDate = self.__versions__[0].getStartDate()
        for i in self.__versions__:
            tmp = i.getStartDate()
            if tmp < startDate:
                startDate = tmp
        return startDate

    def getEndDate(self):

        endDate = self.__versions__[0].getEndDate()
        for i in self.__versions__:
            tmp = i.getEndDate()
            if tmp > endDate:
                endDate = tmp
        return endDate

    def gantt(self) -> None:

        import plotly.figure_factory as ff

        tasks = []
        for i in self.__versions__:
            tasks.append(
                dict(
                    Task=i.__tag__,
                    Start=i.getStartDate().__str__(),
                    Finish=i.getEndDate().__str__(),
                )
            )

        if not len(tasks):
            return

        fig = ff.create_gantt(
            tasks,
            group_tasks=True,
            title="Gantt chart for Project : " + self.__product__.name.__str__(),
        )

        fig.update_layout(
            plot_bgcolor="lightblue",  # Set the background color of the plot area
            paper_bgcolor="white",  # Set the background color of the entire figure
            title_font=dict(size=18, color="black"),  # Customize title appearance
            font=dict(size=12, color="black"),  # Customize font for the entire chart
        )

        current_date = datetime.today().strftime("%Y-%m-%d")

        # Add a vertical line for the current date (Use add_vline for Plotly v5+)
        fig.add_vline(x=current_date, line=dict(color="red", width=2, dash="dash"))

        fig.show()

    def to_dict(self) -> dict:

        return {
            "ProjectFileVersion": "1.0",
            "Product": str(self.__product__.value),
            "Versions": [version.to_dict() for version in self.__versions__],
        }

    @classmethod
    def from_dict(cls, data):

        projectFile_version = data["ProjectFileVersion"]

        product_type = IconeusProduct(data["Product"])

        version_class = cls.version_classes.get(product_type, Version)

        project_instance = cls(IconeusProduct(data["Product"]))

        project_instance.__versions__ = [
            version_class.from_dict(version_data)
            for version_data in data.get("Versions", [])
        ]

        return project_instance

    def serialise(self) -> None:
        with open("Project.json", "w") as json_file:
            outDict = self.to_dict()
            json.dump(outDict, json_file, indent=4)

    @classmethod
    def unserialise(cls) -> Project:

        with open("project.json", "r") as json_file:
            project_dict = json.load(json_file)
            return cls.from_dict(project_dict)

    def __dereference__(self):
        [version.__dereference__() for version in self.__versions__]

    def __eq__(self, other):

        if isinstance(other, Project):
            return (
                self.__product__ == other.__product__
                and self.__versions__ == other.__versions__
            )
        """Remove the dates : I cannot have two projects with the
    	same features and the same schedule (otherwise I am
        assigning twice the same feature to the same dev, which
        is not allowed"""
        # self.getStartDate() == other.getStartDate() and \
        # self.getEndDate() == other.getEndDate() and \
        return False

    def __str__(self) -> None:
        str = "Project " + self.__product__.name + "\n"
        for i in self.__versions__:
            str += "\t" + i.__str__()
        return str
