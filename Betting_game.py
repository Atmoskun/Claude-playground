import random
import statistics
import matplotlib.pyplot as plt # --- NEW! ---

# --- 1. Set up the Game and Strategy Parameters ---

INITIAL_STAKE = 100.0
TOTAL_GAMES = 100
WIN_CHANCE = 0.51  
BET_PERCENT = 0.2   
PAYOUT_RATIO = 2
EOF_Strategy = 33 # Number of games to switch to conservative betting

# --- 2. Set up the Simulation Parameters ---

# How many times to run the 100-game series
NUM_SIMULATIONS = 5000

# --- 3. Define the function for a single 100-game series ---

def run_one_simulation():
    """
    Simulates one "lifetime" of 100 games.
    Returns the final stake.
    """
    current_stake = INITIAL_STAKE

    for game in range(TOTAL_GAMES):       
        remaining_games = TOTAL_GAMES - game
        # 1. Determine bet amount, 0 for dynamic betting
        if remaining_games > EOF_Strategy:
            bet_amount = current_stake / remaining_games
            # print(f"Game {game+1}: Betting ${bet_amount:.2f} in the current game. {remaining_games} games remaining.")
        else:
            bet_amount = current_stake * BET_PERCENT

        # 2. Play the game (win or lose)
        if random.random() < WIN_CHANCE:
            # WIN! (WIN_CHANCE)
            current_stake = current_stake - bet_amount + bet_amount * PAYOUT_RATIO
        else:
            # LOSE 
            current_stake = current_stake - bet_amount

        # 3. Check if bankrupt
        if current_stake <= 0:
            return 0.0

    # After 100 games, return the final amount
    return current_stake

# --- 4. Run the simulations and collect results ---

final_stakes = []
bust_count = 0

print(f"Running {NUM_SIMULATIONS} simulations...")

for i in range(NUM_SIMULATIONS):
    final_stake = run_one_simulation()    
    final_stakes.append(final_stake)
    if final_stake == 0.0:
        bust_count += 1

print("Simulations complete.")

# --- 5. Analyze and print the results ---

average_result = statistics.mean(final_stakes)
median_result = statistics.median(final_stakes) # The "middle" outcome
bust_chance = (bust_count / NUM_SIMULATIONS) * 100

print("\n--- Strategy Results ---")
print(f"Initial Stake: ${INITIAL_STAKE:.2f}")
print(f"Games Played (per simulation): {TOTAL_GAMES}")
print(f"Win Chance: {WIN_CHANCE * 100}%")
print(f"Bet Percent: {BET_PERCENT * 100}%")
print(f"Payout Ratio: {PAYOUT_RATIO}:1")
print("---------------------------------------------")
print(f"Average Final Stake: ${average_result:,.2f}")
print(f"Median (Typical) Final Stake: ${median_result:,.2f}")
print(f"Chance of going bust (stake <= $0): {bust_chance:.2f}%")


# --- 6. Plot the Results (Histogram) ---

# Filter out busts for a cleaner graph
winning_stakes = [stake for stake in final_stakes if stake > 0]

if not winning_stakes:
    print("\nCould not plot histogram: all simulations went bust.")
else:
    print("\nGenerating histogram of results (excluding busts)...")
    
    # Use numpy's percentile for simplicity (or manual calculation)
    Display_Range = 0.95
    winning_stakes_sorted = sorted(winning_stakes)
    percentile_index = int(len(winning_stakes_sorted) * Display_Range)
    max_range = winning_stakes_sorted[percentile_index]
    
    # Create the histogram
    plt.figure(figsize=(10, 6))
    plt.hist(winning_stakes, bins=100, range=(0, max_range), edgecolor='black')
    
    plt.title(f"Distribution of Final Stakes ({NUM_SIMULATIONS} simulations, excl. busts)")
    plt.xlabel("Final Stake ($)")
    plt.ylabel("Frequency")
    # plt.xscale('log')

    # Add summary text
    plt.text(0.98, 0.98, 
             f"Simulations: {NUM_SIMULATIONS}\n"
             f"Display Range: {Display_Range * 100}%\n"
             f"Number of Games in each simulation: {TOTAL_GAMES}\n"
             f"Win Chance: {WIN_CHANCE * 100}%\n"
             f"Bet: {BET_PERCENT * 100}%\n"
             f"Payout ratio: {PAYOUT_RATIO}:1\n"
             f"---\n"
             f"Initial Stake: ${INITIAL_STAKE:.0f}\n"
             f"Bust rate: {bust_chance:.1f}%\n"
             f"Median: ${median_result:,.0f}\n"
             f"Average: ${average_result:,.0f}",transform=plt.gca().transAxes, 
             verticalalignment='top', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.grid(axis='y', alpha=0.5)
    plt.tight_layout()
    plt.show()