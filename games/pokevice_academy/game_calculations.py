"""Poké-Vice Academy game calculations - Reputation Decay Cascade system"""

import random
from typing import Dict, List, Tuple
from src.executables.executables import Executables
from src.calculations.cluster import Cluster
from src.calculations.board import Board
from src.config.config import Config


class GameCalculations(Executables):
    """
    Game-specific calculations for Poké-Vice Academy.

    Key innovations:
    - REPUTATION DECAY CASCADE: Winning symbols degrade through tiers instead of exploding
    - ADDICTION METER: Dynamic volatility that increases with cascade wins
    - DYSFUNCTION WILDS: Special wild behaviors
    """

    def __init__(self):
        super().__init__()
        self.addiction_meter_value = 0
        self.cascade_count = 0
        self.active_dysfunction_wilds = []

    def reputation_decay_cascade(
        self,
        config: Config,
        board: Board,
        clusters: dict,
        addiction_meter: int = 0,
        global_multiplier: int = 1,
        return_data: dict = None
    ) -> Tuple[Board, dict, int, bool]:
        """
        REPUTATION DECAY CASCADE - Core innovation

        Instead of symbols exploding and disappearing:
        1. Winning symbols DEGRADE to lower tier (Legendary → Evolved → Basic → Egg)
        2. Degraded symbols stay on board and can form NEW clusters
        3. Creates chain reactions as symbols cascade down tiers
        4. Only Egg symbols actually vanish
        5. Addiction Meter fills with each cascade

        Returns:
            - Modified board
            - Updated return_data with wins
            - New addiction_meter value
            - Boolean indicating if cascade should continue
        """
        if return_data is None:
            return_data = {"totalWin": 0, "wins": [], "cascades": []}

        cascade_data = {
            "cascade_number": len(return_data["cascades"]) + 1,
            "wins": [],
            "degradations": [],
            "addiction_meter_before": addiction_meter,
            "addiction_meter_after": addiction_meter
        }

        total_cascade_win = 0
        symbols_to_degrade = []

        # Step 1: Evaluate all clusters and calculate wins
        for sym in clusters:
            for cluster in clusters[sym]:
                syms_in_cluster = len(cluster)

                # Check if this cluster size + symbol has a payout
                if (syms_in_cluster, sym) in config.paytable:
                    # Calculate base win
                    sym_win = config.paytable[(syms_in_cluster, sym)]

                    # Apply global multiplier (from Addiction Meter bonuses)
                    symwin_mult = sym_win * global_multiplier
                    total_cascade_win += symwin_mult

                    json_positions = [{"reel": p[0], "row": p[1]} for p in cluster]
                    central_pos = Cluster.get_central_cluster_position(json_positions)

                    cascade_data["wins"].append({
                        "symbol": sym,
                        "clusterSize": syms_in_cluster,
                        "win": symwin_mult,
                        "positions": json_positions,
                        "meta": {
                            "globalMult": global_multiplier,
                            "winWithoutMult": sym_win,
                            "overlay": {"reel": central_pos[0], "row": central_pos[1]},
                        },
                    })

                    # Mark these symbols for degradation (not explosion!)
                    for pos in cluster:
                        symbols_to_degrade.append({
                            "reel": pos[0],
                            "row": pos[1],
                            "symbol": sym
                        })

        # Step 2: Apply REPUTATION DECAY - degrade winning symbols
        has_more_cascades = False

        for symbol_info in symbols_to_degrade:
            reel = symbol_info["reel"]
            row = symbol_info["row"]
            current_sym = symbol_info["symbol"]

            # Check if symbol can degrade
            if current_sym in config.reputation_tiers:
                tier_info = config.reputation_tiers[current_sym]
                downgraded_symbol = tier_info["downgrades_to"]

                # Apply degradation
                board[reel][row].symbol = downgraded_symbol

                cascade_data["degradations"].append({
                    "reel": reel,
                    "row": row,
                    "from": current_sym,
                    "to": downgraded_symbol,
                    "tier": tier_info["tier_name"]
                })

                # If degraded to EGG, mark for explosion (finally disappears)
                if downgraded_symbol == "EGG":
                    board[reel][row].explode = True

                has_more_cascades = True  # Degraded symbols can form new clusters

        # Step 3: Update Addiction Meter
        if total_cascade_win > 0:
            addiction_meter = min(
                addiction_meter + config.addiction_meter["fill_per_cascade"],
                config.addiction_meter["max_value"]
            )
            cascade_data["addiction_meter_after"] = addiction_meter

            # Check for Addiction Meter threshold bonuses
            addiction_effects = self._check_addiction_thresholds(
                config,
                addiction_meter,
                cascade_data["addiction_meter_before"]
            )
            if addiction_effects:
                cascade_data["addiction_effects"] = addiction_effects

        # Step 4: Update return data
        return_data["totalWin"] += total_cascade_win
        return_data["wins"].extend(cascade_data["wins"])
        return_data["cascades"].append(cascade_data)

        return board, return_data, addiction_meter, has_more_cascades

    def _check_addiction_thresholds(
        self,
        config: Config,
        current_value: int,
        previous_value: int
    ) -> List[Dict]:
        """
        Check if Addiction Meter crossed any thresholds and apply effects:
        - 25%: "Buzzed" - 2x wild multiplier spawns
        - 50%: "Tipsy" - Random symbol morphs into wilds
        - 75%: "Wasted" - Entire reel becomes sticky wild
        - 100%: "Blackout" - Triggers random feature upgrade
        """
        effects = []
        thresholds = config.addiction_meter["thresholds"]

        for threshold, effect_name in sorted(thresholds.items()):
            if previous_value < threshold <= current_value:
                effects.append({
                    "threshold": threshold,
                    "effect": effect_name,
                    "triggered": True
                })

        return effects

    def apply_dysfunction_wild_behavior(
        self,
        config: Config,
        board: Board,
        wild_type: str,
        position: Tuple[int, int]
    ) -> Board:
        """
        Apply special Dysfunction Wild behaviors:
        - Narco-mon Wild: Duplicates 2-4 times randomly
        - Rage Wild: Converts adjacent symbols to matching
        - Crisis Wild: Becomes best symbol for clusters
        - Therapy Wild: Must appear in pairs
        """
        reel, row = position
        wild_config = config.dysfunction_wilds.get(wild_type)

        if not wild_config:
            return board

        behavior = wild_config["behavior"]

        if behavior == "duplicate" and random.random() < wild_config["trigger_chance"]:
            # Narco-mon: Duplicate 2-4 times
            dup_count = random.randint(*wild_config["duplicate_count"])
            positions_to_duplicate = self._get_random_empty_positions(board, dup_count)

            for dup_pos in positions_to_duplicate:
                board[dup_pos[0]][dup_pos[1]].symbol = wild_config["symbol"]

        elif behavior == "convert_adjacent" and random.random() < wild_config["trigger_chance"]:
            # Rage Wild: Convert adjacent symbols
            adjacent_positions = self._get_adjacent_positions(board, reel, row)
            for adj_pos in adjacent_positions:
                adj_reel, adj_row = adj_pos
                current_sym = board[adj_reel][adj_row].symbol
                # Convert to matching symbol (pick most common adjacent)
                board[adj_reel][adj_row].symbol = current_sym

        elif behavior == "become_any" and random.random() < wild_config["trigger_chance"]:
            # Crisis Wild: Analyze board and become best symbol for clusters
            best_symbol = self._find_most_common_symbol(board, config)
            board[reel][row].symbol = best_symbol

        return board

    def _get_random_empty_positions(self, board: Board, count: int) -> List[Tuple[int, int]]:
        """Get random empty or low-value positions for wild duplication"""
        positions = []
        for reel_idx, reel in enumerate(board):
            for row_idx, cell in enumerate(reel):
                if cell.symbol not in ["WILD", "EGG"]:
                    positions.append((reel_idx, row_idx))

        return random.sample(positions, min(count, len(positions)))

    def _get_adjacent_positions(
        self,
        board: Board,
        reel: int,
        row: int
    ) -> List[Tuple[int, int]]:
        """Get all adjacent positions (up, down, left, right)"""
        adjacent = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dr, dc in directions:
            new_reel = reel + dr
            new_row = row + dc

            if (0 <= new_reel < len(board) and
                0 <= new_row < len(board[new_reel])):
                adjacent.append((new_reel, new_row))

        return adjacent

    def _find_most_common_symbol(self, board: Board, config: Config) -> str:
        """Find most common non-special symbol on board"""
        symbol_counts = {}

        for reel in board:
            for cell in reel:
                sym = cell.symbol
                if sym not in ["WILD", "EGG", "WILD_N", "WILD_R", "WILD_C", "WILD_T"]:
                    symbol_counts[sym] = symbol_counts.get(sym, 0) + 1

        if not symbol_counts:
            return "DEPR"  # Default to highest premium

        return max(symbol_counts, key=symbol_counts.get)

    def evaluate_clusters_with_addiction_meter(
        self,
        config: Config,
        board: Board,
        addiction_meter: int = 0,
        max_cascades: int = 10
    ) -> dict:
        """
        Main entry point for cluster evaluation with Reputation Decay Cascade.

        Processes multiple cascades:
        1. Find clusters
        2. Pay clusters
        3. Degrade symbols (Reputation Decay)
        4. Check for new clusters in degraded symbols
        5. Repeat until no more wins
        6. Update Addiction Meter throughout
        """
        return_data = {
            "totalWin": 0,
            "wins": [],
            "cascades": [],
            "addiction_meter_start": addiction_meter,
            "addiction_meter_end": addiction_meter,
            "max_cascades_reached": False
        }

        current_addiction = addiction_meter
        global_multiplier = 1

        for cascade_num in range(max_cascades):
            # Find all clusters on current board
            clusters = Cluster.find_clusters(config, board)

            if not clusters:
                break  # No more clusters, cascade ends

            # Apply Addiction Meter bonuses to multiplier
            if current_addiction >= 25:
                global_multiplier = 2
            if current_addiction >= 50:
                global_multiplier = 3
            if current_addiction >= 75:
                global_multiplier = 5

            # Process cascade with Reputation Decay
            board, return_data, current_addiction, has_more = self.reputation_decay_cascade(
                config=config,
                board=board,
                clusters=clusters,
                addiction_meter=current_addiction,
                global_multiplier=global_multiplier,
                return_data=return_data
            )

            # Remove exploded symbols (eggs) and apply gravity
            board = Board.remove_exploded_symbols(board)
            board = Board.apply_gravity(board, config)

            if not has_more:
                break

            if cascade_num == max_cascades - 1:
                return_data["max_cascades_reached"] = True

        return_data["addiction_meter_end"] = current_addiction
        return_data["total_cascades"] = len(return_data["cascades"])

        return return_data

    def check_scatter_triggers(
        self,
        config: Config,
        board: Board
    ) -> dict:
        """
        Check for scatter triggers:
        - 3 EGG scatters = Rehab Bonus
        - 4+ EGG scatters = Battle Bonus
        """
        scatter_count = 0
        scatter_positions = []

        for reel_idx, reel in enumerate(board):
            for row_idx, cell in enumerate(reel):
                if cell.symbol == "EGG":
                    scatter_count += 1
                    scatter_positions.append({"reel": reel_idx, "row": row_idx})

        trigger_info = {
            "scatter_count": scatter_count,
            "positions": scatter_positions,
            "bonus_triggered": None
        }

        if scatter_count >= 4:
            trigger_info["bonus_triggered"] = "battle_bonus"
        elif scatter_count == 3:
            trigger_info["bonus_triggered"] = "rehab_bonus"

        return trigger_info
