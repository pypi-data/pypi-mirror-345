# DevTeam Gantt Planner

DevTeam Gantt Planner is a Python-based tool designed to assist development teams in creating and visualizing Gantt charts for project planning and task management.

## Features

Project Scheduling: Define Features, define the required effort, assign them to developers within the DevTeam. Outline project timelines.

Lucca Integration : the Lucca API can be leveraged to retrieve the holidays of the developers. Project planning will be modified accordingly 

Team Assignment: Allocate tasks to specific developers or teams.

Gantt Chart Generation: Visualize project schedules through interactive Gantt charts.

Once a project is defined, it is possible to visualise it as Gantt chart with different levels of granularity (Project, Version). See below the Gantt chart for a specific version of the project : 

![image](https://github.com/Iconeus/chargedPlanner/blob/main/docs/images/VersionGantt.PNG)

At the developer level, the associated workload can be visualised under the form of a Gannt diagram, or a loadchart. Peaks overcoming 100% effort are highlighted in red :

![image](https://github.com/Iconeus/chargedPlanner/blob/main/docs/images/DevGantt.PNG)

![image](https://github.com/Iconeus/chargedPlanner/blob/main/docs/images/DevCharge.PNG)


## Feature type 

Three types of features are made avalable : 

**Feature** are used to describe specific tasks assigned to a developer, and the associated effort  

**PersistentFeature** are used to book the developers time on the whole time span of their activity. Typically this is useful for taking into account persintent / recurrent tasks such as general meeting time. By default, 20% of the developers time is assigned to meetings via a **PersistentFeature**

**TestingFeature** and **DocumentationFeature** are specific Features that append at the end of a Version. While their lenght is fixed (ie: 15days) the effor required to the assigned developer is computed as a percentage of the global effort required for the version. 


## User Installation

Users can install the latest version of the library direclty from pip via: 
```
  pip install chargedPlanner
```

## Dev Installation

Ensure you have Python 3.6 or higher installed. Then, install the required dependencies:
```
  pip install -r requirements.txt
```

Clone the Repository:

```
https://github.com/Iconeus/chargedPlanner
```

## Prepare Your Data:

Create a json file named devs.json with the following structure:

```
{
    "luccaURL" : "https://iconeus-rh.ilucca.net/api/v3/leaves",
    "devs": [
        {
            "devType": "Manager",
            "name": "<managerName>"
            "luccaID": <luccaID>
        },
        {
            "devType": "Dev",
            "name": "<devName>"
            "luccaID": <luccaID>
        },
}
```

Fill all the devs of your group and place the file in the project resource folder : 
```
C:\Users\<currentUser>\.config\chargedPlanner\config.json
```
Note that the lucca URL and ID are optional, and must only be filed if a link to Lucca is required. The link to Lucca allows automatical retrieval of the holidays of the dev team.

In this case, an api token is required to access the lucca REST API. The token must be saved to the windows credential manager. User must be defined as 'dummy' :

![image](https://github.com/Iconeus/chargedPlanner/blob/main/docs/images/credentialManager.png)


## Getting started :

```python
from chargedPlanner import * 

charles = DevGroup()["Charles"]
selene = DevGroup()["Selene"]

connFeat = Feature(featName="Connectivity",
                   remainingEffort=5,
                   assignee=charles,
                   percentageLoad = 20,
                   startDate=datetime(2024, 12, 26).date())

seedMapFeat = Feature(featName="SeedMap",
                      remainingEffort=15,
                      assignee=selene,
                      percentageLoad=20,
                      startDate=datetime(2024, 11, 15).date())

scanV2Feat = Feature(featName="ScanV2",
                    remainingEffort=15,
                     assignee=charles,
                     percentageLoad=40,
                     startDate=charles.getEndDateForLatestAssignedFeat())

testing = TestingFeature(
        version=version1,
        assignee=selene,
        purcentage=5,
        timespan=timedelta(days=15)
    )

documentation = DocumentationFeature(
        version=version1,
        assignee=daniele,
        purcentage=5,
        timespan=timedelta(days=15)
    )

version1 = IcoStudioVersion("1.0.0")
version1.addFeat(connFeat)
version1.addFeat(seedMapFeat)
version1.addFeat(testing)
version1.addFeat(documentation)

version2 = IcoStudioVersion("1.1.0")
version2.addFeat(scanV2Feat)
version2.addFeat(testing)
version2.addFeat(documentation)

icoStudioProject = Project(IconeusProduct.IcoStudio)
icoStudioProject.addVersion(version1)
icoStudioProject.addVersion(version2)

print(icoStudioProject)
icoStudioProject.gantt()

version1.gantt()

charles.gantt()
charles.loadChart()

selene.gantt()
selene.loadChart()

icoStudioProject.serialise()
```

See the auto tests for code usage 


## Dependencies

See file : requirements.txt

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

Special thanks to the contributors of the following resources:
Gantt Charts in Python - Plotly
