# Trello Analytics Dashboard

An interactive Streamlit dashboard that transforms raw Trello board export data into visual analytics 
covering member activity, card performance, and daily trends over a 120-day window.

🔗 **Live App:** https://trello-analytics-dashboard.streamlit.app/

---

## 📊 Dashboard Highlights

- **1,867 actions** tracked across **120 days** (Feb – Jun 2026)
- **15 active members** out of 25 on the board
- **137 active cards** out of 363 total
- **12 visualizations** — KPI cards, timelines, donuts, heatmaps, leaderboards

---

## 🗂️ Dataset

Five CSV files exported from a Trello Master Board:

| File | Description |
|---|---|
| `trello_board_snapshot.csv` | Board-level metadata |
| `trello_activity_events_in_.csv` | Ball-by-ball event log |
| `trello_member_activity_summary.csv` | Per-member aggregates |
| `trello_daily_activity_summary_in_.csv` | Per-day aggregates |
| `trello_card_activity_summary_in_.csv` | Per-card aggregates |

---

## 🚀 Run Locally

```bash
git clone https://github.com/your-username/trello-analytics-dashboard.git
cd trello-analytics-dashboard
pip install -r requirements.txt
streamlit run app.py
```

---

## 🛠️ Tech Stack

`Streamlit` · `Pandas` · `Plotly` · `NumPy`

---

## 💡 Key Insights

- Activity is **episodic** — 3 days alone account for 17% of all actions
- **One member drives 45%** of total board activity (851 / 1,867 actions)
- Only **30 comments** in 120 days — Trello is used for execution, not communication
- Top cards are all **financial reconciliation** tasks (credit cards, bank recons)
- **Month-end weeks** are consistently the most active — aligned with finance deadlines
- **536 checklist completions** are the strongest signal of actual work done

---

## 📁 File Structure

```
├── app.py
├── requirements.txt
├── README.md
└── data/
    ├── trello_board_snapshot.csv
    ├── trello_activity_events_in_.csv
    ├── trello_member_activity_summary.csv
    ├── trello_daily_activity_summary_in_.csv
    └── trello_card_activity_summary_in_.csv
```

---

*Built with Streamlit · Deployed on Streamlit Community Cloud*
