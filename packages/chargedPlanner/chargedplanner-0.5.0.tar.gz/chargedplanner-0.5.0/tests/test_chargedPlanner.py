import pytest
from datetime import datetime, timedelta

def test_setup():
	from chargedPlanner.chargedPlanner import DevGroup
	DevGroup.reset_instance()  # Clear all instances

def test_calendar_instance():

	from chargedPlanner.chargedPlanner import Calendar
	cal = Calendar()
	assert cal is not None

def test_calendar_add_holiday():

	from chargedPlanner.chargedPlanner import Calendar
	cal = Calendar()

	cal.add_holiday(datetime(2024, 12, 23).date())

	holidays = cal.get_holidays(
		start_date=datetime(2024, 12, 20).date(),
		end_date=datetime(2024, 12, 30).date()
	)

	assert holidays == [
		datetime(2024, 12, 23).date(),
		datetime(2024, 12, 25).date(),
		datetime(2024, 12, 26).date()
	]

def test_calendar_date_delta():

	from chargedPlanner.chargedPlanner import Calendar
	cal = Calendar()
	assert cal.count_working_days(datetime(2024,12,27).date(),datetime(2025,1,2).date()) == 5

	with pytest.raises(ValueError):
		cal.count_working_days(12,datetime(2025,1,2))

	with pytest.raises(ValueError):
		cal.count_working_days(datetime(2025,1,2),12)

def test_calendar_add_holiday():

	from chargedPlanner.chargedPlanner import Calendar

	test_calendar_date_delta()

	cal = Calendar()

	cal.add_holiday(datetime(2024,12,27).date())

	assert cal.count_working_days(datetime(2024,12,27).date(),datetime(2025,1,2).date()) == 4

	cal.add_holiday(datetime(2025,1,1).date(), datetime(2025,1,3).date())

	assert cal.count_working_days(datetime(2024,12,27).date(),datetime(2025,1,4).date()) == 2

def test_calendar_getHolidays():

	from chargedPlanner.chargedPlanner import Calendar

	cal = Calendar()

	h = cal.get_holidays(
		datetime(2024, 12, 24).date(),
		datetime(2024, 12, 26).date())

	assert h == [ datetime(2024, 12, 25).date(),
				  datetime(2024, 12, 26).date() ]

def test_calendar_getDate_after_workDays() : 

	from chargedPlanner.chargedPlanner import Calendar

	cal = Calendar()

	cal.add_holiday(datetime(2024,12,27).date())

	assert(cal.getDate_after_workDays(startDate =datetime(2024,12,20).date(), requiredWorkDays=3) == datetime(2024,12,24).date())
	assert(cal.getDate_after_workDays(startDate =datetime(2024,12,24).date(), requiredWorkDays=3) == datetime(2024,12,31).date())
	assert(cal.getDate_after_workDays(startDate =datetime(2024,12,30).date(), requiredWorkDays=4) == datetime(2025,1,2).date())

	with pytest.raises(ValueError):
		assert (cal.getDate_after_workDays(1, requiredWorkDays=4) == datetime(2025, 1, 2).date())
	with pytest.raises(ValueError):
		assert (cal.getDate_after_workDays(startDate=datetime(2024, 12, 30).date(), requiredWorkDays="a"))

def test_calendar_listWorkDays() :

	from chargedPlanner.chargedPlanner import Calendar

	cal = Calendar()

	l = cal.listWorkDays(start_date=datetime(2024, 12, 24).date(),
				   end_date=datetime(2024, 12, 31).date())

	assert l == [
		datetime(2024, 12, 24).date(),
		datetime(2024, 12, 27).date(),
		datetime(2024, 12, 30).date(),
		datetime(2024, 12, 31).date()
	]

def test_calendar_listWeekends() :

	from chargedPlanner.chargedPlanner import Calendar

	cal = Calendar()

	l = cal.listWeekEnds(start_date=datetime(2024, 12, 24).date(),
				   end_date=datetime(2024, 12, 31).date())

	assert l == [
		datetime(2024, 12, 28).date(),
		datetime(2024, 12, 29).date()
	]

def test_dev() :

	from chargedPlanner.chargedPlanner import DevGroup

	charles = DevGroup()["Charles"]

	charles.add_holiday(
		datetime(2024,12,27).date(),
		datetime(2025,1,4).date())

	print(charles)

	assert charles.get_workdays(
		datetime(2024, 12, 23).date(),
		datetime(2025, 1, 10).date()) == 7

	assert charles.get_holydays(
		datetime(2024, 12, 23).date(),
		datetime(2025, 1, 10).date()
		) == [
			datetime(2024, 12, 27).date(),
			datetime(2025, 1, 4).date()
		]


def test_feat() :

	test_setup()

	from chargedPlanner.chargedPlanner import DevGroup,Feature

	dev = DevGroup()["Charles"]

	remainingEffort = 5
	purcConnect = 30

	connFeat = Feature(featName="Connectivity",
						totalEffort=7,
						remainingEffort=remainingEffort,
				   		assignee=dev,
						percentageLoad=purcConnect,
					   	startDate= datetime(2024, 12, 27).date())

	seedMapFeat = Feature(featName="SeedMap",
							totalEffort=10,
						  	remainingEffort=10,
				   			assignee=dev,
							percentageLoad=20,
	   						startDate=datetime(2024, 12, 27).date())

	# Try calling the methods with wrong args
	with pytest.raises(ValueError):
		dev.addWorkLoad(12, 80)
	with pytest.raises(ValueError):
		dev.addWorkLoad(connFeat, connFeat)

	# This feature is already assigned
	with pytest.raises(ValueError):
		dev.addWorkLoad(seedMapFeat,20)

	print(dev.getWorkload())

	assert(dev.getWorkloadFor(datetime(2024, 12, 30).date()) == 0.7)

	print("connectivity end : ", connFeat.getEndDate())

	assert( dev.getEndDateForFeat(connFeat) == connFeat.getEndDate() )

	requireChargedDays = int( remainingEffort * 100 / purcConnect)
	endDate = dev.getCalendar().getDate_after_workDays( \
		startDate=datetime(2024, 12, 27).date(),
		requiredWorkDays=requireChargedDays)
	assert( connFeat.getEndDate() == endDate  )

	assert dev.getEndDateForLatestAssignedFeat() == datetime(2025, 3, 6).date()

def test_dev() :

	test_setup()

	from chargedPlanner.chargedPlanner import DevGroup, Feature

	dev = DevGroup()["Daniele"]
	assert dev.__name__ == "Daniele"

	dev.gantt()

def test_dev_gantt() :

	test_setup()

	from chargedPlanner.chargedPlanner import DevGroup, Feature

	dev = DevGroup()["Charles"]

	dev.add_holiday(
		datetime(2025,1,15).date(),
		datetime(2025,1,30).date())

	connFeat = Feature(featName="Connectivity",
				   		totalEffort=5,
				   		remainingEffort=5,
				   		assignee=dev,
					   	percentageLoad=80,
				 		startDate=datetime(2024,12,26).date())

	refactor = Feature(featName="Refactor",
						   totalEffort=10,
						   remainingEffort=10,
				   			assignee=dev,
						  	percentageLoad=20,
							startDate = dev.getEndDateForLatestAssignedFeat())

	seedMapFeat = Feature(featName="SeedMap",
						  totalEffort=12,
						  remainingEffort=10,
				   			assignee=dev,
						  	percentageLoad=20,
							startDate = datetime(2024, 12, 26).date())

	scanv2Feat = Feature(featName="ScanV2",
						 totalEffort=5,
						 remainingEffort=4,
				   			assignee=dev,
						 	percentageLoad=90,
						 	startDate = datetime(2025, 2, 2).date())

	dev.gantt()
	dev.loadChart()

def test_figure() :

	import plotly.figure_factory as ff
	import pandas as pd

	# Sample Data with More Than 10 Tasks
	tasks = [
		{"Task": f"Task {i}", "Start": f"2024-03-{i + 1}", "Finish": f"2024-03-{i + 3}"}
		for i in range(1, 15)
	]

	from chargedPlanner.chargedPlanner import prepare_for_gantt
	[df, color_dict] = prepare_for_gantt(tasks)

	# Create Gantt Chart
	fig = ff.create_gantt(df,
						  colors=color_dict,
						  index_col="Task",
						  show_colorbar=False,
						  group_tasks=True,
						  title="Project Timeline")
	fig.show()

def test_version() :

	test_setup()

	from chargedPlanner.chargedPlanner import DevGroup, Feature, IcoStudioVersion

	version = IcoStudioVersion("1.0.0")

	connFeat = Feature(featName="Connectivity",
					   totalEffort=10,
					   remainingEffort=5,
						startDate=datetime(2024, 12, 26).date())

	seedMapFeat = Feature(featName="SeedMap",
						  totalEffort=10,
						  remainingEffort=10,
					startDate = datetime(2024, 12, 26).date())

	scanv2Feat = Feature(featName="ScanV2",
						 totalEffort=6,
						 remainingEffort=4,
					startDate = datetime(2025, 2, 2).date())

	version.addFeat(connFeat)
	version.addFeat(seedMapFeat)
	version.addFeat(scanv2Feat)

	print(version)

	# Exception thrown : the workload is not defined yet
	with pytest.raises(ValueError):
		version.getEndDate()

	charles = DevGroup()["Charles"]
	selene = DevGroup()["Selene"]

	charles.addWorkLoad(connFeat,40)
	charles.addWorkLoad(scanv2Feat,50)
	selene.addWorkLoad(seedMapFeat,100)

	print("Seedmap end : ",seedMapFeat.getEndDate())

	selene.gantt()
	version.gantt()

	assert(version.getEndDate() == datetime(2025, 2, 12).date())

	from chargedPlanner.chargedPlanner import IcoScanVersion, IcoLabVersion
	version = IcoLabVersion("1.0.0")
	version = IcoScanVersion("1.0.0")

def test_testing_feat() :

	test_setup()

	from chargedPlanner.chargedPlanner import DevGroup, Feature, TestingFeature, DebugFeature, IcoStudioVersion

	version = IcoStudioVersion("1.0.0")

	selene = DevGroup()["Selene"]
	charles = DevGroup()["Charles"]

	connFeat = Feature(featName="Connectivity",
					   totalEffort=6,
					   remainingEffort=5,
						assignee=charles,
					    percentageLoad = 20,
						startDate=datetime(2024, 12, 26).date())

	seedMapFeat = Feature(featName="SeedMap",
						  assignee=selene,
						  totalEffort=11,
						  remainingEffort=10,
						  percentageLoad=40,
						  startDate = datetime(2024, 12, 26).date())

	scanv2Feat = Feature(featName="ScanV2",
						 assignee=charles,
						 totalEffort=6,
						 remainingEffort=4,
						 percentageLoad=30,
						 startDate = datetime(2025, 2, 2).date())

	version.addFeat(connFeat)
	version.addFeat(seedMapFeat)
	version.addFeat(scanv2Feat)

	testingSJ = TestingFeature(
		version=version,
		assignee=selene,
		percentageLoad=5,
		timespan=timedelta(days=15)
	)

	testingCS = TestingFeature(
		version=version,
		assignee=charles,
		percentageLoad=5,
		timespan=timedelta(days=15)
	)

	debugCS = DebugFeature(
		version=version,
		assignee=charles,
		percentageLoad=5,
		timespan=timedelta(days=15)
	)

	# Well, I ask for testing during 15 days and I get back a timedelta of 14 days...
	# certainly not ideal, the issue is that the timeframes are computed via ceils, that
	# round up the actual values. Not a big deal though...
	assert( testingSJ.getEndDate() - testingSJ.getStartDate() == timedelta(days=14) )

	assert( testingSJ.getStartDate() == datetime(2025, 2, 19).date() )
	assert( testingSJ.getEndDate() == datetime(2025, 3, 5).date() )

	version.addFeat(testingSJ)

	assert( testingSJ.getEndDate() == version.getEndDate() )

	print(version)

	version.gantt()


def test_documentation_feat() :

	test_setup()

	from chargedPlanner.chargedPlanner import (DevGroup, Feature,
												   TestingFeature, DocumentationFeature,
												   IcoStudioVersion)

	version = IcoStudioVersion("1.0.0")

	selene = DevGroup()["Selene"]
	charles = DevGroup()["Charles"]
	daniele = DevGroup()["Daniele"]

	connFeat = Feature(featName="Connectivity",
					   totalEffort=10,
					   remainingEffort=5,
						assignee=charles,
					    percentageLoad = 20,
						startDate=datetime(2024, 12, 26).date())

	seedMapFeat = Feature(featName="SeedMap",
						  assignee=selene,
						  totalEffort=10,
						  remainingEffort=10,
						  percentageLoad=40,
						  startDate = datetime(2024, 12, 26).date())

	scanv2Feat = Feature(featName="ScanV2",
						 assignee=charles,
						 totalEffort=5,
						 remainingEffort=4,
						 percentageLoad=30,
						 startDate = datetime(2025, 2, 2).date())

	version.addFeat(connFeat)
	version.addFeat(seedMapFeat)
	version.addFeat(scanv2Feat)

	testing = TestingFeature(
		version=version,
		assignee=selene,
		percentageLoad=5,
		timespan=timedelta(days=15)
	)

	assert( testing.getStartDate() == datetime(2025, 2, 19).date() )
	assert( testing.getEndDate() == datetime(2025, 3, 5).date() )

	version.addFeat(testing)

	assert( testing.getEndDate() == version.getEndDate() )

	documentation = DocumentationFeature(
		version=version,
		assignee=daniele,
		percentageLoad=5,
		timespan=timedelta(days=15)
	)

	assert (documentation.getStartDate() == datetime(2025, 3, 5).date())
	assert (documentation.getEndDate() == datetime(2025, 3, 19).date())

	version.addFeat(documentation)

	assert (documentation.getEndDate() == version.getEndDate())
	assert (testing.getEndDate() != version.getEndDate())

	print(version)

	version.gantt()

def test_project() :

	test_setup()

	from chargedPlanner.chargedPlanner import DevGroup, Feature, IcoStudioVersion, IcoLabVersion, Project, IconeusProduct

	charles = DevGroup()["Charles"]
	selene = DevGroup()["Selene"]

	connFeat = Feature(featName="Connectivity",
					   totalEffort=6,
					   remainingEffort=5,
					   assignee=charles,
					   percentageLoad = 20,
					   startDate=datetime(2024, 12, 26).date())

	seedMapFeat = Feature(featName="SeedMap",
							totalEffort=15,
						  remainingEffort=15,
						  assignee=selene,
						  percentageLoad=20,
						  startDate=datetime(2024, 11, 15).date())

	scanV2Feat = Feature(featName="ScanV2",
						totalEffort=20,
					   	remainingEffort=15,
						 assignee=charles,
						 percentageLoad=40,
						 startDate=datetime(2025, 1, 8).date())

	version1 = IcoStudioVersion("1.0.0")
	version1.addFeat(connFeat)
	version1.addFeat(seedMapFeat)

	with pytest.raises(ValueError):
		charles.addWorkLoad(seedMapFeat,50)

	version2 = IcoStudioVersion("1.1.0")
	version2.addFeat(scanV2Feat)

	icoStudioProject = Project(IconeusProduct.IcoStudio)

	icoStudioProject.addVersion(version1)
	icoStudioProject.addVersion(version2)

	icolabVersion = IcoLabVersion("1.0.0")
	with pytest.raises(ValueError):
		icoStudioProject.addVersion(icolabVersion)

	print(icoStudioProject)

	icoStudioProject.gantt()
	version1.gantt()
	charles.gantt()
	charles.loadChart()
	selene.gantt()
	selene.loadChart()

	charles.removeWorkLoad(scanV2Feat)
	selene.addWorkLoad(scanV2Feat, 30)

	icoStudioProject.gantt()
	version1.gantt()
	charles.gantt()
	charles.loadChart()
	selene.gantt()
	selene.loadChart()

def test_serialise_project() :

	test_setup()

	from chargedPlanner.chargedPlanner import DevGroup, Feature, IcoStudioVersion, Project, IconeusProduct

	charles = DevGroup()['Charles']
	selene = DevGroup()['Selene']

	connFeat = Feature(featName="Connectivity",
					   totalEffort=6,
					   remainingEffort=5,
					   assignee=charles,
					   percentageLoad = 20,
					   startDate=datetime(2024, 12, 26).date())

	seedMapFeat = Feature(featName="SeedMap",
						  totalEffort=20,
						  remainingEffort=15,
						  assignee=selene,
						  percentageLoad=20,
						  startDate=datetime(2024, 11, 15).date())

	scanV2Feat = Feature(featName="ScanV2",
						 totalEffort=15,
						 remainingEffort=15,
						 assignee=charles,
						 percentageLoad=40,
						 startDate=datetime(2025, 1, 8).date())

	version1 = IcoStudioVersion("1.0.0")
	version1.addFeat(connFeat)
	version1.addFeat(seedMapFeat)

	version2 = IcoStudioVersion("1.1.0")
	version2.addFeat(scanV2Feat)

	icoStudioProject = Project(IconeusProduct.IcoStudio)

	icoStudioProject.addVersion(version1)
	icoStudioProject.addVersion(version2)

	print(icoStudioProject)
	icoStudioProject.serialise()

	#Store info before dereferencing the project
	startDate = icoStudioProject.getStartDate()
	endDate = icoStudioProject.getEndDate()

	# The project cannot exist twice. Delete it so that
	# it can be reloaded
	icoStudioProject.__dereference__()

	icoStudioProject_Reloaded = Project.unserialise()

	print(icoStudioProject_Reloaded)

	# Note that the schedule for the two projects is not compared
	# See for instance the .eq. operator of class Dev
	assert(icoStudioProject_Reloaded.getStartDate() == startDate)
	assert(icoStudioProject_Reloaded.getEndDate() == endDate)

	# The == operator does NOT compare the dates and the workload
	# for the devs. Since it is not possible to assign a feature twice to
	# a dev, the first project was de-referenced : thus there are no more
	# features attached to devs in the icoStudioProject
	assert( icoStudioProject == icoStudioProject_Reloaded )

def test_unSerialise_project() :

	test_setup()

	from chargedPlanner.chargedPlanner import DevGroup, Project, IconeusProduct, IcoStudioVersion

	project = Project.unserialise()

	assert  IconeusProduct.IcoStudio == project.__product__

	project.gantt()

	charles = DevGroup()['Charles']

	assert isinstance(charles, DevGroup.Dev)
	assert not isinstance(charles, DevGroup.Manager)

	assert 0.4 == pytest.approx(charles.getWorkload().getWorkloadFor(datetime(2024, 12, 30).date())), "Floats do not match within tolerance"
	assert 0.8 == pytest.approx(charles.getWorkload().getWorkloadFor(datetime(2025, 1, 10).date())), "Floats do not match within tolerance"

	version = project.getVersion("1.0.0")

	assert isinstance(version, IcoStudioVersion)

	assert datetime(2024, 11, 15).date() == version.getStartDate(), "Version Start date mismatch"
	assert datetime(2025, 3, 3).date() == version.getEndDate(), "Version End date mismatch"

	with pytest.raises(ValueError):
		version.getFeature("nonExistingFeature")

	connFeat = version.getFeature("Connectivity")

	assert datetime(2025, 1, 30).date() == connFeat.getEndDate()

	charles.gantt()
