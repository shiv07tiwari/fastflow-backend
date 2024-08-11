import base64
import os
from email.message import EmailMessage

from googlesearch import search
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow

from googleapiclient.discovery import build

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


def get_urls_for_search_query(company_name, num_results=10):
    """
    This uses a very basic wrapper around google search.
    Need to replace this with serper in future
    """
    query = f"{company_name} reviews"
    search_results = []
    try:
        for j in search(query, stop=num_results):
            print("Found URL from Google: ", j)
            search_results.append(j)

        return search_results
    except Exception as e:
        return []


def create_flow():
    flow = Flow.from_client_secrets_file(
        'client_secrets.json',  # Path to your OAuth2 credentials
        scopes=[
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/drive'
        ],  # Adjust scopes based on your needs
        redirect_uri='postmessage',
    )
    return flow


class GoogleService:

    def __init__(self):
        self.token = "ya29.a0AcM612zI0QAFcjXKC4ROVJNIdoYMKKhXrqzuGfWCtWeDZbcSdnNKc9TU-5j05MnWMQa2VpydxLORMwy12QIpp1VVvpISkLrWXn6UoPytNJO_6D-lPLlwKP29giMBfFwp8fjh5-nP4I1xV7TmkaX-G3ELlRzdhZOHXQaCgYKAZkSARISFQHGX2MiNYMw1y2aLK8T38MiDyCx4A0169"
        _REFRESH_TOKEN = '1//0g1osyCYdT11xCgYIARAAGBASNwF-L9IrViDG9Tn-sAz-1n7Gcw9989yx1nPbTE4ZUOTGhQn81-T3bhM-u3Y9trtV77tfOmqyDXA'
        self.creds = Credentials.from_authorized_user_info(info={
            "token": self.token,
            "refresh_token": _REFRESH_TOKEN,  # You should store and use refresh tokens in a real app
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            'token_uri': 'https://oauth2.googleapis.com/token'
        })
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)

    async def create_new_sheet(self, rows, headers):
        title = "Sheet"
        try:
            spreadsheet_body = {
                'properties': {'title': title},
                'sheets': [
                    {
                        'properties': {
                            'title': title,
                            'gridProperties': {
                                'rowCount': len(rows) + 1,  # plus one for headers
                                'columnCount': len(headers)
                            }
                        }
                    }
                ]
            }
            spreadsheet = self.sheets_service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
            spreadsheet_id = spreadsheet.get('spreadsheetId')

            range_name = f'{title}!A1:{chr(65 + len(headers) - 1)}{len(rows) + 1}'
            values = [headers] + rows

            data = {
                'values': values
            }

            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=data
            ).execute()

            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit?gid=899975310#gid=899975310"

            return {"message": "Spreadsheet created", "url": spreadsheet_url}
        except ValueError:
            print("Invalid token")
            raise Exception("Invalid token")

    async def append_to_sheet(self, spreadsheet_id, data):
        """
        Appends data to an existing Google Sheet.
        Args:
            spreadsheet_id (str): The ID of the spreadsheet to update.
            data (list[list[Any]]): 2D list of data to append.
        Returns:
            dict: Result containing Google API response.
        """
        sheet_name = "Sheet"
        range_name = f"{sheet_name}!A:A"

        # Dictionary to structure the data for appending
        body = {
            'values': data
        }

        # Append data to the sheet
        try:
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit?gid=899975310#gid=899975310"
            return {"message": "Data appended to sheet", "url": spreadsheet_url}
        except Exception as e:
            print("Failed to append data to the sheet:", e)
            raise

    async def create_sheet(self, rows, headers):
        # flow = create_flow()
        # flow.fetch_token(code="4/0AcvDMrCTRxUIHP90c57TJPx730XAV-k_swFqrqrF5VJqNv9-fKsM5gOtPmrluUSJx1zSYg")
        # credentials = flow.credentials
        sheet_id = "15Eru8Qg5hfAhMvM8QvVtxbmyojG4OBQXIr9I5AGPhgQ"
        existing_sheet = self.sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()

        if existing_sheet:
            res = await self.append_to_sheet(sheet_id, rows)
            return res
        else:
            res = await self.create_new_sheet(rows, headers)
            return res

    def sanitize_header(self, value):
        """Remove any newline or carriage return characters from the header value."""
        if not value:
            return value
        return value.replace('\n', ' ').replace('\r', ' ')

    async def draft_email(self, content, to_email, from_email, subject):
        try:
            message = EmailMessage()
            message.set_content(content)
            message["To"] = self.sanitize_header(to_email) or ''
            message["From"] = self.sanitize_header(from_email) or ''
            message["Subject"] = self.sanitize_header(subject) or ''
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {"message": {"raw": encoded_message}}
            draft = (
                self.gmail_service.users()
                .drafts()
                .create(userId="me", body=create_message)
                .execute()
            )

            print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')
            return draft
        except Exception as e:
            print("Error in sending email: ", e)
            raise e

    async def read_data_from_sheet(self, spreadsheet_id):
        try:
            sheet = self.sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range="A1:D100").execute()
            rows = sheet.get("values", [])
            return rows
        except Exception as e:
            print("Error in reading data from sheet: ", e)
            raise e