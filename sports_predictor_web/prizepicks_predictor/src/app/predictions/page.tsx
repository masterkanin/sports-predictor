'use client';

import { Layout } from "@/components/layout/Layout";
import { FilterPanel } from "@/components/predictions/FilterPanel";
import { PredictionCard } from "@/components/predictions/PredictionCard";
import usePredictionsData from "@/hooks/usePredictionsData";
import { useState } from "react";

export default function Predictions() {
  const {
    loading,
    error,
    predictions,
    total,
    page,
    limit,
    totalPages,
    filters,
    updateFilters,
    resetFilters
  } = usePredictionsData();

  // Handle page change
  const handlePageChange = (newPage: number) => {
    updateFilters({ page: newPage });
  };

  // Handle sort change
  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    let sortBy = 'confidence';
    let sortOrder = 'desc' as 'asc' | 'desc';
    
    if (value === 'confidence_high_to_low') {
      sortBy = 'confidence';
      sortOrder = 'desc';
    } else if (value === 'confidence_low_to_high') {
      sortBy = 'confidence';
      sortOrder = 'asc';
    } else if (value === 'game_time_earliest') {
      sortBy = 'gameTime';
      sortOrder = 'asc';
    } else if (value === 'game_time_latest') {
      sortBy = 'gameTime';
      sortOrder = 'desc';
    } else if (value === 'player_name_az') {
      sortBy = 'player';
      sortOrder = 'asc';
    }
    
    updateFilters({ sortBy, sortOrder });
  };

  if (error) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">Predictions</h1>
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-8">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">
                  Error loading predictions: {error}
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
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Predictions</h1>
        
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filter Panel */}
          <div className="lg:w-1/4">
            <FilterPanel 
              filters={filters}
              updateFilters={updateFilters}
              resetFilters={resetFilters}
            />
          </div>
          
          {/* Predictions List */}
          <div className="lg:w-3/4">
            {/* Sorting Controls */}
            <div className="bg-white p-4 rounded-lg shadow mb-6">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <h2 className="text-lg font-medium text-gray-900 mb-2 sm:mb-0">
                  {loading ? 'Loading predictions...' : `${total} Predictions`}
                </h2>
                <div className="flex items-center space-x-4">
                  <label htmlFor="sort-by" className="text-sm font-medium text-gray-700">
                    Sort by:
                  </label>
                  <select
                    id="sort-by"
                    name="sort-by"
                    className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                    value={filters.sortBy === 'confidence' 
                      ? (filters.sortOrder === 'desc' ? 'confidence_high_to_low' : 'confidence_low_to_high')
                      : filters.sortBy === 'gameTime'
                      ? (filters.sortOrder === 'asc' ? 'game_time_earliest' : 'game_time_latest')
                      : 'player_name_az'
                    }
                    onChange={handleSortChange}
                  >
                    <option value="confidence_high_to_low">Confidence (High to Low)</option>
                    <option value="confidence_low_to_high">Confidence (Low to High)</option>
                    <option value="game_time_earliest">Game Time (Earliest)</option>
                    <option value="game_time_latest">Game Time (Latest)</option>
                    <option value="player_name_az">Player Name (A-Z)</option>
                  </select>
                </div>
              </div>
            </div>
            
            {/* Loading State */}
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <p className="text-gray-500">Loading predictions...</p>
              </div>
            ) : predictions.length === 0 ? (
              <div className="bg-white p-8 rounded-lg shadow text-center">
                <p className="text-gray-500">No predictions match your current filters.</p>
                <button
                  onClick={resetFilters}
                  className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700"
                >
                  Reset Filters
                </button>
              </div>
            ) : (
              <>
                {/* Predictions Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {predictions.map((prediction) => (
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
                
                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="mt-8 flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6 rounded-lg shadow">
                    <div className="flex flex-1 justify-between sm:hidden">
                      <button
                        onClick={() => handlePageChange(page - 1)}
                        disabled={page === 1}
                        className={`relative inline-flex items-center rounded-md border ${page === 1 ? 'border-gray-200 text-gray-400' : 'border-gray-300 text-gray-700 hover:bg-gray-50'} bg-white px-4 py-2 text-sm font-medium`}
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => handlePageChange(page + 1)}
                        disabled={page === totalPages}
                        className={`relative ml-3 inline-flex items-center rounded-md border ${page === totalPages ? 'border-gray-200 text-gray-400' : 'border-gray-300 text-gray-700 hover:bg-gray-50'} bg-white px-4 py-2 text-sm font-medium`}
                      >
                        Next
                      </button>
                    </div>
                    <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm text-gray-700">
                          Showing <span className="font-medium">{(page - 1) * limit + 1}</span> to <span className="font-medium">{Math.min(page * limit, total)}</span> of{' '}
                          <span className="font-medium">{total}</span> results
                        </p>
                      </div>
                      <div>
                        <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                          <button
                            onClick={() => handlePageChange(page - 1)}
                            disabled={page === 1}
                            className={`relative inline-flex items-center rounded-l-md px-2 py-2 ${page === 1 ? 'text-gray-300' : 'text-gray-400 hover:bg-gray-50'} ring-1 ring-inset ring-gray-300 focus:z-20 focus:outline-offset-0`}
                          >
                            <span className="sr-only">Previous</span>
                            &lt;
                          </button>
                          
                          {/* Generate page buttons */}
                          {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                            // Logic to show pages around current page
                            let pageNum;
                            if (totalPages <= 5) {
                              pageNum = i + 1;
                            } else if (page <= 3) {
                              pageNum = i + 1;
                            } else if (page >= totalPages - 2) {
                              pageNum = totalPages - 4 + i;
                            } else {
                              pageNum = page - 2 + i;
                            }
                            
                            return (
                              <button
                                key={pageNum}
                                onClick={() => handlePageChange(pageNum)}
                                aria-current={page === pageNum ? 'page' : undefined}
                                className={`relative z-10 inline-flex items-center ${
                                  page === pageNum
                                    ? 'bg-blue-600 text-white'
                                    : 'text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50'
                                } px-4 py-2 text-sm font-semibold focus:z-20 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600`}
                              >
                                {pageNum}
                              </button>
                            );
                          })}
                          
                          {/* Show ellipsis if needed */}
                          {totalPages > 5 && page < totalPages - 2 && (
                            <span className="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-700 ring-1 ring-inset ring-gray-300 focus:outline-offset-0">
                              ...
                            </span>
                          )}
                          
                          {/* Show last page if not in view */}
                          {totalPages > 5 && page < totalPages - 2 && (
                            <button
                              onClick={() => handlePageChange(totalPages)}
                              className="relative inline-flex items-center px-4 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0"
                            >
                              {totalPages}
                            </button>
                          )}
                          
                          <button
                            onClick={() => handlePageChange(page + 1)}
                            disabled={page === totalPages}
                            className={`relative inline-flex items-center rounded-r-md px-2 py-2 ${page === totalPages ? 'text-gray-300' : 'text-gray-400 hover:bg-gray-50'} ring-1 ring-inset ring-gray-300 focus:z-20 focus:outline-offset-0`}
                          >
                            <span className="sr-only">Next</span>
                            &gt;
                          </button>
                        </nav>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
