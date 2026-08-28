import pandas as pd
import matplotlib.pyplot as plt

# Load predictions
df = pd.read_csv("data/final_valuation_predictions.csv")

# =====================================================
# 1. TRANSFER OPPORTUNITY SCORE
# =====================================================

df["Transfer Opportunity Score"] = (
    df["Value Gap %"]
    .clip(-100, 100)
)

# Save
df.to_csv(
    "data/final_transfer_opportunities.csv",
    index=False
)


# =====================================================
# 2. TOP UNDERVALUED
# =====================================================

under = df[
    df["Actual Value"] >= 5_000_000
].sort_values(
    "Value Gap %",
    ascending=False
).head(10)

plt.figure(figsize=(10, 6))

plt.barh(
    under["Player Name"],
    under["Value Gap %"]
)

plt.xlabel("Predicted Value Gap (%)")
plt.title("Top Potentially Undervalued EPL Players")
plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig(
    "data/top_undervalued.png",
    dpi=300
)

plt.show()


# =====================================================
# 3. TOP OVERVALUED
# =====================================================

over = df[
    df["Actual Value"] >= 5_000_000
].sort_values(
    "Value Gap %"
).head(10)

plt.figure(figsize=(10, 6))

plt.barh(
    over["Player Name"],
    over["Value Gap %"]
)

plt.xlabel("Predicted Value Gap (%)")
plt.title("Top Potentially Overvalued EPL Players")
plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig(
    "data/top_overvalued.png",
    dpi=300
)

plt.show()


# =====================================================
# 4. ACTUAL VS PREDICTED
# =====================================================

plt.figure(figsize=(8, 8))

plt.scatter(
    df["Actual Value"],
    df["Predicted Value"],
    alpha=0.6
)

plt.xlabel("Actual Market Value (€)")
plt.ylabel("Predicted Market Value (€)")

plt.title(
    "Actual vs Predicted Player Market Value"
)

plt.tight_layout()

plt.savefig(
    "data/actual_vs_predicted.png",
    dpi=300
)

plt.show()


# =====================================================
# 5. FEATURE IMPORTANCE
# =====================================================

features = pd.read_csv(
    "data/final_feature_importance.csv"
)

features = features.head(15)

plt.figure(figsize=(10, 7))

plt.barh(
    features["Feature"],
    features["Importance"]
)

plt.xlabel("Importance")

plt.title(
    "Player Valuation Feature Importance"
)

plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig(
    "data/feature_importance.png",
    dpi=300
)

plt.show()


print("\n==============================")
print("VISUAL ANALYTICS COMPLETE")
print("==============================")

print("✓ data/final_transfer_opportunities.csv")
print("✓ data/top_undervalued.png")
print("✓ data/top_overvalued.png")
print("✓ data/actual_vs_predicted.png")
print("✓ data/feature_importance.png")