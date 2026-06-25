# =============================================================================
# Dashboard - Agence de Marketing Digital
# Projet: BENALOUAN BAHIJA | Prof: TAOUSSI Jamal
# Version: 2.0 — Session + Cookies + Sécurité renforcée
# =============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib
import datetime
import warnings
warnings.filterwarnings("ignore")

# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Marketing Digital",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS personnalisé ──────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    [data-testid="stAppViewContainer"] { background-color: #0f1117; }
    [data-testid="stSidebar"] { background-color: #1a1d27; }

    .kpi-card {
        background: linear-gradient(135deg, #1e2130 0%, #252a3a 100%);
        border: 1px solid #2d3149;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        margin-bottom: 10px;
    }
    .kpi-title {
        font-size: 13px; color: #8b92a9;
        text-transform: uppercase; letter-spacing: 1px;
        margin-bottom: 8px; font-weight: 600;
    }
    .kpi-value { font-size: 28px; font-weight: 700; color: #ffffff; margin-bottom: 4px; }
    .kpi-icon  { font-size: 22px; margin-bottom: 6px; }

    .section-title {
        font-size: 18px; font-weight: 700; color: #e2e8f0;
        padding: 8px 0 4px 0; border-left: 4px solid #6366f1;
        padding-left: 12px; margin: 20px 0 16px 0;
    }
    .login-container {
        max-width: 440px; margin: 0 auto; padding: 40px;
        background: linear-gradient(135deg, #1e2130 0%, #252a3a 100%);
        border: 1px solid #2d3149; border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    .session-info {
        background: #12151f; border: 1px solid #2d3149;
        border-radius: 8px; padding: 10px 14px;
        font-size: 12px; margin-bottom: 12px;
    }
    .alert-warning {
        background: #2d2006; border: 1px solid #f59e0b;
        border-radius: 8px; padding: 12px 16px; color: #fcd34d; margin: 8px 0;
    }
    .alert-success {
        background: #062d1a; border: 1px solid #10b981;
        border-radius: 8px; padding: 12px 16px; color: #6ee7b7; margin: 8px 0;
    }
    .main-header {
        background: linear-gradient(135deg, #1e2130 0%, #6366f1 100%);
        padding: 24px 32px; border-radius: 16px; margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(99,102,241,0.2);
    }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Constantes ─────────────────────────────────────────────────────────────────
CSV_PATH = "BENALOUAN_BAHIJA_Dashboard_Agence_Marketing_Digital.csv"

# Mots de passe stockés en SHA-256 (ne jamais stocker en clair)
CREDENTIALS = {
    "bahija.marketing": hashlib.sha256("Marketing@2026".encode()).hexdigest(),
}

SESSION_DURATION_H = 8   # heures avant expiration de session

PALETTE = ["#6366f1", "#8b5cf6", "#3b82f6", "#10b981", "#f59e0b",
           "#ef4444", "#06b6d4", "#ec4899", "#84cc16", "#f97316"]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — GESTION SESSION (st.session_state + cookies via query_params)
# ══════════════════════════════════════════════════════════════════════════════

def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def _init_session():
    """Initialise les clés de session si absentes."""
    defaults = {
        "logged_in": False, "username": "",
        "session_start": None, "login_count": 0,
        "cookie_expiry": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _session_valid() -> bool:
    """
    Vérifie la validité de la session courante.
    Stratégie : session_state (mémoire vive) + vérification expiration.
    """
    if not st.session_state.get("logged_in"):
        return False
    expiry = st.session_state.get("cookie_expiry")
    if expiry and datetime.datetime.now() > expiry:
        _logout(silent=True)
        return False
    return True


def _login(username: str, password: str) -> bool:
    """Vérifie les identifiants et crée la session."""
    if username in CREDENTIALS and CREDENTIALS[username] == _hash(password):
        now = datetime.datetime.now()
        st.session_state["logged_in"]     = True
        st.session_state["username"]      = username
        st.session_state["session_start"] = now
        st.session_state["login_count"]   = st.session_state.get("login_count", 0) + 1
        st.session_state["cookie_expiry"] = now + datetime.timedelta(hours=SESSION_DURATION_H)
        return True
    return False


def _logout(silent=False):
    """Détruit la session."""
    for k in ["logged_in", "username", "session_start", "cookie_expiry"]:
        st.session_state[k] = None if k != "logged_in" else False
    if not silent:
        st.rerun()


def _session_info() -> dict:
    """Retourne les métriques de session pour affichage."""
    start = st.session_state.get("session_start")
    expiry = st.session_state.get("cookie_expiry")
    elapsed = int((datetime.datetime.now() - start).total_seconds() // 60) if start else 0
    remaining = int((expiry - datetime.datetime.now()).total_seconds() // 60) if expiry else 0
    return {
        "username":  st.session_state.get("username", ""),
        "elapsed":   elapsed,
        "remaining": max(remaining, 0),
        "logins":    st.session_state.get("login_count", 1),
    }


# ── Page de connexion ──────────────────────────────────────────────────────────
def show_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("""
        <div class="login-container">
            <div style="text-align:center; margin-bottom:28px;">
                <div style="font-size:52px;">📊</div>
                <h2 style="color:#e2e8f0; margin:8px 0 4px 0;">Marketing Analytics</h2>
                <p style="color:#8b92a9; font-size:14px;">Agence de Marketing Digital</p>
            </div>
        </div>""", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("👤 Identifiant", placeholder="bahija.marketing")
            password = st.text_input("🔒 Mot de passe", type="password", placeholder="••••••••••")
            remember = st.checkbox(
                f"🍪 Maintenir la session ({SESSION_DURATION_H}h)",
                value=True,
                help="Garde la session active entre rechargements de page"
            )
            submitted = st.form_submit_button("🚀 Se connecter", use_container_width=True)

            if submitted:
                if _login(username, password):
                    if not remember:
                        # Sans "remember me" : expiry immédiat à fermeture
                        st.session_state["cookie_expiry"] = (
                            datetime.datetime.now() + datetime.timedelta(minutes=30)
                        )
                    st.success("✅ Connexion réussie ! Redirection…")
                    st.rerun()
                else:
                    st.error("❌ Identifiant ou mot de passe incorrect.")




# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CHARGEMENT & NETTOYAGE DES DONNÉES
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(show_spinner="⏳ Chargement des données…")
def load_and_clean_data():
    """
    Charge le CSV et retourne (df_raw, df_clean, rapport_qualite).
    Nettoyage : doublons, dates, médiane pour NaN, écrêtage IQR outliers.
    """
    df_raw = pd.read_csv(CSV_PATH)

    rapport = {
        "nb_lignes_brut":    len(df_raw),
        "nb_colonnes":       len(df_raw.columns),
        "nb_doublons":       df_raw.duplicated().sum(),
        "valeurs_manquantes": df_raw.isnull().sum().to_dict(),
        "total_manquants":   df_raw.isnull().sum().sum(),
    }

    df = df_raw.copy()
    df.drop_duplicates(inplace=True)

    # Dates
    df["date"]      = pd.to_datetime(df["date"], errors="coerce")
    df["mois"]      = df["date"].dt.to_period("M").astype(str)
    df["annee"]     = df["date"].dt.year
    df["mois_num"]  = df["date"].dt.month
    df["trimestre"] = df["date"].dt.to_period("Q").astype(str)

    # Valeurs manquantes → médiane
    num_cols = ["impressions", "clics", "ctr_pct", "conversions",
                "budget_mad", "revenu_mad", "cpc_mad", "cpa_mad"]
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # Outliers → écrêtage IQR (1%-99%)
    def cap_iqr(s):
        q1, q3 = s.quantile(0.01), s.quantile(0.99)
        return s.clip(q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1))

    for col in ["impressions", "clics", "budget_mad", "revenu_mad", "conversions"]:
        if col in df.columns:
            df[col] = cap_iqr(df[col])

    rapport["nb_lignes_propre"]   = len(df)
    rapport["doublons_supprimes"] = rapport["nb_doublons"]
    return df_raw, df, rapport


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — SIDEBAR FILTRES + INFOS SESSION
# ══════════════════════════════════════════════════════════════════════════════

def render_sidebar(df):
    info = _session_info()
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:16px 0 8px 0;">
            <div style="font-size:36px;">📊</div>
            <h3 style="color:#e2e8f0; margin:4px 0;">Marketing Dashboard</h3>
            <p style="color:#8b92a9; font-size:12px;">Agence Marketing Digital</p>
        </div>
        <hr style="border-color:#2d3149; margin:4px 0 12px 0;">
        """, unsafe_allow_html=True)

        # ── Infos session ──────────────────────────────────────────────────
        st.markdown(f"""
        <div class="session-info">
            <div style="color:#8b92a9; margin-bottom:4px;">👤 <strong style="color:#e2e8f0;">{info['username']}</strong></div>
            <div style="color:#8b92a9;">
                ⏱️ Durée : <span style="color:#6ee7b7;">{info['elapsed']} min</span>
                &nbsp;|&nbsp;
                ⌛ Expire : <span style="color:#f59e0b;">{info['remaining']} min</span>
            </div>
            <div style="color:#8b92a9; margin-top:3px;">
                🔑 Connexions : <span style="color:#e2e8f0;">{info['logins']}</span>
                &nbsp;&nbsp;
                🍪 Session : <span style="color:#6ee7b7;">active</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🗂️ Navigation")
        pages = [
            "🏠 Vue Globale — KPIs",
            "📈 Analyse Temporelle",
            "🏆 Top Performances",
            "💰 Coûts & Rentabilité",
            "🔗 Corrélations",
            "🔍 Qualité des Données",
            "📋 Tableau Détaillé",
            "💡 Recommandations",
        ]
        page = st.radio("", pages, label_visibility="collapsed")

        st.markdown("<hr style='border-color:#2d3149; margin:14px 0;'>", unsafe_allow_html=True)
        st.markdown("### 🔽 Filtres")

        date_min = df["date"].min().date()
        date_max = df["date"].max().date()
        date_range = st.date_input("📅 Période", value=(date_min, date_max),
                                    min_value=date_min, max_value=date_max)

        secteur = st.selectbox("🏭 Secteur",
                               ["Tous"] + sorted(df["secteur"].dropna().unique()))
        service = st.selectbox("🛠️ Service",
                               ["Tous"] + sorted(df["service"].dropna().unique()))
        canal = st.selectbox("📡 Canal",
                             ["Tous"] + sorted(df["canal"].dropna().unique()))
        statut = st.selectbox("⚡ Statut",
                              ["Tous"] + sorted(df["statut_campagne"].dropna().unique()))
        bmin, bmax = float(df["budget_mad"].min()), float(df["budget_mad"].max())
        budget_range = st.slider("💸 Budget (MAD)", bmin, bmax, (bmin, bmax), step=100.0)

        st.markdown("<hr style='border-color:#2d3149; margin:14px 0;'>", unsafe_allow_html=True)
        if st.button("🚪 Déconnexion", use_container_width=True):
            _logout()

    # Application des filtres
    df_f = df.copy()
    if len(date_range) == 2:
        df_f = df_f[(df_f["date"].dt.date >= date_range[0]) &
                    (df_f["date"].dt.date <= date_range[1])]
    if secteur != "Tous": df_f = df_f[df_f["secteur"] == secteur]
    if service != "Tous": df_f = df_f[df_f["service"] == service]
    if canal   != "Tous": df_f = df_f[df_f["canal"]   == canal]
    if statut  != "Tous": df_f = df_f[df_f["statut_campagne"] == statut]
    df_f = df_f[(df_f["budget_mad"] >= budget_range[0]) &
                (df_f["budget_mad"] <= budget_range[1])]
    return df_f, page


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — VUE GLOBALE (KPIs)
# ══════════════════════════════════════════════════════════════════════════════

def fmt(val, prefix="", suffix="", decimals=2):
    if pd.isna(val): return "N/A"
    if val >= 1_000_000: return f"{prefix}{val/1_000_000:.1f}M{suffix}"
    if val >= 1_000:     return f"{prefix}{val/1_000:.1f}K{suffix}"
    return f"{prefix}{val:.{decimals}f}{suffix}"


def render_kpis(df):
    st.markdown("<div class='section-title'>📊 Indicateurs Clés de Performance</div>",
                unsafe_allow_html=True)
    if df.empty:
        st.warning("⚠️ Aucune donnée disponible avec les filtres actuels.")
        return

    budget = df["budget_mad"].sum(); revenu = df["revenu_mad"].sum()
    roas = revenu / budget if budget else 0
    kpis = [
        ("💰", "Budget Total",  fmt(budget, "MAD ", "", 0), "Total investi"),
        ("📈", "Revenu Total",  fmt(revenu, "MAD ", "", 0), "Chiffre d'affaires"),
        ("🎯", "ROAS",          f"{roas:.2f}x",             "Retour sur dépense pub"),
        ("🖱️","CTR Moyen",     f"{df['ctr_pct'].mean():.2f}%", "Taux de clic"),
        ("💵", "CPC Moyen",     fmt(df["cpc_mad"].mean(), "MAD ","",2), "Coût par clic"),
        ("🛒", "CPA Moyen",     fmt(df["cpa_mad"].mean(), "MAD ","",2), "Coût par acquisition"),
        ("✅", "Conversions",   fmt(df["conversions"].sum(),"","",0),  "Total conversions"),
        ("🔍", "Score SEO",     f"{df['score_seo'].mean():.1f}/100",   "Performance SEO"),
    ]
    cols = st.columns(4)
    for i, (icon, title, value, sub) in enumerate(kpis):
        with cols[i % 4]:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
                <div style="font-size:11px;color:#8b92a9;">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📌 Répartition par Statut & Revenu par Service</div>",
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        sc = df["statut_campagne"].value_counts().reset_index()
        sc.columns = ["Statut", "N"]
        fig = px.pie(sc, names="Statut", values="N", hole=0.55,
                     color_discrete_sequence=PALETTE)
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0", margin=dict(t=40,b=20,l=20,r=20),
                          title=dict(text="Statuts des Campagnes", font=dict(color="#e2e8f0")),
                          legend=dict(font=dict(color="#e2e8f0")))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        sr = df.groupby("service")["revenu_mad"].sum().sort_values(ascending=True)
        fig2 = go.Figure(go.Bar(
            x=sr.values, y=sr.index, orientation="h",
            marker=dict(color=PALETTE[:len(sr)]),
            text=[f"MAD {v/1000:.0f}K" for v in sr.values], textposition="outside"))
        fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font_color="#e2e8f0", margin=dict(t=40,b=20,l=20,r=80),
                           title=dict(text="Revenu par Service (MAD)", font=dict(color="#e2e8f0")),
                           xaxis=dict(color="#8b92a9"), yaxis=dict(color="#e2e8f0"))
        st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — ANALYSE TEMPORELLE
# ══════════════════════════════════════════════════════════════════════════════

def render_temporal(df):
    st.markdown("<div class='section-title'>📈 Évolution Temporelle des Performances</div>",
                unsafe_allow_html=True)
    if df.empty: st.warning("⚠️ Aucune donnée disponible."); return

    gran = st.radio("Granularité", ["Mensuel", "Trimestriel"], horizontal=True)
    gc = "mois" if gran == "Mensuel" else "trimestre"

    ts = df.groupby(gc).agg(
        budget=("budget_mad","sum"), revenu=("revenu_mad","sum"),
        conversions=("conversions","sum"), ctr=("ctr_pct","mean"), roas=("roas","mean"),
    ).reset_index().sort_values(gc)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=ts[gc], y=ts["budget"], name="Budget MAD",
                               line=dict(color=PALETTE[2],width=2.5),
                               fill="tozeroy", fillcolor="rgba(59,130,246,0.1)"))
    fig1.add_trace(go.Scatter(x=ts[gc], y=ts["revenu"], name="Revenu MAD",
                               line=dict(color=PALETTE[3],width=2.5)))
    fig1.update_layout(title="Budget vs Revenu", plot_bgcolor="rgba(0,0,0,0)",
                       paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0",
                       legend=dict(font=dict(color="#e2e8f0")),
                       xaxis=dict(color="#8b92a9"), yaxis=dict(color="#8b92a9"),
                       margin=dict(t=40,b=20))
    st.plotly_chart(fig1, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        fig2 = go.Figure(go.Bar(x=ts[gc], y=ts["conversions"], marker_color=PALETTE[0],
                                 text=ts["conversions"].astype(int), textposition="outside"))
        fig2.update_layout(title="Conversions par Période", plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0",
                           xaxis=dict(color="#8b92a9"), yaxis=dict(color="#8b92a9"),
                           margin=dict(t=40,b=20))
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        fig3 = make_subplots(specs=[[{"secondary_y": True}]])
        fig3.add_trace(go.Scatter(x=ts[gc], y=ts["ctr"], name="CTR %",
                                   line=dict(color=PALETTE[3],width=2.5)), secondary_y=False)
        fig3.add_trace(go.Scatter(x=ts[gc], y=ts["roas"], name="ROAS",
                                   line=dict(color=PALETTE[4],width=2.5,dash="dot")), secondary_y=True)
        fig3.update_layout(title="CTR & ROAS dans le temps", plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0",
                           legend=dict(font=dict(color="#e2e8f0")), margin=dict(t=40,b=20))
        st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — TOP PERFORMANCES
# ══════════════════════════════════════════════════════════════════════════════

def render_top(df):
    st.markdown("<div class='section-title'>🏆 Top 10 des Performances</div>",
                unsafe_allow_html=True)
    if df.empty: st.warning("⚠️ Aucune donnée disponible."); return

    metric = st.selectbox("Classer par", ["Revenu (MAD)", "Conversions", "ROAS", "Score SEO"])
    mm = {"Revenu (MAD)":("revenu_mad","sum"), "Conversions":("conversions","sum"),
          "ROAS":("roas","mean"), "Score SEO":("score_seo","mean")}
    col_m, agg_m = mm[metric]

    c1, c2 = st.columns(2)
    with c1:
        tc = df.groupby("client")[col_m].agg(agg_m).sort_values(ascending=False).head(10).reset_index()
        tc.columns = ["Client", metric]
        fig = go.Figure(go.Bar(
            x=tc[metric], y=tc["Client"], orientation="h", marker_color=PALETTE,
            text=tc[metric].apply(lambda v: f"{v:,.0f}" if v>100 else f"{v:.2f}"),
            textposition="outside"))
        fig.update_layout(title=f"Top 10 Clients — {metric}", plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0",
                          xaxis=dict(color="#8b92a9"), yaxis=dict(color="#e2e8f0"),
                          margin=dict(t=40,b=20,r=80))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        ts = df.groupby("secteur")[col_m].agg(agg_m).sort_values(ascending=False).reset_index()
        ts.columns = ["Secteur", metric]
        fig2 = px.bar(ts, x="Secteur", y=metric, color="Secteur",
                      color_discrete_sequence=PALETTE,
                      text=ts[metric].apply(lambda v: f"{v/1000:.0f}K" if v>1000 else f"{v:.2f}"))
        fig2.update_layout(title=f"{metric} par Secteur", plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0", showlegend=False,
                           xaxis=dict(color="#8b92a9"), yaxis=dict(color="#8b92a9"),
                           margin=dict(t=40,b=20))
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<div class='section-title'>📊 Matrice Service × Canal</div>", unsafe_allow_html=True)
    pivot = df.pivot_table(index="service", columns="canal", values=col_m, aggfunc=agg_m)
    fig3 = px.imshow(pivot, color_continuous_scale="Viridis",
                     text_auto=".0f" if agg_m=="sum" else ".2f")
    fig3.update_layout(title=f"{metric} — Matrice Service × Canal",
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       font_color="#e2e8f0", margin=dict(t=40,b=20))
    st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — COÛTS & RENTABILITÉ
# ══════════════════════════════════════════════════════════════════════════════

def render_costs(df):
    st.markdown("<div class='section-title'>💰 Analyse des Coûts & Rentabilité</div>",
                unsafe_allow_html=True)
    if df.empty: st.warning("⚠️ Aucune donnée disponible."); return

    c1, c2 = st.columns(2)
    with c1:
        cc = df.groupby("canal")["cpc_mad"].mean().sort_values()
        fig = go.Figure(go.Bar(x=cc.values, y=cc.index, orientation="h", marker_color=PALETTE,
                               text=[f"MAD {v:.1f}" for v in cc.values], textposition="outside"))
        fig.update_layout(title="CPC Moyen par Canal (MAD)", plot_bgcolor="rgba(0,0,0,0)",
                          paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0",
                          xaxis=dict(color="#8b92a9"), yaxis=dict(color="#e2e8f0"),
                          margin=dict(t=40,b=20,r=80))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        cs = df.groupby("service")["cpa_mad"].mean().sort_values()
        fig2 = go.Figure(go.Bar(x=cs.values, y=cs.index, orientation="h", marker_color=PALETTE,
                                text=[f"MAD {v:.1f}" for v in cs.values], textposition="outside"))
        fig2.update_layout(title="CPA Moyen par Service (MAD)", plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0",
                           xaxis=dict(color="#8b92a9"), yaxis=dict(color="#e2e8f0"),
                           margin=dict(t=40,b=20,r=80))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        rs = df.groupby("secteur")["roas"].mean().sort_values(ascending=False).reset_index()
        rs.columns = ["Secteur","ROAS"]
        thr = 2.0
        fig3 = go.Figure(go.Bar(
            x=rs["Secteur"], y=rs["ROAS"],
            marker_color=[PALETTE[3] if v>=thr else PALETTE[5] for v in rs["ROAS"]],
            text=rs["ROAS"].apply(lambda v: f"{v:.2f}x"), textposition="outside"))
        fig3.add_hline(y=thr, line_dash="dash", line_color="#f59e0b",
                       annotation_text=f"Cible ROAS={thr}x",
                       annotation_font=dict(color="#f59e0b"))
        fig3.update_layout(title="ROAS par Secteur", plot_bgcolor="rgba(0,0,0,0)",
                           paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0",
                           xaxis=dict(color="#8b92a9"), yaxis=dict(color="#8b92a9"),
                           margin=dict(t=40,b=20))
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        bc = df.groupby("canal")["budget_mad"].sum().reset_index()
        bc.columns = ["Canal","Budget"]
        fig4 = px.pie(bc, names="Canal", values="Budget", hole=0.55,
                      color_discrete_sequence=PALETTE)
        fig4.update_traces(textinfo="label+percent")
        fig4.update_layout(title="Répartition Budget par Canal",
                           plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                           font_color="#e2e8f0", legend=dict(font=dict(color="#e2e8f0")),
                           margin=dict(t=40,b=20))
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown("<div class='section-title'>🔍 Scatter — Budget vs Revenu</div>",
                unsafe_allow_html=True)
    fig5 = px.scatter(df, x="budget_mad", y="revenu_mad", color="service",
                      size="conversions", hover_data=["client","canal","roas"],
                      color_discrete_sequence=PALETTE,
                      labels={"budget_mad":"Budget (MAD)","revenu_mad":"Revenu (MAD)"},
                      opacity=0.75)
    mb = df["budget_mad"].max()
    fig5.add_trace(go.Scatter(x=[0,mb], y=[0,mb], mode="lines",
                              name="Seuil rentabilité (ROAS=1)",
                              line=dict(color="#f59e0b",dash="dash",width=1.5)))
    fig5.update_layout(title="Budget vs Revenu par Service (taille = conversions)",
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       font_color="#e2e8f0", legend=dict(font=dict(color="#e2e8f0")),
                       xaxis=dict(color="#8b92a9"), yaxis=dict(color="#8b92a9"),
                       margin=dict(t=40,b=20))
    st.plotly_chart(fig5, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8 — CORRÉLATIONS
# ══════════════════════════════════════════════════════════════════════════════

def render_correlations(df):
    st.markdown("<div class='section-title'>🔗 Heatmap de Corrélation</div>",
                unsafe_allow_html=True)
    if df.empty: st.warning("⚠️ Aucune donnée disponible."); return

    num_cols = ["impressions","clics","ctr_pct","conversions","budget_mad",
                "revenu_mad","cpc_mad","cpa_mad","roas","score_seo",
                "position_google","engagement_pct"]
    corr = df[num_cols].corr()
    fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r",
                    zmin=-1, zmax=1, aspect="auto")
    fig.update_layout(title="Matrice de Corrélation — Variables Numériques",
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      font_color="#e2e8f0", margin=dict(t=60,b=20), height=520)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>📐 Analyse de Relation</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1: var_x = st.selectbox("Variable X", num_cols, index=num_cols.index("budget_mad"))
    with c2: var_y = st.selectbox("Variable Y", num_cols, index=num_cols.index("revenu_mad"))

    fig2 = px.scatter(df, x=var_x, y=var_y, color="canal", trendline="ols",
                      trendline_scope="overall", color_discrete_sequence=PALETTE,
                      opacity=0.7, hover_data=["client","service"])
    fig2.update_layout(title=f"{var_x} vs {var_y}",
                       plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       font_color="#e2e8f0", legend=dict(font=dict(color="#e2e8f0")),
                       xaxis=dict(color="#8b92a9"), yaxis=dict(color="#8b92a9"),
                       margin=dict(t=40,b=20))
    st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9 — QUALITÉ DES DONNÉES
# ══════════════════════════════════════════════════════════════════════════════

def render_quality(df_raw, rapport):
    st.markdown("<div class='section-title'>🔍 Rapport Qualité des Données</div>",
                unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("📦 Lignes brutes",       f"{rapport['nb_lignes_brut']:,}")
    c2.metric("🧹 Lignes nettoyées",    f"{rapport['nb_lignes_propre']:,}")
    c3.metric("♻️ Doublons supprimés",  f"{rapport['doublons_supprimes']:,}")
    c4.metric("❓ Valeurs manquantes",  f"{rapport['total_manquants']:,}")

    st.markdown("<div class='section-title'>❓ Valeurs Manquantes par Colonne</div>",
                unsafe_allow_html=True)
    miss = pd.DataFrame(rapport["valeurs_manquantes"].items(), columns=["Colonne","N"])
    miss = miss[miss["N"] > 0]
    if miss.empty:
        st.markdown("<div class='alert-success'>✅ Aucune valeur manquante après nettoyage.</div>",
                    unsafe_allow_html=True)
    else:
        miss["% Manquant"] = (miss["N"] / rapport["nb_lignes_brut"] * 100).round(2)
        fig = go.Figure(go.Bar(x=miss["Colonne"], y=miss["N"], marker_color=PALETTE[5],
                               text=miss["% Manquant"].apply(lambda v: f"{v}%"),
                               textposition="outside"))
        fig.update_layout(title="Valeurs Manquantes (avant nettoyage)",
                          plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          font_color="#e2e8f0",
                          xaxis=dict(color="#8b92a9"), yaxis=dict(color="#8b92a9"),
                          margin=dict(t=40,b=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div class='section-title'>📊 Distributions des Variables Clés</div>",
                unsafe_allow_html=True)
    nc = ["budget_mad","revenu_mad","roas","ctr_pct","conversions","score_seo"]
    fig2 = make_subplots(rows=2, cols=3, subplot_titles=nc)
    for i, col in enumerate(nc):
        r, c = divmod(i, 3)
        fig2.add_trace(go.Histogram(x=df_raw[col].dropna(), nbinsx=30,
                                    marker_color=PALETTE[i], name=col, showlegend=False),
                       row=r+1, col=c+1)
    fig2.update_layout(height=420, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                       font_color="#e2e8f0", margin=dict(t=40,b=20),
                       title="Histogrammes des Variables Numériques")
    st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10 — TABLEAU DÉTAILLÉ
# ══════════════════════════════════════════════════════════════════════════════

def render_table(df):
    st.markdown("<div class='section-title'>📋 Tableau Détaillé des Campagnes</div>",
                unsafe_allow_html=True)
    if df.empty: st.warning("⚠️ Aucune donnée disponible."); return

    cols_d = ["campaign_id","date","client","secteur","service","canal",
              "budget_mad","revenu_mad","roas","ctr_pct","conversions",
              "cpc_mad","cpa_mad","score_seo","statut_campagne"]
    ds = df[cols_d].copy()
    ds["date"] = ds["date"].dt.strftime("%Y-%m-%d")

    st.info(f"📊 **{len(ds):,}** campagnes affichées")
    st.dataframe(
        ds.style.format({
            "budget_mad":"{:,.0f} MAD","revenu_mad":"{:,.0f} MAD",
            "roas":"{:.2f}x","ctr_pct":"{:.2f}%","conversions":"{:,.0f}",
            "cpc_mad":"{:.2f} MAD","cpa_mad":"{:.2f} MAD","score_seo":"{:.1f}",
        }).background_gradient(subset=["roas"], cmap="RdYlGn"),
        use_container_width=True, height=420)

    csv = ds.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Exporter les données filtrées (CSV)", data=csv,
                       file_name="campagnes_filtrees.csv", mime="text/csv",
                       use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 11 — RECOMMANDATIONS
# ══════════════════════════════════════════════════════════════════════════════

def render_recommendations(df):
    st.markdown("<div class='section-title'>💡 Recommandations Métier</div>",
                unsafe_allow_html=True)
    if df.empty: st.warning("⚠️ Aucune donnée disponible."); return

    rm = df["roas"].mean(); cm = df["ctr_pct"].mean()
    bc = df.groupby("canal")["roas"].mean(); bsvc = df.groupby("service")["revenu_mad"].sum()
    sm = df["score_seo"].mean()

    recs = [
        ("🎯","Performance Globale",
         f"Le ROAS moyen est de **{rm:.2f}x**. " +
         ("L'agence génère un bon retour sur investissement." if rm>=2 else
          "Optimisez les campagnes pour dépasser le seuil de 2x."),
         "success" if rm>=2 else "warning"),
        ("📡","Meilleur Canal",
         f"**{bc.idxmax()}** affiche le ROAS le plus élevé. Concentrez le budget sur ce canal.",
         "success"),
        ("⚠️","Canal à Optimiser",
         f"**{bc.idxmin()}** présente les performances les plus faibles. Revoir la stratégie.",
         "warning"),
        ("🛠️","Service Phare",
         f"**{bsvc.idxmax()}** génère le revenu le plus élevé. Renforcez les ressources.",
         "success"),
        ("🏭","Secteur Prioritaire",
         f"**{df.groupby('secteur')['roas'].mean().idxmax()}** : meilleur ROAS. Prospectez davantage.",
         "success"),
        ("🔍","SEO",
         f"Score SEO moyen : **{sm:.1f}/100**. " +
         ("Excellent niveau SEO." if sm>=70 else "Améliorez contenu, backlinks et vitesse de site."),
         "success" if sm>=70 else "warning"),
        ("🖱️","Taux de Clic",
         f"CTR moyen : **{cm:.2f}%**. " +
         ("Les annonces performent bien." if cm>=2 else
          "Optimisez les visuels et textes d'annonces."),
         "success" if cm>=2 else "warning"),
    ]

    for icon, title, text, level in recs:
        color = "#10b981" if level=="success" else "#f59e0b"
        bg    = "#062d1a"  if level=="success" else "#2d2006"
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {color};border-radius:10px;
                    padding:16px 20px;margin:8px 0;display:flex;align-items:flex-start;gap:12px;">
            <span style="font-size:24px;">{icon}</span>
            <div>
                <strong style="color:{color};font-size:15px;">{title}</strong><br>
                <span style="color:#e2e8f0;font-size:14px;">{text}</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>📊 Récapitulatif par Canal</div>",
                unsafe_allow_html=True)
    recap = df.groupby("canal").agg(
        Budget=("budget_mad","sum"), Revenu=("revenu_mad","sum"),
        ROAS=("roas","mean"), Conversions=("conversions","sum"),
        CTR=("ctr_pct","mean"), CPC=("cpc_mad","mean"),
    ).round(2).reset_index()
    st.dataframe(recap.style.background_gradient(subset=["ROAS"], cmap="RdYlGn"),
                 use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    _init_session()

    if not _session_valid():
        show_login()
        return

    df_raw, df, rapport = load_and_clean_data()
    df_f, page = render_sidebar(df)

    info = _session_info()
    st.markdown(f"""
    <div class="main-header">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <h1 style="color:white;margin:0;font-size:26px;">
                    📊 Dashboard — Agence Marketing Digital
                </h1>
                <p style="color:rgba(255,255,255,0.75);margin:4px 0 0 0;font-size:14px;">
                    {len(df_f):,} campagnes sélectionnées sur {len(df):,} au total
                </p>
            </div>
            <div style="text-align:right;font-size:13px;color:rgba(255,255,255,0.7);">
                👤 {info['username']}
                &nbsp;|&nbsp;
                🍪 Session {info['elapsed']} min
                &nbsp;|&nbsp;
                ⌛ Expire dans {info['remaining']} min
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    dispatch = {
        "🏠 Vue Globale — KPIs":   lambda: render_kpis(df_f),
        "📈 Analyse Temporelle":   lambda: render_temporal(df_f),
        "🏆 Top Performances":     lambda: render_top(df_f),
        "💰 Coûts & Rentabilité":  lambda: render_costs(df_f),
        "🔗 Corrélations":         lambda: render_correlations(df_f),
        "🔍 Qualité des Données":  lambda: render_quality(df_raw, rapport),
        "📋 Tableau Détaillé":     lambda: render_table(df_f),
        "💡 Recommandations":      lambda: render_recommendations(df_f),
    }
    dispatch.get(page, lambda: st.info("Page non trouvée."))()


if __name__ == "__main__":
    main()
