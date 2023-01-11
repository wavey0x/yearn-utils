pragma solidity 0.8.6;

interface IVault {
    struct StrategyParams {
        uint performanceFee;
        uint activation;
        uint debtRatio;
        uint rateLimit;
        uint lastReport;
        uint totalDebt;
        uint totalGain;
        uint totalLoss;
    }
    function totalAssets() external view returns (uint);
    function managementFee() external view returns (uint);
    function performanceFee() external view returns (uint);
    function strategies(address) external view returns (StrategyParams memory);
}

interface IStrategy {
    function vault() external view returns (address);
}

/// @title LossOnFeeChecker
/// @notice Designed to prevent Management fees from creating lossy reports on Yearn vaults with API < 0.3.5
/// @dev Begining with vaults API v0.3.5 management fees are adjust dynamically on report to prevent loss
contract LossOnFeeChecker {

    uint constant MAX_BPS = 10_000;
    uint constant SECS_PER_YEAR = 31_557_600;

    /// @notice Check if harvest does not contain a loss after fees
    /// @dev should be called automically report transaction
    function isHealthy(uint gain, uint loss) external returns (bool) {
        _check(msg.sender, gain, loss);
    }

    /// @notice For testing amounts and strategies not directly on chain
    function testHealthy(address strategy, uint gain, uint loss) external returns (bool) {
        _check(strategy, gain, loss);
    }

    function _check(address _strategy, uint gain, uint loss) internal returns (bool) {
        if (loss > gain) return false;
        uint grossProfit = gain - loss;

        IStrategy strategy = IStrategy(_strategy);
        IVault vault = IVault(strategy.vault());

        uint managementFee = vault.managementFee();
        if (managementFee == 0) return true;

        uint totalAssets = vault.totalAssets();
        if (totalAssets == 0) return true;

        IVault.StrategyParams memory params = vault.strategies(msg.sender);
        uint timeSince = block.timestamp - params.lastReport;
        if (timeSince == 0) return true;
                
        uint governanceFee = (
            totalAssets * timeSince * managementFee
            / MAX_BPS
            / SECS_PER_YEAR
        );

        if (gain > 0) {
            uint strategistFeeAmount = gain * params.performanceFee / MAX_BPS;
            uint performanceFeeAmount = gain * vault.performanceFee() / MAX_BPS;
            governanceFee = governanceFee + strategistFeeAmount + performanceFeeAmount;
        }

        return grossProfit >= governanceFee;
    }
}

