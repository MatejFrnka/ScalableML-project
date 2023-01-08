from consts import *
import hopsworks
from utils.ScrapeOddsportal import scrape_historical

from utils.Hopsworks import get_football_featureview, get_football_featuregroup

LOCAL = False

if not LOCAL:
    import modal

    stub = modal.Stub(
        "scarping-past",
        image=(
            modal.Image.from_dockerfile("dockerfiles/Dockerfile_scraper")
            .conda_install("cudatoolkit=11.2", "cudnn=8.1.0", "cuda-nvcc", channels=["conda-forge", "nvidia"])
            .pip_install("tensorflow~=2.9.1", "selenium==3.141", "numpy", " pandas", "trueskill", "hopsworks",
                         "scikit-learn", "matplotlib")
        ),
    )


    @stub.function(timeout=1200, schedule=modal.Period(days=7), secret=modal.Secret.from_name("HOPSWORKS_API_KEY"))
    def run():
        run_scrape()


def run_scrape():
    project = hopsworks.login()
    # fs is a reference to the Hopsworks Feature Store
    fs = project.get_feature_store()
    # # get featureview
    feature_view = get_football_featureview(fs)
    fg_football = get_football_featuregroup(fs)

    feature_view.delete_all_training_datasets()
    historical, _ = feature_view.training_data()



    country, league = 'england', 'premier-league'
    past = scrape_historical(country, league, historical)
    past = past[ALL_COLUMNS]

    fg_football.insert(past)


if __name__ == '__main__':
    if LOCAL:
        run_scrape()
    else:
        print("Running on Modal!")
        with stub.run():
            run.call()
