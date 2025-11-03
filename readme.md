# HappyFox Backend Assignment

## Setup
- clone the repository
- cd into the repository, setup virtual env and then use required dependencies with commands given below
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- At this point you should create a project in google developer account.
- Name that application something, and enable gmail api on the project.
- In the 'API and Services' section of the project, crate OAuth credentials for the project.
  Note - you must use 'desktop app' option to create Oauth credentials. As this is a CLI app
- Also add the email (for which you will test) into the test email
- Steps to add test email to project
  - goto 'Api and services' section in google cloud dev website
  - goto OAuth consent screen
  - click on 'Audience' in the left hand side menu
  - The new page that would load will have a section called 'Test users', which would have an 'Add User' button, click on it and add your test user which you will use for this script.
- Now your email and credentials that you have generated for that email are ready to be used for this CLI to work.
- Download the credentials files. and place it inside the prject folder.  
- Now you can run the program with ternminal command given below
```bash
  python3 main.py
```
- The program will run and try to verify the OAuth creds , this will open a browser in yourr operating system, and will prompt your google email to verify the CLI application.
- Give the access to this project. It will prompt you by saying the app is not verified by google, but that is standard message, kindly allow access.
- A token will be generated and the program will store the token in token.js in the same directory
## Program Wiki:
+ the rules are saved inside rules.json file
```json
{
  "subject_query": "rw@peterc.org",
  "rules": {
    "collection_rule": "all",
    "rules_array": [
      {
        "field": "from",
        "predicate": "contains",
        "value": "rw@peterc.org"
      },
      {
        "field": "subject",
        "predicate": "contains",
        "value": "Breaking the ice"
      },
      {
        "field": "date_received",
        "predicate": "less_than",
        "value": "100 days"
      }
    ]
  },
  "actions": [
    {
      "action_name": "mark_as_unread"
    },
    {
      "action_name": "move_message",
      "to_mailbox": "SPAM"
    }
  ]
}
```
+ This above is what a standard rules file will look like, for the test purpose and recording a video, I have decided to add subject_query params as my own, as I and every sane person would not allow a 3rd person to read their email, so for recording the video i will pass this param, to only download mails from this user
  - As per normal workflow of this application, the application will download all emails from my inboc and then take rules from rules.json. And apply action. The ffrom action in rules.json works on all emails. So it will still download all emails and then apply filter rule on fetched emails, which would be stored in my sqlite3 db.
  - In the case that you want to download all mails, just keep "subject_query" field as empty and then it would work fffine for you on your personal computer while you test. (we can have one call if you find any issue)
+ collection_rule specifies which filter rule to apply
  - Options - ['any', 'all'] 
+ rules array contains the filterr that would be applied when filtering the data from the sqlite db. The single rule contain thre onject explained below
  - 'field' option can take 4 params - ['from', 'to', 'subject', 'date_received']
  - 'predicate' option can take 3 params - ['contains', 'not_equals', 'less_than'] **Less than only works on date field, and contains and not equals work on 'from', 'to' and 'subject'**
  - value option can take a string which will be used for query, **in case of date_received you must use days or hours, for eg: '100 days' **
+ Actions would apply the selected action on the filtered emails
  - 'action_name' field take one of these 3 valid input - ['mark_as_unread', 'mark_as_read', 'move_message']
  - 'to_mailbox' field can only be applied when your action name is  'move_message', and it takes the name of the label , which would be applied to it
    - These below are valid options **labels =  CHAT, SENT, INBOX, IMPORTANT, TRASH, DRAFT, SPAM, CATEGORY_FORUMS, CATEGORY_UPDATES, CATEGORY_PERSONAL, CATEGORY_PROMOTIONS, CATEGORY_SOCIAL, YELLOW_STAR, STARRED, UNREAD**


*Run the test with below command*
```bash
python -m unittest tests.py -v
```

**BELOW IS A THE VIDEO FFFILE CONTAINING THE DEMO, CODE EXPLANATION AND A WALKTHROUGH**

[▶️ Watch output video](https://uploadnow.io/f/rzgFv9r)



