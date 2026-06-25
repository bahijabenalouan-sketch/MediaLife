# 📊 Dashboard — Agence de Marketing Digital

**Projet Data Visualisation | Prof : TAOUSSI Jamal**  
**Étudiante : BENALOUAN BAHIJA**

---

## 📋 Description

Application web interactive développée avec **Streamlit** pour analyser les performances
d'une agence de marketing digital spécialisée en création d'applications mobiles,
publicités, contenu digital, SEO et branding.

---

## 🚀 Lancement rapide

```bash
# 1. Cloner / décompresser le projet
cd dashboard_marketing

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer le dashboard
streamlit run app.py
```

L'application s'ouvre automatiquement dans votre navigateur à l'adresse :
`http://localhost:8501`

---

## 🔐 Accès

| Champ        | Valeur              |
|--------------|---------------------|
| Identifiant  | `bahija.marketing`  |
| Mot de passe | `Marketing@2026`    |

---

## 📁 Structure du projet

```
dashboard_marketing/
│
├── app.py                                          ← Application principale Streamlit
├── requirements.txt                                ← Dépendances Python
├── README.md                                       ← Ce fichier
└── BENALOUAN_BAHIJA_Dashboard_Agence_Marketing_Digital.csv  ← Données source
```

---

## 🗂️ Pages du Dashboard

| Page | Contenu |
|------|---------|
| 🏠 Vue Globale — KPIs | Budget total, Revenu, ROAS, CTR, CPC, CPA, Conversions, Score SEO |
| 📈 Analyse Temporelle | Évolution budget/revenu, conversions, CTR & ROAS dans le temps |
| 🏆 Top Performances | Top 10 clients, classement par secteur, matrice Service × Canal |
| 💰 Coûts & Rentabilité | CPC/CPA par canal & service, ROAS par secteur, scatter Budget vs Revenu |
| 🔗 Corrélations | Heatmap de corrélation, scatter personnalisé avec régression |
| 🔍 Qualité des Données | Rapport de nettoyage, valeurs manquantes, distributions |
| 📋 Tableau Détaillé | Tableau filtrable + export CSV |
| 💡 Recommandations | Recommandations métier automatiques basées sur les KPIs |

---

## 🔽 Filtres disponibles (Sidebar)

- **Période** : sélecteur de plage de dates
- **Secteur** : Restaurant, Tourisme, Santé, Finance, Retail, Immobilier, Education
- **Service** : Content, Landing page, SEO, App mobile, Publicité, Branding
- **Canal** : Google Ads, Meta Ads, TikTok Ads, LinkedIn Ads, SEO, Emailing, Influence
- **Statut** : Active, Terminée, Pause, Optimisation
- **Budget** : slider de plage de budget (MAD)

---

## 🧹 Nettoyage des données appliqué

1. **Suppression des doublons** : `drop_duplicates()`
2. **Conversion des dates** : `pd.to_datetime()` + extraction mois / trimestre / année
3. **Valeurs manquantes** : remplacement par la médiane par colonne
4. **Valeurs aberrantes** : écrêtage IQR (percentiles 1% – 99%) sur les variables clés
5. **Pas de modification** du fichier CSV original

---

## 📊 KPIs calculés

| KPI | Calcul |
|-----|--------|
| Budget Total | `sum(budget_mad)` |
| Revenu Total | `sum(revenu_mad)` |
| ROAS | `sum(revenu_mad) / sum(budget_mad)` |
| CTR Moyen | `mean(ctr_pct)` |
| CPC Moyen | `mean(cpc_mad)` |
| CPA Moyen | `mean(cpa_mad)` |
| Conversions | `sum(conversions)` |
| Score SEO | `mean(score_seo)` |

---

## 🛠️ Technologies utilisées

- **Python 3.10+**
- **Streamlit** — Interface web
- **Pandas / NumPy** — Traitement des données
- **Plotly** — Visualisations interactives
- **Statsmodels** — Régression (trendline)

---

## ⚙️ Configuration système recommandée

- Python ≥ 3.10
- RAM ≥ 4 Go
- Navigateur moderne (Chrome, Firefox, Edge)
