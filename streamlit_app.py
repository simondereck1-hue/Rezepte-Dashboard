"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         MEIN KOCHBUCH – „Die Seele der Küche"  [REDESIGN v2]               ║
║                                                                              ║
║  ✦ Screenshot-getreues Design: Terrakotta-Header, dunkle Sidebar           ║
║  ✦ Playfair Display (Überschriften) + Lato (Fließtext)                     ║
║  ✦ Karten-Layout mit weichen Schatten & abgerundeten Ecken (28px)          ║
║  ✦ Pillenförmige Ingredient-Tags & Status-Badges                           ║
║  ✦ Luftige Abstände (White-Space-First-Ansatz)                             ║
║  ✦ Alle Backend-Funktionen identisch (Google Sheets, Regex, Favoriten)     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import re
import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🥘 Mein Kochbuch",
    page_icon="🥘",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# ██████████████████████████  CSS DESIGN-SYSTEM  ██████████████████████████████
#
#  Farbpalette (Screenshot-Referenz):
#   --creme      #FBF5EC   warmes Leinen / Seitenhintergrund
#   --braun-d    #3B1F0E   tiefstes Dunkelbraun (Sidebar-Basis)
#   --braun-m    #5C2E10   mittleres Braun (Sidebar-Akzent)
#   --terra      #C85A28   Terrakotta (Header-Gradient, Hauptakzent)
#   --terra-hell #E07848   helles Terrakotta
#   --sand       #EAD9C8   Sand / Karten-Border
#   --sand-hell  #F5EDE0   sehr heller Sand
#   --salbei     #6E9673   Grün (vorhanden-Tags, Salbei)
#   --senf       #C99010   Gold (Tipps-Box, Badges)
#   --text-d     #2E1608   sehr dunkler Text
#   --text-m     #5E3820   mittelbrauner Text
#
# ══════════════════════════════════════════════════════════════════════════════
CSS = """
<style>
/* ═══════════════════════════════════════════════════════════════
   FONTS: Playfair Display (Display/Headings) + Lato (Body)
═══════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,500;1,600&family=Lato:wght@300;400;700;900&display=swap');

/* ═══════════════════════════════════════════════════════════════
   DESIGN TOKENS
═══════════════════════════════════════════════════════════════ */
:root {
    --creme:       #FBF5EC;
    --braun-d:     #3B1F0E;
    --braun-m:     #6B3A1E;
    --braun-s:     #8C4E28;
    --terra:       #C85A28;
    --terra-hell:  #E07848;
    --terra-soft:  #F5E0D2;
    --sand:        #E8D4BC;
    --sand-hell:   #F5EDE0;
    --sand-mid:    #D4B898;
    --salbei:      #6E9673;
    --salbei-soft: #DCF0DF;
    --senf:        #C99010;
    --senf-soft:   #FFF4D0;
    --rose-soft:   #FDEAE8;
    --rose-mid:    #F0A898;
    --text-d:      #2E1608;
    --text-m:      #5E3820;
    --text-s:      #8A5E40;
    --weiss:       #FFFFFF;
    --radius-lg:   28px;
    --radius-md:   20px;
    --radius-sm:   14px;
    --radius-pill: 100px;
    --shadow-card: 0 4px 24px rgba(46,22,8,0.09), 0 1px 6px rgba(46,22,8,0.05);
    --shadow-hover: 0 12px 40px rgba(46,22,8,0.16), 0 2px 10px rgba(46,22,8,0.08);
    --shadow-hero: 0 8px 40px rgba(46,22,8,0.20), 0 2px 10px rgba(46,22,8,0.10);
}

/* ═══════════════════════════════════════════════════════════════
   RESET & TYPOGRAFIE-BASIS
═══════════════════════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Lato', sans-serif;
    color: var(--text-d);
}
p, span, label, div, li { color: inherit; }
.stMarkdown p, .stMarkdown span, .stMarkdown li {
    color: var(--text-d) !important;
    font-family: 'Lato', sans-serif !important;
}
h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif !important;
    color: var(--text-d) !important;
}

/* ═══════════════════════════════════════════════════════════════
   APP HINTERGRUND – warmes Cremepapier mit feiner Textur
═══════════════════════════════════════════════════════════════ */
.stApp {
    background-color: var(--creme);
    background-image:
        radial-gradient(circle at 2px 2px, rgba(200,90,40,0.04) 1px, transparent 0);
    background-size: 28px 28px;
}

/* Main content padding */
.main .block-container {
    padding: 2rem 2.5rem 4rem 2.5rem !important;
    max-width: 1280px !important;
}

/* ═══════════════════════════════════════════════════════════════
   HERO HEADER – Terrakotta Kochbuch-Cover (Screenshot-Stil)
═══════════════════════════════════════════════════════════════ */
.hero-header {
    background:
        radial-gradient(ellipse at 15% 40%, rgba(212,140,40,0.30) 0%, transparent 55%),
        radial-gradient(ellipse at 85% 20%, rgba(100,60,20,0.25) 0%, transparent 50%),
        linear-gradient(135deg, #8B3510 0%, #C85A28 40%, #D97040 70%, #E88A55 100%);
    border-radius: var(--radius-lg);
    padding: 2.5rem 3rem 2.2rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-hero);
}
/* Dekorativer Kochlöffel-Kreis */
.hero-header::before {
    content: "🥘";
    font-size: 9rem;
    position: absolute;
    right: 3%;
    top: 50%;
    transform: translateY(-50%) rotate(-8deg);
    opacity: 0.13;
    line-height: 1;
    pointer-events: none;
}
/* Heller Reflex-Kreis */
.hero-header::after {
    content: "";
    position: absolute;
    top: -80px;
    right: -80px;
    width: 280px;
    height: 280px;
    border-radius: 50%;
    background: rgba(255,255,255,0.07);
    pointer-events: none;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.6rem;
    font-weight: 700;
    font-style: italic;
    color: #FFF4E8;
    margin: 0 0 0.25rem 0;
    line-height: 1.15;
    position: relative;
    z-index: 1;
    text-shadow: 0 2px 16px rgba(46,22,8,0.35);
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-family: 'Lato', sans-serif;
    font-size: 0.95rem;
    font-weight: 300;
    color: rgba(255,244,232,0.82);
    margin: 0 0 2rem 0;
    position: relative;
    z-index: 1;
    letter-spacing: 0.3px;
}
.hero-stats {
    display: flex;
    gap: 1rem;
    position: relative;
    z-index: 1;
    flex-wrap: wrap;
}
.hero-stat {
    background: rgba(255,255,255,0.14);
    backdrop-filter: blur(6px);
    border-radius: var(--radius-sm);
    padding: 0.65rem 1.3rem 0.55rem;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.18);
    min-width: 80px;
    transition: background 0.2s ease;
}
.hero-stat:hover {
    background: rgba(255,255,255,0.20);
}
.hero-stat-number {
    font-family: 'Playfair Display', serif;
    font-size: 1.9rem;
    font-weight: 700;
    color: #FFEAD0;
    display: block;
    line-height: 1;
    margin-bottom: 0.2rem;
}
.hero-stat-label {
    font-family: 'Lato', sans-serif;
    font-size: 0.68rem;
    color: rgba(255,244,232,0.72);
    text-transform: uppercase;
    letter-spacing: 1.4px;
    font-weight: 700;
}

/* ═══════════════════════════════════════════════════════════════
   METRIKEN – luftige Karten
═══════════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: var(--weiss) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.1rem 1.4rem !important;
    border: 1.5px solid var(--sand) !important;
    box-shadow: var(--shadow-card) !important;
    transition: box-shadow 0.25s ease !important;
}
[data-testid="metric-container"]:hover {
    box-shadow: var(--shadow-hover) !important;
}
[data-testid="stMetricValue"] {
    color: var(--terra) !important;
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    font-size: 1.9rem !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-m) !important;
    font-weight: 700 !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.2px !important;
    font-family: 'Lato', sans-serif !important;
}

/* ═══════════════════════════════════════════════════════════════
   TABS – Kochbuch-Navigation (Screenshot-Stil: Clips-Look)
═══════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: var(--sand-hell) !important;
    border-radius: var(--radius-md) !important;
    padding: 5px !important;
    gap: 5px !important;
    border: 1.5px solid var(--sand) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 16px !important;
    font-family: 'Lato', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    color: var(--text-m) !important;
    padding: 0.5rem 1.3rem !important;
    transition: all 0.22s ease !important;
    border: none !important;
    letter-spacing: 0.2px;
}
.stTabs [aria-selected="true"] {
    background: var(--weiss) !important;
    color: var(--terra) !important;
    box-shadow: 0 2px 10px rgba(46,22,8,0.12) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.8rem !important;
}

/* ═══════════════════════════════════════════════════════════════
   REZEPT-KARTE (Expander) – Screenshot-Stil mit Baumrinden-Textur
═══════════════════════════════════════════════════════════════ */
.stExpander {
    background-color: var(--weiss) !important;
    border-radius: var(--radius-lg) !important;
    border: 1.5px solid var(--sand) !important;
    margin-bottom: 0.85rem !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-card) !important;
    transition:
        box-shadow 0.28s ease,
        transform 0.28s ease !important;
}
.stExpander:hover {
    box-shadow: var(--shadow-hover) !important;
    transform: translateY(-2px) !important;
}
.stExpander summary {
    padding: 1.05rem 1.5rem !important;
    transition: background-color 0.22s ease !important;
    border-radius: var(--radius-lg) !important;
}
.stExpander summary:hover {
    background-color: var(--sand-hell) !important;
}
.stExpander summary p {
    color: var(--text-d) !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    font-family: 'Lato', sans-serif !important;
}
.stExpander [data-testid="stExpanderDetails"] {
    padding: 0.8rem 1.6rem 1.5rem 1.6rem !important;
}
.stExpander [data-testid="stExpanderDetails"] p,
.stExpander [data-testid="stExpanderDetails"] span,
.stExpander [data-testid="stExpanderDetails"] label,
.stExpander [data-testid="stExpanderDetails"] div,
.stExpander [data-testid="stExpanderDetails"] li {
    color: var(--text-d) !important;
}
[data-testid="stCheckbox"] label span,
[data-testid="stCheckbox"] span p {
    color: var(--text-d) !important;
    font-size: 0.91rem !important;
    font-family: 'Lato', sans-serif !important;
}

/* ═══════════════════════════════════════════════════════════════
   BADGES – pillenförmig (Screenshot-Stil)
═══════════════════════════════════════════════════════════════ */
.badge {
    display: inline-block;
    padding: 0.22rem 0.8rem;
    border-radius: var(--radius-pill);
    font-size: 0.69rem;
    font-weight: 900;
    letter-spacing: 0.4px;
    margin: 0.15rem 0.1rem;
    font-family: 'Lato', sans-serif;
    text-transform: uppercase;
}
.badge-kategorie  {
    background: var(--terra-soft);
    color: #7A2A10;
    border: 1px solid rgba(200,90,40,0.2);
}
.badge-ernaehrung {
    background: var(--salbei-soft);
    color: #2D5E32;
    border: 1px solid rgba(110,150,115,0.25);
}
.badge-saison {
    background: #D8E8FA;
    color: #1A3D7A;
    border: 1px solid rgba(30,70,160,0.15);
}
.badge-aufwand-leicht {
    background: var(--salbei-soft);
    color: #2D5E32;
    border: 1px solid rgba(110,150,115,0.25);
}
.badge-aufwand-mittel {
    background: var(--senf-soft);
    color: #6A4800;
    border: 1px solid rgba(200,144,16,0.2);
}
.badge-aufwand-schwer {
    background: var(--terra-soft);
    color: #7A2A10;
    border: 1px solid rgba(200,90,40,0.2);
}

/* Favoriten-Badge */
.fav-badge {
    display: inline-block;
    background: linear-gradient(135deg, #F07090, #D84060);
    color: white;
    padding: 0.22rem 0.85rem;
    border-radius: var(--radius-pill);
    font-size: 0.69rem;
    font-weight: 900;
    font-family: 'Lato', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

/* ═══════════════════════════════════════════════════════════════
   SECTION LABELS – wie gedruckte Rubriken im Kochbuch
═══════════════════════════════════════════════════════════════ */
.section-label {
    font-family: 'Lato', sans-serif;
    font-size: 0.66rem;
    font-weight: 900;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    color: var(--terra);
    margin: 1.4rem 0 0.65rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 2px dashed var(--sand);
}

/* ═══════════════════════════════════════════════════════════════
   ZUTAT GRID – organische Pillen
═══════════════════════════════════════════════════════════════ */
.zutat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(148px, 1fr));
    gap: 0.45rem;
    margin-top: 0.5rem;
}
.zutat-item {
    background: var(--creme);
    border: 1.5px solid var(--sand);
    border-radius: var(--radius-sm);
    padding: 0.42rem 0.75rem;
    font-size: 0.82rem;
    color: var(--text-d);
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'Lato', sans-serif;
    transition: border-color 0.18s ease;
}
.zutat-item:hover {
    border-color: var(--terra);
}
.zutat-menge {
    font-weight: 900;
    color: var(--terra);
    white-space: nowrap;
    font-size: 0.78rem;
}
.zutat-name {
    color: var(--text-m);
    font-weight: 700;
}

/* ═══════════════════════════════════════════════════════════════
   ZUTATEN-TAGS (Match-Anzeige) – Screenshot-Pille
═══════════════════════════════════════════════════════════════ */
.zutat-tag {
    display: inline-block;
    background: var(--salbei-soft);
    color: #2D5E32;
    border-radius: var(--radius-pill);
    padding: 0.22rem 0.75rem;
    font-size: 0.76rem;
    font-weight: 700;
    margin: 0.15rem 0.1rem;
    font-family: 'Lato', sans-serif;
    border: 1px solid rgba(110,150,115,0.25);
}
.zutat-tag-missing {
    display: inline-block;
    background: var(--terra-soft);
    color: #7A2A10;
    border-radius: var(--radius-pill);
    padding: 0.22rem 0.75rem;
    font-size: 0.76rem;
    font-weight: 700;
    margin: 0.15rem 0.1rem;
    font-family: 'Lato', sans-serif;
    border: 1px solid rgba(200,90,40,0.2);
}

/* ═══════════════════════════════════════════════════════════════
   SCHRITT-CHECKLISTE
═══════════════════════════════════════════════════════════════ */
.step-done {
    opacity: 0.38;
    text-decoration: line-through;
    color: var(--text-s) !important;
}
.step-active { color: var(--text-d); }

/* ═══════════════════════════════════════════════════════════════
   TIPP-BOX – goldener Chef's Tipp
═══════════════════════════════════════════════════════════════ */
.tipp-box {
    background: var(--senf-soft);
    border: 1.5px solid rgba(201,144,16,0.35);
    border-left: 5px solid var(--senf);
    border-radius: var(--radius-md);
    padding: 1.1rem 1.4rem;
    margin-top: 1.3rem;
}
.tipp-box-title {
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    font-weight: 700;
    font-style: italic;
    color: #6A4800;
    margin: 0 0 0.38rem 0;
}
.tipp-box-text {
    font-size: 0.88rem;
    color: #4A3000;
    line-height: 1.7;
    margin: 0;
    font-family: 'Lato', sans-serif;
}

/* ═══════════════════════════════════════════════════════════════
   MATCH BADGES (Zutaten-Check)
═══════════════════════════════════════════════════════════════ */
.match-badge-full {
    display: inline-block;
    background: linear-gradient(135deg, #7AAE7E, #4A8055);
    color: #fff;
    padding: 0.3rem 1.1rem;
    border-radius: var(--radius-pill);
    font-size: 0.73rem;
    font-weight: 900;
    font-family: 'Lato', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.match-badge-partial {
    display: inline-block;
    background: linear-gradient(135deg, #E0A858, #C07C28);
    color: #fff;
    padding: 0.3rem 1.1rem;
    border-radius: var(--radius-pill);
    font-size: 0.73rem;
    font-weight: 900;
    font-family: 'Lato', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ═══════════════════════════════════════════════════════════════
   ZUTATEN-CHECK HEADER – Salbei-Grün
═══════════════════════════════════════════════════════════════ */
.zutat-check-header {
    background: linear-gradient(135deg, var(--salbei-soft), #C8E8CC);
    border-radius: var(--radius-lg);
    padding: 1.6rem 2.2rem;
    margin-bottom: 1.8rem;
    border: 1.5px solid rgba(110,150,115,0.3);
    box-shadow: var(--shadow-card);
}
.zutat-check-header h2 {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: var(--text-d) !important;
    margin: 0 0 0.45rem 0;
    font-size: 1.5rem;
}
.zutat-check-header p {
    color: var(--text-m) !important;
    font-size: 0.9rem;
    margin: 0;
    line-height: 1.65;
    font-family: 'Lato', sans-serif;
}

/* ═══════════════════════════════════════════════════════════════
   REZEPTE-HEADER (Trennlinie-Stil)
═══════════════════════════════════════════════════════════════ */
.rezepte-header {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: var(--text-d);
    font-size: 1.28rem;
    margin: 0.4rem 0 1.1rem 0;
    padding-bottom: 0.6rem;
    border-bottom: 2px dashed var(--sand-mid);
}

/* ═══════════════════════════════════════════════════════════════
   NO-RESULTS
═══════════════════════════════════════════════════════════════ */
.no-results {
    background: var(--weiss);
    border: 2px dashed var(--sand-mid);
    border-radius: var(--radius-lg);
    padding: 3.5rem 2rem;
    text-align: center;
    margin: 2.5rem 0;
}
.no-results h2 {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    color: var(--text-m);
    font-size: 1.5rem;
    margin: 0 0 0.65rem 0;
}
.no-results p {
    color: var(--text-s) !important;
    font-size: 0.95rem;
    font-family: 'Lato', sans-serif;
}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR – Dunkles Kaffeebraun (Screenshot-Stil: fast Schwarz)
═══════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: linear-gradient(
        175deg,
        #241208 0%,
        #3B1F0E 45%,
        #4E2A14 100%
    ) !important;
}
section[data-testid="stSidebar"] > div {
    background: transparent !important;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSlider p,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #F0E0CC !important;
    font-family: 'Lato', sans-serif !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] span,
section[data-testid="stSidebar"] [data-baseweb="select"] div {
    color: #F0E0CC !important;
}
section[data-testid="stSidebar"] div[data-baseweb="input"] {
    background-color: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.15) !important;
    border-radius: var(--radius-sm) !important;
}
section[data-testid="stSidebar"] div[data-baseweb="input"] input {
    color: #F0E0CC !important;
    font-family: 'Lato', sans-serif !important;
}
section[data-testid="stSidebar"] input::placeholder {
    color: rgba(240,224,204,0.45) !important;
}
section[data-testid="stSidebar"] h2 {
    color: #FFE8C8 !important;
    font-family: 'Playfair Display', serif !important;
    font-style: italic !important;
    font-size: 1.25rem !important;
    letter-spacing: -0.3px;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.09) !important;
    border-color: rgba(255,255,255,0.15) !important;
    border-radius: var(--radius-sm) !important;
}
/* Sidebar Expander */
section[data-testid="stSidebar"] .stExpander {
    background-color: rgba(255,255,255,0.07) !important;
    border-color: rgba(255,255,255,0.12) !important;
    border-radius: 16px !important;
}
section[data-testid="stSidebar"] .stExpander:hover {
    transform: none !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stExpander summary p {
    color: #F0E0CC !important;
}
/* Sidebar Slider */
section[data-testid="stSidebar"] .stSlider [data-baseweb="thumb"] {
    background: var(--terra) !important;
}
section[data-testid="stSidebar"] .stSlider [data-baseweb="track-fill"] {
    background: var(--terra) !important;
}

/* ═══════════════════════════════════════════════════════════════
   BUTTONS – warm & rund
═══════════════════════════════════════════════════════════════ */
.stButton > button {
    border-radius: var(--radius-md) !important;
    font-family: 'Lato', sans-serif !important;
    font-weight: 700 !important;
    border: 1.5px solid var(--sand-mid) !important;
    background: var(--weiss) !important;
    color: var(--text-d) !important;
    transition: all 0.2s ease !important;
    padding: 0.42rem 1.1rem !important;
    letter-spacing: 0.2px;
}
.stButton > button:hover {
    background: var(--terra-soft) !important;
    border-color: var(--terra) !important;
    color: var(--terra) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(200,90,40,0.18) !important;
}

/* ═══════════════════════════════════════════════════════════════
   EINGABEFELDER – warm & einladend
═══════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--sand-mid) !important;
    background: var(--weiss) !important;
    color: var(--text-d) !important;
    font-family: 'Lato', sans-serif !important;
    padding: 0.5rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--terra) !important;
    box-shadow: 0 0 0 3px rgba(200,90,40,0.12) !important;
}
.stTextInput label {
    font-family: 'Lato', sans-serif !important;
    font-weight: 700 !important;
    color: var(--text-m) !important;
    font-size: 0.86rem !important;
}

/* Number Input */
.stNumberInput > div > div > input {
    border-radius: var(--radius-sm) !important;
    border: 1.5px solid var(--sand-mid) !important;
    font-family: 'Lato', sans-serif !important;
    color: var(--text-d) !important;
}

/* Slider */
.stSlider [data-baseweb="thumb"] {
    background: var(--terra) !important;
}
.stSlider [data-baseweb="track-fill"] {
    background: var(--terra) !important;
}

/* Multiselect */
[data-baseweb="tag"] {
    background: var(--terra-soft) !important;
    border-radius: 10px !important;
}
[data-baseweb="tag"] span { color: #7A2A10 !important; }

/* Progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, var(--salbei), #4A8055) !important;
    border-radius: 10px !important;
}

/* ═══════════════════════════════════════════════════════════════
   TRENNLINIE IN KARTEN
═══════════════════════════════════════════════════════════════ */
.stExpander hr, hr {
    border: none !important;
    border-top: 1.5px dashed var(--sand) !important;
    margin: 0.8rem 0 !important;
}

/* ═══════════════════════════════════════════════════════════════
   SELECTBOX & MULTISELECT IN SIDEBAR
═══════════════════════════════════════════════════════════════ */
section[data-testid="stSidebar"] [data-baseweb="popover"] {
    background: #4E2A14 !important;
}

/* ═══════════════════════════════════════════════════════════════
   ATMOSPHÄRISCHE SECTION-DIVIDER
═══════════════════════════════════════════════════════════════ */
.divider-warm {
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--sand), transparent);
    margin: 2rem 0;
    border: none;
}

/* ═══════════════════════════════════════════════════════════════
   KARTEN INFO-BOX (stAlert/stInfo)
═══════════════════════════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border: 1.5px solid var(--sand) !important;
    font-family: 'Lato', sans-serif !important;
}

/* ═══════════════════════════════════════════════════════════════
   DRUCK-MODUS
═══════════════════════════════════════════════════════════════ */
@media print {
    section[data-testid="stSidebar"],
    .stButton,
    [data-testid="stNumberInput"],
    .stTabs [data-baseweb="tab-list"] { display: none !important; }
    .stApp { background: white !important; }
    .stExpander {
        border: 1px solid #ccc !important;
        box-shadow: none !important;
        break-inside: avoid;
        page-break-inside: avoid;
    }
    .hero-header { break-after: avoid; }
}

footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
[data-testid="stDecoration"] { display: none !important; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE SHEETS CONNECTION (unverändert)
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
# PORTIONSRECHNER (unverändert)
# ══════════════════════════════════════════════════════════════════════════════
def skaliere_zutat(zutat_str: str, faktor: float) -> str:
    """Multipliziert alle Zahlen in einem Zutaten-String mit dem Faktor."""
    def ersetze_zahl(match):
        original = match.group(0)
        if "/" in original:
            teile = original.split("/")
            try:
                wert = float(teile[0]) / float(teile[1])
            except Exception:
                return original
        elif "-" in original and not original.startswith("-"):
            try:
                wert = float(original.split("-")[0])
            except Exception:
                return original
        else:
            try:
                wert = float(original.replace(",", "."))
            except Exception:
                return original

        neuer_wert = wert * faktor
        if neuer_wert == int(neuer_wert):
            return str(int(neuer_wert))
        else:
            return f"{neuer_wert:.1f}".replace(".", ",")

    return re.sub(r"\d+/\d+|\d+-\d+|\d+[,\.]\d+|\d+", ersetze_zahl, zutat_str)


def parse_zutat_display(zutat_str: str) -> tuple[str, str]:
    """Trennt Menge+Einheit vom Zutatsnamen."""
    EINHEITEN = r"(?:g|kg|ml|l|EL|TL|Prise|Stück|Stk|Scheib\w*|Dose\w*|Bund|Pkg|Pckg|cm|mm|Glas|Dose|Becher|Tasse|Pck)\b"
    pattern = rf"^(\d+[,\./]?\d*\s*(?:{EINHEITEN})?)\s*(.+)$"
    match = re.match(pattern, zutat_str.strip(), re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "", zutat_str.strip()


# ══════════════════════════════════════════════════════════════════════════════
# SCHRITT-PARSER (unverändert)
# ══════════════════════════════════════════════════════════════════════════════
def parse_zubereitung_steps(zubereitung_str: str) -> list[str]:
    """Gibt eine Liste der einzelnen Zubereitungsschritte zurück."""
    by_newline = [s.strip() for s in str(zubereitung_str).split("\n") if s.strip()]
    if len(by_newline) > 1:
        return by_newline

    text = str(zubereitung_str).strip()
    parts = re.split(r'(?<!\w)(\d+[\.\)]\s+)', text)
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

    return [text] if text else []


# ══════════════════════════════════════════════════════════════════════════════
# INTELLIGENTE ZUTATEN-NORMALISIERUNG (unverändert)
# ══════════════════════════════════════════════════════════════════════════════
_MENGE_EINHEIT_PATTERN = re.compile(
    r"""
    [½¼¾⅓⅔⅛⅜⅝⅞]
    |
    \d+\s*/\s*\d+
    |
    \d+\s*[-–]\s*\d+
    |
    \d+[,\.]\d+
    |
    \d+
    |
    \b(?:
        g|kg|mg|
        ml|l|cl|dl|
        EL|TL|El|Tl|
        Prise|prise|
        Stück|Stk|stk|stück|
        Scheibe[n]?|scheibe[n]?|
        Dose[n]?|dose[n]?|
        Bund|bund|
        Pkg|Pckg|pkg|Pck|pck|
        Paket[e]?|paket[e]?|
        Becher|becher|
        Tasse[n]?|tasse[n]?|
        Glas|Gläser|glas|
        cm|mm|
        Zehe[n]?|zehe[n]?|
        Handvoll|handvoll|
        Spritzer|spritzer|
        Zweig[e]?|zweig[e]?|
        Blatt|Blätter|blatt|
        Wurst|wurst|
        Scheib\w*
    )\b
    |
    \([^)]*\)
    |
    \b(?:ca|etwa|mind|max|ungefähr|je)\b\.?
    """,
    re.IGNORECASE | re.VERBOSE,
)


def bereinige_zutat(zutat_str: str) -> str:
    bereinigt = _MENGE_EINHEIT_PATTERN.sub(" ", zutat_str)
    bereinigt = re.sub(r"[,;:\-–\.]+", " ", bereinigt)
    bereinigt = re.sub(r"\s+", " ", bereinigt).strip()
    return bereinigt.lower()


def normalisiere_wort(wort: str) -> str:
    w = wort.lower().strip()
    for endung in ["nen", "ien", "ern", "chen", "lein", "en", "er", "es", "e", "s"]:
        if w.endswith(endung) and len(w) - len(endung) >= 3:
            return w[:-len(endung)]
    return w


def zutaten_match(rezept_zutat: str, vorhandene_lower: set) -> bool:
    rz_clean = bereinige_zutat(rezept_zutat)
    rz_stamm = normalisiere_wort(rz_clean)

    for v in vorhandene_lower:
        v_clean = bereinige_zutat(v)
        v_stamm = normalisiere_wort(v_clean)

        if v_clean and rz_clean:
            if v_clean in rz_clean or rz_clean in v_clean:
                return True

        if len(rz_stamm) >= 3 and len(v_stamm) >= 3:
            if rz_stamm in v_stamm or v_stamm in rz_stamm:
                return True

    return False


# ══════════════════════════════════════════════════════════════════════════════
# GEWÜRZE & KATEGORIEN (unverändert)
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
    zutaten_map: dict[str, str] = {}

    for zutaten_str in df["Benötigte Zutaten"].dropna():
        items = [z.strip() for z in str(zutaten_str).replace("\n", ",").split(",") if z.strip()]
        for item in items:
            if ist_gewuerz(item) or len(item) <= 2:
                continue
            clean = bereinige_zutat(item)
            stamm = normalisiere_wort(clean)
            if len(clean) < 2:
                continue
            if stamm not in zutaten_map:
                anzeige = clean.strip().capitalize()
                zutaten_map[stamm] = anzeige

    kategorisiert: dict[str, list[str]] = {}
    for stamm, anzeige in sorted(zutaten_map.items(), key=lambda x: x[1]):
        kat = kategorisiere_zutat(anzeige)
        if kat not in kategorisiert:
            kategorisiert[kat] = []
        if anzeige not in kategorisiert[kat]:
            kategorisiert[kat].append(anzeige)

    return kategorisiert


def berechne_matches(df: pd.DataFrame, vorhandene_zutaten: set) -> pd.DataFrame:
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

        anzahl_gesamt    = len(rezept_zutaten)
        anzahl_vorhanden = len(vorhanden)
        anteil = anzahl_vorhanden / anzahl_gesamt if anzahl_gesamt > 0 else 0

        if anzahl_vorhanden > 0:
            ergebnisse.append({
                "row":              row,
                "vorhanden":        vorhanden,
                "fehlend":          fehlend,
                "anzahl_gesamt":    anzahl_gesamt,
                "anzahl_vorhanden": anzahl_vorhanden,
                "anteil":           anteil,
                "vollstaendig":     len(fehlend) == 0,
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
    st.session_state.favoriten = set()

if "completed_steps" not in st.session_state:
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
    if name in st.session_state.favoriten:
        st.session_state.favoriten.discard(name)
    else:
        st.session_state.favoriten.add(name)


def rendere_rezept_karte(row, idx_key: str, zeige_portionsrechner: bool = True):
    """
    Zentrale Funktion zum Rendern einer Rezeptkarte im Kochbuch-Stil.
    Identische Logik wie Original – nur Darstellung aufgewertet.
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
    fav_icon    = "❤️" if ist_favorit else "🤍"
    fav_badge   = '<span class="fav-badge">❤️ Favorit</span> ' if ist_favorit else ""

    badges = fav_badge
    if kategorie:
        badges += f'<span class="badge badge-kategorie">{kategorie}</span> '
    if ernaehrung:
        badges += f'<span class="badge badge-ernaehrung">{ernaehrung}</span> '
    if saison:
        badges += f'<span class="badge badge-saison">{saison}</span> '
    if aufwand:
        badges += f'<span class="badge {aufwand_class(aufwand)}">{aufwand}</span>'

    expander_label = f"{'❤️ ' if ist_favorit else '🥘 '}{name}  ·  ⏱ {zeit} min"

    with st.expander(expander_label, expanded=False):
        # Badges Zeile
        st.markdown(badges, unsafe_allow_html=True)
        st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

        # ── Favoriten-Button ──────────────────────────────────────────────
        fav_col, _ = st.columns([1, 5])
        with fav_col:
            if st.button(
                f"{fav_icon} {'Entfernen' if ist_favorit else 'Favorit'}",
                key=f"fav_{idx_key}_{name}",
                use_container_width=True,
                help="Rezept zu Favoriten hinzufügen / entfernen",
            ):
                toggle_favorit(name)
                st.rerun()

        st.markdown("---")

        # ── Portionsrechner ───────────────────────────────────────────────
        base_portionen = int(row.get("Portionen", 4)) if "Portionen" in row.index else 4
        if base_portionen == 0:
            base_portionen = 4

        if zeige_portionsrechner and zutaten:
            port_col1, port_col2 = st.columns([2, 4])
            with port_col1:
                neue_portionen = st.number_input(
                    "🍽️ Portionen",
                    min_value=1, max_value=20, value=base_portionen, step=1,
                    key=f"portionen_{idx_key}_{name}",
                    help=f"Originalrezept für {base_portionen} Portionen.",
                )
            faktor = neue_portionen / base_portionen
            with port_col2:
                if faktor != 1.0:
                    st.info(
                        f"Faktor: ×{faktor:.2f} – Mengen auf **{neue_portionen} Portionen** umgerechnet",
                        icon="🔢",
                    )
        else:
            faktor = 1.0

        # ── Layout: Zutaten | Zubereitung ─────────────────────────────────
        col_l, col_r = st.columns([1, 2])

        with col_l:
            st.markdown('<div class="section-label">🧂 Zutaten</div>', unsafe_allow_html=True)

            if zutaten:
                items = [z.strip() for z in str(zutaten).replace("\n", ",").split(",") if z.strip()]
                grid_html = '<div class="zutat-grid">'
                for item in items:
                    item_skaliert = skaliere_zutat(item, faktor) if faktor != 1.0 else item
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

            if equipment:
                st.markdown('<div class="section-label">🔧 Equipment</div>', unsafe_allow_html=True)
                eq_items = [e.strip() for e in str(equipment).replace("\n", ",").split(",") if e.strip()]
                for eq in eq_items:
                    st.markdown(f"• {eq}")

        with col_r:
            st.markdown('<div class="section-label">👨‍🍳 Zubereitung</div>', unsafe_allow_html=True)

            if zubereitung:
                steps = parse_zubereitung_steps(zubereitung)

                if len(steps) > 1:
                    key = f"steps_{name}"
                    if key not in st.session_state.completed_steps:
                        st.session_state.completed_steps[key] = set()

                    done_steps = st.session_state.completed_steps[key]
                    fertig = len(done_steps)
                    gesamt = len(steps)

                    if fertig > 0:
                        st.progress(fertig / gesamt, text=f"{fertig}/{gesamt} Schritte erledigt ✓")

                    for i, step in enumerate(steps):
                        is_done = i in done_steps
                        checked = st.checkbox(
                            step, value=is_done,
                            key=f"step_{idx_key}_{name}_{i}",
                        )
                        if checked:
                            st.session_state.completed_steps[key].add(i)
                        else:
                            st.session_state.completed_steps[key].discard(i)

                    if done_steps:
                        if st.button("🔄 Fortschritt zurücksetzen", key=f"reset_{idx_key}_{name}"):
                            st.session_state.completed_steps[key] = set()
                            st.rerun()
                else:
                    for step in steps:
                        st.markdown(step)
            else:
                st.markdown("_Keine Zubereitung angegeben_")

        # ── Koch-Tipps (goldene Tipp-Box) ─────────────────────────────────
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
with st.spinner("🥘 Rezepte werden aus dem Kochbuch geholt …"):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Daten: {e}")
        st.stop()

if df.empty:
    st.warning("Das Google Sheet enthält noch keine Rezepte.")
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# HERO HEADER – Screenshot-getreue Terrakotta-Leiste
# ══════════════════════════════════════════════════════════════════════════════
avg_zeit  = int(df["Benötigte Zeit"].mean()) if not df.empty else 0
n_rezepte = len(df)
n_fav     = len(st.session_state.favoriten)

st.markdown(f"""
<div class="hero-header">
    <h1 class="hero-title">🥘 Mein Kochbuch</h1>
    <p class="hero-subtitle">Deine persönliche Rezeptsammlung — mit Liebe zusammengetragen.</p>
    <div class="hero-stats">
        <div class="hero-stat">
            <span class="hero-stat-number">{n_rezepte}</span>
            <span class="hero-stat-label">Rezepte</span>
        </div>
        <div class="hero-stat">
            <span class="hero-stat-number">{avg_zeit}</span>
            <span class="hero-stat-label">Ø Min</span>
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
tab1, tab2, tab3 = st.tabs(["🥘 Alle Rezepte", "❤️ Favoriten", "🛒 Zutaten-Check"])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – ALLE REZEPTE
# ════════════════════════════════════════════════════════════════════════════
with tab1:

    with st.sidebar:
        st.markdown("## 🔍 Filtern")
        st.markdown("---")

        search_term = st.text_input("Suche nach Gericht", placeholder="z. B. Pasta, Suppe …")
        st.markdown("---")

        min_zeit = int(df["Benötigte Zeit"].min())
        max_zeit = int(df["Benötigte Zeit"].max())
        if min_zeit == max_zeit:
            max_zeit = min_zeit + 1

        zeit_range = st.slider(
            "⏱️ Benötigte Zeit (Min.)",
            min_value=min_zeit, max_value=max_zeit,
            value=(min_zeit, max_zeit), step=5,
        )
        st.markdown("---")

        def ms_filter(label, column, emoji=""):
            options = sorted(df[column].dropna().unique().tolist())
            options = [o for o in options if o]
            return st.multiselect(f"{emoji} {label}", options=options)

        sel_kategorie  = ms_filter("Kategorie",     "Kategorie",     "🍴")
        sel_ernaehrung = ms_filter("Ernährungsform", "Ernährungsform","🌿")
        sel_saison     = ms_filter("Saison-Check",   "Saison-Check",  "🌸")
        sel_aufwand    = ms_filter("Aufwand",         "Aufwand",       "⚡")

        st.markdown("---")
        st.markdown("""
        <div style="color:rgba(240,224,204,0.65); font-size:0.78rem; line-height:1.65;">
        🖨️ <strong style="color:rgba(240,224,204,0.85)">Druck-Tipp:</strong><br>
        Strg+P öffnet den Druckdialog.<br>
        Layout ist für DIN-A4 optimiert.
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
        st.metric("🥘 Rezepte", len(filtered))
    with col2:
        avg_t = int(filtered["Benötigte Zeit"].mean()) if not filtered.empty else 0
        st.metric("⏱️ Ø Zeit", f"{avg_t} min")
    with col3:
        st.metric("🍴 Kategorien", filtered["Kategorie"].nunique())
    with col4:
        st.metric("🌿 Ernährungsformen", filtered["Ernährungsform"].nunique())

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── Rezepte anzeigen ──────────────────────────────────────────────────
    if filtered.empty:
        st.markdown("""
        <div class="no-results">
            <h2>Nichts gefunden 🥺</h2>
            <p>Passe deine Filter an — es warten noch viele Rezepte auf dich!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(
            f'<p class="rezepte-header">✨ {len(filtered)} Rezept{"e" if len(filtered) != 1 else ""} gefunden</p>',
            unsafe_allow_html=True,
        )
        for idx, (_, row) in enumerate(filtered.iterrows()):
            rendere_rezept_karte(row, idx_key=f"tab1_{idx}")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – FAVORITEN
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="zutat-check-header" style="background: linear-gradient(135deg,#FFEAE8,#FFDAD8); border-color:rgba(240,168,152,0.4);">
        <h2>❤️ Meine Lieblingsrezepte</h2>
        <p>Alle mit dem Herz markierten Rezepte – für diese Sitzung gespeichert.</p>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.favoriten:
        st.markdown("""
        <div class="no-results">
            <h2>Noch keine Favoriten 🤍</h2>
            <p>Öffne ein Rezept in „Alle Rezepte" und klicke auf 🤍 Favorit.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        fav_df = df[df["Name des Gerichts"].isin(st.session_state.favoriten)]
        st.markdown(
            f'<p class="rezepte-header">❤️ {len(fav_df)} gespeicherte{"s" if len(fav_df)==1 else ""} Rezept{"e" if len(fav_df)!=1 else ""}</p>',
            unsafe_allow_html=True,
        )
        for idx, (_, row) in enumerate(fav_df.iterrows()):
            rendere_rezept_karte(row, idx_key=f"tab2_{idx}")

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        if st.button("❌ Alle Favoriten löschen"):
            st.session_state.favoriten = set()
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 – ZUTATEN-CHECK
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="zutat-check-header">
        <h2>🛒 Was hab ich im Kühlschrank?</h2>
        <p>
            Wähle deine vorhandenen Zutaten – das Kochbuch zeigt dir, was du kochen kannst.<br>
            <strong>Mengenangaben werden automatisch ignoriert:</strong>
            „1 Limette" und „Limetten (2 Stück)" werden als dieselbe Zutat erkannt.
            Gewürze und Grundzutaten werden ausgeblendet.
        </p>
    </div>
    """, unsafe_allow_html=True)

    alle_zutaten_kategorisiert = extrahiere_alle_zutaten(df)

    st.markdown('<p class="rezepte-header">🧺 Meine Zutaten auswählen</p>', unsafe_allow_html=True)

    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 1, 1])
    with col_ctrl1:
        zutat_suche = st.text_input(
            "🔍 Zutat suchen",
            placeholder="z. B. Lachs, Tomate …",
            key="zutat_suche",
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
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    st.markdown('<p class="rezepte-header">🍳 Passende Rezepte</p>', unsafe_allow_html=True)

    if not vorhandene_zutaten:
        st.markdown("""
        <div class="no-results">
            <h2>Wähle deine Zutaten oben aus 👆</h2>
            <p>Das Kochbuch sucht dann passende Rezepte für dich.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        matches = berechne_matches(df, vorhandene_zutaten)

        if matches.empty:
            st.markdown("""
            <div class="no-results">
                <h2>Keine passenden Rezepte 🥺</h2>
                <p>Mit diesen Zutaten geht leider noch nichts. Füge mehr hinzu!</p>
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
                st.metric("🥘 Rezepte gesamt", len(matches))

            st.markdown("---")

            # ── Vollständige Matches ──────────────────────────────────────
            if not vollstaendig.empty:
                st.markdown(
                    '<p class="rezepte-header">✅ Diese Rezepte kannst du sofort kochen!</p>',
                    unsafe_allow_html=True,
                )
                for idx, (_, match) in enumerate(vollstaendig.iterrows()):
                    row            = match["row"]
                    name           = row.get("Name des Gerichts", "Unbekannt")
                    zeit           = row.get("Benötigte Zeit", 0)
                    vorhanden      = match["vorhanden"]
                    anzahl_gesamt  = match["anzahl_gesamt"]
                    zutat_tags     = " ".join([f'<span class="zutat-tag">{z}</span>' for z in vorhanden])

                    with st.expander(f"✅ {name}  ·  ⏱ {zeit} min", expanded=False):
                        st.markdown(
                            f'<span class="match-badge-full">Alle {anzahl_gesamt} Zutaten vorhanden 🎉</span>',
                            unsafe_allow_html=True,
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
                                    checked = st.checkbox(step, value=(i in done), key=f"mstep_{idx}_{i}")
                                    if checked:
                                        done.add(i)
                                    else:
                                        done.discard(i)
                            else:
                                for step in steps:
                                    st.markdown(step)

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
                st.markdown(
                    '<p class="rezepte-header">🔸 Fast dabei – nur noch ein paar Zutaten fehlen</p>',
                    unsafe_allow_html=True,
                )

                sort_col, _ = st.columns([2, 2])
                with sort_col:
                    min_anteil = st.slider(
                        "Mindestanteil vorhandener Zutaten",
                        min_value=0, max_value=100, value=50, step=10,
                        format="%d%%", key="min_anteil_slider",
                    )

                partiell_gefiltert = partiell[partiell["anteil"] >= min_anteil / 100]

                if partiell_gefiltert.empty:
                    st.info(f"Keine Rezepte mit mindestens {min_anteil}% der Zutaten vorhanden.")
                else:
                    for _, match in partiell_gefiltert.iterrows():
                        row              = match["row"]
                        name             = row.get("Name des Gerichts", "Unbekannt")
                        zeit             = row.get("Benötigte Zeit", 0)
                        vorhanden        = match["vorhanden"]
                        fehlend          = match["fehlend"]
                        anzahl_gesamt    = match["anzahl_gesamt"]
                        anzahl_vorhanden = match["anzahl_vorhanden"]
                        anteil_pct       = int(match["anteil"] * 100)

                        vorhanden_tags = " ".join([f'<span class="zutat-tag">{z}</span>' for z in vorhanden])
                        fehlend_tags   = " ".join([f'<span class="zutat-tag-missing">{z}</span>' for z in fehlend])

                        with st.expander(
                            f"🔸 {name}  ·  ⏱ {zeit} min  ·  {anzahl_vorhanden}/{anzahl_gesamt} ({anteil_pct}%)",
                            expanded=False,
                        ):
                            st.markdown(
                                f'<span class="match-badge-partial">{anzahl_vorhanden} von {anzahl_gesamt} Zutaten ({anteil_pct}%)</span>',
                                unsafe_allow_html=True,
                            )
                            st.markdown("")
                            col_v, col_f = st.columns(2)
                            with col_v:
                                st.markdown('<div class="section-label">✅ Vorhanden</div>', unsafe_allow_html=True)
                                st.markdown(vorhanden_tags if vorhanden_tags else "_–_", unsafe_allow_html=True)
                            with col_f:
                                st.markdown('<div class="section-label">❌ Noch kaufen</div>', unsafe_allow_html=True)
                                st.markdown(fehlend_tags if fehlend_tags else "_–_", unsafe_allow_html=True)
