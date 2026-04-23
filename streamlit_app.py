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

# ── Custom CSS ─────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Lato:wght@300;400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif;
        color: #2c1a0e;
    }

    .stApp {
        background: linear-gradient(135deg, #fdf6ec 0%, #fef9f4 100%);
    }

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

    [data-testid="stMetricValue"] {
        color: #2c1a0e !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #8c6a4e !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
    }

    .stExpander {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid #e0d5c8 !important;
        margin-bottom: 1rem !important;
    }
    
    .stExpander [data-testid="stExpanderDetails"] {
        color: #2c1a0e !important;
    }

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

    .section-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #d4845a;
        margin: 1.2rem 0 0.5rem 0;
        border-bottom: 1px solid #eee;
    }

    section[data-testid="stSidebar"] {
        background-color: #2c1a0e !important;
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stSlider p {
        color: #f5e6d3 !important;
    }
    
    section[data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #3d2b1f !important;
        border-color: #4a3629 !important;
    }
    
    .no-results {
        text-align: center;
        padding: 4rem 2rem;
        color: #8c6a4e;
    }

    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Google Sheets Connection ──────────────────────────────────────────────────
@st.cache_data(ttl=300)
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
    worksheet = sheet.get_worksheet(0)
    data = worksheet.get_all_records()
    
    df = pd.DataFrame(data)
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
        st.stop()

if df.empty:
    st.warning("Das Google Sheet enthält keine Daten.")
    st.stop()

# ── Tabs Setup ────────────────────────────────────────────────────────────────
tab_suche, tab_zutaten_check = st.tabs(["🔍 Rezeptsuche", "🛒 Zutaten-Check"])

# ── Sidebar Filter (Global wirksam) ───────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Filter")
    st.markdown("---")

    search_term = st.text_input("Suche nach Gericht", placeholder="z. B. Pasta, Suppe …")
    st.markdown("---")

    min_zeit = int(df["Benötigte Zeit"].min())
    max_zeit = int(df["Benötigte Zeit"].max())
    if min_zeit == max_zeit:
        max_zeit = min_zeit + 1

    zeit_range = st.slider(
        "⏱️ Benötigte Zeit (Minuten)",
        min_value=min_zeit,
        max_value=max_zeit,
        value=(min_zeit, max_zeit),
        step=5,
    )
    st.markdown("---")

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

# ── Filterlogik (Global) ──────────────────────────────────────────────────────
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

# ── Hilfsfunktionen ──────────────────────────────────────────────────────────
def aufwand_class(aufwand: str) -> str:
    mapping = {"Leicht": "leicht", "Mittel": "mittel", "Schwer": "schwer"}
    return f"badge-aufwand-{mapping.get(aufwand, 'mittel')}"

def get_ingredients_list(zutaten_str):
    if not zutaten_str: return []
    return [z.strip().lower() for z in str(zutaten_str).replace("\n", ",").split(",") if z.strip()]

# Liste der zu ignorierenden Gewürze
GEWUERZE = ["salz", "pfeffer", "zucker", "öl", "olivenöl", "wasser", "essig", "brühwürfel", "brühe", "knoblauchzehe"]

# ── TAB 1: REZEPTSUCHE ────────────────────────────────────────────────────────
with tab_suche:
    if filtered.empty:
        st.markdown('<div class="no-results"><h2>Keine Rezepte gefunden 🥺</h2><p>Passe deine Filter an.</p></div>', unsafe_allow_html=True)
    else:
        for _, row in filtered.iterrows():
            name = row.get("Name des Gerichts", "Unbekannt")
            zeit = row.get("Benötigte Zeit", 0)
            aufwand = row.get("Aufwand", "")
            kategorie = row.get("Kategorie", "")
            ernaehrung = row.get("Ernährungsform", "")
            saison = row.get("Saison-Check", "")
            equipment = row.get("Equipment", "")
            zutaten = row.get("Benötigte Zutaten", "")
            zubereitung = row.get("Zubereitung", "")

            badges = ""
            if kategorie: badges += f'<span class="badge badge-kategorie">{kategorie}</span>'
            if ernaehrung: badges += f'<span class="badge badge-ernaehrung">{ernaehrung}</span>'
            if saison: badges += f'<span class="badge badge-saison">{saison}</span>'
            if aufwand: badges += f'<span class="badge {aufwand_class(aufwand)}">{aufwand}</span>'

            with st.expander(f"🍽️ {name}  •  ⏱️ {zeit} min", expanded=False):
                st.markdown(badges, unsafe_allow_html=True)
                col_l, col_r = st.columns([1, 2])
                with col_l:
                    st.markdown('<div class="section-label">🧂 Zutaten</div>', unsafe_allow_html=True)
                    if zutaten:
                        items = [z.strip() for z in str(zutaten).replace("\n", ",").split(",") if z.strip()]
                        for item in items: st.markdown(f"• {item}")
                    else: st.markdown("_Keine Zutaten angegeben_")
                    if equipment:
                        st.markdown('<div class="section-label">🔧 Equipment</div>', unsafe_allow_html=True)
                        eq_items = [e.strip() for e in str(equipment).replace("\n", ",").split(",") if e.strip()]
                        for eq in eq_items: st.markdown(f"• {eq}")
                with col_r:
                    st.markdown('<div class="section-label">👨‍🍳 Zubereitung</div>', unsafe_allow_html=True)
                    if zubereitung:
                        steps = [s.strip() for s in str(zubereitung).split("\n") if s.strip()]
                        for i, step in enumerate(steps, 1): st.markdown(f"**{i}.** {step}")
                    else: st.markdown("_Keine Zubereitung angegeben_")

# ── TAB 2: ZUTATEN-CHECK ──────────────────────────────────────────────────────
with tab_zutaten_check:
    st.markdown("### 🛒 Was hast du im Kühlschrank?")
    st.info("Wähle deine vorhandenen Zutaten aus. Gewürze werden automatisch ignoriert.")
    
    # Alle Zutaten aus dem gesamten DF extrahieren (einmalig)
    all_ingredients = set()
    for _, row in df.iterrows():
        ing_list = get_ingredients_list(row.get("Benötigte Zutaten", ""))
        for item in ing_list:
            if item not in GEWUERZE:
                all_ingredients.add(item.capitalize())
    
    sorted_ingredients = sorted(list(all_ingredients))
    user_ingredients = st.multiselect("Vorhandene Zutaten auswählen:", options=sorted_ingredients)
    user_ingredients_lower = [i.lower() for i in user_ingredients]

    if user_ingredients:
        match_full = []
        match_partial = []

        for _, row in filtered.iterrows():
            recipe_ing_raw = get_ingredients_list(row.get("Benötigte Zutaten", ""))
            # Filter Gewürze für den Abgleich heraus
            recipe_ing = [i for i in recipe_ing_raw if i not in GEWUERZE]
            
            if not recipe_ing:
                continue
                
            # Check matches
            matches = [i for i in recipe_ing if i in user_ingredients_lower]
            
            if len(matches) == len(recipe_ing):
                match_full.append(row)
            elif len(matches) > 0:
                match_partial.append((row, len(matches), len(recipe_ing)))

        # Ausgabe Vollständig
        st.markdown("#### ✅ Vollständige Übereinstimmung")
        if match_full:
            for r in match_full:
                st.success(f"**{r['Name des Gerichts']}** (Alle Zutaten vorhanden!)")
        else:
            st.write("_Kein Rezept passt perfekt zu deiner Auswahl._")

        # Ausgabe Teilweise
        st.markdown("#### ⚠️ Teilweise Übereinstimmung")
        if match_partial:
            # Sortieren nach Trefferquote
            match_partial.sort(key=lambda x: x[1]/x[2], reverse=True)
            for r, got, total in match_partial:
                st.warning(f"**{r['Name des Gerichts']}**: {got} von {total} Zutaten vorhanden.")
        else:
            st.write("_Keine teilweisen Treffer._")
    else:
        st.write("Wähle oben Zutaten aus, um den Check zu starten.")
