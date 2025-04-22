"use client";
import React from "react";

function MainComponent({
  metrics,
  loading = false,
  error = null,
  timeRange = 3,
  onTimeRangeChange,
}) {
  const [localMetrics, setLocalMetrics] = useState(null);
  const [localLoading, setLocalLoading] = useState(loading);
  const [localError, setLocalError] = useState(error);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await fetch("/api/dashboard-kp-is", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            timeRange,
            includeProjections: true,
            visualizationType: "all",
          }),
        });

        if (!response.ok) throw new Error("Failed to fetch metrics");

        const data = await response.json();
        if (data.success) {
          setLocalMetrics(data.data);
        } else {
          throw new Error(data.error);
        }
      } catch (err) {
        setLocalError(err.message);
      } finally {
        setLocalLoading(false);
      }
    };

    if (!metrics) {
      fetchMetrics();
    } else {
      setLocalMetrics(metrics);
    }
  }, [timeRange, metrics]);

  if (localLoading) {
    return (
      <div className="flex justify-center items-center p-8">
        <i className="fas fa-spinner fa-spin text-3xl text-blue-600"></i>
      </div>
    );
  }

  if (localError) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        Error: {localError}
      </div>
    );
  }

  if (!localMetrics) return null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div className="bg-white/10 backdrop-blur-sm p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <div className="p-3 bg-red-100 rounded-full">
              <i className="fas fa-exclamation-triangle text-red-600 text-xl"></i>
            </div>
            <div className="text-right">
              <p className="text-white text-sm">Portfolio at Risk</p>
              <p className="text-2xl font-bold text-white">
                {localMetrics.financial_metrics.portfolio_at_risk.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-sm p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <div className="p-3 bg-green-100 rounded-full">
              <i className="fas fa-check-circle text-green-600 text-xl"></i>
            </div>
            <div className="text-right">
              <p className="text-white text-sm">Repayment Rate</p>
              <p className="text-2xl font-bold text-white">
                {localMetrics.financial_metrics.repayment_rate.toFixed(2)}%
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-sm p-6 rounded-xl">
          <div className="flex items-center justify-between">
            <div className="p-3 bg-blue-100 rounded-full">
              <i className="fas fa-percentage text-blue-600 text-xl"></i>
            </div>
            <div className="text-right">
              <p className="text-white text-sm">Interest Collection</p>
              <p className="text-2xl font-bold text-white">
                {localMetrics.financial_metrics.interest_collection_rate.toFixed(
                  2
                )}
                %
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white/10 backdrop-blur-sm p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-white mb-4">
          Next Month Predictions
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Object.entries(localMetrics.predictions.nextMonth).map(
            ([key, value]) => (
              <div key={key} className="bg-white/5 p-4 rounded-lg">
                <p className="text-white/80 text-sm">
                  {key.charAt(0).toUpperCase() + key.slice(1)}
                </p>
                <p className="text-xl font-bold text-white">
                  {typeof value === "number" ? value.toFixed(0) : value}
                </p>
                <div className="flex items-center mt-2">
                  <i
                    className={`fas fa-arrow-${
                      localMetrics.predictions.growthRates[key] > 0
                        ? "up text-green-400"
                        : "down text-red-400"
                    } mr-1`}
                  ></i>
                  <span
                    className={`text-sm ${
                      localMetrics.predictions.growthRates[key] > 0
                        ? "text-green-400"
                        : "text-red-400"
                    }`}
                  >
                    {Math.abs(
                      localMetrics.predictions.growthRates[key] * 100
                    ).toFixed(1)}
                    %
                  </span>
                </div>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

function StoryComponent() {
  const mockMetrics = {
    financial_metrics: {
      portfolio_at_risk: 5.2,
      repayment_rate: 94.8,
      interest_collection_rate: 97.3,
    },
    predictions: {
      nextMonth: {
        loans: 150,
        amount: 500000,
        savings: 300000,
        defaults: 3,
      },
      growthRates: {
        loans: 0.15,
        amount: 0.08,
        savings: 0.12,
        defaults: -0.05,
      },
    },
  };

  return (
    <div className="bg-gradient-to-br from-blue-900 to-indigo-900 p-8 space-y-8">
      <div>
        <h2 className="text-xl font-bold text-white mb-4">Loading State</h2>
        <MainComponent loading={true} />
      </div>

      <div>
        <h2 className="text-xl font-bold text-white mb-4">Error State</h2>
        <MainComponent error="Failed to load metrics" />
      </div>

      <div>
        <h2 className="text-xl font-bold text-white mb-4">With Data</h2>
        <MainComponent metrics={mockMetrics} />
      </div>
    </div>
  );
}

export default MainComponent;