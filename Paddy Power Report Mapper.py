"""
Paddy Power Report Formatter
---------------------------------------------------------------------------------------------

This script:
  • Takes audits_basic_data_export.csv via Streamlit upload
  • Generates two downloadable CSVs:
       - Paddy Power GB Visits.csv
       - Paddy Power IE Visits.csv
  • Output encoding: UTF-8-BOM
"""

import re
import pandas as pd
import streamlit as st
import io
from typing import Dict, Optional


# ============================================================
# Country classification
# ============================================================

eircode_pattern = re.compile(r"^[A-Z]\d{2}\s?[A-Z0-9]{4}$")
gb_postcode_pattern = re.compile(r"^(?!BT)[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$")


def classify_country(postcode: str) -> str:
    if not postcode or postcode.strip() == "":
        return "IE"
    pc = postcode.strip().upper().replace("  ", " ")
    if pc.startswith("BT"):
        return "IE"
    if eircode_pattern.match(pc):
        return "IE"
    if gb_postcode_pattern.match(pc):
        return "GB"
    return "IE"


# ============================================================
# GB MAPPING
# ============================================================

gb_mapping: Dict[str, Optional[str]] = {
    'Order Number': 'order_internal_id',
    'Client Name': 'client_name',
    'Audit ID': 'internal_id',
    'Site ID': 'site_internal_id',
    'Order Deadline': 'end_date',
    'Responsibility': 'responsibility',
    'Premises Name': 'site_name',
    'Address1': 'site_address_1',
    'Address2': 'site_address_2',
    'Address3': 'site_address_3',
    'Post Code': 'site_post_code',
    'Submitted Date': 'submitted_date',
    'Approved Date': 'approval_date',
    'Item To Order': 'item_to_order',
    'Actual Visit Date': 'date_of_visit',
    'Actual Visit Time': 'time_of_visit',
    'AMPM': None,
    'Pass-Fail': 'primary_result',
    'Pass-Fail2': 'secondary_result',
    'Abort Reason': 'Please detail why you were unable to conduct this audit:',
    'Extra Site 1': 'site_code',
    'Extra Site 2': None,
    'Extra Site 3': None,
    'Extra Site 4': 'Were you challenged for ID on entry, at the machine, after machine play, or at the counter?',
    'Till ID?': None,
    'VISITORSEX': None,
    'ON ENTRY / BROWSING': 'What was the time when you entered the shop?',
    'As you entered the shop was eye contact made by a member of staff?': 'As you entered the shop was eye contact made by a member of staff?',
    'Were you acknowledged by any staff members?': 'Were you acknowledged by any staff members?',
    'Were you challenged for ID on entry, at the machine or after machine play? (Please indicate below at which point of your visit you were challenged):': 'Were you challenged for ID on entry, at the machine, after machine play, or at the counter?',
    'Were you asked for ID before or after you put a coin into the machine?': 'Were you asked for ID before or after you put a coin into the machine?',
    'Please accurately describe the staff member who asked you for ID at one of these points:': 'Please accurately describe the staff member who asked you for ID at one of these points:',
    'Was the staff member wearing a name badge?': 'Was the staff member wearing a name badge?',
    'Was the member of staff wearing a (black) Paddy Power uniform?': 'What was the name of the staff member?',
    'Please describe the manner in which you were challenged and add any other comments you feel are relevant:': 'Please describe the manner in which you were challenged and add any other comments you feel are relevant:',
    'MACHINE AREA': None,
    'Did all the gaming machines appear to be working?': 'Did all the gaming machines appear to be working?',
    'Were all the machines visible from the counter?': 'Were all the machines visible from the counter?',
    'Please describe what the staff member was doing as you approached the counter:': 'Please describe what the staff member was doing as you approached the counter:',
    'Did the staff member who served you make eye contact with you during the transaction?': 'Did the staff member who served you make eye contact with you during the transaction?',
    'When was eye contact first made?': 'When was eye contact first made?',
    'Were "Think 21" signs visible in the machine area?': None,
    'PLACING THE BET': None,
    'Please describe what the server was doing as you approached the counter (e.g. serving a customer, talking to colleagues):': None,
    'At the till, did the person who served you ask your age?': None,
    'Did the staff member who served you at the till ask for ID?': None,
    'Please enter the 17 digit number from your betting slip:': 'Please enter the 17 digit number from your betting slip:',
    'Unnamed: 47': None,
    'How many staff were visible in the shop at the time of your visit?': 'How many staff were visible in the shop at the time of your visit?',
    'When were the staff first aware of you in the shop?': 'When were the staff first aware of you in the shop?',
    'How many customers were in the shop at the time of your audit?': 'How many customers were in the shop at the time of your audit?',
    "Did you see any 'Think 21' posters in the shop?": "Did you see any 'Think 25' posters in the shop?",
    "Did you see any 'Think 21' posters behind the counter?": "Did you see any 'Think 25' posters behind the counter?",
    'Please give a detailed report of your audit, providing a full description of your experience from entering to leaving the shop:': 'Please give a detailed report of your audit, providing a full description of your experience from entering to leaving the shop:',
    'What time did you leave the shop?': 'What time did you leave the shop?',
    'Were you wearing a face mask/covering during the audit?': None,
    'Please confirm in the space below whether or not you were asked for ID:': None,
    'Unnamed: 57': None,
    'Unnamed: 58': 'Please confirm below whether or not you were asked for ID:',
    'Unnamed: 59': None,
    'Unnamed: 60': None,
    'Unnamed: 61': None,
    'Unnamed: 62': 'Please confirm below whether or not you were asked for ID:',
}

# ============================================================
# IE MAPPING
# ============================================================

ie_mapping: Dict[str, Optional[str]] = {
    'Order Number': 'order_internal_id',
    'Client Name': 'client_name',
    'Audit ID': 'internal_id',
    'Site ID': 'site_internal_id',
    'Order End Date': 'end_date',
    'Responsibility': 'responsibility',
    'Site Name': 'site_name',
    'Address 1': 'site_address_1',
    'Address 2': 'site_address_2',
    'Address 3': 'site_address_3',
    'Post Code': 'site_post_code',
    'Submitted Date': 'submitted_date',
    'Approved Date': 'approval_date',
    'Item To Order': 'item_to_order',
    'Date of Visit': 'date_of_visit',
    'Actual Visit Time': 'time_of_visit',
    'AMPM': None,
    'Pass-Fail': 'primary_result',
    'Pass-Fail2': 'secondary_result',
    'Abort Reason': 'Please detail why you were unable to conduct this audit:',
    'Extra Site 1': 'site_code',
    'Unnamed: 21': None,
    'Unnamed: 22': None,
    'Were you challenged for ID on entry, at the machine, after machine play, or at the counter?': 'Were you challenged for ID on entry, at the machine, after machine play, or at the counter?',
    'Unnamed: 24': None,
    'Unnamed: 25': None,
    'Unnamed: 26': None,
    'What was the time when you entered the shop?': 'What was the time when you entered the shop?',
    'As you entered the shop was eye contact made by a member of staff?': 'As you entered the shop was eye contact made by a member of staff?',
    'Were you acknowledged by any staff members?': 'Were you acknowledged by any staff members?',
    'Please describe any acknowledgement by staff members:': 'Please describe any acknowledgement by staff members:',
    'Please explain what may have prevented staff from greeting you:': 'Please explain what may have prevented staff from greeting you:',
    'If so, what was their name?': 'Were you challenged for ID on entry, at the machine, after machine play, or at the counter?',
    'Was the member of staff wearing a (black) Paddy Power uniform?': 'Were you asked for ID before or after you put a coin into the machine?',
    'Please describe the manner in which you were challenged and add any other comments you feel are relevant:': 'Please describe the manner in which you were challenged and add any other comments you feel are relevant:',
    'Did the staff member appear to record any of the details from your ID?': 'Did the staff member appear to record any of the details from your ID?',
    'Please accurately describe the staff member who asked you for ID at one of these points:': 'Please accurately describe the staff member who asked you for ID at one of these points:',
    'If not, please state why:': 'Was the staff member who served you wearing a name badge?',
    'Did all the gaming machines appear to be working?': 'As required, did you browse for 2 minutes, including time at the self-service machine?',
    'Were all the machines visible from the counter?': 'Please explain why you did not browse for 2 minutes:',
    'Please describe what the staff member was doing as you approached the counter:': 'Please describe what the staff member was doing as you approached the counter:',
    'Did the staff member who served you make eye contact with you?': 'Did the staff member who served you make eye contact with you?',
    'When was eye contact first made?': 'When was eye contact first made?',
    'Please accurately describe the staff member who served you:': 'Please accurately describe the staff member who served you:',
    'Did the staff member who served you smile?': 'Did the staff member who served you smile?',
    'Did the staff member who served you greet you?': 'Did the staff member who served you greet you?',
    'Was the staff member who served you wearing a name badge?': 'Was the staff member who served you wearing a name badge?',
    'What was the name of the staff member who served you?': 'What was the name of the staff member who served you?',
    'Please enter the 17 digit number from the bottom of your betting slip:': 'Please enter the 17 digit number from the bottom of your betting slip:',
    'How many staff were on duty in the shop at the time of your audit?': 'How many staff were on duty in the shop at the time of your audit?',
    'Was the staff member wearing a shirt and tie or a shirt and cravat, as shown in the briefing document?': 'Was the staff member wearing a shirt and tie or a shirt and cravat, as shown in the briefing document?',
    'Describe what the staff member was wearing:': 'Describe what the staff member was wearing:',
    'When were the staff first aware of you in the shop?': 'When were the staff first aware of you in the shop?',
    'How many customers were in the shop at the time of your audit?': 'How many customers were in the shop at the time of your audit?',
    "Did you see any 'Think 21' signage on the front door of the shop?": "Did you see any 'Think 21' signage on the front door of the shop?",
    "Did you see any 'Think 21' posters in the shop?": "Did you see any 'Think 21' posters in the shop?",
    "Did you see any 'Think 21' behind the counter?": "Did you see any 'Think 21' behind the counter?",
    'Please give a detailed report of your audit, providing a full description of your experience from entering to leaving the shop:': 'Please give a detailed report of your audit, providing a full description of your experience from entering to leaving the shop:',
    'Unnamed: 58': "Please rate your overall customer service experience between 1-5 (where 1 is poor and 5 is excellent):",
    "Please rate your overall customer service experience between 1-5 (where 1 is poor and 5 is excellent):": "What time did you leave the shop?",
    'Were you wearing a face mask/covering during the audit?': None,
    'Were you asked to remove your mask/covering during the audit?': None,
    'Please use this space to explain anything unusual about your visit or to clarify any detail of your report:': 'Please use this space to explain anything unusual about your visit or to clarify any detail of your report:',
    'As required, did you browse for 2 minutes, including time at the self-service machine?': 'As required, did you browse for 2 minutes, including time at the self-service machine?',
    'Please explain why you did not browse for 2 minutes:': 'Please explain why you did not browse for 2 minutes:',
    'Please confirm below whether or not you were asked for ID:': 'Please confirm below whether or not you were asked for ID:',
}


# ============================================================
# Output builder
# ============================================================

def build_report(df_in: pd.DataFrame, mapping: Dict[str, Optional[str]], out_file: str) -> pd.DataFrame:
    out = pd.DataFrame()

    # Build output columns
    for report_col, export_col in mapping.items():
        if export_col and export_col in df_in.columns:
            out[report_col] = df_in[export_col]
        else:
            out[report_col] = ""

    # ------------------------------------------------------------
    # Replace "Invalid date" with blank in specific output columns
    # ------------------------------------------------------------
    def col_index(letter):
        idx = 0
        for c in letter:
            idx = idx * 26 + (ord(c) - 64)
        return idx - 1

    if "GB" in out_file:
        target_cols = ["AA", "BC"]
    else:
        target_cols = ["AB", "BH"]

    for letter in target_cols:
        idx = col_index(letter)
        if 0 <= idx < len(out.columns):
            out.iloc[:, idx] = out.iloc[:, idx].replace("Invalid date", "")

    # ------------------------------------------------------------
    # Clean headers: convert "Unnamed:" to empty header ""
    # ------------------------------------------------------------
    cleaned_headers = []
    for h in out.columns:
        if isinstance(h, str) and h.startswith("Unnamed:"):
            cleaned_headers.append("")
        else:
            cleaned_headers.append(h)
    out.columns = cleaned_headers

    return out


# ============================================================
# Streamlit UI and processing
# ============================================================

st.title("Paddy Power Report Mapper")

st.write("""
          1. Export the previous month's data
          2. Drop the file in the below box, it should then give you the output files in your downloads
          3. Standard bits - paste over new data
          4. Copy and paste over values etc!!!
          5. Done.
          """)

uploaded = st.file_uploader("Upload audits_basic_data_export.csv", type=["csv"])

if uploaded:
    # Load source data
    df = pd.read_csv(uploaded, dtype=str).fillna("")

    # Classify country
    df["country_code"] = df["site_post_code"].apply(classify_country)

    df_gb = df[df["country_code"] == "GB"].copy()
    df_ie = df[df["country_code"] == "IE"].copy()

    # Build reports
    gb_out = build_report(df_gb, gb_mapping, "GB")
    ie_out = build_report(df_ie, ie_mapping, "IE")

    # Prepare GB CSV
    gb_buffer = io.BytesIO()
    gb_out.to_csv(gb_buffer, index=False, encoding="utf-8-sig")
    gb_buffer.seek(0)

    # Prepare IE CSV
    ie_buffer = io.BytesIO()
    ie_out.to_csv(ie_buffer, index=False, encoding="utf-8-sig")
    ie_buffer.seek(0)

    st.success("Reports generated successfully!")

    st.download_button(
        label="Download Paddy Power GB Visits.csv",
        data=gb_buffer.getvalue(),
        file_name="Paddy Power GB Visits.csv",
        mime="text/csv",
    )

    st.download_button(
        label="Download Paddy Power IE Visits.csv",
        data=ie_buffer.getvalue(),
        file_name="Paddy Power IE Visits.csv",
        mime="text/csv",
    )
