'use client';

import React from 'react';
import { FilterOptions } from '@/types/prediction';

interface FilterPanelProps {
  filters: FilterOptions;
  updateFilters: (newFilters: Partial<FilterOptions>) => void;
  resetFilters: () => void;
}

export function FilterPanel({ filters, updateFilters, resetFilters }: FilterPanelProps) {
  // Handle sport change
  const handleSportChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    updateFilters({ sport: e.target.value });
  };

  // Handle date change
  const handleDateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    let date = '';
    
    if (value === 'today') {
      date = new Date().toISOString().split('T')[0];
    } else if (value === 'tomorrow') {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      date = tomorrow.toISOString().split('T')[0];
    }
    
    updateFilters({ date });
  };

  // Handle custom date change
  const handleCustomDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateFilters({ date: e.target.value });
  };

  // Handle confidence change
  const handleConfidenceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const confidenceLevels: { [key: string]: number } = {
      'very-high': 90,
      'high': 80,
      'moderate': 65,
      'low': 50,
      'very-low': 0
    };
    
    const checkedValues = Array.from(document.querySelectorAll('input[name="confidence"]:checked'))
      .map(el => (el as HTMLInputElement).id);
    
    // Find the lowest confidence level checked
    let minConfidence = 100;
    checkedValues.forEach(value => {
      const confidenceValue = confidenceLevels[value];
      if (confidenceValue < minConfidence) {
        minConfidence = confidenceValue;
      }
    });
    
    // If none checked, reset to 0
    if (checkedValues.length === 0) {
      minConfidence = 0;
    }
    
    updateFilters({ minConfidence });
  };

  // Handle stat type change
  const handleStatTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    updateFilters({ stat: e.target.value });
  };

  // Handle team change
  const handleTeamChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    updateFilters({ team: e.target.value });
  };

  // Handle player search
  const handlePlayerSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateFilters({ player: e.target.value });
  };

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-lg font-medium text-gray-900 mb-4">Filters</h2>
      
      {/* Sport Filter */}
      <div className="mb-4">
        <label htmlFor="sport" className="block text-sm font-medium text-gray-700 mb-1">
          Sport
        </label>
        <select
          id="sport"
          name="sport"
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          value={filters.sport}
          onChange={handleSportChange}
        >
          <option value="">All Sports</option>
          <option value="NBA">NBA</option>
          <option value="NFL">NFL</option>
          <option value="MLB">MLB</option>
          <option value="NHL">NHL</option>
          <option value="Soccer">Soccer</option>
        </select>
      </div>
      
      {/* Date Filter */}
      <div className="mb-4">
        <label htmlFor="date" className="block text-sm font-medium text-gray-700 mb-1">
          Date
        </label>
        <select
          id="date"
          name="date"
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm mb-2"
          onChange={handleDateChange}
        >
          <option value="">All Dates</option>
          <option value="today">Today</option>
          <option value="tomorrow">Tomorrow</option>
          <option value="custom">Custom Date</option>
        </select>
        <input
          type="date"
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          value={filters.date}
          onChange={handleCustomDateChange}
        />
      </div>
      
      {/* Confidence Filter */}
      <div className="mb-4">
        <label htmlFor="confidence" className="block text-sm font-medium text-gray-700 mb-1">
          Confidence Level
        </label>
        <div className="space-y-2">
          <div className="flex items-center">
            <input
              id="very-high"
              name="confidence"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              defaultChecked={filters.minConfidence === 0 || filters.minConfidence >= 90}
              onChange={handleConfidenceChange}
            />
            <label htmlFor="very-high" className="ml-2 text-sm text-gray-700">
              Very High
            </label>
          </div>
          <div className="flex items-center">
            <input
              id="high"
              name="confidence"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              defaultChecked={filters.minConfidence === 0 || filters.minConfidence >= 80}
              onChange={handleConfidenceChange}
            />
            <label htmlFor="high" className="ml-2 text-sm text-gray-700">
              High
            </label>
          </div>
          <div className="flex items-center">
            <input
              id="moderate"
              name="confidence"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              defaultChecked={filters.minConfidence === 0 || filters.minConfidence >= 65}
              onChange={handleConfidenceChange}
            />
            <label htmlFor="moderate" className="ml-2 text-sm text-gray-700">
              Moderate
            </label>
          </div>
          <div className="flex items-center">
            <input
              id="low"
              name="confidence"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              defaultChecked={filters.minConfidence === 0 || filters.minConfidence >= 50}
              onChange={handleConfidenceChange}
            />
            <label htmlFor="low" className="ml-2 text-sm text-gray-700">
              Low
            </label>
          </div>
          <div className="flex items-center">
            <input
              id="very-low"
              name="confidence"
              type="checkbox"
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              defaultChecked={filters.minConfidence === 0}
              onChange={handleConfidenceChange}
            />
            <label htmlFor="very-low" className="ml-2 text-sm text-gray-700">
              Very Low
            </label>
          </div>
        </div>
      </div>
      
      {/* Stat Type Filter */}
      <div className="mb-4">
        <label htmlFor="stat-type" className="block text-sm font-medium text-gray-700 mb-1">
          Stat Type
        </label>
        <select
          id="stat-type"
          name="stat-type"
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          value={filters.stat}
          onChange={handleStatTypeChange}
        >
          <option value="">All Stats</option>
          <option value="Points">Points</option>
          <option value="Rebounds">Rebounds</option>
          <option value="Assists">Assists</option>
          <option value="3-Pointers">3-Pointers</option>
          <option value="Points + Rebounds + Assists">Points + Rebounds + Assists</option>
          <option value="Steals">Steals</option>
          <option value="Blocks">Blocks</option>
          <option value="Passing Yards">Passing Yards</option>
          <option value="Rushing Yards">Rushing Yards</option>
          <option value="Receiving Yards">Receiving Yards</option>
          <option value="Strikeouts">Strikeouts</option>
          <option value="Total Bases">Total Bases</option>
          <option value="Shots on Goal">Shots on Goal</option>
          <option value="Goal Contributions">Goal Contributions</option>
        </select>
      </div>
      
      {/* Team Filter */}
      <div className="mb-4">
        <label htmlFor="team" className="block text-sm font-medium text-gray-700 mb-1">
          Team
        </label>
        <select
          id="team"
          name="team"
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          value={filters.team}
          onChange={handleTeamChange}
        >
          <option value="">All Teams</option>
          <option value="LAL">Los Angeles Lakers</option>
          <option value="BOS">Boston Celtics</option>
          <option value="GSW">Golden State Warriors</option>
          <option value="PHI">Philadelphia 76ers</option>
          <option value="DEN">Denver Nuggets</option>
          <option value="DAL">Dallas Mavericks</option>
          <option value="MIA">Miami Heat</option>
          <option value="PHX">Phoenix Suns</option>
          <option value="KC">Kansas City Chiefs</option>
          <option value="BAL">Baltimore Ravens</option>
          <option value="LAD">Los Angeles Dodgers</option>
          <option value="NYY">New York Yankees</option>
          <option value="EDM">Edmonton Oilers</option>
          <option value="TOR">Toronto Maple Leafs</option>
          <option value="MCI">Manchester City</option>
          <option value="LIV">Liverpool</option>
        </select>
      </div>
      
      {/* Player Filter */}
      <div className="mb-6">
        <label htmlFor="player" className="block text-sm font-medium text-gray-700 mb-1">
          Player
        </label>
        <input
          type="text"
          id="player"
          name="player"
          placeholder="Search player name"
          className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          value={filters.player}
          onChange={handlePlayerSearch}
        />
      </div>
      
      {/* Filter Buttons */}
      <div className="flex space-x-3">
        <button
          type="button"
          className="flex-1 rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          onClick={() => updateFilters({})}
        >
          Apply Filters
        </button>
        <button
          type="button"
          className="flex-1 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50"
          onClick={resetFilters}
        >
          Reset
        </button>
      </div>
    </div>
  );
}
