# TRELLO ANALYTICS DASHBOARD

from seaborn import set_style
import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go

# file paths dynamic — works on any computer regardless of the user
# it automatically finds the path or itself in any pc :
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Browser setup configuration,  Sets the browser tab title, icon, and forces wide layout 
# initial_sidebar_state="expanded" keeps filters visible on load

st.set_page_config(
    page_title="Trello Analytics · Master Board 2026",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme CSS Styling

# - Main application
# - Sidebar
# - KPI Cards
# - Tables
# - Plotly Charts

# Background color for the Streamlit app
# ST.MARKDOWN mainly used for displaying content on Streamlit app
# INSIDE st.markdown() we can write CSS to customize the appearance of the Streamlit app.


st.markdown("""
<style>
            
# Main background #0f172a (dark navy)
            
.stApp {
    background: #0f172a;
    color: #f8fafc;
}
            
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 95%;
}


# Sidebar background #111827 (dark gray)
            
section[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #1f2937;
}

section[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}
            


            
/* =========================
  White  HEADINGS
========================= */

h1 {
    color: #ffffff !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
}

h2,h3,h4 {
    color: #f8fafc !important;
}
            






/* =========================
   KPI METRIC CONTAINERS
========================= */

            
# KPI card background + border
            
# Rounded Corners
# Borders
# Shadows
# Dark Theme

div[data-testid="metric-container"] {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.25);
}

            
div[data-testid="metric-container"] label {
    color: #94a3b8 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: white !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
}


# DATAFRAME CONTAINERS # Table Border + Rounded Corners

[data-testid="stDataFrame"] {
    border-radius: 14px;          # rounded corners for the dataframe container
    overflow: hidden;
    border: 1px solid #334155;
}
            

            
/* =========================
   PLOTLY CHART CONTAINERS
========================= */

# Chart container dark background
            
.stPlotlyChart {
    background: #1e293b;
    border-radius: 18px;      # Each chart container has rounded corners with a radius of 18px
    padding: 10px;
    border: 1px solid #334155;
}

/* =========================
   MULTISELECT / SELECTBOX
========================= */

# Dark dropdown inputs
            
.stMultiSelect div[data-baseweb="select"] {
    background: #1e293b;
}</style>
            
""", unsafe_allow_html=True)


# stores data in cache or memory for faster access on subsequent runs

# Benefits:
# - Faster dashboard reloads
# - Reduced file I/O operations
# - Better performance

@st.cache_data # stores data in cache or memory for faster access on subsequent runs
def load_data():
    try:
        board_path = os.path.join(DATA_DIR, "trello_board_snapshot.csv") if os.path.exists(os.path.join(DATA_DIR, "trello_board_snapshot.csv")) else r"C:\Users\Findingpi\OneDrive - Circls\Documents\Trello Dashboard\data\trello_board_snapshot.csv"
        members_path = os.path.join(DATA_DIR, "trello_member_activity_summary.csv") if os.path.exists(os.path.join(DATA_DIR, "trello_member_activity_summary.csv")) else r"C:\Users\Findingpi\OneDrive - Circls\Documents\Trello Dashboard\data\trello_member_activity_summary.csv"

        board = pd.read_csv(board_path)
        events = pd.read_csv(os.path.join(DATA_DIR, "trello_activity_events(in).csv"))
        members = pd.read_csv(members_path)
        daily = pd.read_csv(os.path.join(DATA_DIR, "trello_daily_activity_summary(in).csv"))
        cards = pd.read_csv(os.path.join(DATA_DIR, "trello_card_activity_summary(in).csv"))

        # Datetime processing normalization 
        # Convert string date columns into datetime objects
        # for filtering, grouping, and time-series analysis.

        events["action_date"] = pd.to_datetime(events["action_date"])
        events["activity_day_parsed"] = pd.to_datetime(events["activity_day"])
        daily["activity_day"] = pd.to_datetime(daily["activity_day"])
        
        return board, events, members, daily, cards
    except FileNotFoundError as e:
        st.error(f"CSV File Not Found: {e}")
        st.stop()

# Load Data
board, events, members, daily, cards = load_data()

# Sidebar Filters 

with st.sidebar:
    st.header("🔧 Filters")
    
    min_date = events["activity_day_parsed"].min().date()
    max_date = events["activity_day_parsed"].max().date()
    
    date_range = st.date_input(
        "Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    available_members = sorted(events["member_name"].dropna().unique().tolist())
    selected_members = st.multiselect("Members", options=available_members, default=available_members)



#  Ensures valid start and end dates are always available.


if isinstance(date_range, list) and len(date_range) == 2:
    start_dt, end_dt = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_dt, end_dt = pd.Timestamp(min_date), pd.Timestamp(max_date)

# ==================== LIVE RESPONSIVE FILTER COMPILATION ====================
events_filtered = events[
    (events["member_name"].isin(selected_members)) &
    (events["activity_day_parsed"] >= start_dt) &
    (events["activity_day_parsed"] <= end_dt)
]

# FILTER CARDS BASED ON SELECTED MEMBERS during the selected date range.

filtered_card_ids = events_filtered["card_id"].dropna().unique()

cards_filtered = cards[
    cards["card_id"].isin(filtered_card_ids)
].copy()



# Generates daily metrics:
# - Total Actions
# - Checklist Completions
# - Card Moves
# - Card Updates

if not events_filtered.empty:
    daily_dynamic = events_filtered.groupby("activity_day_parsed").agg(
        total_actions=('action_id', 'count'),
        checklist_completions=('action_type', lambda x: (x == 'updateCheckItemStateOnCard').sum()),
        card_moves_detected=('is_card_move', lambda x: (x == 'yes').sum()),
        card_updates=('action_type', lambda x: (x == 'updateCard').sum())
    ).reset_index()
    daily_dynamic.rename(columns={'activity_day_parsed': 'activity_day'}, inplace=True)
    daily_dynamic = daily_dynamic.sort_values("activity_day")
else:
    daily_dynamic = pd.DataFrame(columns=['activity_day', 'total_actions', 'checklist_completions', 'card_moves_detected', 'card_updates'])


# Live Metrics Core Logic Calculations

total_actions_calc = len(events_filtered)

# Values from Trello Board Snapshot
total_cards_calc = int(board["card_count"].iloc[0])

active_cards_calc = (
    events_filtered["card_id"]
    .dropna()
    .nunique()
)
# Active members based on filters
active_members_calc = (
    events_filtered["member_name"].nunique()
    if total_actions_calc > 0
    else 0
)

total_checklist_calc = (
    int(daily_dynamic["checklist_completions"].sum())
    if not daily_dynamic.empty
    else 0
)

total_moves_calc = (
    int(daily_dynamic["card_moves_detected"].sum())
    if not daily_dynamic.empty
    else 0
)

# Header Section Template
st.title("📋 Master Board 2026 — Activity Analytics")
st.caption(f"Analysis Window Tracked · {active_members_calc} Filtered Users · {total_actions_calc:,} Live Active Events Logs")
st.divider()

# KPI metrics row
col1, col2, col3, col4, col5, col6 = st.columns(6)
def kpi_card(col, label, value, sub, color):
    col.markdown(f"""
    <div style="background:#161b22; border:1px solid {color}; border-radius:10px; padding:16px 14px 12px; min-height:100px;">
        <div style="color:#8b949e;font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;font-weight:600;margin-bottom:6px;">{label}</div>
        <div style="color:{color};font-size:1.8rem;font-weight:700;line-height:1.1;">{value}</div>
        <div style="color:#8b949e;font-size:0.78rem;margin-top:4px;">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

kpi_card(col1, "Total Actions", f"{total_actions_calc:,}", "Active range log", "#ff6b6b")

kpi_card(
    col2,
    "Total Cards",
    f"{total_cards_calc:,}",
    "Total Board Cards",
    "#43d98c"
)

kpi_card(
    col3,
    "Active Cards",
    f"{active_cards_calc:,}",
    "Cards touched in filters",
    "#38BDF8"
)

kpi_card(
    col4,
    "Active Members",
    f"{active_members_calc}",
    "Selected users count",
    "#4ecdc4"
)

kpi_card(
    col5,
    "Checklist Done",
    f"{total_checklist_calc:,}",
    "Completions total",
    "#f4e06d"
)

kpi_card(
    col6,
    "Total Members",
    f"{board['member_count'].iloc[0]}",
    "Registered Board Users",
    "#a78bfa"
)

# ==================== CHART 1: DAILY ACTIVITY OVER TIME ====================

# Displays: Total Actions & Checklist Completions


st.subheader("📈 Daily Activity Over Time")
if not daily_dynamic.empty:
    fig_timeline = go.Figure()
    fig_timeline.add_trace(go.Scatter(
        x=daily_dynamic["activity_day"], y=daily_dynamic["total_actions"],
        name="Total Actions", fill="tozeroy", line=dict(color="#6c8fff", width=2),
        fillcolor="rgba(108,143,255,0.1)"
    ))
    fig_timeline.add_trace(go.Scatter(
        x=daily_dynamic["activity_day"], y=daily_dynamic["checklist_completions"],
        name="Checklist Completions", line=dict(color="#ffe66d", width=1.5),
        fillcolor="rgba(255,230,109,0.06)", fill="tozeroy"
    ))
    fig_timeline.update_layout(template="plotly_dark", height=250, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig_timeline, use_container_width=True)
else:
    st.info("No timeline records found for current selection criteria.")

# Blue Line = Total Actions per Day
# Yellow Line = Checklist Completions per Day


# ==================== CHART 2: ACTION CATEGORIES & CARD STATUS ====================


col_a, col_b = st.columns(2)

# Action categories -  updates, moves, checklist actions, comments.

with col_a:
    st.subheader("🍩 Action Categories")
    if not events_filtered.empty:
        cat_counts = events_filtered["activity_category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]
        fig_cat = px.pie(cat_counts, names="category", values="count", hole=0.6, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Bold)
        fig_cat.update_layout(margin=dict(l=0,r=0,t=10,b=0), height=300)
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("No categories context log matching filters.")

# update_layout() graph ki styling, height, theme aur legend position

# displaying charts on streamlit dashboard with use_container_width=True 

filtered_card_ids = events_filtered["card_id"].unique()

cards_filtered = cards[
    cards["card_id"].isin(filtered_card_ids)
]

# CARD STATUS DISTRIBUTION Updates status automatically based on filters

with col_b:
    st.subheader("🃏 Card Status Distribution")

    if not cards_filtered.empty:

        list_counts = (
            cards_filtered["current_list"]
            .value_counts()
            .reset_index()
        )

        list_counts.columns = ["Status", "Cards"]

        fig_list = px.pie(
            list_counts,
            names="Status",
            values="Cards",
            template="plotly_dark",
            color_discrete_sequence=[
                "#6C8FFF",
                "#43D98C",
                "#F4E06D",
                "#A78BFA",
                "#FF6B6B",
                "#38BDF8"
            ]
        )

        fig_list.update_traces(
            textinfo="percent+label",
            textposition="inside",
            hovertemplate=
            "<b>%{label}</b><br>" +
            "Cards: %{value}<br>" +
            "Percentage: %{percent}<extra></extra>"
        )

        fig_list.update_layout(
            height=320,
            margin=dict(l=0, r=0, t=10, b=10),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(
            fig_list,
            use_container_width=True
        )

    else:
        st.info("No cards found for selected filters.")

# Leaderboard Matrix Summary Calculations

# - Total Actions
# - Active Days
# - Cards Touched
# - Checklist Completions
# - Card Moves
# - Efficiency Score

st.subheader("🏆 Member Leaderboard")
if not events_filtered.empty:
    leaderboard_list = []
    for m_name in selected_members:
        m_events = events_filtered[events_filtered["member_name"] == m_name]
        if len(m_events) > 0:
            leaderboard_list.append({
                "member_name": m_name,
                "total_actions": len(m_events),
                "active_days": m_events["activity_day_parsed"].dt.date.nunique(),
                "unique_cards_touched": m_events["card_id"].nunique(),
                "checklist_completions": len(m_events[m_events["action_type"] == "updateCheckItemStateOnCard"]),
                "card_moves_detected": len(m_events[m_events["is_card_move"] == "yes"]),
                "efficiency": round(len(m_events) / max(m_events["activity_day_parsed"].dt.date.nunique(), 1), 1)
            })
    active_df = pd.DataFrame(leaderboard_list)
    if not active_df.empty:
        total_sum = active_df["total_actions"].sum()
        active_df["share_%"] = (
            (active_df["total_actions"] / total_sum * 100)
            .round(1)
        )
        active_df = active_df.sort_values("total_actions", ascending=False)

        st.dataframe(
            active_df[[
                "member_name", "total_actions", "active_days",
                "unique_cards_touched", "checklist_completions",
                "card_moves_detected", "efficiency", "share_%"
            ]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "member_name":           st.column_config.TextColumn("Member"),
                "total_actions":         st.column_config.NumberColumn("Actions",     format="%d"),
                "active_days":           st.column_config.NumberColumn("Active Days", format="%d"),
                "unique_cards_touched":  st.column_config.NumberColumn("Cards",       format="%d"),
                "checklist_completions": st.column_config.NumberColumn("Checklist ✓", format="%d"),
                "card_moves_detected":   st.column_config.NumberColumn("Moves",       format="%d"),
                "efficiency":            st.column_config.NumberColumn("Actions/Day", format="%.1f"),
                "share_%": st.column_config.ProgressColumn(
                    "Share %",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%",   # ← THIS fixes 4560% → 45.6%
                ),
            }
        )

st.subheader("🗓️ Monthly Activity Heatmap")
if not events_filtered.empty:
    events_heat = events_filtered.copy()
    events_heat["month"] = events_heat["activity_day_parsed"].dt.strftime("%b %Y")
    events_heat["week_of_month"] = ((events_heat["activity_day_parsed"].dt.day - 1) // 7) + 1
    
    heat_pivot = events_heat.pivot_table(index="month", columns="week_of_month", values="action_id", aggfunc="count").fillna(0)
    fig_heat = px.imshow(heat_pivot, color_continuous_scale="Blues", template="plotly_dark", labels=dict(x="Week of Month", y="Month", color="Actions"), aspect="auto")
    fig_heat.update_layout(height=250, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("No metrics matching active pipeline to display heatmap.")
    

# CHART 4: DAILY ACTIVITY COMPOSITION (STACKED) 


st.markdown("""
<div style="display:flex;align-items:center;gap:10px;margin:18px 0 10px;">
    <span style="color:#38bdf8;font-size:0.72rem;letter-spacing:0.12em;text-transform:uppercase;font-weight:700;">── Engagement Insights ──</span>
</div>
""", unsafe_allow_html=True)

col_e1, col_e2 = st.columns(2)
with col_e1:
    st.markdown("<p style='color:#ff6b6b;font-size:0.75rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;'>● Daily Activity Composition (Stacked)</p>", unsafe_allow_html=True)
    if not daily_dynamic.empty:
        fig_daily = go.Figure()
        
        # Stacked Trace 1: Card Updates (Bottom Layer)

        fig_daily.add_trace(go.Scatter(
            x=daily_dynamic["activity_day"], y=daily_dynamic["card_updates"],
            name="Card Updates", mode="lines", fill="tozeroy",
            line=dict(color="#6c8fff", width=1.5), fillcolor="rgba(108,143,255,0.3)"
        ))
        # Stacked Trace 2: Checklist Completions (Stacked Layer using 'tonexty')
        fig_daily.add_trace(go.Scatter(
            x=daily_dynamic["activity_day"], y=daily_dynamic["checklist_completions"],
            name="Checklist ✓", mode="lines", fill="tonexty",
            line=dict(color="#f4e06d", width=1.5), fillcolor="rgba(244,224,109,0.2)"
        ))
        # Stacked Trace 3: Card Moves Detected (Top Stacked Layer)
        fig_daily.add_trace(go.Scatter(
            x=daily_dynamic["activity_day"], y=daily_dynamic["card_moves_detected"],
            name="Card Moves", mode="lines", fill="tonexty",
            line=dict(color="#ff6b6b", width=1.5), fillcolor="rgba(255,107,107,0.15)"
        ))
        
        fig_daily.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02), hovermode="x unified")
        st.plotly_chart(fig_daily, use_container_width=True)
    else:
        st.info("No daily tracking records logs matrix found.")



with col_e2:
    st.markdown("<p style='color:#a78bfa;font-size:0.75rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;'>● Member Efficiency (Actions per Active Day)</p>", unsafe_allow_html=True)
    if 'active_df' in locals() and not active_df.empty:
        eff_h = active_df.sort_values("efficiency", ascending=True)
        colors_h = ["#ff6b6b" if x >= 20 else "#f4e06d" if x >= 10 else "#43d98c" for x in eff_h["efficiency"]]
        fig_eff = go.Figure(go.Bar(x=eff_h["efficiency"], y=eff_h["member_name"], orientation="h", marker_color=colors_h, text=eff_h["efficiency"], textposition="outside"))
        fig_eff.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=10, b=60), xaxis=dict(title="Actions/Day"))
        st.plotly_chart(fig_eff, use_container_width=True)


# Chart 5 — Due Date Completion Rate



cards_due = cards_filtered[cards_filtered["due"].notna()].copy()

if not cards_due.empty:
    cards_due["due_complete"] = cards_due["due_complete"].astype(bool)

    completed = cards_due["due_complete"].sum()
    not_complete = (~cards_due["due_complete"]).sum()

    # Two equal columns
    col_d1, col_d2 = st.columns(2)

    # =====================================================
    # LEFT COLUMN
    # =====================================================
    with col_d1:

        st.markdown(
            "<h3 style='margin-bottom:10px;'>📅 Due Date Completion Rate</h3>",
            unsafe_allow_html=True
        )

        fig_due = go.Figure(go.Pie(
            labels=["Completed On Time", "Not Completed"],
            values=[completed, not_complete],
            hole=0.65,
            marker=dict(colors=["#43d98c", "#ff6b6b"])
        ))

        fig_due.update_layout(
            template="plotly_dark",
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True,
            annotations=[dict(
                text=f"{round(completed / len(cards_due) * 100, 1)}%",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=22, color="white")
            )]
        )

        st.plotly_chart(fig_due, use_container_width=True)

    # =====================================================
    # RIGHT COLUMN
    # =====================================================
    with col_d2:

        st.markdown(
            "<h3 style='margin-bottom:10px;'>🎯 Member Work Style</h3>",
            unsafe_allow_html=True
        )

        style_map = {
            "updateCard": ("Card Updater", "#6c8fff"),
            "updateCheckItemStateOnCard": ("Task Checker", "#43d98c"),
        }

        members_style = members[
            members["member_name"].isin(selected_members)
        ].copy()

        # Every other action becomes Card Mover
        members_style["work_style"] = members_style["top_action_type"].apply(
            lambda x: style_map[x][0] if x in style_map else "Card Mover"
        )

        style_counts = (
            members_style["work_style"]
            .value_counts()
            .reset_index()
        )

        style_counts.columns = ["style", "count"]

        fig_style = px.pie(
            style_counts,
            names="style",
            values="count",
            hole=0.6,
            template="plotly_dark",
            color="style",
            color_discrete_map={
                "Card Updater": "#6c8fff",
                "Task Checker": "#43d98c",
                "Card Mover": "#ff6b6b",
            }
        )

        fig_style.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True
        )

        st.plotly_chart(fig_style, use_container_width=True)





# Chart 6 — Card Assignment Workload

st.subheader("👥 Card Assignment Distribution")

# Build member list per card from events
card_members = events_filtered.groupby("card_id")["member_name"]\
    .apply(lambda x: sorted(x.dropna().unique().tolist())).reset_index()
card_members.columns = ["card_id", "member_list"]

cards_with_names = cards_filtered.merge(card_members, on="card_id", how="left")
cards_with_names["member_list"] = cards_with_names["member_list"].apply(
    lambda x: x if isinstance(x, list) else []
)

# ── Merge 4, 5, 6 into a single "4+" bucket ──
def assignment_bucket(n):
    if n == 1:
        return "Solo"
    elif n == 2:
        return "Pair"
    elif n == 3:
        return "Team of 3"
    else:
        return "Team of 4+"      # ← merges 4, 5, 6 together

cards_with_names["assignment_label"] = cards_with_names["assigned_member_count"]\
    .apply(assignment_bucket)

# Order buckets correctly (not alphabetical)
bucket_order = ["Solo", "Pair", "Team of 3", "Team of 4+"]
assign_counts = cards_with_names["assignment_label"]\
    .value_counts().reindex(bucket_order).fillna(0).reset_index()
assign_counts.columns = ["label", "Card Count"]

colors_assign = ["#ff6b6b","#f4e06d","#43d98c","#6c8fff","#a78bfa"]

fig_assign = go.Figure(go.Bar(
    x=assign_counts["label"],
    y=assign_counts["Card Count"],
    marker_color=colors_assign[:len(assign_counts)],
    text=assign_counts["Card Count"].astype(int),
    textposition="outside",
    textfont=dict(color="white", size=12)
))
fig_assign.update_layout(
    template="plotly_dark", height=300,
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis_title="Assignment Type",
    yaxis_title="Number of Cards",
    showlegend=False
)
st.plotly_chart(fig_assign, use_container_width=True)



# Chart 7 — Peak Activity Hours
st.subheader("⏰ Peak Activity Hours")

# Extract hour from timestamp
events_filtered["hour"] = events_filtered["action_date"].dt.hour

# Count actions per hour
hourly_activity = (
    events_filtered.groupby("hour")
    .size()
    .reset_index(name="Total Actions")
)

# Optional: Show only business hours
peak_hours = [10, 12, 14, 16, 18, 20]
hourly_activity = hourly_activity[
    hourly_activity["hour"].isin(peak_hours)
]

# Convert hour to label
hourly_activity["Hour"] = hourly_activity["hour"].apply(
    lambda x: f"{x}:00"
)

# Sort by most active hour
hourly_activity = hourly_activity.sort_values(
    by="Total Actions",
    ascending=True
)

# Create Horizontal Bar Chart
fig_hour = go.Figure(go.Bar(
    y=hourly_activity["Hour"],
    x=hourly_activity["Total Actions"],
    orientation="h",
    marker=dict(
        color=hourly_activity["Total Actions"],
        colorscale="Blues",
        showscale=False
    ),
    text=hourly_activity["Total Actions"],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>Actions: %{x}<extra></extra>"
))

fig_hour.update_layout(
    template="plotly_dark",
    height=350,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="Number of Actions",
    yaxis_title="Hour of Day",
    showlegend=False
)

st.plotly_chart(fig_hour, use_container_width=True)


# Top Action- Work Style
# updateCard- Card Updater
# updateCheckItemStateOnCard- Task Checker
# createCard-  Card Mover
# commentCard- Card Mover
# moveCardToBoard- Card Mover



## CHART 8- Day of Week Activity

st.subheader("📅 Activity by Day of Week")

events_filtered["day_of_week"] = events_filtered["action_date"].dt.day_name()
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
day_counts = events_filtered["day_of_week"].value_counts().reindex(day_order).reset_index()
day_counts.columns = ["day","count"]

day_colors = ["#6c8fff","#6c8fff","#a78bfa","#a78bfa","#f4e06d","#ff6b6b","#ff6b6b"]

fig_day = go.Figure(go.Bar(
    x=day_counts["day"],
    y=day_counts["count"],
    marker_color=day_colors,
    text=day_counts["count"],
    textposition="outside",
    textfont=dict(color="white")
))
fig_day.update_layout(
    template="plotly_dark", height=300,
    margin=dict(l=0,r=0,t=10,b=0),
    showlegend=False,
    yaxis=dict(gridcolor="#1f2937")
)
st.plotly_chart(fig_day, use_container_width=True)





