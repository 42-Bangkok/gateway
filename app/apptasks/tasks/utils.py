"""
https://medium.com/craftsmenltd/from-csv-to-google-sheet-using-python-ef097cb014f9
NOTE:
service_account_from_dict
"""

import gspread
import gspread_dataframe as gd
from rich.console import Console
from datetime import datetime

console = Console()


def human_time() -> str:

    return datetime.today().strftime("%Y-%m-%dT%H:%M")


def upload2gsheet(
    df, sheet_name, worksheet_name, oauth=False, service_account_file=None
):
    console.log(f"Uploading to Google Sheet {sheet_name}...")
    if oauth is False:
        gc = gspread.service_account(
            filename=service_account_file
        )  # user service_account, folder/file must be shared to this service account
    elif oauth is True:
        gc = gspread.oauth()  # use OAuth
    try:
        sheet = gc.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        sheet = gc.create(sheet_name)
    # Handle this
    # APIError: {'code': 400, 'message': 'Invalid requests[0].addSheet: A sheet with the name "2021-12-10T20:08" already exists. Please enter another name.', 'status': 'INVALID_ARGUMENT'}
    worksheet = sheet.add_worksheet(title=worksheet_name, rows="10", cols="10")
    gd.set_with_dataframe(worksheet, df.astype(str))
    console.log("Done!")


def upload2gsheet_static(df, sheet_name, oauth=False, service_account_file=None):
    console.log(f"Uploading to Google Sheet {sheet_name}...")
    if oauth is False:
        gc = gspread.service_account(
            filename=service_account_file
        )  # user service_account, folder/file must be shared to this service account
    elif oauth is True:
        gc = gspread.oauth()  # use OAuth
    try:
        sheet = gc.open(sheet_name)
    except gspread.SpreadsheetNotFound:
        sheet = gc.create(sheet_name)

    worksheet = sheet.get_worksheet(0)
    worksheet.clear()
    worksheet.update_title(human_time())
    gd.set_with_dataframe(worksheet, df.astype(str))
    console.log("Done!")
