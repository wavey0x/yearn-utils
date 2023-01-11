from brownie import Contract, accounts, chain, LossOnFeeChecker, web3
import pytest

def test_helper(helper):
    vault = Contract('0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE', owner=web3.ens.resolve('ychad.eth'))
    decimals = vault.decimals()
    amount = 1_000_000 * 10 ** decimals

