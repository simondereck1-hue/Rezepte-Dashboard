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

# ── Custom CSS (Optimiert für Lesbarkeit) ─────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Lato:wght@300;400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Lato', sans-serif;
        color: #2c1a0e;
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

    /* Metric cards (Fix für Lesbarkeit) */
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

    /* Recipe card & Expander Fix - VERBESSERTE LESBARKEIT */
    .stExpander {
        background-color: white !important;
        border-radius: 12px !important;
        border: 1px solid #e0d5c8 !important;
        margin-bottom: 1rem !important;
        overflow: hidden;
    }
    
    /* Header-Text im Expander (Rezeptname & Zeit) */
    .stExpander summary p {
        color: #2c1a0e !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    /* Hover-Effekt für den Header */
    .stExpander summary:hover {
        background-color: #fcf8f2 !important;
    }
    
    .stExpander [data-testid="stExpanderDetails"] {
        color: #2c1a0e !important;
        padding: 1.5rem !important;
    }

    /* Badge Styles */
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
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #d4845a;
        margin: 1.2rem 0 0.5rem 0;
        border-bottom: 1px solid #eee;
    }

    /* Sidebar - Dunkler Kontrast */
    section[data-testid="stSidebar"] {
        background-color: #2c1a0e !important;
    }
    section[data-testid="stSidebar"] .stMarkdown, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] .stSlider p {
        color: #f5e6d3 !important;
    }
    
    /* Input Fields in Sidebar */
    section[data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #3d2b1f !important;
        border-color: #4a3629 !important;
    }
    
    /* No results */
    .no-results {
        text-align: center;
        padding: 4rem 2rem;
        color: #8c6a4e;
    }

    /* Zutaten-Check Styles */
    .zutat-check-header {
        background: linear-gradient(135deg, #fdf6ec 0%, #fde8d8 100%);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e0d5c8;
    }
    .zutat-check-header h2 {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        color: #2c1a0e;
        margin: 0 0 0.3rem 0;
    }
    .zutat-check-header p {
        color: #8c6a4e;
        margin: 0;
        font-size: 0.95rem;
    }

    .match-full {
        background-color: #d6f0e0 !important;
        border-left: 4px solid #1e7a43 !important;
    }
    .match-partial {
        background-color: #fff9ed !important;
        border-left: 4px solid #d4845a !important;
    }

    .match-badge-full {
        background: #1e7a43;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .match-badge-partial {
        background: #d4845a;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .zutat-tag {
        display: inline-block;
        background: #fde8d8;
        color: #b5501e;
        border-radius: 12px;
        padding: 0.2rem 0.6rem;
        font-size: 0.78rem;
        margin: 0.1rem;
        font-weight: 600;
    }
    .zutat-tag-missing {
        display: inline-block;
        background: #f5e6e6;
        color: #9b3a3a;
        border-radius: 12px;
        padding: 0.2rem 0.6rem;
        font-size: 0.78rem;
        margin: 0.1rem;
        font-weight: 600;
        text-decoration: line-through;
        opacity: 0.7;
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


# ── Gewürze / Grundzutaten die ignoriert werden ───────────────────────────────
GEWUERZE_KEYWORDS = {
    "salz", "pfeffer", "zucker", "öl", "olivenöl", "butter", "essig",
    "senf", "paprika", "kurkuma", "kreuzkümmel", "zimt", "nelken",
    "lorbeer", "thymian", "rosmarin", "oregano", "basilikum", "petersilie",
    "schnittlauch", "dill", "muskat", "chili", "cayenne", "curry",
    "koriander", "ingwer", "knoblauch", "zwiebel", "gewürz", "brühe",
    "suppenwürze", "bouillon", "hefe", "backpulver", "natron", "vanille",
    "wasser", "mehl", "stärke", "speisestärke", "paniermehl", "semmelbrösel",
    "zucker", "honig", "sirup", "essig", "zitronensaft", "limettensaft",
    "worcester", "tabasco", "sojasoße", "sojasauce", "fischsauce",
    "sahne", "milch", "ei", "eier", "margarine",
}

# Kategorien für die Zutaten-Klassifikation
ZUTAT_KATEGORIEN = {
    "🥩 Fleisch & Geflügel": [
        "hähnchen", "huhn", "pute", "truthahn", "ente", "gans",
        "rind", "rindfleisch", "steak", "hack", "hackfleisch",
        "schwein", "schweinefleisch", "speck", "schinken", "wurst",
        "lamm", "lammfleisch", "kalb", "kalbfleisch", "wild", "hirsch",
        "rehfleisch", "filet", "schnitzel", "keule", "brust",
    ],
    "🐟 Fisch & Meeresfrüchte": [
        "lachs", "thunfisch", "kabeljau", "dorsch", "forelle", "hering",
        "makrele", "seelachs", "tilapia", "wolfsbarsch", "dorade",
        "garnelen", "shrimp", "muscheln", "tintenfisch", "oktopus",
        "fisch", "meeresfrüchte", "crevetten",
    ],
    "🥦 Gemüse": [
        "tomate", "tomaten", "gurke", "paprika", "zucchini", "aubergine",
        "brokkoli", "blumenkohl", "karotte", "möhre", "karotten", "möhren",
        "spinat", "salat", "rucola", "mangold", "kohl", "rotkohl",
        "weißkohl", "wirsing", "spitzkohl", "lauch", "porree",
        "fenchel", "sellerie", "rote bete", "rübe", "rettich",
        "radieschen", "avocado", "mais", "erbsen", "bohnen", "linsen",
        "kichererbsen", "champignons", "pilze", "kürbis",
        "süßkartoffel", "kartoffel", "kartoffeln", "spargel",
    ],
    "🍋 Obst": [
        "apfel", "birne", "banane", "erdbeere", "erdbeeren", "himbeere",
        "heidelbeere", "kirsche", "kirschen", "pfirsich", "aprikose",
        "mango", "ananas", "melone", "wassermelone", "orange", "zitrone",
        "limette", "grapefruit", "traube", "trauben", "feige", "pflaume",
        "zwetschge", "kiwi", "papaya", "litschi",
    ],
    "🧀 Milchprodukte & Käse": [
        "käse", "parmesan", "mozzarella", "gouda", "emmentaler",
        "feta", "brie", "camembert", "cheddar", "ricotta", "mascarpone",
        "frischkäse", "quark", "joghurt", "schmand", "crème fraîche",
        "sauerrahm", "kondensmilch",
    ],
    "🌾 Getreide, Nudeln & Reis": [
        "nudeln", "pasta", "spaghetti", "penne", "farfalle", "rigatoni",
        "lasagne", "tagliatelle", "reis", "risotto", "quinoa", "couscous",
        "bulgur", "polenta", "grieß", "haferflocken", "hafer", "brot",
        "toast", "brötchen", "tortilla", "wraps", "pita",
    ],
    "🥚 Eier & Tofu": [
        "tofu", "tempeh", "seitan", "sojajoghurt", "sojamilch",
        "hafermilch", "mandelmilch",
    ],
    "🥫 Konserven & Sonstiges": [
        "dosentomaten", "passierte tomaten", "tomatenmark", "kokosmilch",
        "bohnen dose", "linsen dose", "kichererbsen dose",
        "oliven", "kapern", "sardellen", "anchovis",
        "erbsen dose", "mais dose",
    ],
}


def ist_gewuerz(zutat: str) -> bool:
    zutat_lower = zutat.lower().strip()
    return any(gw in zutat_lower for gw in GEWUERZE_KEYWORDS)


def kategorisiere_zutat(zutat: str) -> str:
    zutat_lower = zutat.lower()
    for kategorie, keywords in ZUTAT_KATEGORIEN.items():
        if any(kw in zutat_lower for kw in keywords):
            return kategorie
    return "🔹 Weitere Zutaten"


def extrahiere_alle_zutaten(df: pd.DataFrame) -> dict:
    """Extrahiert alle Zutaten aus allen Rezepten, filtert Gewürze heraus."""
    alle_zutaten = set()
    for zutaten_str in df["Benötigte Zutaten"].dropna():
        items = [z.strip() for z in str(zutaten_str).replace("\n", ",").split(",") if z.strip()]
        for item in items:
            if not ist_gewuerz(item) and len(item) > 2:
                alle_zutaten.add(item)
    
    # Gruppiere nach Kategorie
    kategorisiert = {}
    for zutat in sorted(alle_zutaten):
        kat = kategorisiere_zutat(zutat)
        if kat not in kategorisiert:
            kategorisiert[kat] = []
        kategorisiert[kat].append(zutat)
    
    return kategorisiert


def berechne_matches(df: pd.DataFrame, vorhandene_zutaten: set) -> pd.DataFrame:
    """Berechnet für jedes Rezept wie viele Zutaten vorhanden sind."""
    if not vorhandene_zutaten:
        return pd.DataFrame()

    ergebnisse = []
    vorhandene_lower = {z.lower() for z in vorhandene_zutaten}

    for _, row in df.iterrows():
        zutaten_str = row.get("Benötigte Zutaten", "")
        if not zutaten_str:
            continue

        # Zutaten des Rezepts (ohne Gewürze)
        rezept_zutaten = [
            z.strip()
            for z in str(zutaten_str).replace("\n", ",").split(",")
            if z.strip() and not ist_gewuerz(z.strip()) and len(z.strip()) > 2
        ]

        if not rezept_zutaten:
            continue

        # Matching (tolerant: Teilstring-Vergleich)
        vorhanden = []
        fehlend = []
        for zutat in rezept_zutaten:
            zutat_lower = zutat.lower()
            matched = any(
                v in zutat_lower or zutat_lower in v
                for v in vorhandene_lower
            )
            if matched:
                vorhanden.append(zutat)
            else:
                fehlend.append(zutat)

        anzahl_gesamt = len(rezept_zutaten)
        anzahl_vorhanden = len(vorhanden)
        anteil = anzahl_vorhanden / anzahl_gesamt if anzahl_gesamt > 0 else 0

        if anzahl_vorhanden > 0:
            ergebnisse.append({
                "row": row,
                "vorhanden": vorhanden,
                "fehlend": fehlend,
                "anzahl_gesamt": anzahl_gesamt,
                "anzahl_vorhanden": anzahl_vorhanden,
                "anteil": anteil,
                "vollstaendig": len(fehlend) == 0,
            })

    if not ergebnisse:
        return pd.DataFrame()

    result_df = pd.DataFrame(ergebnisse)
    result_df = result_df.sort_values(["vollstaendig", "anteil"], ascending=[False, False])
    return result_df


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


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["🍽️ Alle Rezepte", "🛒 Zutaten-Check"])


# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 – Alle Rezepte (unverändert)
# ════════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Sidebar Filter ────────────────────────────────────────────────────────────
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
                st.markdown(badges, unsafe_allow_html=True)
                st.markdown("")

                col_l, col_r = st.columns([1, 2])

                with col_l:
                    st.markdown('<div class="section-label">🧂 Zutaten</div>', unsafe_allow_html=True)
                    if zutaten:
                        items = [z.strip() for z in str(zutaten).replace("\n", ",").split(",") if z.strip()]
                        for item in items:
                            st.markdown(f"• {item}")
                    else:
                        st.markdown("_Keine Zutaten angegeben_")

                    if equipment:
                        st.markdown('<div class="section-label">🔧 Equipment</div>', unsafe_allow_html=True)
                        eq_items = [e.strip() for e in str(equipment).replace("\n", ",").split(",") if e.strip()]
                        for eq in eq_items:
                            st.markdown(f"• {eq}")

                with col_r:
                    st.markdown('<div class="section-label">👨‍🍳 Zubereitung</div>', unsafe_allow_html=True)
                    if zubereitung:
                        steps = [s.strip() for s in str(zubereitung).split("\n") if s.strip()]
                        if len(steps) > 1:
                            for i, step in enumerate(steps, 1):
                                st.markdown(f"**{i}.** {step}")
                        else:
                            st.markdown(zubereitung)
                    else:
                        st.markdown("_Keine Zubereitung angegeben_")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 – Zutaten-Check
# ════════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown("""
    <div class="zutat-check-header">
        <h2>🛒 Was habe ich im Kühlschrank?</h2>
        <p>Wähle deine vorhandenen Zutaten aus – das Dashboard zeigt dir, welche Rezepte du kochen kannst. Gewürze und Grundzutaten werden automatisch ignoriert.</p>
    </div>
    """, unsafe_allow_html=True)

    # Alle Zutaten aus Rezepten extrahieren
    alle_zutaten_kategorisiert = extrahiere_alle_zutaten(df)

    # ── Zutaten-Auswahl ───────────────────────────────────────────────────────
    st.markdown("### 🧺 Meine Zutaten auswählen")

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 1, 1])
    with col_ctrl1:
        zutat_suche = st.text_input(
            "🔍 Zutat suchen",
            placeholder="z. B. Lachs, Tomate …",
            key="zutat_suche"
        )
    with col_ctrl2:
        st.markdown("<br>", unsafe_allow_html=True)
        alle_auswaehlen = st.button("✅ Alle auswählen", use_container_width=True)
    with col_ctrl3:
        st.markdown("<br>", unsafe_allow_html=True)
        alle_abwaehlen = st.button("❌ Alle abwählen", use_container_width=True)

    # Session State für ausgewählte Zutaten
    if "selected_zutaten" not in st.session_state:
        st.session_state.selected_zutaten = set()

    # Alle verfügbaren Zutaten flach
    alle_zutaten_flat = [z for zutaten in alle_zutaten_kategorisiert.values() for z in zutaten]

    if alle_auswaehlen:
        st.session_state.selected_zutaten = set(alle_zutaten_flat)
        st.rerun()

    if alle_abwaehlen:
        st.session_state.selected_zutaten = set()
        st.rerun()

    st.markdown("---")

    # Kategorien als aufklappbare Sektionen mit Checkboxen
    kategorien_sorted = sorted(alle_zutaten_kategorisiert.keys())

    for kategorie in kategorien_sorted:
        zutaten_in_kat = sorted(alle_zutaten_kategorisiert[kategorie])

        # Suchfilter anwenden
        if zutat_suche:
            zutaten_in_kat = [
                z for z in zutaten_in_kat
                if zutat_suche.lower() in z.lower()
            ]
            if not zutaten_in_kat:
                continue

        anzahl_ausgewaehlt = sum(1 for z in zutaten_in_kat if z in st.session_state.selected_zutaten)
        label = f"{kategorie}  ({anzahl_ausgewaehlt}/{len(zutaten_in_kat)} ausgewählt)"

        with st.expander(label, expanded=(zutat_suche != "")):
            # Alle / Keine Buttons pro Kategorie
            btn_col1, btn_col2, _ = st.columns([1, 1, 4])
            with btn_col1:
                if st.button(f"Alle", key=f"alle_{kategorie}", use_container_width=True):
                    st.session_state.selected_zutaten.update(zutaten_in_kat)
                    st.rerun()
            with btn_col2:
                if st.button(f"Keine", key=f"keine_{kategorie}", use_container_width=True):
                    st.session_state.selected_zutaten -= set(zutaten_in_kat)
                    st.rerun()

            st.markdown("")

            # Checkboxen in 3 Spalten
            n_cols = 3
            cols = st.columns(n_cols)
            for i, zutat in enumerate(zutaten_in_kat):
                with cols[i % n_cols]:
                    checked = zutat in st.session_state.selected_zutaten
                    if st.checkbox(zutat, value=checked, key=f"cb_{zutat}"):
                        st.session_state.selected_zutaten.add(zutat)
                    else:
                        st.session_state.selected_zutaten.discard(zutat)

    # ── Zusammenfassung der Auswahl ───────────────────────────────────────────
    st.markdown("---")

    vorhandene_zutaten = st.session_state.selected_zutaten

    if vorhandene_zutaten:
        st.markdown(f"**Ausgewählte Zutaten ({len(vorhandene_zutaten)}):** " +
                    " ".join([f'<span class="zutat-tag">{z}</span>' for z in sorted(vorhandene_zutaten)]),
                    unsafe_allow_html=True)
        st.markdown("")

    # ── Ergebnisse ────────────────────────────────────────────────────────────
    st.markdown("### 🍳 Passende Rezepte")

    if not vorhandene_zutaten:
        st.info("👆 Wähle oben deine vorhandenen Zutaten aus, um passende Rezepte zu sehen.")
    else:
        matches = berechne_matches(df, vorhandene_zutaten)

        if matches.empty:
            st.markdown("""
            <div class="no-results">
                <h2>Keine passenden Rezepte 🥺</h2>
                <p>Mit den ausgewählten Zutaten können leider keine Rezepte gekocht werden. Füge mehr Zutaten hinzu!</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            vollstaendig = matches[matches["vollstaendig"] == True]
            partiell = matches[matches["vollstaendig"] == False]

            # Metriken
            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric("✅ Sofort kochbar", len(vollstaendig))
            with mc2:
                st.metric("🔸 Fast vollständig", len(partiell))
            with mc3:
                st.metric("🍽️ Rezepte gesamt", len(matches))

            st.markdown("---")

            # ── Vollständige Matches ──────────────────────────────────────────
            if not vollstaendig.empty:
                st.markdown("#### ✅ Diese Rezepte kannst du sofort kochen!")
                for _, match in vollstaendig.iterrows():
                    row = match["row"]
                    name = row.get("Name des Gerichts", "Unbekannt")
                    zeit = row.get("Benötigte Zeit", 0)
                    vorhanden = match["vorhanden"]
                    anzahl_gesamt = match["anzahl_gesamt"]

                    zutat_tags = " ".join([f'<span class="zutat-tag">{z}</span>' for z in vorhanden])

                    with st.expander(f"✅ {name}  •  ⏱️ {zeit} min", expanded=False):
                        st.markdown(
                            f'<span class="match-badge-full">Alle {anzahl_gesamt} Zutaten vorhanden</span>',
                            unsafe_allow_html=True
                        )
                        st.markdown("")
                        st.markdown('<div class="section-label">🧂 Zutaten (alle vorhanden)</div>', unsafe_allow_html=True)
                        st.markdown(zutat_tags, unsafe_allow_html=True)
                        st.markdown("")

                        zubereitung = row.get("Zubereitung", "")
                        if zubereitung:
                            st.markdown('<div class="section-label">👨‍🍳 Zubereitung</div>', unsafe_allow_html=True)
                            steps = [s.strip() for s in str(zubereitung).split("\n") if s.strip()]
                            if len(steps) > 1:
                                for i, step in enumerate(steps, 1):
                                    st.markdown(f"**{i}.** {step}")
                            else:
                                st.markdown(zubereitung)

            # ── Partielle Matches ─────────────────────────────────────────────
            if not partiell.empty:
                st.markdown("---")
                st.markdown("#### 🔸 Fast dabei – nur noch ein paar Zutaten fehlen")

                # Sortieroption
                sort_col1, sort_col2 = st.columns([2, 2])
                with sort_col1:
                    min_anteil = st.slider(
                        "Mindestanteil vorhandener Zutaten",
                        min_value=0,
                        max_value=100,
                        value=50,
                        step=10,
                        format="%d%%",
                        key="min_anteil_slider"
                    )

                partiell_gefiltert = partiell[partiell["anteil"] >= min_anteil / 100]

                if partiell_gefiltert.empty:
                    st.info(f"Keine Rezepte mit mindestens {min_anteil}% der Zutaten vorhanden.")
                else:
                    for _, match in partiell_gefiltert.iterrows():
                        row = match["row"]
                        name = row.get("Name des Gerichts", "Unbekannt")
                        zeit = row.get("Benötigte Zeit", 0)
                        vorhanden = match["vorhanden"]
                        fehlend = match["fehlend"]
                        anzahl_gesamt = match["anzahl_gesamt"]
                        anzahl_vorhanden = match["anzahl_vorhanden"]
                        anteil_pct = int(match["anteil"] * 100)

                        vorhanden_tags = " ".join([f'<span class="zutat-tag">{z}</span>' for z in vorhanden])
                        fehlend_tags = " ".join([f'<span class="zutat-tag-missing">{z}</span>' for z in fehlend])

                        with st.expander(
                            f"🔸 {name}  •  ⏱️ {zeit} min  •  {anzahl_vorhanden}/{anzahl_gesamt} Zutaten ({anteil_pct}%)",
                            expanded=False
                        ):
                            st.markdown(
                                f'<span class="match-badge-partial">{anzahl_vorhanden} von {anzahl_gesamt} Zutaten vorhanden ({anteil_pct}%)</span>',
                                unsafe_allow_html=True
                            )
                            st.markdown("")

                            col_v, col_f = st.columns(2)
                            with col_v:
                                st.markdown('<div class="section-label">✅ Vorhanden</div>', unsafe_allow_html=True)
                                st.markdown(vorhanden_tags if vorhanden_tags else "_–_", unsafe_allow_html=True)
                            with col_f:
                                st.markdown('<div class="section-label">❌ Fehlend</div>', unsafe_allow_html=True)
                                st.markdown(fehlend_tags if fehlend_tags else "_–_", unsafe_allow_html=True)
