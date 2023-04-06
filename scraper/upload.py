import boto3
import os
from syncKendra import syncKendra
import os
from dotenv import load_dotenv
from pathlib import Path
import zipfile

def uploadS3(bucket_name, profile_name):
    # Set the S3 bucket name and directory path of the files you want to upload
    zip_file_path = './courses.zip'
    temp_extract_path = './temp_extract'
    directory_path = temp_extract_path

    # Extract the zip file to a temporary directory
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_path)

    # Create a session with the AWS profile
    session = boto3.Session(profile_name=profile_name)

    # Create an S3 resource using the session
    s3 = session.resource('s3')

    # Loop through the files in the local directory and upload them to S3
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = os.path.join(os.path.relpath(root, directory_path), file)
            s3_path = s3_path.replace('\\', '/')  # Replace backslashes with forward slashes for S3 path
            s3_object = s3.Object(bucket_name, s3_path)
            s3_object.upload_file(local_path)
            print(f'Uploaded {file} to {bucket_name}/{s3_path}')

    # Delete the temporary directory and its contents
    for root, dirs, files in os.walk(directory_path, topdown=False):
        for file in files:
            os.remove(os.path.join(root, file))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    os.rmdir(directory_path)

load_dotenv(dotenv_path=Path("../.env"))

profile_name = os.getenv("PROFILE_NAME")
bucket_name = os.getenv("S3_BUCKET_NAME")
kendra_data_source_id = os.getenv("KENDRA_DATA_SOURCE_ID")
kendra_index_id = os.getenv("KENDRA_INDEX_ID")

uploadS3(bucket_name,profile_name)
syncKendra(kendra_data_source_id,kendra_index_id,profile_name)