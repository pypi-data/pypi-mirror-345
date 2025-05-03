import pytest
from datetime import datetime, timedelta

def test_lucca_api():

    from chargedPlanner.LuccaAPI import LuccaAPI

    l = LuccaAPI()

    lucca_ID = 33

    data = []
    # url = ("?leavePeriod.ownerId=" + str(lucca_ID) + "&date=between," +
    #        str(datetime(2025, 4, 20).date()) + "," +
    #        str(datetime(2025, 4, 25).date()))
    #
    # ans = l.__post__(url)

    # print(ans)

    for i in range(5) :
        ans = l.getLeaves(
            lucca_ID,
            start_date= datetime(2025, 1, 1).date(),
            end_date= datetime(2025, 12, 30).date()
        )
