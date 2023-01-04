import pandas as pd
import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from PIL import Image
import hopsworks

CACHE_TTL = 60 * 60


@st.cache(ttl=CACHE_TTL)
def download_model():
    project = hopsworks.login()
    fs = project.get_feature_store()
    mr = project.get_model_registry()
    model = mr.get_best_model(name="model_football", metric="date_run", direction="max")
    model_dir = Path(model.download())
    print(model_dir)
    with open(model_dir / "metrics.json") as file:
        metrics = json.load(file)
    training_image = Image.open(model_dir / 'training.png')
    return metrics, training_image


metrics, training_image = download_model()

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

st.write(f"Model trained on {model_trained_date.strftime('%d/%m/%Y at %H:%M')}")

st.image(training_image, caption="Model training")
