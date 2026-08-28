import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Premier League Evaluator",
    page_icon="🏆",
    layout="wide"
)


# ============================================================
# CSS  —  retro pop-art / matchday poster theme
# ============================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Anton&family=Bebas+Neue&family=Archivo:wght@400;600;700;800&display=swap');

:root{
    --cream: #F3E4BF;
    --cream-light: #FBF3DE;
    --red: #C6402F;
    --red-dark: #A6321F;
    --green: #1B5E3F;
    --navy: #122744;
    --gold: #E3A73F;
    --ink: #1A1A1A;
    --muted: #6b6357;
}

/* ---------- App background: cream + faint dot field ---------- */
[data-testid="stAppViewContainer"], .stApp {
    background-color: var(--cream);
    background-image:
        radial-gradient(rgba(26,26,26,0.06) 1px, transparent 1px);
    background-size: 16px 16px;
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

* {
    font-family: 'Archivo', sans-serif;
}

/* ---------- Top scoreboard ticker ---------- */
.ticker-bar {
    background: var(--navy);
    border-bottom: 4px solid var(--gold);
    border-radius: 10px;
    padding: 10px 20px;
    margin: 0 0 22px 0;
    display: flex;
    flex-wrap: wrap;
    gap: 22px;
    justify-content: center;
    box-shadow: 5px 5px 0 var(--ink);
}

.ticker-item {
    color: #F3E4BF;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 15px;
    letter-spacing: 1px;
    white-space: nowrap;
}

.ticker-item b {
    color: var(--gold);
}

/* ---------- Hero badge ---------- */
.hero-wrap {
    text-align: center;
    margin-bottom: 6px;
}

.hero-badge {
    display: inline-block;
    background: var(--gold);
    border: 3px solid var(--ink);
    border-radius: 999px;
    padding: 7px 22px;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 15px;
    letter-spacing: 2px;
    color: var(--ink);
    box-shadow: 4px 4px 0 var(--ink);
    margin-bottom: 18px;
}

/* ---------- Pennant banner ---------- */
.pennant-row {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    margin: 4px auto 10px auto;
    max-width: 820px;
}

.pennant {
    width: 0;
    height: 0;
    border-left: 11px solid transparent;
    border-right: 11px solid transparent;
    border-top: 16px solid var(--red);
    margin: 0 2px;
}

/* ---------- Giant stacked title ---------- */
.hero-title {
    font-family: 'Anton', sans-serif;
    text-transform: uppercase;
    line-height: 0.95;
    letter-spacing: 1px;
    margin: 6px 0 4px 0;
}

.hero-title .line-red {
    display: block;
    font-size: clamp(2.6rem, 6vw, 4.6rem);
    color: var(--red);
    text-shadow: 4px 4px 0 var(--ink);
}

.hero-title .line-green {
    display: block;
    font-size: clamp(2.6rem, 6vw, 4.6rem);
    color: var(--green);
    text-shadow: 4px 4px 0 var(--ink);
}

.hero-subtitle {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 18px;
    letter-spacing: 2px;
    color: var(--muted);
    margin-top: 10px;
}

/* ---------- Section headers ---------- */
h2, h3 {
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 1px;
    color: var(--ink) !important;
    text-transform: uppercase;
}

h2 {
    font-size: 1.9rem !important;
    border-left: 8px solid var(--red);
    padding-left: 12px;
}

/* ---------- Divider ---------- */
hr {
    border: none !important;
    height: 6px !important;
    background: repeating-linear-gradient(
        90deg,
        var(--red) 0px, var(--red) 18px,
        var(--green) 18px, var(--green) 36px
    ) !important;
    border-radius: 6px;
    opacity: 1 !important;
    margin: 22px 0 !important;
}

/* ---------- Cards: player / value / stat ---------- */
.player-card {
    background: var(--navy);
    border: 3px solid var(--ink);
    border-radius: 14px;
    padding: 22px 24px;
    margin-bottom: 15px;
    box-shadow: 6px 6px 0 var(--ink);
    color: var(--cream-light);
}

.player-card h2 {
    color: var(--cream-light) !important;
    border-left: none !important;
    padding-left: 0 !important;
    font-family: 'Anton', sans-serif !important;
    letter-spacing: 1px;
    margin-bottom: 4px;
}

.player-card h1 {
    color: var(--gold) !important;
    font-family: 'Anton', sans-serif !important;
}

.value-card {
    background: var(--cream-light);
    border: 3px solid var(--ink);
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    box-shadow: 5px 5px 0 var(--ink);
}

.value-title {
    color: var(--muted);
    font-family: 'Bebas Neue', sans-serif;
    font-size: 14px;
    letter-spacing: 2px;
}

.value-number {
    font-family: 'Anton', sans-serif;
    font-size: 26px;
    color: var(--red);
    letter-spacing: 0.5px;
}

.stat-box {
    background: var(--cream-light);
    border: 3px solid var(--ink);
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    box-shadow: 4px 4px 0 var(--ink);
}

.stat-name {
    color: var(--muted);
    font-family: 'Bebas Neue', sans-serif;
    font-size: 13px;
    letter-spacing: 1.5px;
}

.stat-value {
    font-family: 'Anton', sans-serif;
    font-size: 21px;
    color: var(--green);
}

/* ---------- Streamlit widgets restyled ---------- */

/* Tabs */
[data-testid="stTabs"] button[role="tab"] {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 17px;
    letter-spacing: 1.5px;
    color: var(--ink);
    background: var(--cream-light);
    border: 3px solid var(--ink);
    border-bottom: none;
    border-radius: 10px 10px 0 0;
    padding: 6px 18px;
    margin-right: 4px;
}

[data-testid="stTabs"] button[aria-selected="true"] {
    background: var(--red);
    color: var(--cream-light);
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: transparent;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 1.5px;
    background: var(--red) !important;
    color: var(--cream-light) !important;
    border: 3px solid var(--ink) !important;
    border-radius: 10px !important;
    box-shadow: 4px 4px 0 var(--ink);
    transition: transform 0.08s ease;
}

.stButton > button:hover {
    transform: translate(-2px, -2px);
    box-shadow: 6px 6px 0 var(--ink);
    color: var(--cream-light) !important;
}

/* Selectboxes */
[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: var(--cream-light) !important;
    border: 3px solid var(--ink) !important;
    border-radius: 10px !important;
    box-shadow: 3px 3px 0 var(--ink);
    font-family: 'Archivo', sans-serif;
    font-weight: 700;
}

[data-testid="stSelectbox"] label {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 1.5px;
    font-size: 15px;
    color: var(--ink) !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--cream-light);
    border: 3px solid var(--ink);
    border-radius: 12px;
    padding: 14px;
    box-shadow: 5px 5px 0 var(--ink);
}

[data-testid="stMetricLabel"] {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 1px;
}

[data-testid="stMetricValue"] {
    font-family: 'Anton', sans-serif;
    color: var(--red);
}

/* Expander */
[data-testid="stExpander"] {
    border: 3px solid var(--ink) !important;
    border-radius: 12px !important;
    background: var(--cream-light);
    box-shadow: 5px 5px 0 var(--ink);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 3px solid var(--ink);
    border-radius: 10px;
    overflow: hidden;
}

/* Warnings / errors keep readable but themed */
[data-testid="stAlert"] {
    border: 3px solid var(--ink);
    border-radius: 10px;
    box-shadow: 4px 4px 0 var(--ink);
}

/* Footer */
.footer-band {
    text-align: center;
    color: var(--cream-light);
    background: var(--navy);
    border: 3px solid var(--ink);
    border-radius: 12px;
    padding: 16px;
    margin-top: 10px;
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 1.5px;
    box-shadow: 5px 5px 0 var(--ink);
}

.footer-band .tag {
    color: var(--gold);
    font-size: 13px;
    display: block;
    margin-top: 4px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown("""
<div class="ticker-bar">
    <div class="ticker-item">🏆 <b>PL 2025/26</b></div>
    <div class="ticker-item">⚙️ <b>ML-POWERED</b> VALUATIONS</div>
    <div class="ticker-item">📊 <b>20</b> CLUBS TRACKED</div>
    <div class="ticker-item">🔄 UPDATED <b>EVERY MATCHWEEK</b></div>
</div>
""", unsafe_allow_html=True)

pennant_colors = ["#C6402F", "#1B5E3F"] * 14
pennants_html = "".join(
    f'<div class="pennant" style="border-top-color:{c}"></div>'
    for c in pennant_colors
)
st.markdown(f'<div class="pennant-row">{pennants_html}</div>', unsafe_allow_html=True)

st.markdown("""
<div class="hero-wrap">
    <div class="hero-badge">⚽ MACHINE LEARNING · 20 CLUBS · EVERY MATCHWEEK</div>
    <div class="hero-title">
        <span class="line-red">PREMIER LEAGUE</span>
        <span class="line-green">EVALUATOR</span>
    </div>
    <div class="hero-subtitle">MACHINE LEARNING + FOOTBALL PERFORMANCE ANALYTICS</div>
</div>
""", unsafe_allow_html=True)

st.divider()


# ============================================================
# FILES
# ============================================================

DATA_DIR = Path("data")

dataset_file = DATA_DIR / "final_player_value_dataset.csv"
valuation_file = DATA_DIR / "all_epl_player_valuations.csv"


if not dataset_file.exists():

    st.error(
        "final_player_value_dataset.csv not found inside data/"
    )

    st.stop()


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(dataset_file)

df.columns = df.columns.astype(str).str.strip()


# ============================================================
# PLAYER NAME
# ============================================================

name_candidates = [
    "Player Name",
    "name",
    "player_name",
    "Name"
]

name_column = None

for col in name_candidates:

    if col in df.columns:
        name_column = col
        break


if name_column is None:

    st.error("Player name column not found.")

    st.write(df.columns.tolist())

    st.stop()


df["Player Name"] = (
    df[name_column]
    .astype(str)
    .str.strip()
)


# ============================================================
# CLUB
# ============================================================

club_candidates = [
    "Club",
    "current_club_name",
    "club",
    "Current Club"
]

club_column = None

for col in club_candidates:

    if col in df.columns:
        club_column = col
        break


if club_column:

    df["Club"] = (
        df[club_column]
        .astype(str)
        .str.strip()
    )

else:

    df["Club"] = "Unknown"


# ============================================================
# POSITION
# ============================================================

position_candidates = [
    "Position",
    "position"
]

position_column = None

for col in position_candidates:

    if col in df.columns:
        position_column = col
        break


if position_column:

    df["Position"] = (
        df[position_column]
        .astype(str)
        .str.strip()
    )

else:

    df["Position"] = "Unknown"


# ============================================================
# MARKET VALUE
# ============================================================

if "market_value_in_eur" in df.columns:

    df["market_value_in_eur"] = pd.to_numeric(
        df["market_value_in_eur"],
        errors="coerce"
    )

else:

    df["market_value_in_eur"] = np.nan


# ============================================================
# LOAD VALUATION FILE
# ============================================================

if valuation_file.exists():

    valuation_df = pd.read_csv(valuation_file)

    valuation_df.columns = (
        valuation_df.columns
        .astype(str)
        .str.strip()
    )

else:

    valuation_df = pd.DataFrame()


# ============================================================
# MERGE FINAL VALUATION
# ============================================================

if not valuation_df.empty:

    valuation_name = None

    for col in [
        "Player Name",
        "name",
        "player_name",
        "Name"
    ]:

        if col in valuation_df.columns:

            valuation_name = col
            break


    if (
        valuation_name is not None
        and "Final Valuation" in valuation_df.columns
    ):

        valuation_df["Player Name"] = (
            valuation_df[valuation_name]
            .astype(str)
            .str.strip()
        )

        valuation_df["Final Valuation"] = pd.to_numeric(
            valuation_df["Final Valuation"],
            errors="coerce"
        )

        lookup = (
            valuation_df[
                [
                    "Player Name",
                    "Final Valuation"
                ]
            ]
            .drop_duplicates("Player Name")
        )

        df = df.merge(
            lookup,
            on="Player Name",
            how="left"
        )

    else:

        df["Final Valuation"] = np.nan

else:

    df["Final Valuation"] = np.nan


# ============================================================
# FALLBACK VALUES
# ============================================================

df["Final Valuation"] = (
    df["Final Valuation"]
    .fillna(df["market_value_in_eur"])
)


if "ML Estimated Value" in df.columns:

    df["Final Valuation"] = (
        df["Final Valuation"]
        .fillna(
            pd.to_numeric(
                df["ML Estimated Value"],
                errors="coerce"
            )
        )
    )


# ============================================================
# MONEY FORMAT
# ============================================================

def money(value):

    if pd.isna(value):
        return "N/A"

    value = float(value)

    if value >= 1_000_000_000:
        return f"€{value / 1_000_000_000:.2f}B"

    if value >= 1_000_000:
        return f"€{value / 1_000_000:.2f}M"

    if value >= 1_000:
        return f"€{value / 1_000:.0f}K"

    return f"€{value:,.0f}"


# ============================================================
# RADAR STATISTICS
# ============================================================

RADAR_STATS = {

    "Goals": [
        "Goals"
    ],

    "Assists": [
        "Assists"
    ],

    "Shots": [
        "Shots"
    ],

    "Shots On Target": [
        "Shots On Target"
    ],

    "Touches": [
        "Touches"
    ],

    "Passes": [
        "Passes"
    ],

    "Successful Passes": [
        "Successful Passes"
    ],

    "Forward Passes": [
        "fThird Passes",
        "Forward Passes"
    ],

    "Tackles": [
        "Tackles"
    ],

    "Interceptions": [
        "Interceptions"
    ],

    "Ground Duels": [
        "Ground Duels"
    ],

    "Progressive Carries": [
        "Progressive Carries"
    ],

    "Possession Won": [
        "Possession Won"
    ]
}


# ============================================================
# INDIVIDUAL RADAR
# ============================================================

def individual_radar(row, title):

    labels = []
    columns = []

    for label, candidates in RADAR_STATS.items():

        found = None

        for candidate in candidates:

            if candidate in df.columns:
                found = candidate
                break

        if found is not None:

            labels.append(label)
            columns.append(found)


    # Keep graph compact
    labels = labels[:8]
    columns = columns[:8]


    if len(columns) < 3:

        st.warning(
            "Not enough statistics available for radar chart."
        )

        return


    # League maximum
    league_values = df[columns].apply(
        pd.to_numeric,
        errors="coerce"
    ).fillna(0)


    maximum = league_values.max()

    maximum[maximum == 0] = 1


    values = []

    for column in columns:

        value = pd.to_numeric(
            row[column],
            errors="coerce"
        )

        if pd.isna(value):
            value = 0

        score = value / maximum[column]

        score = min(score, 1)

        values.append(score)


    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    )


    values = values + values[:1]

    angles = np.concatenate(
        [angles, angles[:1]]
    )


    # SMALL GRAPH — themed to match the poster palette
    fig, ax = plt.subplots(
        figsize=(4.3, 4.3),
        subplot_kw={"polar": True}
    )

    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")

    ax.plot(
        angles,
        values,
        linewidth=2.5,
        color="#C6402F"
    )

    ax.fill(
        angles,
        values,
        alpha=0.22,
        color="#C6402F"
    )


    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels,
        fontsize=8,
        color="#1A1A1A",
        fontweight="bold"
    )

    ax.set_ylim(0, 1)

    ax.set_yticklabels([])

    ax.set_title(
        title,
        fontsize=13,
        fontweight="bold",
        pad=18,
        color="#1A1A1A"
    )

    ax.grid(alpha=0.3, color="#1A1A1A")
    ax.spines['polar'].set_color("#1A1A1A")


    st.pyplot(
        fig,
        use_container_width=False
    )

    plt.close(fig)


# ============================================================
# COMPARISON RADAR
# ============================================================

def comparison_radar(
    row1,
    row2,
    name1,
    name2
):

    labels = []
    columns = []

    for label, candidates in RADAR_STATS.items():

        found = None

        for candidate in candidates:

            if candidate in df.columns:
                found = candidate
                break

        if found is not None:

            labels.append(label)
            columns.append(found)


    labels = labels[:8]
    columns = columns[:8]


    if len(columns) < 3:

        st.warning(
            "Not enough statistics available."
        )

        return


    league_values = df[columns].apply(
        pd.to_numeric,
        errors="coerce"
    ).fillna(0)


    maximum = league_values.max()

    maximum[maximum == 0] = 1


    values1 = []
    values2 = []


    for column in columns:

        value1 = pd.to_numeric(
            row1[column],
            errors="coerce"
        )

        value2 = pd.to_numeric(
            row2[column],
            errors="coerce"
        )


        if pd.isna(value1):
            value1 = 0

        if pd.isna(value2):
            value2 = 0


        values1.append(
            min(value1 / maximum[column], 1)
        )

        values2.append(
            min(value2 / maximum[column], 1)
        )


    angles = np.linspace(
        0,
        2 * np.pi,
        len(labels),
        endpoint=False
    )


    values1 = values1 + values1[:1]

    values2 = values2 + values2[:1]

    angles = np.concatenate(
        [angles, angles[:1]]
    )


    # SMALL COMPARISON GRAPH — red vs green, matchday palette
    fig, ax = plt.subplots(
        figsize=(4.8, 4.8),
        subplot_kw={"polar": True}
    )

    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")


    ax.plot(
        angles,
        values1,
        linewidth=2.5,
        label=name1,
        color="#C6402F"
    )

    ax.fill(
        angles,
        values1,
        alpha=0.18,
        color="#C6402F"
    )


    ax.plot(
        angles,
        values2,
        linewidth=2.5,
        label=name2,
        color="#1B5E3F"
    )

    ax.fill(
        angles,
        values2,
        alpha=0.18,
        color="#1B5E3F"
    )


    ax.set_xticks(
        angles[:-1]
    )

    ax.set_xticklabels(
        labels,
        fontsize=8,
        color="#1A1A1A",
        fontweight="bold"
    )

    ax.set_ylim(0, 1)

    ax.set_yticklabels([])

    ax.set_title(
        "Performance Comparison",
        fontsize=14,
        fontweight="bold",
        pad=18,
        color="#1A1A1A"
    )


    ax.legend(
        loc="upper right",
        bbox_to_anchor=(1.25, 1.12),
        fontsize=8
    )


    ax.grid(alpha=0.3, color="#1A1A1A")
    ax.spines['polar'].set_color("#1A1A1A")


    st.pyplot(
        fig,
        use_container_width=False
    )

    plt.close(fig)


# ============================================================
# SEPARATE APP SECTIONS
# ============================================================

tab_player, tab_compare = st.tabs([
    "👤 Player Analysis",
    "🔄 Compare Players"
])

with tab_player:
    # ============================================================
    # TEAM SELECTION
    # ============================================================

    st.subheader("🏟️ Select Team")


    teams = sorted(
        df["Club"]
        .dropna()
        .unique()
    )


    selected_team = st.selectbox(
        "Choose a Premier League team",
        teams
    )


    # ============================================================
    # PLAYER SELECTION
    # ============================================================

    team_players = (
        df[
            df["Club"] == selected_team
        ]
        .sort_values("Player Name")
    )


    st.subheader("👤 Select Player")


    players = (
        team_players["Player Name"]
        .dropna()
        .unique()
        .tolist()
    )


    if not players:

        st.warning(
            "No players found."
        )

        st.stop()


    selected_player = st.selectbox(
        "Choose a player",
        players
    )


    player = team_players[
        team_players["Player Name"]
        == selected_player
    ]


    player_row = player.iloc[0]


    # ============================================================
    # PLAYER HEADER
    # ============================================================

    st.divider()

    st.markdown(
        f"""
        <div class="player-card">

        <h2>⚽ {player_row["Player Name"]}</h2>

        <p style="font-size:16px;color:#9aa4b2;">
        {player_row["Club"]} &nbsp; • &nbsp;
        {player_row["Position"]}
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


    # ============================================================
    # VALUE CARDS
    # ============================================================

    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            f"""
            <div class="value-card">

            <div class="value-title">
            MARKET VALUE
            </div>

            <div class="value-number">
            {money(player_row["market_value_in_eur"])}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
            <div class="value-card">

            <div class="value-title">
            FINAL VALUATION
            </div>

            <div class="value-number">
            {money(player_row["Final Valuation"])}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col3:

        if (
            not pd.isna(
                player_row["market_value_in_eur"]
            )
            and
            not pd.isna(
                player_row["Final Valuation"]
            )
        ):

            gap = (
                player_row["Final Valuation"]
                -
                player_row["market_value_in_eur"]
            )

            if gap >= 0:

                gap_text = "+" + money(gap)

            else:

                gap_text = "-" + money(abs(gap))

        else:

            gap_text = "N/A"


        st.markdown(
            f"""
            <div class="value-card">

            <div class="value-title">
            VALUE GAP
            </div>

            <div class="value-number">
            {gap_text}
            </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ============================================================
    # INDIVIDUAL PERFORMANCE
    # ============================================================

    st.divider()

    st.header("📊 Player Performance")


    # Center the graph
    left, center, right = st.columns(
        [1, 1.4, 1]
    )


    with center:

        individual_radar(
            player_row,
            selected_player
        )


    # ============================================================
    # QUICK STATS
    # ============================================================

    st.subheader("⚡ Key Statistics")


    quick_stats = [

        ("Goals", "Goals"),
        ("Assists", "Assists"),
        ("Shots", "Shots"),
        ("Touches", "Touches"),
        ("Passes", "Passes"),
        ("Tackles", "Tackles"),
        ("Interceptions", "Interceptions"),
        ("Minutes", "Minutes")

    ]


    available_stats = []

    for label, column in quick_stats:

        if column in df.columns:

            value = pd.to_numeric(
                player_row[column],
                errors="coerce"
            )

            if pd.isna(value):
                value = 0

            available_stats.append(
                (label, value)
            )


    stat_columns = st.columns(4)


    for i, (label, value) in enumerate(
        available_stats
    ):

        with stat_columns[i % 4]:

            st.markdown(
                f"""
                <div class="stat-box">

                <div class="stat-name">
                {label}
                </div>

                <div class="stat-value">
                {value:,.0f}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    # ============================================================
    # ALL STATS
    # ============================================================

    st.divider()

    with st.expander("📋 View all player statistics"):

        excluded = [
            "market_value_in_eur",
            "Final Valuation"
        ]


        numeric_columns = []

        for column in df.columns:

            if column in excluded:
                continue

            converted = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            if converted.notna().sum() > 10:

                numeric_columns.append(column)


        stats = pd.DataFrame({

            "Statistic": numeric_columns,

            "Value": [
                player_row[column]
                for column in numeric_columns
            ]

        })


        st.dataframe(
            stats,
            use_container_width=True,
            hide_index=True
        )



with tab_compare:
    # ============================================================
    # PLAYER COMPARISON
    # ============================================================

    st.divider()

    st.header("🔄 Compare Two Players")

    st.write(
        "Compare player valuation and performance."
    )


    all_players = sorted(
        df["Player Name"]
        .dropna()
        .unique()
        .tolist()
    )


    c1, c2 = st.columns(2)


    with c1:

        default_index = (
            all_players.index(selected_player)
            if selected_player in all_players
            else 0
        )

        player1_name = st.selectbox(
            "Player 1",
            all_players,
            index=default_index,
            key="comparison_player_1"
        )


    with c2:

        second_index = (
            1
            if len(all_players) > 1
            else 0
        )

        player2_name = st.selectbox(
            "Player 2",
            all_players,
            index=second_index,
            key="comparison_player_2"
        )


    player1_data = df[
        df["Player Name"] == player1_name
    ]


    player2_data = df[
        df["Player Name"] == player2_name
    ]


    if not player1_data.empty and not player2_data.empty:

        p1 = player1_data.iloc[0]
        p2 = player2_data.iloc[0]


        # ========================================================
        # PLAYER CARDS
        # ========================================================

        card1, card2 = st.columns(2)


        with card1:

            st.markdown(
                f"""
                <div class="player-card">

                <h2>{p1["Player Name"]}</h2>

                <p style="color:#9aa4b2;">
                {p1["Club"]} • {p1["Position"]}
                </p>

                <h1>
                {money(p1["Final Valuation"])}
                </h1>

                </div>
                """,
                unsafe_allow_html=True
            )


        with card2:

            st.markdown(
                f"""
                <div class="player-card">

                <h2>{p2["Player Name"]}</h2>

                <p style="color:#9aa4b2;">
                {p2["Club"]} • {p2["Position"]}
                </p>

                <h1>
                {money(p2["Final Valuation"])}
                </h1>

                </div>
                """,
                unsafe_allow_html=True
            )


        # ========================================================
        # COMPARISON RADAR
        # ========================================================

        st.subheader("📊 Performance Comparison")


        comparison_left, comparison_center, comparison_right = (
            st.columns([1, 1.5, 1])
        )


        with comparison_center:

            comparison_radar(
                p1,
                p2,
                player1_name,
                player2_name
            )


        # ========================================================
        # VALUE COMPARISON
        # ========================================================

        st.subheader("💰 Market Value Comparison")


        v1, v2, v3 = st.columns(3)


        with v1:

            st.metric(
                player1_name,
                money(p1["Final Valuation"])
            )


        with v2:

            st.metric(
                player2_name,
                money(p2["Final Valuation"])
            )


        with v3:

            if (
                not pd.isna(p1["Final Valuation"])
                and
                not pd.isna(p2["Final Valuation"])
            ):

                difference = (
                    p1["Final Valuation"]
                    -
                    p2["Final Valuation"]
                )

                st.metric(
                    "Value Difference",
                    money(abs(difference))
                )


        # ========================================================
        # FULL COMPARISON TABLE
        # ========================================================

        st.subheader("📋 Statistics Comparison")


        excluded = [
            "market_value_in_eur",
            "Final Valuation"
        ]


        comparison_columns = []


        for column in df.columns:

            if column in excluded:
                continue

            converted = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            if converted.notna().sum() > 10:

                comparison_columns.append(column)


        comparison_rows = []


        for column in comparison_columns:

            value1 = pd.to_numeric(
                p1[column],
                errors="coerce"
            )

            value2 = pd.to_numeric(
                p2[column],
                errors="coerce"
            )


            comparison_rows.append({

                "Statistic": column,

                player1_name: (
                    round(value1, 2)
                    if not pd.isna(value1)
                    else 0
                ),

                player2_name: (
                    round(value2, 2)
                    if not pd.isna(value2)
                    else 0
                )

            })


        comparison_table = pd.DataFrame(
            comparison_rows
        )


        st.dataframe(
            comparison_table,
            use_container_width=True,
            hide_index=True
        )



# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer-band">
    🏆 PREMIER LEAGUE EVALUATOR
    <span class="tag">MACHINE LEARNING • SPORTS ANALYTICS • FOOTBALL PERFORMANCE</span>
    </div>
    """,
    unsafe_allow_html=True
)