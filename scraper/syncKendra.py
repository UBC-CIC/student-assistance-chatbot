import boto3
from botocore.exceptions import ClientError
import pprint
import time

REGION = "ca-central-1"
session = boto3.Session(profile_name="myprofile")
kendra = session.client("kendra",region_name=REGION)


def syncKendra(dataSourceId, indexId):
    try:

        print("Synchronize the data source.")

        sync_response = kendra.start_data_source_sync_job(
            Id = dataSourceId,
            IndexId = indexId
        )

        pprint.pprint(sync_response)

        print("Wait for the data source to sync with the index.")
        time.sleep(5)
        while True:

            jobs = kendra.list_data_source_sync_jobs(
                Id = dataSourceId,
                IndexId = indexId
            )
            # For this example, there should be one job
            status = jobs["History"][0]["Status"]

            print(" Syncing data source. Status: "+status)
            if status != "SYNCING":
                break
            time.sleep(60)

    except  ClientError as e:
            print("%s" % e)

    print("Program ends.")