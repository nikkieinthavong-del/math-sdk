"""Rehab Bonus - 3x1 Reel Pokéball Catch Mechanics"""

import random
from typing import Dict, List, Tuple


class RehabBonus:
    """
    POKÉHAB CENTER - MANDATORY ATTENDANCE
    3-Scatter Bonus Feature

    Mechanics:
    - 3x1 vertical reel with 5 throws (spins)
    - Each throw shows: [BALL TYPE] [CATCH/MISS/UPGRADE] [MULTIPLIER]
    - Target Pokémon grid with different values
    - Caught Pokémon are crossed off and award their value
    - Special outcomes: Restraining Order adds throws, Upgrade guarantees Master Ball
    """

    def __init__(self, config):
        self.config = config
        self.bonus_config = config.rehab_bonus_config
        self.reset_state()

    def reset_state(self):
        """Initialize/reset bonus state"""
        self.throws_remaining = self.bonus_config["throws"]
        self.total_win = 0
        self.throws_history = []
        self.caught_pokemon = []
        self.available_targets = self._initialize_targets()
        self.next_throw_upgraded = False  # Upgrade flag

    def _initialize_targets(self) -> List[Dict]:
        """
        Initialize target Pokémon grid:
        Row 1: [SOBBLE-TER] (1x, 100x)
        Row 2: [SLAK-OFF] [SLAK-OFF] (2x, 50x each)
        Row 3: [WHIS-MURRR] x3 (3x, 25x each)
        Row 4: [RATT-ITUDE] x4 (4x, 15x each)
        """
        targets = []
        for target_config in self.bonus_config["targets"]:
            for i in range(target_config["count"]):
                targets.append({
                    "name": target_config["name"],
                    "payout": target_config["payout"],
                    "caught": False,
                    "id": f"{target_config['name']}_{i}"
                })
        return targets

    def spin_3x1_reel(self) -> Dict:
        """
        Spin the 3x1 reel and get result for each position:
        Position 1: BALL TYPE
        Position 2: CATCH/MISS/UPGRADE
        Position 3: MULTIPLIER (1x-10x)
        """
        weights = self.bonus_config["reel_weights"]

        # Position 1: Ball Type
        if self.next_throw_upgraded:
            ball_type = "MASTER_BALL"
            self.next_throw_upgraded = False
        else:
            ball_type = random.choices(
                list(weights["position_1"].keys()),
                weights=list(weights["position_1"].values())
            )[0]

        # Position 2: Catch Result
        catch_result = random.choices(
            list(weights["position_2"].keys()),
            weights=list(weights["position_2"].values())
        )[0]

        # Position 3: Multiplier
        multiplier_str = random.choices(
            list(weights["position_3"].keys()),
            weights=list(weights["position_3"].values())
        )[0]
        multiplier = int(multiplier_str.replace("x", ""))

        return {
            "position_1": ball_type,
            "position_2": catch_result,
            "position_3": multiplier,
            "reel_result": [ball_type, catch_result, f"{multiplier}x"]
        }

    def process_throw(self) -> Dict:
        """
        Process a single pokéball throw.

        Returns throw result with:
        - Reel outcome
        - Catch success/failure
        - Win amount
        - Special effects
        - Animation data
        """
        if self.throws_remaining <= 0:
            return {
                "status": "no_throws_remaining",
                "total_win": self.total_win
            }

        # Spin the 3x1 reel
        reel_result = self.spin_3x1_reel()

        ball_type = reel_result["position_1"]
        catch_result = reel_result["position_2"]
        multiplier = reel_result["position_3"]

        throw_data = {
            "throw_number": len(self.throws_history) + 1,
            "reel_result": reel_result["reel_result"],
            "ball_type": ball_type,
            "catch_result": catch_result,
            "multiplier": multiplier,
            "win": 0,
            "caught_pokemon": None,
            "special_effect": None,
            "animation": None
        }

        # Handle special ball: RESTRAINING_ORDER
        if ball_type == "RESTRAINING_ORDER":
            bonus_throws = self.bonus_config["pokeballs"]["RESTRAINING_ORDER"]["bonus_throws"]
            self.throws_remaining += bonus_throws
            throw_data["special_effect"] = f"RESTRAINING_ORDER: +{bonus_throws} throws"
            throw_data["animation"] = "restraining_order_effect"
            self.throws_remaining -= 1  # Still consumes current throw
            self.throws_history.append(throw_data)
            return throw_data

        # Handle UPGRADE result
        if catch_result == "UPGRADE":
            self.next_throw_upgraded = True
            throw_data["special_effect"] = "UPGRADE: Next throw guaranteed Master Ball"
            throw_data["animation"] = "upgrade_effect"
            self.throws_remaining -= 1
            self.throws_history.append(throw_data)
            return throw_data

        # Handle CATCH or MISS
        ball_config = self.bonus_config["pokeballs"][ball_type]
        catch_rate = ball_config["catch_rate"]

        # Determine if catch is successful
        catch_success = catch_result == "CATCH" or random.random() < catch_rate

        if catch_success:
            # Select random uncaught target
            uncaught = [t for t in self.available_targets if not t["caught"]]

            if uncaught:
                # Catch pokemon
                target = random.choice(uncaught)
                target["caught"] = True

                # Calculate win
                base_payout = target["payout"]

                # Apply ball multiplier if range
                ball_mult = ball_config.get("multiplier", 1)
                if isinstance(ball_mult, tuple):
                    ball_mult = random.uniform(*ball_mult)

                # Apply reel multiplier
                total_win = base_payout * ball_mult * multiplier

                self.total_win += total_win
                self.caught_pokemon.append(target["name"])

                throw_data["win"] = total_win
                throw_data["caught_pokemon"] = target["name"]
                throw_data["animation"] = self._get_catch_animation(target["name"])

            else:
                # All pokemon caught - bonus win
                throw_data["special_effect"] = "ALL_POKEMON_CAUGHT"
                throw_data["animation"] = "all_caught_bonus"

        else:
            # Miss
            throw_data["animation"] = self._get_miss_animation()

        self.throws_remaining -= 1
        self.throws_history.append(throw_data)

        return throw_data

    def _get_catch_animation(self, pokemon_name: str) -> str:
        """Get catch animation based on pokemon"""
        animations = {
            "SOBBLE-TER": "sobble_caught_therapy",
            "SLAK-OFF": "slakoff_got_job",
            "WHIS-MURRR": "whismur_gossip_seized",
            "RATT-ITUDE": "rattitude_anger_management"
        }
        return animations.get(pokemon_name, "generic_catch")

    def _get_miss_animation(self) -> str:
        """Get random miss animation"""
        miss_animations = [
            "dodge_cigarette",
            "pawns_ball",
            "restraining_order_bounce"
        ]
        return random.choice(miss_animations)

    def play_full_bonus(self) -> Dict:
        """
        Play entire rehab bonus (all throws) and return final results.
        """
        self.reset_state()

        results = {
            "bonus_type": "rehab_bonus",
            "throws": [],
            "total_win": 0,
            "caught_pokemon": [],
            "targets_caught": 0,
            "total_targets": len(self.available_targets)
        }

        # Process all throws
        while self.throws_remaining > 0:
            throw_result = self.process_throw()
            results["throws"].append(throw_result)

            # Check if all pokemon caught (early completion bonus)
            if all(t["caught"] for t in self.available_targets):
                results["all_caught_bonus"] = True
                break

        results["total_win"] = self.total_win
        results["caught_pokemon"] = self.caught_pokemon
        results["targets_caught"] = sum(1 for t in self.available_targets if t["caught"])

        return results

    def get_current_state(self) -> Dict:
        """Get current bonus state for frontend"""
        return {
            "throws_remaining": self.throws_remaining,
            "total_win": self.total_win,
            "available_targets": [
                {
                    "name": t["name"],
                    "payout": t["payout"],
                    "caught": t["caught"]
                }
                for t in self.available_targets
            ],
            "next_throw_upgraded": self.next_throw_upgraded,
            "throws_history": self.throws_history
        }


def simulate_rehab_bonus(config, num_simulations: int = 10000) -> Dict:
    """
    Simulate rehab bonus multiple times for RTP calculation.

    Returns statistics:
    - Average win
    - Win distribution
    - Catch rates
    - Throw efficiency
    """
    bonus = RehabBonus(config)
    wins = []
    catches = []
    throw_counts = []

    for _ in range(num_simulations):
        result = bonus.play_full_bonus()
        wins.append(result["total_win"])
        catches.append(result["targets_caught"])
        throw_counts.append(len(result["throws"]))

    return {
        "average_win": sum(wins) / len(wins),
        "min_win": min(wins),
        "max_win": max(wins),
        "average_catches": sum(catches) / len(catches),
        "average_throws": sum(throw_counts) / len(throw_counts),
        "win_distribution": {
            "0-50x": sum(1 for w in wins if w < 50),
            "50-100x": sum(1 for w in wins if 50 <= w < 100),
            "100-250x": sum(1 for w in wins if 100 <= w < 250),
            "250-500x": sum(1 for w in wins if 250 <= w < 500),
            "500x+": sum(1 for w in wins if w >= 500)
        }
    }
