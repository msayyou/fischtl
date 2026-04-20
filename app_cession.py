# ─────────────────────────────────────────────────────────────────────────────
#  FiscHôtel Advisor™ — MODULE CESSION
#  Outil de diagnostic fiscal orienté cédant
#  REIV Hospitality · Mehdi SAYYOU
# ─────────────────────────────────────────────────────────────────────────────

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="FiscHôtel Advisor™ — Cession",
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
.fh-brand em { color:#0d7a5f; font-style:italic; }
.fh-sub { font-family:'DM Mono',monospace; font-size:11px; color:#9a9a96;
          letter-spacing:.06em; margin-bottom:18px; }
.fh-mode { display:inline-block; background:#fef3e0; color:#7a4500;
           border:1px solid #f5c875; border-radius:6px; font-size:11px;
           font-weight:600; padding:3px 10px; letter-spacing:.04em;
           margin-bottom:16px; }

/* KPI cards */
.kpi { background:#f3f1ec; border-radius:10px; padding:14px 18px; margin-bottom:8px; }
.kpi.green { background:#e0f2ec; border-left:3px solid #0d7a5f; }
.kpi.amber { background:#fef3e0; border-left:3px solid #b06a00; }
.kpi.red   { background:#fdeaea; border-left:3px solid #b32b2b; }
.kpi.blue  { background:#e8eef9; border-left:3px solid #1a4fa0; }
.kpi.ink   { background:#0f0f0e; border-left:3px solid #0d7a5f; }
.kpi-lbl { font-size:11px; color:#6b6b68; font-weight:600;
           letter-spacing:.06em; text-transform:uppercase; }
.kpi-val { font-family:'DM Mono',monospace; font-size:24px;
           font-weight:600; color:#0f0f0e; margin:3px 0; }
.kpi.ink .kpi-lbl { color:#9a9a96; }
.kpi.ink .kpi-val { color:#faf9f6; }
.kpi.ink .kpi-sub { color:#6b6b68; }
.kpi-sub { font-size:11px; color:#9a9a96; }

/* Big hero number */
.hero { text-align:center; padding:28px 20px 20px; }
.hero-lbl { font-size:12px; color:#6b6b68; font-weight:600;
            letter-spacing:.08em; text-transform:uppercase; margin-bottom:6px; }
.hero-val { font-family:'DM Serif Display',serif; font-size:52px; color:#0d7a5f;
            line-height:1; margin-bottom:6px; }
.hero-sub { font-size:13px; color:#9a9a96; }

/* Verdict */
.verdict { border-radius:8px; padding:14px 18px; font-size:13px;
           line-height:1.7; margin:12px 0; }
.verdict.ok   { background:#e0f2ec; border-left:4px solid #0d7a5f; color:#085041; }
.verdict.warn { background:#fef3e0; border-left:4px solid #b06a00; color:#7a4500; }
.verdict.bad  { background:#fdeaea; border-left:4px solid #b32b2b; color:#7a1a1a; }
.verdict.info { background:#e8eef9; border-left:4px solid #1a4fa0; color:#0c2d6b; }

/* Argument card */
.arg-card { border:1px solid #e8e5de; border-radius:10px; padding:16px 18px;
            margin-bottom:12px; background:#faf9f6; }
.arg-head { font-weight:600; font-size:13px; color:#0f0f0e; margin-bottom:6px; }
.arg-body { font-size:12.5px; color:#3a3a38; line-height:1.7; }
.arg-num  { font-family:'DM Mono',monospace; color:#0d7a5f; font-weight:600; }

/* Section titles */
.sec { font-family:'DM Serif Display',serif; font-size:17px; color:#0f0f0e;
       border-bottom:1px solid #e8e5de; padding-bottom:8px; margin:22px 0 14px; }
.sec-sub { font-size:11px; color:#9a9a96; font-style:italic; margin-bottom:14px; }

/* Disclaimer */
.disc { font-size:11px; color:#9a9a96; background:#f3f1ec; border-radius:6px;
        padding:10px 14px; line-height:1.6; margin-top:16px; }

/* Sidebar dark */
section[data-testid="stSidebar"] { background:#0f0f0e !important; }
section[data-testid="stSidebar"] * { color:#e8e5de !important; }
section[data-testid="stSidebar"] .stSlider > label { color:#9a9a96 !important; font-size:12px; }
section[data-testid="stSidebar"] hr { border-color:#2a2a28 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap:4px; background:#f3f1ec;
    border-radius:10px; padding:4px; }
.stTabs [data-baseweb="tab"] { border-radius:8px; font-weight:500;
    font-size:13px; padding:8px 16px; }
.stTabs [aria-selected="true"] { background:#0d7a5f !important; color:white !important; }

/* Divider */
.div { height:1px; background:#e8e5de; margin:16px 0; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MOTEUR DE CALCUL
# ══════════════════════════════════════════════════════════════════════════════

def pv_ann(flux: float, taux: float, n: int) -> float:
    if taux == 0 or n == 0:
        return flux * n
    return flux * (1 - (1 + taux) ** -n) / taux


def abatt_ir(duree: int) -> tuple[float, float]:
    if duree <= 5:
        return 0.0, 0.0
    ab_ir = min((duree - 5) * 6, 100.0) if duree < 22 else 100.0
    if duree <= 21:
        ab_ps = (duree - 5) * 1.65
    elif duree <= 29:
        ab_ps = (22 - 5) * 1.65 + (duree - 22) * 9.0
    else:
        ab_ps = 100.0
    return ab_ir, min(ab_ps, 100.0)


def surtaxe(pv_m: float) -> float:
    pv = pv_m * 1_000_000
    if pv <= 50_000:
        return 0.0
    tranches = [(50_000, 100_000, .02), (100_000, 150_000, .03),
                (150_000, 200_000, .04), (200_000, 250_000, .05),
                (250_000, float("inf"), .06)]
    t = 0.0
    for lo, hi, r in tranches:
        if pv > lo:
            t += (min(pv, hi) - lo) * r
    return t / 1_000_000


def calc_net_cedant_is(prix: float, vnc: float, amort: float, taux_is: float) -> dict:
    """Net cédant — structure IS (société à l'IS)."""
    vnc_net = vnc - amort
    pv_fisc = prix - vnc_net
    imp_is = max(0, pv_fisc) * taux_is
    base_div = max(0, pv_fisc - imp_is)
    imp_div = base_div * 0.30
    net = prix - imp_is - imp_div
    friction = (imp_is + imp_div) / prix if prix else 0
    return dict(vnc_net=vnc_net, pv_fisc=pv_fisc,
                imp_is=imp_is, imp_div=imp_div,
                net=net, friction=friction)


def calc_net_cedant_ir(prix: float, vnc: float, duree: int) -> dict:
    """Net cédant — régime IR (PV immobilière)."""
    pv_eco = prix - vnc
    ab_ir_pct, ab_ps_pct = abatt_ir(duree)
    pv_ir = max(0, pv_eco) * (1 - ab_ir_pct / 100)
    pv_ps = max(0, pv_eco) * (1 - ab_ps_pct / 100)
    imp_irpp = pv_ir * 0.19
    imp_ps = pv_ps * 0.172
    surt = surtaxe(pv_ir)
    tot = imp_irpp + imp_ps + surt
    net = prix - tot
    friction = tot / prix if prix else 0
    return dict(pv_eco=pv_eco, ab_ir_pct=ab_ir_pct, ab_ps_pct=ab_ps_pct,
                pv_ir=pv_ir, imp_irpp=imp_irpp, imp_ps=imp_ps,
                surt=surt, tot=tot, net=net, friction=friction)


def calc_deal(prix: float, vnc: float, amort: float, dette: float, fdc: float,
              typesoc: str, taux_is: float, dur: int, tact: float) -> dict:
    """Comparaison asset deal vs share deal."""
    prix_titres = prix - dette

    # Asset deal
    dmto_a = (prix + fdc) * 0.065
    pv_ced_a = prix + fdc - (vnc - amort)
    is_ced_a = max(0, pv_ced_a) * taux_is
    net_ced_a = prix + fdc - is_ced_a

    # Share deal
    if typesoc == "SARL":
        dmto_s = max(0, prix_titres - 0.023) * 0.03
    else:
        dmto_s = prix_titres * 0.001
    pv_ced_s = prix_titres - (vnc - amort)
    is_ced_s = max(0, pv_ced_s) * taux_is
    net_ced_s = prix_titres - is_ced_s

    # Valeur step-up pour l'acquéreur (VAN amort. supplémentaire)
    bati = prix * 0.80  # proxy 80% bati si non paramétré ici
    van_stepup_acq = pv_ann(bati / dur * taux_is, tact, dur)
    surprix_max = min(van_stepup_acq, dmto_a - dmto_s)

    return dict(
        prix_titres=prix_titres, dmto_a=dmto_a, dmto_s=dmto_s,
        net_ced_a=net_ced_a, net_ced_s=net_ced_s,
        is_ced_a=is_ced_a, is_ced_s=is_ced_s,
        econ_ced=net_ced_s - net_ced_a,
        econ_acq=dmto_a - dmto_s,
        van_stepup_acq=van_stepup_acq,
        surprix_max=max(0, surprix_max),
    )


def calc_stepup(prix: float, vnc: float, ter: float, dur: int,
                taux_is: float, tact: float) -> dict:
    """VAN du step-up pour l'acquéreur — argument de négociation du cédant."""
    terrain = prix * ter
    bati = prix * (1 - ter)
    vnc_bati = vnc * (1 - ter)
    vnc_terrain = vnc * ter

    base_avant = vnc_bati
    eco_avant = base_avant / dur * taux_is
    van_avant = pv_ann(eco_avant, tact, dur)

    base_apres = bati
    eco_apres = base_apres / dur * taux_is
    van_apres = pv_ann(eco_apres, tact, dur)

    gain_brut = van_apres - van_avant

    pv_lat = terrain - vnc_terrain
    is_reint_an = (pv_lat / 5) * taux_is
    cout_reint = pv_ann(is_reint_an, tact, 5)

    gain_net = gain_brut - cout_reint

    return dict(
        terrain=terrain, bati=bati,
        van_avant=van_avant, van_apres=van_apres,
        eco_avant=eco_avant, eco_apres=eco_apres,
        gain_brut=gain_brut, pv_lat=pv_lat,
        cout_reint=cout_reint, gain_net=gain_net,
        is_reint_an=is_reint_an,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS UI
# ══════════════════════════════════════════════════════════════════════════════

C = dict(teal="#0d7a5f", red="#b32b2b", amber="#b06a00",
         blue="#1a4fa0", gray="#9a9a96", ink="#0f0f0e")

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
        height=h, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(family="Instrument Sans", size=12, color="#3a3a38"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#e8e5de", gridwidth=0.5)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div class="fh-brand" style="font-size:20px">Fisc<em>Hôtel</em> Advisor™</div>
    <div class="fh-sub">MODULE CESSION · REIV HOSPITALITY</div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("**🏨 Actif hôtelier**")
    prix   = st.slider("Prix de cession cible (M€)", 1.0, 120.0, 20.0, 0.5,
                       help="Prix que vous envisagez de négocier")
    vnc    = st.slider("VNC bilan (M€)", 0.5, 60.0, 8.0, 0.5,
                       help="Valeur nette comptable de l'actif au bilan")
    amort  = st.slider("Amortissements cumulés (M€)", 0.0, 30.0, 3.0, 0.1,
                       help="Total des amortissements pratiqués depuis l'acquisition")
    ter    = st.slider("Part terrain (%)", 5, 55, 20, 1,
                       help="% de la valeur vénale représenté par le foncier") / 100
    dette  = st.slider("Dette résiduelle (M€)", 0.0, 80.0, 8.0, 0.5,
                       help="Dette financière nette dans la structure à la date de cession")
    fdc    = st.slider("Goodwill / fonds de commerce (M€)", 0.0, 20.0, 2.0, 0.5,
                       help="Valeur du fonds de commerce / marque négociée en supplément")
    dur    = st.slider("Durée amortissement restante (ans)", 10, 50, 25, 5)

    st.markdown("---")
    st.markdown("**⚖️ Profil fiscal cédant**")
    regime   = st.selectbox("Régime fiscal de la structure",
                            ["Société à l'IS", "SCI / Détention IR", "LMNP / BIC"],
                            help="Régime fiscal de la structure cédante")
    taux_is  = st.select_slider("Taux IS (%)", [15, 25], 25) / 100
    tmi      = st.slider("TMI IR cédant (%)", 11, 45, 41, 1,
                         help="Tranche marginale d'imposition du cédant personne physique") / 100
    duree_det = st.slider("Durée de détention (ans)", 1, 35, 10, 1,
                          help="Depuis l'acquisition initiale de l'actif")
    typesoc  = st.selectbox("Type de société cédée",
                            ["SARL", "SAS / SA"],
                            help="Détermine le taux de droits de cession de titres")
    tact     = st.slider("Taux d'actualisation (%)", 4.0, 12.0, 7.0, 0.5) / 100

    st.markdown("---")
    # Synthèse sidebar
    pv_eco = prix - vnc
    equity = prix - dette
    ab_ir_s, ab_ps_s = abatt_ir(duree_det)
    st.markdown(f"""
**Synthèse**
- Equity value : **{fm(equity)}**
- PV économique : **{fm(pv_eco)}**
- Abatt. IR / PS : **{ab_ir_s:.0f}% / {ab_ps_s:.0f}%** ({duree_det} ans)
- Terrain / Bâti : **{fm(prix*ter)} / {fm(prix*(1-ter))}**
    """)


# ══════════════════════════════════════════════════════════════════════════════
#  CALCULS CENTRAUX
# ══════════════════════════════════════════════════════════════════════════════

r_is  = calc_net_cedant_is(prix, vnc, amort, taux_is)
r_ir  = calc_net_cedant_ir(prix, vnc, duree_det)
r_deal = calc_deal(prix, vnc, amort, dette, fdc, typesoc, taux_is, dur, tact)
r_su   = calc_stepup(prix, vnc, ter, dur, taux_is, tact)

# Net cédant selon le régime sélectionné
if regime == "Société à l'IS":
    net_principal = r_is["net"]
    friction_principale = r_is["friction"]
    regime_label = "IS"
else:
    net_principal = r_ir["net"]
    friction_principale = r_ir["friction"]
    regime_label = "IR"


# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("""
<div class="fh-brand">Fisc<em>Hôtel</em> Advisor™</div>
<div class="fh-sub">DIAGNOSTIC FISCAL DE CESSION · REIV HOSPITALITY</div>
""", unsafe_allow_html=True)
st.markdown('<div class="fh-mode">⚡ MODE CESSION</div>', unsafe_allow_html=True)

# ── Hero metrics ──
col1, col2, col3, col4 = st.columns(4)
with col1:
    kpi("Prix de cession cible", fm(prix), "Prix négocié", "ink")
with col2:
    kpi("Net cédant estimé", fm(net_principal),
        f"Régime {regime_label} · Friction {fp(friction_principale*100)}",
        "green")
with col3:
    kpi("PV économique", fm(pv_eco),
        f"vs VNC {fm(vnc)}", "blue" if pv_eco > 0 else "red")
with col4:
    kpi("Equity value", fm(equity),
        f"Prix − Dette {fm(dette)}", "")


# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════

t1, t2, t3, t4 = st.tabs([
    "💰 Net cédant & sensibilité prix",
    "⚖️ IS vs IR — Optimisation structure",
    "🤝 Asset deal vs Share deal",
    "🧠 Stratégie de négociation",
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — NET CÉDANT & SENSIBILITÉ PRIX
# ══════════════════════════════════════════════════════════════════════════════

with t1:
    sec("Net cédant simulé — votre encaissement réel selon le prix",
        f"Régime fiscal : {regime} · Durée détention : {duree_det} ans")

    # Courbe net cédant en fonction du prix
    prix_range = np.linspace(max(1, prix * 0.6), prix * 1.4, 80)
    net_is_curve, net_ir_curve = [], []
    for p_test in prix_range:
        ri = calc_net_cedant_is(p_test, vnc, amort, taux_is)
        rr = calc_net_cedant_ir(p_test, vnc, duree_det)
        net_is_curve.append(ri["net"])
        net_ir_curve.append(rr["net"])

    fig_sens = go.Figure()
    fig_sens.add_trace(go.Scatter(
        x=list(prix_range), y=net_is_curve, name="Net cédant IS",
        line=dict(color=C["red"], width=2),
        fill="tozeroy", fillcolor="rgba(179,43,43,0.05)",
    ))
    fig_sens.add_trace(go.Scatter(
        x=list(prix_range), y=net_ir_curve, name="Net cédant IR",
        line=dict(color=C["teal"], width=2, dash="dot"),
        fill="tozeroy", fillcolor="rgba(13,122,95,0.05)",
    ))
    fig_sens.add_vline(x=prix, line_dash="dash", line_color=C["amber"], line_width=1.5,
                       annotation_text=f"Prix cible {fm(prix)}",
                       annotation_position="top left",
                       annotation_font_color=C["amber"])
    fig_sens.add_scatter(x=[prix], y=[r_is["net"]], mode="markers",
                         marker=dict(color=C["red"], size=10), showlegend=False)
    fig_sens.add_scatter(x=[prix], y=[r_ir["net"]], mode="markers",
                         marker=dict(color=C["teal"], size=10), showlegend=False)
    fig_sens.update_layout(
        height=320, legend=dict(orientation="h", y=1.08),
        xaxis=dict(title="Prix de cession (M€)"),
        yaxis=dict(title="Net cédant (M€)", gridcolor="#e8e5de"),
    )
    plotly_base(fig_sens, h=320)
    st.plotly_chart(fig_sens, use_container_width=True)

    sec("Décomposition de la friction fiscale au prix cible")
    col_is, col_ir = st.columns(2)

    with col_is:
        st.markdown("**Structure IS**")
        df_is = pd.DataFrame([
            ("Prix de cession",           fm(prix)),
            ("VNC après amortissements",  fm(r_is["vnc_net"])),
            ("PV fiscale IS",             fm(r_is["pv_fisc"])),
            ("IS 25% sur PV",            f"− {fm(r_is['imp_is'])}"),
            ("PFU 30% sur dividende",    f"− {fm(r_is['imp_div'])}"),
            ("Friction totale",           fp(r_is["friction"] * 100)),
            ("NET ENCAISSÉ",              fm(r_is["net"])),
        ], columns=["Poste", "Montant"])
        st.dataframe(df_is, hide_index=True, use_container_width=True)

    with col_ir:
        st.markdown(f"**Régime IR ({duree_det} ans détention)**")
        rows_ir = [
            ("Prix de cession",           fm(prix)),
            ("PV économique",             fm(r_ir["pv_eco"])),
            (f"Abatt. IR {r_ir['ab_ir_pct']:.0f}%",
             fm(r_ir["pv_eco"] * r_ir["ab_ir_pct"] / 100)),
            ("IRPP 19%",                 f"− {fm(r_ir['imp_irpp'])}"),
            ("PS 17,2%",                 f"− {fm(r_ir['imp_ps'])}"),
        ]
        if r_ir["surt"] > 0:
            rows_ir.append(("Surtaxe PV", f"− {fm(r_ir['surt'])}"))
        rows_ir += [
            ("Friction totale",           fp(r_ir["friction"] * 100)),
            ("NET ENCAISSÉ",              fm(r_ir["net"])),
        ]
        df_ir = pd.DataFrame(rows_ir, columns=["Poste", "Montant"])
        st.dataframe(df_ir, hide_index=True, use_container_width=True)

    sec("Impact du prix sur le net cédant — table de sensibilité")
    steps = [-20, -15, -10, -5, 0, +5, +10, +15, +20]
    sens_rows = []
    for delta_pct in steps:
        p_t = prix * (1 + delta_pct / 100)
        ri = calc_net_cedant_is(p_t, vnc, amort, taux_is)
        rr = calc_net_cedant_ir(p_t, vnc, duree_det)
        sens_rows.append({
            "Δ prix": f"{delta_pct:+d}%",
            "Prix (M€)": f"{p_t:.2f}",
            "Net IS (M€)": f"{ri['net']:.2f}",
            "Friction IS": fp(ri["friction"] * 100),
            "Net IR (M€)": f"{rr['net']:.2f}",
            "Friction IR": fp(rr["friction"] * 100),
            "Écart IS−IR (M€)": f"{ri['net'] - rr['net']:+.2f}",
        })
    df_sens = pd.DataFrame(sens_rows)
    # Highlight current price row
    st.dataframe(df_sens, hide_index=True, use_container_width=True)

    winner = "IS" if r_is["net"] > r_ir["net"] else "IR"
    ecart = abs(r_is["net"] - r_ir["net"])
    v_kind = "ok" if winner == regime_label else "warn"
    verdict(
        f"<b>Au prix cible de {fm(prix)}</b>, votre structure actuelle ({regime}) "
        f"génère un net de <b>{fm(net_principal)}</b> (friction {fp(friction_principale*100)}). "
        f"Le régime {winner} est théoriquement plus favorable de <b>{fm(ecart)}</b>. "
        + ("Votre structure est optimale." if winner == regime_label
           else f"Une restructuration avant cession mérite d'être étudiée."),
        v_kind,
    )

    disc("Net cédant IS : IS 25% sur PV vs VNC nette + PFU 30% sur dividende résiduel. "
         "Net cédant IR : 19% IRPP + 17,2% PS avec abattements durée + surtaxe si PV > 50 k€. "
         "Calculs indicatifs — hors situations spécifiques (mère-fille, SIIC, niches sectorielles).")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — IS vs IR OPTIMISATION
# ══════════════════════════════════════════════════════════════════════════════

with t2:
    sec("Optimisation de structure avant cession — IS vs IR",
        "Quel régime fiscal maximise votre encaissement net ?")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("Net cédant IS", fm(r_is["net"]),
            f"Friction {fp(r_is['friction']*100)}",
            "green" if r_is["net"] > r_ir["net"] else "")
    with col2:
        kpi("Net cédant IR", fm(r_ir["net"]),
            f"Friction {fp(r_ir['friction']*100)} · Abatt. IR {r_ir['ab_ir_pct']:.0f}%",
            "green" if r_ir["net"] > r_is["net"] else "")
    with col3:
        gagnant = "IS" if r_is["net"] > r_ir["net"] else "IR"
        kpi("Régime optimal", gagnant,
            f"Avantage {fm(abs(r_is['net'] - r_ir['net']))}",
            "blue")

    # Waterfall IS
    sec("Décomposition cascade — Structure IS")
    fig_wf_is = go.Figure(go.Waterfall(
        orientation="v",
        x=["Prix cession", "IS sur PV", "PFU dividende", "Net cédant"],
        y=[prix, -r_is["imp_is"], -r_is["imp_div"],
           r_is["net"] - prix + r_is["imp_is"] + r_is["imp_div"]],
        measure=["absolute", "relative", "relative", "total"],
        connector=dict(line=dict(color="#e8e5de")),
        decreasing=dict(marker_color=C["red"]),
        increasing=dict(marker_color=C["teal"]),
        totals=dict(marker_color=C["blue"]),
        text=[fm(prix), f"−{fm(r_is['imp_is'])}", f"−{fm(r_is['imp_div'])}", fm(r_is["net"])],
        textposition="outside",
    ))
    plotly_base(fig_wf_is, h=280)
    st.plotly_chart(fig_wf_is, use_container_width=True)

    # Courbe abattements et point de bascule
    sec("Point de bascule IS / IR selon la durée de détention")
    dur_range = list(range(1, 36))
    net_is_dur = [calc_net_cedant_is(prix, vnc, amort, taux_is)["net"]] * len(dur_range)
    net_ir_dur = [calc_net_cedant_ir(prix, vnc, d)["net"] for d in dur_range]

    # Find crossover
    crossover = None
    for i in range(len(dur_range) - 1):
        if (net_ir_dur[i] - net_is_dur[i]) * (net_ir_dur[i+1] - net_is_dur[i+1]) <= 0:
            crossover = dur_range[i]
            break

    fig_bascule = go.Figure()
    fig_bascule.add_trace(go.Scatter(
        x=dur_range, y=net_is_dur, name="Net IS (constant)",
        line=dict(color=C["red"], width=2, dash="dot"),
    ))
    fig_bascule.add_trace(go.Scatter(
        x=dur_range, y=net_ir_dur, name="Net IR (progressif)",
        line=dict(color=C["teal"], width=2),
        fill="tonexty", fillcolor="rgba(13,122,95,0.06)",
    ))
    fig_bascule.add_vline(x=duree_det, line_color=C["amber"], line_dash="dash",
                          annotation_text=f"Votre détention ({duree_det} ans)",
                          annotation_font_color=C["amber"])
    if crossover:
        fig_bascule.add_vline(x=crossover, line_color=C["blue"], line_dash="dot",
                              annotation_text=f"Bascule IR > IS ({crossover} ans)",
                              annotation_position="top right",
                              annotation_font_color=C["blue"])
    fig_bascule.update_layout(
        xaxis=dict(title="Durée de détention (ans)"),
        yaxis=dict(title="Net cédant (M€)", gridcolor="#e8e5de"),
        legend=dict(orientation="h", y=1.08),
    )
    plotly_base(fig_bascule, h=300)
    st.plotly_chart(fig_bascule, use_container_width=True)

    # Conseil restructuration
    sec("Fenêtre de restructuration avant cession")
    col_a, col_b = st.columns(2)
    with col_a:
        arg_card(
            "Option 1 — Passage SCI IR → IS avant cession",
            f"Si votre structure est actuellement à l'IR et que la détention est courte "
            f"({duree_det} ans, abatt. {r_ir['ab_ir_pct']:.0f}%), le passage à l'IS avant "
            f"cession n'est pas recommandé : il génère une double friction immédiate. "
            f"Maintenir le régime IR jusqu'à la cession."
        )
    with col_b:
        arg_card(
            "Option 2 — Apport-cession (art. 150-0 B ter CGI)",
            f"Si la structure est à l'IR et la PV économique est significative "
            f"({fm(pv_eco)}), l'apport des titres à une holding IS suivi de la cession "
            f"peut permettre un report d'imposition. Conditions strictes (réemploi 60%). "
            f"Délai de mise en œuvre : 6–12 mois minimum."
        )

    gagnant_long = "IS" if r_is["net"] > r_ir["net"] else "IR"
    ecart_regimes = abs(r_is["net"] - r_ir["net"])
    if gagnant_long == regime_label:
        verdict(
            f"<b>Votre structure actuelle ({regime}) est cohérente avec l'optimum fiscal.</b> "
            f"Le régime {gagnant_long} est supérieur de <b>{fm(ecart_regimes)}</b> à ce prix et à cette durée. "
            f"Aucune restructuration urgente nécessaire avant la cession.",
            "ok"
        )
    else:
        verdict(
            f"<b>Écart structurel identifié.</b> Le régime {gagnant_long} serait supérieur de "
            f"<b>{fm(ecart_regimes)}</b>. Votre structure actuelle ({regime}) n'est pas optimale "
            f"à ce prix ({fm(prix)}) et cette durée ({duree_det} ans). "
            f"Une consultation fiscale spécialisée est recommandée avant d'engager la cession.",
            "warn"
        )

    disc("Le passage d'un régime à l'autre avant cession peut générer des frictions fiscales "
         "intermédiaires. Art. 150-0 B ter CGI (apport-cession) : report conditionné au réemploi "
         "de 60% du produit dans les 2 ans. Délai minimum de mise en œuvre : 6 à 12 mois. "
         "Consulter un avocat fiscaliste avant toute restructuration.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — ASSET vs SHARE DEAL
# ══════════════════════════════════════════════════════════════════════════════

with t3:
    d = r_deal
    sec("Asset deal vs Share deal — Impact sur votre net cédant",
        f"Prix cible {fm(prix)} · Equity {fm(d['prix_titres'])} · Dette {fm(dette)}")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi("Net cédant — Asset deal", fm(d["net_ced_a"]),
            f"IS {fm(d['is_ced_a'])} · Prix {fm(prix + fdc)}",
            "green" if d["net_ced_a"] > d["net_ced_s"] else "")
    with col2:
        kpi("Net cédant — Share deal", fm(d["net_ced_s"]),
            f"IS {fm(d['is_ced_s'])} · Prix titres {fm(d['prix_titres'])}",
            "green" if d["net_ced_s"] > d["net_ced_a"] else "")
    with col3:
        fav = "Asset" if d["net_ced_a"] > d["net_ced_s"] else "Share"
        kpi("Préférence cédant", f"{fav} deal",
            f"Écart {fm(abs(d['econ_ced']))}",
            "blue")

    sec("Comparaison détaillée")
    df_comp = pd.DataFrame([
        ("Prix brut reçu",
         fm(prix + fdc), fm(d["prix_titres"])),
        ("IS sur plus-value",
         f"− {fm(d['is_ced_a'])}", f"− {fm(d['is_ced_s'])}"),
        ("Dette restante dans structure",
         "0 (remboursée)", f"+ {fm(dette)} (reste dans sté)"),
        ("DMTO à la charge acquéreur",
         fm(d["dmto_a"]), fm(d["dmto_s"])),
        ("NET CÉDANT",
         fm(d["net_ced_a"]), fm(d["net_ced_s"])),
    ], columns=["Poste", "Asset deal", "Share deal"])
    st.dataframe(df_comp, hide_index=True, use_container_width=True)

    # Visual comparison
    fig_deal = go.Figure()
    categories = ["Net cédant — Asset", "Net cédant — Share"]
    values = [d["net_ced_a"], d["net_ced_s"]]
    colors = [C["teal"] if d["net_ced_a"] >= d["net_ced_s"] else C["red"],
              C["teal"] if d["net_ced_s"] > d["net_ced_a"] else C["red"]]
    fig_deal.add_trace(go.Bar(
        x=categories, y=values, marker_color=colors,
        text=[fm(v) for v in values], textposition="outside", width=0.35,
    ))
    plotly_base(fig_deal, h=240)
    fig_deal.update_layout(showlegend=False,
                           yaxis=dict(title="M€", gridcolor="#e8e5de"))
    st.plotly_chart(fig_deal, use_container_width=True)

    sec("Levier de négociation — Valeur du step-up pour l'acquéreur")
    st.markdown(f"""
    En **share deal**, l'acquéreur ne bénéficie pas du step-up fiscal immédiat.
    Voici ce que vaut le step-up pour lui — c'est le montant qu'il peut **vous payer en supplément**
    pour que vous acceptiez un asset deal.
    """)

    su = r_su
    col_su1, col_su2 = st.columns(2)
    with col_su1:
        kpi("VAN step-up brut (acquéreur)", fm(su["gain_brut"]),
            f"Suramortissement bâti sur {dur} ans", "blue")
    with col_su2:
        kpi("Coût réintégration terrain (acquéreur)", fm(su["cout_reint"]),
            f"PV latente terrain {fm(su['pv_lat'])} × 1/5 × 5 ans", "amber")

    kpi("Surprix maximum justifiable (acquéreur)", fm(d["surprix_max"]),
        "Ce qu'il peut offrir au-delà du prix share deal pour que l'asset deal soit équivalent",
        "green")

    if d["econ_ced"] > 0:
        v_text = (
            f"<b>Vous préférez le share deal</b> (écart +{fm(d['econ_ced'])}). "
            f"L'acquéreur, lui, préfère l'asset deal pour le step-up. "
            f"Sa capacité à vous surpayer est estimée à <b>{fm(d['surprix_max'])}</b>. "
            f"Tactique recommandée : proposer un prix asset deal de "
            f"<b>{fm(d['prix_titres'] + d['surprix_max'])}</b> (+{fm(d['surprix_max'])} vs share deal) "
            f"pour capturer une partie de la valeur fiscale acquéreur."
        )
        verdict(v_text, "ok")
    else:
        v_text = (
            f"<b>L'asset deal est légèrement plus favorable pour vous</b> (écart {fm(abs(d['econ_ced']))}). "
            f"Vous avez intérêt à orienter la négociation vers un asset deal "
            f"et argumenter avec la valeur step-up acquéreur ({fm(su['gain_brut'])}) "
            f"pour justifier votre prix."
        )
        verdict(v_text, "info")

    disc(f"Asset deal : DMTO ≈ 6,5% sur valeur immeuble + goodwill, à la charge de l'acquéreur. "
         f"Share deal SARL : 3% sur prix des parts (abatt. 23 k€). SAS/SA : 0,1%. "
         f"En share deal, la dette reste dans la structure — le prix des titres est donc l'equity value, "
         f"pas la valeur brute de l'actif.")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — STRATÉGIE DE NÉGOCIATION
# ══════════════════════════════════════════════════════════════════════════════

with t4:
    sec("Stratégie de négociation — Arguments fiscaux à votre disposition",
        "Dossier de négociation orienté cédant · Construire votre position de prix")

    # Score global
    score = 0
    score_detail = []
    if pv_eco > 0:
        score += 1
        score_detail.append("PV économique positive — valeur créée documentable")
    if r_su["gain_net"] > 0:
        score += 1
        score_detail.append(f"Step-up favorable pour l'acquéreur ({fm(r_su['gain_net'])} VAN nette)")
    if d["econ_acq"] > 0:
        score += 1
        score_detail.append(f"Économie DMTO share deal ({fm(d['econ_acq'])}) — levier de prix")
    if r_ir["ab_ir_pct"] >= 60:
        score += 1
        score_detail.append(f"Abattements IR significatifs ({r_ir['ab_ir_pct']:.0f}%) — flexibilité de structure")

    col_score, col_prix = st.columns([1, 2])
    with col_score:
        color_score = "green" if score >= 3 else "amber" if score == 2 else "red"
        kpi("Score position cédant", f"{score}/4 leviers",
            " · ".join(score_detail[:2]), color_score)
    with col_prix:
        prix_plancher_is = r_is["net"] / (1 - r_is["friction"])
        prix_cible_asset = d["prix_titres"] + d["surprix_max"]
        kpi("Fourchette de prix recommandée",
            f"{fm(d['prix_titres'])} → {fm(prix_cible_asset)}",
            f"Share deal plancher → Asset deal cible (+{fm(d['surprix_max'])} step-up)",
            "blue")

    sec("Arguments à présenter à l'acquéreur")

    arg_card(
        f"Argument 1 — Valeur du step-up : {fm(r_su['gain_net'])} de VAN pour l'acquéreur",
        f"En acceptant un <b>asset deal</b>, l'acquéreur bénéficie d'un step-up immédiat "
        f"sur la base amortissable (de <b>{fm(r_su['van_avant'])}</b> à <b>{fm(r_su['van_apres'])}</b> de VAN). "
        f"Gain net après réintégration terrain : <b class='arg-num'>{fm(r_su['gain_net'])}</b>. "
        f"Cet avantage justifie un prix asset deal supérieur de "
        f"<b class='arg-num'>{fm(d['surprix_max'])}</b> au share deal."
    )

    arg_card(
        f"Argument 2 — Économie DMTO en share deal : {fm(d['econ_acq'])}",
        f"Le share deal économise à l'acquéreur <b class='arg-num'>{fm(d['econ_acq'])}</b> de droits de mutation "
        f"({'3% parts SARL' if typesoc == 'SARL' else '0,1% titres SAS'} vs 6,5% asset deal). "
        f"Cette économie peut être partagée : vous récupérez une partie sous forme de prix "
        f"de cession plus élevé, et l'acquéreur garde le solde. "
        f"Proposition : prix share deal majoré de <b class='arg-num'>{fm(d['econ_acq'] * 0.5)}</b> "
        f"(50% de l'économie DMTO)."
    )

    arg_card(
        f"Argument 3 — PV économique documentée : {fm(pv_eco)}",
        f"La valeur vénale de <b>{fm(prix)}</b> représente une création de valeur de "
        f"<b class='arg-num'>{fm(pv_eco)}</b> vs le bilan ({fm(vnc)}). "
        f"Cette plus-value est justifiable par : (1) la valorisation par les revenus "
        f"(EBITDA × multiple sectoriel), (2) la valeur de remplacement des constructions, "
        f"(3) la rareté de l'actif sur le marché local. "
        f"Terrain : <b>{fm(prix * ter)}</b> · Bâti : <b>{fm(prix * (1 - ter))}</b>."
    )

    if r_ir["ab_ir_pct"] > 0:
        arg_card(
            f"Argument 4 — Flexibilité structurelle : abattement {r_ir['ab_ir_pct']:.0f}% IR disponible",
            f"Votre durée de détention ({duree_det} ans) vous ouvre un abattement IR de "
            f"<b class='arg-num'>{r_ir['ab_ir_pct']:.0f}%</b> ({r_ir['ab_ps_pct']:.0f}% PS). "
            f"Vous pouvez accepter une légère décote de prix en échange d'une structure "
            f"share deal avec paiement différé / earn-out, sans dégradation significative "
            f"de votre net fiscal."
        )

    sec("Tableau de bord de négociation — Votre position vs acquéreur")

    # Zone de négociation visuelle
    fig_neg = go.Figure()

    scenarios = [
        ("Share deal\n(plancher cédant)", d["net_ced_s"], C["teal"]),
        ("Asset deal\n(prix actuel)", d["net_ced_a"], C["blue"]),
        ("Asset deal\n(+ step-up capturé)", d["net_ced_a"] + d["surprix_max"] * (1 - r_is["friction"]),
         C["amber"]),
    ]
    for label, val, color in scenarios:
        fig_neg.add_trace(go.Bar(
            x=[label], y=[val], marker_color=color,
            text=[fm(val)], textposition="outside", width=0.4,
        ))
    plotly_base(fig_neg, h=280)
    fig_neg.update_layout(showlegend=False,
                          yaxis=dict(title="Net cédant (M€)", gridcolor="#e8e5de"),
                          title="Net cédant selon la structure et le niveau de prix")
    st.plotly_chart(fig_neg, use_container_width=True)

    sec("Recommandation finale")
    if d["net_ced_s"] > d["net_ced_a"] and r_su["gain_net"] > 0:
        verdict(
            f"<b>Position recommandée : Share deal de base + argument step-up pour majorer le prix.</b> "
            f"Proposez un share deal à <b>{fm(d['prix_titres'])}</b> (votre intérêt naturel), "
            f"puis utilisez la valeur step-up acquéreur (<b>{fm(r_su['gain_net'])}</b>) "
            f"pour justifier un prix asset deal majoré de <b>{fm(d['surprix_max'])}</b>. "
            f"Cela vous permet soit de pousser le share deal à un prix plus élevé, "
            f"soit d'accepter l'asset deal en étant compensé pour votre friction IS supplémentaire.",
            "ok"
        )
    elif d["net_ced_a"] >= d["net_ced_s"]:
        verdict(
            f"<b>L'asset deal vous est légèrement favorable dans ce scénario.</b> "
            f"Orientez la négociation vers un asset deal et utilisez les arguments step-up "
            f"pour justifier votre prix de <b>{fm(prix + fdc)}</b> (immeuble + goodwill). "
            f"L'acquéreur économise {fm(r_su['gain_net'])} en VAN fiscale — "
            f"c'est votre principal levier.",
            "info"
        )
    else:
        verdict(
            f"<b>Position complexe — score {score}/4.</b> "
            f"Les leviers fiscaux sont limités dans cette configuration. "
            f"Concentrez la négociation sur la valeur opérationnelle de l'actif "
            f"(EBITDA, positionnement marché, perspectives RevPAR) "
            f"plutôt que sur les arguments fiscaux.",
            "warn"
        )

    st.markdown("---")
    disc(
        "⚠️ FiscHôtel Advisor™ est un outil de diagnostic fiscal prévisionnel à usage professionnel. "
        "Les résultats sont indicatifs et ne constituent pas un conseil juridique ou fiscal. "
        "Toute décision de cession doit être précédée d'un audit fiscal complet et validée par un "
        "avocat fiscaliste spécialisé en droit immobilier. © REIV Hospitality · Mehdi SAYYOU"
    )
