from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import os
def fetch_google_cloud_bucket_file(filename):
    json_file_path = os.path.abspath('./light-tribute-368217-8f373ac9f832.json')
    json_file_relpath = os.path.relpath(json_file_path)

    # Load the service account credentials from the JSON file
    creds = Credentials.from_service_account_file(json_file_relpath, scopes=['https://www.googleapis.com/auth/cloud-platform'])

    # Build the Cloud Storage client
    service = build('storage', 'v1', credentials=creds)

    # List the objects in the bucket
    results = service.objects().list(bucket='shiplocationdata').execute()
    items = results.get('items', [])

    # Find the object with the specified filename
    file = None
    for item in items:
        file_name = item['name']
        bucket_name = item['bucket']
        if file_name == filename:
            # Get the contents of the object
            request = service.objects().get_media(bucket=bucket_name, object=file_name)
            file = request.execute()
            break

    return file
