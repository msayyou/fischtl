# ─────────────────────────────────────────────────────────────────────────────
#  FiscHôtel Advisor™  —  Diagnostic fiscal immobilier hôtelier
#  REIV Hospitality  ·  Mehdi SAYYOU
#  Modules : IS/IR · Asset/Share Deal · Step-up fusion · Arbitrage global J+3
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from io import BytesIO

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FiscHôtel Advisor™",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Instrument Sans', sans-serif;
}

/* Header brand */
.fh-brand {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    letter-spacing: -0.5px;
    color: #0f0f0e;
    margin-bottom: 2px;
}
.fh-brand em { color: #0d7a5f; font-style: italic; }
.fh-sub {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #9a9a96;
    letter-spacing: 0.06em;
    margin-bottom: 20px;
}

/* Metric cards */
.kpi-card {
    background: #f3f1ec;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.kpi-card.green  { background: #e0f2ec; border-left: 3px solid #0d7a5f; }
.kpi-card.amber  { background: #fef3e0; border-left: 3px solid #b06a00; }
.kpi-card.red    { background: #fdeaea; border-left: 3px solid #b32b2b; }
.kpi-card.blue   { background: #e8eef9; border-left: 3px solid #1a4fa0; }
.kpi-label { font-size: 11px; color: #6b6b68; font-weight: 600;
             letter-spacing: 0.06em; text-transform: uppercase; }
.kpi-value { font-family: 'DM Mono', monospace; font-size: 22px;
             font-weight: 600; color: #0f0f0e; margin: 2px 0; }
.kpi-sub   { font-size: 11px; color: #9a9a96; }

/* Verdict band */
.verdict {
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 13px;
    line-height: 1.7;
    margin-top: 12px;
}
.verdict.ok   { background: #e0f2ec; border-left: 4px solid #0d7a5f; color: #085041; }
.verdict.warn { background: #fef3e0; border-left: 4px solid #b06a00; color: #7a4500; }
.verdict.bad  { background: #fdeaea; border-left: 4px solid #b32b2b; color: #7a1a1a; }

/* Section title */
.sec-title {
    font-family: 'DM Serif Display', serif;
    font-size: 17px;
    color: #0f0f0e;
    border-bottom: 1px solid #e8e5de;
    padding-bottom: 8px;
    margin: 20px 0 14px;
}
.sec-sub {
    font-size: 11px;
    color: #9a9a96;
    font-style: italic;
    margin-bottom: 14px;
}

/* Disclaimer */
.disc {
    font-size: 11px;
    color: #9a9a96;
    background: #f3f1ec;
    border-radius: 6px;
    padding: 10px 14px;
    line-height: 1.6;
    margin-top: 16px;
}

/* Timeline step */
.tl-row { display: flex; gap: 0; margin: 16px 0; }
.tl-step {
    flex: 1;
    text-align: center;
    position: relative;
    padding: 0 4px;
}
.tl-dot {
    width: 30px; height: 30px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 600;
    margin: 0 auto 6px;
    font-family: 'DM Mono', monospace;
}
.tl-dot.ok  { background: #0d7a5f; color: #fff; }
.tl-dot.ko  { background: #b32b2b; color: #fff; }
.tl-dot.mid { background: #b06a00; color: #fff; }
.tl-txt { font-size: 10.5px; color: #6b6b68; line-height: 1.4; }
.tl-val { font-size: 11px; font-weight: 600; color: #0f0f0e;
          font-family: 'DM Mono', monospace; margin-top: 2px; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0f0f0e !important;
}
section[data-testid="stSidebar"] * { color: #e8e5de !important; }
section[data-testid="stSidebar"] .stSlider > label { color: #9a9a96 !important; font-size: 12px; }
section[data-testid="stSidebar"] hr { border-color: #2a2a28 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #f3f1ec;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 500;
    font-size: 13px;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: #0d7a5f !important;
    color: white !important;
}

/* Plotly chart frames */
.js-plotly-plot { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MOTEUR DE CALCUL
# ══════════════════════════════════════════════════════════════════════════════

def pv_annuites(flux: float, taux: float, n: int) -> float:
    """Valeur actuelle nette d'une série d'annuités constantes."""
    if taux == 0:
        return flux * n
    return flux * (1 - (1 + taux) ** -n) / taux


def abattements_ir(duree: int) -> tuple[float, float]:
    """Calcule les abattements IR et PS selon la durée de détention."""
    if duree <= 5:
        return 0.0, 0.0
    ab_ir = min((duree - 5) * 6, 100) if duree < 22 else 100.0
    if duree <= 21:
        ab_ps = (duree - 5) * 1.65
    elif duree <= 29:
        ab_ps = (22 - 5) * 1.65 + (duree - 22) * 9
    else:
        ab_ps = 100.0
    return ab_ir, min(ab_ps, 100.0)


def surtaxe_pv(pv_nette_m: float) -> float:
    """Surtaxe sur plus-values immobilières > 50 k€ (en M€)."""
    pv = pv_nette_m * 1_000_000
    if pv <= 50_000:
        return 0.0
    tranches = [
        (50_000,  100_000, 0.02),
        (100_000, 150_000, 0.03),
        (150_000, 200_000, 0.04),
        (200_000, 250_000, 0.05),
        (250_000, float("inf"), 0.06),
    ]
    total = 0.0
    for lo, hi, rate in tranches:
        if pv > lo:
            total += (min(pv, hi) - lo) * rate
    return total / 1_000_000


def calcul_module_ir(p: dict) -> dict:
    """Module 1 — Arbitrage sortie IS vs IR."""
    val, vnc, amort = p["val"], p["vnc"], p["amort"]
    taux_is, tmi = p["taux_is"], p["tmi"]
    duree_det = p["duree_det"]

    pv_eco = val - vnc

    # IS
    vnc_net = vnc - amort
    pv_is = val - vnc_net
    imp_is = max(0, pv_is) * taux_is
    base_div = max(0, pv_is - imp_is)
    imp_div = base_div * 0.30
    net_is = val - imp_is - imp_div
    fr_is = (imp_is + imp_div) / val if val else 0

    # IR
    ab_ir, ab_ps = abattements_ir(duree_det)
    pv_ir_impo = max(0, pv_eco) * (1 - ab_ir / 100)
    pv_ps_impo = max(0, pv_eco) * (1 - ab_ps / 100)
    imp_irpp = pv_ir_impo * 0.19
    imp_ps = pv_ps_impo * 0.172
    surt = surtaxe_pv(pv_ir_impo)
    tot_ir = imp_irpp + imp_ps + surt
    net_ir = val - tot_ir
    fr_ir = tot_ir / val if val else 0

    return dict(
        pv_eco=pv_eco, vnc_net=vnc_net, pv_is=pv_is,
        imp_is=imp_is, imp_div=imp_div, net_is=net_is, fr_is=fr_is,
        ab_ir=ab_ir, ab_ps=ab_ps, pv_ir_impo=pv_ir_impo,
        imp_irpp=imp_irpp, imp_ps=imp_ps, surt=surt,
        tot_ir=tot_ir, net_ir=net_ir, fr_ir=fr_ir,
        winner="IR" if fr_ir < fr_is else "IS",
    )


def calcul_module_deal(p: dict) -> dict:
    """Module 2 — Asset deal vs Share deal."""
    val, vnc, dette, fdc = p["val"], p["vnc"], p["dette"], p["fdc"]
    taux_is = p["taux_is"]
    typesoc = p["typesoc"]
    tact = p["tact"]
    dur = p["dur"]

    prix_titres = val - dette
    terrain = val * p["ter"]
    bati = val * (1 - p["ter"])

    # Asset deal — acquéreur
    dmto_asset = (val + fdc) * 0.065
    cout_acq_asset = val + fdc + dmto_asset
    base_amort_asset = bati + fdc
    van_amort_asset = pv_annuites(base_amort_asset / dur * taux_is, tact, dur)

    # Asset deal — cédant
    pv_asset_ced = val + fdc - vnc
    is_asset_ced = max(0, pv_asset_ced) * taux_is
    net_ced_asset = val + fdc - is_asset_ced

    # Share deal — acquéreur
    if typesoc == "SARL":
        dmto_share = max(0, prix_titres - 0.023) * 0.03
    else:
        dmto_share = prix_titres * 0.001
    cout_acq_share = prix_titres + dette + dmto_share

    # Share deal — cédant
    pv_titres = prix_titres - vnc
    is_share = max(0, pv_titres) * taux_is
    net_ced_share = prix_titres - is_share

    econ_acq = cout_acq_asset - cout_acq_share
    econ_ced = net_ced_share - net_ced_asset

    return dict(
        prix_titres=prix_titres, terrain=terrain, bati=bati,
        dmto_asset=dmto_asset, cout_acq_asset=cout_acq_asset,
        base_amort_asset=base_amort_asset, van_amort_asset=van_amort_asset,
        is_asset_ced=is_asset_ced, net_ced_asset=net_ced_asset,
        dmto_share=dmto_share, cout_acq_share=cout_acq_share,
        is_share=is_share, net_ced_share=net_ced_share,
        econ_acq=econ_acq, econ_ced=econ_ced,
    )


def calcul_module_stepup(p: dict) -> dict:
    """Module 3 — Step-up fiscal fusion-absorption."""
    val, vnc = p["val"], p["vnc"]
    ter, dur = p["ter"], p["dur"]
    taux_is, tact = p["taux_is"], p["tact"]

    terrain = val * ter
    bati = val * (1 - ter)
    vnc_terrain = vnc * ter
    vnc_bati = vnc * (1 - ter)

    # Avant fusion
    base_avant = vnc_bati
    amort_ann_avant = base_avant / dur
    eco_is_avant = amort_ann_avant * taux_is
    van_avant = pv_annuites(eco_is_avant, tact, dur)

    # Après fusion (step-up)
    base_apres = bati
    amort_ann_apres = base_apres / dur
    eco_is_apres = amort_ann_apres * taux_is
    van_apres = pv_annuites(eco_is_apres, tact, dur)

    # Gain step-up brut
    gain_brut = van_apres - van_avant

    # Réintégration terrain
    pv_lat_terrain = terrain - vnc_terrain
    reint_an = pv_lat_terrain / 5
    is_reint_an = reint_an * taux_is
    cout_reint = pv_annuites(is_reint_an, tact, 5)

    gain_net = gain_brut - cout_reint

    # Calendrier réintégration
    cal = []
    for i in range(1, 6):
        act = is_reint_an / (1 + tact) ** i
        cal.append({"Année": f"J+{i}", "PV réintégrée (k€)": round(reint_an * 1000, 1),
                    "IS dû (k€)": round(is_reint_an * 1000, 1),
                    "IS actualisé (k€)": round(act * 1000, 1)})
    cal.append({"Année": "Total", "PV réintégrée (k€)": round(pv_lat_terrain * 1000, 1),
                "IS dû (k€)": round(is_reint_an * 5 * 1000, 1),
                "IS actualisé (k€)": round(cout_reint * 1000, 1)})

    return dict(
        terrain=terrain, bati=bati, vnc_bati=vnc_bati,
        base_avant=base_avant, amort_ann_avant=amort_ann_avant,
        eco_is_avant=eco_is_avant, van_avant=van_avant,
        base_apres=base_apres, amort_ann_apres=amort_ann_apres,
        eco_is_apres=eco_is_apres, van_apres=van_apres,
        pv_lat_terrain=pv_lat_terrain, is_reint_an=is_reint_an,
        cout_reint=cout_reint, gain_brut=gain_brut, gain_net=gain_net,
        calendrier=cal,
    )


def calcul_module_global(p: dict, d: dict, s: dict) -> dict:
    """Module 4 — Arbitrage global J+0 vs J+3."""
    delai = 3
    tact, dur = p["tact"], p["dur"]
    taux_is = p["taux_is"]
    fact_act = (1 + tact) ** delai

    # Scénario A : Asset deal J+0
    van_amort_a = d["van_amort_asset"]
    dmto_a = d["dmto_asset"]
    van_nette_a = van_amort_a - dmto_a

    # Scénario B : Share deal + fusion J+3
    # Phase 1 : amort VNC sur 3 ans
    van_phase1 = pv_annuites(s["eco_is_avant"], tact, delai)
    # Phase 2 : step-up actif sur (dur - 3) ans, actualisé à J+0
    van_phase2 = pv_annuites(s["eco_is_apres"], tact, dur - delai) / fact_act
    # Coût réintégration actualisé à J+0
    cout_reint_j0 = s["cout_reint"] / fact_act
    dmto_b = d["dmto_share"]
    econ_dmto = dmto_a - dmto_b
    van_nette_b = van_phase1 + van_phase2 - cout_reint_j0 - dmto_b

    diff = van_nette_a - van_nette_b
    winner = "B" if diff > 0 else "A"

    # Courbe d'accumulation VAN sur le temps
    années = list(range(0, dur + 1))
    van_cum_a, van_cum_b = [], []
    cum_a = -dmto_a
    cum_b = -dmto_b
    for i, an in enumerate(années):
        van_cum_a.append(cum_a)
        van_cum_b.append(cum_b)
        if i < dur:
            eco_a = d["base_amort_asset"] / dur * taux_is / (1 + tact) ** (i + 1)
            cum_a += eco_a
            if i < delai:
                eco_b = s["eco_is_avant"] / (1 + tact) ** (i + 1)
            else:
                eco_b = s["eco_is_apres"] / (1 + tact) ** (i + 1)
                if delai <= i < delai + 5:
                    eco_b -= s["is_reint_an"] / (1 + tact) ** (i + 1)
            cum_b += eco_b

    return dict(
        van_nette_a=van_nette_a, van_nette_b=van_nette_b,
        diff=diff, winner=winner,
        van_phase1=van_phase1, van_phase2=van_phase2,
        cout_reint_j0=cout_reint_j0, dmto_a=dmto_a, dmto_b=dmto_b,
        econ_dmto=econ_dmto, van_amort_a=van_amort_a,
        années=années, van_cum_a=van_cum_a, van_cum_b=van_cum_b,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS UI
# ══════════════════════════════════════════════════════════════════════════════

def fm(v: float, d: int = 2) -> str:
    return f"{v:,.{d}f} M€".replace(",", " ")

def fk(v: float) -> str:
    return f"{v * 1000:,.0f} k€".replace(",", " ")

def fp(v: float, d: int = 1) -> str:
    return f"{v:.{d}f}%"

def kpi(label: str, value: str, sub: str = "", color: str = "") -> None:
    css = f"kpi-card {color}".strip()
    st.markdown(f"""
    <div class="{css}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

def verdict(text: str, kind: str = "ok") -> None:
    st.markdown(f'<div class="verdict {kind}">{text}</div>', unsafe_allow_html=True)

def section(title: str, sub: str = "") -> None:
    st.markdown(f'<div class="sec-title">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="sec-sub">{sub}</div>', unsafe_allow_html=True)

def disc(text: str) -> None:
    st.markdown(f'<div class="disc">{text}</div>', unsafe_allow_html=True)

COLORS = {
    "teal":  "#0d7a5f",
    "red":   "#b32b2b",
    "amber": "#b06a00",
    "blue":  "#1a4fa0",
    "gray":  "#9a9a96",
}

def bar_chart(labels, values, colors, title=""):
    fig = go.Figure()
    for label, val, color in zip(labels, values, colors):
        fig.add_trace(go.Bar(
            name=label, x=[label], y=[val],
            marker_color=color, text=[fm(val)], textposition="outside",
            width=0.5,
        ))
    fig.update_layout(
        height=260, margin=dict(l=10, r=10, t=30 if title else 10, b=10),
        title=title, title_font_size=13,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False, yaxis_visible=False,
        xaxis=dict(tickfont=dict(size=11, color="#3a3a38")),
        bargap=0.3,
    )
    return fig

def waterfall_chart(labels, values, colors, title=""):
    fig = go.Figure(go.Waterfall(
        name="", orientation="v",
        x=labels, y=values,
        connector=dict(line=dict(color="#e8e5de", width=1)),
        decreasing=dict(marker_color=COLORS["red"]),
        increasing=dict(marker_color=COLORS["teal"]),
        totals=dict(marker_color=COLORS["blue"]),
        text=[fm(v) for v in values], textposition="outside",
    ))
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=30 if title else 10, b=10),
        title=title, title_font_size=13,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — PARAMÈTRES
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="fh-brand">Fisc<em>Hôtel</em> Advisor™</div>
    <div class="fh-sub">REIV HOSPITALITY · DIAGNOSTIC FISCAL</div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**🏨 Actif hôtelier**")
    val   = st.slider("Valeur vénale (M€)",      1.0, 100.0, 20.0, 0.5)
    vnc   = st.slider("VNC bilan actuel (M€)",    0.5,  50.0,  8.0, 0.5)
    ter   = st.slider("Part terrain (%)",          5,    55,   20,   1) / 100
    dette = st.slider("Dette dans la structure (M€)", 0.0, 70.0, 8.0, 0.5)
    fdc   = st.slider("Goodwill / fonds de commerce (M€)", 0.0, 15.0, 2.0, 0.5)
    amort = st.slider("Amortissements cumulés (M€)", 0.0, 20.0, 3.0, 0.1)
    dur   = st.slider("Durée amortissement (ans)", 20, 50, 30, 5)

    st.markdown("---")
    st.markdown("**⚖️ Fiscal & structure**")
    taux_is  = st.select_slider("Taux IS (%)", [15, 25], 25) / 100
    tmi      = st.slider("TMI IR cédant (%)", 11, 45, 41, 1) / 100
    duree_det = st.slider("Durée de détention (ans)", 1, 35, 10, 1)
    tact     = st.slider("Taux d'actualisation (%)", 4.0, 12.0, 7.0, 0.5) / 100
    typesoc  = st.selectbox("Type société cédée", ["SARL", "SAS / SA"])

    st.markdown("---")
    prix_titres = val - dette
    st.markdown(f"""
    **Synthèse actif**
    - Valeur vénale : **{fm(val)}**
    - Equity (val − dette) : **{fm(prix_titres)}**
    - Bâti / Terrain : **{fm(val*(1-ter))} / {fm(val*ter)}**
    - PV économique : **{fm(val-vnc)}**
    """)


# ══════════════════════════════════════════════════════════════════════════════
#  PARAMÈTRES PACK
# ══════════════════════════════════════════════════════════════════════════════

p = dict(val=val, vnc=vnc, ter=ter, dette=dette, fdc=fdc, amort=amort,
         dur=dur, taux_is=taux_is, tmi=tmi, duree_det=duree_det,
         tact=tact, typesoc=typesoc)

# ── Calculs ───────────────────────────────────────────────────────────────────
r_ir = calcul_module_ir(p)
r_deal = calcul_module_deal(p)
r_su = calcul_module_stepup(p)
r_glob = calcul_module_global(p, r_deal, r_su)


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER PAGE
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="fh-brand" style="font-size:24px;margin-bottom:4px">
    Fisc<em>Hôtel</em> Advisor™
</div>
<div class="fh-sub">Diagnostic fiscal immobilier hôtelier · REIV Hospitality</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 IS vs IR — Sortie",
    "🤝 Asset vs Share Deal",
    "🔼 Step-up fiscal",
    "⚖️ Arbitrage global J+0 / J+3",
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — IS vs IR
# ══════════════════════════════════════════════════════════════════════════════

with tab1:
    section("Arbitrage de sortie — Régime IS vs Régime IR",
            f"Actif {fm(val)} · Durée détention {duree_det} ans · PV économique {fm(r_ir['pv_eco'])}")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("Net cédant — IS", fm(r_ir["net_is"]),
            f"Friction {fp(r_ir['fr_is']*100)} · {'Meilleur' if r_ir['winner']=='IS' else 'Plus cher'}",
            "green" if r_ir["winner"] == "IS" else "")
    with col2:
        kpi("Net cédant — IR", fm(r_ir["net_ir"]),
            f"Friction {fp(r_ir['fr_ir']*100)} · {'Meilleur' if r_ir['winner']=='IR' else 'Plus cher'}",
            "green" if r_ir["winner"] == "IR" else "")
    with col3:
        kpi("Écart net IS − IR",
            fm(abs(r_ir["net_ir"] - r_ir["net_is"])),
            f"En faveur du régime {r_ir['winner']}", "blue")

    st.markdown("---")
    col_is, col_ir = st.columns(2)

    with col_is:
        st.markdown("**Régime IS — Détail**")
        df_is = pd.DataFrame([
            ("Prix de cession",          fm(val),                ""),
            ("VNC après amortissements", fm(r_ir["vnc_net"]),    ""),
            ("PV fiscale IS",            fm(r_ir["pv_is"]),      ""),
            ("IS 25% sur PV",           f"− {fm(r_ir['imp_is'])}", "🔴"),
            ("PFU 30% sur dividende",   f"− {fm(r_ir['imp_div'])}", "🔴"),
            ("Net cédant",              fm(r_ir["net_is"]),      "✅"),
        ], columns=["Poste", "Montant", ""])
        st.dataframe(df_is, hide_index=True, use_container_width=True,
                     column_config={"": st.column_config.TextColumn(width="small")})

    with col_ir:
        st.markdown("**Régime IR — Détail**")
        rows_ir = [
            ("PV économique",           fm(r_ir["pv_eco"]),      ""),
            (f"Abatt. IR {r_ir['ab_ir']:.0f}% / PS {r_ir['ab_ps']:.0f}% ({duree_det} ans)",
             fm(r_ir['pv_eco'] * r_ir['ab_ir'] / 100), "🟢"),
            ("PV imposable IR",         fm(r_ir["pv_ir_impo"]),  ""),
            ("IRPP 19%",               f"− {fm(r_ir['imp_irpp'])}", "🔴"),
            ("PS 17,2%",               f"− {fm(r_ir['imp_ps'])}", "🔴"),
        ]
        if r_ir["surt"] > 0:
            rows_ir.append(("Surtaxe PV > 50 k€", f"− {fm(r_ir['surt'])}", "🔴"))
        rows_ir.append(("Net cédant", fm(r_ir["net_ir"]), "✅"))
        df_ir = pd.DataFrame(rows_ir, columns=["Poste", "Montant", ""])
        st.dataframe(df_ir, hide_index=True, use_container_width=True,
                     column_config={"": st.column_config.TextColumn(width="small")})

    section("Friction fiscale comparée")
    fig_ir = go.Figure()
    frictions = [
        ("IS — friction totale", r_ir["fr_is"] * 100, COLORS["red"]),
        ("IR — friction totale", r_ir["fr_ir"] * 100, COLORS["teal"]),
        ("Différentiel", abs(r_ir["fr_is"] - r_ir["fr_ir"]) * 100, COLORS["blue"]),
    ]
    for label, val_f, color in frictions:
        fig_ir.add_trace(go.Bar(
            name=label, x=[label], y=[val_f],
            marker_color=color,
            text=[f"{val_f:.1f}%"], textposition="outside",
            width=0.45,
        ))
    fig_ir.update_layout(
        height=250, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(ticksuffix="%", gridcolor="#e8e5de"),
        xaxis=dict(tickfont=dict(size=11)),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_ir, use_container_width=True)

    # Courbe abattements IR sur le temps
    section("Évolution des abattements IR / PS selon la durée de détention")
    années_ab = list(range(1, 36))
    ab_ir_curve = [abattements_ir(a)[0] for a in années_ab]
    ab_ps_curve = [abattements_ir(a)[1] for a in années_ab]
    fig_ab = go.Figure()
    fig_ab.add_trace(go.Scatter(x=années_ab, y=ab_ir_curve, name="Abatt. IRPP",
                                line=dict(color=COLORS["teal"], width=2), fill="tozeroy",
                                fillcolor="rgba(13,122,95,0.08)"))
    fig_ab.add_trace(go.Scatter(x=années_ab, y=ab_ps_curve, name="Abatt. PS",
                                line=dict(color=COLORS["blue"], width=2, dash="dot")))
    fig_ab.add_vline(x=duree_det, line_dash="dash", line_color=COLORS["amber"],
                     annotation_text=f"Votre détention ({duree_det} ans)",
                     annotation_position="top right")
    fig_ab.update_layout(
        height=260, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(ticksuffix="%", range=[0, 105], gridcolor="#e8e5de"),
        xaxis=dict(title="Durée de détention (ans)"),
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig_ab, use_container_width=True)

    v_kind = "ok" if r_ir["winner"] == "IR" else "warn"
    if r_ir["winner"] == "IR":
        v_text = (f"<b>Avantage IR</b> — Sur {duree_det} ans de détention (abatt. "
                  f"{r_ir['ab_ir']:.0f}% IR / {r_ir['ab_ps']:.0f}% PS), le régime IR génère "
                  f"<b>{fm(abs(r_ir['net_ir'] - r_ir['net_is']))}</b> de plus en net cédant. "
                  f"Structure recommandée : SCI IR ou détention directe plutôt qu'IS "
                  f"si l'horizon de sortie est confirmé.")
    else:
        seuil = 22 if r_ir["ab_ir"] < 100 else duree_det
        v_text = (f"<b>Avantage IS</b> — À {duree_det} ans, les abattements IR ({r_ir['ab_ir']:.0f}%) "
                  f"ne compensent pas encore la friction IS. "
                  f"Le régime IR devient supérieur à partir de <b>22 ans</b> (exonération IRPP complète). "
                  f"Envisager un allongement de la durée de détention ou une restructuration avant cession.")
    verdict(v_text, v_kind)

    disc("IS : IS 25% sur PV vs VNC + PFU 30% sur dividende. "
         "IR : 19% IRPP + 17,2% PS avec abattements progressifs "
         "(6%/an de 6 à 21 ans, exo IR à 22 ans, PS à 30 ans) + surtaxe PV nette > 50 k€. "
         "Hors situations spécifiques (SIIC, régime mère-fille, niches sectorielles). "
         "Cet outil ne constitue pas un conseil fiscal — consulter un avocat spécialisé.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — ASSET vs SHARE DEAL
# ══════════════════════════════════════════════════════════════════════════════

with tab2:
    d = r_deal
    section("Structuration de l'acquisition — Asset deal vs Share deal",
            f"Valeur vénale {fm(val)} · Prix titres (equity) {fm(d['prix_titres'])} · Dette {fm(dette)}")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("DMTO asset deal", fm(d["dmto_asset"]),
            f"≈ 6,5% sur {fm(val + fdc)}", "red")
    with col2:
        kpi("Droits share deal", fm(d["dmto_share"]),
            f"{'3% parts SARL' if typesoc=='SARL' else '0,1% titres SAS'}", "amber")
    with col3:
        kpi("Économie droits (share)", fm(abs(d["econ_acq"])),
            f"{'Share deal moins cher en droits' if d['econ_acq']>0 else 'Asset deal moins cher'}",
            "green" if d["econ_acq"] > 0 else "")

    st.markdown("---")
    col_acq, col_ced = st.columns(2)

    with col_acq:
        st.markdown("**Vision acquéreur**")
        df_acq = pd.DataFrame([
            ("Prix payé",              fm(val + fdc),              fm(d["prix_titres"] + dette)),
            ("Droits acquisition",     f"+ {fm(d['dmto_asset'])}", f"+ {fm(d['dmto_share'])}"),
            ("Base amortissable",      fm(d["base_amort_asset"]), "0 (VNC historique)"),
            ("VAN éco. IS amort.",     fm(d["van_amort_asset"]),  "Non disponible"),
            ("Coût total acquéreur",   fm(d["cout_acq_asset"]),   fm(d["cout_acq_share"])),
        ], columns=["Poste", "Asset deal", "Share deal"])
        st.dataframe(df_acq, hide_index=True, use_container_width=True)

    with col_ced:
        st.markdown("**Vision cédant**")
        df_ced = pd.DataFrame([
            ("Prix reçu brut",         fm(val + fdc),             fm(d["prix_titres"])),
            ("IS sur PV",             f"− {fm(d['is_asset_ced'])}", f"− {fm(d['is_share'])}"),
            ("Dette restante dans sté", "—",                     f"{fm(dette)} (reste)"),
            ("Net encaissé",           fm(d["net_ced_asset"]),    fm(d["net_ced_share"])),
        ], columns=["Poste", "Asset deal", "Share deal"])
        st.dataframe(df_ced, hide_index=True, use_container_width=True)

    section("Zones de négociation — Surplus de prix acceptable")
    van_step = d["van_amort_asset"]
    surprix_max = min(van_step, d["econ_acq"])
    fig_neg = go.Figure()
    cats = ["Économie DMTO (share)", "VAN amort. asset deal",
            "Surprix max acceptable (acquéreur)"]
    vals = [d["econ_acq"], van_step, surprix_max]
    colors_neg = [COLORS["teal"], COLORS["blue"], COLORS["amber"]]
    for cat, v, c in zip(cats, vals, colors_neg):
        fig_neg.add_trace(go.Bar(x=[cat], y=[v], marker_color=c,
                                  text=[fm(v)], textposition="outside", width=0.4))
    fig_neg.update_layout(
        height=260, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="M€", gridcolor="#e8e5de"),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_neg, use_container_width=True)

    v_kind = "warn"
    v_text = (f"<b>Intérêts divergents — zone de négociation.</b> "
              f"L'acquéreur économise <b>{fm(abs(d['econ_acq']))}</b> en droits avec le share deal, "
              f"mais perd la base amortissable (<b>{fm(d['base_amort_asset'])}</b> en asset deal → "
              f"VAN éco. IS ≈ <b>{fm(d['van_amort_asset'])}</b>). "
              f"Le cédant préfère le share deal : "
              f"{('gain net de ' + fm(abs(d['econ_ced']))) if d['econ_ced'] > 0 else ('diff de ' + fm(abs(d['econ_ced'])) + ' en faveur de lasset deal')}. "
              f"Surprix max acceptable pour l'acquéreur : <b>{fm(surprix_max)}</b>.")
    verdict(v_text, v_kind)

    disc("DMTO asset deal ≈ 6,5% (5,80% droits + 0,80% notaire) sur valeur immeuble + goodwill. "
         "Share deal SARL : 3% sur prix parts (abattement 23 k€). SAS/SA : 0,1% sur prix titres. "
         "Pas de reprise base amortissable en share deal sans fusion ultérieure (art. 210 A CGI). "
         "La zone de surprix représente la VAN maximale de l'avantage amortissement pour l'acquéreur.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — STEP-UP
# ══════════════════════════════════════════════════════════════════════════════

with tab3:
    s = r_su
    section("Step-up fiscal — Fusion-absorption post-acquisition (art. 210 A CGI)",
            f"Gain brut {fm(s['gain_brut'])} · Coût réintégration {fm(s['cout_reint'])} · Gain net {fm(s['gain_net'])}")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("Gain step-up brut (VAN)", fm(s["gain_brut"]),
            f"Suramort. actualisé sur {dur} ans", "green")
    with col2:
        kpi("Coût réintégration terrain", fm(s["cout_reint"]),
            f"IS PV latente {fm(s['pv_lat_terrain'])} × 1/5 × 5 ans", "amber")
    with col3:
        kpi("Gain net step-up (VAN)", fm(s["gain_net"]),
            "Opération favorable" if s["gain_net"] > 0 else "Coût > gain — Vigilance",
            "green" if s["gain_net"] > 0 else "red")

    st.markdown("---")
    col_av, col_ap = st.columns(2)

    with col_av:
        st.markdown("**Sans fusion — share deal pur**")
        df_av = pd.DataFrame([
            ("Base amortissable (VNC bâti)", fm(s["base_avant"])),
            ("Amortissement annuel",         fk(s["amort_ann_avant"])),
            ("Économie IS annuelle",         fk(s["eco_is_avant"])),
            (f"VAN éco. IS ({dur} ans)",     fm(s["van_avant"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_av, hide_index=True, use_container_width=True)

    with col_ap:
        st.markdown("**Après fusion — step-up actif**")
        df_ap = pd.DataFrame([
            ("Base amortissable (valeur vénale bâti)", fm(s["base_apres"])),
            ("Amortissement annuel step-up",           fk(s["amort_ann_apres"])),
            ("Économie IS annuelle",                   fk(s["eco_is_apres"])),
            (f"VAN éco. IS ({dur} ans)",               fm(s["van_apres"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_ap, hide_index=True, use_container_width=True)

    section("Calendrier de réintégration terrain — art. 210 A al. 3")
    df_cal = pd.DataFrame(s["calendrier"])
    st.dataframe(df_cal, hide_index=True, use_container_width=True)

    section("Comparaison VAN — Step-up vs coût terrain")
    fig_su = go.Figure()
    su_cats = ["Gain step-up brut", "Coût réintégration terrain", "Gain net"]
    su_vals = [s["gain_brut"], -s["cout_reint"], s["gain_net"]]
    su_colors = [COLORS["teal"], COLORS["red"], COLORS["blue"] if s["gain_net"] > 0 else COLORS["red"]]
    for cat, v, c in zip(su_cats, su_vals, su_colors):
        fig_su.add_trace(go.Bar(x=[cat], y=[abs(v)], marker_color=c,
                                 text=[fm(v)], textposition="outside", width=0.4))
    fig_su.update_layout(
        height=250, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="M€", gridcolor="#e8e5de"),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_su, use_container_width=True)

    v_kind = "ok" if s["gain_net"] > 0 else "bad"
    if s["gain_net"] > 0:
        ratio = s["gain_net"] / s["gain_brut"] * 100
        v_text = (f"<b>Step-up favorable.</b> VAN nette <b>{fm(s['gain_net'])}</b> "
                  f"({ratio:.0f}% du gain brut après coût terrain). "
                  f"PV latente terrain {fm(s['pv_lat_terrain'])} — coût IS absorbé par le gain amortissement. "
                  f"<b>Délai 3 ans minimum recommandé avant fusion</b> pour écarter le risque d'abus de droit.")
    else:
        v_text = (f"<b>Vigilance.</b> La PV latente terrain ({fm(s['pv_lat_terrain'])}) génère un coût de "
                  f"réintégration IS ({fm(s['cout_reint'])}) qui excède le gain amortissement bâti. "
                  f"Envisager : (1) un asset deal d'emblée, ou (2) une expertise immobilière pour "
                  f"requalifier l'allocation terrain/bâti dans l'acte de fusion.")
    verdict(v_text, v_kind)

    disc("Neutralité IS sur PV de fusion (art. 210 A CGI). "
         "Terrain non amortissable : PV latente réintégrée par cinquièmes sur 5 ans. "
         "Délai minimum 3 ans entre share deal et fusion (risque abus de droit art. L64 LPF). "
         "Engagement de reprise des provisions de la société absorbée. "
         "Déclaration spéciale à déposer dans les 60 jours suivant la fusion.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — ARBITRAGE GLOBAL J+0 vs J+3
# ══════════════════════════════════════════════════════════════════════════════

with tab4:
    g_res = r_glob
    section("Arbitrage global — Asset deal J+0 vs Share deal + Fusion J+3",
            f"VAN comparée sur {dur} ans · Taux actualisation {fp(tact*100)} · Délai fusion 3 ans")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("VAN nette scénario A", fm(g_res["van_nette_a"]),
            "Asset deal direct J+0",
            "green" if g_res["winner"] == "A" else "")
    with col2:
        kpi("VAN nette scénario B", fm(g_res["van_nette_b"]),
            "Share deal + Fusion J+3",
            "green" if g_res["winner"] == "B" else "")
    with col3:
        kpi("Scénario recommandé",
            f"Scénario {g_res['winner']}",
            f"Avantage {fm(abs(g_res['diff']))}",
            "green")

    st.markdown("---")
    section("Timeline décisionnelle")
    timeline_html = """
    <div class="tl-row">
        <div class="tl-step">
            <div class="tl-dot mid">J0</div>
            <div class="tl-txt">Acquisition</div>
            <div class="tl-val">Share deal</div>
        </div>
        <div class="tl-step">
            <div class="tl-dot ko">J+1</div>
            <div class="tl-txt">Attente</div>
            <div class="tl-val">Amort. VNC seul</div>
        </div>
        <div class="tl-step">
            <div class="tl-dot ko">J+2</div>
            <div class="tl-txt">Attente</div>
            <div class="tl-val">Coût délai cumulé</div>
        </div>
        <div class="tl-step">
            <div class="tl-dot mid">J+3</div>
            <div class="tl-txt">Fusion TUP</div>
            <div class="tl-val">Step-up actif</div>
        </div>
        <div class="tl-step">
            <div class="tl-dot ko">J+4–8</div>
            <div class="tl-txt">Réintégration terrain</div>
            <div class="tl-val">IS 1/5 × 5 ans</div>
        </div>
        <div class="tl-step">
            <div class="tl-dot ok">J+8+</div>
            <div class="tl-txt">Gain plein régime</div>
            <div class="tl-val">Step-up actif</div>
        </div>
    </div>
    """
    st.markdown(timeline_html, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Scénario A — Asset deal J+0**")
        df_a = pd.DataFrame([
            ("DMTO acquisition",              f"− {fm(g_res['dmto_a'])}"),
            ("Base amortissable (step-up J+0)", fm(r_deal["base_amort_asset"])),
            (f"VAN éco. IS ({dur} ans)",       fm(g_res["van_amort_a"])),
            ("VAN nette",                     fm(g_res["van_nette_a"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_a, hide_index=True, use_container_width=True)

    with col_b:
        st.markdown("**Scénario B — Share deal + Fusion J+3**")
        df_b = pd.DataFrame([
            ("DMTO share deal",                        f"− {fm(g_res['dmto_b'])}"),
            ("Gain DMTO vs asset deal",                fm(g_res["econ_dmto"])),
            ("VAN amort. phase 1 (J+0 à J+3)",         fm(g_res["van_phase1"])),
            (f"VAN amort. phase 2 (J+3–{dur}, actualisée)", fm(g_res["van_phase2"])),
            ("Coût réintégration terrain (act. à J+0)", f"− {fm(g_res['cout_reint_j0'])}"),
            ("VAN nette",                              fm(g_res["van_nette_b"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_b, hide_index=True, use_container_width=True)

    section("Accumulation de VAN dans le temps — Scénario A vs B")
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=g_res["années"], y=g_res["van_cum_a"],
        name="Scénario A — Asset deal",
        line=dict(color=COLORS["red"], width=2.5),
        fill="tozeroy", fillcolor="rgba(179,43,43,0.06)",
    ))
    fig_cum.add_trace(go.Scatter(
        x=g_res["années"], y=g_res["van_cum_b"],
        name="Scénario B — Share+Fusion",
        line=dict(color=COLORS["teal"], width=2.5, dash="dot"),
        fill="tozeroy", fillcolor="rgba(13,122,95,0.06)",
    ))
    fig_cum.add_vline(x=3, line_dash="dash", line_color=COLORS["amber"],
                      annotation_text="Fusion J+3", annotation_position="top")
    fig_cum.add_vline(x=8, line_dash="dot", line_color=COLORS["gray"],
                      annotation_text="Fin réintégration", annotation_position="top")
    fig_cum.add_hline(y=0, line_color="#e8e5de", line_width=1)
    fig_cum.update_layout(
        height=320, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="VAN cumulée (M€)", gridcolor="#e8e5de"),
        xaxis=dict(title="Années depuis acquisition"),
        legend=dict(orientation="h", y=1.08),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    st.plotly_chart(fig_cum, use_container_width=True)

    section("Comparaison VAN finale")
    fig_final = go.Figure()
    fig_final.add_trace(go.Bar(
        x=["Scénario A — Asset deal J+0", "Scénario B — Share deal + Fusion J+3"],
        y=[g_res["van_nette_a"], g_res["van_nette_b"]],
        marker_color=[COLORS["red"] if g_res["winner"]=="B" else COLORS["teal"],
                      COLORS["teal"] if g_res["winner"]=="B" else COLORS["red"]],
        text=[fm(g_res["van_nette_a"]), fm(g_res["van_nette_b"])],
        textposition="outside", width=0.4,
    ))
    fig_final.update_layout(
        height=240, showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="M€", gridcolor="#e8e5de"),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_final, use_container_width=True)

    winner_name = ("B — Share deal + Fusion J+3" if g_res["winner"] == "B"
                   else "A — Asset deal J+0")
    v_kind = "ok"
    if g_res["winner"] == "B":
        v_text = (f"<b>Recommandation : Scénario {winner_name}.</b> "
                  f"L'économie DMTO initiale (<b>{fm(g_res['econ_dmto'])}</b>) combinée au step-up différé "
                  f"génère une VAN nette supérieure de <b>{fm(abs(g_res['diff']))}</b>. "
                  f"Condition nécessaire : un délai de 3 ans opérationnellement acceptable "
                  f"et une substance économique documentée pour écarter le risque d'abus de droit.")
    else:
        v_text = (f"<b>Recommandation : Scénario {winner_name}.</b> "
                  f"Le surcoût DMTO (<b>{fm(g_res['dmto_a'])}</b>) est compensé par le step-up immédiat "
                  f"et la base amortissable pleine dès J+0. VAN supérieure de <b>{fm(abs(g_res['diff']))}</b>. "
                  f"Particulièrement pertinent sur actifs à fort bâti (terrain "
                  f"{fp(ter*100)}) ou lorsque le délai de 3 ans est opérationnellement contraignant.")
    verdict(v_text, v_kind)

    disc("VAN calculée sur la durée d'amortissement complète. "
         "Scénario A : DMTO élevés mais step-up immédiat, base amortissable pleine dès J+0, "
         "sans délai ni risque abus de droit. "
         "Scénario B : économie DMTO initiale, 3 ans sans step-up (coût du délai intégré), "
         "puis réintégration terrain sur 5 ans actualisée à J+0. "
         "Modèle indicatif — l'arbitrage réel dépend de la structure de financement, "
         "de la capacité opérationnelle à gérer le délai et de l'avis d'un conseil fiscal qualifié.")

    st.markdown("---")
    st.markdown(
        '<div class="disc">⚠️ <b>FiscHôtel Advisor™</b> est un outil de diagnostic prévisionnel. '
        'Les résultats sont indicatifs et ne constituent pas un conseil juridique ou fiscal. '
        'Toute décision structurelle doit être validée par un avocat fiscaliste spécialisé en droit immobilier. '
        '© REIV Hospitality</div>',
        unsafe_allow_html=True
    )
