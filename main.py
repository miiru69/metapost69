import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets Authentication
creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])

scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]

creds = Credentials.from_service_account_info(
    creds_json,
    scopes=scopes
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    os.environ["SHEET_ID"]
).sheet1

# Facebook Pages
pages = [
    {
        "id": os.environ["PAGE1_ID"],
        "token": os.environ["PAGE1_TOKEN"]
    },
    {
        "id": os.environ["PAGE2_ID"],
        "token": os.environ["PAGE2_TOKEN"]
    },
    {
        "id": os.environ["PAGE3_ID"],
        "token": os.environ["PAGE3_TOKEN"]
    },
    {
        "id": os.environ["PAGE4_ID"],
        "token": os.environ["PAGE4_TOKEN"]
    },
    {
        "id": os.environ["PAGE5_ID"],
        "token": os.environ["PAGE5_TOKEN"]
    }
]

rows = sheet.get_all_records()

for i, row in enumerate(rows, start=2):

    status = str(row["status"]).strip().lower()

    if status == "pending":

        post_text = row["post_text"]

        all_success = True

        for page in pages:

            url = f"https://graph.facebook.com/v23.0/{page['id']}/feed"

            response = requests.post(
                url,
                data={
                    "message": post_text,
                    "access_token": page["token"]
                }
            )

            print(f"Page ID: {page['id']}")
            print("Facebook Status:", response.status_code)
            print("Facebook Response:", response.text)

            if response.status_code != 200:
                all_success = False

        if all_success:
            sheet.update_cell(i, 2, "Posted")
            print("Posted Successfully To All 5 Pages")
        else:
            print("One or More Pages Failed")

        break

print("Done")
