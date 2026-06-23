import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page Configuration / Page header

st.set_page_config(
    page_title="Trello Analytics · Master Board 2026",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Background color for the Streamlit app

st.markdown("""
<style>
/* ── Global background & text ── */
.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}
...
""", unsafe_allow_html=True)


@st.cache_data # stores data in cache or memory for faster access on subsequent runs
def load_data():
    try:
        board = pd.read_csv(
            r"C:\Users\Findingpi\OneDrive - Circls\Documents\Trello Dashboard\data\trello_board_snapshot.csv"
        )

        events = pd.read_csv(
            os.path.join(DATA_DIR, "trello_activity_events(in).csv"),
            parse_dates=["action_date"]
        )

        members = pd.read_csv(
            r"C:\Users\Findingpi\OneDrive - Circls\Documents\Trello Dashboard\data\trello_member_activity_summary.csv"
        )

        daily = pd.read_csv(
            os.path.join(DATA_DIR, "trello_daily_activity_summary(in).csv"),
            parse_dates=["activity_day"]
        )

        cards = pd.read_csv(
            os.path.join(DATA_DIR, "trello_card_activity_summary(in).csv")
        )

        return board, events, members, daily, cards
    except FileNotFoundError as e:
        st.error(f"CSV File Not Found: {e}")
        st.stop()


# Load Data
board, events, members, daily, cards = load_data()

# Dashboard Header
st.title("📋 Master Board 2026 — Activity Analytics")

try:
    st.caption(
        f"120-day analysis window · "
        f"{board['member_count'].iloc[0]} members · "
        f"{board['card_count'].iloc[0]} cards · "
        f"{board['actions_in_period'].iloc[0]:,} actions"
    )

except KeyError as e:
    st.warning(f"Missing column in dataset: {e}")

st.divider() # divided into horizontal sections for better visual separation


### Step 5 — KPI metrics row

col1, col2, col3, col4, col5, col6 = st.columns(6)

def kpi_card(col, label, value, sub, color, glow):
    col.markdown(f"""
    <div style="
        background:#161b22;
        border:1px solid {color};
        border-radius:10px;
        padding:16px 14px 12px;
        box-shadow: 0 0 14px {glow};
        min-height:100px;
    ">
        <div style="color:#8b949e;font-size:0.68rem;letter-spacing:0.1em;
                    text-transform:uppercase;font-weight:600;margin-bottom:6px;">
            {label}
        </div>
        <div style="color:{color};font-size:2rem;font-weight:700;line-height:1.1;">
            {value}
        </div>
        <div style="color:#8b949e;font-size:0.78rem;margin-top:4px;">
            {sub}
        </div>
    </div>
    """, unsafe_allow_html=True)

kpi_card(col1, "Total Actions",  f"{board['actions_in_period'].iloc[0]:,}",       "Over 120 days",                              "#ff6b6b", "rgba(255,107,107,0.35)")
kpi_card(col2, "Active Cards",   f"{board['active_cards_in_period'].iloc[0]}",     f"of {board['card_count'].iloc[0]} total",    "#43d98c", "rgba(67,217,140,0.35)")
kpi_card(col3, "Active Members", f"{board['active_members_in_period'].iloc[0]}",   f"of {board['member_count'].iloc[0]} on board","#4ecdc4", "rgba(78,205,196,0.35)")
kpi_card(col4, "Checklist Done", "536",                                             "completions",                                "#f4e06d", "rgba(244,224,109,0.35)")
kpi_card(col5, "Card Moves",     "298",                                             "across lists",                               "#a78bfa", "rgba(167,139,250,0.35)")
kpi_card(col6, "Comments",       "30",                                              "total posted",                               "#43d98c", "rgba(67,217,140,0.35)")

### Step 6 — Sidebar filters


with st.sidebar: # left sidebar for filters
    st.header("🔧 Filters")
    
    date_range = st.date_input(
        "Date Range",
        [daily["activity_day"].min(), daily["activity_day"].max()]
    ) # Data Range filter 
    
    selected_members = st.multiselect(
        "Members",
        options=members["member_name"].tolist(),
        default=members[members["total_actions"] > 0]["member_name"].tolist()
    ) # member name filter
    
    selected_lists = st.multiselect(
        "Card Lists",
        options=cards["current_list"].unique().tolist(),
        default=cards["current_list"].unique().tolist()
    ) # card list filter  

# Apply filters
daily_filtered = daily[
    (daily["activity_day"] >= pd.Timestamp(date_range[0])) &
    (daily["activity_day"] <= pd.Timestamp(date_range[1]))
]
members_filtered = members[members["member_name"].isin(selected_members)]
cards_filtered   = cards[cards["current_list"].isin(selected_lists)]



### Step 7 — Daily activity timeline (Plotly)

st.subheader("📈 Daily Activity Over Time")

daily_sorted = daily_filtered.sort_values("activity_day")

fig_timeline = go.Figure() # create a new figure for the timeline plot

 # create a scatter plot trace for total actions
fig_timeline.add_trace(go.Scatter(
    x=daily_sorted["activity_day"], y=daily_sorted["total_actions"],
    name="Total Actions", fill="tozeroy", # name is legend label 
    line=dict(color="#6c8fff", width=2), # line color and width
    fillcolor="rgba(108,143,255,0.1)"  # Area color 
))

# create a scatter plot trace for checklist completions
fig_timeline.add_trace(go.Scatter(
    x=daily_sorted["activity_day"], y=daily_sorted["checklist_completions"],
    name="Checklist Completions",
    line=dict(color="#ffe66d", width=1.5),
    fillcolor="rgba(255,230,109,0.06)", fill="tozeroy"
))

# Blue Line = Total Actions per Day
# Yellow Line = Checklist Completions per Day

# create a scatter plot trace for card moves

# update_layout() graph ki styling, height, theme aur legend position
fig_timeline.update_layout(
    template="plotly_dark", height=250,
    margin=dict(l=0, r=0, t=10, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02)
)
# displaying charts on streamlit dashboard with use_container_width=True 
st.plotly_chart(fig_timeline, use_container_width=True)


### Step 8 — Donut charts (action categories + card status)


col_a, col_b = st.columns(2)

with col_a: # left column for action categories donut chart
    st.subheader("🍩 Action Categories")
    cat_counts = events["activity_category"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]
    
    #create a pie chart using Plotly Express with a hole in the center (donut chart)
    fig_cat = px.pie(cat_counts, names="category", values="count",
                     hole=0.6, template="plotly_dark",
                     color_discrete_sequence=px.colors.qualitative.Bold)
    # Chart appearance getting customize 
    fig_cat.update_layout(margin=dict(l=0,r=0,t=10,b=0), height=300) # margin and height of the chart
    st.plotly_chart(fig_cat, use_container_width=True) # displaying on streamlit dashboard 

with col_b:# right column for card status donut chart 
    st.subheader("🃏 Card Status Distribution")
    list_counts = cards_filtered["current_list"].value_counts().reset_index()
    list_counts.columns = ["list", "count"]
    
    fig_list = px.pie(list_counts, names="list", values="count",
                      hole=0.6, template="plotly_dark",
                      color_discrete_sequence=["#a78bfa","#43d98c","#6c8fff","#ff6b6b"])
    fig_list.update_layout(margin=dict(l=0,r=0,t=10,b=0), height=300)
    st.plotly_chart(fig_list, use_container_width=True) # displaying on streamlit dashboard 


### Step 9 — Member leaderboard (interactive table)


st.subheader("🏆 Member Leaderboard")

active = members_filtered[members_filtered["total_actions"] > 0].copy() # create a copy of the filtered members & stored in dataframe where total_actions > 0)
active["efficiency"] = (active["total_actions"] / active["active_days"].clip(lower=1)).round(1) # if anyone has activedays 0 then it will be 1 
active["share_%"] = (active["total_actions"] / active["total_actions"].sum() * 100).round(1)

st.dataframe(
    active[["member_name","total_actions","active_days","unique_cards_touched",
            "checklist_completions","card_moves_detected","comments","efficiency","share_%"]]
    .sort_values("total_actions", ascending=False)
    .reset_index(drop=True),
    use_container_width=True,
    # Customize the column headers and formats for the displayed dataframe
    column_config={
        "total_actions":   st.column_config.NumberColumn("Actions",    format="%d"),
        "active_days":     st.column_config.NumberColumn("Days"),
        "efficiency":      st.column_config.NumberColumn("Actions/Day", format="%.1f"),
        "share_%":         st.column_config.ProgressColumn("Share %", min_value=0, max_value=100),
    },
    hide_index=True
)


### Step 10 — Top cards horizontal bar chart


st.subheader("📌 Top 10 Most Active Cards")

top_cards = (cards_filtered
    .nlargest(10, "actions_in_period") # on the basis of actions_in_period column, select top 10 rows
    [["card_name","current_list","actions_in_period","updates","comments","moves_detected"]] # select only these columns from the dataframe
)


fig_cards = go.Figure() # create a new figure for the top cards bar chart

# Card Activity Breakdown (Updates vs Moves vs Comments)
fig_cards.add_trace(go.Bar(y=top_cards["card_name"], x=top_cards["updates"],
    orientation='h', name='Updates', marker_color='#6c8fff'))
fig_cards.add_trace(go.Bar(y=top_cards["card_name"], x=top_cards["moves_detected"],
    orientation='h', name='Moves', marker_color='#ff6b6b'))
fig_cards.add_trace(go.Bar(y=top_cards["card_name"], x=top_cards["comments"],
    orientation='h', name='Comments', marker_color='#4ecdc4'))
# autorange='reversed' active card diaplay on top of the chart
# update_layout used for customizing the chart layout 
fig_cards.update_layout(
    barmode='stack', template='plotly_dark', height=400,
    margin=dict(l=0,r=0,t=10,b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    yaxis=dict(autorange="reversed")
)
st.plotly_chart(fig_cards, use_container_width=True) # display on streamlit dashboard


### Step 11 — Monthly activity heatmap
# It displays how many actions were performed in each week of each month 

st.subheader("🗓️ Monthly Activity Heatmap")

daily_sorted = daily_filtered.copy() # creating duplicate dataframeto avoid modifying the original filtered dataframe
daily_sorted["month"] = daily_sorted["activity_day"].dt.strftime("%b %Y") # month year 
daily_sorted["week_of_month"] = ((daily_sorted["activity_day"].dt.day - 1) // 7) + 1

heat_pivot = daily_sorted.pivot_table(
    index="month", columns="week_of_month",
    values="total_actions", aggfunc="sum"
).fillna(0)
# imshow() matrix/table convert into color based visualization 
fig_heat = px.imshow(
    heat_pivot,
    color_continuous_scale="Blues",
    template="plotly_dark",
    labels=dict(x="Week of Month", y="Month", color="Actions"),
    aspect="auto"
)
# graph appearance customize using update_layout() function
fig_heat.update_layout(height=250, margin=dict(l=0,r=0,t=10,b=0))
st.plotly_chart(fig_heat, use_container_width=True)



### Step 12 — Member efficiency scatter

# st.subheader("⚡ Member Efficiency vs. Breadth")

# active["size"] = active["unique_cards_touched"].clip(lower=1)
# fig_scatter = px.scatter(
#     active[active["total_actions"] > 0],
#     x="active_days", y="total_actions",
#     size="size", color="member_name",
#     hover_data=["checklist_completions","card_moves_detected"],
#     template="plotly_dark", labels={"active_days":"Active Days","total_actions":"Total Actions"},
#     size_max=40
# )
# fig_scatter.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0), showlegend=False)
# st.plotly_chart(fig_scatter, use_container_width=True)

# #scatter chart (bubble chart) 

# # active days vs total actions
# # actions per day vs unique cards touched
# # Total no of cards touched vs total actions

st.subheader("🟣 Member Efficiency (Actions per Active Day)")

# Efficiency Calculation
active = members_filtered[members_filtered["total_actions"] > 0].copy()

active["efficiency"] = (
    active["total_actions"] /
    active["active_days"].clip(lower=1)
).round(1)

# Sort by efficiency
active = active.sort_values("efficiency", ascending=False)

# Color logic
colors = [
    "#ff6b6b" if x >= 20
    else "#f4e06d" if x >= 10
    else "#43d98c"
    for x in active["efficiency"]
]

# Bar Chart
fig_efficiency = go.Figure()

fig_efficiency.add_trace(
    go.Bar(
        x=active["member_name"],
        y=active["efficiency"],
        marker_color=colors,
        text=active["efficiency"],
        textposition="outside"
    )
)

fig_efficiency.update_layout(
    template="plotly_dark",
    height=350,
    title="Member Efficiency (Actions per Active Day)",
    xaxis_title="Members",
    yaxis_title="Actions per Active Day",
    margin=dict(l=0, r=0, t=40, b=0),
    showlegend=False
)

st.plotly_chart(
    fig_efficiency,
    use_container_width=True
)

