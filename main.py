import duckdb
import pandas as pd
import numpy as np
import re
import unicodedata

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score


# =========================================================
# 1. LOAD EPL STATS
# =========================================================

stats = pd.read_csv("data/epl_player_stats_24_25.csv")

print("EPL players:", len(stats))


# =========================================================
# 2. CONNECT TO TRANSFERMARKT DATABASE
# =========================================================

con = duckdb.connect("data/transfermarkt-datasets.duckdb")


# =========================================================
# 3. GET PLAYER INFORMATION
# =========================================================

players = con.execute("""
    SELECT
        player_id,
        name AS player_name_tm,
        date_of_birth,
        position AS tm_position,
        height_in_cm,
        international_caps,
        international_goals,
        contract_expiration_date
    FROM players
""").fetchdf()


# =========================================================
# 4. GET LATEST EPL MARKET VALUE
# =========================================================

values = con.execute("""
    SELECT
        pv.player_id,
        pv.market_value_in_eur

    FROM player_valuations pv

    WHERE pv.player_club_domestic_competition_id = 'GB1'
      AND pv.date <= '2025-05-30'

    QUALIFY ROW_NUMBER() OVER (
        PARTITION BY pv.player_id
        ORDER BY pv.date DESC
    ) = 1
""").fetchdf()


print("Transfermarkt valuation records:", len(values))


# =========================================================
# 5. CLEAN NAMES
# =========================================================

def clean_name(name):

    name = str(name).lower().strip()

    name = unicodedata.normalize("NFKD", name)

    name = "".join(
        c for c in name
        if not unicodedata.combining(c)
    )

    name = re.sub(
        r"[^a-z0-9\s]",
        "",
        name
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    )

    return name


stats["name_clean"] = (
    stats["Player Name"]
    .apply(clean_name)
)

players["name_clean"] = (
    players["player_name_tm"]
    .apply(clean_name)
)


# =========================================================
# 6. MERGE PLAYER INFORMATION
# =========================================================

player_info = players[
    [
        "player_id",
        "name_clean",
        "date_of_birth",
        "height_in_cm",
        "international_caps",
        "international_goals",
        "contract_expiration_date"
    ]
].drop_duplicates(
    subset=["name_clean"]
)


df = stats.merge(
    player_info,
    on="name_clean",
    how="left"
)


# =========================================================
# 7. MERGE MARKET VALUE
# =========================================================

df = df.merge(
    values,
    on="player_id",
    how="left"
)


# =========================================================
# 8. AGE
# =========================================================

df["date_of_birth"] = pd.to_datetime(
    df["date_of_birth"],
    errors="coerce"
)

df["age"] = (
    pd.Timestamp("2025-05-30")
    - df["date_of_birth"]
).dt.days / 365.25


# =========================================================
# 9. CONTRACT YEARS REMAINING
# =========================================================

df["contract_expiration_date"] = pd.to_datetime(
    df["contract_expiration_date"],
    errors="coerce"
)

df["contract_years_remaining"] = (
    (
        df["contract_expiration_date"]
        - pd.Timestamp("2025-05-30")
    ).dt.days / 365.25
)

df["contract_years_remaining"] = (
    df["contract_years_remaining"]
    .clip(lower=0)
)


# =========================================================
# 10. CONVERT PERCENTAGES
# =========================================================

percentage_columns = [
    "Conversion %",
    "Passes%",
    "Crosses %",
    "fThird Passes %",
    "gDuels %",
    "aDuels %",
    "Saves %"
]

for col in percentage_columns:

    if col in df.columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.replace("%", "", regex=False)
        )

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# =========================================================
# 11. KEEP PLAYERS WITH MARKET VALUE
# =========================================================

df = df.dropna(
    subset=["market_value_in_eur"]
).copy()

df = df[
    df["market_value_in_eur"] > 0
].copy()

print(
    "Players with market value:",
    len(df)
)


# =========================================================
# 12. POSITION PERFORMANCE FEATURES
# =========================================================

# ATTACK

df["Attack_Score"] = (
    df["Goals"] * 5
    + df["Assists"] * 4
    + df["Shots"] * 0.20
    + df["Shots On Target"] * 0.30
    + df["Carries Ended with Goal"] * 3
    + df["Carries Ended with Assist"] * 3
)


# MIDFIELD

df["Midfield_Score"] = (
    df["Assists"] * 4
    + df["Progressive Carries"] * 0.20
    + df["Carries Ended with Chance"] * 2
    + df["Successful Passes"] * 0.05
    + df["Tackles"] * 0.30
    + df["Interceptions"] * 0.30
    + df["Possession Won"] * 0.10
)


# DEFENCE

df["Defensive_Score"] = (
    df["Tackles"] * 0.50
    + df["Interceptions"] * 0.60
    + df["Clearances"] * 0.20
    + df["Blocks"] * 0.50
    + df["Ground Duels"] * 0.20
    + df["Aerial Duels"] * 0.30
    + df["Clean Sheets"] * 2
)


# GOALKEEPING

df["Goalkeeper_Score"] = (
    df["Saves"] * 0.50
    + df["Clean Sheets"] * 3
    + df["Goals Prevented"] * 5
    + df["Penalties Saved"] * 4
    + df["High Claims"] * 0.20
    + df["Punches"] * 0.20
)


# =========================================================
# 13. POSITION-AWARE PERFORMANCE SCORE
# =========================================================

def position_score(row):

    position = str(row["Position"]).upper()

    if position == "GKP":
        return row["Goalkeeper_Score"]

    elif position == "DEF":
        return row["Defensive_Score"]

    elif position == "MID":
        return row["Midfield_Score"]

    elif position == "FWD":
        return row["Attack_Score"]

    return 0


df["Position_Performance_Score"] = (
    df.apply(position_score, axis=1)
)


# =========================================================
# 14. FEATURES
# =========================================================

features = [

    "age",
    "height_in_cm",

    "international_caps",
    "international_goals",

    "contract_years_remaining",

    "Position_Performance_Score",

    "Goals",
    "Assists",

    "Shots",
    "Shots On Target",
    "Conversion %",

    "Touches",
    "Carries",
    "Progressive Carries",

    "Carries Ended with Goal",
    "Carries Ended with Assist",
    "Carries Ended with Shot",
    "Carries Ended with Chance",

    "Passes",
    "Successful Passes",
    "Passes%",
    "Through Balls",

    "Tackles",
    "Interceptions",
    "Clearances",
    "Blocks",

    "Ground Duels",
    "gDuels %",

    "Aerial Duels",
    "aDuels %",

    "Fouls",
    "Yellow Cards",
    "Red Cards",

    "Saves",
    "Saves %",
    "Penalties Saved",

    "High Claims",
    "Punches",
    "Goals Prevented",

    "Appearances",
    "Minutes",
    "Clean Sheets"
]


features = [
    col for col in features
    if col in df.columns
]


categorical_features = [
    "Position"
]


# =========================================================
# 15. X AND Y
# =========================================================

X = df[
    features + categorical_features
]


# IMPORTANT:
# LOG TRANSFORMATION OF MARKET VALUE

y = np.log1p(
    df["market_value_in_eur"]
)


# =========================================================
# 16. TRAIN / TEST SPLIT
# =========================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\n==============================")
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
# 17. PREPROCESSING
# =========================================================

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        )
    ]
)


categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),

        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


preprocessor = ColumnTransformer(
    transformers=[

        (
            "numeric",
            numeric_pipeline,
            features
        ),

        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ]
)


# =========================================================
# 18. RANDOM FOREST
# =========================================================

model = RandomForestRegressor(

    n_estimators=500,

    max_depth=12,

    min_samples_leaf=2,

    random_state=42,

    n_jobs=-1
)


pipeline = Pipeline(
    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            model
        )
    ]
)


# =========================================================
# 19. TRAIN
# =========================================================

pipeline.fit(
    X_train,
    y_train
)


print(
    "\nModel trained successfully!"
)


# =========================================================
# 20. PREDICT LOG VALUE
# =========================================================

predicted_log = pipeline.predict(
    X_test
)


# Convert back to EUR

predicted_value = np.expm1(
    predicted_log
)


actual_value = np.expm1(
    y_test
)


# =========================================================
# 21. MODEL PERFORMANCE
# =========================================================

mae = mean_absolute_error(
    actual_value,
    predicted_value
)

r2 = r2_score(
    actual_value,
    predicted_value
)


print("\n==============================")
print("FINAL LOG-TRANSFORMED MODEL")
print("==============================")

print(
    f"MAE: €{mae:,.0f}"
)

print(
    f"R² Score: {r2:.3f}"
)


# =========================================================
# 22. FEATURE IMPORTANCE
# =========================================================

rf = pipeline.named_steps["model"]


encoded_position_names = (
    pipeline
    .named_steps["preprocessor"]
    .named_transformers_["categorical"]
    .named_steps["onehot"]
    .get_feature_names_out(
        categorical_features
    )
)


feature_names = (
    features
    + list(encoded_position_names)
)


importance = pd.DataFrame({

    "Feature": feature_names,

    "Importance": rf.feature_importances_

})


importance = importance.sort_values(
    "Importance",
    ascending=False
)


print("\n==============================")
print("FEATURE IMPORTANCE")
print("==============================")


print(
    importance
    .head(25)
    .to_string(index=False)
)


# =========================================================
# 23. RESULTS DATAFRAME
# =========================================================

results = df.loc[
    X_test.index,
    [
        "Player Name",
        "Club",
        "Position",
        "age"
    ]
].copy()


results["Actual Value"] = (
    actual_value
)

results["Predicted Value"] = (
    predicted_value
)


# =========================================================
# 24. VALUE GAP
# =========================================================

results["Value Gap"] = (
    results["Predicted Value"]
    - results["Actual Value"]
)


results["Value Gap %"] = (
    results["Value Gap"]
    / results["Actual Value"]
) * 100


# =========================================================
# 25. FILTER EXTREME OUTLIERS
# =========================================================

# We don't want tiny market values producing
# ridiculous percentages.

results["Reliable Gap"] = (
    results["Actual Value"] >= 5_000_000
)


# =========================================================
# 26. TRANSFER OPPORTUNITY SCORE
# =========================================================

results["Transfer Opportunity Score"] = (
    results["Value Gap %"]
    .clip(-100, 100)
)


# =========================================================
# 27. UNDERVALUED
# =========================================================

undervalued = results[
    results["Reliable Gap"]
].sort_values(
    "Value Gap %",
    ascending=False
)


print("\n==============================")
print("TOP POTENTIALLY UNDERVALUED")
print("==============================")


display_under = undervalued.head(15).copy()


display_under["Actual Value"] = (
    display_under["Actual Value"]
    .apply(lambda x: f"€{x:,.0f}")
)

display_under["Predicted Value"] = (
    display_under["Predicted Value"]
    .apply(lambda x: f"€{x:,.0f}")
)

display_under["Value Gap"] = (
    display_under["Value Gap"]
    .apply(lambda x: f"€{x:,.0f}")
)

display_under["Value Gap %"] = (
    display_under["Value Gap %"]
    .apply(lambda x: f"{x:.1f}%")
)


print(
    display_under[
        [
            "Player Name",
            "Club",
            "Position",
            "Actual Value",
            "Predicted Value",
            "Value Gap",
            "Value Gap %"
        ]
    ].to_string(index=False)
)


# =========================================================
# 28. OVERVALUED
# =========================================================

overvalued = results[
    results["Reliable Gap"]
].sort_values(
    "Value Gap %",
    ascending=True
)


print("\n==============================")
print("TOP POTENTIALLY OVERVALUED")
print("==============================")


display_over = overvalued.head(15).copy()


display_over["Actual Value"] = (
    display_over["Actual Value"]
    .apply(lambda x: f"€{x:,.0f}")
)

display_over["Predicted Value"] = (
    display_over["Predicted Value"]
    .apply(lambda x: f"€{x:,.0f}")
)

display_over["Value Gap"] = (
    display_over["Value Gap"]
    .apply(lambda x: f"€{x:,.0f}")
)

display_over["Value Gap %"] = (
    display_over["Value Gap %"]
    .apply(lambda x: f"{x:.1f}%")
)


print(
    display_over[
        [
            "Player Name",
            "Club",
            "Position",
            "Actual Value",
            "Predicted Value",
            "Value Gap",
            "Value Gap %"
        ]
    ].to_string(index=False)
)


# =========================================================
# 29. SAVE FINAL DATA
# =========================================================

results.to_csv(
    "data/final_valuation_predictions.csv",
    index=False
)


importance.to_csv(
    "data/final_feature_importance.csv",
    index=False
)


df.to_csv(
    "data/final_valuation_dataset.csv",
    index=False
)


# =========================================================
# 30. SAVE TRANSFER SHORTLIST
# =========================================================

undervalued.to_csv(
    "data/transfer_opportunities.csv",
    index=False
)


# =========================================================
# 31. FINISHED
# =========================================================

print("\n==============================")
print("FILES SAVED")
print("==============================")

print(
    "✓ data/final_valuation_predictions.csv"
)

print(
    "✓ data/final_feature_importance.csv"
)

print(
    "✓ data/final_valuation_dataset.csv"
)

print(
    "✓ data/transfer_opportunities.csv"
)

print("\nFINAL VALUATION MODEL COMPLETE! ⚽📊")