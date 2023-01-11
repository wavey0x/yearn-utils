from brownie import Contract, accounts, chain, ShareValueHelper, web3
import pytest

def test_helper(helper):
    vault = Contract('0xa354F35829Ae975e850e23e9615b11Da1B3dC4DE', owner=web3.ens.resolve('ychad.eth'))
    decimals = vault.decimals()
    amount = 1_000_000 * 10 ** decimals
    
    # Convert to shares
    shares_precise = helper.amountToShares(vault, amount)
    shares_imprecise = amount * 10**decimals // vault.pricePerShare()
    print(f'\n-- Converting {amount} tokens to shares --')
    print(f'Precise: {shares_precise}')
    print(f'Imprecise: {shares_imprecise}')

    # Convert to amount
    amount_precise = helper.sharesToAmount(vault, amount)
    amount_imprecise = vault.pricePerShare() * amount // 10**decimals
    print(f'\n-- Converting {amount} shares to underlying amount --')
    print(f'Precise: {amount_precise}')
    print(f'Imprecise: {amount_imprecise}')


    # Harvest a strategy so we can test during a locked profit scenario


    strategy = Contract('0x342491C093A640c7c2347c4FFA7D8b9cBC84D1EB', owner=web3.ens.resolve('ychad.eth'))
    assert strategy.estimatedTotalAssets() > 10**decimals
    strategy.harvest()
    pps = vault.pricePerShare()
    chain.sleep(60*60)
    chain.mine()
    assert pps < vault.pricePerShare()

    amount = 10_000e6
    tx = vault.deposit(amount)
    imprecise = int(amount * 10**decimals / vault.pricePerShare())
    expected = helper.amountToShares(vault, amount) # Must check this after the deposit so that calc is done at same block
    actual = tx.return_value
    print(f'\nExpected (via pps): {imprecise}')
    print(f'Expected (precise): {expected}')
    print(f'Actual: {actual}')
    assert expected == actual

    chain.sleep(60*60)
    chain.mine()
    amount = expected
    tx = vault.withdraw(amount)
    expected = helper.sharesToAmount(vault, amount)
    imprecise = int(amount * vault.pricePerShare() / 10**decimals)
    actual = tx.return_value
    print(f'\nExpected (via pps): {imprecise}')
    print(f'Expected (precise): {expected}')
    print(f'Actual: {actual}')
    assert expected == actual
    assert tx.return_value == expected

