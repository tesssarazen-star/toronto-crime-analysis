 # import libraries
import pandas as pd

# read from data/raw
crime = pd.read_csv("data/raw/neighbourhood-crime-rates - 4326.csv")
homicide = pd.read_csv("data/raw/homicides - 4326.csv")
shooting = pd.read_csv("data/raw/shootings-firearm-discharges - 4326.csv")

crime = crime[[
    "_id",
    "AREA_NAME",
    "HOOD_ID",
    "ASSAULT_2025",
    "ASSAULT_RATE_2025",
    "AUTOTHEFT_2025",
    "AUTOTHEFT_RATE_2025",
    "BREAKENTER_2025",
    "BREAKENTER_RATE_2025",
    "HOMICIDE_2025",
    "HOMICIDE_RATE_2025",
    "ROBBERY_2025",
    "ROBBERY_RATE_2025",
    "SHOOTING_2025",
    "SHOOTING_RATE_2025",
    "THEFTFROMMV_2025",
    "THEFTFROMMV_RATE_2025",
    "THEFTOVER_2025",
    "THEFTOVER_RATE_2025",
    "POPULATION_2025"
    ]].copy(deep=True)

# ------ fill missing homicide values with homicide dataset ---------
homicide = homicide[homicide["OCC_YEAR"] == 2025]

#convert from string to numeric
homicide["HOOD_158"] = pd.to_numeric(
    homicide["HOOD_158"],
    errors="coerce"
).astype("Int64")

homicide = (
    homicide
    .groupby("HOOD_158")
    .size()
    .reset_index(name="HOMICIDE_2025_NEW")
    .rename(columns={"HOOD_158": "HOOD_ID"})
)

update_homicide_crime = crime.merge(
    homicide,
    on="HOOD_ID",
    how="left"
)

# No matching homicide record = 0 homicides
update_homicide_crime["HOMICIDE_2025_NEW"] = (
    update_homicide_crime["HOMICIDE_2025_NEW"]
    .fillna(0)
    .astype(int)
)
# calculate homicide rate per 100,000 population
update_homicide_crime["HOMICIDE_RATE_2025_NEW"] = (
    update_homicide_crime["HOMICIDE_2025_NEW"]
    / update_homicide_crime["POPULATION_2025"]
) * 100000

# ------ fill missing shooting values with shooting-firearm-discharge dataset ---------
shooting = shooting[shooting["OCC_YEAR"] == 2025]

#convert from string to numeric
shooting["HOOD_158"] = pd.to_numeric(
    shooting["HOOD_158"],
    errors="coerce"
).astype("Int64")

shooting = (
    shooting
    .groupby("HOOD_158")
    .size()
    .reset_index(name="SHOOTING_2025_NEW")
    .rename(columns={"HOOD_158": "HOOD_ID"})
)

update_shooting_crime = update_homicide_crime.merge(
    shooting,
    on="HOOD_ID",
    how="left"
)

# No matching shooting record = 0 shootings
update_shooting_crime["SHOOTING_2025_NEW"] = (
    update_shooting_crime["SHOOTING_2025_NEW"]
    .fillna(0)
    .astype(int)
)
# calculate shooting rate per 100,000 population
update_shooting_crime["SHOOTING_RATE_2025_NEW"] = (
    update_shooting_crime["SHOOTING_2025_NEW"]
    / update_shooting_crime["POPULATION_2025"]
) * 100000


# ------ create clean dataframe ---------
clean_crime = update_shooting_crime.copy(deep=True)

# Replace old homicide values
clean_crime["HOMICIDE_2025"] = clean_crime["HOMICIDE_2025_NEW"]
clean_crime["HOMICIDE_RATE_2025"] = clean_crime["HOMICIDE_RATE_2025_NEW"]

# Replace old shooting values
clean_crime["SHOOTING_2025"] = clean_crime["SHOOTING_2025_NEW"]
clean_crime["SHOOTING_RATE_2025"] = clean_crime["SHOOTING_RATE_2025_NEW"]

# Remove temporary columns
clean_crime = clean_crime.drop(
    columns=[
        "HOMICIDE_2025_NEW",
        "HOMICIDE_RATE_2025_NEW",
        "SHOOTING_2025_NEW",
        "SHOOTING_RATE_2025_NEW"
    ]
)

# Data quality checks
assert clean_crime.isna().sum().sum() == 0
assert clean_crime.duplicated().sum() == 0

clean_crime.to_csv(
    "data/processed/clean_crime.csv",
    index=False
)