'use client';

import { useState, useEffect } from 'react';
import { PerformanceData } from '@/types/prediction';

export default function usePerformanceData() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
  const [timePeriod, setTimePeriod] = useState('7'); // Default to last 7 days
  const [customDateRange, setCustomDateRange] = useState<{start: string, end: string} | null>(null);

  useEffect(() => {
    const fetchPerformanceData = async () => {
      try {
        setLoading(true);
        
        // Build query string
        const queryParams = new URLSearchParams();
        queryParams.append('endpoint', 'performance');
        
        if (timePeriod) queryParams.append('period', timePeriod);
        if (customDateRange) {
          queryParams.append('startDate', customDateRange.start);
          queryParams.append('endDate', customDateRange.end);
        }
        
        const response = await fetch(`/api/predictions?${queryParams.toString()}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch performance data');
        }
        
        const data = await response.json();
        setPerformanceData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
      } finally {
        setLoading(false);
      }
    };
    
    fetchPerformanceData();
  }, [timePeriod, customDateRange]);

  // Update time period
  const updateTimePeriod = (period: string) => {
    setTimePeriod(period);
    // Clear custom date range when selecting a predefined period
    setCustomDateRange(null);
  };

  // Update custom date range
  const updateCustomDateRange = (start: string, end: string) => {
    setCustomDateRange({ start, end });
    // Clear predefined period when using custom range
    setTimePeriod('custom');
  };

  return {
    loading,
    error,
    performanceData,
    timePeriod,
    customDateRange,
    updateTimePeriod,
    updateCustomDateRange
  };
}
