export interface StockInfo {
  symbol: string;
  name: string;
  sector: string;
  index: string;
}

export interface StockQuote {
  symbol: string;
  name: string;
  price: number;
  prevClose: number;
  change: number;
  changePct: number;
  volume: number;
  avgVolume: number;
  dayHigh: number;
  dayLow: number;
  week52High: number;
  week52Low: number;
  marketCap: number;
  peRatio: number;
  sector: string;
}

export interface PricePoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface CSADPoint {
  absReturn: number;
  csad: number;
  mktReturn: number;
  fitted: number;
}

export interface HerdingResult {
  sector: string;
  nStocks: number;
  herdingDetected: boolean;
  intensity: number;
  gamma2: number;
  gamma1: number;
  alpha: number;
  pValue: number;
  tStat: number;
  rSquared: number;
  observations: number;
  csadData: CSADPoint[];
  error?: string;
}

export interface PanicResult {
  panicScore: number;
  level: string;
  factors: {
    volumeAnomaly: number;
    deliveryPressure: number;
    priceVolDivergence: number;
    drawdownSeverity: number;
    volatilityRegime: number;
  };
  details: {
    currentDrawdown: number;
    currentVolatility: number;
    avgVolatility: number;
  };
  volumeData: VolumePoint[];
}

export interface VolumePoint {
  date: string;
  volume: number;
  zscore: number;
  returns: number;
  isPanic: boolean;
}

export interface BehaviorGapResult {
  investmentReturn: number;
  investmentCagr: number;
  investorCagr: number;
  behaviorGap: number;
  periodYears: number;
  gapInterpretation: string;
}

export interface MissingDayScenario {
  scenario: string;
  finalValue: number;
  totalReturn: number;
  cagr: number;
  reduction: number;
}

export interface HistogramBin {
  binStart: number;
  binEnd: number;
  sip: number;
  panic: number;
}

export interface MonteCarloResult {
  totalInvested: number;
  years: number;
  nSimulations: number;
  sip: { mean: number; median: number; p10: number; p90: number };
  panic: { mean: number; median: number; p10: number; p90: number };
  costOfPanic: { meanLoss: number; pctLoss: number; winRate: number };
  histogram: HistogramBin[];
}

export interface AnalysisResult {
  quote: StockQuote;
  priceChart: PricePoint[];
  herding: HerdingResult;
  panic: PanicResult;
  behaviorGap: BehaviorGapResult;
  missingDays: MissingDayScenario[];
  monteCarlo: MonteCarloResult;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
