import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv("data/final_player_value_dataset.csv")

print("EPL players:", len(df))


# =========================================================
# STANDARDIZE IMPORTANT COLUMNS
# =========================================================

# Your dataset uses these columns:
# Player Name
# Club
# Position

# Make sure they exist
required_identity_columns = [
    "Player Name",
    "Club",
    "Position"
]

for col in required_identity_columns:
    if col not in df.columns:
        raise ValueError(
            f"Required column '{col}' not found. "
            f"Available columns: {list(df.columns)}"
        )


# =========================================================
# MARKET VALUE
# =========================================================

df["market_value_in_eur"] = pd.to_numeric(
    df["market_value_in_eur"],
    errors="coerce"
)

known = df[
    df["market_value_in_eur"].notna()
].copy()

print("Players with market value:", len(known))
print(
    "Players without market value:",
    len(df) - len(known)
)


# =========================================================
# FEATURES
# =========================================================

features = [
    "age",
    "height_in_cm",
    "international_caps",
    "international_goals",

    "Appearances",
    "Minutes",

    "Goals",
    "Assists",
    "Shots",
    "Shots On Target",

    "Touches",

    "Passes",
    "Successful Passes",
    "Passes%",

    "Ground Duels",
    "gDuels Won",
    "gDuels %",

    "Aerial Duels",
    "aDuels Won",
    "aDuels %",

    "Tackles",
    "Interceptions",

    "Progressive Carries",
    "Carries",
    "Possession Won",

    "Clean Sheets",
    "Clearances",
    "Blocks",

    "Carries Ended with Chance",

    "Conversion %",
    "Through Balls",
    "Crosses",
    "Successful Crosses",

    "Fouls",
    "Yellow Cards",
    "Red Cards",

    "Offsides",
    "Big Chances Missed",
    "Hit Woodwork"
]


# =========================================================
# ONLY USE FEATURES THAT EXIST
# =========================================================

features = [
    feature
    for feature in features
    if feature in df.columns
]

print()
print("Features used:")
print(features)


# =========================================================
# PREPARE TRAINING DATA
# =========================================================

X = known[features].copy()

y = known["market_value_in_eur"].copy()


# Convert everything to numeric
for col in X.columns:
    X[col] = pd.to_numeric(
        X[col],
        errors="coerce"
    )


# Missing statistics = 0
X = X.fillna(0)


# =========================================================
# TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print()
print("==============================")
print("TRAIN / TEST")
print("==============================")

print(
    "Training players:",
    len(X_train)
)

print(
    "Testing players:",
    len(X_test)
)


# =========================================================
# RANDOM FOREST
# =========================================================

model = RandomForestRegressor(
    n_estimators=500,
    max_depth=12,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)


model.fit(
    X_train,
    y_train
)

print()
print("Model trained successfully!")


# =========================================================
# MODEL PERFORMANCE
# =========================================================

test_predictions = model.predict(
    X_test
)


mae = mean_absolute_error(
    y_test,
    test_predictions
)

r2 = r2_score(
    y_test,
    test_predictions
)


print()
print("==============================")
print("MODEL PERFORMANCE")
print("==============================")

print(
    f"MAE: €{mae:,.0f}"
)

print(
    f"R² Score: {r2:.3f}"
)


# =========================================================
# PREDICT ALL EPL PLAYERS
# =========================================================

all_X = df[features].copy()


for col in all_X.columns:
    all_X[col] = pd.to_numeric(
        all_X[col],
        errors="coerce"
    )


all_X = all_X.fillna(0)


all_predictions = model.predict(
    all_X
)


df["ML Estimated Value"] = (
    all_predictions
)


# =========================================================
# FINAL VALUATION
# =========================================================

# If Transfermarkt value exists,
# use it as the actual valuation.
#
# If it doesn't exist,
# use our ML prediction.

df["Final Valuation"] = np.where(
    df["market_value_in_eur"].notna(),
    df["market_value_in_eur"],
    df["ML Estimated Value"]
)


# =========================================================
# VALUATION TYPE
# =========================================================

df["Valuation Type"] = np.where(
    df["market_value_in_eur"].notna(),
    "Transfermarkt",
    "ML Estimated"
)


# =========================================================
# ROUND VALUES
# =========================================================

df["ML Estimated Value"] = (
    df["ML Estimated Value"]
    .round(-3)
)

df["Final Valuation"] = (
    df["Final Valuation"]
    .round(-3)
)


# =========================================================
# CREATE FINAL RESULT
# =========================================================

result_columns = [
    "Player Name",
    "Club",
    "Position",

    "market_value_in_eur",

    "ML Estimated Value",

    "Final Valuation",

    "Valuation Type"
]


# Make sure every required column exists
for col in result_columns:

    if col not in df.columns:

        raise ValueError(
            f"Column '{col}' missing from dataset."
        )


result = df[
    result_columns
].copy()


# =========================================================
# REMOVE DUPLICATE PLAYERS
# =========================================================

# Keep one row per player + club

result = result.drop_duplicates(
    subset=[
        "Player Name",
        "Club"
    ],
    keep="first"
)


# =========================================================
# SORT BY CLUB AND PLAYER
# =========================================================

result = result.sort_values(
    by=[
        "Club",
        "Player Name"
    ]
).reset_index(drop=True)


# =========================================================
# DISPLAY
# =========================================================

print()
print("==============================")
print("ALL EPL PLAYER VALUATIONS")
print("==============================")

print(
    "Total players:",
    len(result)
)

print()

print(
    result.head(20).to_string(
        index=False
    )
)


# =========================================================
# CHECK CLUB COUNTS
# =========================================================

print()
print("==============================")
print("PLAYERS PER CLUB")
print("==============================")

club_counts = (
    result
    .groupby("Club")
    .size()
    .sort_values(
        ascending=False
    )
)

print(club_counts.to_string())


# =========================================================
# ML ESTIMATED PLAYERS
# =========================================================

missing = result[
    result["Valuation Type"] == "ML Estimated"
].copy()


print()
print("==============================")
print("ML ESTIMATED PLAYERS")
print("==============================")

print(
    "ML estimated players:",
    len(missing)
)


# =========================================================
# SAVE FINAL CSV
# =========================================================

output_file = (
    "data/all_epl_player_valuations.csv"
)


result.to_csv(
    output_file,
    index=False
)


# =========================================================
# VERIFY SAVED FILE
# =========================================================

check = pd.read_csv(
    output_file
)


print()
print("==============================")
print("FILES SAVED")
print("==============================")

print(
    f"✓ {output_file}"
)

print()
print(
    "Rows saved:",
    len(check)
)

print()
print("Columns saved:")

for col in check.columns:
    print(
        "✓",
        col
    )


# =========================================================
# FINAL CHECK
# =========================================================

print()
print("==============================")
print("FINAL CHECK")
print("==============================")

print(
    "Players in final CSV:",
    len(check)
)

print(
    "Unique players:",
    check["Player Name"].nunique()
)

print(
    "Unique clubs:",
    check["Club"].nunique()
)

print()

print(
    "ALL EPL PLAYERS NOW HAVE A VALUATION! ⚽📊"
)