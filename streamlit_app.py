"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         REZEPT-DASHBOARD PRO – High-End Version                             ║
║         Erstellt auf Basis des bestehenden Dashboards                       ║
║                                                                              ║
║  NEU in dieser Version:                                                     ║
║  ✦ Hero-Header mit Verlauf & Premium-Typografie                             ║
║  ✦ Favoriten-Funktion (Session State)                                       ║
║  ✦ Portionsrechner mit Regex-basierter Mengenumrechnung                     ║
║  ✦ Interaktive Schritt-Checkliste (Koch-Modus)                              ║
║  ✦ Verbessertes Singular/Plural-Matching (Tomate/Tomaten)                   ║
║  ✦ Koch-Tipps Sektion mit Gold-Akzenten                                     ║
║  ✦ Druck-Modus CSS für DIN-A4                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🍽️ Rezept-Dashboard Pro",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── HIGH-END CSS ──────────────────────────────────────────────────────────────
# Komplettes Design-System mit:
# - Google Fonts (Playfair Display + Inter)
# - Hero-Gradient-Header
# - Gold-Akzent-System
# - Micro-Interactions (Hover-Effekte)
# - Druck-Modus (@media print)
# - Checklisten-Styling
# - Portionsrechner-UI
st.markdown("""
<style>
    /* ── FONTS ── */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Inter:wght@300;400;500;600&display=swap');

    /* ── RESET & BASE ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1a0e06;
    }

    /* ── GLOBALE LESBARKEIT: alle nativen Streamlit-Texte ── */
    /* Stellt sicher, dass kein Element mit dunklem Hintergrund
       unsichtbaren dunklen Text trägt */
    p, span, label, div, li, h1, h2, h3, h4, h5, h6 {
        color: inherit;
    }

    /* Streamlit-interne Markdown-Texte immer dunkel auf hellem Grund */
    .stMarkdown p, .stMarkdown span, .stMarkdown li {
        color: #1a0e06 !important;
    }

    /* ── APP BACKGROUND ── */
    .stApp {
        background: linear-gradient(160deg, #fdf6ec 0%, #fef9f4 60%, #fdf0e0 100%);
    }

    /* ══════════════════════════════════════════════════════
       HERO HEADER – Das emotionale Herzstück
       Ein sanfter Verlauf suggeriert Wärme und Appetit.
    ══════════════════════════════════════════════════════ */
    .hero-header {
        background: linear-gradient(135deg, #2c1a0e 0%, #4a2c1a 40%, #7a4020 70%, #d4845a 100%);
        border-radius: 20px;
        padding: 3rem 3.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(44, 26, 14, 0.25);
    }
    /* Dekoratives Muster im Hero */
    .hero-header::before {
        content: "";
        position: absolute;
        top: -50%;
        right: -10%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-header::after {
        content: "";
        position: absolute;
        bottom: -30%;
        left: 20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(212, 132, 90, 0.2) 0%, transparent 70%);
        border-radius: 50%;
    }
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 3.2rem;
        font-weight: 700;
        color: #fff;
        margin: 0 0 0.4rem 0;
        line-height: 1.15;
        letter-spacing: -0.5px;
        position: relative;
        z-index: 1;
    }
    .hero-subtitle {
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        color: rgba(255,255,255,0.75);
        margin: 0 0 1.5rem 0;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    .hero-stats {
        display: flex;
        gap: 2rem;
        position: relative;
        z-index: 1;
    }
    .hero-stat {
        text-align: center;
    }
    .hero-stat-number {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: #ffd580;
        display: block;
        line-height: 1;
    }
    .hero-stat-label {
        font-size: 0.75rem;
        color: rgba(255,255,255,0.65);
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }

    /* ══════════════════════════════════════════════════════
       METRIC CARDS
    ══════════════════════════════════════════════════════ */
    [data-testid="stMetricValue"] {
        color: #2c1a0e !important;
        font-family: 'Playfair Display', serif !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: #8c6a4e !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-size: 0.75rem !important;
    }

    /* ══════════════════════════════════════════════════════
       RECIPE EXPANDER – „Weich" & Premium
       Micro-Interaction: sanfter Hover-Übergang
    ══════════════════════════════════════════════════════ */
    .stExpander {
        background-color: #ffffff !important;
        border-radius: 14px !important;
        border: 1px solid #e8ddd4 !important;
        margin-bottom: 0.85rem !important;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(44, 26, 14, 0.06);
        transition: box-shadow 0.25s ease, transform 0.2s ease !important;
    }
    .stExpander:hover {
        box-shadow: 0 6px 20px rgba(44, 26, 14, 0.12) !important;
        transform: translateY(-1px);
    }
    .stExpander summary {
        transition: background-color 0.2s ease !important;
    }
    .stExpander summary:hover {
        background-color: #fdf6ec !important;
    }
    .stExpander summary p {
        color: #2c1a0e !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stExpander [data-testid="stExpanderDetails"] {
        color: #1a0e06 !important;
        padding: 1.5rem 1.8rem !important;
    }
    /* Alle Texte INNERHALB eines Expanders explizit dunkel */
    .stExpander [data-testid="stExpanderDetails"] p,
    .stExpander [data-testid="stExpanderDetails"] span,
    .stExpander [data-testid="stExpanderDetails"] label,
    .stExpander [data-testid="stExpanderDetails"] div,
    .stExpander [data-testid="stExpanderDetails"] li {
        color: #1a0e06 !important;
    }
    /* Checkbox-Labels überall lesbar */
    [data-testid="stCheckbox"] label,
    [data-testid="stCheckbox"] span,
    [data-testid="stCheckbox"] p {
        color: #1a0e06 !important;
        font-size: 0.92rem !important;
    }

    /* ══════════════════════════════════════════════════════
       BADGES
    ══════════════════════════════════════════════════════ */
    .badge {
        display: inline-block;
        padding: 0.22rem 0.65rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        margin: 0.15rem;
        font-family: 'Inter', sans-serif;
    }
    .badge-kategorie  { background: #fde8d8; color: #b5501e; }
    .badge-ernaehrung { background: #d6f0e0; color: #1e7a43; }
    .badge-saison     { background: #dce9fb; color: #1e4d8c; }
    .badge-aufwand-leicht { background: #d6f0e0; color: #1e7a43; }
    .badge-aufwand-mittel { background: #fff3cd; color: #8a6000; }
    .badge-aufwand-schwer { background: #fde8d8; color: #b5501e; }

    /* ══════════════════════════════════════════════════════
       FAVORITEN-BADGE (Herz)
    ══════════════════════════════════════════════════════ */
    .fav-badge {
        display: inline-block;
        background: linear-gradient(135deg, #ff6b9d, #c44569);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.4px;
    }

    /* ══════════════════════════════════════════════════════
       SECTION LABELS
    ══════════════════════════════════════════════════════ */
    .section-label {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #d4845a;
        margin: 1.3rem 0 0.6rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #f0e8de;
        font-family: 'Inter', sans-serif;
    }

    /* ══════════════════════════════════════════════════════
       ZUTAT GRID – Übersichtliche Darstellung
    ══════════════════════════════════════════════════════ */
    .zutat-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 0.4rem;
        margin-top: 0.5rem;
    }
    .zutat-item {
        background: #fdf6ec;
        border: 1px solid #ead8c5;
        border-radius: 8px;
        padding: 0.35rem 0.6rem;
        font-size: 0.82rem;
        color: #2c1a0e;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    .zutat-menge {
        font-weight: 700;
        color: #d4845a;
        white-space: nowrap;
    }
    .zutat-name {
        color: #4a3020;
    }

    /* ══════════════════════════════════════════════════════
       INTERAKTIVE CHECKLISTE – Koch-Modus
       Schritte können als „erledigt" markiert werden
    ══════════════════════════════════════════════════════ */
    .step-done {
        opacity: 0.45;
        text-decoration: line-through;
        color: #8c6a4e !important;
    }
    .step-active {
        color: #2c1a0e;
    }
    .step-number {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        background: linear-gradient(135deg, #d4845a, #b5501e);
        color: white;
        border-radius: 50%;
        font-size: 0.7rem;
        font-weight: 700;
        margin-right: 0.5rem;
        flex-shrink: 0;
    }
    .step-number-done {
        background: #c8dfc8 !important;
        color: #1e7a43 !important;
    }

    /* ══════════════════════════════════════════════════════
       GOLD-AKZENT: Koch-Tipps Box
       Visuelle Hervorhebung mit warmem Gold
    ══════════════════════════════════════════════════════ */
    .tipp-box {
        background: linear-gradient(135deg, #fffbf0, #fff8e1);
        border: 1px solid #f0d080;
        border-left: 4px solid #d4a017;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-top: 1rem;
    }
    .tipp-box-title {
        font-family: 'Playfair Display', serif;
        font-size: 0.9rem;
        font-weight: 700;
        color: #8a6000;
        margin: 0 0 0.4rem 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .tipp-box-text {
        font-size: 0.88rem;
        color: #5a4000;
        line-height: 1.6;
        margin: 0;
    }

    /* ══════════════════════════════════════════════════════
       PORTIONSRECHNER – Inline UI
    ══════════════════════════════════════════════════════ */
    .portions-bar {
        background: linear-gradient(135deg, #2c1a0e, #4a2c1a);
        border-radius: 10px;
        padding: 0.8rem 1.2rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 0.8rem 0;
    }
    .portions-label {
        color: rgba(255,255,255,0.8);
        font-size: 0.82rem;
        font-weight: 500;
        white-space: nowrap;
    }

    /* ══════════════════════════════════════════════════════
       SIDEBAR
    ══════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1008 0%, #2c1a0e 100%) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stSlider p,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #f5e6d3 !important;
    }
    /* Multiselect-Tags und Dropdown-Texte in der Sidebar */
    section[data-testid="stSidebar"] [data-baseweb="tag"] span,
    section[data-testid="stSidebar"] [data-baseweb="select"] span,
    section[data-testid="stSidebar"] [data-baseweb="select"] div {
        color: #f5e6d3 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="input"] {
        background-color: #3d2b1f !important;
        border-color: #5a3e2e !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="input"] input {
        color: #f5e6d3 !important;
    }
    section[data-testid="stSidebar"] h2 {
        color: #ffd580 !important;
        font-family: 'Playfair Display', serif !important;
    }
    /* Sidebar-Expander (Zutaten-Kategorien): Text muss lesbar bleiben */
    section[data-testid="stSidebar"] .stExpander summary p {
        color: #f5e6d3 !important;
    }
    section[data-testid="stSidebar"] .stExpander {
        background-color: #3d2b1f !important;
        border-color: #5a3e2e !important;
    }
    section[data-testid="stSidebar"] .stExpander [data-testid="stExpanderDetails"] p,
    section[data-testid="stSidebar"] .stExpander [data-testid="stExpanderDetails"] span,
    section[data-testid="stSidebar"] .stExpander [data-testid="stExpanderDetails"] label,
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] label,
    section[data-testid="stSidebar"] [data-testid="stCheckbox"] span {
        color: #f5e6d3 !important;
    }

    /* ══════════════════════════════════════════════════════
       ZUTATEN-CHECK UI
    ══════════════════════════════════════════════════════ */
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
        font-size: 0.92rem;
        font-family: 'Inter', sans-serif;
    }
    .match-badge-full {
        background: linear-gradient(135deg, #1e7a43, #27ae60);
        color: white;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .match-badge-partial {
        background: linear-gradient(135deg, #d4845a, #b5501e);
        color: white;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.72rem;
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
    .no-results {
        text-align: center;
        padding: 4rem 2rem;
        color: #8c6a4e;
    }

    /* ══════════════════════════════════════════════════════
       FAVORITEN-LEISTE
    ══════════════════════════════════════════════════════ */
    .fav-bar {
        background: linear-gradient(135deg, #fff8f0, #ffeedd);
        border: 1px solid #e8c8a0;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1.2rem;
        font-family: 'Inter', sans-serif;
    }

    /* ══════════════════════════════════════════════════════
       DRUCK-MODUS – Optimiert für DIN-A4
       Alle farbigen Hintergründe werden entfernt,
       Schriftgrößen angepasst, Sidebar ausgeblendet.
    ══════════════════════════════════════════════════════ */
    @media print {
        section[data-testid="stSidebar"],
        .stButton,
        [data-testid="stToolbar"],
        [data-testid="stHeader"],
        .stTabs [role="tablist"],
        footer { display: none !important; }

        .stApp, html, body {
            background: white !important;
            color: black !important;
        }
        .hero-header {
            background: #2c1a0e !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        .stExpander {
            box-shadow: none !important;
            border: 1px solid #ccc !important;
            page-break-inside: avoid;
        }
        .section-label { color: #555 !important; }
        .badge { border: 1px solid #ccc !important; }
        [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"] { color: black !important; }
        .zutat-item { background: #f9f9f9 !important; }
        .tipp-box { background: #fffde7 !important; -webkit-print-color-adjust: exact; }

        /* DIN-A4 Seitenränder */
        @page {
            size: A4 portrait;
            margin: 18mm 15mm 18mm 15mm;
        }
    }

    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE SHEETS CONNECTION
# Caching mit ttl=300s → kein unnötiger API-Abruf bei jedem Rerun
# ══════════════════════════════════════════════════════════════════════════════
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
    for col in ["Aufwand", "Kategorie", "Ernährungsform", "Equipment", "Saison-Check", "Koch-Tipps"]:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
    return df


# ══════════════════════════════════════════════════════════════════════════════
# PORTIONSRECHNER – PRO-FEATURE
# Nutzt Regex, um Zahlen/Mengen in Zutatstrings zu erkennen und zu skalieren.
# Unterstützt: "200g", "2 EL", "1/2 TL", "3-4", Dezimalzahlen
# ══════════════════════════════════════════════════════════════════════════════
def skaliere_zutat(zutat_str: str, faktor: float) -> str:
    """
    Multipliziert alle Zahlen in einem Zutaten-String mit dem Faktor.
    Beispiel: "200g Mehl" × 1.5 → "300g Mehl"
    Beispiel: "1/2 TL Salz" × 2 → "1.0 TL Salz"
    """
    def ersetze_zahl(match):
        original = match.group(0)
        # Brüche auflösen (1/2 → 0.5)
        if "/" in original:
            teile = original.split("/")
            try:
                wert = float(teile[0]) / float(teile[1])
            except:
                return original
        # Bereich (3-4) → nimm erstes
        elif "-" in original and not original.startswith("-"):
            try:
                wert = float(original.split("-")[0])
            except:
                return original
        else:
            try:
                wert = float(original.replace(",", "."))
            except:
                return original

        neuer_wert = wert * faktor
        # Schöne Ausgabe: ganze Zahlen ohne Dezimalstellen
        if neuer_wert == int(neuer_wert):
            return str(int(neuer_wert))
        else:
            return f"{neuer_wert:.1f}".replace(".", ",")

    # Regex: Brüche, Bereiche, Dezimalzahlen, ganze Zahlen
    return re.sub(r"\d+/\d+|\d+-\d+|\d+[,\.]\d+|\d+", ersetze_zahl, zutat_str)


def parse_zutat_display(zutat_str: str) -> tuple[str, str]:
    """
    Trennt Menge+Einheit vom Zutatsnamen für das Grid-Display.
    Gibt (menge_str, name_str) zurück.
    Beispiel: "200g Parmesan" → ("200g", "Parmesan")
    Beispiel: "2 EL Olivenöl" → ("2 EL", "Olivenöl")
    Beispiel: "Parmesan" → ("", "Parmesan")
    """
    EINHEITEN = r"(?:g|kg|ml|l|EL|TL|Prise|Stück|Stk|Scheib\w*|Dose\w*|Bund|Pkg|Pckg|cm|mm|Glas|Dose|Becher|Tasse|Pck)\b"
    pattern = rf"^(\d+[,\./]?\d*\s*(?:{EINHEITEN})?)\s*(.+)$"
    match = re.match(pattern, zutat_str.strip(), re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "", zutat_str.strip()


# ══════════════════════════════════════════════════════════════════════════════
# SCHRITT-PARSER – Zubereitung in einzelne Schritte aufteilen
# Unterstützt zwei Formate aus Google Sheets:
#   A) Zeilenumbrüche: "Schritt 1\nSchritt 2\n..."
#   B) Nummerierte Liste in einer Zeile: "1. Zwiebeln... 2. Öl... 3. ..."
# ══════════════════════════════════════════════════════════════════════════════
def parse_zubereitung_steps(zubereitung_str: str) -> list[str]:
    """
    Gibt eine Liste der einzelnen Zubereitungsschritte zurück.
    Erkennungslogik:
    1. Erst per Zeilenumbruch splitten (Format A).
    2. Falls nur 1 Zeile → versuche nummerierte Schritte via Regex zu finden (Format B).
       Muster: "1. Text 2. Text" oder "1) Text 2) Text"
    """
    # Format A: Zeilenumbrüche
    by_newline = [s.strip() for s in str(zubereitung_str).split("\n") if s.strip()]
    if len(by_newline) > 1:
        return by_newline

    # Format B: Nummerierung in einem langen String
    # Regex: Trenne an "Ziffer. " oder "Ziffer) " am Anfang eines Schritts
    text = str(zubereitung_str).strip()
    # Splitpunkte finden: "2. ", "3. " usw. (aber NICHT "z. B." = Kleinbuchstabe)
    parts = re.split(r'(?<!\w)(\d+[\.\)]\s+)', text)
    # parts sieht aus wie: ['', '1. ', 'Schritt eins ', '2. ', 'Schritt zwei']
    # Zusammenbauen: Nummer + Text wieder verbinden
    steps = []
    i = 1
    while i < len(parts) - 1:
        nummer = parts[i].strip()
        inhalt = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if inhalt:
            steps.append(f"{nummer} {inhalt}")
        i += 2

    if len(steps) > 1:
        return steps

    # Fallback: gesamter Text als ein Schritt
    return [text] if text else []


# ══════════════════════════════════════════════════════════════════════════════
# PLURAL/SINGULAR MATCHING – PRO-FEATURE
# Verbesserte Matching-Logik: "Tomate" matcht auch "Tomaten" und umgekehrt.
# Funktioniert für häufige deutsche Pluralformen (en, e, er, s)
# ══════════════════════════════════════════════════════════════════════════════
def normalisiere_wort(wort: str) -> str:
    """
    Reduziert ein deutsches Wort auf seinen wahrscheinlichen Wortstamm,
    indem gängige Pluralendungen entfernt werden.
    Tomate → tomat | Tomaten → tomat | Kartoffel → kartoffel | Kartoffeln → kartoffel
    """
    w = wort.lower().strip()
    # Reihenfolge ist wichtig: längste Endung zuerst prüfen
    for endung in ["nen", "ien", "ern", "chen", "lein", "en", "er", "es", "e", "s"]:
        if w.endswith(endung) and len(w) - len(endung) >= 3:
            return w[:-len(endung)]
    return w


def zutaten_match(rezept_zutat: str, vorhandene_lower: set) -> bool:
    """
    Mehrstufige Matching-Strategie:
    1. Direkte Teilstring-Übereinstimmung (wie bisher)
    2. Stamm-basierter Vergleich (Singular/Plural)
    """
    rz_lower = rezept_zutat.lower()
    rz_stamm = normalisiere_wort(rz_lower)

    for v in vorhandene_lower:
        v_stamm = normalisiere_wort(v)
        # Direktes Matching (original)
        if v in rz_lower or rz_lower in v:
            return True
        # Stamm-Matching (NEU)
        if len(rz_stamm) >= 4 and len(v_stamm) >= 4:
            if rz_stamm in v_stamm or v_stamm in rz_stamm:
                return True
    return False


# ══════════════════════════════════════════════════════════════════════════════
# GEWÜRZE & KATEGORIEN (unverändert aus Original)
# ══════════════════════════════════════════════════════════════════════════════
GEWUERZE_KEYWORDS = {
    "salz", "pfeffer", "zucker", "öl", "olivenöl", "butter", "essig",
    "senf", "paprika", "kurkuma", "kreuzkümmel", "zimt", "nelken",
    "lorbeer", "thymian", "rosmarin", "oregano", "basilikum", "petersilie",
    "schnittlauch", "dill", "muskat", "chili", "cayenne", "curry",
    "koriander", "ingwer", "knoblauch", "zwiebel", "gewürz", "brühe",
    "suppenwürze", "bouillon", "hefe", "backpulver", "natron", "vanille",
    "wasser", "mehl", "stärke", "speisestärke", "paniermehl", "semmelbrösel",
    "honig", "sirup", "zitronensaft", "limettensaft",
    "worcester", "tabasco", "sojasoße", "sojasauce", "fischsauce",
    "sahne", "milch", "ei", "eier", "margarine",
}

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
        "apfel", "birne", "banane", "erdbeere", "himbeere",
        "heidelbeere", "kirsche", "pfirsich", "aprikose",
        "mango", "ananas", "melone", "wassermelone", "orange", "zitrone",
        "limette", "grapefruit", "traube", "feige", "pflaume",
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
    "🥚 Tofu & Pflanzliches": [
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
    alle_zutaten = set()
    for zutaten_str in df["Benötigte Zutaten"].dropna():
        items = [z.strip() for z in str(zutaten_str).replace("\n", ",").split(",") if z.strip()]
        for item in items:
            if not ist_gewuerz(item) and len(item) > 2:
                alle_zutaten.add(item)
    kategorisiert = {}
    for zutat in sorted(alle_zutaten):
        kat = kategorisiere_zutat(zutat)
        if kat not in kategorisiert:
            kategorisiert[kat] = []
        kategorisiert[kat].append(zutat)
    return kategorisiert


def berechne_matches(df: pd.DataFrame, vorhandene_zutaten: set) -> pd.DataFrame:
    """
    Verbesserte Matching-Logik mit Singular/Plural-Erkennung.
    Nutzt die neue zutaten_match()-Funktion statt simplem Teilstring-Check.
    """
    if not vorhandene_zutaten:
        return pd.DataFrame()

    ergebnisse = []
    vorhandene_lower = {z.lower() for z in vorhandene_zutaten}

    for _, row in df.iterrows():
        zutaten_str = row.get("Benötigte Zutaten", "")
        if not zutaten_str:
            continue

        rezept_zutaten = [
            z.strip()
            for z in str(zutaten_str).replace("\n", ",").split(",")
            if z.strip() and not ist_gewuerz(z.strip()) and len(z.strip()) > 2
        ]
        if not rezept_zutaten:
            continue

        vorhanden, fehlend = [], []
        for zutat in rezept_zutaten:
            if zutaten_match(zutat, vorhandene_lower):
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


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INITIALISIERUNG
# ══════════════════════════════════════════════════════════════════════════════
if "favoriten" not in st.session_state:
    # Set mit den Namen der favorisierten Rezepte
    st.session_state.favoriten = set()

if "completed_steps" not in st.session_state:
    # Dict: {rezept_name: set(step_indices)} – markierte Kochschritte
    st.session_state.completed_steps = {}

if "selected_zutaten" not in st.session_state:
    st.session_state.selected_zutaten = set()


# ══════════════════════════════════════════════════════════════════════════════
# HILFSFUNKTIONEN
# ══════════════════════════════════════════════════════════════════════════════
def aufwand_class(aufwand: str) -> str:
    mapping = {"Leicht": "leicht", "Mittel": "mittel", "Schwer": "schwer"}
    return f"badge-aufwand-{mapping.get(aufwand, 'mittel')}"


def toggle_favorit(name: str):
    """Fügt ein Rezept zu Favoriten hinzu oder entfernt es."""
    if name in st.session_state.favoriten:
        st.session_state.favoriten.discard(name)
    else:
        st.session_state.favoriten.add(name)


def rendere_rezept_karte(row, idx_key: str, zeige_portionsrechner: bool = True):
    """
    Zentrale Funktion zum Rendern einer Rezeptkarte.
    Wird in Tab 1 und Tab 2 wiederverwendet.

    NEU:
    - Favoriten-Button (❤️/🤍) mit Session State
    - Portionsrechner (Regex-basiert)
    - Interaktive Schritt-Checkliste
    - Koch-Tipps Box (gold)
    - Zutat-Grid
    """
    name        = row.get("Name des Gerichts", "Unbekannt")
    zeit        = row.get("Benötigte Zeit", 0)
    aufwand     = row.get("Aufwand", "")
    kategorie   = row.get("Kategorie", "")
    ernaehrung  = row.get("Ernährungsform", "")
    saison      = row.get("Saison-Check", "")
    equipment   = row.get("Equipment", "")
    zutaten     = row.get("Benötigte Zutaten", "")
    zubereitung = row.get("Zubereitung", "")
    tipps       = row.get("Koch-Tipps", "") if "Koch-Tipps" in row.index else ""

    ist_favorit = name in st.session_state.favoriten
    fav_icon = "❤️" if ist_favorit else "🤍"
    fav_badge = '<span class="fav-badge">❤️ Favorit</span> ' if ist_favorit else ""

    # Badges
    badges = fav_badge
    if kategorie:
        badges += f'<span class="badge badge-kategorie">{kategorie}</span>'
    if ernaehrung:
        badges += f'<span class="badge badge-ernaehrung">{ernaehrung}</span>'
    if saison:
        badges += f'<span class="badge badge-saison">{saison}</span>'
    if aufwand:
        badges += f'<span class="badge {aufwand_class(aufwand)}">{aufwand}</span>'

    expander_label = f"{'❤️ ' if ist_favorit else '🍽️ '}{name}  •  ⏱️ {zeit} min"

    with st.expander(expander_label, expanded=False):
        st.markdown(badges, unsafe_allow_html=True)
        st.markdown("")

        # ── Favoriten-Button ──────────────────────────────────────────────
        fav_col, _ = st.columns([1, 5])
        with fav_col:
            if st.button(
                f"{fav_icon} {'Entfernen' if ist_favorit else 'Favorit'}",
                key=f"fav_{idx_key}_{name}",
                use_container_width=True,
                help="Rezept zu Favoriten hinzufügen / entfernen"
            ):
                toggle_favorit(name)
                st.rerun()

        st.markdown("---")

        # ── Portionsrechner (PRO-FEATURE) ─────────────────────────────────
        # Standard-Portionen: 4 (kann im Sheet definiert sein)
        base_portionen = int(row.get("Portionen", 4)) if "Portionen" in row.index else 4
        if base_portionen == 0:
            base_portionen = 4

        if zeige_portionsrechner and zutaten:
            port_col1, port_col2 = st.columns([2, 4])
            with port_col1:
                neue_portionen = st.number_input(
                    "🍽️ Portionen",
                    min_value=1,
                    max_value=20,
                    value=base_portionen,
                    step=1,
                    key=f"portionen_{idx_key}_{name}",
                    help=f"Originalrezept für {base_portionen} Portionen. Zutatenmengen werden automatisch umgerechnet."
                )
            faktor = neue_portionen / base_portionen
            with port_col2:
                if faktor != 1.0:
                    st.info(
                        f"Faktor: ×{faktor:.2f} — Mengen werden auf **{neue_portionen} Portionen** umgerechnet",
                        icon="🔢"
                    )
        else:
            faktor = 1.0
            neue_portionen = base_portionen

        # ── Layout: Links Zutaten, Rechts Zubereitung ─────────────────────
        col_l, col_r = st.columns([1, 2])

        with col_l:
            # ── ZUTATEN-GRID ──────────────────────────────────────────────
            st.markdown('<div class="section-label">🧂 Zutaten</div>', unsafe_allow_html=True)

            if zutaten:
                items = [z.strip() for z in str(zutaten).replace("\n", ",").split(",") if z.strip()]

                grid_html = '<div class="zutat-grid">'
                for item in items:
                    # Portionsrechner: Mengen skalieren
                    if faktor != 1.0:
                        item_skaliert = skaliere_zutat(item, faktor)
                    else:
                        item_skaliert = item

                    menge, zutat_name = parse_zutat_display(item_skaliert)
                    if menge:
                        grid_html += (
                            f'<div class="zutat-item">'
                            f'<span class="zutat-menge">{menge}</span>'
                            f'<span class="zutat-name">{zutat_name}</span>'
                            f'</div>'
                        )
                    else:
                        grid_html += f'<div class="zutat-item"><span class="zutat-name">{zutat_name}</span></div>'
                grid_html += '</div>'
                st.markdown(grid_html, unsafe_allow_html=True)
            else:
                st.markdown("_Keine Zutaten angegeben_")

            # ── Equipment ─────────────────────────────────────────────────
            if equipment:
                st.markdown('<div class="section-label">🔧 Equipment</div>', unsafe_allow_html=True)
                eq_items = [e.strip() for e in str(equipment).replace("\n", ",").split(",") if e.strip()]
                for eq in eq_items:
                    st.markdown(f"• {eq}")

        with col_r:
            # ── INTERAKTIVE SCHRITT-CHECKLISTE (PRO-FEATURE) ──────────────
            st.markdown('<div class="section-label">👨‍🍳 Zubereitung</div>', unsafe_allow_html=True)

            if zubereitung:
                # parse_zubereitung_steps erkennt sowohl Zeilenumbrüche
                # als auch nummerierte Schritte in einem einzigen String
                steps = parse_zubereitung_steps(zubereitung)

                if len(steps) > 1:
                    # Initialisiere Fortschritts-Set für dieses Rezept
                    key = f"steps_{name}"
                    if key not in st.session_state.completed_steps:
                        st.session_state.completed_steps[key] = set()

                    done_steps = st.session_state.completed_steps[key]
                    fertig = len(done_steps)
                    gesamt = len(steps)

                    # Fortschrittsanzeige
                    if fertig > 0:
                        st.progress(fertig / gesamt, text=f"{fertig}/{gesamt} Schritte erledigt")

                    # Schritte als Checkboxen – jeder Schritt in eigener Zeile
                    for i, step in enumerate(steps):
                        is_done = i in done_steps
                        checked = st.checkbox(
                            step,
                            value=is_done,
                            key=f"step_{idx_key}_{name}_{i}",
                        )
                        if checked:
                            st.session_state.completed_steps[key].add(i)
                        else:
                            st.session_state.completed_steps[key].discard(i)

                    # Alle zurücksetzen
                    if done_steps:
                        if st.button("🔄 Fortschritt zurücksetzen", key=f"reset_{idx_key}_{name}"):
                            st.session_state.completed_steps[key] = set()
                            st.rerun()
                else:
                    # Einzelner Text-Block: trotzdem per Nummerierung splitten versuchen
                    for step in steps:
                        st.markdown(step)
            else:
                st.markdown("_Keine Zubereitung angegeben_")

        # ── KOCH-TIPPS (PRO-FEATURE – Gold-Akzent) ────────────────────────
        if tipps and tipps.strip():
            st.markdown(f"""
            <div class="tipp-box">
                <p class="tipp-box-title">💡 Chef's Tipp</p>
                <p class="tipp-box-text">{tipps}</p>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATEN LADEN
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("Rezepte werden geladen …"):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Daten: {e}")
        st.stop()

if df.empty:
    st.warning("Das Google Sheet enthält keine Daten.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER (NEU)
# ══════════════════════════════════════════════════════════════════════════════
avg_zeit = int(df["Benötigte Zeit"].mean()) if not df.empty else 0
n_rezepte = len(df)
n_fav = len(st.session_state.favoriten)

st.markdown(f"""
<div class="hero-header">
    <h1 class="hero-title">🍽️ Rezept-Dashboard</h1>
    <p class="hero-subtitle">Deine persönliche Rezeptsammlung — durchsuche, filtere und entdecke neue Lieblinge.</p>
    <div class="hero-stats">
        <div class="hero-stat">
            <span class="hero-stat-number">{n_rezepte}</span>
            <span class="hero-stat-label">Rezepte</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">{avg_zeit}</span>
            <span class="hero-stat-label">Ø Minuten</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">{n_fav}</span>
            <span class="hero-stat-label">Favoriten</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["🍽️ Alle Rezepte", "❤️ Favoriten", "🛒 Zutaten-Check"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – ALLE REZEPTE
# ════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Sidebar Filter ────────────────────────────────────────────────────
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
            "⏱️ Benötigte Zeit (Min.)",
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

        sel_kategorie  = ms_filter("Kategorie",      "Kategorie",      "🍴")
        sel_ernaehrung = ms_filter("Ernährungsform",  "Ernährungsform", "🌿")
        sel_saison     = ms_filter("Saison-Check",    "Saison-Check",   "🌸")
        sel_aufwand    = ms_filter("Aufwand",         "Aufwand",        "⚡")

        st.markdown("---")

        # Druck-Hinweis
        st.markdown("""
        <div style="color:#f5e6d3; font-size:0.8rem; opacity:0.7; margin-top:0.5rem;">
        🖨️ <strong>Druck-Tipp:</strong><br>
        Strg+P (Cmd+P) öffnet den Browser-Druckdialog. Das Layout ist für DIN-A4 optimiert.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🔄 Filter zurücksetzen", use_container_width=True):
            st.rerun()

    # ── Filterlogik ───────────────────────────────────────────────────────
    filtered = df.copy()

    if search_term:
        filtered = filtered[
            filtered["Name des Gerichts"].str.contains(search_term, case=False, na=False)
        ]

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

    # ── Metriken ──────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🍽️ Rezepte", len(filtered))
    with col2:
        avg_t = int(filtered["Benötigte Zeit"].mean()) if not filtered.empty else 0
        st.metric("⏱️ Ø Zeit", f"{avg_t} min")
    with col3:
        st.metric("🍴 Kategorien", filtered["Kategorie"].nunique())
    with col4:
        st.metric("🌿 Ernährungsformen", filtered["Ernährungsform"].nunique())

    st.markdown("---")

    # ── Rezepte anzeigen ──────────────────────────────────────────────────
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

        for idx, (_, row) in enumerate(filtered.iterrows()):
            rendere_rezept_karte(row, idx_key=f"tab1_{idx}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – FAVORITEN (NEU)
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="zutat-check-header">
        <h2>❤️ Meine Favoriten</h2>
        <p>Hier erscheinen alle Rezepte, die du mit dem Herz-Button markiert hast – nur für diese Sitzung gespeichert.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.favoriten:
        st.info("Du hast noch keine Favoriten gespeichert. Öffne ein Rezept in Tab 1 und klicke auf 🤍 Favorit.")
    else:
        fav_df = df[df["Name des Gerichts"].isin(st.session_state.favoriten)]
        st.markdown(f"**{len(fav_df)} gespeicherte{'s' if len(fav_df)==1 else ''} Rezept{'e' if len(fav_df)!=1 else ''}**")
        st.markdown("")

        for idx, (_, row) in enumerate(fav_df.iterrows()):
            rendere_rezept_karte(row, idx_key=f"tab2_{idx}")

        st.markdown("---")
        if st.button("❌ Alle Favoriten löschen"):
            st.session_state.favoriten = set()
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 – ZUTATEN-CHECK
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="zutat-check-header">
        <h2>🛒 Was habe ich im Kühlschrank?</h2>
        <p>Wähle deine vorhandenen Zutaten aus – das Dashboard zeigt dir, welche Rezepte du kochen kannst.
        Gewürze und Grundzutaten werden automatisch ignoriert. Singular/Plural wird automatisch erkannt (Tomate = Tomaten).</p>
    </div>
    """, unsafe_allow_html=True)

    alle_zutaten_kategorisiert = extrahiere_alle_zutaten(df)

    # ── Zutaten-Auswahl ───────────────────────────────────────────────────
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

    alle_zutaten_flat = [z for zutaten in alle_zutaten_kategorisiert.values() for z in zutaten]

    if alle_auswaehlen:
        st.session_state.selected_zutaten = set(alle_zutaten_flat)
        st.rerun()
    if alle_abwaehlen:
        st.session_state.selected_zutaten = set()
        st.rerun()

    st.markdown("---")

    kategorien_sorted = sorted(alle_zutaten_kategorisiert.keys())
    for kategorie in kategorien_sorted:
        zutaten_in_kat = sorted(alle_zutaten_kategorisiert[kategorie])
        if zutat_suche:
            zutaten_in_kat = [z for z in zutaten_in_kat if zutat_suche.lower() in z.lower()]
            if not zutaten_in_kat:
                continue

        anzahl_ausgewaehlt = sum(1 for z in zutaten_in_kat if z in st.session_state.selected_zutaten)
        label = f"{kategorie}  ({anzahl_ausgewaehlt}/{len(zutaten_in_kat)} ausgewählt)"

        with st.expander(label, expanded=(zutat_suche != "")):
            btn_col1, btn_col2, _ = st.columns([1, 1, 4])
            with btn_col1:
                if st.button("Alle", key=f"alle_{kategorie}", use_container_width=True):
                    st.session_state.selected_zutaten.update(zutaten_in_kat)
                    st.rerun()
            with btn_col2:
                if st.button("Keine", key=f"keine_{kategorie}", use_container_width=True):
                    st.session_state.selected_zutaten -= set(zutaten_in_kat)
                    st.rerun()

            st.markdown("")
            n_cols = 3
            cols = st.columns(n_cols)
            for i, zutat in enumerate(zutaten_in_kat):
                with cols[i % n_cols]:
                    checked = zutat in st.session_state.selected_zutaten
                    if st.checkbox(zutat, value=checked, key=f"cb_{zutat}"):
                        st.session_state.selected_zutaten.add(zutat)
                    else:
                        st.session_state.selected_zutaten.discard(zutat)

    st.markdown("---")

    vorhandene_zutaten = st.session_state.selected_zutaten

    if vorhandene_zutaten:
        st.markdown(
            f"**Ausgewählte Zutaten ({len(vorhandene_zutaten)}):** " +
            " ".join([f'<span class="zutat-tag">{z}</span>' for z in sorted(vorhandene_zutaten)]),
            unsafe_allow_html=True
        )
        st.markdown("")

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
            partiell     = matches[matches["vollstaendig"] == False]

            mc1, mc2, mc3 = st.columns(3)
            with mc1:
                st.metric("✅ Sofort kochbar", len(vollstaendig))
            with mc2:
                st.metric("🔸 Fast vollständig", len(partiell))
            with mc3:
                st.metric("🍽️ Rezepte gesamt", len(matches))

            st.markdown("---")

            # ── Vollständige Matches ──────────────────────────────────────
            if not vollstaendig.empty:
                st.markdown("#### ✅ Diese Rezepte kannst du sofort kochen!")
                for idx, (_, match) in enumerate(vollstaendig.iterrows()):
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
                            steps = parse_zubereitung_steps(zubereitung)
                            if len(steps) > 1:
                                key = f"match_steps_{name}"
                                if key not in st.session_state.completed_steps:
                                    st.session_state.completed_steps[key] = set()
                                done = st.session_state.completed_steps[key]
                                if done:
                                    st.progress(len(done)/len(steps), text=f"{len(done)}/{len(steps)} erledigt")
                                for i, step in enumerate(steps):
                                    checked = st.checkbox(
                                        step,
                                        value=(i in done),
                                        key=f"mstep_{idx}_{i}"
                                    )
                                    if checked:
                                        done.add(i)
                                    else:
                                        done.discard(i)
                            else:
                                for step in steps:
                                    st.markdown(step)

                        # Koch-Tipps auch im Zutaten-Check
                        tipps = row.get("Koch-Tipps", "") if "Koch-Tipps" in row.index else ""
                        if tipps and tipps.strip():
                            st.markdown(f"""
                            <div class="tipp-box">
                                <p class="tipp-box-title">💡 Chef's Tipp</p>
                                <p class="tipp-box-text">{tipps}</p>
                            </div>
                            """, unsafe_allow_html=True)

            # ── Partielle Matches ─────────────────────────────────────────
            if not partiell.empty:
                st.markdown("---")
                st.markdown("#### 🔸 Fast dabei – nur noch ein paar Zutaten fehlen")

                sort_col, _ = st.columns([2, 2])
                with sort_col:
                    min_anteil = st.slider(
                        "Mindestanteil vorhandener Zutaten",
                        min_value=0, max_value=100, value=50, step=10,
                        format="%d%%", key="min_anteil_slider"
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
                        fehlend   = match["fehlend"]
                        anzahl_gesamt    = match["anzahl_gesamt"]
                        anzahl_vorhanden = match["anzahl_vorhanden"]
                        anteil_pct = int(match["anteil"] * 100)

                        vorhanden_tags = " ".join([f'<span class="zutat-tag">{z}</span>' for z in vorhanden])
                        fehlend_tags   = " ".join([f'<span class="zutat-tag-missing">{z}</span>' for z in fehlend])

                        with st.expander(
                            f"🔸 {name}  •  ⏱️ {zeit} min  •  {anzahl_vorhanden}/{anzahl_gesamt} ({anteil_pct}%)",
                            expanded=False
                        ):
                            st.markdown(
                                f'<span class="match-badge-partial">{anzahl_vorhanden} von {anzahl_gesamt} Zutaten ({anteil_pct}%)</span>',
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
