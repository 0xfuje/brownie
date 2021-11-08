from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
    get_contract,
)
from brownie import network, exceptions
from scripts.deploy_lottery import deploy_lottery
from web3 import Web3
import pytest


def only_local():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()


def test_get_entrance_fee():
    only_local()
    # Arrange
    lottery = deploy_lottery()
    # Act
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    print(lottery.getEntranceFee())
    # Assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    only_local()
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    only_local()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    only_local()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # Act
    lottery.endLottery({"from": account})
    # Assert
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    only_local()
    # Arrange
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=3), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=4), "value": lottery.getEntranceFee()})

    fund_with_link(lottery)

    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()

    tx = lottery.endLottery({"from": account})
    request_id = tx.events["RequestedRandomness"]["requestId"]
    STATIC_RNG = 1255
    # Act
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )

    # 999 % 3 = 0
    # Assert
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
