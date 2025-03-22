// This file contains the API routes for fetching prediction data
import { NextRequest, NextResponse } from 'next/server';
import { PredictionData } from '@/types/prediction';

// Mock data for predictions
const mockPredictions: PredictionData[] = [
  {
    id: '1',
    player: 'LeBron James',
    team: 'LAL',
    opponent: 'BOS',
    gameTime: '2025-03-21T20:00:00Z',
    sport: 'NBA',
    stat: 'Points',
    line: 25.5,
    predictedValue: 27.5,
    overProbability: 0.74,
    confidence: 80,
    confidenceCategory: 'High',
    keyFactors: [
      'High usage rate',
      'Weak opponent defense',
      'Recent scoring streak'
    ]
  },
  {
    id: '2',
    player: 'Stephen Curry',
    team: 'GSW',
    opponent: 'PHX',
    gameTime: '2025-03-21T22:30:00Z',
    sport: 'NBA',
    stat: '3-Pointers',
    line: 4.5,
    predictedValue: 5.8,
    overProbability: 0.82,
    confidence: 92,
    confidenceCategory: 'Very High',
    keyFactors: [
      'Phoenix allows most 3PA',
      'Recent hot shooting streak',
      'Home court advantage'
    ]
  },
  {
    id: '3',
    player: 'Nikola Jokić',
    team: 'DEN',
    opponent: 'MIA',
    gameTime: '2025-03-22T19:00:00Z',
    sport: 'NBA',
    stat: 'Assists',
    line: 8.5,
    predictedValue: 10.2,
    overProbability: 0.78,
    confidence: 85,
    confidenceCategory: 'High',
    keyFactors: [
      'Murray returning from injury',
      'Miami\'s defensive scheme',
      'Averaging 11.2 assists last 5 games'
    ]
  },
  {
    id: '4',
    player: 'Joel Embiid',
    team: 'PHI',
    opponent: 'NYK',
    gameTime: '2025-03-22T19:30:00Z',
    sport: 'NBA',
    stat: 'Rebounds',
    line: 11.5,
    predictedValue: 10.3,
    overProbability: 0.35,
    confidence: 75,
    confidenceCategory: 'High',
    keyFactors: [
      'Strong NYK rebounding',
      'Limited minutes expected',
      'Under in last 3 matchups'
    ]
  },
  {
    id: '5',
    player: 'Luka Dončić',
    team: 'DAL',
    opponent: 'LAC',
    gameTime: '2025-03-22T20:30:00Z',
    sport: 'NBA',
    stat: 'Points + Rebounds + Assists',
    line: 47.5,
    predictedValue: 52.3,
    overProbability: 0.68,
    confidence: 70,
    confidenceCategory: 'Moderate',
    keyFactors: [
      'High usage without Irving',
      'Clippers defensive focus',
      'Averaging 51.2 PRA last 10 games'
    ]
  },
  {
    id: '6',
    player: 'Jayson Tatum',
    team: 'BOS',
    opponent: 'LAL',
    gameTime: '2025-03-21T20:00:00Z',
    sport: 'NBA',
    stat: 'Points',
    line: 28.5,
    predictedValue: 26.8,
    overProbability: 0.42,
    confidence: 65,
    confidenceCategory: 'Moderate',
    keyFactors: [
      'Lakers improved defense',
      'Brown taking more shots',
      'Under in 4 of last 6 games'
    ]
  },
  {
    id: '7',
    player: 'Patrick Mahomes',
    team: 'KC',
    opponent: 'BAL',
    gameTime: '2025-03-23T18:00:00Z',
    sport: 'NFL',
    stat: 'Passing Yards',
    line: 285.5,
    predictedValue: 310.2,
    overProbability: 0.71,
    confidence: 75,
    confidenceCategory: 'High',
    keyFactors: [
      'Baltimore secondary injuries',
      'High-scoring game expected',
      'Strong performance in last matchup'
    ]
  },
  {
    id: '8',
    player: 'Lamar Jackson',
    team: 'BAL',
    opponent: 'KC',
    gameTime: '2025-03-23T18:00:00Z',
    sport: 'NFL',
    stat: 'Rushing Yards',
    line: 65.5,
    predictedValue: 78.3,
    overProbability: 0.68,
    confidence: 72,
    confidenceCategory: 'High',
    keyFactors: [
      'KC struggles against mobile QBs',
      'Designed run plays increasing',
      'Weather conditions favor running'
    ]
  },
  {
    id: '9',
    player: 'Shohei Ohtani',
    team: 'LAD',
    opponent: 'SF',
    gameTime: '2025-03-22T21:10:00Z',
    sport: 'MLB',
    stat: 'Strikeouts',
    line: 7.5,
    predictedValue: 8.7,
    overProbability: 0.64,
    confidence: 68,
    confidenceCategory: 'Moderate',
    keyFactors: [
      'Giants high K-rate vs. RHP',
      'Ohtani\'s splitter effectiveness',
      'Favorable umpire for pitchers'
    ]
  },
  {
    id: '10',
    player: 'Aaron Judge',
    team: 'NYY',
    opponent: 'BOS',
    gameTime: '2025-03-22T18:05:00Z',
    sport: 'MLB',
    stat: 'Total Bases',
    line: 1.5,
    predictedValue: 2.3,
    overProbability: 0.76,
    confidence: 82,
    confidenceCategory: 'High',
    keyFactors: [
      'Strong vs. Boston pitching',
      'Wind blowing out to right field',
      'Hot streak in last 7 games'
    ]
  },
  {
    id: '11',
    player: 'Connor McDavid',
    team: 'EDM',
    opponent: 'VGK',
    gameTime: '2025-03-22T22:00:00Z',
    sport: 'NHL',
    stat: 'Points',
    line: 1.5,
    predictedValue: 1.8,
    overProbability: 0.62,
    confidence: 67,
    confidenceCategory: 'Moderate',
    keyFactors: [
      'Vegas goaltender struggles',
      'Power play opportunities',
      'Multi-point games in 3 of last 5'
    ]
  },
  {
    id: '12',
    player: 'Auston Matthews',
    team: 'TOR',
    opponent: 'MTL',
    gameTime: '2025-03-22T19:00:00Z',
    sport: 'NHL',
    stat: 'Shots on Goal',
    line: 4.5,
    predictedValue: 5.7,
    overProbability: 0.79,
    confidence: 85,
    confidenceCategory: 'High',
    keyFactors: [
      'Montreal allows most shots in league',
      'Matthews averaging 5.8 SOG last 10 games',
      'Rivalry game intensity'
    ]
  },
  {
    id: '13',
    player: 'Erling Haaland',
    team: 'MCI',
    opponent: 'ARS',
    gameTime: '2025-03-23T16:30:00Z',
    sport: 'Soccer',
    stat: 'Shots on Target',
    line: 2.5,
    predictedValue: 3.2,
    overProbability: 0.67,
    confidence: 73,
    confidenceCategory: 'High',
    keyFactors: [
      'Arsenal missing key defender',
      'City\'s attacking form',
      'Haaland\'s home record'
    ]
  },
  {
    id: '14',
    player: 'Mohamed Salah',
    team: 'LIV',
    opponent: 'CHE',
    gameTime: '2025-03-23T14:00:00Z',
    sport: 'Soccer',
    stat: 'Goal Contributions',
    line: 0.5,
    predictedValue: 0.9,
    overProbability: 0.81,
    confidence: 78,
    confidenceCategory: 'High',
    keyFactors: [
      'Chelsea defensive vulnerabilities',
      'Salah\'s record vs. Chelsea',
      'Liverpool\'s attacking tactics'
    ]
  }
];

// Mock data for performance metrics
const mockPerformance = {
  overall: {
    accuracy: 72,
    highConfidenceAccuracy: 78,
    mse: 5.2,
    mae: 1.8,
    totalPredictions: 1245,
    trend: {
      accuracy: [68, 70, 71, 69, 72, 73, 72],
      dates: ['2025-02-21', '2025-02-28', '2025-03-07', '2025-03-14', '2025-03-21']
    }
  },
  bySport: {
    NBA: {
      accuracy: 78,
      predictions: 856,
      byStatType: [
        { statType: 'Points', accuracy: 76, predictions: 324 },
        { statType: 'Rebounds', accuracy: 81, predictions: 287 },
        { statType: 'Assists', accuracy: 79, predictions: 245 }
      ]
    },
    NFL: {
      accuracy: 68,
      predictions: 156,
      byStatType: [
        { statType: 'Passing Yards', accuracy: 68, predictions: 62 },
        { statType: 'Rushing Yards', accuracy: 71, predictions: 58 },
        { statType: 'Receiving Yards', accuracy: 65, predictions: 36 }
      ]
    },
    MLB: {
      accuracy: 74,
      predictions: 98,
      byStatType: [
        { statType: 'Strikeouts', accuracy: 74, predictions: 42 },
        { statType: 'Total Bases', accuracy: 73, predictions: 38 },
        { statType: 'Hits', accuracy: 76, predictions: 18 }
      ]
    },
    NHL: {
      accuracy: 65,
      predictions: 87,
      byStatType: [
        { statType: 'Points', accuracy: 64, predictions: 42 },
        { statType: 'Shots on Goal', accuracy: 68, predictions: 32 },
        { statType: 'Saves', accuracy: 62, predictions: 13 }
      ]
    },
    Soccer: {
      accuracy: 62,
      predictions: 48,
      byStatType: [
        { statType: 'Shots on Target', accuracy: 64, predictions: 22 },
        { statType: 'Goal Contributions', accuracy: 61, predictions: 18 },
        { statType: 'Passes', accuracy: 59, predictions: 8 }
      ]
    }
  },
  byConfidence: {
    'Very High': { accuracy: 86, predictions: 124 },
    'High': { accuracy: 78, predictions: 356 },
    'Moderate': { accuracy: 65, predictions: 487 },
    'Low': { accuracy: 52, predictions: 198 },
    'Very Low': { accuracy: 41, predictions: 80 }
  }
};

export async function GET(request: NextRequest) {
  // Get query parameters
  const { searchParams } = new URL(request.url);
  const endpoint = searchParams.get('endpoint');
  
  // Handle different endpoints
  switch (endpoint) {
    case 'predictions':
      // Filter predictions based on query parameters
      let filteredPredictions = [...mockPredictions];
      
      // Apply sport filter
      const sport = searchParams.get('sport');
      if (sport) {
        filteredPredictions = filteredPredictions.filter(p => p.sport === sport);
      }
      
      // Apply confidence filter
      const minConfidence = searchParams.get('minConfidence');
      if (minConfidence) {
        filteredPredictions = filteredPredictions.filter(p => p.confidence >= parseInt(minConfidence));
      }
      
      // Apply date filter
      const date = searchParams.get('date');
      if (date) {
        const targetDate = new Date(date).toISOString().split('T')[0];
        filteredPredictions = filteredPredictions.filter(p => {
          const predictionDate = new Date(p.gameTime).toISOString().split('T')[0];
          return predictionDate === targetDate;
        });
      }
      
      // Apply stat filter
      const stat = searchParams.get('stat');
      if (stat) {
        filteredPredictions = filteredPredictions.filter(p => p.stat === stat);
      }
      
      // Apply team filter
      const team = searchParams.get('team');
      if (team) {
        filteredPredictions = filteredPredictions.filter(p => p.team === team || p.opponent === team);
      }
      
      // Apply player filter
      const player = searchParams.get('player');
      if (player) {
        filteredPredictions = filteredPredictions.filter(p => 
          p.player.toLowerCase().includes(player.toLowerCase())
        );
      }
      
      // Apply sorting
      const sortBy = searchParams.get('sortBy') || 'confidence';
      const sortOrder = searchParams.get('sortOrder') || 'desc';
      
      filteredPredictions.sort((a, b) => {
        let comparison = 0;
        
        switch (sortBy) {
          case 'confidence':
            comparison = a.confidence - b.confidence;
            break;
          case 'gameTime':
            comparison = new Date(a.gameTime).getTime() - new Date(b.gameTime).getTime();
            break;
          case 'player':
            comparison = a.player.localeCompare(b.player);
            break;
          case 'line':
            comparison = a.line - b.line;
            break;
          case 'predictedValue':
            comparison = a.predictedValue - b.predictedValue;
            break;
          default:
            comparison = a.confidence - b.confidence;
        }
        
        return sortOrder === 'asc' ? comparison : -comparison;
      });
      
      // Apply pagination
      const page = parseInt(searchParams.get('page') || '1');
      const limit = parseInt(searchParams.get('limit') || '10');
      const startIndex = (page - 1) * limit;
      const endIndex = page * limit;
      
      const paginatedPredictions = filteredPredictions.slice(startIndex, endIndex);
      
      return NextResponse.json({
        predictions: paginatedPredictions,
        total: filteredPredictions.length,
        page,
        limit,
        totalPages: Math.ceil(filteredPredictions.length / limit)
      });
      
    case 'performance':
      return NextResponse.json(mockPerformance);
      
    case 'summary':
      // Return summary statistics
      return NextResponse.json({
        totalPredictions: mockPredictions.length,
        sportBreakdown: {
          NBA: mockPredictions.filter(p => p.sport === 'NBA').length,
          NFL: mockPredictions.filter(p => p.sport === 'NFL').length,
          MLB: mockPredictions.filter(p => p.sport === 'MLB').length,
          NHL: mockPredictions.filter(p => p.sport === 'NHL').length,
          Soccer: mockPredictions.filter(p => p.sport === 'Soccer').length
        },
        confidenceBreakdown: {
          'Very High': mockPredictions.filter(p => p.confidenceCategory === 'Very High').length,
          'High': mockPredictions.filter(p => p.confidenceCategory === 'High').length,
          'Moderate': mockPredictions.filter(p => p.confidenceCategory === 'Moderate').length,
          'Low': mockPredictions.filter(p => p.confidenceCategory === 'Low').length,
          'Very Low': mockPredictions.filter(p => p.confidenceCategory === 'Very Low').length
        },
        featuredPredictions: mockPredictions
          .filter(p => p.confidence >= 80)
          .sort((a, b) => b.confidence - a.confidence)
          .slice(0, 3)
      });
      
    default:
      return NextResponse.json({ error: 'Invalid endpoint' }, { status: 400 });
  }
}
