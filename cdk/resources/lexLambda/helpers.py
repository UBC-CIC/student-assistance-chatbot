"""
Helper function for Lex bot
"""
import logging
import json
import pprint
import os
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
import config as help_desk_config

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_slot_values(slot_values, intent_request):
    """
    Get slot values for each slot.
    :param slot_values: Slot values
    :param intent_request: Requested Intent
    :return: Slot values
    """
    if slot_values is None:
        slot_values = {key: None for key in help_desk_config.SLOT_CONFIG}

    slots = intent_request['intent']['slots']

    for key, config in help_desk_config.SLOT_CONFIG.items():
        slot_values[key] = slots.get(key)
        logger.debug('<<help_desk_bot>> retrieving slot value for %s = %s', key, slot_values[key])
        if slot_values[key]:
            if config.get(
                    'type', help_desk_config.ORIGINAL_VALUE) == help_desk_config.TOP_RESOLUTION:
                # get the resolved slot name of what the user said/typed
                if len(intent_request['intent']['slotDetails'][key]['resolutions']) > 0:
                    slot_values[key] = intent_request['currentIntent'][
                        'slotDetails'][key]['resolutions'][0]['value']
                else:
                    error_msg = help_desk_config.SLOT_CONFIG[key].get(
                        'error', 'Sorry, I don\'t understand "{}".')
                    raise help_desk_config.SlotError(error_msg.format(slots.get(key)))

    return slot_values


def get_remembered_slot_values(slot_values, session_attributes):
    """
    Get remembered slot values.
    :param slot_values: Slot values
    :param session_attributes: Session attributes
    :return: Remembered slot values
    """
    logger.debug(
        '<<help_desk_bot>> get_remembered_slot_values() - session_attributes: %s',
        session_attributes)

    remembered_slots = session_attributes.get('rememberedSlots')
    if remembered_slots is not None:
        remembered_slot_values = json.loads(remembered_slots)
    else:
        remembered_slot_values = {key: None for key in help_desk_config.SLOT_CONFIG}

    if slot_values is None:
        slot_values = {key: None for key in help_desk_config.SLOT_CONFIG}

    for key, config in help_desk_config.SLOT_CONFIG.items():
        if config.get('remember', False):
            logger.debug('<<help_desk_bot>> get_remembered_slot_values() - slot_values[%s] = %s',
                         key,
                         slot_values.get(key))
            logger.debug(
                '<<help_desk_bot>> get_remembered_slot_values() - remembered_slot_values[%s] = %s',
                key,
                remembered_slot_values.get(key))
            if slot_values.get(key) is None:
                slot_values[key] = remembered_slot_values.get(key)

    return slot_values


def remember_slot_values(slot_values, session_attributes):
    """
    Remember a slot value.
    :param slot_values: Slot values
    :param session_attributes: Session attributes
    :return: Updated slot values
    """
    if slot_values is None:
        slot_values = {key: None for key, config in help_desk_config.SLOT_CONFIG.items() if
                       config['remember']}
    session_attributes['rememberedSlots'] = json.dumps(slot_values)
    logger.debug('<<help_desk_bot>> Storing updated slot values: %s', slot_values)
    return slot_values


def get_latest_slot_values(intent_request, session_attributes):
    """
    Get latest slot values.
    :param intent_request: Requested Intent
    :param session_attributes: Session attributes
    :return: Latest slot values
    """
    slot_values = session_attributes.get('slot_values')

    try:
        slot_values = get_slot_values(slot_values, intent_request)
    except help_desk_config.SlotError as err:
        raise help_desk_config.SlotError(err)

    logger.debug('<<help_desk_bot>> "get_latest_slot_values(): slot_values: %s', slot_values)

    slot_values = get_remembered_slot_values(slot_values, session_attributes)
    debug_message = '<<help_desk_bot>> "get_latest_slot_values(): slot_values ' + \
                    'after get_remembered_slot_values: %s'
    logger.debug(debug_message, slot_values)

    remember_slot_values(slot_values, session_attributes)

    return slot_values


def close(session_attributes, fulfillment_state, message, intent_name="KendraSearchIntent"):
    """
    Get final response.
    :param session_attributes: Session attributes
    :param fulfillment_state: Fulfillment state
    :param message: Message
    :return: response to be returned by Lex chat bot
    """
    response = {
        "sessionState": {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close',
            },
            'intent': {
                'name': intent_name,
                'state': fulfillment_state,
            }
        },
        "messages": [
            message
         ]
    }

    logger.info(
        '<<help_desk_bot>> "Lambda fulfillment function response = %s', pprint.pformat(response,
                                                                                       indent=4))

    return response


def increment_counter(session_attributes, counter):
    """
    Increment counter value in session attribute.
    :param session_attributes: Session attributes
    :param counter: Key in session attribute
    :return: Updated count
    """
    counter_value = session_attributes.get(counter, '0')

    if counter_value:
        count = int(counter_value) + 1
    else:
        count = 1

    session_attributes[counter] = count

    return count


def create_presigned_url(bucket_name, object_name, expiration=604800):
    """
    Generate a presigned URL for S3 object.
    :param bucket_name: S3 Bucket name
    :param object_name: S3 object name
    :param expiration: Time after which link will expire
    :return: Signed URL
    """
    s3_client = boto3.client('s3', os.environ['AWS_REGION'],
                             config=Config(signature_version='s3v4'))
    try:
        response_s3 = s3_client.generate_presigned_url('get_object',
                                                       Params={'Bucket': bucket_name,
                                                               'Key': object_name},
                                                       ExpiresIn=expiration)
    except ClientError as client_error:
        logger.error(client_error)
        return None
    return response_s3


def question_result_type(response, i):
    """
    Generate the answer text for question result type.
    :param response: Kendra query response
    :return: Answer text
    """
    try:
        faq_answer_text += '\"' + response['resultItems'][i]['documentExcerpt']['text'] + '\"'
    except KeyError:
        faq_answer_text = "Sorry, I could not find an answer in our FAQs."

    return faq_answer_text


def answer_result_type(response, i):
    """
    Generate the answer text from the document, plus the URL link to the document.
    :param response: Kendra query response
    :return: Answer text
    """
    try:
        document_title = response['ResultItems'][i]['DocumentTitle']['Text']
        document_id = response['ResultItems'][i]['DocumentId']
        document_text = response['ResultItems'][i]['AdditionalAttributes'][0][
            'Value']['TextWithHighlightsValue']['Text']
        pos = document_id.rindex("/")
        document_key = document_id[(pos + 1):]
        logger.info(document_key)
        document_url = get_field_from_kendra_document(response, "ubcURI")
        
        if response['ResultItems'][i]['AdditionalAttributes'][0][
                'Value']['TextWithHighlightsValue']['Highlights'][0]['TopAnswer']:
            begin = int(response['ResultItems'][i]['AdditionalAttributes'][0][
                'Value']['TextWithHighlightsValue']['Highlights'][0]['BeginOffset'])
            end = int(response['ResultItems'][i]['AdditionalAttributes'][0][
                'Value']['TextWithHighlightsValue']['Highlights'][0]['EndOffset'])
            topanswer = response['ResultItems'][i]['AdditionalAttributes'][0][
                'Value']['TextWithHighlightsValue']['Text']
            answer_text = "On searching the Enterprise repository, I have found" \
                          " the following answer as a top answer--"
            answer_text += "\nDocument Title: " + document_title
            # + " --- Excerpt: " + document_excerpt_text + ">"
            answer_text += '-- \"' + topanswer[begin:end] + '\"'
            answer_text += "\nReference: " + document_url + "\n"
        else:
            answer_text += "\n\n -- " + document_title + "\n --- \"" + document_text + "\""
            answer_text += "\n\n Reference: " + document_url + "\n"
    except KeyError:
        answer_text = "\"Sorry, I could not find the answer in our documents.\""

    return answer_text
    
def answer_result_type_fallback(response, i):
    """
    Generate the answer text from the document, plus the URL link to the document.
    :param response: Kendra query response
    :return: Answer text
    """
    try:
        document_title = response['resultItems'][i]['documentTitle']['text']
        document_id = response['resultItems'][i]['documentId']
        document_text = response['resultItems'][i]['additionalAttributes'][0][
            'value']['textWithHighlightsValue']['text']
        pos = document_id.rindex("/")
        document_key = document_id[(pos + 1):]
        logger.info(document_key)
        document_url = get_field_from_kendra_document_fallback(response, "ubcURI")
        
        if response['resultItems'][i]['additionalAttributes'][0][
                'value']['textWithHighlightsValue']['highlights'][0]['topAnswer']:
            begin = int(response['resultItems'][i]['additionalAttributes'][0][
                'value']['textWithHighlightsValue']['highlights'][0]['beginOffset'])
            end = int(response['ResultItems'][i]['AdditionalAttributes'][0][
                'value']['textWithHighlightsValue']['highlights'][0]['endOffset'])
            topanswer = response['resultItems'][i]['additionalAttributes'][0][
                'value']['textWithHighlightsValue']['text']
            answer_text = "On searching the Enterprise repository, I have found" \
                          " the following answer as a top answer--"
            answer_text += "\nDocument Title: " + document_title
            # + " --- Excerpt: " + document_excerpt_text + ">"
            answer_text += '-- \"' + topanswer[begin:end] + '\"'
            answer_text += "\nReference: " + document_url + "\n"
        else:
            answer_text += "\n\n -- " + document_title + "\n --- \"" + document_text + "\""
            answer_text += "\n\n Reference: " + document_url + "\n"
    except KeyError:
        answer_text = "\"Sorry, I could not find the answer in our documents.\""

    return answer_text

def document_result_type(response, i, document_list=""):
    """
    Assemble the list of document links.
    :param response: Kendra query response
    :return: Answer text
    """
        
    document_id = response['ResultItems'][i]['DocumentId']
    pos = document_id.rindex("/")
    
    logger.info(
        '<<help_desk_bot>> "helper.document_result_type(): document_id = %s',
        str(document_id))
        
    document_key = document_id[(pos + 1):]
    logger.info(document_key)

    url = get_field_from_kendra_document(response, "ubcURI")

    logger.info(url)
    document_list += '\n' + response['ResultItems'][i]['DocumentTitle']['Text'] + ' - '
    document_list += '\"' + response['ResultItems'][i]['DocumentExcerpt']['Text'] + '\"'
    document_list += '\nReference: ' + url + '\n'
    return document_list

def document_result_type_fallback(response, i, document_list=""):
    """
    Assemble the list of document links.
    :param response: Kendra query response
    :return: Answer text
    """
        
    document_id = response['resultItems'][i]['documentId']
    pos = document_id.rindex("/")
    
    logger.info(
        '<<help_desk_bot>> "helper.document_result_type(): document_id = %s',
        str(document_id))
        
    document_key = document_id[(pos + 1):]
    logger.info(document_key)

    url = get_field_from_kendra_document_fallback(response, "ubcURI")

    logger.info(url)
    document_list += '\n' + response['resultItems'][i]['documentTitle']['text'] + ' - '
    document_list += '\"' + response['resultItems'][i]['documentExcerpt']['text'] + '\"'
    document_list += '\nReference: ' + url + '\n'
    return document_list

def get_kendra_answer(intent_request, document_list=""):
    """
    Get answer from the JSON response returned by the Kendra Index
    :param question: Question string
    :return: Answer returned from Kendra
    """
    
    logger.info(
        '<<help_desk_bot>> "helper.get_kendra_answer() %s', str(intent_request))
        
    try:
        if "resultItems" in intent_request:
            logger.info('<<help_desk_bot> get_kendra_answer: resultitems = %s',
                     json.dumps(intent_request['resultItems']))
            first_result_type = intent_request['resultItems'][0]['type']
        else:
            logger.info('<<help_desk_bot> get_kendra_answer: resultitems = %s',
                     json.dumps(intent_request['ResultItems']))
            first_result_type = intent_request['ResultItems'][0]['Type']
    except KeyError:
        logger.info(
            '<<help_desk_bot>> "helper.get_kendra_answer() had KeyError: %s', str(KeyError))
        return None
    except (IndexError, TypeError):
        error_txt = 'Sorry, we do not have the answer currently. Please try again later!'
        logger.error(error_txt)
        return error_txt

    answer_text = None
    
    logger.info(
        '<<help_desk_bot>> "helper.get_kendra_answer(): result_type = %s',
        str(first_result_type))

    if first_result_type == 'QUESTION_ANSWER':
         answer_text = question_result_type(intent_request, 0)
    elif first_result_type == 'ANSWER':
        if "resultItems" in intent_request:
            answer_text = answer_result_type_fallback(intent_request, 0, document_list)
        else:
            answer_text = answer_result_type(intent_request, 0, document_list)

    elif first_result_type == 'DOCUMENT':
        if "resultItems" in intent_request:
            answer_text = document_result_type_fallback(intent_request, 0, document_list)
        else:
            answer_text = document_result_type(intent_request, 0, document_list)
    return answer_text

def get_kendra_multiple_answers(intent_request, number_answers, answer_text=""):
    """
    Get a list of answers from the JSON response returned by the Kendra Index
    :param question: Question string
    :return: Answers returned from Kendra
    """
    
    logger.info(
        '<<help_desk_bot>> "helper.get_kendra_multiply_answers() beginning')
        
    try:
        if "resultItems" in intent_request:
            logger.info('<<help_desk_bot> get_kendra_multiple_answers: resultitems = %s',
                     json.dumps(intent_request['resultItems']))
            result_list = intent_request['resultItems']
        else:
            logger.info('<<help_desk_bot> get_kendra_multiple_answers: resultitems = %s',
                     json.dumps(intent_request['ResultItems']))
            result_list = intent_request['ResultItems']
    except KeyError:
        logger.info(
            '<<help_desk_bot>> "helper.get_kendra_multiple_answers() had KeyError: %s', KeyError)
        return None
    except (IndexError, TypeError):
        error_txt = 'Sorry, we do not have the answer currently. Please try again later!'
        logger.error(error_txt)
        return error_txt

    logger.info(
        '<<help_desk_bot>> "helper.get_kendra_multiple_answers(): result_list = %s',
        result_list)
        
    i = 0
    added = 0
    while i < len(result_list) and added < number_answers:
        if "resultItems" in intent_request:
            result_type = result_list[i]['type']
        else:
            result_type = result_list[i]['Type']
        
        logger.info(
            '<<help_desk_bot>> "helper.get_kendra_multiple_answers(): result_type = %s',
            str(result_type))
        if result_type == 'DOCUMENT':
            if "resultItems" in intent_request:
                answer_text += document_result_type_fallback(intent_request, i, "")
            else:
                answer_text += document_result_type(intent_request, i, "")

            answer_text += '\n\n'
            added += 1
        i += 1

    return answer_text

def get_field_from_kendra_document(kendra_response, field):
    
    for attribute in kendra_response["ResultItems"][0]["DocumentAttributes"]:
        if attribute['Key'] == field:
            return attribute["Value"]["StringValue"]
    
    return ""
    
def get_field_from_kendra_document_fallback(kendra_response, field):
    
    for attribute in kendra_response["resultItems"][0]["documentAttributes"]:
        if attribute['key'] == field:
            return attribute["value"]["stringValue"]
    
    return ""