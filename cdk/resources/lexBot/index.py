import boto3
import time
import logging
import os
from botocore.config import Config
import urllib3

region = os.environ["AWS_REGION"]

logger = logging.getLogger()
try:
    log_level = os.environ["LogLevel"]
    if log_level not in ["INFO", "DEBUG"]:
        log_level = "INFO"
except:
    log_level = "INFO"
logger.setLevel(log_level)

lex = boto3.client("lexv2-models")


def get_bot_id(bot_name):
    bot_info = lex.list_bots()
    logger.info(bot_info)
    filtered_bot = list(filter(lambda x: (x["botName"] == bot_name), bot_info["botSummaries"]))

    timeout = 0
    while len(filtered_bot) == 0:
        if timeout == 5:
            raise RuntimeError("Could not find bot")
        timeout += 1
        time.sleep(5)
        bot_info = lex.list_bots()
        logger.info(bot_info)
        filtered_bot = list(filter(lambda x: (x["botName"] == bot_name), bot_info["botSummaries"]))

    timeout = 0
    while not filtered_bot[0]["botStatus"] == "Available":
        if timeout == 5:
            raise RuntimeError("Bot not available")
        timeout += 1
        bot_info = lex.list_bots()
        logger.info(bot_info)
        filtered_bot = list(filter(lambda x: (x["botName"] == bot_name), bot_info["botSummaries"]))
        time.sleep(5)
    bot_id = filtered_bot[0]["botId"]
    logger.info(f"bot_id: {bot_id}")
    return bot_id


def get_bot_alias_id(bot_id):
    bot_alias_id = lex.list_bot_aliases(botId=bot_id, maxResults=1,)["botAliasSummaries"][
        0
    ]["botAliasId"]
    logger.info(bot_alias_id)
    return bot_alias_id


def build_bot(bot_id):
    build_response = lex.build_bot_locale(botId=bot_id, botVersion="DRAFT", localeId="en_US")
    return build_response


def put_resource_policy(bot_id, bot_alias_id, account_id):
    bot_arn = "".join(["arn:aws:lex:", region, ":", account_id, ":bot-alias/", bot_id, "/", bot_alias_id])
    resource_response = lex.create_resource_policy_statement(
        resourceArn=bot_arn,
        statementId="PSTNAudioLex",
        effect="Allow",
        principal=[
            {
                "service": "voiceconnector.chime.amazonaws.com",
            },
        ],
        action=[
            "lex:StartConversation",
        ],
        condition={
            "StringEquals": {"AWS:SourceAccount": account_id},
            "ArnEquals": {"AWS:SourceArn": "arn:aws:voiceconnector:" + region + ":" + account_id + ":*"},
        },
    )

    logger.info(resource_response)
    return resource_response


def import_bot(bot_name, import_id, lex_role_arn):
    bot_import_result = lex.start_import(
        importId=import_id,
        resourceSpecification={
            "botImportSpecification": {
                "botName": bot_name,
                "roleArn": lex_role_arn,
                "dataPrivacy": {"childDirected": False},
                "idleSessionTTLInSeconds": 600,
            },
        },
        mergeStrategy="Overwrite",
    )
    logger.info(bot_import_result)
    return bot_import_result


def upload_bot(upload_info):
    http = urllib3.PoolManager()
    try:
        with open("lexBot.zip", mode="rb") as bot:
            file_data = bot.read()

    except Exception as e:
        error = {"error": f"Exception thrown: {e}"}
        print(error)
        raise Exception(error)
    try:
        upload = http.request(
            "PUT", upload_info["uploadUrl"], body=file_data, headers={"Content-Type": "application/zip"}
        )

    except Exception as e:
        error = {"error": f"Exception thrown: {e}"}
        print(error)
        raise Exception(error)
    logger.info(upload.data.decode("utf-8"))
    return upload


def create_bot(bot_name, lex_role_arn, account_id):
    response_data = {}
    upload_info = lex.create_upload_url()
    upload_bot(upload_info)
    import_bot(bot_name, upload_info["importId"], lex_role_arn)
    bot_id = get_bot_id(bot_name)
    bot_alias_id = get_bot_alias_id(bot_id)
    # put_resource_policy(bot_id, bot_alias_id, account_id)
    build_bot(bot_id)
    response_data["bot_id"] = bot_id
    response_data["bot_alias_id"] = bot_alias_id
    return response_data


def delete_bot(bot_name):
    bot_id = get_bot_id(bot_name)
    print(bot_id)
    response = lex.delete_bot(botId=bot_id, skipResourceInUseCheck=True)
    return response


def handler(event, context):
    print(event)
    bot_name = event["ResourceProperties"]["uid"]
    lex_role_arn = event["ResourceProperties"]["lex_role_arn"]
    account_id = context.invoked_function_arn.split(":")[4]
    if event["RequestType"] == "Create":
        try:
            response_data = create_bot(bot_name, lex_role_arn, account_id)
            return {"PhysicalResourceId": bot_name, "Data": response_data}
        except Exception as e:
            error = {"error": f"Exception thrown: {e}"}
            print(error)
            raise Exception(error)
    elif event["RequestType"] == "Delete":
        try:
            response_data = delete_bot(bot_name)
            return {"PhysicalResourceId": bot_name, "Data": response_data}
        except Exception as e:
            error = {"error": f"Exception thrown: {e}"}
            print(error)
            raise Exception(error)
    else:
        responseData = {"Message": "Update is no-op. Returning success status."}
        return {"PhysicalResourceId": bot_name, "Data": responseData}