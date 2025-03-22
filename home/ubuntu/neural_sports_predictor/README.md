# Neural Network-Based Sports Predictor for PrizePicks

## Overview

This project implements a neural network-driven sports prediction system tailored for PrizePicks over/under forecasting. The system is designed to be powerful, flexible, and self-updating, achieving high accuracy across multiple sports including NBA, NFL, MLB, NHL, and soccer.

## Key Features

- **Multi-Sport Support**: Handles different sports with their unique statistics while using a common framework
- **Automated Data Collection**: Gathers comprehensive data including player statistics, team matchups, injury reports, schedules, weather conditions, betting lines, and social media sentiment
- **Dual-Task Prediction**: Performs both regression (exact stat value prediction) and classification (over/under probability)
- **Advanced Neural Network Architecture**: Utilizes hybrid deep learning with feedforward networks, sequence models, attention mechanisms, and player embeddings
- **Accuracy-Boosting Techniques**: Implements feature engineering, regularization, hyperparameter optimization, ensemble learning, and uncertainty estimation
- **Daily Retraining**: Automatically updates with the latest data to continuously improve predictions
- **Performance Monitoring**: Tracks prediction accuracy, detects data drift, and calibrates confidence estimates

## System Architecture

The system is organized into several key components:

1. **Data Collection**: Gathers data from various sources for all supported sports
2. **Neural Network Model**: Processes data and generates predictions with uncertainty estimates
3. **Training Pipeline**: Handles model training, hyperparameter optimization, and ensemble creation
4. **Prediction Pipeline**: Generates daily predictions for upcoming games
5. **Automation System**: Orchestrates the daily workflow of data collection, training, and prediction
6. **Monitoring System**: Tracks performance and ensures prediction quality

## Installation

### Prerequisites

- Python 3.10+
- TensorFlow 2.x
- pandas, numpy, scikit-learn
- Other dependencies listed in requirements.txt

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/neural-sports-predictor.git
cd neural-sports-predictor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the system:
- Update API keys and data source configurations in `config/pipeline/data_collection.json`
- Adjust model parameters in `config/pipeline/training.json` if needed
- Set scheduling preferences in `config/pipeline/automation.json`

## Usage

### Running the System

The system can be run in various modes using the main script:

```bash
# Run data collection only
python main.py --mode collect

# Run model training only
python main.py --mode train

# Generate predictions only
python main.py --mode predict

# Run the full pipeline (collect, train, predict)
python main.py --mode full

# Run the system as a daemon (continuous operation)
python main.py --mode daemon

# Run performance monitoring
python main.py --mode monitor
```

### Sport-Specific Operation

You can also run the system for a specific sport:

```bash
python main.py --mode predict --sport nba
```

### Output

Predictions are saved in JSON format in the `output/predictions` directory. Each prediction includes:

- Player information (name, team, opponent)
- Game date and context
- Predicted stat value (regression output)
- Over/under probability for the PrizePicks line
- Confidence score and uncertainty range
- Key factors influencing the prediction

## Project Structure

```
neural_sports_predictor/
├── config/                  # Configuration files
│   ├── sports/              # Sport-specific configurations
│   └── pipeline/            # Pipeline configurations
├── src/                     # Source code
│   ├── data_collection/     # Data collection modules
│   ├── models/              # Neural network model components
│   ├── training/            # Training and prediction pipelines
│   └── automation/          # Automation and monitoring systems
├── tests/                   # Test modules
├── data/                    # Data storage
├── models/                  # Saved models
├── output/                  # System outputs
│   ├── data/                # Processed data
│   ├── training/            # Training results
│   ├── predictions/         # Generated predictions
│   ├── monitoring/          # Monitoring results
│   └── evaluation/          # Performance evaluation
└── logs/                    # System logs
```

## Extending the System

### Adding a New Sport

1. Create a new sport configuration file in `config/sports/`
2. Implement a sport-specific data collector in `src/data_collection/`
3. Update the data normalization mappings in `src/models/normalizer.py`
4. Test the integration with the existing pipeline

### Customizing the Model

The neural network architecture can be customized by modifying:

- `src/models/base_model.py`: Core model architecture
- `src/models/sport_specific_model.py`: Sport-specific adaptations
- `config/pipeline/training.json`: Training hyperparameters

## Performance Monitoring

The system includes comprehensive performance monitoring:

- Accuracy tracking for both regression and classification tasks
- Data drift detection to identify when input distributions change
- Confidence calibration to ensure probability estimates are accurate
- Visualization tools for performance analysis

## Testing

Run the test suite to verify system functionality:

```bash
python -m unittest discover tests
```

## License

[Specify your license information here]

## Acknowledgments

[Any acknowledgments or credits]
