"""
Main simulation script for Poké-Vice Academy

Runs simulations, optimizations, and analysis for the game.
Target RTPs: 94%, 96%, 98%
Max Win: 10,000x
"""

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    # Simulation parameters
    num_threads = 10
    rust_threads = 20
    batching_size = 50000
    compression = True
    profiling = False

    # Number of simulations
    # Recommended: 10M for final validation, 1M for testing
    num_sim_args = {
        "base": int(1e6),      # 1M base game spins
        "bonus": int(1e5),     # 100K bonus triggers
    }

    # What to run
    run_conditions = {
        "run_sims": True,
        "run_optimization": True,
        "run_analysis": True,
        "run_format_checks": True,
        "run_bonus_sims": True,  # Simulate both bonuses separately
    }

    target_modes = ["base"]

    # Initialize game
    config = GameConfig()
    gamestate = GameState(config)

    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    # Run base game simulations
    if run_conditions["run_sims"]:
        print("=" * 60)
        print("POKÉ-VICE ACADEMY - Simulation Starting")
        print("=" * 60)
        print(f"Base Game Spins: {num_sim_args['base']:,}")
        print(f"Bonus Simulations: {num_sim_args['bonus']:,}")
        print(f"Target RTP: {config.rtp * 100}%")
        print(f"Max Win: {config.wincap:,}x")
        print("=" * 60)

        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

        print("\n✓ Base game simulations complete")

    # Simulate bonuses separately for detailed analysis
    if run_conditions["run_bonus_sims"]:
        print("\n" + "=" * 60)
        print("BONUS SIMULATIONS")
        print("=" * 60)

        from rehab_bonus import simulate_rehab_bonus
        from battle_bonus import simulate_battle_bonus

        # Rehab Bonus simulation
        print("\nSimulating Rehab Bonus (3-scatter)...")
        rehab_stats = simulate_rehab_bonus(config, num_simulations=10000)
        print(f"  Average Win: {rehab_stats['average_win']:.2f}x")
        print(f"  Min Win: {rehab_stats['min_win']:.2f}x")
        print(f"  Max Win: {rehab_stats['max_win']:.2f}x")
        print(f"  Average Catches: {rehab_stats['average_catches']:.1f}")
        print(f"  Win Distribution:")
        for range_name, count in rehab_stats['win_distribution'].items():
            print(f"    {range_name}: {count}")

        # Battle Bonus simulation
        print("\nSimulating Battle Bonus (4-scatter)...")
        battle_stats = simulate_battle_bonus(config, num_simulations=1000)
        print(f"  Average Win: {battle_stats['average_win']:.2f}x")
        print(f"  Min Win: {battle_stats['min_win']:.2f}x")
        print(f"  Max Win: {battle_stats['max_win']:.2f}x")
        print(f"  Final Victory Rate: {battle_stats['final_victory_rate'] * 100:.1f}%")
        print(f"  Average Rounds Completed: {battle_stats['average_rounds_completed']:.1f}")
        print(f"  Win Distribution:")
        for range_name, count in battle_stats['win_distribution'].items():
            print(f"    {range_name}: {count}")

        print("\n✓ Bonus simulations complete")

    # Generate config files
    generate_configs(gamestate)

    # Run optimization
    if run_conditions["run_optimization"]:
        print("\n" + "=" * 60)
        print("OPTIMIZATION")
        print("=" * 60)
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)
        print("✓ Optimization complete")

    # Generate analysis
    if run_conditions["run_analysis"]:
        print("\n" + "=" * 60)
        print("ANALYSIS")
        print("=" * 60)
        custom_keys = [
            {"symbol": "scatter"},
            {"symbol": "EGG"},
            {"addiction_meter": "thresholds"}
        ]
        create_stat_sheet(gamestate, custom_keys=custom_keys)
        print("✓ Analysis complete")

    # Verification tests
    if run_conditions["run_format_checks"]:
        print("\n" + "=" * 60)
        print("VERIFICATION")
        print("=" * 60)
        execute_all_tests(config)
        print("✓ Verification complete")

    print("\n" + "=" * 60)
    print("POKÉ-VICE ACADEMY - Simulation Complete!")
    print("=" * 60)
    print(f"\nResults written to: {config.output_path}")
    print(f"Artifacts: {config.artifacts_path}")
