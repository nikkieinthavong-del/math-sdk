"""Poké-Vice Academy game executables - entry points and game loop"""

from game_calculations import GameCalculations
from src.calculations.cluster import Cluster
from game_events import (
    update_addiction_meter_event,
    reputation_decay_event,
    rehab_bonus_start_event,
    rehab_bonus_throw_event,
    battle_bonus_start_event,
    battle_bonus_turn_event
)
from src.events.events import update_freespin_event


class GameExecutables(GameCalculations):
    """
    Game-specific executable functions for Poké-Vice Academy.

    Manages:
    - Cluster evaluation with Reputation Decay
    - Addiction Meter tracking
    - Bonus trigger integration
    """

    def reset_addiction_meter(self):
        """Initialize Addiction Meter at start of game"""
        self.addiction_meter = 0

    def get_clusters_update_wins(self):
        """
        Find clusters on board and update win manager.
        Uses Reputation Decay Cascade system.
        """
        # Find clusters (wilds substitute)
        clusters = Cluster.get_clusters(self.board, "wild")

        # Initialize return data
        return_data = {
            "totalWin": 0,
            "wins": [],
            "cascades": []
        }

        # Evaluate clusters with Reputation Decay and Addiction Meter
        has_more_cascades = True
        cascade_count = 0
        max_cascades = 10

        while has_more_cascades and cascade_count < max_cascades:
            # Calculate global multiplier based on Addiction Meter
            global_multiplier = self._get_addiction_multiplier()

            # Process one cascade iteration
            self.board, return_data, self.addiction_meter, has_more_cascades = (
                self.reputation_decay_cascade(
                    config=self.config,
                    board=self.board,
                    clusters=clusters,
                    addiction_meter=self.addiction_meter,
                    global_multiplier=global_multiplier,
                    return_data=return_data
                )
            )

            # Emit reputation decay event if degradations occurred
            if return_data["cascades"]:
                last_cascade = return_data["cascades"][-1]
                if last_cascade.get("degradations"):
                    reputation_decay_event(self, last_cascade["degradations"])

            # Remove exploded symbols (eggs) and refill
            if has_more_cascades:
                from src.calculations.board import Board
                self.board = Board.remove_exploded_symbols(self.board)
                self.board = Board.apply_gravity(self.board, self.config)

                # Find new clusters
                clusters = Cluster.get_clusters(self.board, "wild")
                if not clusters:
                    has_more_cascades = False

            cascade_count += 1

        # Update win data
        self.win_data = {
            "totalWin": return_data["totalWin"],
            "wins": return_data["wins"]
        }

        # Record cluster wins
        Cluster.record_cluster_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data["totalWin"]

        # Emit Addiction Meter update event
        update_addiction_meter_event(self)

    def _get_addiction_multiplier(self):
        """
        Get global multiplier based on Addiction Meter thresholds:
        - < 25%: 1x
        - 25-49%: 2x (Buzzed)
        - 50-74%: 3x (Tipsy)
        - 75-99%: 5x (Wasted)
        - 100%: 10x (Blackout)
        """
        if self.addiction_meter >= 100:
            return 10
        elif self.addiction_meter >= 75:
            return 5
        elif self.addiction_meter >= 50:
            return 3
        elif self.addiction_meter >= 25:
            return 2
        else:
            return 1

    def trigger_rehab_bonus_game(self):
        """
        Trigger and play Rehab Bonus (3-scatter).
        Integrates with Stake Engine RGS.
        """
        from rehab_bonus import RehabBonus

        # Initialize bonus
        bonus = RehabBonus(self.config)

        # Emit start event
        rehab_bonus_start_event(self, self.config.rehab_bonus_config)

        # Play all throws
        while bonus.throws_remaining > 0:
            throw_result = bonus.process_throw()

            # Emit throw event
            rehab_bonus_throw_event(self, throw_result)

            # Check if all targets caught
            if all(t["caught"] for t in bonus.available_targets):
                break

        # Get final results
        final_result = {
            "total_win": bonus.total_win,
            "caught_pokemon": bonus.caught_pokemon,
            "throws_used": len(bonus.throws_history)
        }

        # Add to win manager
        self.win_manager.update_spinwin(bonus.total_win)
        self.win_data["totalWin"] = self.win_data.get("totalWin", 0) + bonus.total_win

        return final_result

    def trigger_battle_bonus_game(self):
        """
        Trigger and play Battle Bonus (4-scatter).
        Integrates with Stake Engine RGS.
        """
        from battle_bonus import BattleBonus

        # Initialize bonus
        bonus = BattleBonus(self.config)

        # Emit start event
        battle_bonus_start_event(self, self.config.battle_bonus_config)

        # Play all rounds
        result = bonus.play_full_battle()

        # Emit turn events from battle log
        for log_entry in bonus.battle_log:
            if "turn_number" in log_entry:
                battle_bonus_turn_event(self, log_entry)

        # Add to win manager
        self.win_manager.update_spinwin(result["total_win"])
        self.win_data["totalWin"] = self.win_data.get("totalWin", 0) + result["total_win"]

        return result

    def update_freespin(self) -> None:
        """Called before a new reveal during bonus game."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}

    def check_scatter_bonus_triggers(self):
        """
        Check if scatter bonuses should trigger.
        Returns bonus type or None.
        """
        scatter_info = self.check_scatter_triggers(self.config, self.board)

        if scatter_info["bonus_triggered"] == "rehab_bonus":
            return "rehab_bonus"
        elif scatter_info["bonus_triggered"] == "battle_bonus":
            return "battle_bonus"

        return None
