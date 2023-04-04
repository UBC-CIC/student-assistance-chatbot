"""
Generates Lex Bot response by triggering intent handler according to the intent passed.
"""

import logging
import json
import helpers
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, _):
    """
    Lambda function handler. Triggers applicable intent handler and returns Lex bot response.
    :param event: Event body
    :param _: Context (not used)
    :return: Lex bot response
    """
    logger.info('<help_desk_bot>> Lex event info = %s', json.dumps(event))
    
    # Make compatible with Lex V2
    session_state = event.get('sessionState', None)
    
    if session_state is None:
        session_state = {}
        
    session_attributes = session_state.get('sessionAttributes', None)

    if session_attributes is None:
        session_attributes = {}

    logger.debug('<<help_desk_bot> lambda_handler: session_attributes = %s',
                 json.dumps(session_attributes))

    current_intent = session_state.get('intent', None)
    if current_intent is None:
        response_string = 'Sorry, I didn\'t understand. Could you please repeat?'
        return helpers.close(session_attributes, 'Fulfilled',
                             {'contentType': 'CustomPayload', 'content': response_string})
    intent_name = current_intent.get('name', None)
    if intent_name is None:
        response_string = 'Sorry, I didn\'t understand. Could you please repeat?'
        return helpers.close(session_attributes, 'Fulfilled',
                             {'contentType': 'CustomPayload', 'content': response_string})

    # see HANDLERS dict at bottom
    if HANDLERS.get(intent_name, False):
        return HANDLERS[intent_name]['handler'](current_intent, session_attributes, intent_name)
        # dispatch to the event handler
    response_string = "The intent " + intent_name + " is not yet supported."
    return helpers.close(session_attributes, 'Fulfilled',
                         {'contentType': 'CustomPayload', 'content': response_string},
                         intent_name)


def kendra_search_intent_handler(current_intent, session_attributes, intent_name, query_string="",):
    """
    Fallback intent handler. Generates response by querying Kendra index.
    :param current_intent: Request
    :param session_attributes: Session attributes
    :param intent_name: Name of intent
    :param query_string: Used when querying Kendra
    :return: Response string
    """
    session_attributes['fallbackCount'] = '0'

    if session_attributes.get('inputTranscript', None) is not None:
        query_string += session_attributes['inputTranscript']

    logger.debug(
        '<<help_desk_bot>> kendra_search_intent_handler(): calling get_kendra_answer(query="%s")',
        query_string)
        
    answer_text = "I am not certain about the answer to this question, however I have found some potentially relevant information: \n "

    kendra_response = helpers.get_kendra_answer(current_intent['kendraResponse'])
    if kendra_response is None:
        response = "Sorry, I was not able to understand your question. Could you please repeat?"
        return helpers.close(session_attributes,
                             'Fulfilled', {'contentType': 'CustomPayload', 'content': response})
    logger.debug(
        '<<help_desk_bot>> "kendra_search_intent_handler(): kendra_response = %s',
        str(kendra_response))
    return helpers.close(session_attributes, 'Fulfilled',
                         {'contentType': 'PlainText', 'content': answer_text + kendra_response},
                         intent_name)
                         
def get_course_info_intent_handler(current_intent, session_attributes, intent_name):
    #     """
    #     GetCourseInfoIntent handler. Generates response by querying Kendra index.
    #     :param current_intent: Request
    #     :param session_attributes: Session attributes
    #     :param intent_name: Name of intent 
    #     :return: Response string
    #     """
    
    client = boto3.client('kendra')
    
    queryText = (current_intent['slots']['Course']['value']['interpretedValue'])
    
    logger.info(
        '<<help_desk_bot>> "get_course_info_intent_handler(): queryText = %s',
        str(queryText))
    response = client.query(
        IndexId = os.environ['KENDRA_INDEX'],
        QueryText = queryText
    )

    
    logger.info(
        '<<help_desk_bot>> "get_course_info_intent_handler(): response = %s',
        str(response))
        
    opening_text = "For " + queryText + ", we found the following information:\n"
    
    kendra_response = helpers.get_kendra_answer(response, opening_text)
    logger.info(
        '<<help_desk_bot>> "get_course_info_intent_handler(): kendra_response = %s',
        str(kendra_response))
    return helpers.close(session_attributes, 'Fulfilled',
                         {'contentType': 'PlainText', 'content': kendra_response},
                         intent_name)
    
def get_course_by_topic_intent_handler(current_intent, session_attributes, intent_name):
    #     """
    #     GetCourseByTopicIntent intent handler. Generates response by querying Kendra index.
    #     :param current_intent: Request
    #     :param session_attributes: Session attributes
    #     :param intent_name: Name of intent 
    #     :return: Response string
    #     """
    
    client = boto3.client('kendra')
    
    queryText = (current_intent['slots']['CourseTopic']['value']['interpretedValue'])
    
    logger.info(
        '<<help_desk_bot>> "get_course_by_topic_intent_handler(): queryText = %s',
        str(queryText))
    response = client.query(
        IndexId = os.environ['KENDRA_INDEX'],
        QueryText = queryText
    )

    
    logger.info(
        '<<help_desk_bot>> "get_course_info_intent_handler(): response = %s',
        str(response))
        
    opening_text = "For classes about " + queryText + ", we recommend checking out the following:\n"
    
    kendra_response = helpers.get_kendra_multiple_answers(response, 3, opening_text)
    logger.info(
        '<<help_desk_bot>> "get_course_info_intent_handler(): kendra_response = %s',
        str(kendra_response))
    return helpers.close(session_attributes, 'Fulfilled',
                         {'contentType': 'PlainText', 'content': kendra_response},
                         intent_name)

def get_course_by_prof_intent_handler(current_intent, session_attributes, intent_name):
    #     """
    #     GetCourseByProfIntent handler. Generates response by querying Kendra index.
    #     :param current_intent: Request
    #     :param session_attributes: Session attributes
    #     :param intent_name: Name of intent 
    #     :return: Response string
    #     """
    
    client = boto3.client('kendra')
    
    queryText = (current_intent['slots']['ProfFirstName']['value']['interpretedValue'] + " " + current_intent['slots']['ProfLastName']['value']['interpretedValue'])
    
    logger.info(
        '<<help_desk_bot>> "get_course_by_prof_intent_handler(): queryText = %s',
        str(queryText))
    response = client.query(
        IndexId = os.environ['KENDRA_INDEX'],
        QueryText = queryText
    )

    answer_text = "We have found the following classes taught by " + queryText + ":\n"
    
    logger.info(
        '<<help_desk_bot>> "get_course_by_prof_intent_handler(): response = %s',
        str(response))
    kendra_response = helpers.get_kendra_multiple_answers(response, 3, answer_text)
    logger.info(
        '<<help_desk_bot>> "get_course_by_prof_intent_handler(): kendra_response = %s',
        str(kendra_response))
    return helpers.close(session_attributes, 'Fulfilled',
                         {'contentType': 'PlainText', 'content': kendra_response},
                         intent_name)
                         
def get_course_eligibility_intent(current_intent, session_attributes, intent_name):
    #     """
    #     GetCourseEligibilityIntent handler. Generates response by querying Kendra index.
    #     :param intent_request: Request
    #     :param session_attributes: Session attributes
    #     :param intent_name: Name of intent 
    #     :return: Response string
    #     """
    
    client = boto3.client('kendra')
    
    queryText = current_intent['slots']['Course']['value']['interpretedValue'].replace(" ", "")
    
    logger.info(
        '<<help_desk_bot>> "get_course_eligibility_intent(): queryText = %s',
        str(queryText))
    response = client.query(
        IndexId = os.environ['KENDRA_INDEX'],
        QueryText = queryText
    )
    
    logger.info(
        '<<help_desk_bot>> "get_course_eligibility_intent(): response = %s',
        str(response))
        
    answer_text = ""
    
    answer_text += "Are there any general seats available? If not are there any restricted seats available for students studying " +current_intent['slots']['Major']['value']['interpretedValue']+"?\n\n" 
    answer_text += "Will registering in this course bring you above your allowed credit limit? Your credit limit is dependant on program and year level. This can be found on your faculty website \n\n" 
        
    prereqs = helpers.get_field_from_kendra_document(response, "prereq")
    coreqs = helpers.get_field_from_kendra_document(response, "coreq")

    if prereqs != "":
        answer_text += queryText + " has the following " + prereqs + "\n"
    if coreqs != "":
        answer_text += queryText + " has the following " + prereqs + "\n"
    
    answer_text += "\n"
        
    
    answer_text += "If all the above is satisfied and are still unable to register within the class, please reach out to academic advising: \n" 
    answer_text += "https://students.ubc.ca/enrolment/academic-learning-resources/academic-advising"
    # kendra_response = helpers.get_kendra_answer(response, answer_text)
    
    return helpers.close(session_attributes, 'Fulfilled',
                         {'contentType': 'PlainText', 'content': answer_text},
                         intent_name)    
                         
def get_credit_limit_intent(current_intent, session_attributes, intent_name):
    #     """
    #     GetCreditLimitIntent handler. Generates response by querying Kendra index.
    #     :param current_intent: Request
    #     :param session_attributes: Session attributes
    #     :param intent_name: Name of intent 
    #     :return: Response string
    #     """
    
    faculty = current_intent['slots']['Faculty']['value']['interpretedValue']
    
    logger.info(
        '<<help_desk_bot>> "get_credit_limit_intent(): faculty = %s',
        str(faculty))
    
    answer_text = "For the faculty of " + faculty + ", here is a link to credit limit information: \n"
    
    if faculty == "APSC":
        answer_text += "https://academicservices.engineering.ubc.ca/registration/registration-requests/#"
    elif faculty == "ARTS":
        answer_text += "https://www.arts.ubc.ca/degree-planning/course-registration/credit-limits-increases/#:~:text=As%20an%20Arts%20student%2C%20you,summer%20credits%20are%20not%20required)."
    elif faculty == "COMM":
        answer_text += "https://mybcom.sauder.ubc.ca/ugo/faqs#"
    elif faculty == "FRST":
        answer_text += "https://forestry.ubc.ca/students/undergraduate-student-portal/undergraduate-student-services/academic-regulations/#:~:text=Course%20Load%20Requirements&text=All%20students%20are%20restricted%20to,see%20Chiara%20Longhi%2C%20FSC%202613."
    elif faculty == "KIN":
        answer_text += "https://kin.educ.ubc.ca/undergraduate/bkin/degree-requirements/#:~:text=Under%20normal%20circumstances%20students%20must,from%20the%20established%20credit%20limits."
    elif faculty == "LFS":
        answer_text += "https://www.landfood.ubc.ca/undergraduate/courses-degree-planning/lfs-faqs/#:~:text=All%20students%20are%20allowed%20to,please%20contact%20LFS%20Student%20Services."
    elif faculty == "SCIE":
        answer_text += "https://www.calendar.ubc.ca/vancouver/index.cfm?tree=12,215,410,1456"
    else: 
        answer_text = "Contact academic advising for your credit limit: https://students.ubc.ca/enrolment/academic-learning-resources/academic-advising"
    
    return helpers.close(session_attributes, 'Fulfilled',
                         {'contentType': 'PlainText', 'content': answer_text},
                         intent_name)
                         
def get_course_prerequisites_intent(current_intent, session_attributes, intent_name):
    #     """
    #     GetCoursePrereqsIntent handler. Generates response by querying Kendra index.
    #     :param intent_request: Request
    #     :param session_attributes: Session attributes
    #     :param intent_name: Name of intent 
    #     :return: Response string
    #     """
    
    client = boto3.client('kendra')
    
    queryText = current_intent['slots']['Course']['value']['interpretedValue'].replace(" ", "")
    
    logger.info(
        '<<help_desk_bot>> "get_course_eligibility_intent(): queryText = %s',
        str(queryText))
    response = client.query(
        IndexId = os.environ['KENDRA_INDEX'],
        QueryText = queryText
    )
    
    logger.info(
        '<<help_desk_bot>> "get_course_prerequisites_intent(): response = %s',
        str(response))
        
    prereqs = helpers.get_field_from_kendra_document(response, "prereq")
    coreqs = helpers.get_field_from_kendra_document(response, "coreq")
    
    answer_text = ""
    kendra_text = ""

    if prereqs != "":
        answer_text += queryText.upper() + " has the following " + prereqs + "\n"
    if coreqs != "":
        answer_text += queryText.upper() + " has the following " + coreqs + "\n"
        
    if prereqs == "" and coreqs == "":
        answer_text += queryText.upper() + "has no prerequisites or corequisiites. \n"
    

    kendra_response = helpers.get_kendra_answer(response, answer_text)
    
    return helpers.close(session_attributes, 'Fulfilled',
                         {'contentType': 'PlainText', 'content': kendra_response},
                         intent_name) 
                         
def get_credit_d_fail_intent(current_intent, session_attributes, intent_name):
    #     """
    #     GetCreditDFailIntent handler. Generates response by querying Kendra index.
    #     :param intent_request: Request
    #     :param session_attributes: Session attributes
    #     :param intent_name: Name of intent 
    #     :return: Response string
    #     """
    
    client = boto3.client('kendra')
    
    queryText = (current_intent['slots']['Course']['value']['interpretedValue'])
    
    answer_text = "For general Credit/D/Fail information: https://students.ubc.ca/enrolment/courses/creditdfail-grading\n"
    
    logger.info(
        '<<help_desk_bot>> "get_credit_d_fail_intent(): queryText = %s',
        str(queryText))
    response = client.query(
        IndexId = os.environ['KENDRA_INDEX'],
        QueryText = queryText
    )

    
    logger.info(
        '<<help_desk_bot>> "get_credit_d_fail_intent(): response = %s',
        str(response))
    kendra_response_URL = helpers.get_field_from_kendra_document(response, "ubcURI")
    logger.info(
        '<<help_desk_bot>> "get_credit_d_fail_intent(): kendra_response = %s',
        str(kendra_response))
    answer_text += "For " + queryText + " Credit/D/Fail information: " + kendra_response_URL
    return helpers.close(session_attributes, 'Fulfilled',
                         {'contentType': 'PlainText', 'content': answer_text},
                         intent_name)


HANDLERS = {
    'KendraSearchIntent': {'handler': kendra_search_intent_handler},
    'GetCourseInfoIntent': {'handler': get_course_info_intent_handler},
    'GetCourseByTopicIntent': {'handler': get_course_by_topic_intent_handler},
    'GetCourseByProfIntent': {'handler' : get_course_by_prof_intent_handler},
    "GetCourseEligibilityIntent": {'handler' : get_course_eligibility_intent},
    "GetCreditLimitIntent": {'handler' : get_credit_limit_intent},
    "GetCoursePrerequisitesIntent": {"handler": get_course_prerequisites_intent},
    "GetCrDFailIntent": {'handler': get_credit_d_fail_intent}
}