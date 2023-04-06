from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

import re
import json
import boto3
from botocore.exceptions import ClientError

PREREQ_SELECTOR = "//*[contains(text(),'Pre-req')]"
COREQ_SELECTOR = "//*[contains(text(),'Co-req')]"
SELECTOR = ".table.table-striped > tbody > tr > td > a"
METADATA_DIRECTORY = "./metadata/"
REGEX = "^.*dept=([^&]*)&course=([^&]*)&section=([^&]*)"

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
    def __init__(self, credit, description, mode_of_delivery, requires_in_person_attendance, date_buildings, instructor):
        self.credit = credit
        self.description = description
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
def formatText(course, prereq, coreq, dept, course_num, section):
    msg = ""
    if dept:
        msg += "Department: " + dept + "\n"
    if course_num:
        msg += "Course Number: " + course_num + "\n"
    if section:
        msg += "Section: " + section + "\n"
    if course.description:
        msg += "Description: " + course.description + "\n"
    if prereq:
        msg += prereq + "\n"
    if coreq:
        msg += coreq + "\n"
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
    description = courseMain.split("\n")[3]
    if "Credit" in description:
        description = None
    date_buildings = None if not re.search(DATE_BUILDING_REGEX,courseMain) else re.search(DATE_BUILDING_REGEX,courseMain).groups()
    date_buildings_arr = []
    if date_buildings:
        for elem in date_buildings:
            date_buildings_arr.append(parseDateBuilding(elem))
    instructor = None if not re.search(INSTRUCTOR_REGEX,courseMain) else re.search(INSTRUCTOR_REGEX,courseMain).groups()[0]
    return Course(credit, description, mode_of_delivery, requires_in_person_attendance, date_buildings_arr, instructor)

def generateMetadata(department,courseNumber, sourceURI):
    indexName = "ubc-scraped-courses"
    metadata = {
        "DocumentId": "s3://"+indexName+"/"+department+"/"+courseNumber + ".txt",
        "Attributes": {
            "_category": department,
            "courseNumber": courseNumber,
            "ubcURI": sourceURI, 
        },
        "Title": department + courseNumber,
    }
    json_object = json.dumps(metadata)
    return json_object


def scrape(url,parentUrl,prereq,coreq,bucketName,driver,s3):
    driver.get(url)
    subjBox = driver.find_elements(By.CSS_SELECTOR, SELECTOR)
    if not prereq:
        try:
            prereqBox = driver.find_element(By.XPATH,PREREQ_SELECTOR)
            prereq = prereqBox.text
        except:
            pass
    if not coreq:
        try:
            coreqBox = driver.find_element(By.XPATH,COREQ_SELECTOR)
            coreq = coreqBox.text
        except:
            pass        
    urls = []
    for subj in subjBox:
        innerUrl = subj.get_attribute("href")
        if "https://ssc.adm.ubc.ca/" not in innerUrl:
            urls.append(innerUrl)
            
    if len(urls) != 0:
        for innerUrl in urls:
            scrape(innerUrl,url,prereq,coreq,bucketName,driver,s3)
    else:
        
        courseMain = driver.find_element(By.XPATH, "//*[@role='main']").text.replace("Save To Worklist","")
        result = re.search(REGEX,driver.current_url)
        department = result.groups()[0]
        courseNumber = result.groups()[1]
        section = result.groups()[2]
        formatted = formatText(parse(courseMain),prereq,coreq,department, courseNumber, section)
        directory = department + "/"
        filename = courseNumber + ".txt"

        # Write data to file-like object
        file_data = formatted.encode('utf-8')

        # Upload file to S3
        try:
            s3.put_object(Bucket=bucketName, Key=directory+filename, Body=file_data)
            print(f"File uploaded to s3://{bucketName}/{directory+filename}")
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
        json_object = generateMetadata(department,courseNumber,parentUrl)
        # Write data to file-like object
        metadata_data = json_object.encode('utf-8')
        # Upload file to S3
        try:
            s3.put_object(Bucket=bucketName, Key=directory + filename + ".metadata.json", Body=metadata_data)
            print(f"File uploaded to s3://{bucketName}/{directory+filename}")
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")



def beginScraper(bucket_name,profile_name):
    
    URL = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea"
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options,executable_path=GeckoDriverManager().install())
    session = boto3.Session(profile_name=profile_name)
    s3 = session.client('s3')
    scrape(URL,None,None,None,bucket_name,driver,s3)
