import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

# Google Credentials
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

# Load Pages
with open("pages.json", "r", encoding="utf-8") as f:
    pages = json.load(f)

# Read Google Sheet
rows = sheet.get_all_records()

for i, row in enumerate(rows, start=2):

    status = str(row["status"]).strip().lower()

    if status == "pending":

        post_text = row["post_text"]

        all_success = True

        for page in pages:

            page_id = page["id"]
            token = os.environ[page["token_env"]]

            url = f"https://graph.facebook.com/v23.0/{page_id}/feed"

            response = requests.post(
                url,
                data={
                    "message": post_text,
                    "access_token": token
                }
            )

            print(f"\nPosting To Page: {page_id}")
            print("Facebook Status:", response.status_code)
            print("Facebook Response:", response.text)

            if response.status_code != 200:
                all_success = False

        if all_success:
            sheet.update_cell(i, 2, "Posted")
            print("\nPosted Successfully To All Pages")
        else:
            print("\nOne Or More Pages Failed")

        break

print("\nDone")
