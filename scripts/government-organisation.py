import json
import os
import csv
import urllib.request
import pandas as pd

# Replaces the government-organisation list with a list scraped from the source below
# follows a tip from https://twitter.com/GidsG/status/1370024709467738123
# merges with the original file as they're not all there

SOURCE_URL = "https://www.gov.uk/api/content/government/organisations"
SOURCE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../government-organisation.csv")

existing_orgs = {}
existing_urls = set()
href_to_key = {}
with open(SOURCE_FILE, encoding="utf8") as c:
    count = 0
    reader = csv.DictReader(c)
    for row in reader:
        existing_orgs[row['key']] = {
            **row,
            "active": row['end-date'] == "",
            "orgtype": [],
            "alternateNames": [],
            "logo_image": "",
        }
        existing_urls.add(row['website'])
        if row['website'].startswith("https://www.gov.uk/"):
            href_to_key[row["website"].replace("https://www.gov.uk/", "/")] = row["key"]
        count += 1
    print(f"{count:,.0f} organisations found in old register")

new_orgs = set()
new_urls = set()
with urllib.request.urlopen(SOURCE_URL) as response:
    data = json.loads(response.read())
    count = 0
    new_orgs = set()
    new_organisations = []
    for orgtype, orgs in data.get("details", {}).items():
        for org in orgs:
            href_to_key[org["href"]] = org["analytics_identifier"]
            new_organisations.append(org)
            count += 1
            new_orgs.add(org["analytics_identifier"])
            new_urls.add("https://www.gov.uk" + org["href"])
    print(f"{count:,.0f} organisations found in new source")

print(f"{len([f for f in new_orgs if f in existing_orgs])} organisations are in both")
print(f"{len([f for f in new_orgs if f not in existing_orgs])} organisations are new source but not in old register")
print(f"{len([f for f in existing_orgs.keys() if f not in new_orgs])} organisations are old register but not in new source")
total_count = len([f for f in existing_orgs.keys() if f not in new_orgs]) + len([f for f in new_orgs if f not in existing_orgs]) + len([f for f in new_orgs if f in existing_orgs])
print(f"{total_count} unique organisations across both datasets")

print()
print("By URL")
print(f"{len([f for f in new_urls if f in existing_urls])} organisations are in both")
print(f"{len([f for f in new_urls if f not in existing_urls])} organisations are new source but not in old register")
print(f"{len([f for f in existing_urls if f not in new_urls])} organisations are old register but not in new source")
total_count = len([f for f in existing_urls if f not in new_urls]) + len([f for f in new_urls if f not in existing_urls]) + len([f for f in new_urls if f in existing_urls])
print(f"{total_count} unique organisations across both datasets")

# for f in new_organisations:
#     if f["analytics_identifier"] in existing_orgs:
#         continue
#     print((
#         f["analytics_identifier"],
#         f["analytics_identifier"],
#         f["title"],
#         "https://www.gov.uk" + f["href"],
#     ))


#             if not org["analytics_identifier"] in existing_orgs:
#                 print("Not in register: {} {}".format(org["analytics_identifier"], org["title"]))
#             # if not org["closed_at"]:
#             #     print(json.dumps(org, indent=4))
#             # print({
#             #     "index-entry-number": "",
#             #     "entry-number": "",
#             #     "entry-timestamp": "",
#             #     "key": org["analytics_identifier"],
#             #     "government-organisation": org["analytics_identifier"],
#             #     "name": org["title"],
#             #     "website": "https://www.gov.uk" + org["href"] if org.get("href") else None,
#             #     "start-date": "",
#             #     "end-date": org.get("closed_at"),
#             # })
#     for key, org in existing_orgs.items():
#         if key not in url_orgs:
#             print("Not on website: {} {}".format(key, org["name"]))

# # for k, v in href_to_key.items():
# #     print(k, v)
