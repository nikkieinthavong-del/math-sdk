"""Poké-Vice Academy game state overrides"""

from game_executables import GameExecutables


class GameStateOverride(GameExecutables):
    """
    Override universal state functions for Poké-Vice Academy.
    Handles custom state management for Addiction Meter and bonuses.
    """

    def reset_book(self):
        """Reset global values for new spin"""
        super().reset_book()

        # Reset Poké-Vice Academy specific values
        self.tumble_win = 0
        self.cascade_metadata = []

        # Don't reset addiction_meter - it persists across spins!
        # Only decays naturally per game_events

    def reset_fs_spin(self):
        """Reset for freespin/bonus games"""
        super().reset_fs_spin()

        # Reset Addiction Meter for bonus games
        self.reset_addiction_meter()

    def assign_special_sym_function(self):
        """Assign special symbol behaviors (wilds, scatters)"""
        # Wilds are handled by cluster evaluation
        # Scatters trigger bonuses (checked in gamestate)
        pass

    def check_repeat(self) -> None:
        """
        Check if spin failed criteria constraint.
        Extended for bonus triggers.
        """
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            # Check if forced bonus required
            distribution_conditions = self.get_current_distribution_conditions()

            if distribution_conditions.get("force_freegame") and not self.triggered_freegame:
                self.repeat = True

            # Check scatter trigger requirements
            if "scatter_triggers" in distribution_conditions:
                scatter_info = self.check_scatter_triggers(self.config, self.board)
                required_scatters = distribution_conditions["scatter_triggers"]

                if scatter_info["scatter_count"] not in required_scatters:
                    self.repeat = True

            # No win when win expected
            if self.win_manager.running_bet_win == 0 and self.criteria != "0":
                self.repeat = True
