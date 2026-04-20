# ─────────────────────────────────────────────────────────────────────────────
#  FiscHôtel Advisor™ — MODULE ACQUISITION
#  Outil de diagnostic fiscal orienté acquéreur
#  REIV Hospitality · Mehdi SAYYOU
#
#  Question centrale : quel est le coût fiscal réel de cette acquisition,
#  quelle structure optimise mon rendement net, et quel prix puis-je justifier ?
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="FiscHôtel Advisor™ — Acquisition",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Instrument Sans', sans-serif; }

.fh-brand { font-family:'DM Serif Display',serif; font-size:26px;
            letter-spacing:-.5px; color:#0f0f0e; margin-bottom:2px; }
.fh-brand em { color:#1a4fa0; font-style:italic; }
.fh-sub  { font-family:'DM Mono',monospace; font-size:11px; color:#9a9a96;
           letter-spacing:.06em; margin-bottom:18px; }
.fh-mode { display:inline-block; background:#e8eef9; color:#0c2d6b;
           border:1px solid #b5d4f4; border-radius:6px; font-size:11px;
           font-weight:600; padding:3px 10px; letter-spacing:.04em;
           margin-bottom:16px; }

.kpi { background:#f3f1ec; border-radius:10px; padding:14px 18px; margin-bottom:8px; }
.kpi.green { background:#e0f2ec; border-left:3px solid #0d7a5f; }
.kpi.amber { background:#fef3e0; border-left:3px solid #b06a00; }
.kpi.red   { background:#fdeaea; border-left:3px solid #b32b2b; }
.kpi.blue  { background:#e8eef9; border-left:3px solid #1a4fa0; }
.kpi.ink   { background:#0f0f0e; border-left:3px solid #1a4fa0; }
.kpi-lbl { font-size:11px; color:#6b6b68; font-weight:600;
           letter-spacing:.06em; text-transform:uppercase; }
.kpi-val { font-family:'DM Mono',monospace; font-size:22px;
           font-weight:600; color:#0f0f0e; margin:3px 0; }
.kpi.ink .kpi-lbl { color:#9a9a96; }
.kpi.ink .kpi-val { color:#faf9f6; }
.kpi.ink .kpi-sub { color:#6b6b68; }
.kpi-sub { font-size:11px; color:#9a9a96; }

.verdict { border-radius:8px; padding:14px 18px; font-size:13px;
           line-height:1.7; margin:12px 0; }
.verdict.ok   { background:#e0f2ec; border-left:4px solid #0d7a5f; color:#085041; }
.verdict.warn { background:#fef3e0; border-left:4px solid #b06a00; color:#7a4500; }
.verdict.bad  { background:#fdeaea; border-left:4px solid #b32b2b; color:#7a1a1a; }
.verdict.info { background:#e8eef9; border-left:4px solid #1a4fa0; color:#0c2d6b; }

.arg-card { border:1px solid #e8e5de; border-radius:10px; padding:16px 18px;
            margin-bottom:12px; background:#faf9f6; }
.arg-head { font-weight:600; font-size:13px; color:#0f0f0e; margin-bottom:6px; }
.arg-body { font-size:12.5px; color:#3a3a38; line-height:1.7; }
.arg-num  { font-family:'DM Mono',monospace; color:#1a4fa0; font-weight:600; }
.arg-good { color:#0d7a5f; font-weight:600; }
.arg-bad  { color:#b32b2b; font-weight:600; }

.sec { font-family:'DM Serif Display',serif; font-size:17px; color:#0f0f0e;
       border-bottom:1px solid #e8e5de; padding-bottom:8px; margin:22px 0 14px; }
.sec-sub { font-size:11px; color:#9a9a96; font-style:italic; margin-bottom:14px; }
.disc { font-size:11px; color:#9a9a96; background:#f3f1ec; border-radius:6px;
        padding:10px 14px; line-height:1.6; margin-top:16px; }

section[data-testid="stSidebar"] { background:#0a1628 !important; }
section[data-testid="stSidebar"] * { color:#e8eef9 !important; }
section[data-testid="stSidebar"] .stSlider > label { color:#8ba4cc !important; font-size:12px; }
section[data-testid="stSidebar"] hr { border-color:#1a2d4a !important; }

.stTabs [data-baseweb="tab-list"] { gap:4px; background:#f3f1ec;
    border-radius:10px; padding:4px; }
.stTabs [data-baseweb="tab"] { border-radius:8px; font-weight:500;
    font-size:13px; padding:8px 16px; }
.stTabs [aria-selected="true"] { background:#1a4fa0 !important; color:white !important; }

table { width:100%; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MOTEUR DE CALCUL
# ══════════════════════════════════════════════════════════════════════════════

def pv_ann(flux: float, taux: float, n: int) -> float:
    """Valeur actuelle nette d'annuités constantes."""
    if taux == 0 or n == 0:
        return flux * n
    return flux * (1 - (1 + taux) ** -n) / taux


def calc_cout_acquisition(prix: float, dette: float, fdc: float,
                           typesoc: str, ter: float) -> dict:
    """
    Coût total d'entrée selon la structure choisie.
    Acquéreur : combien ça coûte réellement pour prendre le contrôle ?
    """
    equity = prix - dette          # prix des titres (share deal)
    bati   = prix * (1 - ter)

    # ── Asset deal ──────────────────────────────────────────────────────────
    dmto_a      = (prix + fdc) * 0.065          # ≈ 6,5% droits + notaire
    cout_total_a = prix + fdc + dmto_a           # ce que sort l'acquéreur
    base_amort_a = bati + fdc                    # base amortissable dans le bilan

    # ── Share deal ──────────────────────────────────────────────────────────
    if typesoc == "SARL":
        dmto_s = max(0.0, equity - 0.023) * 0.03
    else:
        dmto_s = equity * 0.001
    cout_total_s = equity + dette + dmto_s       # équivalent au cout actif
    base_amort_s = 0.0                           # pas de step-up immédiat

    econ_dmto    = dmto_a - dmto_s               # économie droits en share deal
    surcout_step = 0.0                           # valorisé dans le module step-up

    return dict(
        equity=equity, bati=bati,
        dmto_a=dmto_a, cout_total_a=cout_total_a, base_amort_a=base_amort_a,
        dmto_s=dmto_s, cout_total_s=cout_total_s, base_amort_s=base_amort_s,
        econ_dmto=econ_dmto,
    )


def calc_rendement(prix: float, dette: float, fdc: float, ter: float,
                   dur: int, taux_is: float, tact: float,
                   loyer_ann: float, vacance: float,
                   structure: str) -> dict:
    """
    Rendement locatif net après IS sur la durée de détention.
    Prend en compte l'amortissement selon structure (asset vs share).
    """
    bati          = prix * (1 - ter)
    base_amort    = (bati + fdc) if structure == "asset" else bati * 0.40  # VNC proxy share
    amort_ann     = base_amort / dur

    revenus_nets  = loyer_ann * (1 - vacance / 100)
    resultat_av_amort = revenus_nets - (prix * 0.015)     # charges foncières proxy 1,5%
    resultat_fisc = max(0.0, resultat_av_amort - amort_ann)
    is_ann        = resultat_fisc * taux_is
    caf_ann       = revenus_nets - (prix * 0.015) - is_ann

    van_caf       = pv_ann(caf_ann, tact, dur)
    rendement_brut = loyer_ann / (prix + fdc) * 100
    rendement_net  = caf_ann   / (prix + fdc) * 100

    return dict(
        base_amort=base_amort, amort_ann=amort_ann,
        revenus_nets=revenus_nets, resultat_fisc=resultat_fisc,
        is_ann=is_ann, caf_ann=caf_ann, van_caf=van_caf,
        rendement_brut=rendement_brut, rendement_net=rendement_net,
    )


def calc_stepup(prix: float, vnc_ced: float, ter: float,
                dur: int, taux_is: float, tact: float,
                delai_fusion: int = 3) -> dict:
    """
    Step-up par fusion-absorption post share deal.
    Acquéreur : quel est le gain VAN du step-up, net du coût terrain et du délai ?
    """
    terrain   = prix * ter
    bati      = prix * (1 - ter)
    vnc_bati  = vnc_ced * (1 - ter)
    vnc_terr  = vnc_ced * ter

    # Sans fusion : amort sur VNC bâti
    eco_avant  = (vnc_bati / dur) * taux_is
    van_avant  = pv_ann(eco_avant, tact, dur)

    # Avec fusion (step-up) : amort sur valeur vénale bâti
    eco_apres  = (bati / dur) * taux_is
    van_apres  = pv_ann(eco_apres, tact, dur)

    gain_brut  = van_apres - van_avant

    # Coût réintégration terrain (art. 210 A al. 3)
    pv_lat     = max(0.0, terrain - vnc_terr)
    is_reint   = (pv_lat / 5) * taux_is
    cout_reint = pv_ann(is_reint, tact, 5)

    # Coût du délai : manque à amortir pendant les `delai_fusion` ans
    eco_perdue_an = eco_apres - eco_avant           # gain annuel après step-up
    cout_delai    = pv_ann(eco_perdue_an, tact, delai_fusion)  # VAN des annuités perdues

    gain_net    = gain_brut - cout_reint
    gain_net_av_delai = gain_net - cout_delai       # net du délai d'attente

    # Calendrier réintégration
    calendrier = []
    for i in range(1, 6):
        act = is_reint / (1 + tact) ** i
        calendrier.append({
            "Année": f"J+{delai_fusion + i}",
            "PV réintégrée (k€)": round(pv_lat / 5 * 1000, 1),
            "IS dû (k€)": round(is_reint * 1000, 1),
            "IS actualisé (k€)": round(act * 1000, 1),
        })

    return dict(
        terrain=terrain, bati=bati, vnc_bati=vnc_bati, pv_lat=pv_lat,
        eco_avant=eco_avant, eco_apres=eco_apres,
        van_avant=van_avant, van_apres=van_apres,
        gain_brut=gain_brut, cout_reint=cout_reint,
        cout_delai=cout_delai, gain_net=gain_net,
        gain_net_av_delai=gain_net_av_delai,
        is_reint=is_reint, calendrier=calendrier,
    )


def calc_global_jplus(cout: dict, su: dict, tact: float,
                      dur: int, taux_is: float,
                      delai_fusion: int = 3) -> dict:
    """
    Arbitrage J+0 (asset deal) vs J+3 (share deal + fusion).
    Acquéreur : quelle route maximise la VAN de l'investissement ?
    """
    fact_act = (1 + tact) ** delai_fusion

    # Scénario A — Asset deal J+0
    # Step-up immédiat, DMTO élevés
    van_amort_a = pv_ann(su["eco_apres"], tact, dur)
    van_nette_a = van_amort_a - cout["dmto_a"]

    # Scénario B — Share deal + fusion J+3
    # Phase 1 : amort VNC pendant 3 ans
    van_p1 = pv_ann(su["eco_avant"], tact, delai_fusion)
    # Phase 2 : step-up actif, sur (dur - delai) ans, actualisé à J+0
    van_p2 = pv_ann(su["eco_apres"], tact, dur - delai_fusion) / fact_act
    # Coût réintégration terrain actualisé à J+0
    cout_reint_j0 = su["cout_reint"] / fact_act
    van_nette_b   = van_p1 + van_p2 - cout_reint_j0 - cout["dmto_s"]

    diff    = van_nette_b - van_nette_a      # positif = B meilleur
    winner  = "B" if diff > 0 else "A"

    # Courbe d'accumulation VAN cumulée sur le temps
    annees   = list(range(0, dur + 1))
    cum_a, cum_b = [-cout["dmto_a"]], [-cout["dmto_s"]]
    for i in range(dur):
        eco_a = su["eco_apres"] / (1 + tact) ** (i + 1)
        cum_a.append(cum_a[-1] + eco_a)

        if i < delai_fusion:
            eco_b = su["eco_avant"] / (1 + tact) ** (i + 1)
        else:
            eco_b = su["eco_apres"] / (1 + tact) ** (i + 1)
            yr_reint = i - delai_fusion + 1
            if 1 <= yr_reint <= 5:
                eco_b -= su["is_reint"] / (1 + tact) ** (i + 1)
        cum_b.append(cum_b[-1] + eco_b)

    return dict(
        van_nette_a=van_nette_a, van_nette_b=van_nette_b,
        diff=diff, winner=winner,
        van_p1=van_p1, van_p2=van_p2,
        cout_reint_j0=cout_reint_j0,
        van_amort_a=van_amort_a,
        annees=annees, cum_a=cum_a, cum_b=cum_b,
    )


def calc_prix_max(cout: dict, su: dict, glob: dict,
                  tact: float, dur: int) -> dict:
    """
    Prix maximum justifiable par l'acquéreur selon la structure.
    Approche : le prix est justifié si la VAN des économies IS couvre le coût d'entrée.
    """
    # Prix max asset deal : VAN amort / (1 + taux_droits)
    # On cherche le prix P tel que van_amort(P) >= cout_entree(P)
    # Approximation : prix max = VAN amort brute / (1 + 0.065)
    prix_max_asset = glob["van_amort_a"] / 0.065 if glob["van_amort_a"] > 0 else 0

    # Prix max share deal : VAN nette B
    surprix_step = max(0.0, su["gain_net"])     # VAN gain step-up = surprix justifiable

    return dict(
        surprix_step=surprix_step,
            prix_max_asset=prix_max_asset,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS UI
# ══════════════════════════════════════════════════════════════════════════════

C = dict(blue="#1a4fa0", teal="#0d7a5f", red="#b32b2b",
         amber="#b06a00", gray="#9a9a96", ink="#0f0f0e")

def fm(v: float, d: int = 2) -> str:
    return f"{v:,.{d}f} M€".replace(",", "\u202f")

def fk(v: float) -> str:
    return f"{v * 1000:,.0f} k€".replace(",", "\u202f")

def fp(v: float, d: int = 1) -> str:
    return f"{v:.{d}f}%"

def kpi(label, value, sub="", color=""):
    st.markdown(f"""<div class="kpi {color}">
        <div class="kpi-lbl">{label}</div>
        <div class="kpi-val">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

def verdict(text, kind="ok"):
    st.markdown(f'<div class="verdict {kind}">{text}</div>', unsafe_allow_html=True)

def sec(title, sub=""):
    st.markdown(f'<div class="sec">{title}</div>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<div class="sec-sub">{sub}</div>', unsafe_allow_html=True)

def disc(text):
    st.markdown(f'<div class="disc">{text}</div>', unsafe_allow_html=True)

def arg_card(head, body):
    st.markdown(f"""<div class="arg-card">
        <div class="arg-head">{head}</div>
        <div class="arg-body">{body}</div>
    </div>""", unsafe_allow_html=True)

def plotly_base(fig, h=260):
    fig.update_layout(
        height=h,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=24, b=10),
        font=dict(family="Instrument Sans", size=12, color="#3a3a38"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e8e5de", gridwidth=0.5)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR — PARAMÈTRES
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="fh-brand" style="font-size:20px">Fisc<em>Hôtel</em> Advisor™</div>
    <div class="fh-sub">MODULE ACQUISITION · REIV HOSPITALITY</div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**🏨 Actif cible**")
    prix    = st.slider("Prix demandé par le cédant (M€)", 1.0, 120.0, 20.0, 0.5,
                        help="Prix de cession affiché ou négocié avec le cédant")
    vnc_ced = st.slider("VNC bilan cédant (M€)",           0.5,  60.0,  8.0, 0.5,
                        help="Valeur nette comptable au bilan de la société cédante")
    ter     = st.slider("Part terrain (%)",                  5,    55,   20,   1,
                        help="Part foncière dans la valeur vénale totale") / 100
    dette   = st.slider("Dette dans la structure (M€)",     0.0,  80.0,  8.0, 0.5,
                        help="Dette financière nette reprise avec la société")
    fdc     = st.slider("Goodwill / fonds de commerce (M€)", 0.0, 20.0,  2.0, 0.5,
                        help="Valeur du fonds demandée en supplément (asset deal)")
    dur     = st.slider("Durée d'amortissement (ans)",      10,   50,   25,    5)
    delai   = st.slider("Délai avant fusion TUP (ans)",      2,    5,    3,    1,
                        help="Délai entre l'acquisition share deal et la fusion (min. 3 ans recommandé)")

    st.markdown("---")
    st.markdown("**⚙️ Paramètres fiscaux acquéreur**")
    taux_is  = st.select_slider("Taux IS holding (%)",   [15, 25], 25) / 100
    tact     = st.slider("Taux d'actualisation (%)",      4.0, 12.0, 7.0, 0.5) / 100
    typesoc  = st.selectbox("Type société cédée",        ["SARL", "SAS / SA"])

    st.markdown("---")
    st.markdown("**🏦 Revenus locatifs attendus**")
    loyer    = st.slider("Loyer annuel attendu (M€)",     0.1,   5.0,  1.0, 0.05,
                         help="Loyer annuel brut hors charges (bail commercial)")
    vacance  = st.slider("Taux de vacance (%)",            0,    20,    5,   1,
                         help="Taux de vacance / impayés estimé")

    st.markdown("---")
    equity = prix - dette
    st.markdown(f"""
**Synthèse cible**
- Equity value : **{fm(equity)}**
- Bâti / Terrain : **{fm(prix*(1-ter))} / {fm(prix*ter)}**
- PV latente cédant : **{fm(prix - vnc_ced)}**
- Rendement brut : **{fp(loyer / (prix + fdc) * 100)}**
    """)


# ══════════════════════════════════════════════════════════════════════════════
#  CALCULS CENTRAUX
# ══════════════════════════════════════════════════════════════════════════════

r_cout  = calc_cout_acquisition(prix, dette, fdc, typesoc, ter)
r_rend_a = calc_rendement(prix, dette, fdc, ter, dur, taux_is, tact,
                           loyer, vacance, "asset")
r_rend_s = calc_rendement(prix, dette, fdc, ter, dur, taux_is, tact,
                           loyer, vacance, "share")
r_su    = calc_stepup(prix, vnc_ced, ter, dur, taux_is, tact, delai)
r_glob  = calc_global_jplus(r_cout, r_su, tact, dur, taux_is, delai)
r_prix  = calc_prix_max(r_cout, r_su, r_glob, tact, dur)


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="fh-brand">Fisc<em>Hôtel</em> Advisor™</div>
<div class="fh-sub">DIAGNOSTIC FISCAL D'ACQUISITION · REIV HOSPITALITY</div>
""", unsafe_allow_html=True)
st.markdown('<div class="fh-mode">🔵 MODE ACQUISITION</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi("Prix demandé", fm(prix), "Prix cédant affiché", "ink")
with col2:
    kpi("Coût total — Asset deal", fm(r_cout["cout_total_a"]),
        f"dont DMTO {fm(r_cout['dmto_a'])}", "red")
with col3:
    kpi("Coût total — Share deal", fm(r_cout["cout_total_s"]),
        f"dont droits {fm(r_cout['dmto_s'])}", "blue")
with col4:
    kpi("Gain step-up (VAN nette)", fm(r_su["gain_net"]),
        f"Après réintégration terrain", "green" if r_su["gain_net"] > 0 else "amber")


# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════

t1, t2, t3, t4 = st.tabs([
    "💸 Coût réel d'entrée",
    "📈 Rendement & base amortissable",
    "🔼 Step-up fiscal — Fusion J+" + str(delai),
    "⚖️ Arbitrage global J+0 / J+" + str(delai),
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — COÛT RÉEL D'ENTRÉE
# ══════════════════════════════════════════════════════════════════════════════

with t1:
    sec("Coût total d'entrée selon la structure",
        "Ce que vous sortez réellement pour prendre le contrôle de l'actif")

    col_a, col_s = st.columns(2)
    with col_a:
        kpi("Asset deal — Coût total", fm(r_cout["cout_total_a"]),
            f"Prix {fm(prix + fdc)} + DMTO {fm(r_cout['dmto_a'])}", "red")
        df_a = pd.DataFrame([
            ("Prix immeuble + goodwill",   fm(prix + fdc)),
            ("DMTO ≈ 6,5%",              f"+ {fm(r_cout['dmto_a'])}"),
            ("Reprise dette",              "0 (refinancement)"),
            ("Base amortissable obtenue",  fm(r_cout["base_amort_a"])),
            ("COÛT TOTAL",                 fm(r_cout["cout_total_a"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_a, hide_index=True, use_container_width=True)

    with col_s:
        kpi("Share deal — Coût total", fm(r_cout["cout_total_s"]),
            f"Equity {fm(r_cout['equity'])} + dette {fm(dette)} + droits {fm(r_cout['dmto_s'])}",
            "blue")
        df_s = pd.DataFrame([
            ("Prix des titres (equity)",       fm(r_cout["equity"])),
            (f"Droits cession ({'3% SARL' if typesoc == 'SARL' else '0,1% SAS'})",
             f"+ {fm(r_cout['dmto_s'])}"),
            ("Reprise dette dans structure",  f"+ {fm(dette)}"),
            ("Base amortissable obtenue",      "0 (sans fusion)"),
            ("COÛT TOTAL",                     fm(r_cout["cout_total_s"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_s, hide_index=True, use_container_width=True)

    sec("Sensibilité du coût d'entrée au prix")
    prix_range  = np.linspace(max(1, prix * 0.7), prix * 1.3, 60)
    cout_a_curve, cout_s_curve = [], []
    for p in prix_range:
        c = calc_cout_acquisition(p, dette, fdc, typesoc, ter)
        cout_a_curve.append(c["cout_total_a"])
        cout_s_curve.append(c["cout_total_s"])

    fig_sens = go.Figure()
    fig_sens.add_trace(go.Scatter(
        x=list(prix_range), y=cout_a_curve, name="Coût asset deal",
        line=dict(color=C["red"], width=2),
    ))
    fig_sens.add_trace(go.Scatter(
        x=list(prix_range), y=cout_s_curve, name="Coût share deal",
        line=dict(color=C["blue"], width=2, dash="dot"),
        fill="tonexty", fillcolor="rgba(26,79,160,0.06)",
    ))
    fig_sens.add_vline(x=prix, line_dash="dash", line_color=C["amber"], line_width=1.5,
                       annotation_text=f"Prix actuel {fm(prix)}",
                       annotation_font_color=C["amber"])
    fig_sens.update_layout(
        xaxis=dict(title="Prix demandé (M€)"),
        yaxis=dict(title="Coût total acquéreur (M€)", gridcolor="#e8e5de"),
        legend=dict(orientation="h", y=1.08),
    )
    plotly_base(fig_sens, h=300)
    st.plotly_chart(fig_sens, use_container_width=True)

    sec("Décomposition du surcoût asset deal vs share deal")
    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        x=["Coût share deal", "Surcoût DMTO", "Base amort. gagnée (VAN IS)", "Net écart"],
        y=[r_cout["cout_total_s"],
           r_cout["dmto_a"] - r_cout["dmto_s"],
           -r_su["gain_brut"],
           0],
        measure=["absolute", "relative", "relative", "total"],
        connector=dict(line=dict(color="#e8e5de")),
        decreasing=dict(marker_color=C["teal"]),
        increasing=dict(marker_color=C["red"]),
        totals=dict(marker_color=C["blue"]),
        text=[fm(r_cout["cout_total_s"]),
              f"+{fm(r_cout['dmto_a']-r_cout['dmto_s'])}",
              f"−{fm(r_su['gain_brut'])}",
              fm(r_cout["cout_total_s"] + r_cout["dmto_a"] - r_cout["dmto_s"] - r_su["gain_brut"])],
        textposition="outside",
    ))
    plotly_base(fig_wf, h=280)
    st.plotly_chart(fig_wf, use_container_width=True)

    econ = r_cout["econ_dmto"]
    if econ > 0:
        verdict(
            f"<b>Le share deal économise {fm(econ)} de droits d'entrée.</b> "
            f"Mais sans step-up immédiat, vous perdez la base amortissable ({fm(r_cout['base_amort_a'])}). "
            f"La VAN des économies IS manquées est de <b>{fm(r_su['gain_brut'])}</b>. "
            f"Le share deal n'est favorable que si vous planifiez la fusion dans {delai} ans "
            f"(gain step-up net : <b>{fm(r_su['gain_net'])}</b>).",
            "warn"
        )
    else:
        verdict(
            f"<b>L'asset deal est structurellement préférable dans ce scénario.</b> "
            f"Le différentiel de droits est faible ({fm(abs(econ))}) et la base amortissable "
            f"({fm(r_cout['base_amort_a'])}) génère une VAN IS de <b>{fm(r_su['van_apres'])}</b>.",
            "ok"
        )

    disc("DMTO asset deal : 5,80% droits d'enregistrement + 0,80% émoluments notaire ≈ 6,5% sur prix. "
         "Share deal SARL : 3% sur prix des parts (abattement 23 k€). SAS/SA : 0,1% plat. "
         "En share deal, la dette dans la structure fait partie du coût économique total "
         "même si elle n'est pas payée directement à l'acquisition.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — RENDEMENT & BASE AMORTISSABLE
# ══════════════════════════════════════════════════════════════════════════════

with t2:
    sec("Rendement locatif net IS — Asset deal vs Share deal",
        f"Loyer attendu {fm(loyer)} · Vacance {vacance}% · IS {int(taux_is*100)}%")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("Rendement brut", fp(r_rend_a["rendement_brut"]),
            f"Loyer / (prix + goodwill)", "")
    with col2:
        kpi("Rendement net IS — Asset", fp(r_rend_a["rendement_net"]),
            f"CAF annuelle {fk(r_rend_a['caf_ann'])}", "green")
    with col3:
        kpi("Rendement net IS — Share", fp(r_rend_s["rendement_net"]),
            f"CAF annuelle {fk(r_rend_s['caf_ann'])}", "blue")

    sec("Impact de l'amortissement sur le résultat fiscal annuel")
    df_rend = pd.DataFrame([
        ("Revenus locatifs bruts",       fm(loyer),                    fm(loyer)),
        (f"Vacance {vacance}%",
         f"− {fm(loyer * vacance / 100)}", f"− {fm(loyer * vacance / 100)}"),
        ("Charges foncières (proxy 1,5%)", f"− {fm(prix * 0.015)}",   f"− {fm(prix * 0.015)}"),
        ("Amortissement annuel",
         f"− {fk(r_rend_a['amort_ann'])} (base {fm(r_cout['base_amort_a'])})",
         f"− {fk(r_rend_s['amort_ann'])} (base VNC)"),
        ("Résultat fiscal IS",           fm(r_rend_a["resultat_fisc"]), fm(r_rend_s["resultat_fisc"])),
        ("IS annuel",                   f"− {fk(r_rend_a['is_ann'])}", f"− {fk(r_rend_s['is_ann'])}"),
        ("CAF nette IS",                 fk(r_rend_a["caf_ann"]),      fk(r_rend_s["caf_ann"])),
        ("VAN CAF sur durée",            fm(r_rend_a["van_caf"]),       fm(r_rend_s["van_caf"])),
    ], columns=["Poste", "Asset deal", "Share deal"])
    st.dataframe(df_rend, hide_index=True, use_container_width=True)

    sec("Base amortissable : impact cumulé sur le résultat fiscal")
    annees = list(range(1, dur + 1))
    cumul_a = [r_rend_a["amort_ann"] * i for i in annees]
    cumul_s = [r_rend_s["amort_ann"] * i for i in annees]
    econ_is_cumul_a = [x * taux_is for x in cumul_a]
    econ_is_cumul_s = [x * taux_is for x in cumul_s]

    fig_amort = go.Figure()
    fig_amort.add_trace(go.Scatter(
        x=annees, y=econ_is_cumul_a, name="Éco. IS cumulée — Asset deal",
        line=dict(color=C["teal"], width=2),
        fill="tozeroy", fillcolor="rgba(13,122,95,0.07)",
    ))
    fig_amort.add_trace(go.Scatter(
        x=annees, y=econ_is_cumul_s, name="Éco. IS cumulée — Share deal (sans step-up)",
        line=dict(color=C["blue"], width=1.5, dash="dot"),
        fill="tozeroy", fillcolor="rgba(26,79,160,0.04)",
    ))
    ecart_final = econ_is_cumul_a[-1] - econ_is_cumul_s[-1]
    fig_amort.add_annotation(
        x=dur, y=econ_is_cumul_a[-1],
        text=f"Écart {fm(ecart_final)}",
        showarrow=True, arrowhead=2,
        font=dict(color=C["teal"], size=11),
    )
    fig_amort.update_layout(
        xaxis=dict(title="Années"),
        yaxis=dict(title="Économie IS cumulée (M€)", gridcolor="#e8e5de"),
        legend=dict(orientation="h", y=1.08),
    )
    plotly_base(fig_amort, h=300)
    st.plotly_chart(fig_amort, use_container_width=True)

    gain_rend = r_rend_a["van_caf"] - r_rend_s["van_caf"]
    verdict(
        f"<b>L'asset deal génère {fm(gain_rend)} de VAN CAF supplémentaire</b> "
        f"grâce à la base amortissable plus élevée "
        f"({fm(r_cout['base_amort_a'])} vs {fm(r_rend_s['base_amort'])} en share deal). "
        f"Cette différence représente la valeur fiscale de l'amortissement sur {dur} ans "
        f"que vous perdez en restant en share deal sans step-up.",
        "ok" if gain_rend > 0 else "warn",
    )

    disc("Base amortissable asset deal : bâti + goodwill (valeur vénale complète). "
         "Base amortissable share deal sans fusion : VNC héritée de la société cédante (~40% proxy). "
         "Charges foncières proxy à 1,5% du prix : à affiner selon l'actif (taxe foncière, assurances, GER). "
         "Le loyer et la vacance sont des hypothèses à valider par due diligence locative.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — STEP-UP
# ══════════════════════════════════════════════════════════════════════════════

with t3:
    su = r_su
    sec(f"Step-up fiscal — Fusion-absorption à J+{delai} (art. 210 A CGI)",
        "Transformer votre share deal en base amortissable pleine, avec neutralité IS")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("Gain step-up brut (VAN)", fm(su["gain_brut"]),
            f"Suramortissement bâti sur {dur} ans", "green")
    with col2:
        kpi("Coût réintégration terrain", fm(su["cout_reint"]),
            f"PV latente {fm(su['pv_lat'])} — IS 1/5 × 5 ans", "amber")
    with col3:
        kpi("Gain net step-up", fm(su["gain_net"]),
            f"Après terrain · Avant coût délai",
            "green" if su["gain_net"] > 0 else "red")

    kpi("Gain net après coût du délai ({} ans sans step-up)".format(delai),
        fm(su["gain_net_av_delai"]),
        f"Coût délai {fm(su['cout_delai'])} — gain économies IS manquées pendant {delai} ans",
        "green" if su["gain_net_av_delai"] > 0 else "red")

    sec("Comparaison base amortissable — Avant / Après fusion")
    col_av, col_ap = st.columns(2)
    with col_av:
        st.markdown(f"**Sans fusion — J+0 à J+{delai}**")
        df_av = pd.DataFrame([
            ("Base amortissable (VNC bâti cédant)",  fm(su["vnc_bati"])),
            ("Amortissement annuel",                  fk(su["eco_avant"] / taux_is)),
            ("Économie IS annuelle",                  fk(su["eco_avant"])),
            (f"VAN éco. IS ({dur} ans)",              fm(su["van_avant"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_av, hide_index=True, use_container_width=True)

    with col_ap:
        st.markdown(f"**Après fusion step-up — J+{delai}**")
        df_ap = pd.DataFrame([
            ("Base amortissable (valeur vénale bâti)", fm(su["bati"])),
            ("Amortissement annuel",                    fk(su["eco_apres"] / taux_is)),
            ("Économie IS annuelle",                    fk(su["eco_apres"])),
            (f"VAN éco. IS ({dur} ans)",                fm(su["van_apres"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_ap, hide_index=True, use_container_width=True)

    sec(f"Calendrier de réintégration terrain — à partir de J+{delai}")
    df_cal = pd.DataFrame(su["calendrier"])
    st.dataframe(df_cal, hide_index=True, use_container_width=True)

    sec("VAN comparée — Gain step-up vs coûts")
    cats   = ["Gain step-up brut", "Coût terrain", "Coût délai", "Gain net final"]
    vals   = [su["gain_brut"], su["cout_reint"], su["cout_delai"], su["gain_net_av_delai"]]
    colors = [C["teal"], C["red"], C["amber"],
              C["blue"] if su["gain_net_av_delai"] > 0 else C["red"]]
    fig_su = go.Figure()
    for cat, val, col in zip(cats, vals, colors):
        fig_su.add_trace(go.Bar(
            x=[cat], y=[abs(val)], marker_color=col,
            text=[("− " if cat != "Gain step-up brut" and cat != "Gain net final" else "") + fm(val)],
            textposition="outside", width=0.4,
        ))
    plotly_base(fig_su, h=260)
    fig_su.update_layout(showlegend=False,
                         yaxis=dict(title="M€", gridcolor="#e8e5de"))
    st.plotly_chart(fig_su, use_container_width=True)

    cond_ok = su["gain_net_av_delai"] > 0
    if cond_ok:
        verdict(
            f"<b>Step-up favorable même après coût du délai.</b> "
            f"Gain net final <b>{fm(su['gain_net_av_delai'])}</b>. "
            f"Vous avez intérêt à planifier la fusion dès J+{delai} "
            f"pour déclencher le step-up et activer la base amortissable complète ({fm(su['bati'])}). "
            f"Pensez à documenter la substance économique de la période d'attente.",
            "ok"
        )
    else:
        verdict(
            f"<b>Step-up peu convaincant dans cette configuration.</b> "
            f"La part terrain élevée ({fp(ter*100)}) génère un coût de réintégration "
            f"({fm(su['cout_reint'])}) qui, combiné au coût du délai ({fm(su['cout_delai'])}), "
            f"dépasse le gain amortissement bâti. "
            f"Envisager un asset deal direct à J+0 pour éviter ces frictions.",
            "bad"
        )

    disc(f"Art. 210 A CGI : neutralité IS sur la PV de fusion. "
         f"Terrain non amortissable : PV latente réintégrée 1/5 par an sur 5 ans. "
         f"Délai {delai} ans entre share deal et fusion (risque abus de droit art. L64 LPF). "
         f"Le coût du délai représente la VAN des économies IS manquées pendant les {delai} ans "
         f"d'attente avant que le step-up soit activé.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — ARBITRAGE GLOBAL J+0 / J+N
# ══════════════════════════════════════════════════════════════════════════════

with t4:
    g = r_glob
    sec(f"Arbitrage global — Asset deal J+0 vs Share deal + Fusion J+{delai}",
        f"VAN comparée sur {dur} ans · Taux actualisation {fp(tact*100)} · Toutes frictions incluses")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("VAN nette — Scénario A (Asset J+0)",
            fm(g["van_nette_a"]), "Step-up immédiat, DMTO élevés",
            "green" if g["winner"] == "A" else "")
    with col2:
        kpi(f"VAN nette — Scénario B (Share + Fusion J+{delai})",
            fm(g["van_nette_b"]), "Économie DMTO, step-up différé",
            "green" if g["winner"] == "B" else "")
    with col3:
        kpi("Recommandation",
            f"Scénario {g['winner']}",
            f"Avantage {fm(abs(g['diff']))}",
            "blue")

    sec("Décomposition de la VAN par scénario")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Scénario A — Asset deal J+0**")
        df_ga = pd.DataFrame([
            ("DMTO acquisition",              f"− {fm(r_cout['dmto_a'])}"),
            (f"VAN éco. IS ({dur} ans)",      fm(g["van_amort_a"])),
            ("VAN nette",                     fm(g["van_nette_a"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_ga, hide_index=True, use_container_width=True)

    with col_b:
        st.markdown(f"**Scénario B — Share deal + Fusion J+{delai}**")
        df_gb = pd.DataFrame([
            ("Droits share deal",                      f"− {fm(r_cout['dmto_s'])}"),
            (f"VAN amort. phase 1 (J+0 à J+{delai})", fm(g["van_p1"])),
            (f"VAN amort. phase 2 (J+{delai}–{dur}, step-up)", fm(g["van_p2"])),
            ("Coût réintégration terrain (act. J+0)",  f"− {fm(g['cout_reint_j0'])}"),
            ("VAN nette",                              fm(g["van_nette_b"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_gb, hide_index=True, use_container_width=True)

    sec("Accumulation de VAN dans le temps")
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=g["annees"], y=g["cum_a"],
        name="Scénario A — Asset deal J+0",
        line=dict(color=C["red"], width=2.5),
        fill="tozeroy", fillcolor="rgba(179,43,43,0.05)",
    ))
    fig_cum.add_trace(go.Scatter(
        x=g["annees"], y=g["cum_b"],
        name=f"Scénario B — Share + Fusion J+{delai}",
        line=dict(color=C["blue"], width=2.5, dash="dot"),
        fill="tozeroy", fillcolor="rgba(26,79,160,0.05)",
    ))
    fig_cum.add_vline(x=delai, line_dash="dash", line_color=C["amber"],
                      annotation_text=f"Fusion J+{delai}",
                      annotation_font_color=C["amber"])
    fig_cum.add_vline(x=delai + 5, line_dash="dot", line_color=C["gray"],
                      annotation_text="Fin réintégration terrain",
                      annotation_font_color=C["gray"])
    fig_cum.add_hline(y=0, line_color="#e8e5de", line_width=1)

    # Crossover
    for i in range(len(g["annees"]) - 1):
        if (g["cum_a"][i] - g["cum_b"][i]) * (g["cum_a"][i+1] - g["cum_b"][i+1]) < 0:
            fig_cum.add_vline(x=g["annees"][i], line_dash="dot", line_color=C["teal"],
                              annotation_text=f"Break-even an {g['annees'][i]}",
                              annotation_position="bottom right",
                              annotation_font_color=C["teal"])
            break

    fig_cum.update_layout(
        xaxis=dict(title="Années depuis acquisition"),
        yaxis=dict(title="VAN cumulée (M€)", gridcolor="#e8e5de"),
        legend=dict(orientation="h", y=1.08),
    )
    plotly_base(fig_cum, h=340)
    st.plotly_chart(fig_cum, use_container_width=True)

    sec("Bilan de décision — Grille d'arbitrage acquéreur")
    arg_card(
        f"Privilégier l'asset deal (Scénario A) si…",
        f"· Le délai de {delai} ans avant fusion est opérationnellement contraignant<br>"
        f"· La part terrain est élevée (&gt;{fp(ter*100)}) — coût réintégration important<br>"
        f"· Vous avez besoin de la base amortissable maximale dès J+0 pour le financement<br>"
        f"· Le cédant est en IS et la structure juridique facilite l'asset deal<br>"
        f"· VAN A − VAN B = <span class='arg-num'>{fm(g['van_nette_a'] - g['van_nette_b'])}</span>"
    )
    arg_card(
        f"Privilégier le share deal + fusion (Scénario B) si…",
        f"· L'économie DMTO (<span class='arg-num'>{fm(r_cout['econ_dmto'])}</span>) est significative<br>"
        f"· Le délai de {delai} ans est gérable opérationnellement et juridiquement<br>"
        f"· La part terrain est faible (&lt;20%) — coût réintégration limité<br>"
        f"· La dette dans la structure est avantageuse à reprendre (taux fixe historique)<br>"
        f"· VAN B − VAN A = <span class='arg-num'>{fm(g['van_nette_b'] - g['van_nette_a'])}</span>"
    )

    winner_label = "A — Asset deal J+0" if g["winner"] == "A" else f"B — Share deal + Fusion J+{delai}"
    v_kind = "ok"
    if g["winner"] == "A":
        v_text = (
            f"<b>Recommandation : Scénario {winner_label}.</b> "
            f"Malgré des droits d'entrée plus élevés ({fm(r_cout['dmto_a'])}), "
            f"le step-up immédiat génère une VAN IS de <b>{fm(g['van_amort_a'])}</b> "
            f"sur {dur} ans, supérieure au scénario B de <b>{fm(abs(g['diff']))}</b>. "
            f"Priorité : négocier le prix à la baisse pour compenser le surcoût DMTO."
        )
    else:
        v_text = (
            f"<b>Recommandation : Scénario {winner_label}.</b> "
            f"L'économie DMTO ({fm(r_cout['econ_dmto'])}) et le step-up différé "
            f"génèrent une VAN nette supérieure de <b>{fm(abs(g['diff']))}</b>. "
            f"Condition critique : planifier et documenter la fusion dès J+{delai} "
            f"avec une substance économique établie pendant la période d'attente."
        )
    verdict(v_text, v_kind)

    st.markdown("---")
    disc(
        "⚠️ FiscHôtel Advisor™ est un outil de diagnostic fiscal prévisionnel à usage professionnel. "
        "Les résultats sont indicatifs et ne constituent pas un conseil juridique ou fiscal. "
        "La modélisation intègre les principaux paramètres fiscaux mais ne couvre pas les situations "
        "spécifiques (crédit-bail, régimes spéciaux, financement complexe). "
        "Toute structuration d'acquisition doit être validée par un avocat fiscaliste spécialisé. "
        "© REIV Hospitality · Mehdi SAYYOU"
    )
