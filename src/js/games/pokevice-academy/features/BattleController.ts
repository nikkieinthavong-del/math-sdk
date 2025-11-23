/**
 * Battle Bonus Controller
 *
 * Manages the "Dysfunction Duel" 4-scatter bonus:
 * - RPG-style battle system
 * - 3x1 attack reel
 * - 4 rounds of opponents
 * - Progressive multiplier
 * - Mega win potential (1,000x-5,000x)
 */

import {
  BattleOpponent,
  BattleTurnResult,
  BattleRoundResult,
  BattleBonusResult,
  SpinEvent
} from '../engine/types';

export class BattleController {
  private playerHP: number;
  private playerMaxHP: number;
  private spinsRemaining: number;
  private multiplier: number;
  private totalWin: number;
  private currentRound: number;
  private currentOpponent: BattleOpponent | null;
  private battleLog: SpinEvent[];
  private roundResults: BattleRoundResult[];
  private opponentFrozenTurns: number;

  private readonly opponents: BattleOpponent[] = [
    {
      name: 'INTERN_JENNY',
      hp: 80,
      maxHp: 80,
      attacks: [
        { name: 'Overtime Burnout', damage: 15 },
        { name: 'Coffee Withdrawal', damage: 20 }
      ]
    },
    {
      name: 'OFFICER_GRUMPY',
      hp: 150,
      maxHp: 150,
      attacks: [
        { name: 'Bribery Bite', damage: 25 },
        { name: 'Warrant Strike', damage: 35 },
        { name: 'Taser Fang', damage: 45, effect: 'critical' }
      ]
    },
    {
      name: 'CHAMPION_KAREN',
      hp: 250,
      maxHp: 250,
      attacks: [
        { name: 'Speak to Your Manager', damage: 40, effect: 'stun' },
        { name: 'Lawsuit Lash', damage: 50 },
        { name: 'Yelp Review', damage: 30, effect: 'debuff' }
      ]
    },
    {
      name: 'PROFESSOR_REHAB',
      hp: 400,
      maxHp: 400,
      attacks: [
        { name: 'Gaslighting Pulse', damage: 35, effect: 'confusion' },
        { name: 'Prescription Overload', damage: 60 },
        { name: 'Insurance Fraud', damage: 80, effect: 'critical' }
      ]
    }
  ];

  constructor(startingSpins: number = 5, playerHP: number = 100) {
    this.playerHP = playerHP;
    this.playerMaxHP = playerHP;
    this.spinsRemaining = startingSpins;
    this.multiplier = 1.0;
    this.totalWin = 0;
    this.currentRound = 0;
    this.currentOpponent = null;
    this.battleLog = [];
    this.roundResults = [];
    this.opponentFrozenTurns = 0;
  }

  /**
   * Start a new round with the next opponent
   */
  public startRound(roundNumber: number): void {
    if (roundNumber >= this.opponents.length) {
      throw new Error('No more opponents');
    }

    this.currentRound = roundNumber;
    this.currentOpponent = { ...this.opponents[roundNumber] };

    this.battleLog.push({
      type: 'battleBonusStart',
      payload: {
        round: roundNumber + 1,
        opponent: this.currentOpponent.name,
        opponentHP: this.currentOpponent.hp
      },
      timestamp: Date.now()
    });
  }

  /**
   * Execute a single battle turn
   */
  public executeTurn(): BattleTurnResult | null {
    if (!this.currentOpponent || this.spinsRemaining <= 0) {
      return null;
    }

    // Spin the 3x1 battle reel
    const reelResult = this.spin3x1BattleReel();
    const [moveType, powerLevel, bonusEffect] = reelResult;

    const playerHPBefore = this.playerHP;
    const opponentHPBefore = this.currentOpponent.hp;
    const multiplierBefore = this.multiplier;

    // Execute player action based on reel
    let playerAction: BattleTurnResult['playerAction'];

    switch (moveType) {
      case 'ATTACK':
        playerAction = this.executeAttack(powerLevel);
        break;
      case 'DEFEND':
        playerAction = this.executeDefense(powerLevel);
        break;
      case 'ITEM':
        playerAction = this.useItem();
        break;
      default:
        playerAction = { type: 'attack', name: 'Default', damage: 0 };
    }

    // Apply bonus effect from position 3
    this.applyBonusEffect(bonusEffect);

    // Opponent attacks (if not frozen and player didn't dodge)
    let opponentAction: BattleTurnResult['opponentAction'] | undefined;

    if (this.opponentFrozenTurns > 0) {
      this.opponentFrozenTurns--;
    } else if (playerAction.type !== 'defend' || !playerAction.effect?.includes('dodge')) {
      opponentAction = this.opponentAttack();
    }

    // Consume spin
    this.spinsRemaining--;

    const turnResult: BattleTurnResult = {
      turnNumber: this.battleLog.filter(e => e.type === 'battleBonusTurn').length + 1,
      reelResult: [moveType, powerLevel, bonusEffect],
      playerAction,
      opponentAction,
      playerHpAfter: this.playerHP,
      opponentHpAfter: this.currentOpponent.hp,
      multiplierAfter: this.multiplier
    };

    this.battleLog.push({
      type: 'battleBonusTurn',
      payload: turnResult,
      timestamp: Date.now()
    });

    return turnResult;
  }

  /**
   * Spin the 3x1 battle reel
   */
  private spin3x1BattleReel(): [string, string, string] {
    const moveType = this.weightedRandom([
      { value: 'ATTACK', weight: 50 },
      { value: 'DEFEND', weight: 30 },
      { value: 'ITEM', weight: 20 }
    ]);

    const powerLevel = this.weightedRandom([
      { value: 'WEAK', weight: 40 },
      { value: 'MEDIUM', weight: 35 },
      { value: 'STRONG', weight: 20 },
      { value: 'CRITICAL', weight: 5 }
    ]);

    const bonusEffect = this.weightedRandom([
      { value: 'NONE', weight: 50 },
      { value: 'MULTIPLIER_0.5', weight: 20 },
      { value: 'EXTRA_SPIN', weight: 20 },
      { value: 'HEAL_10', weight: 10 }
    ]);

    return [moveType, powerLevel, bonusEffect];
  }

  /**
   * Execute player attack
   */
  private executeAttack(powerLevel: string): BattleTurnResult['playerAction'] {
    const damages: Record<string, number> = {
      WEAK: 15,
      MEDIUM: 25,
      STRONG: 35,
      CRITICAL: 50
    };

    const damage = damages[powerLevel] || 15;
    const isCritical = powerLevel === 'CRITICAL';

    // Apply damage to opponent
    if (this.currentOpponent) {
      this.currentOpponent.hp -= damage;
    }

    // Update multiplier
    this.multiplier += isCritical ? 1.0 : 0.5;

    return {
      type: 'attack',
      name: `${powerLevel} Attack`,
      damage,
      effect: isCritical ? 'critical' : undefined
    };
  }

  /**
   * Execute player defense
   */
  private executeDefense(powerLevel: string): BattleTurnResult['playerAction'] {
    const heals: Record<string, number> = {
      WEAK: 10,
      MEDIUM: 15,
      STRONG: 25,
      CRITICAL: 25
    };

    const heal = Math.min(heals[powerLevel] || 10, this.playerMaxHP - this.playerHP);
    this.playerHP += heal;

    // Defense may grant extra spin
    if (powerLevel === 'STRONG' || powerLevel === 'CRITICAL') {
      this.spinsRemaining += 1;
    }

    return {
      type: 'defend',
      name: `${powerLevel} Defense`,
      heal,
      effect: powerLevel === 'CRITICAL' ? 'dodge' : undefined
    };
  }

  /**
   * Use random item
   */
  private useItem(): BattleTurnResult['playerAction'] {
    const items = [
      { name: 'ENERGY_DRINK', effect: 'spins_3_attack_10' },
      { name: 'CIGARETTE_BREAK', effect: 'spins_1_heal_10' },
      { name: 'RESTRAINING_ORDER', effect: 'freeze_2' },
      { name: 'ADDERALL', effect: 'guarantee_critical' }
    ];

    const item = items[Math.floor(Math.random() * items.length)];

    // Apply item effects
    switch (item.effect) {
      case 'spins_3_attack_10':
        this.spinsRemaining += 3;
        return { type: 'item', name: item.name, effect: '+3 spins, +10 attack next turn' };
      case 'spins_1_heal_10':
        this.spinsRemaining += 1;
        this.playerHP = Math.min(this.playerHP + 10, this.playerMaxHP);
        return { type: 'item', name: item.name, heal: 10 };
      case 'freeze_2':
        this.opponentFrozenTurns = 2;
        return { type: 'item', name: item.name, effect: 'Opponent frozen 2 turns' };
      case 'guarantee_critical':
        return { type: 'item', name: item.name, effect: 'Next attack critical' };
      default:
        return { type: 'item', name: item.name };
    }
  }

  /**
   * Opponent attack
   */
  private opponentAttack(): BattleTurnResult['opponentAction'] {
    if (!this.currentOpponent || this.currentOpponent.attacks.length === 0) {
      return undefined;
    }

    const attack = this.currentOpponent.attacks[
      Math.floor(Math.random() * this.currentOpponent.attacks.length)
    ];

    // Apply damage to player
    this.playerHP -= attack.damage;

    // Apply special effects
    if (attack.effect === 'debuff') {
      this.multiplier = Math.max(1.0, this.multiplier - 0.5);
    }

    return {
      attackName: attack.name,
      damage: attack.damage
    };
  }

  /**
   * Apply bonus effect from reel position 3
   */
  private applyBonusEffect(effect: string): void {
    switch (effect) {
      case 'MULTIPLIER_0.5':
        this.multiplier += 0.5;
        break;
      case 'EXTRA_SPIN':
        this.spinsRemaining += 1;
        break;
      case 'HEAL_10':
        this.playerHP = Math.min(this.playerHP + 10, this.playerMaxHP);
        break;
    }
  }

  /**
   * Check round status
   */
  public checkRoundStatus(): 'victory' | 'defeat' | 'continue' | 'no_spins' {
    if (this.playerHP <= 0) {
      return 'defeat';
    }

    if (this.currentOpponent && this.currentOpponent.hp <= 0) {
      return 'victory';
    }

    if (this.spinsRemaining <= 0) {
      return 'no_spins';
    }

    return 'continue';
  }

  /**
   * Complete current round
   */
  public completeRound(): BattleRoundResult {
    const status = this.checkRoundStatus();
    const roundWin = status === 'victory' ? this.calculateRoundWin() : 0;

    const result: BattleRoundResult = {
      roundNumber: this.currentRound + 1,
      opponent: this.currentOpponent?.name || '',
      outcome: status === 'victory' ? 'victory' : status === 'no_spins' ? 'no_spins' : 'defeat',
      turns: this.battleLog
        .filter(e => e.type === 'battleBonusTurn')
        .map(e => e.payload as BattleTurnResult),
      roundWin
    };

    if (status === 'victory') {
      this.totalWin += roundWin;
    }

    this.roundResults.push(result);
    return result;
  }

  /**
   * Calculate round win with multiplier
   */
  private calculateRoundWin(): number {
    const baseRewards = [50, 150, 500, 1500]; // Rewards for each round
    const baseReward = baseRewards[this.currentRound] || 50;
    return baseReward * this.multiplier;
  }

  /**
   * Play full battle
   */
  public playFullBattle(): BattleBonusResult {
    for (let round = 0; round < this.opponents.length; round++) {
      this.startRound(round);

      // Battle until round ends
      while (this.checkRoundStatus() === 'continue') {
        this.executeTurn();
      }

      const roundResult = this.completeRound();

      // Stop if defeated or out of spins
      if (roundResult.outcome !== 'victory') {
        break;
      }

      // Award bonus spins for victory
      const bonusSpins = [3, 5, 10, 0][round];
      this.spinsRemaining += bonusSpins;
    }

    const finalStatus =
      this.playerHP <= 0
        ? 'defeated'
        : this.currentRound >= this.opponents.length - 1
        ? 'victory'
        : 'ran_out_of_spins';

    return {
      totalWin: this.totalWin,
      rounds: this.roundResults,
      roundsCompleted: this.roundResults.filter(r => r.outcome === 'victory').length,
      finalStatus,
      finalMultiplier: this.multiplier
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

  /**
   * Get current state
   */
  public getState() {
    return {
      playerHP: this.playerHP,
      playerMaxHP: this.playerMaxHP,
      opponentHP: this.currentOpponent?.hp || 0,
      opponentMaxHP: this.currentOpponent?.maxHp || 0,
      spinsRemaining: this.spinsRemaining,
      multiplier: this.multiplier,
      currentRound: this.currentRound,
      totalWin: this.totalWin
    };
  }
}
