import pandas as pd
import requests
import csv

pd.options.mode.chained_assignment = None

SOURCE_URL = "https://www.gov.uk/api/content/government/organisations"
REGISTER = "./government-organisation.csv"

# fetch existing register
register = pd.read_csv(REGISTER).sort_values("index-entry-number")
print(f"{len(register):,.0f} organisations found in current register")

# fetch new data from gov.uk api
r = requests.get(SOURCE_URL)
r.json()

new_organisations = []
for orgtype, orgs in r.json().get("details", {}).items():
    for org in orgs:
        new_organisations.append({
            "orgtype": orgtype,
            **org
        })

new_orgs = pd.json_normalize(new_organisations)
print(f"{len(new_orgs):,.0f} organisations found in new source")

# turn gov.uk data into register format 
register_new = pd.DataFrame({
    "index-entry-number": None,
    "entry-number": None,
    "entry-timestamp": None,
    "key": new_orgs["analytics_identifier"],
    "government-organisation": new_orgs["analytics_identifier"],
    "name": new_orgs["title"],
    "website": new_orgs["href"].apply(lambda x: "https://www.gov.uk" + x if x else None),
    "start-date": None,
    "end-date": None,
}, index=new_orgs.index)

# get the organisations we're going to add
register_to_add = register_new[~register_new["key"].isin(register["key"])]
register_to_add.loc[:, "index-entry-number"] = register["index-entry-number"].max() + 1 + register_to_add.reset_index().index
register_to_add.loc[:, "entry-number"] = register_to_add["index-entry-number"]
register_to_add.loc[:, "entry-timestamp"] = pd.Timestamp.now()

# merge the old and new register
register_merged = pd.concat([
    register,
    register_to_add,
], ignore_index=True).sort_values("index-entry-number", ascending=False)


print(f"{len(register_new['key'].isin(register['key']))} organisations are in both")
# print(f"{len([f for f in new_orgs if f not in existing_orgs])} organisations are new source but not in old register")
# print(f"{len([f for f in existing_orgs.keys() if f not in new_orgs])} organisations are old register but not in new source")
print(f"{len(register_merged):,.0f} unique organisations across both datasets")


# save to CSV file
register_merged.to_csv(
    REGISTER,
    index=False,
    quoting=csv.QUOTE_MINIMAL,
)
