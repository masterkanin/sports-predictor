'use client';

import { Layout } from "@/components/layout/Layout";
import usePerformanceData from "@/hooks/usePerformanceData";
import { useState } from "react";

export default function Performance() {
  const {
    loading,
    error,
    performanceData,
    timePeriod,
    customDateRange,
    updateTimePeriod,
    updateCustomDateRange
  } = usePerformanceData();

  const [activeSport, setActiveSport] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overall');

  if (loading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Performance Tracking</h1>
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-500">Loading performance data...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Performance Tracking</h1>
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  Error loading performance data: {error}
                </p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  // If no performance data is available
  if (!performanceData) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Performance Tracking</h1>
          <div className="bg-white shadow rounded-lg p-6 text-center">
            <p className="text-gray-500">No performance data available.</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Performance Tracking</h1>
        
        {/* Time Period Selector */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Time Period</h2>
            <div className="flex flex-wrap gap-4 mb-4">
              <button 
                className={`px-4 py-2 border ${timePeriod === '7' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => updateTimePeriod('7')}
              >
                Last 7 Days
              </button>
              <button 
                className={`px-4 py-2 border ${timePeriod === '30' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => updateTimePeriod('30')}
              >
                Last 30 Days
              </button>
              <button 
                className={`px-4 py-2 border ${timePeriod === '90' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => updateTimePeriod('90')}
              >
                Last 90 Days
              </button>
              <button 
                className={`px-4 py-2 border ${timePeriod === 'custom' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => updateTimePeriod('custom')}
              >
                Custom Range
              </button>
            </div>
            
            {/* Custom Date Range */}
            {timePeriod === 'custom' && (
              <div className="flex flex-col sm:flex-row gap-4 mb-4">
                <div className="flex-1">
                  <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-1">
                    Start Date
                  </label>
                  <input
                    type="date"
                    id="start-date"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    value={customDateRange?.start || ''}
                    onChange={(e) => updateCustomDateRange(e.target.value, customDateRange?.end || '')}
                  />
                </div>
                <div className="flex-1">
                  <label htmlFor="end-date" className="block text-sm font-medium text-gray-700 mb-1">
                    End Date
                  </label>
                  <input
                    type="date"
                    id="end-date"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                    value={customDateRange?.end || ''}
                    onChange={(e) => updateCustomDateRange(customDateRange?.start || '', e.target.value)}
                  />
                </div>
                <div className="flex items-end">
                  <button
                    className="px-4 py-2 border border-transparent text-white bg-blue-600 hover:bg-blue-700 rounded-md shadow-sm text-sm font-medium"
                    onClick={() => {
                      if (customDateRange?.start && customDateRange?.end) {
                        // Apply custom date range
                      }
                    }}
                  >
                    Apply
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
        
        {/* Overall Performance Summary */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Overall Performance</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">Overall Accuracy</div>
                <div className="text-3xl font-bold text-blue-600">{performanceData.overall.accuracy}%</div>
                <div className="mt-2 text-sm text-gray-500">Based on {performanceData.overall.totalPredictions} predictions</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">High Confidence Accuracy</div>
                <div className="text-3xl font-bold text-green-600">{performanceData.overall.highConfidenceAccuracy}%</div>
                <div className="mt-2 text-sm text-gray-500">For predictions with 80%+ confidence</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="text-sm text-gray-500 mb-1">Average Error</div>
                <div className="text-3xl font-bold text-gray-800">{performanceData.overall.mae.toFixed(1)}</div>
                <div className="mt-2 text-sm text-gray-500">Mean absolute error in predictions</div>
              </div>
            </div>
            
            {/* Accuracy Trend Chart */}
            <div>
              <h3 className="text-md font-medium text-gray-700 mb-2">Accuracy Trend</h3>
              <div className="h-64 bg-gray-50 rounded-lg p-4 flex items-center justify-center">
                <div className="w-full h-full relative">
                  {/* Simple bar chart visualization */}
                  <div className="absolute bottom-0 left-0 right-0 flex items-end justify-between h-48">
                    {performanceData.overall.trend.accuracy.map((accuracy, index) => (
                      <div key={index} className="flex flex-col items-center w-1/7">
                        <div 
                          className="w-12 bg-blue-500 rounded-t-sm" 
                          style={{ height: `${accuracy * 0.6}%` }}
                        ></div>
                        <div className="text-xs text-gray-500 mt-1">
                          {performanceData.overall.trend.dates[index]?.split('-').slice(1).join('/')}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {/* Y-axis labels */}
                  <div className="absolute top-0 left-0 bottom-0 flex flex-col justify-between text-xs text-gray-500">
                    <div>100%</div>
                    <div>75%</div>
                    <div>50%</div>
                    <div>25%</div>
                    <div>0%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Performance by Category Tabs */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Performance by Category</h2>
            
            {/* Tab Navigation */}
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                <button
                  onClick={() => setActiveTab('overall')}
                  className={`${
                    activeTab === 'overall'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                >
                  Overall
                </button>
                <button
                  onClick={() => setActiveTab('sport')}
                  className={`${
                    activeTab === 'sport'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                >
                  By Sport
                </button>
                <button
                  onClick={() => setActiveTab('confidence')}
                  className={`${
                    activeTab === 'confidence'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
                >
                  By Confidence
                </button>
              </nav>
            </div>
            
            {/* Tab Content */}
            <div className="mt-6">
              {/* Overall Tab */}
              {activeTab === 'overall' && (
                <div className="h-80 bg-gray-50 rounded-lg p-4 flex items-center justify-center">
                  <div className="text-center">
                    <p className="text-gray-500">Overall performance visualization will be displayed here</p>
                    <p className="text-sm text-gray-400 mt-2">Showing accuracy across all predictions</p>
                  </div>
                </div>
              )}
              
              {/* By Sport Tab */}
              {activeTab === 'sport' && (
                <div>
                  {/* Sport Selection */}
                  <div className="flex flex-wrap gap-4 mb-6">
                    <button 
                      className={`px-4 py-2 border ${!activeSport ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                      onClick={() => setActiveSport(null)}
                    >
                      All Sports
                    </button>
                    {Object.keys(performanceData.bySport).map((sport) => (
                      <button 
                        key={sport}
                        className={`px-4 py-2 border ${activeSport === sport ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                        onClick={() => setActiveSport(sport)}
                      >
                        {sport}
                      </button>
                    ))}
                  </div>
                  
                  {/* Sport Performance Visualization */}
                  <div className="h-80 bg-gray-50 rounded-lg p-4">
                    {!activeSport ? (
                      <div className="h-full flex flex-col">
                        <h3 className="text-md font-medium text-gray-700 mb-4">Accuracy by Sport</h3>
                        <div className="flex-1 flex items-center">
                          <div className="w-full">
                            {Object.entries(performanceData.bySport).map(([sport, data]) => (
                              <div key={sport} className="mb-4">
                                <div className="flex justify-between items-center mb-1">
                                  <span className="text-sm font-medium text-gray-700">{sport}</span>
                                  <span className="text-sm text-gray-500">{data.accuracy}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2.5">
                                  <div 
                                    className="h-2.5 rounded-full bg-blue-600" 
                                    style={{ width: `${data.accuracy}%` }}
                                  ></div>
                                </div>
                                <div className="mt-1 text-xs text-gray-500">{data.predictions} predictions</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="h-full flex flex-col">
                        <h3 className="text-md font-medium text-gray-700 mb-4">
                          {activeSport} Performance by Stat Type
                        </h3>
                        <div className="flex-1 flex items-center">
                          <div className="w-full">
                            {performanceData.bySport[activeSport].byStatType.map((statData) => (
                              <div key={statData.statType} className="mb-4">
                                <div className="flex justify-between items-center mb-1">
                                  <span className="text-sm font-medium text-gray-700">{statData.statType}</span>
                                  <span className="text-sm text-gray-500">{statData.accuracy}%</span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-2.5">
                                  <div 
                                    className="h-2.5 rounded-full bg-blue-600" 
                                    style={{ width: `${st<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>