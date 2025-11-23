"""Optimization setup for Poké-Vice Academy"""

from src.config.distributions import Optimization


class OptimizationSetup:
    """
    Optimization parameters for Poké-Vice Academy.

    Targets:
    - Base Game RTP: 68% of total
    - Rehab Bonus RTP: 18% of total
    - Battle Bonus RTP: 14% of total
    - Total RTP: 94%, 96%, or 98% (configurable)
    """

    def __init__(self, config):
        self.config = config

        # Target RTP breakdown
        self.base_rtp_contribution = 0.68  # 68% from base game
        self.rehab_bonus_contribution = 0.18  # 18% from rehab bonus
        self.battle_bonus_contribution = 0.14  # 14% from battle bonus

        # Optimization parameters
        self.optimizations = self._setup_optimizations()

    def _setup_optimizations(self):
        """
        Set up optimization targets for each bet mode.

        The optimization system will adjust symbol weights to hit these targets.
        """
        optimizations = []

        # Base mode optimization
        base_target_rtp = self.config.rtp * self.base_rtp_contribution

        base_opt = Optimization(
            rtp=base_target_rtp,
            avgWin=None,  # Let optimizer find natural average
            hit_rate=0.28,  # 28% hit frequency (every ~3.5 spins)
            recordConditions={
                "criteria": ["basegame"],
                "gametype": [self.config.basegame_type]
            }
        )
        optimizations.append(("base", base_opt))

        return optimizations

    def get_optimization_for_mode(self, mode_name: str):
        """Get optimization parameters for a specific bet mode"""
        for name, opt in self.optimizations:
            if name == mode_name:
                return opt
        return None
