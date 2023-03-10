```diff
- The scraper no longer works because the scraped website has been changed
```

# **<p style="text-align: center;font-style: italic;">Beating the Bookies using Neural Networks</p>**
## **<p style="text-align: center;">ID2223 Project</p>**
## **<p style="text-align: center;">HT 2022</p>**  


<br/><br/>
<br/><br/>
## <p style="text-align: center;">Authors: **Daniel Workinn & Matej Frnka**</p> 
## <p style="text-align: center;">January 2022</p> 

<br/><br/>
<br/><br/>
<br/><br/> 

## 1. Introduction

For this project, we set out to beat online bookmakers in prediction outcomes of football games. In the last two decades, online sports betting has become a huge industry, replacing most of the traditional, physical form, of placing bets on sports events. By the growth of this industry, the bookmaker's process of setting odds for sports events has become increasingly sophisticated. Today, in 2023, most if not all bookmakers rely on machine learning models for setting odds as well as some function of "wisdom of the crowd". The latter part refers to the bookmakers changing the odds depending on the amount of money wagered on specific outcomes, which both improves their odds setting, in terms of reflecting underlying probability of outcomes, as well as manages bookmakers risk for specific outcomes. The result of this odds setting process is very accurate odds being offered. Out of all of the online bookmakers, Pinnacle stands out in terms of accuracy of their odds setting. They are good enough to earn the reputation within betting circles as being the "true odds" for a sports event.  

In this project, we try to further improve the odds offered by Pinnacle. This is done by scraping the results of football games, as well as the odds offered by Pinnacle, creating new features using this data and training a Neural Network for the task. All data used in the project is scraped from Oddsportal (found here: https://www.oddsportal.com/). The data as well as the trained model is uploaded to Hopsworks. Hopsworks is then connected with Streamlit hosting on which a Streamlit UI is built to showcase the performance of the model (found here: https://matejfrnka-scalableml-ui-app-mzih9s.streamlit.app/). In this UI, the performance of the model is shown both on offline test data (a hold outset of all of the data), as well as real-time predictions on upcoming matches and evaluation of those predictions once the match is finished. The real-time part, making predictions on upcoming matches and evaluating the results after the match is over, is achieved by continuously scraping Oddsportal for upcoming matches as well as contiuously updating the results of played matches by running the scraper on Modal. Once a new upcoming match is found on Oddsportal by Modal scraping it, Modal loads the model from Hopsworks, makes predictions (interference) and uploads the upcoming match and prediction to Hopsworks. When the game has been played, again Modal scrapes the results of the game, and evaluates the performance. Lastly, the Streamlit app grabs all predictions and performance of the model and displays it in the Streamlit UI. The full Github repository can be found here: https://github.com/MatejFrnka/ScalableML-project.

To run our code, please see **7. How to run**!

## 2. The Data

As previously stated, all data used for this project has been scraped from Oddsportal.com. The scraped dataset includes 150.000 football games, the results and bookmakers odds. From these 150.000 football games, only 111.000 include the odds given by Pinnacle. Since our goal of this project is to try to beat specifically Pinnacle, only these 111.000 games are used. A screenshot of the scraped data used for the project can be seen below:

![alt text](./images/id2223%20project%20data.png "Football Dataset")

Below is a short explaination of the columns:
* country: country of the league of the match
* league: league of the match
* h_team: home team in the match
* a_team: away team in the match
* date: date of the match
* time: time of the match
* fthg: full time home goals
* ftag: full time away goals
* h1thg: half time 1 home goals
* ht1ag: half time 1 away goals
* ht2hg: half time 2 home goals
* ht2ag: half time 2 away goals
* ho_pinnacle: home open odds of pinnacle
* do_pinnacle: draw open odds of pinnacle
* ao_pinnacle: away open odds of pinnacle

## 3. Feature Engineering

To help the model improve the odds offered of Pinnacle, new features were built using the scraped data. The features we created are introduced below.  

* Last odds: Odds for the Home and Away team from last time the teams met
* Win streak: The number of games consecutively won or lost for the Home and Away team before the current match
* Shock: How big of a suprise the result was of the X previous games for the Home and Away team
* Points: The number of "football points" (0 for loss, 1 for draw, 3 for win) the Home and Away team has earned in the X previous games
* Last full time results: The full time result for the Home and Away team the last time the teams met
* Realized EV: The probabilities summed together for the X previous games for the Home and Away team 

For some extra clarification, the Shock feature was calculated by taking into account the Pinnacle given probability of the teams to win as well as how many goals the teams scored. If a huge favorite loses 0:10 against an underdog, the Shock is a big negative number and vice versa. If a huge favorite wins 2:0 against an underdog, the Shock is a small positive number. Similarly, the Realized EV feature was calculated by summing the probability (given by Pinnacle) for the team to win, if the the won, and if the team lost summing 1 - the probability the for the team to win. Both Shock and Realized EV can be computed for a specified number of previous played games. In our case we used 1, 3 & 5 for Shock and 3, 5, 9 for Realized EV. A screenshot of the data with added features can be seen below:

![alt text](./images/id2223%20project%20data%20with%20features.png "Football Dataset")


## 4. Modeling

One of our goals of this project was to get practical experience with Neural Networks and therefore a Multi-layer Perpectron (MLP) Neural Network was chosen as the model for the task.  

Before starting experimenting with different configurations of the neural network, we did some data preprocessing. This started with creating target labels for the data. We used binary representation of the three outcomes, home win, draw, and away win ([1,0,0] for home win, [0,1,0] for draw and [0,0,1] for away win). Even though this task is a Multi-class Classification, we found that approaching the problem as a regression problem produced better results. For this reason, we use Mean Squared Error (MSE) as our loss function. The next step was to remove the oldest data, the oldest 10.000 matches. This was done because our added features had not converged to appropriate values yet, and the removal of data again improved the results. The next step was to scale the data using Scikit-learn's MinMaxScaler. The scaler was fitted on the training data and then used to transform the training, validation and testing data.  

The next step was to start testing different architectures of the MLP neural network. We tried different different number of hidden layers and different number of neurons in said layers. This was done in combination with testing different learning rates and applying regularization techniques such as Dropout regularization. The one thing that stayed constant was using the optimizer Adam, Relu as the activation function on the hidden layers and Softmax as the activation function on the output layer.  

Our final architecture consisted of 40 input neurons, two hidden layers of size 800 neurons each, and an output layer of 3 neruons (40x800x800x3).

## 5. Evaluation

To evaluate the performance of our model, we simulated betting on the testing data. This simulation consisted of only placing bets on matches if our model believed the chance of a team winning the game was more than 80%. We used a "flat bet" betting strategi, meaning we always bet 1 unit on each match. A plot of the Return of Investment (ROI) over games can be seen below:

![alt text](./images/id2223%20roi.png "Football Dataset")

The model placed roughly 200 bets on 10.000 matches and ended up with a -2.4% return of investment (ROI).

## 6. Conclusions

This project included many challenges. To name a few, scraping Oddsportal turned out to be nothing short than a nightmare. It was very time consuming having to browse individual webpages for each match. These pages also included Javascripts that had to be run to retrieve the required information. Setting up the scraper on Modal was also a challenge which included building a custom docker file with the necessary programs installed. Coming up with meaningful features was also hard since none of us had extensive knowledge about football from before the project. The result of the model, was as expected when we started the project, not very good - the online bookmakers are doing a very good job!

All in all, the project was very challenging and we learnt a lot!

## 7. How to run
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
