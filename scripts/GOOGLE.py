import pickle
from datetime import datetime
import os
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

def Create_Service(client_secret_file, api_name, api_version, *scopes):
  """
  Creates a service object for a Google API with automatic token refresh.

  Args:
      client_secret_file: Path to the file containing your Google Cloud Platform project's client ID and secret.
      api_name: Name of the Google API you want to access (e.g., "drive", "sheets").
      api_version: Version of the API you want to use.
      *scopes: Variable arguments representing the list of permissions your application needs for the API.

  Returns:
      A service object for the specified Google API or None on errors.
  """

  CLIENT_SECRET_FILE = client_secret_file
  API_SERVICE_NAME = api_name
  API_VERSION = api_version
  SCOPES = [scope for scope in scopes[0]]

  # Define pickle file path
  pickle_file = f'artifacts/service_token/token_{API_SERVICE_NAME}_{API_VERSION}.pickle'

  try:
    # Try to load credentials from pickle file
    with open(pickle_file, 'rb') as token:
      cred = pickle.load(token)
  except (OSError, pickle.UnpicklingError):
    cred = None

  # Check and refresh credentials if necessary
  if not cred or not cred.valid:
    if cred and cred.expired and cred.refresh_token:
      print('Refreshing expired token...')
      cred.refresh(Request())

    else:
      print('Obtaining new credentials...')
      flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
      cred = flow.run_local_server()  # Might require user interaction

  # Save refreshed or newly obtained credentials
  with open(pickle_file, 'wb') as token:
    pickle.dump(cred, token)

  try:
    # Build the service object using the credentials
    service = build(API_SERVICE_NAME, API_VERSION, credentials=cred)
    print(API_SERVICE_NAME, 'service created successfully')
    return service
  except Exception as e:
    print('Unable to connect.')
    print(e)
    return None

def convert_to_RFC_datetime(year=1900, month=1, day=1, hour=0, minute=0):
  """
  Converts a date/time to RFC 3339 format (not used in refresh functionality).
  """
  dt = datetime.datetime(year, month, day, hour, minute, 0).isoformat() + 'Z'
  return dt
