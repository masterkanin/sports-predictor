'use client';

import React from 'react';
import { PredictionData } from '@/types/prediction';

interface PredictionCardProps {
  player: string;
  team: string;
  opponent: string;
  gameTime: string;
  stat: string;
  line: number;
  predictedValue: number;
  overProbability: number;
  confidence: number;
  confidenceCategory: string;
  keyFactors: string[];
}

export function PredictionCard({
  player,
  team,
  opponent,
  gameTime,
  stat,
  line,
  predictedValue,
  overProbability,
  confidence,
  confidenceCategory,
  keyFactors
}: PredictionCardProps) {
  // Determine if prediction is over or under
  const isOver = overProbability > 0.5;
  
  // Format the over probability as a percentage
  const overProbabilityPercent = Math.round(overProbability * 100);
  
  // Determine confidence color
  const getConfidenceColor = () => {
    if (confidenceCategory === 'Very High') return 'bg-green-600';
    if (confidenceCategory === 'High') return 'bg-green-500';
    if (confidenceCategory === 'Moderate') return 'bg-yellow-500';
    if (confidenceCategory === 'Low') return 'bg-orange-500';
    return 'bg-red-500';
  };
  
  // Determine prediction direction text and color
  const getPredictionText = () => {
    if (isOver) {
      return {
        text: 'OVER',
        color: 'text-green-600'
      };
    } else {
      return {
        text: 'UNDER',
        color: 'text-red-600'
      };
    }
  };
  
  const predictionInfo = getPredictionText();

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        {/* Header with player and teams */}
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="text-lg font-bold text-gray-900">{player}</h3>
            <p className="text-sm text-gray-500">{team} vs {opponent}</p>
          </div>
          <div className="flex flex-col items-end">
            <span className="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-gray-100 text-gray-800">
              {gameTime}
            </span>
            <span className="text-sm text-gray-500 mt-1">{stat}</span>
          </div>
        </div>
        
        {/* Prediction details */}
        <div className="flex justify-between items-center mb-4">
          <div className="flex flex-col">
            <span className="text-sm text-gray-500">Line</span>
            <span className="text-xl font-bold">{line.toFixed(1)}</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-sm text-gray-500">Prediction</span>
            <span className="text-xl font-bold">{predictedValue.toFixed(1)}</span>
          </div>
          <div className="flex flex-col items-end">
            <span className="text-sm text-gray-500">Recommendation</span>
            <span className={`text-xl font-bold ${predictionInfo.color}`}>{predictionInfo.text}</span>
          </div>
        </div>
        
        {/* Confidence meter */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm text-gray-500">Confidence</span>
            <span className="text-sm font-medium">{confidence}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className={`h-2.5 rounded-full ${getConfidenceColor()}`} 
              style={{ width: `${confidence}%` }}
            ></div>
          </div>
          <div className="mt-1 text-xs text-right text-gray-500">{confidenceCategory}</div>
        </div>
        
        {/* Over/Under probability */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-1">
            <span className="text-sm text-gray-500">Over Probability</span>
            <span className="text-sm font-medium">{overProbabilityPercent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className={`h-2.5 rounded-full ${isOver ? 'bg-green-500' : 'bg-red-500'}`} 
              style={{ width: `${overProbabilityPercent}%` }}
            ></div>
          </div>
        </div>
        
        {/* Key factors */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Key Factors</h4>
          <ul className="space-y-1">
            {keyFactors.map((factor, index) => (
              <li key={index} className="text-xs text-gray-600 flex items-start">
                <span className="text-blue-500 mr-1">•</span>
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}
