import os.path
import sqlite3
import json

# debugging
import pdb
import process_emails_and_apply_actions
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.
# SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

# below is the list of labels that most of the emails have
# labels =  CHAT, SENT, INBOX, IMPORTANT, TRASH, DRAFT, SPAM, CATEGORY_FORUMS, CATEGORY_UPDATES, CATEGORY_PERSONAL, CATEGORY_PROMOTIONS, CATEGORY_SOCIAL, YELLOW_STAR, STARRED, UNREAD

def authenticate_and_create_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            try:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            except Exception as e:
                print(e)
                print("It would seem you dont have a credentials file in the directory, Need the file to verify your identity. Exiting for now, after displaying the error messages.")
                print("--------------------------------")
                raise e
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open("token.json", "w") as token:
          token.write(creds.to_json())

    try:
        # Call the Gmail API
        # Note - This is something we will use only once and return if service object is successfully created
        service = build("gmail", "v1", credentials=creds)
        results = service.users().labels().list(userId="me").execute()

        # pdb.set_trace()
        labels = results.get("labels", [])
        if not labels:
            print("No labels found. Hence Returning/Exiting")
            return

        # for debugging we can use this
        # print("Labels:")
        # for label in labels:
        #     print(label["name"])
        return service

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")


def read(service, rules):
    try:
        query_params = {"userId": "me", "labelIds": ["INBOX"],  "maxResults": 100 }
        if rules.get("subject_query") and len(rules.get("subject_query")) > 1:
            query_params["q"] = rules.get("subject_query")

        results = (service.users().messages().list(**query_params).execute())
        messages = results.get("messages", [])

        if not messages:
            print("No messages found.")
            return


        print("Successfully created the messages object.")
        # print(messages[0])
        return messages
    except HttpError as error:
        print(f"An error occurred: {error}")


def store_messages_in_db(conn, messages):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM emails")
        all_emails = c.fetchall()

        # this is for my personal testing
        # if len(all_emails) >= 100:
        #     print("we already have 100 msgs, skipping loading the messages... and performing operations on emails loaded in db:")
        #     return

        c.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                sender TEXT,
                receiver TEXT,
                date_received TEXT,
                subject TEXT,
                snippet TEXT,
                label_ids TEXT ARRAY
            )
        ''')

        print("Kindly wait, loading 100 emails :")

        for index, msg in enumerate(messages):
            # print(f'Message ID: {message["id"]}')

            txt = service.users().messages().get(userId='me', id=msg['id']).execute()
            # print(f'  Subject: {txt["snippet"]}')

            headers = txt['payload']['headers']

            id = txt['id']

            sender = next(header['value'] for header in headers if header['name'] == 'From')
            sender = sender.split("<")[1].split(">")[0]
            receiver = headers[0]['value']

            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            date_str_clean = date_str.split(" (")[0]
            dt = datetime.strptime(date_str_clean, "%a, %d %b %Y %H:%M:%S %z")
            date = dt.strftime("%Y-%m-%d %H:%M:%S")

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            snippet = txt['snippet']
            labels = ",".join(txt['labelIds'])

            # pdb.set_trace()

            c.execute('''INSERT OR REPLACE INTO emails VALUES (?, ?, ?, ?, ?, ?, ?)''', (id, sender, receiver, date, subject, snippet, labels))
            print("Successfully Saved " + str(index + 1) + " into the db.")
        conn.commit()
        print(f"Fetched and stored {len(messages)} emails.")
    except Exception as e:
        raise e

def load_rules():
    with open("rules.json") as f:
        cfg = json.load(f)

    return cfg





if __name__ == "__main__":
    # authenticate with gmail api server
    service = authenticate_and_create_service()
    # load the rules from file
    rules = load_rules()
    # connect to the db
    conn = sqlite3.connect('emails.db')
    # get the message object from gmail api
    messages = read(service, rules)
    # query the messages and then store them in db
    store_messages_in_db(conn, messages)

    # the below command filters the emails based on rules
    result = process_emails_and_apply_actions.filter_emails(rules, conn)



