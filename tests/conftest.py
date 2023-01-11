import pytest, brownie
from brownie import Contract, accounts, chain, ShareValueHelper
import pytest

@pytest.fixture
def helper(accounts):
    dev = accounts[0]
    yield dev.deploy(ShareValueHelper)

# @pytest.fixture
# def vault():
#     # USDC vault
#     yield Contract('0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE')