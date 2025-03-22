'use client';

import { useState, useEffect } from 'react';
import { SummaryData, PredictionData } from '@/types/prediction';

export default function useDashboardData() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null);
  const [activeSport, setActiveSport] = useState<string | null>(null);
  const [activeTimeFrame, setActiveTimeFrame] = useState('today');
  const [activeConfidence, setActiveConfidence] = useState('high');

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/predictions?endpoint=summary');
        
        if (!response.ok) {
          throw new Error('Failed to fetch dashboard data');
        }
        
        const data = await response.json();
        setSummaryData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  // Filter featured predictions based on active filters
  const filteredPredictions = summaryData?.featuredPredictions.filter(prediction => {
    // Filter by sport
    if (activeSport && prediction.sport !== activeSport) {
      return false;
    }
    
    // Filter by time frame
    if (activeTimeFrame === 'today') {
      const today = new Date().toISOString().split('T')[0];
      const predictionDate = new Date(prediction.gameTime).toISOString().split('T')[0];
      if (predictionDate !== today) {
        return false;
      }
    } else if (activeTimeFrame === 'tomorrow') {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      const tomorrowStr = tomorrow.toISOString().split('T')[0];
      const predictionDate = new Date(prediction.gameTime).toISOString().split('T')[0];
      if (predictionDate !== tomorrowStr) {
        return false;
      }
    } else if (activeTimeFrame === 'week') {
      const today = new Date();
      const nextWeek = new Date();
      nextWeek.setDate(today.getDate() + 7);
      const predictionDate = new Date(prediction.gameTime);
      if (predictionDate < today || predictionDate > nextWeek) {
        return false;
      }
    }
    
    // Filter by confidence
    if (activeConfidence === 'high' && prediction.confidence < 80) {
      return false;
    } else if (activeConfidence === 'all') {
      // No filtering needed
    }
    
    return true;
  }) || [];

  return {
    loading,
    error,
    summaryData,
    filteredPredictions,
    activeSport,
    setActiveSport,
    activeTimeFrame,
    setActiveTimeFrame,
    activeConfidence,
    setActiveConfidence
  };
}
