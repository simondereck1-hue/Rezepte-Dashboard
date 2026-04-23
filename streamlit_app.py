import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🍽️ Rezept-Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Lato:wght@300;400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif;
    }

    /* Background */
    .stApp {
        background: linear-gradient(135deg, #fdf6ec 0%, #fef9f4 100%);
    }

    /* Header */
    .dashboard-header {
        text-align: center;
        padding: 2rem 0 1.5rem 0;
    }
    .dashboard-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 700;
        color: #2c1a0e;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .dashboard-header p {
        color: #8c6a4e;
        font-size: 1.05rem;
        margin-top: 0.4rem;
        font-weight: 300;
    }

    /* Metric cards */
    .metric-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        border-radius: 14px;
        padding: 1.2rem 1.6rem;
        box-shadow: 0 2px 12px rgba(44,26,14,0.07);
        flex: 1;
        border-left: 4px solid #d4845a;
    }
    .metric-card .metric-value {
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #2c1a0e;
        line-height: 1;
    }
    .metric-card .metric-label {
        font-size: 0.8rem;
        color: #8c6a4e;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.3rem;
        font-weight: 700;
    }

    /* Recipe card */
    .recipe-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        box-shadow: 0 2px 16px rgba(44,26,14,0.08);
        margin-bottom: 1.2rem;
        border-top: 4px solid #d4845a;
        transition: box-shadow 0.2s;
    }
    .recipe-card:hover {
        box-shadow: 0 6px 24px rgba(44,26,14,0.14);
    }
    .recipe-card h3 {
        font-family: 'Playfair Display', serif;
        color: #2c1a0e;
        font-size: 1.35rem;
        margin: 0 0 0.8rem 0;
    }

    /* Badge */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin: 0.15rem;
    }
    .badge-kategorie  { background: #fde8d8; color: #b5501e; }
    .badge-ernaehrung { background: #d6f0e0; color: #1e7a43; }
    .badge-saison     { background: #dce9fb; color: #1e4d8c; }
    .badge-aufwand-leicht { background: #d6f0e0; color: #1e7a43; }
    .badge-aufwand-mittel { background: #fff3cd; color: #8a6000; }
    .badge-aufwand-schwer { background: #fde8d8; color: #b5501e; }

    /* Section label in expander */
    .section-label {
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #8c6a4e;
        margin: 1rem 0 0.3rem 0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #2c1a0e;
    }
    section[data-testid="stSidebar"] * {
        color: #f5e6d3 !important;
    }
    section[data-testid="stSidebar"] .stSlider > div > div > div > div {
        background: #d4845a;
    }

    /* No results */
    .no-results {
        text-align: center;
        padding: 4rem 2rem;
        color: #8c6a4e;
    }
    .no-results h2 {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        color: #2c1a0e;
    }

    /* Hide default streamlit footer */
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Google Sheets Connection ──────────────────────────────────────────────────
@st.cache_data(ttl=300)  # Cache für 5 Minuten
def load_data() -> pd.DataFrame:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/drive.readonly",
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scopes,
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_url(st.secrets["spreadsheet_url"])
    worksheet = sheet.get_worksheet(0)  # erstes Tabellenblatt
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    # Spaltenbereinigung
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Name des Gerichts"])
    df = df[df["Name des Gerichts"].astype(str).str.strip() != ""]
    df["Benötigte Zeit"] = pd.to_numeric(df["Benötigte Zeit"], errors="coerce").fillna(0).astype(int)
    for col in ["Aufwand", "Kategorie", "Ernährungsform", "Equipment", "Saison-Check"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
    return df


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-header">
    <h1>🍽️ Rezept-Dashboard</h1>
    <p>Deine persönliche Rezeptsammlung – durchsuche, filtere und entdecke.</p>
</div>
""", unsafe_allow_html=True)

# ── Daten laden ───────────────────────────────────────────────────────────────
with st.spinner("Rezepte werden geladen …"):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Daten: {e}")
        st.info("Stelle sicher, dass die Google Sheets Verbindung in den Streamlit Secrets korrekt konfiguriert ist.")
        st.stop()

if df.empty:
    st.warning("Das Google Sheet enthält keine Daten.")
    st.stop()


# ── Sidebar Filter ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filter")
    st.markdown("---")

    # Textsuche
    search_term = st.text_input("Suche nach Gericht", placeholder="z. B. Pasta, Suppe …")

    st.markdown("---")

    # Zeit-Slider
    min_zeit = int(df["Benötigte Zeit"].min())
    max_zeit = int(df["Benötigte Zeit"].max())
    if min_zeit == max_zeit:
        max_zeit = min_zeit + 1  # Slider braucht min < max

    zeit_range = st.slider(
        "⏱️ Benötigte Zeit (Minuten)",
        min_value=min_zeit,
        max_value=max_zeit,
        value=(min_zeit, max_zeit),
        step=5,
    )

    st.markdown("---")

    # Multiselect Filter
    def ms_filter(label, column, emoji=""):
        options = sorted(df[column].dropna().unique().tolist())
        options = [o for o in options if o]
        return st.multiselect(f"{emoji} {label}", options=options)

    sel_kategorie   = ms_filter("Kategorie",      "Kategorie",      "🍴")
    sel_ernaehrung  = ms_filter("Ernährungsform",  "Ernährungsform", "🌿")
    sel_saison      = ms_filter("Saison-Check",    "Saison-Check",   "🌸")
    sel_aufwand     = ms_filter("Aufwand",         "Aufwand",        "⚡")

    st.markdown("---")
    if st.button("🔄 Filter zurücksetzen", use_container_width=True):
        st.rerun()


# ── Filterlogik ───────────────────────────────────────────────────────────────
filtered = df.copy()

if search_term:
    filtered = filtered[filtered["Name des Gerichts"].str.contains(search_term, case=False, na=False)]

filtered = filtered[
    (filtered["Benötigte Zeit"] >= zeit_range[0]) &
    (filtered["Benötigte Zeit"] <= zeit_range[1])
]

if sel_kategorie:
    filtered = filtered[filtered["Kategorie"].isin(sel_kategorie)]
if sel_ernaehrung:
    filtered = filtered[filtered["Ernährungsform"].isin(sel_ernaehrung)]
if sel_saison:
    filtered = filtered[filtered["Saison-Check"].isin(sel_saison)]
if sel_aufwand:
    filtered = filtered[filtered["Aufwand"].isin(sel_aufwand)]


# ── Metriken ──────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🍽️ Gefundene Rezepte", len(filtered))
with col2:
    avg_time = int(filtered["Benötigte Zeit"].mean()) if not filtered.empty else 0
    st.metric("⏱️ Ø Zubereitungszeit", f"{avg_time} min")
with col3:
    kategorien = filtered["Kategorie"].nunique()
    st.metric("🍴 Kategorien", kategorien)
with col4:
    ernaehrungsformen = filtered["Ernährungsform"].nunique()
    st.metric("🌿 Ernährungsformen", ernaehrungsformen)

st.markdown("---")


# ── Aufwand-Badge Klasse ──────────────────────────────────────────────────────
def aufwand_class(aufwand: str) -> str:
    mapping = {"Leicht": "leicht", "Mittel": "mittel", "Schwer": "schwer"}
    return f"badge-aufwand-{mapping.get(aufwand, 'mittel')}"


# ── Rezepte anzeigen ──────────────────────────────────────────────────────────
if filtered.empty:
    st.markdown("""
    <div class="no-results">
        <h2>Keine Rezepte gefunden 🥺</h2>
        <p>Passe deine Filter an, um Ergebnisse zu sehen.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"### {len(filtered)} Rezept{'e' if len(filtered) != 1 else ''} gefunden")
    st.markdown("")

    for _, row in filtered.iterrows():
        name       = row.get("Name des Gerichts", "Unbekannt")
        zeit       = row.get("Benötigte Zeit", 0)
        aufwand    = row.get("Aufwand", "")
        kategorie  = row.get("Kategorie", "")
        ernaehrung = row.get("Ernährungsform", "")
        saison     = row.get("Saison-Check", "")
        equipment  = row.get("Equipment", "")
        zutaten    = row.get("Benötigte Zutaten", "")
        zubereitung = row.get("Zubereitung", "")

        # Badges HTML
        badges = ""
        if kategorie:
            badges += f'<span class="badge badge-kategorie">{kategorie}</span>'
        if ernaehrung:
            badges += f'<span class="badge badge-ernaehrung">{ernaehrung}</span>'
        if saison:
            badges += f'<span class="badge badge-saison">{saison}</span>'
        if aufwand:
            badges += f'<span class="badge {aufwand_class(aufwand)}">{aufwand}</span>'

        with st.expander(f"🍽️ {name}  •  ⏱️ {zeit} min", expanded=False):
            # Badges Zeile
            st.markdown(badges, unsafe_allow_html=True)
            st.markdown("")

            col_l, col_r = st.columns([1, 2])

            with col_l:
                st.markdown('<div class="section-label">🧂 Zutaten</div>', unsafe_allow_html=True)
                if zutaten:
                    # Zutaten als Liste formatieren (getrennt durch Komma oder Zeilenumbruch)
                    items = [z.strip() for z in zutaten.replace("\n", ",").split(",") if z.strip()]
                    for item in items:
                        st.markdown(f"• {item}")
                else:
                    st.markdown("_Keine Zutaten angegeben_")

                if equipment:
                    st.markdown('<div class="section-label">🔧 Equipment</div>', unsafe_allow_html=True)
                    eq_items = [e.strip() for e in equipment.replace("\n", ",").split(",") if e.strip()]
                    for eq in eq_items:
                        st.markdown(f"• {eq}")

            with col_r:
                st.markdown('<div class="section-label">👨‍🍳 Zubereitung</div>', unsafe_allow_html=True)
                if zubereitung:
                    # Nummerierte Schritte falls durch Zeilenumbrüche getrennt
                    steps = [s.strip() for s in zubereitung.split("\n") if s.strip()]
                    if len(steps) > 1:
                        for i, step in enumerate(steps, 1):
                            st.markdown(f"**{i}.** {step}")
                    else:
                        st.markdown(zubereitung)
                else:
                    st.markdown("_Keine Zubereitung angegeben_")
