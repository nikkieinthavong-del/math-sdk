"""Battle Bonus - 4-Round RPG Battle System with 3x1 Attack Reel"""

import random
from typing import Dict, List, Tuple, Optional


class BattleBonus:
    """
    DYSFUNCTION DUEL - Pokémon Battle Royale: Prescription Required
    4-Scatter Bonus Feature

    Mechanics:
    - Start with 5 spins
    - 3x1 vertical reel shows: [MOVE TYPE] [POWER LEVEL] [BONUS EFFECT]
    - Your Pokémon: "DEPRESSO" vs 4 escalating opponents
    - Progressive multiplier system rewards aggressive play
    - Battle through 4 rounds for MEGA WIN (1,000x-5,000x)
    """

    def __init__(self, config):
        self.config = config
        self.battle_config = config.battle_bonus_config
        self.reset_state()

    def reset_state(self):
        """Initialize/reset battle state"""
        self.spins_remaining = self.battle_config["starting_spins"]
        self.current_round = 0
        self.player_hp = self.battle_config["player_hp"]
        self.player_max_hp = self.battle_config["player_hp"]
        self.multiplier = 1.0
        self.total_win = 0
        self.battle_log = []
        self.current_opponent = None
        self.opponent_hp = 0
        self.turn_count = 0
        self.charging_attack = None
        self.opponent_frozen_turns = 0

    def start_round(self, round_number: int):
        """Initialize a new battle round"""
        self.current_round = round_number
        opponent_config = self.battle_config["opponents"][round_number]

        self.current_opponent = opponent_config["name"]
        self.opponent_hp = opponent_config["hp"]
        self.turn_count = 0

        self.battle_log.append({
            "event": "round_start",
            "round": round_number + 1,
            "opponent": self.current_opponent,
            "opponent_hp": self.opponent_hp
        })

    def spin_battle_reel(self) -> Dict:
        """
        Spin the 3x1 battle reel:
        Position 1: MOVE TYPE (Attack/Defend/Item)
        Position 2: POWER LEVEL (Weak/Medium/Strong/CRITICAL)
        Position 3: BONUS EFFECT (Multiplier/Extra Spin/Heal)

        Weighted distribution:
        - Attack: 50%
        - Defense: 30%
        - Item: 20%
        """
        move_weights = {
            "ATTACK": 50,
            "DEFEND": 30,
            "ITEM": 20
        }

        power_weights = {
            "WEAK": 40,
            "MEDIUM": 35,
            "STRONG": 20,
            "CRITICAL": 5
        }

        bonus_weights = {
            "NONE": 50,
            "MULTIPLIER_0.5": 20,
            "EXTRA_SPIN": 20,
            "HEAL_10": 10
        }

        move_type = random.choices(
            list(move_weights.keys()),
            weights=list(move_weights.values())
        )[0]

        power_level = random.choices(
            list(power_weights.keys()),
            weights=list(power_weights.values())
        )[0]

        bonus_effect = random.choices(
            list(bonus_weights.keys()),
            weights=list(bonus_weights.values())
        )[0]

        return {
            "position_1": move_type,
            "position_2": power_level,
            "position_3": bonus_effect,
            "reel_result": [move_type, power_level, bonus_effect]
        }

    def execute_attack(self, power_level: str) -> Dict:
        """Execute player attack based on power level"""
        attacks = self.battle_config["player_attacks"]

        # Select attack based on power level
        attack_map = {
            "WEAK": "ANXIETY_ATTACK",
            "MEDIUM": "THERAPY_SLAP",
            "STRONG": "PRESCRIPTION_PUNCH",
            "CRITICAL": "EXISTENTIAL_CRISIS"
        }

        attack_name = attack_map.get(power_level, "ANXIETY_ATTACK")
        attack_config = attacks[attack_name]

        damage = attack_config["damage"]
        hit_success = True

        # Check hit rate for critical attacks
        if "hit_rate" in attack_config:
            hit_success = random.random() < attack_config["hit_rate"]

        result = {
            "action": "attack",
            "attack_name": attack_name,
            "damage": damage if hit_success else 0,
            "hit": hit_success,
            "critical": attack_config.get("critical", False),
            "effect": attack_config.get("effect")
        }

        if hit_success:
            self.opponent_hp -= damage

            # Apply attack effects
            effect = attack_config.get("effect")
            if effect == "heal_5":
                heal_amount = min(5, self.player_max_hp - self.player_hp)
                self.player_hp += heal_amount
                result["heal"] = heal_amount
            elif effect == "mult_bonus_1x":
                self.multiplier += 1.0
                result["multiplier_bonus"] = 1.0
            elif effect and "mult_bonus" in effect:
                bonus = float(effect.split("_")[-1].replace("x", ""))
                self.multiplier += bonus

            # Update progressive multiplier
            if attack_config.get("critical"):
                self.multiplier += 1.0
            else:
                self.multiplier += 0.5

        return result

    def execute_defense(self, power_level: str) -> Dict:
        """Execute player defense move"""
        defenses = self.battle_config["player_defense"]

        defense_map = {
            "WEAK": "EMOTIONAL_WALLS",
            "MEDIUM": "DISSOCIATION",
            "STRONG": "THERAPY_SESSION",
            "CRITICAL": "THERAPY_SESSION"
        }

        defense_name = defense_map.get(power_level, "EMOTIONAL_WALLS")
        defense_config = defenses[defense_name]

        result = {
            "action": "defend",
            "defense_name": defense_name,
            "block": defense_config.get("block", 0),
            "dodge": defense_config.get("dodge", False),
            "heal": 0
        }

        # Apply defense effects
        if "heal" in defense_config:
            heal_amount = min(defense_config["heal"], self.player_max_hp - self.player_hp)
            self.player_hp += heal_amount
            result["heal"] = heal_amount

        if "bonus_spins" in defense_config:
            self.spins_remaining += defense_config["bonus_spins"]
            result["bonus_spins"] = defense_config["bonus_spins"]

        # Defense reduces multiplier slightly
        if "mult_penalty" in defense_config:
            self.multiplier = max(1.0, self.multiplier + defense_config["mult_penalty"])

        return result

    def use_item(self) -> Dict:
        """Use random battle item"""
        items = self.battle_config["battle_items"]
        item_name = random.choice(list(items.keys()))
        item_config = items[item_name]

        result = {
            "action": "item",
            "item_name": item_name
        }

        # Apply item effects
        if "spins" in item_config:
            self.spins_remaining += item_config["spins"]
            result["bonus_spins"] = item_config["spins"]

        if "heal" in item_config:
            heal_amount = min(item_config["heal"], self.player_max_hp - self.player_hp)
            self.player_hp += heal_amount
            result["heal"] = heal_amount

        if "attack_bonus" in item_config:
            result["attack_bonus"] = item_config["attack_bonus"]

        if "opponent_freeze" in item_config:
            self.opponent_frozen_turns = item_config["opponent_freeze"]
            result["freeze_turns"] = item_config["opponent_freeze"]

        if item_config.get("random_effect"):
            # WHISKEY BOTTLE random effect
            effects = [
                {"type": "heal", "value": 30},
                {"type": "damage_self", "value": 20},
                {"type": "spins", "value": 5},
                {"type": "instant_lose", "value": True}
            ]
            random_effect = random.choice(effects)

            if random_effect["type"] == "heal":
                heal = min(random_effect["value"], self.player_max_hp - self.player_hp)
                self.player_hp += heal
                result["random_heal"] = heal
            elif random_effect["type"] == "damage_self":
                self.player_hp -= random_effect["value"]
                result["random_damage"] = random_effect["value"]
            elif random_effect["type"] == "spins":
                self.spins_remaining += random_effect["value"]
                result["random_spins"] = random_effect["value"]
            elif random_effect["type"] == "instant_lose":
                self.player_hp = 0
                result["instant_lose"] = True

        # Items don't consume spin
        self.spins_remaining += 1

        return result

    def opponent_attack(self) -> Optional[Dict]:
        """Execute opponent's attack"""
        if self.opponent_frozen_turns > 0:
            self.opponent_frozen_turns -= 1
            return {
                "action": "opponent_frozen",
                "turns_remaining": self.opponent_frozen_turns
            }

        opponent_config = self.battle_config["opponents"][self.current_round]
        attack = random.choice(opponent_config["attacks"])

        damage = attack["damage"]

        result = {
            "action": "opponent_attack",
            "attack_name": attack["name"],
            "damage": damage,
            "critical": attack.get("critical", False),
            "stun": attack.get("stun", False),
            "debuff": attack.get("debuff", False)
        }

        self.player_hp -= damage

        # Apply debuff effects
        if attack.get("debuff"):
            self.multiplier = max(1.0, self.multiplier - 0.5)
            result["multiplier_reduction"] = 0.5

        return result

    def process_turn(self) -> Dict:
        """
        Process a single battle turn:
        1. Spin battle reel
        2. Execute player action
        3. Apply bonus effects
        4. Opponent attacks (if player didn't defend)
        5. Check win/lose conditions
        """
        if self.spins_remaining <= 0:
            return {
                "status": "no_spins_remaining",
                "result": "defeat",
                "total_win": self.total_win * 0.5  # Lose round, collect half
            }

        # Spin the reel
        reel_result = self.spin_battle_reel()

        move_type = reel_result["position_1"]
        power_level = reel_result["position_2"]
        bonus_effect = reel_result["position_3"]

        turn_data = {
            "turn_number": self.turn_count + 1,
            "reel_result": reel_result["reel_result"],
            "player_action": None,
            "opponent_action": None,
            "player_hp_before": self.player_hp,
            "opponent_hp_before": self.opponent_hp,
            "multiplier_before": self.multiplier
        }

        # Execute player action based on reel
        if move_type == "ATTACK":
            turn_data["player_action"] = self.execute_attack(power_level)
        elif move_type == "DEFEND":
            turn_data["player_action"] = self.execute_defense(power_level)
        elif move_type == "ITEM":
            turn_data["player_action"] = self.use_item()

        # Apply bonus effects from position 3
        if bonus_effect == "MULTIPLIER_0.5":
            self.multiplier += 0.5
        elif bonus_effect == "EXTRA_SPIN":
            self.spins_remaining += 1
        elif bonus_effect == "HEAL_10":
            heal = min(10, self.player_max_hp - self.player_hp)
            self.player_hp += heal

        turn_data["bonus_effect"] = bonus_effect

        # Opponent attacks (unless player defended successfully)
        opponent_dodged = (
            turn_data["player_action"]
            and turn_data["player_action"].get("dodge") == True
        )

        if not opponent_dodged and self.opponent_hp > 0:
            turn_data["opponent_action"] = self.opponent_attack()

        # Special ability: Professor Rehab's "Therapy Bill"
        if self.current_opponent == "PROFESSOR_REHAB" and self.turn_count % 3 == 0:
            therapy_bill = 50
            self.total_win = max(0, self.total_win - therapy_bill)
            turn_data["special_ability"] = {
                "name": "Therapy Bill",
                "deduction": therapy_bill
            }

        # Update state
        turn_data["player_hp_after"] = self.player_hp
        turn_data["opponent_hp_after"] = self.opponent_hp
        turn_data["multiplier_after"] = self.multiplier

        self.spins_remaining -= 1
        self.turn_count += 1
        self.battle_log.append(turn_data)

        # Check win/lose conditions
        if self.opponent_hp <= 0:
            return self._handle_round_victory()
        elif self.player_hp <= 0:
            return self._handle_defeat()

        return {
            "status": "continue",
            "turn_data": turn_data
        }

    def _handle_round_victory(self) -> Dict:
        """Handle victory against current opponent"""
        opponent_config = self.battle_config["opponents"][self.current_round]

        # Award round reward
        reward = opponent_config["defeat_reward"]
        if isinstance(reward, tuple):
            # Final boss range
            reward = random.uniform(*reward)

        round_win = reward * self.multiplier
        self.total_win += round_win

        # Award bonus spins
        bonus_spins = opponent_config.get("bonus_spins", 0)
        self.spins_remaining += bonus_spins

        victory_data = {
            "status": "round_victory",
            "opponent": self.current_opponent,
            "round": self.current_round + 1,
            "reward": reward,
            "multiplier": self.multiplier,
            "round_win": round_win,
            "bonus_spins": bonus_spins,
            "total_win": self.total_win
        }

        self.battle_log.append(victory_data)

        # Check if final boss defeated
        if self.current_round >= len(self.battle_config["opponents"]) - 1:
            victory_data["status"] = "final_victory"
            victory_data["achievement"] = "GRADUATED"
            return victory_data

        return victory_data

    def _handle_defeat(self) -> Dict:
        """Handle player defeat"""
        defeat_data = {
            "status": "defeat",
            "round": self.current_round + 1,
            "opponent": self.current_opponent,
            "total_win": self.total_win * 0.5,  # Collect half winnings
            "turns_survived": self.turn_count
        }

        self.battle_log.append(defeat_data)
        return defeat_data

    def play_full_battle(self) -> Dict:
        """
        Play entire battle bonus (all 4 rounds if possible).
        """
        self.reset_state()

        results = {
            "bonus_type": "battle_bonus",
            "rounds": [],
            "total_win": 0,
            "rounds_completed": 0,
            "final_status": None,
            "final_multiplier": 1.0
        }

        # Play through all rounds
        for round_num in range(len(self.battle_config["opponents"])):
            self.start_round(round_num)

            round_result = {
                "round_number": round_num + 1,
                "opponent": self.current_opponent,
                "turns": []
            }

            # Battle until round ends
            while True:
                turn_result = self.process_turn()
                round_result["turns"].append(turn_result)

                if turn_result["status"] in ["round_victory", "final_victory"]:
                    round_result["outcome"] = "victory"
                    round_result["win"] = turn_result.get("round_win", 0)
                    results["rounds_completed"] += 1
                    break
                elif turn_result["status"] == "defeat":
                    round_result["outcome"] = "defeat"
                    results["final_status"] = "defeated"
                    break
                elif turn_result["status"] == "no_spins_remaining":
                    round_result["outcome"] = "no_spins"
                    results["final_status"] = "ran_out_of_spins"
                    break

            results["rounds"].append(round_result)

            # Check if battle should end
            if results["final_status"] or turn_result.get("status") == "final_victory":
                if turn_result.get("status") == "final_victory":
                    results["final_status"] = "victory"
                break

        results["total_win"] = self.total_win
        results["final_multiplier"] = self.multiplier

        return results


def simulate_battle_bonus(config, num_simulations: int = 1000) -> Dict:
    """
    Simulate battle bonus multiple times for RTP calculation.
    """
    battle = BattleBonus(config)
    wins = []
    rounds_completed = []
    final_victories = 0

    for _ in range(num_simulations):
        result = battle.play_full_battle()
        wins.append(result["total_win"])
        rounds_completed.append(result["rounds_completed"])

        if result["final_status"] == "victory":
            final_victories += 1

    return {
        "average_win": sum(wins) / len(wins),
        "min_win": min(wins),
        "max_win": max(wins),
        "average_rounds_completed": sum(rounds_completed) / len(rounds_completed),
        "final_victory_rate": final_victories / num_simulations,
        "win_distribution": {
            "0-100x": sum(1 for w in wins if w < 100),
            "100-500x": sum(1 for w in wins if 100 <= w < 500),
            "500-1000x": sum(1 for w in wins if 500 <= w < 1000),
            "1000-2500x": sum(1 for w in wins if 1000 <= w < 2500),
            "2500x+": sum(1 for w in wins if w >= 2500)
        }
    }
