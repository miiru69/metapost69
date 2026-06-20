import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

print("Bot Started")

# Google Sheets Login
creds = Credentials.from_service_account_info(
    json.loads(os.environ["GOOGLE_CREDENTIALS"]),
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    os.environ["SHEET_ID"]
).sheet1

print("Google Sheet Connected")

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

print("Rows Found:", len(rows))

for i, row in enumerate(rows, start=2):

    status = str(row.get("status", "")).strip().lower()

    if status != "pending":
        continue

    post_text = str(row.get("post_text", "")).strip()

    if not post_text:
        print("Empty post text")
        continue

    print("Posting:", post_text[:100])

    success_count = 0

    for page in pages:

        page_id = page["id"]
        token = page["token"]

        try:

            response = requests.post(
                f"https://graph.facebook.com/v23.0/{page_id}/feed",
                data={
                    "message": post_text,
                    "access_token": token
                },
                timeout=30
            )

            print(f"Page {page_id}")
            print("Status:", response.status_code)
            print("Response:", response.text)

            if response.status_code == 200:
                success_count += 1

        except Exception as e:
            print(f"Error on page {page_id}: {e}")

    print(f"Success Count: {success_count}/5")

    if success_count == 5:
        sheet.update_cell(i, 2, "Posted")
        print("Marked as Posted")
    else:
        print("Some pages failed")

    break

print("Finished")
