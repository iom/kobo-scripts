# Import necessary libraries
import requests  # For making HTTP requests
import json     # For working with JSON data
import dotenv   # For loading environment variables from a .env file
import os       # For interacting with the operating system

# Load environment variables from a .env file.
# This is useful for storing sensitive information like URLs and tokens
# outside of the main script. Make sure you have a .env file in the same directory
# as this script with the following variables defined:
# URL='your_kobotoolbox_instance_url'
# TOKEN='your_kobotoolbox_api_token'
# XFORM='your_form_id'
# MEDIA_NAME='path/to/your/media/file.jpg' (or any other media file)
dotenv.load_dotenv()

# Retrieve environment variables
URL = os.getenv('URL')
TOKEN = os.getenv('TOKEN')
XFORM = os.getenv('XFORM')

# Check if the necessary environment variables are set.
# If not, the script cannot function correctly.
if not all([URL, TOKEN, XFORM, os.getenv('MEDIA_NAME')]):
    print("Error: Please ensure URL, TOKEN, XFORM, and MEDIA_NAME are defined in your .env file.")
    exit()

# Construct the headers for API requests.
# Most KoboToolbox API requests require an Authorization header with your API token.
headers = {'Authorization': f'Token {TOKEN}'}

# Construct the URL to list media files associated with a specific form (XFORM).
url = f"{URL}/assets/{XFORM}/files/"

# --- GET FORM MEDIA LIST ---
print(f"Fetching the list of media files for form ID: {XFORM}...")
try:
    # Make a GET request to the KoboToolbox API to retrieve the list of media files.
    response = requests.get(url, headers=headers, params={'format': 'json'})
    response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
    media_json = response.json()
    print("Successfully retrieved the media file list.")
except requests.exceptions.RequestException as e:
    print(f"Error fetching media list: {e}")
    exit()

# --- HANDLE A SINGLE FILE FOR A SINGLE FORM (Example) ---
# This script is designed to handle one media file for a specific form.
# You can extend it to iterate over lists of form IDs and/or media files
# by modifying the logic here.

# Get the full path to the media file from the environment variable.
MEDIA_PATH = os.getenv('MEDIA_NAME')
# Extract the filename from the full path.
MEDIA_NAME = os.path.basename(MEDIA_PATH)
print(f"Processing media file: {MEDIA_NAME}")

# --- DELETE EXISTING FILE (Optional) ---
print("Checking if the media file already exists in the form's media...")
found = False
for media in media_json['results']:
    # Compare the filename of the existing media with the name of the file to be uploaded.
    if media['metadata']['filename'] == MEDIA_NAME:
        found = True
        del_url = media['url']
        print(f"Found existing media file: {MEDIA_NAME} at {del_url}. Attempting to delete...")
        try:
            # Make a DELETE request to remove the existing media file.
            delete_response = requests.delete(del_url, headers=headers)
            delete_response.raise_for_status()
            print(f"Successfully deleted {MEDIA_NAME}. Status code: {delete_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error deleting {MEDIA_NAME}: {e}")
        break

if not found:
    print(f"Media file {MEDIA_NAME} not found in the form's media. It will be uploaded.")
    # Depending on your workflow, you might want to exit here if the file was expected to exist.
    # For this script, we proceed with the upload regardless.

# --- UPLOAD FILE ---
print(f"Attempting to upload: {MEDIA_NAME}...")
post_url = f"{URL}/assets/{XFORM}/files.json"
# The 'filename' in the payload seems to be redundant as the filename is also
# part of the 'files' dictionary.
payload = {'filename': MEDIA_NAME}

try:
    # Open the media file in binary read mode ('rb').
    with open(MEDIA_PATH, 'rb') as bytes_content:
        # Prepare the 'files' dictionary for the POST request.
        # The key 'content' is what KoboToolbox expects for the file data.
        files = {'content': bytes_content}
        # Prepare the 'data' dictionary for additional information about the file.
        # 'description' is a human-readable description of the file.
        # 'metadata' is a JSON string containing metadata, including the filename.
        # 'file_type' should be 'form_media' for media associated with the form.
        data = {
            'description': 'Input and equipment media file',
            'metadata': json.dumps({'filename': MEDIA_NAME}),
            'file_type': 'form_media'
        }
        # Make a POST request to upload the new media file.
        upload_response = requests.post(url=post_url, headers=headers, data=data, files=files)
        upload_response.raise_for_status()
        print(f"Successfully uploaded {MEDIA_NAME}. Status code: {upload_response.status_code}")
except FileNotFoundError:
    print(f"Error: Media file not found at path: {MEDIA_PATH}")
except requests.exceptions.RequestException as e:
    print(f"Error uploading {MEDIA_NAME}: {e}")
    exit()

# --- REDEPLOY FORM ---
print(f"Attempting to redeploy form ID: {XFORM} to apply changes...")
asset_url = f"{URL}/assets/{XFORM}/"
# Define headers specifically for the redeployment request.
# 'Accept: application/json' indicates that the client expects JSON responses.
redeploy_headers = {
    'Accept': 'application/json',
    'Authorization': f'Token {TOKEN}'
}

try:
    # Get the current asset information to retrieve the latest version ID.
    response = requests.get(asset_url, headers=redeploy_headers, params={'format': 'json'})
    response.raise_for_status()
    asset_data = response.json()
    version_to_deploy = asset_data['version_id']
    print(f"Current form version ID: {version_to_deploy}")

    # Prepare the data for the redeployment PATCH request.
    # 'version_id' specifies the version to deploy.
    # 'active: True' activates this version, making it the current live version.
    deployment_data = {
        'version_id': version_to_deploy,
        'active': True
    }
    # Make a PATCH request to the deployment endpoint to redeploy the form.
    redeploy_response = requests.patch(asset_url + 'deployment/', headers=redeploy_headers, data=deployment_data)
    redeploy_response.raise_for_status()
    print(f"Successfully redeployed form ID: {XFORM}. Status code: {redeploy_response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"Error redeploying form ID {XFORM}: {e}")