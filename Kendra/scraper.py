from selenium import webdriver
import undetected_chromedriver.v2 as uc
from selenium.webdriver.common.by import By
op = webdriver.ChromeOptions()
from selenium.webdriver.chrome.options import Options
import re
import os
import json

URL = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea"
SELECTOR = ".table.table-striped > tbody > tr > td > a"
BASE_DIRECTORY = "./classes/"
METADATA_DIRECTORY = "./metadata/"
REGEX = "^.*dept=([^&]*)&course=([^&]*)&section=([^&]*)"

chrome_options = Options()
chrome_options.add_argument("--headless")
driver = uc.Chrome(options=chrome_options)

indexName = "ubc-scraped-courses"

CREDIT_REGEX = "Credits: (.*)"
MODE_OF_DELIVERY_REGEX = "Mode of Delivery: (.*)"
REQUIRES_IN_PERSON_ATTENDANCE_REGEX = "Requires In-Person Attendance: (.*)"
DATE_BUILDING_REGEX = "((?:1|2) (?:Mon|Tue|Wed|Thu|Fri|Sat|Sun).*)"
INSTRUCTOR_REGEX = "Instructor: (.*)"

class DateBuilding():
    def __init__(self,term,days,startTime,endTime,building,room):
        self.term = term
        self.days = days
        self.startTime = startTime
        self.endTime = endTime
        self.building = building
        self.room = room
    def __str__(self):
        return self.__dict__


class Course():
    def __init__(self, credit, mode_of_delivery, requires_in_person_attendance, date_buildings, instructor):
        self.credit = credit
        self.mode_of_delivery = mode_of_delivery
        self.requires_in_person_attendance = requires_in_person_attendance
        self.date_buildings = date_buildings
        self.instructor = instructor
    def __str__(self):
        return self.__dict__
def formatDateBuildings(date_buildings):
    msg = ""
    for date_building in date_buildings:
        if date_building.term:
            msg += "Term: " + date_building.term 
        if date_building.days:
            msg += ", Days: " + ' '.join(date_building.days)
        if date_building.startTime:
            msg += ", Start Time: " + date_building.startTime
        if date_building.endTime:
            msg += ", End Time: " + date_building.endTime
        if date_building.building:
            msg += ", Building: " + date_building.building
        if date_building.room:
            msg += ", Room: " + date_building.room
        msg += "\n"
    return msg
def formatText(course, dept, course_num, section):
    msg = ""
    if dept:
        msg += "Department: " + dept + "\n"
    if course_num:
        msg += "Course Number: " + course_num + "\n"
    if section:
        msg += "Section: " + section + "\n"
    if course.credit:
        msg += "Credits: " + course.credit + "\n"
    if course.mode_of_delivery:
        msg += "Mode of Delivery: " + course.mode_of_delivery + "\n"
    if course.requires_in_person_attendance:
        msg += "Requires in Person Attendance: " + course.requires_in_person_attendance + "\n"
    if course.date_buildings:
        msg += formatDateBuildings(course.date_buildings)
    if course.instructor:
        msg += "Instructor: " + course.instructor + "\n"
    return msg

def parseDateBuilding(date_building):
    if date_building is None:
        return None, None, None, None, None, None
    splitted = date_building.split(" ")
    term, startTime, endTime, building, room = None, None, None, None, None
    days = []
    i = 0
    termBool, daysBool, startTimeBool, endTimeBool, buildingBool, roomBool = True, True, True, True, True, True

    while i < len(splitted):
        if termBool:
            term = splitted[i]
            termBool = False
        elif daysBool: 
            if splitted[i] in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]:
                days.append(splitted[i])
            else:
                daysBool = False
                i -= 1
        elif startTimeBool:
            startTime = splitted[i]
            startTimeBool = False
        elif endTimeBool:
            endTime = splitted[i]
            endTimeBool = False
        elif buildingBool:
            building = splitted[i]
            buildingBool = False
        elif roomBool:
            room = splitted[i]
            roomBool = False
        i += 1
    return DateBuilding(term, days, startTime, endTime, building, room)

def parse(courseMain):
    credit = None if not re.search(CREDIT_REGEX,courseMain) else re.search(CREDIT_REGEX,courseMain).groups()[0]
    mode_of_delivery = None if not re.search(MODE_OF_DELIVERY_REGEX,courseMain) else re.search(MODE_OF_DELIVERY_REGEX,courseMain).groups()[0]
    requires_in_person_attendance = None if not re.search(REQUIRES_IN_PERSON_ATTENDANCE_REGEX,courseMain) else re.search(REQUIRES_IN_PERSON_ATTENDANCE_REGEX,courseMain).groups()[0]
    date_buildings = None if not re.search(DATE_BUILDING_REGEX,courseMain) else re.search(DATE_BUILDING_REGEX,courseMain).groups()
    date_buildings_arr = []
    if date_buildings:
        for elem in date_buildings:
            date_buildings_arr.append(parseDateBuilding(elem))
    instructor = None if not re.search(INSTRUCTOR_REGEX,courseMain) else re.search(INSTRUCTOR_REGEX,courseMain).groups()[0]
    return Course(credit, mode_of_delivery, requires_in_person_attendance, date_buildings_arr, instructor)

def generateMetadata(department,courseNumber, sourceURI):
    metadata = {
        "DocumentId": "s3://"+indexName+"/"+department+"/"+courseNumber + ".txt",
        "Attributes": {
            "_category": department,
            "courseNumber": courseNumber,
            "ubcURI": sourceURI, 
        },
        "Title": department + courseNumber,
        # "ContentType": "txt"
    }
    json_object = json.dumps(metadata)
    return json_object


def scrape(url,parentUrl):
    driver.get(url)
    subjBox = driver.find_elements(By.CSS_SELECTOR, SELECTOR)
    urls = []
    for subj in subjBox:
        innerUrl = subj.get_attribute("href")
        if "https://ssc.adm.ubc.ca/" not in innerUrl:
            urls.append(innerUrl)
            
    if len(urls) != 0:
        for innerUrl in urls:
            scrape(innerUrl,url)
    else:
        try:
            courseMain = driver.find_element(By.XPATH, "//*[@role='main']").text.replace("Save To Worklist","")
            result = re.search(REGEX,driver.current_url)
            department = result.groups()[0]
            courseNumber = result.groups()[1]
            section = result.groups()[2]
            formatted = formatText(parse(courseMain),department, courseNumber, section)
            directory = BASE_DIRECTORY + department + "/"
            filename = courseNumber + ".txt"
            os.makedirs(os.path.dirname(directory),exist_ok=True)
            with open(directory + filename, "a+", encoding="utf-8") as f:
                f.write(formatted + "\n")
            json_object = generateMetadata(department,courseNumber,parentUrl)
            #metadataDirectory = METADATA_DIRECTORY + department + "/"
            #os.makedirs(os.path.dirname(metadataDirectory),exist_ok=True)
            with open(directory + filename + ".metadata.json", "w") as m:
                m.write(json_object)
        except:
            pass
    
scrape(URL,None)

# Files below only used to help to clean up json files

def find_json_files(directory):
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return json_files

def remove_contentType(json_files):
    for file in json_files:
        with open(file, 'r') as json_file:
            json_data = json.load(json_file)
            if 'ContentType' in json_data:
                del json_data['ContentType']
                with open(file, 'w') as json_file:
                    json.dump(json_data, json_file)

# json_files = find_json_files("./classes")
# remove_contentType(json_files)