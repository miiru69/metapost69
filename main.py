python
import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials

print("Bot Started")

# Google Auth
creds_json = json.loads(os.environ["GOOGLE_CREDENTIALS"])

creds = Credentials.from_service_account_info(
    creds_json,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

client = gspread.authorize(creds)

sheet = client.open_by_key(
    os.environ["SHEET_ID"]
).sheet1

print("Google Sheet Connected")

# Pages
pages = []

for n in range(1, 6):
    pages.append({
        "id": os.environ[f"PAGE{n}_ID"],
        "token": os.environ[f"PAGE{n}_TOKEN"]
    })

rows = sheet.get_all_records()

print("Rows Found:", len(rows))

for i, row in enumerate(rows, start=2):

    status = str(row.get("status", "")).strip().lower()

    if status != "pending":
        continue

    post_text = row.get("post_text", "")

    if not post_text:
        print("Post text empty")
        continue

    print("Posting:", post_text[:50])

    success_count = 0

    for page in pages:

        try:

            response = requests.post(
                f"https://graph.facebook.com/v23.0/{page['id']}/feed",
                data={
                    "message": post_text,
                    "access_token": page["token"]
                }
            )

            print(
                f"Page {page['id']} | "
                f"Status {response.status_code}"
            )

            print(response.text)

            if response.status_code == 200:
                success_count += 1

        except Exception as e:
            print("Error:", str(e))

    print(f"Success: {success_count}/5")

    if success_count == 5:
        sheet.update_cell(i, 2, "Posted")
        print("Marked As Posted")

    break

print("Finished")
