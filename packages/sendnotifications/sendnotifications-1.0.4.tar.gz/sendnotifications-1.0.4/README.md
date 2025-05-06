# sendnotifications

sendnotifications is a simple package that enables users to send notification to MSTeams or Email. The package is built using `urllib3` for distribution.

## Features

- Send notification on channel w/ adaptive card using NotifyMsTeams.
- Send notification on email using prefix of team name on attributes using NotifyEmail.


## Installation

This package will be made available as lambda layer
for email grant sns:publish, sns:createtopic on IAM Role

## Usage


### Example: Training and Making Predictions

```python
from sendnotifications import NotifyMsTeams, NotifyEmail

# Initialize the predictor

def testemail:
    messages = []
    messages.append("Test")
    messages.append("Test1")
    notifye = NotifyEmail("Title - Testing card",messages,"vthelu")
    notifyt = NotifyMsTeams("homes-analytics-alerts",messages,"Test Title",1,"warn")
    print ("notifyt response:{}, notifye response{}".format(notifyt, notifye))

```