'''  This Code has been written by Arihan Sinha  '''

# Basic Imports ---->
import os
import tkinter as tk
from tkinter import filedialog

# Imports For AWS ---->
import boto3

# Imports For GOOGLE ---->
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

# Imports For AZURE ---->
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError
)

from azure.storage.fileshare import (
    ShareServiceClient,
    ShareClient,
    ShareDirectoryClient,
    ShareFileClient
)

# Create a GUI window
root = tk.Tk()
root.withdraw()  # Hide the main window

# Ask user to select a folder using the operating system's GUI
selected_folder = filedialog.askdirectory(title="Select a folder to upload")

# Set the scope and API for google
SCOPES = ['https://www.googleapis.com/auth/drive']
API_VERSION = 'v3'

# CREDENTIALS ---->
# Google Drive
creds = None
token_file = './credentials.json'
FOLDER_ID = ""  # Enter the folder ID here
if os.path.exists(token_file):
    # creds = Credentials.from_authorized_user_file('./credentials.json', SCOPES)
    print(creds)
    
if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          flow = InstalledAppFlow.from_client_secrets_file(
              'credentials.json', SCOPES)
          creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open('token.json', 'w') as token:
          token.write(creds.to_json())
          
service = build('drive', API_VERSION, credentials=creds)
        
# AWS
AWS_ACCESS_KEY = "AWS_ACCESS_KEY"
AWS_SECRET_KEY = "AWS_SECRET_KEY"
BUCKET_NAME = "BUCKET_NAME"

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

# AZURE
CONNECTION_STRING = "CONNECTION_STRING"

# Create a ShareServiceClient from a connection string
service_client = ShareServiceClient.from_connection_string(CONNECTION_STRING)



# FUNC TO UPLOAD FOLDER FOR GOOGLE DRIVE ---->
def upload_to_drive(service, file_path, file_name, folder_id=None):
    file_name = os.path.basename(file_path)
    media = MediaFileUpload(file_path, resumable=True)
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    if folder_id:
        request = service.files().create(
        media_body=media,
        body=file_metadata
    )
    else:
        request = service.files().create(
            media_body=media,
            body={'name': file_name}
        )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print("Uploaded %d%%." % int(status.progress() * 100))
    


# FUNC TO UPLOAD FOLDER FOR AWS ---->
def upload_to_aws(file_path, s3_key):
    s3_client.upload_file(file_path, BUCKET_NAME, s3_key)


# FUNC TO UPLOAD FOLDER FOR AZURE ---->
def create_file_share(connection_string, share_name):
    try:
        # Create a ShareClient from a connection string
        share_client = ShareClient.from_connection_string(
            connection_string, share_name)

        print("Creating share:", share_name)
        share_client.create_share()

    except ResourceExistsError as ex:
        print("ResourceExistsError:", ex.message)
        
        
def create_directory(connection_string, share_name, dir_name):
    try:
        # Create a ShareDirectoryClient from a connection string
        dir_client = ShareDirectoryClient.from_connection_string(
            connection_string, share_name, dir_name)

        print("Creating directory:", share_name + "/" + dir_name)
        dir_client.create_directory()

    except ResourceExistsError as ex:
        print("ResourceExistsError:", ex.message)
        
        
def upload_local_file(connection_string, local_file_path, share_name, dest_file_path):
    try:
        source_file = open(local_file_path, "rb")
        data = source_file.read()

        # Create a ShareFileClient from a connection string
        file_client = ShareFileClient.from_connection_string(
            connection_string, share_name, dest_file_path)

        print("Uploading to:", share_name + "/" + dest_file_path)
        file_client.upload_file(data)

    except ResourceExistsError as ex:
        print("ResourceExistsError:", ex.message)

    except ResourceNotFoundError as ex:
        print("ResourceNotFoundError:", ex.message)
          
# create_file_share(CONNECTION_STRING, "testshare")
    
    
# Set to store unique file extensions
file_extensions = set()

# Walk through the selected folder and its subfolders
for root_dir, _, files in os.walk(selected_folder):
    for file in files:
        _, file_extension = os.path.splitext(file)
        if file_extension:
            file_extensions.add(file_extension.lower()) 
            
            
images = ['.apng', '.avif', '.gif', '.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp', '.png', '.svg', '.webp', '.bmp', '.ico', '.tif', '.tiff']
documents = ['.doc', '.docx', '.pdf', '.htm', '.odt', '.xls', '.xlsx', '.ods', '.ppt', '.pptx', '.txt', '.rtf', '.tex', '.wks', '.wps', '.wpd', '.odp', '.pps', '.csv', '.xml', '.key', '.pages', '.numbers']
videos = ['.webm', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.ogg', '.mp4', '.m4p', '.m4v', '.avi', '.wmv', '.mov', '.qt', '.flv', '.swf', '.avchd']
system = ['.bak', '.cab', '.cfg', '.cpl', '.cur', '.dll', '.dmp', '.drv', '.icns', '.ini', '.lnk', '.msi', '.sys', '.tmp', '.dmg', '.pkg', '.app', '.command', '.ipa', '.jar', '.wsf', '.apk', '.bat', '.cgi', '.pl', '.com', '.exe', '.gadget', '.pif', '.wsf', '.vbs']
language = ['.c', '.class', '.cpp', '.cs', '.h', '.java', '.sh', '.swift', '.vb', '.ipynb', '.js', '.html', '.css', '.php', '.json', '.xml', '.yml', '.yaml', '.md', '.cfg', '.ini', '.log', '.properties', '.prop', '.rc', '.rss', '.xaml', '.xhtml', '.xib', '.plist', '.strings', '.bat', '.cmd', '.url', '.desktop', '.applescript', '.bas', '.cgi', '.pl', '.rb', '.c', '.cs', '.h', '.java', '.php', '.py', '.sh', '.swift', '.vb', '.vbproj', '.vcxproj', '.xcodeproj',]

# Distribute the files into their respective cloud storage
drive = system + language 
azure_ext = videos
aws_ext = images + documents

for root_dir, _, files in os.walk(selected_folder):
            for file in files:
                file_path = os.path.join(root_dir, file)
                file_type = os.path.splitext(file)[1][1:]
                _, extension = os.path.splitext(file)
                folder_name = extension[1:]
                file_name = folder_name + "/" + file
                if extension in drive:
                    folder_metadata = {
                        'name': file_type.capitalize(),
                        'mimeType': 'application/vnd.google-apps.folder',
                        'parents': [FOLDER_ID]
                    }
                    folder = service.files().create(body=folder_metadata).execute()
                    folder_id = folder['id']
                    upload_to_drive(service, file_path, file, folder_id)
                                               
                elif extension in azure_ext:
                    create_directory(CONNECTION_STRING, "testshare", folder_name)
                    upload_local_file(CONNECTION_STRING, file_path, "testshare", file_name)
                elif extension in aws_ext:
                    upload_to_aws(file_path, file_name)
                else:
                    print(f"File type not supported --------------------> {extension}")
                
                
print("Operation Complete...")
                
