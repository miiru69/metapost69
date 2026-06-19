import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

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

rows = sheet.get_all_records()

for i, row in enumerate(rows, start=2):

    if row["status"].lower() == "pending":

        post_text = row["post_text"]

        page_id = os.environ["FB_PAGE_ID"]

        token = os.environ["FB_PAGE_TOKEN"]

        url = f"https://graph.facebook.com/{page_id}/feed"

        r = requests.post(
            url,
            data={
                "message": post_text,
                "access_token": token
            }
        )

        if r.status_code == 200:

            sheet.update_cell(
                i,
                2,
                "Posted"
            )

        break
