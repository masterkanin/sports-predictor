'use client';

import { Layout } from "@/components/layout/Layout";
import useDashboardData from "@/hooks/useDashboardData";
import { PredictionCard } from "@/components/predictions/PredictionCard";

export default function Dashboard() {
  const { 
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
  } = useDashboardData();

  if (loading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
          <div className="flex items-center justify-center h-64">
            <p className="text-gray-500">Loading dashboard data...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  Error loading dashboard data: {error}
                </p>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
        
        {/* Summary Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">
                Total Predictions
              </dt>
              <dd className="mt-1 text-3xl font-semibold text-gray-900">
                {summaryData?.totalPredictions.toLocaleString() || 0}
              </dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">
                Overall Accuracy
              </dt>
              <dd className="mt-1 text-3xl font-semibold text-green-600">
                72%
              </dd>
            </div>
          </div>
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <dt className="text-sm font-medium text-gray-500 truncate">
                High Confidence Picks
              </dt>
              <dd className="mt-1 text-3xl font-semibold text-blue-600">
                {summaryData?.confidenceBreakdown?.['High'] || 0}
              </dd>
            </div>
          </div>
        </div>
        
        {/* Quick Filters */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Filters</h2>
            <div className="flex flex-wrap gap-4">
              <button 
                className={`px-4 py-2 border ${!activeSport ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveSport(null)}
              >
                All Sports
              </button>
              <button 
                className={`px-4 py-2 border ${activeSport === 'NBA' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveSport('NBA')}
              >
                NBA
              </button>
              <button 
                className={`px-4 py-2 border ${activeSport === 'NFL' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveSport('NFL')}
              >
                NFL
              </button>
              <button 
                className={`px-4 py-2 border ${activeSport === 'MLB' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveSport('MLB')}
              >
                MLB
              </button>
              <button 
                className={`px-4 py-2 border ${activeSport === 'NHL' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveSport('NHL')}
              >
                NHL
              </button>
              <button 
                className={`px-4 py-2 border ${activeSport === 'Soccer' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveSport('Soccer')}
              >
                Soccer
              </button>
            </div>
            <div className="mt-4 flex flex-wrap gap-4">
              <button 
                className={`px-4 py-2 border ${activeTimeFrame === 'today' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveTimeFrame('today')}
              >
                Today
              </button>
              <button 
                className={`px-4 py-2 border ${activeTimeFrame === 'tomorrow' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveTimeFrame('tomorrow')}
              >
                Tomorrow
              </button>
              <button 
                className={`px-4 py-2 border ${activeTimeFrame === 'week' ? 'border-transparent text-white bg-blue-600 hover:bg-blue-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveTimeFrame('week')}
              >
                This Week
              </button>
            </div>
            <div className="mt-4 flex flex-wrap gap-4">
              <button 
                className={`px-4 py-2 border ${activeConfidence === 'high' ? 'border-transparent text-white bg-green-600 hover:bg-green-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveConfidence('high')}
              >
                High Confidence
              </button>
              <button 
                className={`px-4 py-2 border ${activeConfidence === 'all' ? 'border-transparent text-white bg-green-600 hover:bg-green-700' : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'} rounded-md shadow-sm text-sm font-medium`}
                onClick={() => setActiveConfidence('all')}
              >
                All Confidence Levels
              </button>
            </div>
          </div>
        </div>
        
        {/* Featured Predictions */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Featured High-Confidence Predictions</h2>
            {filteredPredictions.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredPredictions.map((prediction) => (
                  <PredictionCard
                    key={prediction.id}
                    player={prediction.player}
                    team={prediction.team}
                    opponent={prediction.opponent}
                    gameTime={new Date(prediction.gameTime).toLocaleString()}
                    stat={prediction.stat}
                    line={prediction.line}
                    predictedValue={prediction.predictedValue}
                    overProbability={prediction.overProbability}
                    confidence={prediction.confidence}
                    confidenceCategory={prediction.confidenceCategory}
                    keyFactors={prediction.keyFactors}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500">No predictions match your current filters.</p>
              </div>
            )}
            <div className="mt-6 text-center">
              <a href="/predictions" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
                View All Predictions
              </a>
            </div>
          </div>
        </div>
        
        {/* Performance Overview */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Performance Overview</h2>
            <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
              <p className="text-gray-500">Performance chart will be displayed here</p>
            </div>
            <div className="mt-6 text-center">
              <a href="/performance" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
                View Detailed Performance
              </a>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
