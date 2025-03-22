import { Layout } from "@/components/layout/Layout";

export default function About() {
  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">About PrizePicks Sports Predictor</h1>
        
        {/* Overview Section */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Overview</h2>
            <p className="text-gray-700 mb-4">
              The PrizePicks Sports Predictor is a neural network-driven sports prediction system tailored for PrizePicks over/under forecasting. 
              The system is designed to be powerful, flexible, and self-updating, achieving high accuracy across multiple sports.
            </p>
            <p className="text-gray-700">
              Using advanced machine learning techniques, the system analyzes vast amounts of data to predict player performance and provide 
              confidence-rated recommendations for PrizePicks contests.
            </p>
          </div>
        </div>
        
        {/* Features Section */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Key Features</h2>
            <ul className="space-y-2 text-gray-700">
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Multi-Sport Support:</strong> Predictions for NBA, NFL, MLB, NHL, and soccer</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Dual-Task Prediction:</strong> Both exact statistical values and over/under probabilities</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Advanced Neural Network:</strong> Hybrid architecture with sequence models and attention mechanisms</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Comprehensive Data Analysis:</strong> Player stats, team matchups, injuries, schedules, weather, and more</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Daily Updates:</strong> Automated data collection and model retraining</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Confidence Ratings:</strong> Uncertainty estimation for each prediction</span>
              </li>
              <li className="flex items-start">
                <span className="text-blue-600 mr-2">•</span>
                <span><strong>Performance Tracking:</strong> Continuous monitoring and improvement</span>
              </li>
            </ul>
          </div>
        </div>
        
        {/* Technology Section */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Technology</h2>
            <p className="text-gray-700 mb-4">
              The PrizePicks Sports Predictor is built using cutting-edge technologies:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="text-md font-medium text-gray-900 mb-2">Data Collection</h3>
                <ul className="space-y-1 text-gray-700 text-sm">
                  <li>• Sports data APIs</li>
                  <li>• Web scraping</li>
                  <li>• News and social media analysis</li>
                  <li>• Weather data integration</li>
                </ul>
              </div>
              <div>
                <h3 className="text-md font-medium text-gray-900 mb-2">Machine Learning</h3>
                <ul className="space-y-1 text-gray-700 text-sm">
                  <li>• TensorFlow/PyTorch</li>
                  <li>• LSTM and Transformer models</li>
                  <li>• Attention mechanisms</li>
                  <li>• Ensemble learning</li>
                </ul>
              </div>
              <div>
                <h3 className="text-md font-medium text-gray-900 mb-2">Backend</h3>
                <ul className="space-y-1 text-gray-700 text-sm">
                  <li>• Python</li>
                  <li>• Automated pipelines</li>
                  <li>• Database storage</li>
                  <li>• RESTful API</li>
                </ul>
              </div>
              <div>
                <h3 className="text-md font-medium text-gray-900 mb-2">Frontend</h3>
                <ul className="space-y-1 text-gray-700 text-sm">
                  <li>• Next.js</li>
                  <li>• Tailwind CSS</li>
                  <li>• Responsive design</li>
                  <li>• Data visualization</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        
        {/* How It Works Section */}
        <div className="bg-white shadow rounded-lg mb-8">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">How It Works</h2>
            <ol className="space-y-4 text-gray-700">
              <li className="flex">
                <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0">1</span>
                <div>
                  <h3 className="font-medium text-gray-900">Data Collection</h3>
                  <p className="mt-1">The system automatically collects data from various sources including player statistics, team matchups, injury reports, schedules, weather conditions, betting lines, and player news.</p>
                </div>
              </li>
              <li className="flex">
                <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0">2</span>
                <div>
                  <h3 className="font-medium text-gray-900">Feature Engineering</h3>
                  <p className="mt-1">Raw data is transformed into meaningful features that capture player form, matchup context, and other relevant factors that influence performance.</p>
                </div>
              </li>
              <li className="flex">
                <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0">3</span>
                <div>
                  <h3 className="font-medium text-gray-900">Neural Network Processing</h3>
                  <p className="mt-1">The hybrid neural network processes the features, using sequence models to capture temporal patterns and attention mechanisms to focus on the most relevant information.</p>
                </div>
              </li>
              <li className="flex">
                <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0">4</span>
                <div>
                  <h3 className="font-medium text-gray-900">Dual Prediction</h3>
                  <p className="mt-1">The system generates both a regression prediction (exact statistical value) and a classification prediction (probability of over/under) for each player stat.</p>
                </div>
              </li>
              <li className="flex">
                <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0">5</span>
                <div>
                  <h3 className="font-medium text-gray-900">Confidence Estimation</h3>
                  <p className="mt-1">Uncertainty estimation techniques are applied to gauge the confidence of each prediction, helping users make informed decisions.</p>
                </div>
              </li>
              <li className="flex">
                <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center mr-3 flex-shrink-0">6</span>
                <div>
                  <h3 className="font-medium text-gray-900">Performance Tracking</h3>
                  <p className="mt-1">The system continuously monitors prediction accuracy and uses this feedback to improve future predictions.</p>
                </div>
              </li>
            </ol>
          </div>
        </div>
        
        {/* FAQ Section */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Frequently Asked Questions</h2>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900">How accurate are the predictions?</h3>
                <p className="mt-1 text-gray-700">
                  The system achieves varying accuracy rates depending on the sport and stat type. Overall accuracy typically ranges from 65-80%, 
                  with high-confidence predictions achieving the upper end of this range.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900">How often are predictions updated?</h3>
                <p className="mt-1 text-gray-700">
                  The system collects new data and retrains its models daily, ensuring predictions reflect the latest information.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900">What does the confidence rating mean?</h3>
                <p className="mt-1 text-gray-700">
                  Confidence ratings indicate how certain the model is about its prediction. Higher confidence ratings generally correlate with higher accuracy.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Can I request predictions for specific players?</h3>
                <p className="mt-1 text-gray-700">
                  Currently, the system automatically generates predictions for all players with PrizePicks lines. Custom prediction requests may be added in a future update.
                </p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900">How should I use these predictions?</h3>
                <p className="mt-1 text-gray-700">
                  The predictions are designed to provide data-driven insights to inform your PrizePicks selections. We recommend focusing on high-confidence predictions 
                  and considering the key factors provided with each prediction.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
