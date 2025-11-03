import pdb
import sqlite3
import json
import requests

def filter_emails(rules, conn):
    cursor = conn.cursor()
    # just testing if all emails are fetched
    # cursor.execute("SELECT * FROM emails")
    # all_emails = cursor.fetchall()
    query = query_builder_generator(rules)
    cursor.execute(query)
    rows = cursor.fetchall()
    if len(rows) < 1:
        print("No rows found for these rules, exiting...")

    body = { "ids": [], "addLabelIds": [], "removeLabelIds": [] }

    for row in rows:
        body["ids"].append(row[0])

    # now we process the actions and create the body ffor the rest api
    if len(rules['actions']) > 0:
        for action in rules['actions']:
            process_action_and_form_body(action, body)

    # at this point body is ready and we can proceed to make ther REST api call for batch processing of the mails
    with open("token.json") as f:
        token = json.load(f)

    response = batch_process(body, token['token'])
    if response.status_code == 204:
        print("Success. Leaving the program")
        return True



def query_builder_generator(rules):
    query = "SELECT * FROM emails"
    # if there eixts rules, then surely a where clause needs to be added
    if len(rules['rules']['rules_array']) > 0:
        query += " WHERE "
        try:
            for index, rule in enumerate(rules['rules']['rules_array']):
                # pdb.set_trace()

                if index > 0:
                    if (rules['rules']['collection_rule'] == 'any'):
                        query += " OR "
                    else:
                        query += " AND "
                field_name = ""
                predicate_and_value = ""
                # logic for field
                match rule['field']:
                    case "from":
                        field_name = "sender"
                    case "to":
                        field_name = "receiver"
                    case "subject":
                        field_name = "subject"
                    case "date_received":
                        field_name = "date_received"
                    case _:
                        raise ValueError("A field name is not properly set")
                # logic for predicate
                match rule['predicate']:
                    case "contains":
                        if field_name != "date_received":
                            predicate_and_value = f" LIKE '%{rule['value']}%'"
                        else:
                            raise ValueError("contains predicate which should be used on date only")
                    case "not_equals":
                        if field_name != "date_received":
                            predicate_and_value = f" != '%{rule['value']}%'"
                        else:
                            raise ValueError("contains predicate which should be used on date only")
                    case "less_than":
                        if field_name == "date_received":
                            # datetime(date_received) >= datetime('now', '-3 days')
                            predicate_and_value = f" >= datetime('now', '-{rule['value']}')"
                        else:
                            raise ValueError("contains predicate should be not be used here")
                    case _:
                        raise ValueError("A predicate is not properly set")

                query += field_name + predicate_and_value

            return query
        except Exception as e:
            print("Error:", e)
            raise e



def process_action_and_form_body(action, body):
    # pdb.set_trace()
    if action["action_name"] == "mark_as_read":
        body["removeLabelIds"].append("UNREAD")
    if action["action_name"] == "mark_as_unread":
        body["addLabelIds"].append("UNREAD")

    # in this case I am expecting the user to provide correct labels in the rules json itself, you can reference the main.py file for that
    if action["action_name"] == "move_message":
        body["addLabelIds"].append(action["to_mailbox"])

def batch_process(body, access_token):
    # the user id is me
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        return response
    except Exception as e:
        # pdb.set_trace()
        print(e)
        raise e
