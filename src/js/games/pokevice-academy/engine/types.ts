/**
 * Poké-Vice Academy - TypeScript Type Definitions
 * "Gotta Catch These Hands"
 */

export type SymbolKind =
  // Premium symbols
  | 'DEPR' // Depresso - Legendary
  | 'RAGE' // RageApe - Evolved
  | 'SLAK' // Slak-Addict - Basic
  | 'KARE' // Karena - Basic

  // Mid symbols
  | 'METH' // Methadone-Pod
  | 'CIGA' // Cigar-itt

  // Low symbols
  | 'BEER' // Beer Bottle
  | 'PILL' // Pill Bottle
  | 'CIGT' // Cigarette
  | 'TICK' // Parking Ticket

  // Special symbols
  | 'WILD' // Therapy Couch Wild
  | 'EGG'  // Egg Scatter

  // Dysfunction Wilds
  | 'WILD_N' // Narco-mon Wild
  | 'WILD_R' // Rage Wild
  | 'WILD_C' // Crisis Wild
  | 'WILD_T'; // Therapy Wild (paired)

export type ReputationTier =
  | 'legendary'   // Tier 3 (DEPR)
  | 'evolved'     // Tier 2 (RAGE)
  | 'basic'       // Tier 1 (SLAK, KARE, METH)
  | 'egg-ready'   // Tier 0 (Low symbols, degrades to EGG)
  | 'egg';        // Final form (vanishes)

export interface Cell {
  symbol: SymbolKind;
  tier: ReputationTier;
  degraded: boolean; // Marked if degraded this cascade
}

export type Grid = Cell[][];
export type Position = { reel: number; row: number };

// ADDICTION METER
export interface AddictionMeter {
  value: number; // 0-100
  threshold: 'sober' | 'buzzed' | 'tipsy' | 'wasted' | 'blackout';
  multiplier: number; // Global multiplier based on threshold
}

export const ADDICTION_THRESHOLDS = {
  sober: 0,
  buzzed: 25,
  tipsy: 50,
  wasted: 75,
  blackout: 100
} as const;

// CLUSTER WIN
export interface ClusterWin {
  symbol: SymbolKind;
  positions: Position[];
  size: number;
  payout: number;
  multiplier: number;
  totalWin: number;
}

// REPUTATION DECAY CASCADE
export interface ReputationDecay {
  cascadeNumber: number;
  degradations: Array<{
    position: Position;
    from: SymbolKind;
    to: SymbolKind;
    tier: ReputationTier;
  }>;
  newClusters: ClusterWin[];
  addictionMeterBefore: number;
  addictionMeterAfter: number;
}

// SPIN EVENTS
export interface SpinEvent {
  type:
    | 'spinStart'
    | 'initialGrid'
    | 'clusterWin'
    | 'reputationDecay'
    | 'cascadeComplete'
    | 'addictionMeterUpdate'
    | 'addictionThreshold'
    | 'dysfunctionWildTrigger'
    | 'scatterTrigger'
    | 'rehabBonusStart'
    | 'rehabBonusThrow'
    | 'rehabBonusEnd'
    | 'battleBonusStart'
    | 'battleBonusTurn'
    | 'battleBonusRoundEnd'
    | 'battleBonusEnd'
    | 'spinEnd';
  payload?: any;
  timestamp?: number;
}

// SPIN RESULT
export interface SpinResult {
  grid: Grid;
  cascades: ReputationDecay[];
  totalWin: number;
  addictionMeter: AddictionMeter;
  scatterCount: number;
  bonusTriggered: 'none' | 'rehab' | 'battle';
  events: SpinEvent[];
}

// REHAB BONUS (3-SCATTER)
export interface RehabBonusConfig {
  throws: number;
  targets: Array<{
    name: string;
    count: number;
    payout: number;
    caught: boolean;
  }>;
}

export interface RehabThrowResult {
  throwNumber: number;
  ballType: 'GREAT_BALL' | 'ULTRA_BALL' | 'MASTER_BALL' | 'BEER_BALL' | 'RESTRAINING_ORDER';
  catchResult: 'CATCH' | 'MISS' | 'UPGRADE';
  multiplier: number;
  caughtPokemon?: string;
  win: number;
  animation: string;
}

export interface RehabBonusResult {
  totalWin: number;
  throws: RehabThrowResult[];
  targetsCaught: number;
  totalTargets: number;
}

// BATTLE BONUS (4-SCATTER)
export interface BattleOpponent {
  name: string;
  hp: number;
  maxHp: number;
  attacks: Array<{
    name: string;
    damage: number;
    effect?: string;
  }>;
}

export interface BattleTurnResult {
  turnNumber: number;
  reelResult: [string, string, string]; // [MOVE_TYPE, POWER_LEVEL, BONUS_EFFECT]
  playerAction: {
    type: 'attack' | 'defend' | 'item';
    name: string;
    damage?: number;
    heal?: number;
    effect?: string;
  };
  opponentAction?: {
    attackName: string;
    damage: number;
  };
  playerHpAfter: number;
  opponentHpAfter: number;
  multiplierAfter: number;
}

export interface BattleRoundResult {
  roundNumber: number;
  opponent: string;
  outcome: 'victory' | 'defeat' | 'no_spins';
  turns: BattleTurnResult[];
  roundWin: number;
}

export interface BattleBonusResult {
  totalWin: number;
  rounds: BattleRoundResult[];
  roundsCompleted: number;
  finalStatus: 'victory' | 'defeated' | 'ran_out_of_spins';
  finalMultiplier: number;
}

// GAME CONFIG
export interface GameConfig {
  gridSize: {
    reels: number;
    rows: number;
  };
  minClusterSize: number;
  paytable: Map<string, Map<number, number>>; // symbol -> clusterSize -> payout
  addictionMeter: {
    maxValue: number;
    fillPerCascade: number;
    decayPerSpin: number;
  };
  reputationTiers: Map<SymbolKind, {
    tier: number;
    degradesTo: SymbolKind;
    tierName: string;
  }>;
}
