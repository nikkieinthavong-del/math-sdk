/**
 * Rehab Bonus Controller
 *
 * Manages the "Pokéhab Center - Mandatory Attendance" 3-scatter bonus:
 * - 3x1 vertical reel mechanics
 * - 5 Pokéball throws
 * - Target Pokémon catching system
 * - Dynamic win calculation
 */

import {
  RehabBonusConfig,
  RehabThrowResult,
  RehabBonusResult,
  SpinEvent
} from '../engine/types';

export class RehabController {
  private config: RehabBonusConfig;
  private throwsRemaining: number;
  private throwHistory: RehabThrowResult[];
  private totalWin: number;
  private nextThrowUpgraded: boolean = false;

  constructor(config: RehabBonusConfig) {
    this.config = { ...config };
    this.throwsRemaining = config.throws;
    this.throwHistory = [];
    this.totalWin = 0;
  }

  /**
   * Execute a single Pokéball throw
   */
  public executeThrow(): RehabThrowResult {
    if (this.throwsRemaining <= 0) {
      throw new Error('No throws remaining');
    }

    // Spin the 3x1 reel
    const reelResult = this.spin3x1Reel();

    const throwNumber = this.throwHistory.length + 1;
    const { ballType, catchResult, multiplier } = reelResult;

    const throwResult: RehabThrowResult = {
      throwNumber,
      ballType,
      catchResult,
      multiplier,
      win: 0,
      animation: ''
    };

    // Handle special outcomes
    if (ballType === 'RESTRAINING_ORDER') {
      this.throwsRemaining += 2; // Add 2 extra throws
      throwResult.animation = 'restraining_order_effect';
      throwResult.win = 0;
    } else if (catchResult === 'UPGRADE') {
      this.nextThrowUpgraded = true; // Next throw gets Master Ball
      throwResult.animation = 'upgrade_effect';
      throwResult.win = 0;
    } else if (catchResult === 'CATCH') {
      // Successful catch
      const catchResult = this.processCatch(ballType, multiplier);
      throwResult.caughtPokemon = catchResult.pokemonName;
      throwResult.win = catchResult.win;
      throwResult.animation = catchResult.animation;
      this.totalWin += catchResult.win;
    } else {
      // Miss
      throwResult.animation = this.getRandomMissAnimation();
    }

    this.throwsRemaining--;
    this.throwHistory.push(throwResult);

    return throwResult;
  }

  /**
   * Spin the 3x1 reel and get result
   */
  private spin3x1Reel(): {
    ballType: RehabThrowResult['ballType'];
    catchResult: RehabThrowResult['catchResult'];
    multiplier: number;
  } {
    // Position 1: Ball Type
    let ballType: RehabThrowResult['ballType'];

    if (this.nextThrowUpgraded) {
      ballType = 'MASTER_BALL';
      this.nextThrowUpgraded = false;
    } else {
      ballType = this.weightedRandom([
        { value: 'GREAT_BALL', weight: 40 },
        { value: 'ULTRA_BALL', weight: 30 },
        { value: 'MASTER_BALL', weight: 5 },
        { value: 'BEER_BALL', weight: 20 },
        { value: 'RESTRAINING_ORDER', weight: 5 }
      ]);
    }

    // Position 2: Catch Result
    const catchResult = this.weightedRandom([
      { value: 'CATCH', weight: 45 },
      { value: 'MISS', weight: 40 },
      { value: 'UPGRADE', weight: 15 }
    ]) as RehabThrowResult['catchResult'];

    // Position 3: Multiplier
    const multiplierValues = [1, 2, 3, 5, 10];
    const multiplierWeights = [40, 25, 15, 12, 8];
    const multiplierIndex = this.weightedRandomIndex(multiplierWeights);
    const multiplier = multiplierValues[multiplierIndex];

    return { ballType, catchResult, multiplier };
  }

  /**
   * Process a successful catch
   */
  private processCatch(
    ballType: RehabThrowResult['ballType'],
    multiplier: number
  ): {
    pokemonName: string;
    win: number;
    animation: string;
  } {
    // Find first uncaught target
    const uncaught = this.config.targets.filter(t => !t.caught);

    if (uncaught.length === 0) {
      // All caught - bonus win!
      return {
        pokemonName: 'ALL_CAUGHT',
        win: 100 * multiplier,
        animation: 'all_caught_bonus'
      };
    }

    // Select random uncaught target
    const target = uncaught[Math.floor(Math.random() * uncaught.length)];
    target.caught = true;

    // Calculate win based on ball type
    let basePayout = target.payout;

    // Apply ball multiplier
    const ballMultipliers: Record<string, number> = {
      GREAT_BALL: this.randomInRange(3, 5),
      ULTRA_BALL: this.randomInRange(8, 12),
      MASTER_BALL: this.randomInRange(20, 50),
      BEER_BALL: 2
    };

    const ballMult = ballMultipliers[ballType] || 1;

    // Total win = base * ball multiplier * reel multiplier
    const win = basePayout * ballMult * multiplier;

    // Get catch animation
    const animations: Record<string, string> = {
      'SOBBLE-TER': 'sobble_caught_therapy',
      'SLAK-OFF': 'slakoff_got_job',
      'WHIS-MURRR': 'whismur_gossip_seized',
      'RATT-ITUDE': 'rattitude_anger_management'
    };

    return {
      pokemonName: target.name,
      win,
      animation: animations[target.name] || 'generic_catch'
    };
  }

  /**
   * Get random miss animation
   */
  private getRandomMissAnimation(): string {
    const animations = [
      'dodge_cigarette',
      'pawns_ball',
      'restraining_order_bounce'
    ];
    return animations[Math.floor(Math.random() * animations.length)];
  }

  /**
   * Check if all targets caught
   */
  public allTargetsCaught(): boolean {
    return this.config.targets.every(t => t.caught);
  }

  /**
   * Get current state
   */
  public getState(): {
    throwsRemaining: number;
    totalWin: number;
    targets: typeof this.config.targets;
    throwHistory: RehabThrowResult[];
  } {
    return {
      throwsRemaining: this.throwsRemaining,
      totalWin: this.totalWin,
      targets: this.config.targets,
      throwHistory: [...this.throwHistory]
    };
  }

  /**
   * Play full bonus and return result
   */
  public playFullBonus(): RehabBonusResult {
    const events: SpinEvent[] = [];

    // Start event
    events.push({
      type: 'rehabBonusStart',
      payload: {
        throws: this.config.throws,
        targets: this.config.targets
      },
      timestamp: Date.now()
    });

    // Execute all throws
    while (this.throwsRemaining > 0 && !this.allTargetsCaught()) {
      const throwResult = this.executeThrow();

      events.push({
        type: 'rehabBonusThrow',
        payload: throwResult,
        timestamp: Date.now()
      });
    }

    // End event
    events.push({
      type: 'rehabBonusEnd',
      payload: {
        totalWin: this.totalWin,
        targetsCaught: this.config.targets.filter(t => t.caught).length,
        totalTargets: this.config.targets.length
      },
      timestamp: Date.now()
    });

    return {
      totalWin: this.totalWin,
      throws: this.throwHistory,
      targetsCaught: this.config.targets.filter(t => t.caught).length,
      totalTargets: this.config.targets.length
    };
  }

  // Utility methods
  private weightedRandom<T>(items: Array<{ value: T; weight: number }>): T {
    const totalWeight = items.reduce((sum, item) => sum + item.weight, 0);
    let random = Math.random() * totalWeight;

    for (const item of items) {
      random -= item.weight;
      if (random <= 0) {
        return item.value;
      }
    }

    return items[items.length - 1].value;
  }

  private weightedRandomIndex(weights: number[]): number {
    const totalWeight = weights.reduce((sum, w) => sum + w, 0);
    let random = Math.random() * totalWeight;

    for (let i = 0; i < weights.length; i++) {
      random -= weights[i];
      if (random <= 0) {
        return i;
      }
    }

    return weights.length - 1;
  }

  private randomInRange(min: number, max: number): number {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }
}
