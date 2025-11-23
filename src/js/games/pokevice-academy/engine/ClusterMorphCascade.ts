/**
 * Cluster Morph Cascade - Reputation Decay System
 *
 * Core Innovation: Instead of symbols exploding, they DEGRADE through tiers:
 * Legendary (DEPR) → Evolved (RAGE) → Basic (SLAK/KARE) → Egg-Ready → EGG (vanish)
 *
 * This creates cascading chain reactions as degraded symbols form new clusters.
 */

import {
  Grid,
  Cell,
  ClusterWin,
  Position,
  SymbolKind,
  ReputationDecay,
  GameConfig,
  ReputationTier
} from './types';

export interface CascadeResult {
  finalGrid: Grid;
  cascades: ReputationDecay[];
  totalWin: number;
}

export class ClusterMorphCascade {
  private config: GameConfig;
  private maxCascades = 10;

  // Symbol degradation mapping
  private readonly degradationMap: Map<SymbolKind, SymbolKind> = new Map([
    // Premium degradation chain
    ['DEPR', 'RAGE'],  // Legendary → Evolved
    ['RAGE', 'SLAK'],  // Evolved → Basic
    ['SLAK', 'KARE'],  // Basic → Basic
    ['KARE', 'EGG'],   // Basic → Egg

    // Mid degradation chain
    ['METH', 'CIGA'],  // Mid → Mid
    ['CIGA', 'EGG'],   // Mid → Egg

    // Low symbols degrade directly to EGG
    ['BEER', 'EGG'],
    ['PILL', 'EGG'],
    ['CIGT', 'EGG'],
    ['TICK', 'EGG'],
  ]);

  constructor(config: GameConfig) {
    this.config = config;
  }

  /**
   * Process all cascades for a spin until no more wins
   */
  public async processCascades(
    initialGrid: Grid,
    addictionMeter: number
  ): Promise<CascadeResult> {
    let grid = this.cloneGrid(initialGrid);
    const cascades: ReputationDecay[] = [];
    let totalWin = 0;
    let cascadeNumber = 0;

    // Calculate global multiplier from Addiction Meter
    const globalMultiplier = this.getAddictionMultiplier(addictionMeter);

    while (cascadeNumber < this.maxCascades) {
      // Find all clusters on current grid
      const clusters = this.findClusters(grid);

      if (clusters.length === 0) {
        break; // No more wins, cascade ends
      }

      // Calculate wins for these clusters
      const clusterWins = this.evaluateClusters(clusters, globalMultiplier);
      const cascadeWin = clusterWins.reduce((sum, win) => sum + win.totalWin, 0);
      totalWin += cascadeWin;

      // Apply Reputation Decay - degrade winning symbols
      const degradations = this.applyReputationDecay(grid, clusters);

      // Store cascade data
      cascades.push({
        cascadeNumber: cascadeNumber + 1,
        degradations,
        newClusters: clusterWins,
        addictionMeterBefore: addictionMeter,
        addictionMeterAfter: addictionMeter + this.config.addictionMeter.fillPerCascade
      });

      // Remove EGG symbols (finally vanish) and apply gravity
      grid = this.removeEggsAndApplyGravity(grid);

      cascadeNumber++;
    }

    return {
      finalGrid: grid,
      cascades,
      totalWin
    };
  }

  /**
   * Find all clusters (connected groups of matching symbols)
   * Minimum size: 5 symbols
   */
  private findClusters(grid: Grid): Array<{symbol: SymbolKind; positions: Position[]}> {
    const visited = new Set<string>();
    const clusters: Array<{symbol: SymbolKind; positions: Position[]}> = [];

    for (let reel = 0; reel < grid.length; reel++) {
      for (let row = 0; row < grid[reel].length; row++) {
        const key = `${reel},${row}`;
        if (visited.has(key)) continue;

        const symbol = grid[reel][row].symbol;

        // Skip special symbols (except wilds are evaluated separately)
        if (symbol === 'EGG') continue;

        // Find connected cluster
        const cluster = this.floodFillCluster(grid, reel, row, symbol, visited);

        // Check minimum cluster size
        if (cluster.length >= this.config.minClusterSize) {
          clusters.push({ symbol, positions: cluster });
        }
      }
    }

    return clusters;
  }

  /**
   * Flood fill algorithm to find connected matching symbols
   */
  private floodFillCluster(
    grid: Grid,
    startReel: number,
    startRow: number,
    targetSymbol: SymbolKind,
    visited: Set<string>
  ): Position[] {
    const cluster: Position[] = [];
    const queue: Position[] = [{ reel: startReel, row: startRow }];

    while (queue.length > 0) {
      const pos = queue.shift()!;
      const key = `${pos.reel},${pos.row}`;

      if (visited.has(key)) continue;
      if (pos.reel < 0 || pos.reel >= grid.length) continue;
      if (pos.row < 0 || pos.row >= grid[pos.reel].length) continue;

      const cellSymbol = grid[pos.reel][pos.row].symbol;

      // Check if symbol matches (or is wild)
      const isMatch = cellSymbol === targetSymbol || cellSymbol === 'WILD';

      if (!isMatch) continue;

      visited.add(key);
      cluster.push(pos);

      // Check adjacent cells (up, down, left, right)
      queue.push({ reel: pos.reel, row: pos.row + 1 });
      queue.push({ reel: pos.reel, row: pos.row - 1 });
      queue.push({ reel: pos.reel + 1, row: pos.row });
      queue.push({ reel: pos.reel - 1, row: pos.row });
    }

    return cluster;
  }

  /**
   * Evaluate clusters and calculate wins
   */
  private evaluateClusters(
    clusters: Array<{symbol: SymbolKind; positions: Position[]}>,
    globalMultiplier: number
  ): ClusterWin[] {
    const wins: ClusterWin[] = [];

    for (const cluster of clusters) {
      const size = cluster.positions.length;
      const symbolPaytable = this.config.paytable.get(cluster.symbol);

      if (!symbolPaytable) continue;

      // Find payout for cluster size
      let payout = 0;
      for (const [clusterSize, payoutValue] of symbolPaytable.entries()) {
        if (size >= clusterSize) {
          payout = payoutValue;
        }
      }

      if (payout > 0) {
        wins.push({
          symbol: cluster.symbol,
          positions: cluster.positions,
          size,
          payout,
          multiplier: globalMultiplier,
          totalWin: payout * globalMultiplier
        });
      }
    }

    return wins;
  }

  /**
   * Apply Reputation Decay to winning symbols
   * Symbols degrade through tiers instead of exploding
   */
  private applyReputationDecay(
    grid: Grid,
    clusters: Array<{symbol: SymbolKind; positions: Position[]}>
  ): Array<{position: Position; from: SymbolKind; to: SymbolKind; tier: string}> {
    const degradations: Array<{position: Position; from: SymbolKind; to: SymbolKind; tier: string}> = [];

    for (const cluster of clusters) {
      for (const pos of cluster.positions) {
        const cell = grid[pos.reel][pos.row];
        const currentSymbol = cell.symbol;

        // Get degraded form
        const degradedSymbol = this.degradationMap.get(currentSymbol);

        if (degradedSymbol) {
          // Apply degradation
          grid[pos.reel][pos.row].symbol = degradedSymbol;
          grid[pos.reel][pos.row].degraded = true;

          degradations.push({
            position: pos,
            from: currentSymbol,
            to: degradedSymbol,
            tier: this.getTierName(currentSymbol)
          });
        }
      }
    }

    return degradations;
  }

  /**
   * Remove EGG symbols and apply gravity
   */
  private removeEggsAndApplyGravity(grid: Grid): Grid {
    const newGrid: Grid = [];

    for (let reel = 0; reel < grid.length; reel++) {
      const newReel: Cell[] = [];

      // Collect non-EGG symbols from bottom to top
      for (let row = grid[reel].length - 1; row >= 0; row--) {
        if (grid[reel][row].symbol !== 'EGG') {
          newReel.unshift(grid[reel][row]);
        }
      }

      // Fill remaining spaces with new random symbols (simplified - in real game would use reel strips)
      while (newReel.length < grid[reel].length) {
        newReel.unshift(this.generateRandomCell());
      }

      newGrid.push(newReel);
    }

    return newGrid;
  }

  /**
   * Generate a random cell (simplified - real implementation would use weighted reel strips)
   */
  private generateRandomCell(): Cell {
    const symbols: SymbolKind[] = ['BEER', 'PILL', 'CIGT', 'TICK', 'CIGA', 'METH'];
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];

    return {
      symbol,
      tier: 'basic',
      degraded: false
    };
  }

  /**
   * Get global multiplier based on Addiction Meter
   */
  private getAddictionMultiplier(meter: number): number {
    if (meter >= 100) return 10; // Blackout
    if (meter >= 75) return 5;   // Wasted
    if (meter >= 50) return 3;   // Tipsy
    if (meter >= 25) return 2;   // Buzzed
    return 1;                     // Sober
  }

  /**
   * Get tier name for symbol
   */
  private getTierName(symbol: SymbolKind): string {
    if (symbol === 'DEPR') return 'Legendary';
    if (symbol === 'RAGE') return 'Evolved';
    if (['SLAK', 'KARE', 'METH'].includes(symbol)) return 'Basic';
    return 'Egg-Ready';
  }

  /**
   * Clone grid
   */
  private cloneGrid(grid: Grid): Grid {
    return grid.map(reel =>
      reel.map(cell => ({ ...cell }))
    );
  }
}
