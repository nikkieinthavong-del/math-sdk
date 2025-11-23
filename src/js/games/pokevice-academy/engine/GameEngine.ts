/**
 * Poké-Vice Academy - Main Game Engine
 *
 * Orchestrates:
 * - Reputation Decay Cascade system
 * - Addiction Meter progression
 * - Cluster evaluation
 * - Bonus triggering
 */

import {
  Grid,
  Cell,
  SpinResult,
  SpinEvent,
  ClusterWin,
  Position,
  SymbolKind,
  GameConfig,
  AddictionMeter,
  ADDICTION_THRESHOLDS
} from './types';
import { ClusterMorphCascade } from './ClusterMorphCascade';
import { AddictionMeterSystem } from './AddictionMeter';

export class PokeViceGameEngine {
  private config: GameConfig;
  private cascadeEngine: ClusterMorphCascade;
  private addictionMeterSystem: AddictionMeterSystem;
  private currentAddictionMeter: number = 0;

  constructor(config: GameConfig) {
    this.config = config;
    this.cascadeEngine = new ClusterMorphCascade(config);
    this.addictionMeterSystem = new AddictionMeterSystem(config);
  }

  /**
   * Execute a complete spin:
   * 1. Generate initial grid
   * 2. Evaluate clusters
   * 3. Process Reputation Decay Cascades
   * 4. Update Addiction Meter
   * 5. Check for bonus triggers
   */
  public async executeSpin(initialGrid: Grid): Promise<SpinResult> {
    const events: SpinEvent[] = [];
    let grid = this.cloneGrid(initialGrid);

    // Event: Spin start
    events.push({
      type: 'spinStart',
      payload: { addictionMeter: this.currentAddictionMeter },
      timestamp: Date.now()
    });

    // Event: Initial grid
    events.push({
      type: 'initialGrid',
      payload: { grid: this.cloneGrid(grid) },
      timestamp: Date.now()
    });

    // Process cascades with Reputation Decay
    const cascadeResult = await this.cascadeEngine.processCascades(
      grid,
      this.currentAddictionMeter
    );

    // Update grid to final state
    grid = cascadeResult.finalGrid;

    // Update Addiction Meter
    const meterBefore = this.currentAddictionMeter;
    this.currentAddictionMeter = this.addictionMeterSystem.update(
      this.currentAddictionMeter,
      cascadeResult.totalWin > 0 ? 'cascade_win' : 'no_win'
    );

    const addictionMeter = this.addictionMeterSystem.getState(this.currentAddictionMeter);

    // Add cascade events
    cascadeResult.cascades.forEach(cascade => {
      events.push({
        type: 'reputationDecay',
        payload: cascade,
        timestamp: Date.now()
      });
    });

    // Event: Addiction meter update
    if (this.currentAddictionMeter !== meterBefore) {
      events.push({
        type: 'addictionMeterUpdate',
        payload: {
          before: meterBefore,
          after: this.currentAddictionMeter,
          addictionMeter
        },
        timestamp: Date.now()
      });

      // Check for threshold crossings
      const thresholdsCrossed = this.addictionMeterSystem.checkThresholdsCrossed(
        meterBefore,
        this.currentAddictionMeter
      );

      thresholdsCrossed.forEach(threshold => {
        events.push({
          type: 'addictionThreshold',
          payload: {
            threshold,
            effect: threshold,
            multiplier: addictionMeter.multiplier
          },
          timestamp: Date.now()
        });
      });
    }

    // Check for scatter triggers
    const scatterCount = this.countScatters(grid);
    let bonusTriggered: 'none' | 'rehab' | 'battle' = 'none';

    if (scatterCount >= 4) {
      bonusTriggered = 'battle';
      events.push({
        type: 'scatterTrigger',
        payload: { count: scatterCount, bonusType: 'battle' },
        timestamp: Date.now()
      });
    } else if (scatterCount === 3) {
      bonusTriggered = 'rehab';
      events.push({
        type: 'scatterTrigger',
        payload: { count: scatterCount, bonusType: 'rehab' },
        timestamp: Date.now()
      });
    }

    // Event: Spin end
    events.push({
      type: 'spinEnd',
      payload: {
        totalWin: cascadeResult.totalWin,
        scatterCount,
        bonusTriggered,
        addictionMeter
      },
      timestamp: Date.now()
    });

    return {
      grid,
      cascades: cascadeResult.cascades,
      totalWin: cascadeResult.totalWin,
      addictionMeter,
      scatterCount,
      bonusTriggered,
      events
    };
  }

  /**
   * Count EGG scatter symbols on grid
   */
  private countScatters(grid: Grid): number {
    let count = 0;
    for (const reel of grid) {
      for (const cell of reel) {
        if (cell.symbol === 'EGG') {
          count++;
        }
      }
    }
    return count;
  }

  /**
   * Clone grid for immutability
   */
  private cloneGrid(grid: Grid): Grid {
    return grid.map(reel =>
      reel.map(cell => ({ ...cell }))
    );
  }

  /**
   * Get current Addiction Meter value
   */
  public getAddictionMeter(): AddictionMeter {
    return this.addictionMeterSystem.getState(this.currentAddictionMeter);
  }

  /**
   * Reset Addiction Meter (for bonus games)
   */
  public resetAddictionMeter(): void {
    this.currentAddictionMeter = 0;
  }

  /**
   * Set Addiction Meter value directly (for testing)
   */
  public setAddictionMeter(value: number): void {
    this.currentAddictionMeter = Math.max(0, Math.min(100, value));
  }
}
