"""
API Documentation for Neural Network-Based Sports Predictor for PrizePicks

This document provides detailed information about the system's API for integration with other applications.
"""

# API Documentation: Neural Network-Based Sports Predictor for PrizePicks

## Introduction

The Neural Network-Based Sports Predictor provides a programmatic interface for integrating with other applications. This document describes the available API endpoints, data formats, and usage examples.

## API Overview

The system provides both a command-line interface and a programmatic API for integration. The programmatic API allows other applications to:

1. Retrieve predictions for specific sports and dates
2. Access historical performance metrics
3. Trigger data collection and model training
4. Monitor system status and health

## Python API

### Initialization

```python
from neural_sports_predictor import PredictionSystem

# Initialize the system with configuration directory
system = PredictionSystem(config_dir='/path/to/config')
```

### Generating Predictions

```python
# Get predictions for all sports for today
predictions = system.generate_predictions()

# Get predictions for a specific sport
nba_predictions = system.generate_predictions(sport='nba')

# Get predictions for a specific date
predictions_0321 = system.generate_predictions(date='2025-03-21')

# Get predictions with minimum confidence threshold
high_confidence_predictions = system.generate_predictions(min_confidence=75)
```

### Accessing Historical Performance

```python
# Get performance metrics for the last 30 days
performance = system.get_performance_metrics(days=30)

# Get performance for a specific sport
nba_performance = system.get_performance_metrics(sport='nba')

# Get performance for a specific date range
custom_performance = system.get_performance_metrics(
    start_date='2025-02-01',
    end_date='2025-03-01'
)
```

### Training Models

```python
# Trigger model training for all sports
system.train_models()

# Train model for a specific sport
system.train_models(sport='nba')

# Train with specific configuration overrides
system.train_models(
    hyperparameters={
        'learning_rate': 0.001,
        'batch_size': 64
    }
)
```

### Data Collection

```python
# Trigger data collection for all sports
system.collect_data()

# Collect data for a specific sport
system.collect_data(sport='nba')

# Collect data for a specific date
system.collect_data(date='2025-03-21')
```

### System Monitoring

```python
# Get system status
status = system.get_status()

# Check for data drift
drift_report = system.check_data_drift()

# Get model calibration metrics
calibration = system.get_calibration_metrics()
```

## REST API

The system can also be configured to expose a REST API for integration with web applications or services.

### Configuration

To enable the REST API, set the following in `config/pipeline/api.json`:

```json
{
  "enable_rest_api": true,
  "host": "0.0.0.0",
  "port": 5000,
  "enable_authentication": true,
  "api_key": "your-secure-api-key"
}
```

### Authentication

All API endpoints require authentication using an API key:

```
Authorization: Bearer your-secure-api-key
```

### Endpoints

#### GET /predictions

Retrieve predictions for all sports or a specific sport.

**Parameters:**
- `sport` (optional): Sport name (e.g., "nba", "nfl")
- `date` (optional): Date in YYYY-MM-DD format
- `min_confidence` (optional): Minimum confidence score (0-100)

**Example Request:**
```
GET /predictions?sport=nba&date=2025-03-21&min_confidence=75
Authorization: Bearer your-secure-api-key
```

**Example Response:**
```json
{
  "sport": "nba",
  "date": "2025-03-21",
  "predictions": [
    {
      "player": "LeBron James",
      "team": "LAL",
      "opponent": "BOS",
      "stat": "Points",
      "predicted_value": 27.5,
      "over_probability": 0.74,
      "line": 25.5,
      "confidence": "High",
      "confidence_score": 80,
      "top_factors": ["High usage rate", "Weak opponent defense", "Recent scoring streak"]
    },
    // Additional predictions...
  ]
}
```

#### GET /performance

Retrieve performance metrics.

**Parameters:**
- `sport` (optional): Sport name (e.g., "nba", "nfl")
- `days` (optional): Number of days to include
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Example Request:**
```
GET /performance?sport=nba&days=30
Authorization: Bearer your-secure-api-key
```

**Example Response:**
```json
{
  "sport": "nba",
  "period": "last 30 days",
  "metrics": {
    "regression": {
      "mse": 5.2,
      "rmse": 2.28,
      "mae": 1.8
    },
    "classification": {
      "accuracy": 0.75,
      "auc": 0.82,
      "precision": 0.78,
      "recall": 0.72
    }
  }
}
```

#### POST /train

Trigger model training.

**Parameters:**
- `sport` (optional): Sport name (e.g., "nba", "nfl")

**Example Request:**
```
POST /train
Authorization: Bearer your-secure-api-key
Content-Type: application/json

{
  "sport": "nba"
}
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Training initiated for NBA",
  "job_id": "train_nba_20250321_123456"
}
```

#### POST /collect

Trigger data collection.

**Parameters:**
- `sport` (optional): Sport name (e.g., "nba", "nfl")
- `date` (optional): Date in YYYY-MM-DD format

**Example Request:**
```
POST /collect
Authorization: Bearer your-secure-api-key
Content-Type: application/json

{
  "sport": "nba",
  "date": "2025-03-21"
}
```

**Example Response:**
```json
{
  "status": "success",
  "message": "Data collection initiated for NBA on 2025-03-21",
  "job_id": "collect_nba_20250321_123456"
}
```

#### GET /status

Get system status.

**Example Request:**
```
GET /status
Authorization: Bearer your-secure-api-key
```

**Example Response:**
```json
{
  "status": "healthy",
  "components": {
    "data_collection": "operational",
    "training": "operational",
    "prediction": "operational",
    "monitoring": "operational"
  },
  "last_update": "2025-03-21T12:34:56Z",
  "version": "1.0.0"
}
```

## Webhook Integration

The system can be configured to send webhook notifications for various events.

### Configuration

To enable webhooks, set the following in `config/pipeline/api.json`:

```json
{
  "enable_webhooks": true,
  "webhook_url": "https://your-service.com/webhook",
  "webhook_events": ["predictions_ready", "training_complete", "data_drift_detected"],
  "webhook_secret": "your-webhook-secret"
}
```

### Webhook Payload

Each webhook includes a signature header for verification:

```
X-Webhook-Signature: HMAC-SHA256 signature
```

**Example Payload (predictions_ready):**
```json
{
  "event": "predictions_ready",
  "timestamp": "2025-03-21T12:34:56Z",
  "data": {
    "sport": "nba",
    "date": "2025-03-21",
    "prediction_count": 42,
    "url": "/predictions?sport=nba&date=2025-03-21"
  }
}
```

**Example Payload (training_complete):**
```json
{
  "event": "training_complete",
  "timestamp": "2025-03-21T12:34:56Z",
  "data": {
    "sport": "nba",
    "metrics": {
      "regression_mse": 5.2,
      "classification_accuracy": 0.75
    }
  }
}
```

**Example Payload (data_drift_detected):**
```json
{
  "event": "data_drift_detected",
  "timestamp": "2025-03-21T12:34:56Z",
  "data": {
    "sport": "nba",
    "features": ["points", "rebounds"],
    "drift_score": 0.08,
    "severity": "medium"
  }
}
```

## Data Formats

### Prediction Object

```json
{
  "player": "string",         // Player name
  "team": "string",           // Team abbreviation
  "opponent": "string",       // Opponent team abbreviation
  "date": "string",           // Game date (YYYY-MM-DD)
  "stat": "string",           // Statistic type (e.g., "Points", "Rebounds")
  "predicted_value": number,  // Predicted stat value
  "over_probability": number, // Probability of going over the line (0-1)
  "line": number,             // PrizePicks line
  "confidence": "string",     // Confidence category
  "confidence_score": number, // Confidence score (0-100)
  "prediction_range": [       // Prediction range (low, high)
    number,
    number
  ],
  "top_factors": [            // Top factors influencing prediction
    "string",
    "string",
    "string"
  ]
}
```

### Performance Metrics Object

```json
{
  "regression": {
    "mse": number,            // Mean squared error
    "rmse": number,           // Root mean squared error
    "mae": number,            // Mean absolute error
    "mape": number,           // Mean absolute percentage error
    "r2": number              // R-squared
  },
  "classification": {
    "accuracy": number,       // Overall accuracy
    "auc": number,            // Area under ROC curve
    "precision": number,      // Precision
    "recall": number,         // Recall
    "f1": number,             // F1 score
    "over_accuracy": number,  // Accuracy for over predictions
    "under_accuracy": number  // Accuracy for under predictions
  },
  "calibration": {
    "calibration_error": number,  // Calibration error
    "calibration_curve": [        // Calibration curve points
      {
        "confidence": number,     // Confidence bin
        "accuracy": number,       // Observed accuracy
        "count": number           // Number of samples
      }
    ]
  }
}
```

## Error Handling

All API endpoints return standard HTTP status codes:

- 200: Success
- 400: Bad request (invalid parameters)
- 401: Unauthorized (invalid or missing API key)
- 404: Not found (resource not available)
- 500: Internal server error

Error responses include a JSON object with details:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    // Additional error details
  }
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse. The default limits are:

- 100 requests per minute for GET endpoints
- 10 requests per minute for POST endpoints

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1616343600
```

## Integration Examples

### Python Client Example

```python
import requests
import json

API_URL = "http://your-server:5000"
API_KEY = "your-secure-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Get NBA predictions for today
response = requests.get(
    f"{API_URL}/predictions",
    params={"sport": "nba"},
    headers=headers
)

if response.status_code == 200:
    predictions = response.json()
    
    # Process predictions
    for pred in predictions["predictions"]:
        player = pred["player"]
        stat = pred["stat"]
        value = pred["predicted_value"]
        probability = pred["over_probability"]
        
        print(f"{player} {stat}: {value} ({probability*100:.1f}% over)")
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### JavaScript Client Example

```javascript
const API_URL = "http://your-server:5000";
const API_KEY = "your-secure-api-key";

async function getPredictions(sport = null, date = null) {
  const params = new URLSearchParams();
  if (sport) params.append("sport", sport);
  if (date) params.append("date", date);
  
  try {
    const response = await fetch(`${API_URL}/predictions?${params}`, {
      headers: {
        "Authorization": `Bearer ${API_KEY}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching predictions:", error);
    return null;
  }
}

// Usage
getPredictions("nba").then(data => {
  if (data) {
    console.log(`Found ${data.predictions.length} predictions`);
    
    // Process predictions
    data.predictions.forEach(pred => {
      console.log(
        `${pred.player} ${pred.stat}: ${pred.predicted_value} ` +
        `(${(pred.over_probability * 100).toFixed(1)}% over)`
      );
    });
  }
});
```

## Security Considerations

- Always use HTTPS in production environments
- Keep your API key secure and rotate it regularly
- Implement IP whitelisting for additional security
- Use webhook signatures to verify webhook authenticity
- Monitor API usage for unusual patterns

## Support and Feedback

For API support or to provide feedback, please contact:
- Email: api-support@example.com
- GitHub Issues: https://github.com/yourusername/neural-sports-predictor/issues
