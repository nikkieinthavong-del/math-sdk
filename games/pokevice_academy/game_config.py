"""Poké-Vice Academy game configuration file"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Singleton Poké-Vice Academy configuration class."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "pokevice_academy"
        self.provider_number = 0
        self.working_name = "Poké-Vice Academy: Gotta Catch These Hands"
        self.wincap = 10000.0  # Max win: 10,000x
        self.win_type = "cluster"
        self.rtp = 0.9600  # Default to 96% (medium volatility)
        self.construct_paths()

        # Game Dimensions: 6x5 grid
        self.num_reels = 6
        self.num_rows = [5] * self.num_reels

        # Symbol definitions
        # PREMIUM SYMBOLS
        self.DEPRESSO = "DEPR"      # Psychic/Dark - Sad espresso cup
        self.RAGEAPE = "RAGE"        # Fighting - Roid-raging Primeape
        self.SLAK_ADDICT = "SLAK"    # Normal - Slakoth with track marks
        self.KARENA = "KARE"         # Fairy/Poison - Entitled Gardevoir

        # MID SYMBOLS
        self.METHADONE_POD = "METH"  # Steel/Poison - Medical vending machine
        self.CIGARITT = "CIGA"       # Fire - Chain-smoking Charmander

        # LOW SYMBOLS
        self.BEER_BOTTLE = "BEER"    # Poison - Empty 40oz
        self.PILL_BOTTLE = "PILL"    # Psychic - Prescription bottle
        self.CIGARETTE = "CIGT"      # Fire - Lit cigarette
        self.PARKING_TICKET = "TICK" # Fighting - Crumpled citation

        # SPECIAL SYMBOLS
        self.EGG_SCATTER = "EGG"     # Abandoned egg in dumpster
        self.THERAPY_WILD = "WILD"   # Worn leather couch

        # REPUTATION DECAY TIERS - Symbols degrade through tiers
        # Legendary → Evolved → Basic → Egg
        self.reputation_tiers = {
            # Premium degradation chains
            "DEPR": {"tier": 3, "downgrades_to": "RAGE", "tier_name": "Legendary"},
            "RAGE": {"tier": 2, "downgrades_to": "SLAK", "tier_name": "Evolved"},
            "SLAK": {"tier": 1, "downgrades_to": "KARE", "tier_name": "Basic"},
            "KARE": {"tier": 0, "downgrades_to": "EGG", "tier_name": "Egg-Ready"},

            # Mid degradation chains
            "METH": {"tier": 1, "downgrades_to": "CIGA", "tier_name": "Basic"},
            "CIGA": {"tier": 0, "downgrades_to": "EGG", "tier_name": "Egg-Ready"},

            # Low symbols degrade to egg directly
            "BEER": {"tier": 0, "downgrades_to": "EGG", "tier_name": "Egg-Ready"},
            "PILL": {"tier": 0, "downgrades_to": "EGG", "tier_name": "Egg-Ready"},
            "CIGT": {"tier": 0, "downgrades_to": "EGG", "tier_name": "Egg-Ready"},
            "TICK": {"tier": 0, "downgrades_to": "EGG", "tier_name": "Egg-Ready"},
        }

        # CLUSTER PAYTABLE
        # Format: (cluster_size_range, symbol) : payout_multiplier
        # Based on GDD cluster requirements
        t1, t2, t3, t4 = (5, 7), (8, 11), (12, 19), (20, 30)

        pay_group = {
            # DEPRESSO - Highest premium (150x for 15+)
            (t1, "DEPR"): 15.0,
            (t2, "DEPR"): 35.0,
            (t3, "DEPR"): 75.0,
            (t4, "DEPR"): 150.0,

            # RAGEAPE - Second premium (100x for 12+)
            (t1, "RAGE"): 10.0,
            (t2, "RAGE"): 25.0,
            (t3, "RAGE"): 50.0,
            (t4, "RAGE"): 100.0,

            # SLAK-ADDICT - Third premium (75x for 10+)
            (t1, "SLAK"): 7.5,
            (t2, "SLAK"): 18.0,
            (t3, "SLAK"): 37.5,
            (t4, "SLAK"): 75.0,

            # KARENA - Fourth premium (50x for 8+)
            (t1, "KARE"): 5.0,
            (t2, "KARE"): 12.5,
            (t3, "KARE"): 25.0,
            (t4, "KARE"): 50.0,

            # METHADONE-POD - Mid symbol (30x for 6+)
            (t1, "METH"): 3.0,
            (t2, "METH"): 7.5,
            (t3, "METH"): 15.0,
            (t4, "METH"): 30.0,

            # CIGAR-ITT - Mid symbol (25x for 6+)
            (t1, "CIGA"): 2.5,
            (t2, "CIGA"): 6.0,
            (t3, "CIGA"): 12.5,
            (t4, "CIGA"): 25.0,

            # BEER BOTTLE - Low symbol (15x for 5+)
            (t1, "BEER"): 1.5,
            (t2, "BEER"): 3.75,
            (t3, "BEER"): 7.5,
            (t4, "BEER"): 15.0,

            # PILL BOTTLE - Low symbol (12x for 5+)
            (t1, "PILL"): 1.2,
            (t2, "PILL"): 3.0,
            (t3, "PILL"): 6.0,
            (t4, "PILL"): 12.0,

            # CIGARETTE - Low symbol (10x for 5+)
            (t1, "CIGT"): 1.0,
            (t2, "CIGT"): 2.5,
            (t3, "CIGT"): 5.0,
            (t4, "CIGT"): 10.0,

            # PARKING TICKET - Low symbol (8x for 5+)
            (t1, "TICK"): 0.8,
            (t2, "TICK"): 2.0,
            (t3, "TICK"): 4.0,
            (t4, "TICK"): 8.0,
        }

        self.paytable = self.convert_range_table(pay_group)

        # Special symbols configuration
        self.include_padding = True
        self.special_symbols = {
            "wild": ["WILD"],  # Therapy Couch Wild - substitutes for all except scatter
            "scatter": ["EGG"]  # Egg Scatter - triggers bonuses
        }

        # ADDICTION METER CONFIGURATION
        # Dynamic volatility system that fills with cascade wins
        self.addiction_meter = {
            "max_value": 100,
            "fill_per_cascade": 10,  # Each cascade win adds 10%
            "decay_per_spin": 5,     # Meter decays 5% per non-winning spin
            "thresholds": {
                25: "buzzed",      # 2x wild multiplier spawns
                50: "tipsy",       # Random symbol morphs into wilds
                75: "wasted",      # Entire reel becomes sticky wild
                100: "blackout"    # Triggers random feature upgrade
            }
        }

        # BONUS TRIGGER CONFIGURATION
        # 3 Scatters = Rehab Bonus (Pokéhab Center)
        # 4 Scatters = Battle Bonus (Dysfunction Duel)
        self.rehab_bonus_triggers = {
            self.basegame_type: {3: "rehab_bonus"},
            self.freegame_type: {3: "rehab_bonus"}
        }

        self.battle_bonus_triggers = {
            self.basegame_type: {4: "battle_bonus"},
            self.freegame_type: {4: "battle_bonus"}
        }

        # Combined scatter triggers for RGS
        self.freespin_triggers = {
            self.basegame_type: {3: 1, 4: 1},  # 3 = rehab, 4 = battle
            self.freegame_type: {3: 1, 4: 1}
        }

        self.anticipation_triggers = {
            self.basegame_type: 2,  # Show anticipation at 2 scatters
            self.freegame_type: 2
        }

        # DYSFUNCTION WILDS CONFIGURATION
        self.dysfunction_wilds = {
            "narco_wild": {
                "symbol": "WILD_N",
                "behavior": "duplicate",
                "duplicate_count": (2, 4),  # Duplicates 2-4 times
                "trigger_chance": 0.15
            },
            "rage_wild": {
                "symbol": "WILD_R",
                "behavior": "convert_adjacent",
                "trigger_chance": 0.20
            },
            "crisis_wild": {
                "symbol": "WILD_C",
                "behavior": "become_any",
                "trigger_chance": 0.25
            },
            "therapy_wild": {
                "symbol": "WILD_T",
                "behavior": "paired",  # Requires 2 to activate
                "trigger_chance": 0.10
            }
        }

        # REHAB BONUS (3-SCATTER) CONFIGURATION
        self.rehab_bonus_config = {
            "throws": 5,  # 5 pokéball throws
            "reel_size": 3,  # 3x1 vertical reel

            # Target Pokémon grid with payouts
            "targets": [
                {"name": "SOBBLE-TER", "count": 1, "payout": 100.0},
                {"name": "SLAK-OFF", "count": 2, "payout": 50.0},
                {"name": "WHIS-MURRR", "count": 3, "payout": 25.0},
                {"name": "RATT-ITUDE", "count": 4, "payout": 15.0}
            ],

            # Pokéball types with catch rates
            "pokeballs": {
                "GREAT_BALL": {"catch_rate": 0.40, "multiplier": (3, 5)},
                "ULTRA_BALL": {"catch_rate": 0.60, "multiplier": (8, 12)},
                "MASTER_BALL": {"catch_rate": 1.00, "multiplier": (20, 50)},
                "BEER_BALL": {"catch_rate": 0.30, "multiplier": 2.0},
                "RESTRAINING_ORDER": {"effect": "add_throws", "bonus_throws": 2}
            },

            # 3x1 Reel composition weights
            "reel_weights": {
                "position_1": {  # Ball type
                    "GREAT_BALL": 40,
                    "ULTRA_BALL": 30,
                    "MASTER_BALL": 5,
                    "BEER_BALL": 20,
                    "RESTRAINING_ORDER": 5
                },
                "position_2": {  # Catch result
                    "CATCH": 45,
                    "MISS": 40,
                    "UPGRADE": 15
                },
                "position_3": {  # Multiplier
                    "1x": 40,
                    "2x": 25,
                    "3x": 15,
                    "5x": 12,
                    "10x": 8
                }
            }
        }

        # BATTLE BONUS (4-SCATTER) CONFIGURATION
        self.battle_bonus_config = {
            "starting_spins": 5,
            "player_pokemon": "DEPRESSO",
            "player_hp": 100,

            # Battle opponents in order
            "opponents": [
                {
                    "name": "INTERN_JENNY",
                    "hp": 80,
                    "attacks": [
                        {"name": "Overtime Burnout", "damage": 15},
                        {"name": "Coffee Withdrawal", "damage": 20}
                    ],
                    "defeat_reward": 50.0,
                    "bonus_spins": 3
                },
                {
                    "name": "OFFICER_GRUMPY",
                    "hp": 150,
                    "attacks": [
                        {"name": "Bribery Bite", "damage": 25},
                        {"name": "Warrant Strike", "damage": 35},
                        {"name": "Taser Fang", "damage": 45, "critical": True}
                    ],
                    "defeat_reward": 150.0,
                    "bonus_spins": 5
                },
                {
                    "name": "CHAMPION_KAREN",
                    "hp": 250,
                    "attacks": [
                        {"name": "Speak to Your Manager", "damage": 40, "stun": True},
                        {"name": "Lawsuit Lash", "damage": 50},
                        {"name": "Yelp Review", "damage": 30, "debuff": True}
                    ],
                    "defeat_reward": 500.0,
                    "bonus_spins": 10
                },
                {
                    "name": "PROFESSOR_REHAB",
                    "hp": 400,
                    "attacks": [
                        {"name": "Gaslighting Pulse", "damage": 35, "confusion": True},
                        {"name": "Prescription Overload", "damage": 60},
                        {"name": "Insurance Fraud", "damage": 80, "critical": True}
                    ],
                    "special_ability": "Therapy Bill",  # Deducts 50x every 3 turns
                    "defeat_reward": (1000.0, 5000.0),  # Range for mega win
                    "bonus_spins": 0
                }
            ],

            # Player attack moves
            "player_attacks": {
                "ANXIETY_ATTACK": {"damage": 15, "effect": "miss_chance_40"},
                "THERAPY_SLAP": {"damage": 25, "effect": "heal_5"},
                "PRESCRIPTION_PUNCH": {"damage": 35, "effect": "charge_2_turns"},
                "EXISTENTIAL_CRISIS": {"damage": 50, "hit_rate": 0.10, "critical": True},
                "SARCASM_BLAST": {"damage": 20, "effect": "mult_bonus_1x"}
            },

            # Defense moves
            "player_defense": {
                "EMOTIONAL_WALLS": {"block": 20},
                "DISSOCIATION": {"dodge": True, "bonus_spins": 1},
                "SELF_MEDICATION": {"heal": 25, "mult_penalty": -1},
                "THERAPY_SESSION": {"heal": 15, "bonus_spins": 2, "damage_reduction": 0.10}
            },

            # Items
            "battle_items": {
                "ENERGY_DRINK": {"spins": 3, "attack_bonus": 10},
                "CIGARETTE_BREAK": {"spins": 1, "heal": 10},
                "RESTRAINING_ORDER": {"opponent_freeze": 2},
                "ADDERALL": {"guarantee_critical": True},
                "WHISKEY_BOTTLE": {"random_effect": True}  # Can heal 30, damage self 20, +5 spins, or instant lose
            }
        }

        # Maximum board multiplier (from cascades and Addiction Meter)
        self.maximum_board_mult = 512

        # Reel strips - will be created separately
        reels = {
            "BR0": "BR0.csv",  # Base game reel
            "FR0": "FR0.csv",  # Free game/bonus reel
        }
        self.reels = {}
        for r, f in reels.items():
            reel_path = os.path.join(self.reels_path, f)
            if os.path.exists(reel_path):
                self.reels[r] = self.read_reels_csv(reel_path)

        # BET MODES AND DISTRIBUTIONS
        # Support for multiple RTP configurations: 94%, 96%, 98%
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    # Wincap distribution (0.1% of spins)
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                            },
                            "scatter_triggers": {4: 1},  # Battle bonus for wincap
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    # Bonus feature distribution (15% of spins trigger bonuses)
                    Distribution(
                        criteria="bonus",
                        quota=0.15,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                            },
                            "scatter_triggers": {3: 10, 4: 5},  # More rehab than battle
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    # Zero win distribution (40% of spins)
                    Distribution(
                        criteria="0",
                        quota=0.40,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    # Regular basegame wins (45% of spins)
                    Distribution(
                        criteria="basegame",
                        quota=0.45,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
        ]


# Create singleton instance
game_config = GameConfig()
