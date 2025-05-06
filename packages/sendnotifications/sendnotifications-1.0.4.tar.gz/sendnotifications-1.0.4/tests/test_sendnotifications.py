import pytest

from sendnotifications.sendonteams import NotifyMsTeams
from sendnotifications.sendonemail import NotifyEmail



def test_sendnotifications():
     messages = []
     messages.append("New adaptive card")
     messages.append("New method of message on teams channel")
     NotifyMsTeams("dba-only",messages,"Title - Testing card")
     NotifyEmail("Title - Testing card",messages,"vthelu")
     print ("notifyt response:{}, notifye response{}".format(notifyt,notifye))


if __name__ == "__main__":
     pytest.main()