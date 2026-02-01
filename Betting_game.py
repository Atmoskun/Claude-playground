"""
Betting Game Simulation

This module simulates a betting game with configurable parameters and analyzes
the outcomes across multiple simulations. It uses a dynamic betting strategy
that switches from aggressive to conservative betting after a certain number of games.
"""

import random
import statistics
from dataclasses import dataclass
from typing import List, Tuple
import matplotlib.pyplot as plt


@dataclass
class GameConfig:
    """Configuration parameters for the betting game."""

    initial_stake: float = 100.0
    total_games: int = 100
    win_chance: float = 0.51
    bet_percent: float = 0.2
    payout_ratio: int = 2
    strategy_switch_point: int = 33  # Games remaining to switch to conservative betting
    num_simulations: int = 5000

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.initial_stake <= 0:
            raise ValueError("Initial stake must be positive")
        if not 0 < self.win_chance < 1:
            raise ValueError("Win chance must be between 0 and 1")
        if not 0 < self.bet_percent <= 1:
            raise ValueError("Bet percent must be between 0 and 1")
        if self.payout_ratio <= 0:
            raise ValueError("Payout ratio must be positive")
        if self.total_games <= 0:
            raise ValueError("Total games must be positive")
        if self.num_simulations <= 0:
            raise ValueError("Number of simulations must be positive")


class BettingSimulator:
    """Simulates betting games with configurable strategies."""

    def __init__(self, config: GameConfig):
        """
        Initialize the betting simulator.

        Args:
            config: Game configuration parameters
        """
        config.validate()
        self.config = config

    def run_one_simulation(self) -> float:
        """
        Simulate one complete game series.

        Returns:
            The final stake after all games (0.0 if bankrupt)
        """
        current_stake = self.config.initial_stake

        for game in range(self.config.total_games):
            remaining_games = self.config.total_games - game

            # Determine bet amount based on strategy
            bet_amount = self._calculate_bet(current_stake, remaining_games)

            # Play the game
            if random.random() < self.config.win_chance:
                # Win: get back the bet plus winnings
                current_stake += bet_amount * (self.config.payout_ratio - 1)
            else:
                # Lose: lose the bet amount
                current_stake -= bet_amount

            # Check for bankruptcy
            if current_stake <= 0:
                return 0.0

        return current_stake

    def _calculate_bet(self, current_stake: float, remaining_games: int) -> float:
        """
        Calculate the bet amount based on the current strategy.

        Args:
            current_stake: Current available stake
            remaining_games: Number of games remaining

        Returns:
            The bet amount for this game
        """
        if remaining_games > self.config.strategy_switch_point:
            # Aggressive strategy: divide stake evenly across remaining games
            return current_stake / remaining_games
        else:
            # Conservative strategy: bet a fixed percentage
            return current_stake * self.config.bet_percent

    def run_simulations(self) -> List[float]:
        """
        Run multiple simulations and collect results.

        Returns:
            List of final stakes from all simulations
        """
        print(f"Running {self.config.num_simulations} simulations...")

        final_stakes = []
        for _ in range(self.config.num_simulations):
            final_stake = self.run_one_simulation()
            final_stakes.append(final_stake)

        print("Simulations complete.")
        return final_stakes


class SimulationAnalyzer:
    """Analyzes and reports on simulation results."""

    def __init__(self, config: GameConfig, final_stakes: List[float]):
        """
        Initialize the analyzer.

        Args:
            config: Game configuration used for simulations
            final_stakes: Results from all simulations
        """
        self.config = config
        self.final_stakes = final_stakes

    def calculate_statistics(self) -> Tuple[float, float, float, int]:
        """
        Calculate key statistics from simulation results.

        Returns:
            Tuple of (average, median, bust_rate_percent, bust_count)
        """
        average = statistics.mean(self.final_stakes)
        median = statistics.median(self.final_stakes)
        bust_count = sum(1 for stake in self.final_stakes if stake == 0.0)
        bust_rate = (bust_count / len(self.final_stakes)) * 100

        return average, median, bust_rate, bust_count

    def print_results(self) -> None:
        """Print detailed simulation results to console."""
        average, median, bust_rate, _ = self.calculate_statistics()

        print("\n" + "=" * 50)
        print("STRATEGY RESULTS")
        print("=" * 50)
        print(f"Initial Stake:              ${self.config.initial_stake:.2f}")
        print(f"Games per Simulation:       {self.config.total_games}")
        print(f"Win Chance:                 {self.config.win_chance * 100}%")
        print(f"Conservative Bet Percent:   {self.config.bet_percent * 100}%")
        print(f"Payout Ratio:               {self.config.payout_ratio}:1")
        print(f"Strategy Switch Point:      {self.config.strategy_switch_point} games")
        print("-" * 50)
        print(f"Average Final Stake:        ${average:,.2f}")
        print(f"Median Final Stake:         ${median:,.2f}")
        print(f"Bankruptcy Rate:            {bust_rate:.2f}%")
        print("=" * 50)

    def plot_histogram(self, display_percentile: float = 0.95) -> None:
        """
        Create a histogram of the simulation results.

        Args:
            display_percentile: Percentile to use for x-axis range (default 0.95)
        """
        # Filter out bankruptcies for cleaner visualization
        winning_stakes = [stake for stake in self.final_stakes if stake > 0]

        if not winning_stakes:
            print("\nCannot plot histogram: all simulations went bust.")
            return

        print(f"\nGenerating histogram (showing {display_percentile * 100}% of results)...")

        # Calculate display range
        winning_stakes_sorted = sorted(winning_stakes)
        percentile_index = int(len(winning_stakes_sorted) * display_percentile)
        max_range = winning_stakes_sorted[percentile_index]

        # Calculate statistics for display
        average, median, bust_rate, _ = self.calculate_statistics()

        # Create the histogram
        plt.figure(figsize=(12, 7))
        plt.hist(winning_stakes, bins=100, range=(0, max_range),
                 edgecolor='black', alpha=0.7)

        plt.title(f"Distribution of Final Stakes ({self.config.num_simulations} simulations, excluding bankruptcies)",
                  fontsize=14, fontweight='bold')
        plt.xlabel("Final Stake ($)", fontsize=12)
        plt.ylabel("Frequency", fontsize=12)

        # Add summary statistics box
        summary_text = (
            f"Simulations: {self.config.num_simulations:,}\n"
            f"Display Range: {display_percentile * 100}%\n"
            f"Games per Simulation: {self.config.total_games}\n"
            f"Win Chance: {self.config.win_chance * 100}%\n"
            f"Conservative Bet: {self.config.bet_percent * 100}%\n"
            f"Payout Ratio: {self.config.payout_ratio}:1\n"
            f"Strategy Switch: {self.config.strategy_switch_point} games\n"
            f"{'─' * 25}\n"
            f"Initial Stake: ${self.config.initial_stake:.0f}\n"
            f"Bankruptcy Rate: {bust_rate:.1f}%\n"
            f"Median: ${median:,.0f}\n"
            f"Average: ${average:,.0f}"
        )

        plt.text(0.98, 0.98, summary_text,
                transform=plt.gca().transAxes,
                verticalalignment='top',
                horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
                fontfamily='monospace',
                fontsize=9)

        plt.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()

        # Save the figure
        output_file = 'betting_game_results.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"Histogram saved to: {output_file}")

        plt.show()


def main() -> None:
    """Main entry point for the betting game simulation."""
    # Configure the game parameters
    config = GameConfig(
        initial_stake=100.0,
        total_games=100,
        win_chance=0.51,
        bet_percent=0.2,
        payout_ratio=2,
        strategy_switch_point=33,
        num_simulations=5000
    )

    # Run simulations
    simulator = BettingSimulator(config)
    final_stakes = simulator.run_simulations()

    # Analyze and display results
    analyzer = SimulationAnalyzer(config, final_stakes)
    analyzer.print_results()
    analyzer.plot_histogram(display_percentile=0.95)


if __name__ == "__main__":
    main()
