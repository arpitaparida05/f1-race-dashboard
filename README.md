# 🏎️ Formula 1 Race Strategy & Telemetry Analytics Console

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://arpita-f1-dashboard.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![FastF1](https://img.shields.io/badge/FastF1-v3.x-red)
![License](https://img.shields.io/badge/License-MIT-green)

A production-grade Formula 1 race strategy and telemetry analysis console. This project models driver pace, quantify tyre compound degradation through Ordinary Least Squares (OLS) regression, and visualizes circuit track evolution across Grand Prix sessions.

🔗 **Live Web Dashboard:** [arpita-f1-dashboard.streamlit.app](https://arpita-f1-dashboard.streamlit.app)

---

## 📌 Key Features

* **Head-to-Head Pace Modeling:** Lap-by-lap pace overlay isolating pure racing laps by filtering pit-in/pit-out laps and safety car anomalies.
* **Tyre Degradation Analysis (OLS):** Stint performance curves tracking lap time degradation as a function of tyre age (`TyreLife`), mapped across official Pirelli compounds (Soft, Medium, Hard).
* **Track Evolution Distribution:** Box-plot distributions measuring track rubbering-in and lap time compression across entire race distances.
* **Pit-Wall Console Interface:** High-contrast dark telemetry theme with real-time KPI cards for fastest laps, delta intervals, and stint metrics.
* **Resilient Data Architecture:** Decoupled offline ingestion pipeline generating sanitized CSV datasets to avoid live API rate-limiting and cloud container IP restrictions.

---

## 🛠️ Tech Stack & Architecture

* **Core Engine:** Python 3.11, FastF1
* **Data Processing:** Pandas, NumPy, Statsmodels (OLS regression)
* **Visualization:** Plotly Graph Objects (`go`), Plotly Express (`px`)
* **Deployment & UI:** Streamlit Cloud, Custom CSS
