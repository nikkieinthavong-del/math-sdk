"""Poké-Vice Academy game state management"""

from game_override import GameStateOverride
from game_events import GameEvents
from rehab_bonus import RehabBonus
from battle_bonus import BattleBonus


class GameEvents(GameEvents):
    """Custom game events for Poké-Vice Academy"""

    @staticmethod
    def update_addiction_meter_event(state):
        """Update Addiction Meter based on cascades"""
        if hasattr(state, 'addiction_meter'):
            # Decay meter on non-winning spins
            if state.win_data["totalWin"] == 0:
                state.addiction_meter = max(
                    0,
                    state.addiction_meter - state.config.addiction_meter["decay_per_spin"]
                )


class GameState(GameStateOverride):
    """
    Core game state for Poké-Vice Academy.

    Manages:
    - Base game with Reputation Decay Cascade
    - Addiction Meter progression
    - Rehab Bonus (3-scatter) triggers
    - Battle Bonus (4-scatter) triggers
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addiction_meter = 0
        self.rehab_bonus = None
        self.battle_bonus = None

    def run_spin(self, sim):
        """Execute base game spin with Addiction Meter and bonus triggers"""
        self.reset_seed(sim)
        self.repeat = True

        while self.repeat:
            # Reset simulation variables and draw board
            self.reset_book()
            self.draw_board()

            # Update Addiction Meter decay (from previous spin)
            GameEvents.update_addiction_meter_event(self)

            # Evaluate clusters with Reputation Decay Cascade
            self.get_clusters_with_addiction_meter()
            self.emit_tumble_win_events()

            # Process cascades (Reputation Decay continues until no wins)
            cascade_count = 0
            max_cascades = 10

            while self.win_data["totalWin"] > 0 and not self.wincap_triggered and cascade_count < max_cascades:
                # Apply Reputation Decay (degrade symbols)
                self.apply_reputation_decay()

                # Tumble/cascade
                self.tumble_game_board()

                # Re-evaluate clusters
                self.get_clusters_with_addiction_meter()
                self.emit_tumble_win_events()

                cascade_count += 1

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            # Check for scatter-triggered bonuses
            scatter_info = self.check_scatter_triggers()

            if scatter_info["bonus_triggered"] == "rehab_bonus":
                self.trigger_rehab_bonus()
            elif scatter_info["bonus_triggered"] == "battle_bonus":
                self.trigger_battle_bonus()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def get_clusters_with_addiction_meter(self):
        """
        Evaluate clusters using Reputation Decay Cascade and Addiction Meter.
        """
        from game_calculations import GameCalculations

        calc = GameCalculations()

        # Evaluate clusters with current Addiction Meter state
        result = calc.evaluate_clusters_with_addiction_meter(
            config=self.config,
            board=self.board,
            addiction_meter=self.addiction_meter,
            max_cascades=1  # Process one cascade at a time for state control
        )

        # Update win data
        self.win_data = {
            "totalWin": result.get("totalWin", 0),
            "wins": result.get("wins", [])
        }

        # Update Addiction Meter
        self.addiction_meter = result.get("addiction_meter_end", self.addiction_meter)

        # Store cascade metadata
        if hasattr(self, 'cascade_metadata'):
            self.cascade_metadata.append(result)
        else:
            self.cascade_metadata = [result]

    def apply_reputation_decay(self):
        """
        Apply Reputation Decay to winning symbols.
        Symbols degrade: Legendary → Evolved → Basic → Egg
        """
        # This is handled inside the calculation logic
        # but we can track state here if needed
        pass

    def check_scatter_triggers(self):
        """Check for EGG scatter bonus triggers"""
        from game_calculations import GameCalculations

        calc = GameCalculations()
        return calc.check_scatter_triggers(self.config, self.board)

    def trigger_rehab_bonus(self):
        """
        Trigger Rehab Bonus (3-scatter):
        - Pokéhab Center - Mandatory Attendance
        - 3x1 reel with Pokéball catching mechanics
        """
        self.rehab_bonus = RehabBonus(self.config)
        bonus_result = self.rehab_bonus.play_full_bonus()

        # Add bonus win to total
        bonus_win = bonus_result["total_win"]
        self.win_data["totalWin"] += bonus_win
        self.win_data["bonus_type"] = "rehab_bonus"
        self.win_data["bonus_result"] = bonus_result

        # Log bonus event
        self.book.events.append({
            "type": "bonus_triggered",
            "bonus": "rehab_bonus",
            "win": bonus_win,
            "details": bonus_result
        })

    def trigger_battle_bonus(self):
        """
        Trigger Battle Bonus (4-scatter):
        - Dysfunction Duel
        - RPG-style battle with 4 rounds
        """
        self.battle_bonus = BattleBonus(self.config)
        bonus_result = self.battle_bonus.play_full_battle()

        # Add bonus win to total
        bonus_win = bonus_result["total_win"]
        self.win_data["totalWin"] += bonus_win
        self.win_data["bonus_type"] = "battle_bonus"
        self.win_data["bonus_result"] = bonus_result

        # Log bonus event
        self.book.events.append({
            "type": "bonus_triggered",
            "bonus": "battle_bonus",
            "win": bonus_win,
            "details": bonus_result
        })

    def run_freespin(self):
        """
        Run freespins/bonus games.
        In Poké-Vice Academy, this is called for bonus features.
        """
        self.reset_fs_spin()

        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board()

            # Update Addiction Meter
            GameEvents.update_addiction_meter_event(self)

            # Evaluate clusters with Addiction Meter
            self.get_clusters_with_addiction_meter()
            self.emit_tumble_win_events()

            # Process cascades
            while self.win_data["totalWin"] > 0 and not self.wincap_triggered:
                self.apply_reputation_decay()
                self.tumble_game_board()
                self.get_clusters_with_addiction_meter()
                self.emit_tumble_win_events()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            # Check for retrigger
            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_freespin()

    def get_game_state_for_frontend(self):
        """
        Return current game state for frontend display.
        Includes Addiction Meter, bonus states, etc.
        """
        state = {
            "board": self.get_board_symbols(),
            "addiction_meter": self.addiction_meter,
            "total_win": self.win_data.get("totalWin", 0),
            "cascade_count": len(getattr(self, 'cascade_metadata', [])),
        }

        # Add bonus state if active
        if self.rehab_bonus:
            state["rehab_bonus"] = self.rehab_bonus.get_current_state()

        if self.battle_bonus:
            state["battle_bonus"] = {
                "current_round": self.battle_bonus.current_round,
                "player_hp": self.battle_bonus.player_hp,
                "opponent_hp": self.battle_bonus.opponent_hp,
                "spins_remaining": self.battle_bonus.spins_remaining,
                "multiplier": self.battle_bonus.multiplier
            }

        return state

    def get_board_symbols(self):
        """Get current board symbols as 2D array"""
        symbols = []
        for reel in self.board:
            reel_symbols = []
            for cell in reel:
                reel_symbols.append(cell.symbol)
            symbols.append(reel_symbols)
        return symbols
