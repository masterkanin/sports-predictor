'use client';

import { useState, useEffect } from 'react';
import { PredictionsResponse, FilterOptions } from '@/types/prediction';

export default function usePredictionsData() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [predictionsData, setPredictionsData] = useState<PredictionsResponse | null>(null);
  const [filters, setFilters] = useState<FilterOptions>({
    sport: '',
    date: '',
    minConfidence: 0,
    stat: '',
    team: '',
    player: '',
    sortBy: 'confidence',
    sortOrder: 'desc',
    page: 1,
    limit: 6
  });

  useEffect(() => {
    const fetchPredictionsData = async () => {
      try {
        setLoading(true);
        
        // Build query string from filters
        const queryParams = new URLSearchParams();
        queryParams.append('endpoint', 'predictions');
        
        if (filters.sport) queryParams.append('sport', filters.sport);
        if (filters.date) queryParams.append('date', filters.date);
        if (filters.minConfidence) queryParams.append('minConfidence', filters.minConfidence.toString());
        if (filters.stat) queryParams.append('stat', filters.stat);
        if (filters.team) queryParams.append('team', filters.team);
        if (filters.player) queryParams.append('player', filters.player);
        if (filters.sortBy) queryParams.append('sortBy', filters.sortBy);
        if (filters.sortOrder) queryParams.append('sortOrder', filters.sortOrder);
        if (filters.page) queryParams.append('page', filters.page.toString());
        if (filters.limit) queryParams.append('limit', filters.limit.toString());
        
        const response = await fetch(`/api/predictions?${queryParams.toString()}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch predictions data');
        }
        
        const data = await response.json();
        setPredictionsData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPredictionsData();
  }, [filters]);

  // Update filters
  const updateFilters = (newFilters: Partial<FilterOptions>) => {
    // Reset to page 1 when filters change (except when explicitly changing page)
    if (!('page' in newFilters)) {
      setFilters({ ...filters, ...newFilters, page: 1 });
    } else {
      setFilters({ ...filters, ...newFilters });
    }
  };

  // Reset filters
  const resetFilters = () => {
    setFilters({
      sport: '',
      date: '',
      minConfidence: 0,
      stat: '',
      team: '',
      player: '',
      sortBy: 'confidence',
      sortOrder: 'desc',
      page: 1,
      limit: 6
    });
  };

  return {
    loading,
    error,
    predictions: predictionsData?.predictions || [],
    total: predictionsData?.total || 0,
    page: predictionsData?.page || 1,
    limit: predictionsData?.limit || 6,
    totalPages: predictionsData?.totalPages || 1,
    filters,
    updateFilters,
    resetFilters
  };
}
