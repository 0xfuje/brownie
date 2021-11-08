from brownie import network
import time
import pytest
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
)
from scripts.deploy_lottery import deploy_lottery


def skip_local():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()


def test_can_pick_winner():
    skip_local()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 1000000000})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 1000000000})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    time.sleep(60)
    winner = lottery.recentWinner()
    assert winner == account
    assert lottery.balance() == 0
