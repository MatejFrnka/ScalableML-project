Run pipelines in the following order:

1. `feature-pipeline-initial`
    * This pipeline is meant to be run locally to upload existing data to hopsworks
1. `training-pipeline`
    * This pipeline trains the model and uploads it to hopsworks
    * It should be re-run weekly to be retrained on the newest data
1. `feature-upcoming-pipeline`
    * This pipelines scrapes upcoming matches and predicts the outcomes. Requires model to be uploaded in hopsworks
    * It should be run often, at least once a day
1. `feature-past-pipeline`
    * This pipelines scrapes results of games
    * It should be run weekly before model is retrained
1. The ui
    * UI requires `training-pipeline` and `feature-upcoming-pipeline`

`feature-upcoming-pipeline` and `feature-past-pipeline` require selenium and webdriver.