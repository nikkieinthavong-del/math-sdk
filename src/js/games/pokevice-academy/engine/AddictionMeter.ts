/**
 * Addiction Meter System
 *
 * Dynamic volatility system that tracks player's cascade performance:
 * - Fills +10% per cascade win
 * - Decays -5% per non-winning spin
 * - Provides multiplier bonuses at thresholds
 * - Triggers special effects
 */

import { AddictionMeter, ADDICTION_THRESHOLDS, GameConfig } from './types';

export type AddictionEvent = 'cascade_win' | 'no_win';

export class AddictionMeterSystem {
  private config: GameConfig;

  constructor(config: GameConfig) {
    this.config = config;
  }

  /**
   * Update Addiction Meter based on spin outcome
   */
  public update(currentValue: number, event: AddictionEvent): number {
    let newValue = currentValue;

    if (event === 'cascade_win') {
      // Fill meter on cascade win
      newValue += this.config.addictionMeter.fillPerCascade;
    } else if (event === 'no_win') {
      // Decay meter on non-winning spin
      newValue -= this.config.addictionMeter.decayPerSpin;
    }

    // Clamp to 0-100 range
    return Math.max(0, Math.min(this.config.addictionMeter.maxValue, newValue));
  }

  /**
   * Get current state with threshold and multiplier
   */
  public getState(value: number): AddictionMeter {
    const threshold = this.getThreshold(value);
    const multiplier = this.getMultiplier(value);

    return {
      value,
      threshold,
      multiplier
    };
  }

  /**
   * Get current threshold level
   */
  private getThreshold(value: number): AddictionMeter['threshold'] {
    if (value >= ADDICTION_THRESHOLDS.blackout) return 'blackout';
    if (value >= ADDICTION_THRESHOLDS.wasted) return 'wasted';
    if (value >= ADDICTION_THRESHOLDS.tipsy) return 'tipsy';
    if (value >= ADDICTION_THRESHOLDS.buzzed) return 'buzzed';
    return 'sober';
  }

  /**
   * Get multiplier based on current value
   */
  private getMultiplier(value: number): number {
    if (value >= ADDICTION_THRESHOLDS.blackout) return 10; // 100%: Blackout
    if (value >= ADDICTION_THRESHOLDS.wasted) return 5;    // 75%: Wasted
    if (value >= ADDICTION_THRESHOLDS.tipsy) return 3;     // 50%: Tipsy
    if (value >= ADDICTION_THRESHOLDS.buzzed) return 2;    // 25%: Buzzed
    return 1;                                               // 0%: Sober
  }

  /**
   * Check which thresholds were crossed between two values
   */
  public checkThresholdsCrossed(
    previousValue: number,
    currentValue: number
  ): AddictionMeter['threshold'][] {
    const crossed: AddictionMeter['threshold'][] = [];

    const thresholds: Array<[number, AddictionMeter['threshold']]> = [
      [ADDICTION_THRESHOLDS.buzzed, 'buzzed'],
      [ADDICTION_THRESHOLDS.tipsy, 'tipsy'],
      [ADDICTION_THRESHOLDS.wasted, 'wasted'],
      [ADDICTION_THRESHOLDS.blackout, 'blackout']
    ];

    for (const [threshold, name] of thresholds) {
      if (previousValue < threshold && currentValue >= threshold) {
        crossed.push(name);
      }
    }

    return crossed;
  }

  /**
   * Get effect description for threshold
   */
  public getThresholdEffect(threshold: AddictionMeter['threshold']): string {
    const effects: Record<AddictionMeter['threshold'], string> = {
      sober: 'Normal gameplay (1x multiplier)',
      buzzed: '2x wild multiplier spawns (2x global multiplier)',
      tipsy: 'Random symbols morph into wilds (3x global multiplier)',
      wasted: 'Entire reel becomes sticky wild (5x global multiplier)',
      blackout: 'Random feature upgrade mid-spin (10x global multiplier)'
    };

    return effects[threshold];
  }

  /**
   * Render Addiction Meter for UI
   * Returns percentage fill and visual state
   */
  public renderMeter(value: number): {
    percentage: number;
    threshold: AddictionMeter['threshold'];
    multiplier: number;
    color: string;
    label: string;
  } {
    const state = this.getState(value);
    const percentage = (value / this.config.addictionMeter.maxValue) * 100;

    // Visual styling based on threshold
    const colors: Record<AddictionMeter['threshold'], string> = {
      sober: '#4CAF50',      // Green
      buzzed: '#FFC107',     // Amber
      tipsy: '#FF9800',      // Orange
      wasted: '#F44336',     // Red
      blackout: '#9C27B0'    // Purple
    };

    const labels: Record<AddictionMeter['threshold'], string> = {
      sober: 'SOBER',
      buzzed: 'BUZZED 🍺',
      tipsy: 'TIPSY 🥴',
      wasted: 'WASTED 💀',
      blackout: 'BLACKOUT ⚡'
    };

    return {
      percentage,
      threshold: state.threshold,
      multiplier: state.multiplier,
      color: colors[state.threshold],
      label: labels[state.threshold]
    };
  }

  /**
   * Trigger special effect based on threshold crossing
   */
  public triggerThresholdEffect(
    threshold: AddictionMeter['threshold'],
    grid: any // Grid reference for applying effects
  ): {
    effectType: string;
    description: string;
    gridModifications?: any;
  } {
    switch (threshold) {
      case 'buzzed':
        return {
          effectType: 'multiplier_boost',
          description: '2x wild multiplier activated!',
          gridModifications: {
            globalMultiplier: 2
          }
        };

      case 'tipsy':
        return {
          effectType: 'wild_morph',
          description: 'Random symbols morphing into wilds!',
          gridModifications: {
            globalMultiplier: 3,
            wildMorphCount: Math.floor(Math.random() * 3) + 2 // 2-4 wilds
          }
        };

      case 'wasted':
        return {
          effectType: 'sticky_wild_reel',
          description: 'Entire reel becomes sticky wild!',
          gridModifications: {
            globalMultiplier: 5,
            stickyWildReel: Math.floor(Math.random() * 6) // Random reel 0-5
          }
        };

      case 'blackout':
        return {
          effectType: 'feature_upgrade',
          description: 'BLACKOUT BONUS! Feature upgrade activated!',
          gridModifications: {
            globalMultiplier: 10,
            upgradeBonus: true,
            guaranteedScatter: true // Guarantee scatter symbol spawn
          }
        };

      default:
        return {
          effectType: 'none',
          description: 'Normal gameplay'
        };
    }
  }

  /**
   * Reset meter (for bonus games)
   */
  public reset(): number {
    return 0;
  }
}
