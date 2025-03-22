export interface PredictionData {
  id: string;
  player: string;
  team: string;
  opponent: string;
  gameTime: string;
  sport: 'NBA' | 'NFL' | 'MLB' | 'NHL' | 'Soccer';
  stat: string;
  line: number;
  predictedValue: number;
  overProbability: number;
  confidence: number;
  confidenceCategory: 'Very High' | 'High' | 'Moderate' | 'Low' | 'Very Low';
  keyFactors: string[];
}

export interface PerformanceData {
  overall: {
    accuracy: number;
    highConfidenceAccuracy: number;
    mse: number;
    mae: number;
    totalPredictions: number;
    trend: {
      accuracy: number[];
      dates: string[];
    };
  };
  bySport: {
    [key: string]: {
      accuracy: number;
      predictions: number;
      byStatType: {
        statType: string;
        accuracy: number;
        predictions: number;
      }[];
    };
  };
  byConfidence: {
    [key: string]: {
      accuracy: number;
      predictions: number;
    };
  };
}

export interface SummaryData {
  totalPredictions: number;
  sportBreakdown: {
    [key: string]: number;
  };
  confidenceBreakdown: {
    [key: string]: number;
  };
  featuredPredictions: PredictionData[];
}

export interface PredictionsResponse {
  predictions: PredictionData[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface FilterOptions {
  sport?: string;
  date?: string;
  minConfidence?: number;
  stat?: string;
  team?: string;
  player?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  limit?: number;
}
