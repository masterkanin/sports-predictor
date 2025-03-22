import { Layout } from "@/components/layout/Layout";

export default function Settings() {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Settings</h1>
        
        {/* Filters Configuration */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Default Filters</h2>
            <p className="text-sm text-gray-500 mb-4">Configure your default filter settings for predictions.</p>
            
            <div className="space-y-6">
              {/* Default Sport */}
              <div>
                <label htmlFor="default-sport" className="block text-sm font-medium text-gray-700 mb-1">
                  Default Sport
                </label>
                <select
                  id="default-sport"
                  name="default-sport"
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="">All Sports</option>
                  <option value="nba">NBA</option>
                  <option value="nfl">NFL</option>
                  <option value="mlb">MLB</option>
                  <option value="nhl">NHL</option>
                  <option value="soccer">Soccer</option>
                </select>
              </div>
              
              {/* Default Confidence Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Default Confidence Levels
                </label>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      id="settings-very-high"
                      name="settings-confidence"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      defaultChecked
                    />
                    <label htmlFor="settings-very-high" className="ml-2 text-sm text-gray-700">
                      Very High
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="settings-high"
                      name="settings-confidence"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      defaultChecked
                    />
                    <label htmlFor="settings-high" className="ml-2 text-sm text-gray-700">
                      High
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="settings-moderate"
                      name="settings-confidence"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      defaultChecked
                    />
                    <label htmlFor="settings-moderate" className="ml-2 text-sm text-gray-700">
                      Moderate
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="settings-low"
                      name="settings-confidence"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <label htmlFor="settings-low" className="ml-2 text-sm text-gray-700">
                      Low
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="settings-very-low"
                      name="settings-confidence"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <label htmlFor="settings-very-low" className="ml-2 text-sm text-gray-700">
                      Very Low
                    </label>
                  </div>
                </div>
              </div>
              
              {/* Default Time Period */}
              <div>
                <label htmlFor="default-time-period" className="block text-sm font-medium text-gray-700 mb-1">
                  Default Time Period for Performance
                </label>
                <select
                  id="default-time-period"
                  name="default-time-period"
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="7">Last 7 Days</option>
                  <option value="30" selected>Last 30 Days</option>
                  <option value="90">Last 90 Days</option>
                  <option value="ytd">Year to Date</option>
                  <option value="all">All Time</option>
                </select>
              </div>
            </div>
          </div>
        </div>
        
        {/* Display Preferences */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Display Preferences</h2>
            <p className="text-sm text-gray-500 mb-4">Customize how predictions and data are displayed.</p>
            
            <div className="space-y-6">
              {/* Theme */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Theme
                </label>
                <div className="flex items-center space-x-4">
                  <div className="flex items-center">
                    <input
                      id="theme-light"
                      name="theme"
                      type="radio"
                      className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
                      defaultChecked
                    />
                    <label htmlFor="theme-light" className="ml-2 text-sm text-gray-700">
                      Light
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="theme-dark"
                      name="theme"
                      type="radio"
                      className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <label htmlFor="theme-dark" className="ml-2 text-sm text-gray-700">
                      Dark
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="theme-system"
                      name="theme"
                      type="radio"
                      className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <label htmlFor="theme-system" className="ml-2 text-sm text-gray-700">
                      System
                    </label>
                  </div>
                </div>
              </div>
              
              {/* Predictions Per Page */}
              <div>
                <label htmlFor="predictions-per-page" className="block text-sm font-medium text-gray-700 mb-1">
                  Predictions Per Page
                </label>
                <select
                  id="predictions-per-page"
                  name="predictions-per-page"
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                >
                  <option value="6">6</option>
                  <option value="12" selected>12</option>
                  <option value="24">24</option>
                  <option value="48">48</option>
                </select>
              </div>
              
              {/* Display Options */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Display Options
                </label>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      id="show-key-factors"
                      name="show-key-factors"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      defaultChecked
                    />
                    <label htmlFor="show-key-factors" className="ml-2 text-sm text-gray-700">
                      Show Key Factors
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="show-confidence-bars"
                      name="show-confidence-bars"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      defaultChecked
                    />
                    <label htmlFor="show-confidence-bars" className="ml-2 text-sm text-gray-700">
                      Show Confidence Bars
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="compact-view"
                      name="compact-view"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <label htmlFor="compact-view" className="ml-2 text-sm text-gray-700">
                      Compact View
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Notification Settings (Future) */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Notification Settings</h2>
            <p className="text-sm text-gray-500 mb-4">Configure notification preferences (coming soon).</p>
            
            <div className="space-y-6 opacity-50">
              {/* Email Notifications */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Notifications
                </label>
                <div className="space-y-2">
                  <div className="flex items-center">
                    <input
                      id="notify-high-confidence"
                      name="notify-high-confidence"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      disabled
                    />
                    <label htmlFor="notify-high-confidence" className="ml-2 text-sm text-gray-700">
                      High Confidence Predictions
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="notify-performance-reports"
                      name="notify-performance-reports"
                      type="checkbox"
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      disabled
                    />
                    <label htmlFor="notify-performance-reports" className="ml-2 text-sm text-gray-700">
                      Weekly Performance Reports
                    </label>
                  </div>
                </div>
              </div>
              
              {/* Email Address */}
              <div>
                <label htmlFor="email-address" className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email-address"
                  name="email-address"
                  placeholder="your@email.com"
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                  disabled
                />
              </div>
            </div>
            
            <div className="mt-4 text-sm text-gray-500 italic">
              Notification features will be available in a future update.
            </div>
          </div>
        </div>
        
        {/* Save Button */}
        <div className="mt-8 flex justify-end">
          <button
            type="button"
            className="rounded-md bg-blue-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
          >
            Save Settings
          </button>
        </div>
      </div>
    </Layout>
  );
}
