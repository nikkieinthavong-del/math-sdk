POKÉ-VICE ACADEMY
"Gotta Catch These Hands"
======================

A darkly comedic, adult-parody slot game featuring washed-up, dysfunctional pocket monsters
attending mandatory rehabilitation at the worst-rated training facility in the region.

GAME SPECIFICATIONS
-------------------
- Grid: 6x5 Cluster Pays
- Win Type: Cluster (min 5 matching symbols)
- Max Win: 10,000x
- Target RTPs: 94%, 96%, 98%
- Volatility: 8.5/10 (High-Very High)
- Hit Frequency: ~28% (every 3.5 spins)

CORE MECHANICS
--------------
1. REPUTATION DECAY CASCADE™
   - Winning symbols degrade through tiers instead of exploding
   - Legendary → Evolved → Basic → Egg
   - Creates chain reactions as symbols transform
   - Only Egg symbols actually disappear

2. ADDICTION METER™
   - Dynamic volatility system (0-100%)
   - Fills +10% per cascade win
   - Decays -5% per non-winning spin
   - Thresholds:
     * 25%: "Buzzed" - 2x multiplier
     * 50%: "Tipsy" - 3x multiplier
     * 75%: "Wasted" - 5x multiplier
     * 100%: "Blackout" - 10x multiplier + feature upgrade

3. BONUS FEATURES
   - 3 EGG Scatters: REHAB BONUS (Pokéhab Center)
     * 3x1 reel with 5 Pokéball throws
     * Catch Pokémon targets for multiplied wins
     * Average win: ~75-150x

   - 4 EGG Scatters: BATTLE BONUS (Dysfunction Duel)
     * RPG-style battle with 3x1 attack reel
     * 4 rounds of opponents
     * Progressive multiplier system
     * Mega win potential: 1,000x-5,000x

SYMBOLS
-------
Premium:
- DEPR (Depresso): 150x cluster
- RAGE (RageApe): 100x cluster
- SLAK (Slak-Addict): 75x cluster
- KARE (Karena): 50x cluster

Mid:
- METH (Methadone-Pod): 30x cluster
- CIGA (Cigar-itt): 25x cluster

Low:
- BEER (Beer Bottle): 15x cluster
- PILL (Pill Bottle): 12x cluster
- CIGT (Cigarette): 10x cluster
- TICK (Parking Ticket): 8x cluster

Special:
- WILD: Therapy Couch (substitutes all except scatter)
- EGG: Abandoned Egg (scatter, triggers bonuses)

FILES
-----
- game_config.py: Game configuration (symbols, paytables, bonuses)
- game_calculations.py: Reputation Decay Cascade logic
- game_executables.py: Main game loop and RGS integration
- gamestate.py: State management
- game_events.py: Event emission for frontend
- game_override.py: State overrides
- game_optimization.py: RTP optimization targets
- rehab_bonus.py: 3-scatter bonus mechanics
- battle_bonus.py: 4-scatter bonus mechanics
- run.py: Simulation script (run 10M+ spins for validation)
- reels/BR0.csv: Base game reel strip
- reels/FR0.csv: Bonus game reel strip

RUNNING SIMULATIONS
-------------------
python games/pokevice_academy/run.py

This will:
1. Run base game simulations (1M spins)
2. Run bonus simulations (100K triggers)
3. Optimize symbol weights for target RTP
4. Generate analysis reports
5. Verify RGS compliance

RESULTS
-------
Results will be written to:
- artifacts/pokevice_academy/: Simulation data
- Output RTP, hit frequency, bonus trigger rates
- Detailed win distribution analysis

FRONTEND INTEGRATION
--------------------
TypeScript engine files (to be implemented):
- GameEngine.ts: Core game engine
- ClusterMorphCascade.ts: Frontend cascade animations
- AddictionMeter.ts: Meter UI and effects
- RehabController.ts: Rehab bonus UI
- BattleController.ts: Battle bonus UI

DEVELOPMENT STATUS
------------------
✓ Math engine complete
✓ Bonus mechanics complete
✓ State management complete
✓ Reel strips created
⧗ TypeScript frontend engine (pending)
⧗ Simulations and validation (pending)

TARGET LAUNCH
-------------
~12 weeks from GDD to live (estimated)
