"""Poké-Vice Academy game events"""

from copy import deepcopy

# Event type constants
UPDATE_ADDICTION_METER = "updateAddictionMeter"
REPUTATION_DECAY = "reputationDecay"
DYSFUNCTION_WILD_TRIGGER = "dysfunctionWildTrigger"
REHAB_BONUS_START = "rehabBonusStart"
REHAB_BONUS_THROW = "rehabBonusThrow"
BATTLE_BONUS_START = "battleBonusStart"
BATTLE_BONUS_TURN = "battleBonusTurn"
ADDICTION_THRESHOLD = "addictionThreshold"


def update_addiction_meter_event(gamestate):
    """
    Emit event when Addiction Meter updates.
    Tracks meter value and any threshold effects triggered.
    """
    event = {
        "index": len(gamestate.book.events),
        "type": UPDATE_ADDICTION_METER,
        "addictionMeter": gamestate.addiction_meter,
        "thresholds": {}
    }

    # Check threshold effects
    meter_config = gamestate.config.addiction_meter
    for threshold, effect_name in meter_config["thresholds"].items():
        if gamestate.addiction_meter >= threshold:
            event["thresholds"][threshold] = effect_name

    gamestate.book.add_event(event)


def reputation_decay_event(gamestate, degradations):
    """
    Emit event for Reputation Decay cascade.
    Shows which symbols degraded and to what tier.
    """
    event = {
        "index": len(gamestate.book.events),
        "type": REPUTATION_DECAY,
        "degradations": deepcopy(degradations),
        "cascadeNumber": len(gamestate.cascade_metadata) if hasattr(gamestate, 'cascade_metadata') else 0
    }
    gamestate.book.add_event(event)


def dysfunction_wild_event(gamestate, wild_type, effect_data):
    """Emit event when Dysfunction Wild triggers special behavior"""
    event = {
        "index": len(gamestate.book.events),
        "type": DYSFUNCTION_WILD_TRIGGER,
        "wildType": wild_type,
        "effect": effect_data
    }
    gamestate.book.add_event(event)


def addiction_threshold_event(gamestate, threshold, effect):
    """Emit event when Addiction Meter crosses a threshold"""
    event = {
        "index": len(gamestate.book.events),
        "type": ADDICTION_THRESHOLD,
        "threshold": threshold,
        "effect": effect,
        "currentMeter": gamestate.addiction_meter
    }
    gamestate.book.add_event(event)


def rehab_bonus_start_event(gamestate, config):
    """Emit event when Rehab Bonus starts"""
    event = {
        "index": len(gamestate.book.events),
        "type": REHAB_BONUS_START,
        "throws": config["throws"],
        "targets": deepcopy(config["targets"])
    }
    gamestate.book.add_event(event)


def rehab_bonus_throw_event(gamestate, throw_data):
    """Emit event for each Pokéball throw in Rehab Bonus"""
    event = {
        "index": len(gamestate.book.events),
        "type": REHAB_BONUS_THROW,
        "throwNumber": throw_data["throw_number"],
        "reelResult": throw_data["reel_result"],
        "ballType": throw_data["ball_type"],
        "catchResult": throw_data["catch_result"],
        "win": throw_data["win"],
        "caughtPokemon": throw_data.get("caught_pokemon"),
        "animation": throw_data.get("animation")
    }
    gamestate.book.add_event(event)


def battle_bonus_start_event(gamestate, config):
    """Emit event when Battle Bonus starts"""
    event = {
        "index": len(gamestate.book.events),
        "type": BATTLE_BONUS_START,
        "playerPokemon": config["player_pokemon"],
        "playerHP": config["player_hp"],
        "startingSpins": config["starting_spins"],
        "opponents": [opp["name"] for opp in config["opponents"]]
    }
    gamestate.book.add_event(event)


def battle_bonus_turn_event(gamestate, turn_data):
    """Emit event for each battle turn"""
    event = {
        "index": len(gamestate.book.events),
        "type": BATTLE_BONUS_TURN,
        "turnNumber": turn_data["turn_number"],
        "reelResult": turn_data["reel_result"],
        "playerAction": turn_data.get("player_action"),
        "opponentAction": turn_data.get("opponent_action"),
        "playerHP": turn_data["player_hp_after"],
        "opponentHP": turn_data["opponent_hp_after"],
        "multiplier": turn_data["multiplier_after"]
    }
    gamestate.book.add_event(event)


class GameEvents:
    """Collection of game event helper methods"""

    @staticmethod
    def update_addiction_meter_event(state):
        """Update Addiction Meter based on cascades"""
        if hasattr(state, 'addiction_meter'):
            # Emit event if meter changed
            update_addiction_meter_event(state)
