import pickle
from pathlib import Path

from consts import *
import hopsworks
from tensorflow.python.keras import models
from utils.scrape_oddsportal import scrape_upcoming

from utils.BackTest import *
from utils.Hopsworks import get_football_featureview

LOCAL = False

if not LOCAL:
    import modal

    stub = modal.Stub(
        "scarping-upcoming",
        image=(
            modal.Image.from_dockerfile("dockerfiles/Dockerfile_scraper")
            .conda_install("cudatoolkit=11.2", "cudnn=8.1.0", "cuda-nvcc", channels=["conda-forge", "nvidia"])
            .pip_install("tensorflow~=2.9.1", "selenium==3.141", "numpy", " pandas", "trueskill", "hopsworks",
                         "scikit-learn", "matplotlib")
        ),
    )


    @stub.function(timeout=1200, schedule=modal.Period(days=1), secret=modal.Secret.from_name("HOPSWORKS_API_KEY"))
    def run():
        run_scrape()


def run_scrape():
    project = hopsworks.login()
    # fs is a reference to the Hopsworks Feature Store
    mr = project.get_model_registry()
    # Create an entry in the model registry that includes the model's name, desc, metrics

    hopsworks_model = mr.get_best_model(name="model_football", metric="date_run", direction="max")
    model_dir = Path(hopsworks_model.download())

    model = models.load_model(model_dir / 'model')
    with open(model_dir / 'scaler.pickle', "rb") as file:
        scaler = pickle.load(file)

    with open(model_dir / 'evaluator.pickle', "rb") as file:
        evaluator = pickle.load(file)

    # fs is a reference to the Hopsworks Feature Store
    fs = project.get_feature_store()
    # # get featureview
    feature_view = get_football_featureview(fs)
    past_data, _ = feature_view.training_data()
    # get featureview
    feature_view = get_football_featureview(fs)

    fg_upcoming = fs.get_or_create_feature_group(
        name="fg_upcoming",
        version=FG_UPCOMING_VERSION,
        primary_key=KEY_COLUMNS,
        event_time=['date'],
        description="Football data")

    past_games, _ = feature_view.training_data()
    country, league = 'england', 'premier-league'
    upcoming = scrape_upcoming(country, league, past_games)
    upcoming = upcoming[ALL_COLUMNS]

    print(upcoming)

    X_upcoming = upcoming[X_COLUMNS].copy()
    X_upcoming[X_SCALE_COLUMNS] = scaler.transform(X_upcoming[X_SCALE_COLUMNS])

    predictions = model.predict(X_upcoming)
    predicted_percentages = Games(*predictions.T)
    buy_sig = evaluator.generate_buy_signals(predicted_percentages)
    upcoming["h_buy"] = buy_sig.home
    upcoming["d_buy"] = buy_sig.draw
    upcoming["a_buy"] = buy_sig.away
    upcoming["h_predicted"] = predicted_percentages.home
    upcoming["d_predicted"] = predicted_percentages.draw
    upcoming["a_predicted"] = predicted_percentages.away

    fg_upcoming.insert(upcoming)


if __name__ == '__main__':
    if LOCAL:
        run_scrape()
    else:
        print("Running on Modal!")
        with stub.run():
            run.call()
