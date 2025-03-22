"""
User Guide for Neural Network-Based Sports Predictor for PrizePicks

This document provides detailed instructions on how to use the Neural Network-Based Sports Predictor system.
"""

# User Guide: Neural Network-Based Sports Predictor for PrizePicks

## Introduction

The Neural Network-Based Sports Predictor is a sophisticated system designed to generate accurate predictions for PrizePicks over/under lines across multiple sports. This guide will walk you through the setup, configuration, and daily operation of the system.

## System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.10 or higher
- **RAM**: Minimum 8GB, recommended 16GB+
- **Storage**: Minimum 50GB for data storage
- **Internet Connection**: Required for data collection

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/neural-sports-predictor.git
cd neural-sports-predictor
```

### Step 2: Set Up Python Environment

It's recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Data Sources

1. Open `config/pipeline/data_collection.json`
2. Add your API keys for the following services:
   - Sports data providers (e.g., SportRadar, ESPN)
   - Weather data services (for outdoor sports)
   - News and social media APIs
3. Save the configuration file

## Basic Usage

### Running the Full Pipeline

To run the complete pipeline (data collection, training, and prediction):

```bash
python main.py --mode full
```

This will:
1. Collect the latest data for all configured sports
2. Retrain the models with the updated data
3. Generate predictions for upcoming games
4. Save the predictions to the output directory

### Running Individual Components

#### Data Collection Only

```bash
python main.py --mode collect
```

This will gather the latest data for all sports and save it to the `output/data/YYYY-MM-DD/` directory.

#### Training Only

```bash
python main.py --mode train
```

This will train models using the most recent data and save them to the `models/` directory.

#### Prediction Only

```bash
python main.py --mode predict
```

This will generate predictions using the latest trained models and save them to the `output/predictions/` directory.

### Sport-Specific Operations

To run operations for a specific sport only:

```bash
python main.py --mode predict --sport nba
```

Supported sport values: `nba`, `nfl`, `mlb`, `nhl`, `soccer`

### Date-Specific Operations

To run operations for a specific date:

```bash
python main.py --mode predict --date 2025-03-21
```

## Automated Operation

### Setting Up the Daemon

For continuous operation, run the system as a daemon:

```bash
python main.py --mode daemon
```

This will:
1. Start the automation system
2. Schedule daily data collection, training, and prediction
3. Run monitoring checks at regular intervals
4. Continue running until manually stopped

To stop the daemon, press `Ctrl+C` in the terminal.

### Configuring the Schedule

To customize the scheduling:

1. Open `config/pipeline/automation.json`
2. Modify the following settings:
   - `data_collection_time`: Time to run daily data collection (e.g., "01:00")
   - `training_time`: Time to run daily model training (e.g., "02:00")
   - `prediction_time`: Time to generate daily predictions (e.g., "08:00")
   - `monitoring_interval_hours`: Hours between monitoring checks (e.g., 6)
3. Save the configuration file

## Understanding Predictions

### Prediction Output Format

Predictions are saved as JSON files in the `output/predictions/` directory. Each prediction includes:

```json
{
  "player": "LeBron James",
  "team": "LAL",
  "opponent": "BOS",
  "date": "2025-03-21",
  "stat": "Points",
  "predicted_value": 27.5,
  "over_probability": 0.74,
  "line": 25.5,
  "confidence": "High",
  "confidence_score": 80,
  "top_factors": ["High usage rate", "Weak opponent defense", "Recent scoring streak"]
}
```

### Key Fields

- `predicted_value`: The exact statistical value the player is predicted to achieve
- `over_probability`: The probability (0-1) that the player will exceed the PrizePicks line
- `confidence`: Categorical confidence level (Very Low, Low, Moderate, High, Very High)
- `confidence_score`: Numerical confidence score (0-100)
- `top_factors`: Key factors influencing the prediction

### Interpreting Confidence

- **Very High** (90-100): Extremely confident prediction
- **High** (75-89): Strong confidence in the prediction
- **Moderate** (50-74): Reasonable confidence, but some uncertainty
- **Low** (25-49): Significant uncertainty in the prediction
- **Very Low** (0-24): Highly uncertain prediction

## Monitoring Performance

### Running Performance Monitoring

```bash
python main.py --mode monitor
```

This will:
1. Analyze recent prediction performance
2. Generate performance visualizations
3. Check for data drift and model degradation
4. Save results to the `output/monitoring/` directory

### Viewing Performance Reports

Performance visualizations are saved in the `output/monitoring/visualizations/` directory, including:

- Accuracy trends over time
- Regression error metrics
- Classification performance
- Confidence calibration curves
- Sport-by-sport comparisons

## Customization

### Adding a New Sport

1. Create a new configuration file in `config/sports/` (use existing files as templates)
2. Implement a sport-specific data collector in `src/data_collection/`
3. Update the normalization mappings in `src/models/normalizer.py`
4. Test the integration with the existing pipeline

### Modifying Model Architecture

To customize the neural network architecture:

1. Modify `src/models/base_model.py` for core architecture changes
2. Adjust `src/models/sport_specific_model.py` for sport-specific adaptations
3. Update hyperparameters in `config/pipeline/training.json`

### Adjusting Feature Engineering

To modify the features used by the model:

1. Edit `src/models/feature_engineering.py`
2. Update the feature configuration in `config/pipeline/training.json`

## Troubleshooting

### Common Issues

#### Data Collection Failures

**Symptoms**: Missing data files, error messages in logs about API failures

**Solutions**:
- Check API keys in configuration files
- Verify internet connection
- Check API rate limits
- Review logs for specific error messages

#### Training Errors

**Symptoms**: Failed model training, missing model files

**Solutions**:
- Ensure sufficient data is available
- Check for data format issues
- Verify GPU/CPU resources
- Adjust batch size or learning rate

#### Prediction Failures

**Symptoms**: Missing prediction files, incomplete predictions

**Solutions**:
- Verify model files exist
- Check for data preprocessing errors
- Ensure PrizePicks lines are available
- Review logs for specific error messages

### Logging

Logs are stored in the `logs/` directory:
- `main_YYYYMMDD.log`: Main application logs
- `data_collection.log`: Data collection logs
- `training.log`: Model training logs
- `prediction.log`: Prediction generation logs
- `automation.log`: Automation system logs
- `monitoring.log`: Monitoring system logs

## Advanced Topics

### Ensemble Configuration

The system uses ensemble learning to improve prediction accuracy. To configure:

1. Open `config/pipeline/training.json`
2. Adjust the following settings:
   - `ensemble_models`: Number of models in the ensemble
   - `ensemble_diversity`: Parameter controlling model diversity
   - `ensemble_blend_weight`: Weight for blending ensemble predictions

### Uncertainty Estimation

To configure uncertainty estimation:

1. Open `config/pipeline/prediction.json`
2. Modify the following settings:
   - `mc_dropout_samples`: Number of Monte Carlo samples
   - `dropout_rate`: Dropout rate for uncertainty estimation
   - `max_expected_std`: Maximum expected standard deviation

## Support and Feedback

For support or to provide feedback, please contact:
- Email: support@example.com
- GitHub Issues: https://github.com/yourusername/neural-sports-predictor/issues
