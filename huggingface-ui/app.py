import pandas as pd
import streamlit as st
import json
from datetime import datetime, timedelta
from pathlib import Path
import hopsworks

CACHE_TTL = 60 * 60


@st.cache(ttl=CACHE_TTL)
def download_data():
    print("Logging it")
    project = hopsworks.login()
    print("Getting feature store")
    fs = project.get_feature_store()
    print("Getting feature group")
    fg = fs.get_feature_group("fg_upcoming", version=2)
    print("Creating query")
    query = fg.select_all()
    print("Executing query")
    upcoming = query.read()
    upcoming['date'] = pd.to_datetime(upcoming['date'])
    upcoming = upcoming[upcoming['date'] > datetime.now()]

    print("Getting model registry")
    mr = project.get_model_registry()
    print("Getting model")
    model = mr.get_best_model(name="metrics_football", metric="date_run", direction="max")
    print("Downloading model")
    model_dir = Path(model.download())
    print(model_dir)
    with open(model_dir / "metrics.json") as file:
        metrics = json.load(file)
    return metrics, upcoming, datetime.now()


metrics, upcoming, data_updated = download_data()
upcoming = upcoming.copy()

model_trained_date = datetime.fromtimestamp(metrics['date_run'])
win_percentage = metrics['win_percentage']
bet_count = metrics['bet_count']
win_count = metrics['bet_winning']
loose_count = metrics['bet_loosing']
backtest_start = datetime.fromtimestamp(metrics['first_date'])
backtest_end = datetime.fromtimestamp(metrics['last_date'])
roi = metrics['roi']

st.write("""
# Football predictions
## Upcoming matches:
""")

buy_col = []
calculated_at_odds = []
upcoming['date_str'] = upcoming['date'].dt.strftime('%d/%m/%Y')
upcoming = upcoming.sort_values(by=["date"])
upcoming = upcoming.reset_index(drop=True)
for row in upcoming.itertuples():
    if row.h_buy:
        buy_col.append(row.h_team)
        calculated_at_odds.append(str(round(1 / row.ho_pinnacle, 2)))
    elif row.a_buy:
        buy_col.append(row.a_team)
        calculated_at_odds.append(str(round(1 / row.ao_pinnacle, 2)))
    elif row.d_buy:
        buy_col.append("Draw")
        calculated_at_odds.append(str(round(1 / row.do_pinnacle, 2)))
    else:
        buy_col.append("No bet")
        calculated_at_odds.append("--")

column_rename = {
    "date_str": "Date",
    "h_team": "Home Team",
    "a_team": "Away Team",
}

table_data = upcoming[column_rename.keys()]
table_data.columns = map(column_rename.get, table_data.columns)
table_data["Bet on:"] = buy_col
table_data["With odds:"] = calculated_at_odds
table_data = table_data.style.set_properties(subset=["Bet on:"], **{'font-weight': 'bold'})

st.table(table_data)

st.write("""
## Backtesting results:
""")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Bets total:", value=bet_count)
with col2:
    st.metric(label="Winning bets:", value=win_count)
with col3:
    st.metric(label="Loosing bets:", value=loose_count)
with col4:
    st.metric(label="ROI:", value=f"{round(roi, 1)}%")

chart_data = pd.DataFrame(
    metrics['money_chart']['money'],
    index=[datetime.fromtimestamp(t) for t in metrics['money_chart']['date']],
    columns=['Return %'])

st.line_chart(chart_data)

st.text(f"Model trained on {model_trained_date.strftime('%d/%m/%Y at %H:%M')}")
st.text(f"Data downloaded on {data_updated.strftime('%d/%m/%Y at %H:%M')}")
