import { Layout } from "@/components/layout/Layout";

export default function Home() {
  return (
    <Layout>
      <div className="flex flex-col items-center justify-center min-h-screen py-2">
        <main className="flex flex-col items-center justify-center w-full flex-1 px-4 sm:px-20 text-center">
          <h1 className="text-4xl font-bold text-blue-600 mb-8">
            PrizePicks Sports Predictor
          </h1>
          <p className="text-xl mb-8">
            Neural Network-Based Sports Prediction System
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl">
            <a
              href="/dashboard"
              className="p-6 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 flex flex-col items-center"
            >
              <h2 className="text-2xl font-bold text-blue-600 mb-4">Dashboard</h2>
              <p className="text-gray-700">
                View summary statistics and featured predictions
              </p>
            </a>
            <a
              href="/predictions"
              className="p-6 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 flex flex-col items-center"
            >
              <h2 className="text-2xl font-bold text-blue-600 mb-4">Predictions</h2>
              <p className="text-gray-700">
                Browse and filter all available predictions
              </p>
            </a>
            <a
              href="/performance"
              className="p-6 bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-300 flex flex-col items-center"
            >
              <h2 className="text-2xl font-bold text-blue-600 mb-4">Performance</h2>
              <p className="text-gray-700">
                Track prediction accuracy and historical performance
              </p>
            </a>
          </div>
        </main>
      </div>
    </Layout>
  );
}
