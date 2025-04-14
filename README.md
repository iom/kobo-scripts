# A collection of python script to work with Kobotoolbox API

Feel free to submit more scripts or improvements to existing ones. You can also create issues for any bugs or feature requests.

## Overview

The `media-update` script automates the process of updating a media file associated with a specific form in KoboToolbox. It performs the following steps:

1.  **Fetches the list of existing media files** for the specified form.
2.  **Deletes the existing media file** (if found) with the same name as the one being uploaded. This step is optional but ensures that the latest version of the media is used.
3.  **Uploads the new media file** to the form.
4.  **Redeploys the form** to activate the changes, making the new media file available in your data collection forms.

## Prerequisites

Before running this script, ensure you have the following:

* **Python 3.6 or higher** installed on your system.
* The following Python libraries installed:
    ```bash
    pip install requests python-dotenv
    ```
* A **`.env` file** in the same directory as the script with the following environment variables defined:
    ```
    URL='your_kobotoolbox_instance_url'
    TOKEN='your_kobotoolbox_api_token'
    XFORM='your_form_id'
    MEDIA_NAME='path/to/your/media/file.jpg'
    ```
    * `URL`: The base URL of your KoboToolbox instance (e.g., `https://kf.kobotoolbox.org` or `https://ee.kobotoolbox.org`).
    * `TOKEN`: Your KoboToolbox API token. You can generate this from your KoboToolbox account settings.
    * `XFORM`: The ID of the KoboToolbox form you want to update the media for (the numeric part of the form's URL).
    * `MEDIA_NAME`: The full path to the media file you want to upload (e.g., `/path/to/image.png`).

## Setup

1.  **Save the Python script:** Save the provided Python code as a `.py` file (e.g., `update_kobo_media.py`).
2.  **Create a `.env` file:** In the same directory as the script, create a file named `.env` and populate it with your KoboToolbox credentials and form/media details as described in the "Prerequisites" section. **Important:** Do not hardcode sensitive information directly in the script.
3.  **Ensure the media file exists:** Make sure the media file specified in the `MEDIA_NAME` environment variable exists at the given path.

## How to Use

1.  **Open your terminal or command prompt.**
2.  **Navigate to the directory** where you saved the Python script and the `.env` file.
3.  **Run the script** using the Python interpreter:
    ```bash
    python update_kobo_media.py
    ```
4.  **Observe the output:** The script will print messages indicating the progress of fetching media, deleting (if applicable), uploading, and redeploying the form. Check for any error messages.

## How it Works

The script utilizes the KoboToolbox API to interact with your forms and media files. Here's a breakdown of the process:

1.  **Environment Variable Loading:** The `dotenv` library loads the configuration variables (URL, TOKEN, XFORM, MEDIA\_NAME) from the `.env` file, making it easy to manage sensitive information and configuration.
2.  **API Authentication:** The script constructs an `Authorization` header using your API token. This header is included in all API requests to authenticate your access.
3.  **Fetching Media List:** A `GET` request is sent to the `/assets/{XFORM}/files/` endpoint to retrieve a JSON list of all media files currently associated with the specified form.
4.  **Deleting Existing Media (Optional):** The script iterates through the fetched media list. If a media file with the same filename as the one specified in `MEDIA_NAME` is found, a `DELETE` request is sent to the media file's URL to remove it.
5.  **Uploading New Media:** A `POST` request is sent to the `/assets/{XFORM}/files.json` endpoint to upload the new media file. The request includes:
    * Headers with the authorization token.
    * `data`: A dictionary containing metadata about the file (description, filename, file type). The `metadata` is passed as a JSON string.
    * `files`: A dictionary containing the actual file content, opened in binary read mode.
6.  **Redeploying the Form:** After successfully uploading the media, the script needs to redeploy the form for the changes to take effect. This involves:
    * Fetching the current form asset details using a `GET` request to `/assets/{XFORM}/` to get the latest `version_id`.
    * Sending a `PATCH` request to `/assets/{XFORM}/deployment/` with the `version_id` and `active: True` in the request body to redeploy the form with the new media.

## Important Notes

* **Error Handling:** The script includes basic error handling using `try...except` blocks to catch potential issues like network errors, file not found errors, and API errors. Review the output for any error messages.
* **API Rate Limiting:** Be mindful of KoboToolbox API rate limits. If you are performing this operation frequently for many forms, you might encounter throttling.
* **Permissions:** Ensure your API token has the necessary permissions to view, delete, add, and deploy assets in your KoboToolbox project.
* **File Paths:** Double-check the path to your media file specified in the `.env` file to avoid `FileNotFoundError`.
* **Customization:** You can adapt this script to handle multiple forms or multiple media files by modifying the loops and API calls accordingly.
