"""
Technical Documentation for Neural Network-Based Sports Predictor for PrizePicks

This document provides detailed technical information about the system architecture, components, and implementation.
"""

# Technical Documentation: Neural Network-Based Sports Predictor for PrizePicks

## System Architecture

The Neural Network-Based Sports Predictor is built with a modular architecture designed for flexibility, scalability, and maintainability. The system consists of several key components that work together to provide accurate predictions for PrizePicks over/under lines.

### High-Level Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Data Collection│     │  Neural Network │     │    Prediction   │
│     Pipeline    │────▶│      Model      │────▶│    Pipeline     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                       ▲                       │
         │                       │                       │
         │                       │                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Automation   │     │    Training     │     │    Monitoring   │
│      System     │────▶│     Pipeline    │     │      System     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Component Descriptions

#### 1. Data Collection Pipeline

The data collection pipeline is responsible for gathering all necessary data from various sources, including:

- **Player Statistics**: Historical game logs and performance metrics
- **Team Data**: Team performance, rankings, and matchup history
- **Injury Reports**: Player availability and injury status
- **Schedules**: Game schedules, travel distances, rest days
- **Weather Conditions**: For outdoor sports
- **Betting Lines**: PrizePicks lines and other betting market data
- **News and Social Media**: Player news and sentiment analysis

**Key Classes:**
- `BaseDataCollector`: Abstract base class defining the interface for all sport-specific collectors
- `SportSpecificCollector`: Implementations for each supported sport (NBA, NFL, MLB, NHL, Soccer)
- `DataCollectionManager`: Orchestrates the collection process across all sports

**Data Flow:**
1. The `DataCollectionManager` initiates collection for each configured sport
2. Sport-specific collectors gather data from their respective sources
3. Data is cleaned, normalized, and stored in a consistent format
4. Processed data is saved to the data storage system

#### 2. Neural Network Model

The neural network model is the core of the prediction system, implementing a hybrid architecture that combines:

- **Feedforward Neural Network**: For processing static features
- **Sequence Models (LSTM/Transformer)**: For processing time-series data
- **Attention Mechanisms**: For focusing on relevant historical games
- **Player and Team Embeddings**: For capturing entity-specific characteristics

**Key Classes:**
- `BaseModel`: Core neural network architecture with dual-task learning
- `SportSpecificModel`: Extensions for each sport's unique requirements
- `MultiSportNormalizer`: Transforms sport-specific statistics into a common format
- `FeatureEngineer`: Creates derived features to enhance prediction accuracy
- `UncertaintyEstimator`: Provides methods for estimating prediction confidence

**Model Architecture:**
```
                                 ┌─────────────────┐
                                 │  Player/Team    │
                                 │   Embeddings    │
                                 └────────┬────────┘
                                          │
┌─────────────────┐            ┌─────────▼────────┐
│  Static Features│            │  Sequential Data  │
│    (Tabular)    │            │  (Game History)   │
└────────┬────────┘            └────────┬─────────┘
         │                              │
┌────────▼────────┐            ┌────────▼─────────┐
│   Feedforward   │            │  LSTM/Transformer │
│     Layers      │            │      Layers       │
└────────┬────────┘            └────────┬─────────┘
         │                              │
         └──────────────┬───────────────┘
                        │
              ┌─────────▼─────────┐
              │  Attention Layer  │
              └─────────┬─────────┘
                        │
              ┌─────────▼─────────┐
              │   Shared Hidden   │
              │      Layers       │
              └─────────┬─────────┘
                        │
                ┌───────┴───────┐
                │               │
      ┌─────────▼─────┐ ┌───────▼─────────┐
      │  Regression   │ │  Classification  │
      │    Output     │ │     Output      │
      └───────────────┘ └─────────────────┘
```

#### 3. Training Pipeline

The training pipeline handles model training, hyperparameter optimization, and ensemble creation:

**Key Classes:**
- `TrainingPipeline`: Manages the end-to-end training process
- `HyperparameterOptimizer`: Finds optimal model configurations
- `EnsembleBuilder`: Creates and manages ensemble models

**Training Process:**
1. Data is split into training, validation, and test sets
2. Feature engineering is applied to create derived features
3. Hyperparameter optimization is performed to find the best configuration
4. Multiple models are trained for ensemble learning
5. Models are evaluated on validation data
6. Final models are saved for prediction

#### 4. Prediction Pipeline

The prediction pipeline generates daily predictions for upcoming games:

**Key Classes:**
- `PredictionPipeline`: Manages the prediction generation process
- `PredictionFormatter`: Formats predictions in the standardized output format

**Prediction Process:**
1. Latest data is collected for upcoming games
2. Feature engineering is applied to prepare input data
3. Models generate predictions (both regression and classification)
4. Uncertainty estimation is performed using Monte Carlo Dropout
5. Confidence scores are calculated based on uncertainty
6. Key factors influencing predictions are identified
7. Predictions are formatted and saved

#### 5. Automation System

The automation system orchestrates the daily workflow:

**Key Classes:**
- `AutomationSystem`: Manages scheduling and orchestration
- `TaskScheduler`: Schedules and executes tasks at specified times

**Automation Process:**
1. Data collection is scheduled for early morning
2. Model training follows data collection
3. Predictions are generated before the start of games
4. Performance monitoring is run after game results are available

#### 6. Monitoring System

The monitoring system tracks performance and ensures prediction quality:

**Key Classes:**
- `MonitoringSystem`: Manages performance tracking and alerting
- `PerformanceTracker`: Tracks prediction accuracy over time
- `DataDriftDetector`: Identifies changes in data distributions
- `ConfidenceCalibrator`: Ensures probability estimates are accurate

**Monitoring Process:**
1. Predictions are compared with actual outcomes
2. Performance metrics are calculated and tracked
3. Data drift is detected by comparing feature distributions
4. Confidence calibration is performed to improve probability estimates
5. Alerts are generated for performance degradation or data issues

## Data Flow

### End-to-End Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Raw Data    │     │ Processed   │     │ Trained     │     │ Predictions │
│ Sources     │────▶│ Data        │────▶│ Models      │────▶│             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                           │                   ▲                   │
                           │                   │                   │
                           ▼                   │                   ▼
                    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
                    │ Feature     │     │ Performance │     │ Actual      │
                    │ Engineering │────▶│ Monitoring  │◀────│ Outcomes    │
                    └─────────────┘     └─────────────┘     └─────────────┘
```

### Data Storage Structure

```
neural_sports_predictor/
├── data/
│   ├── raw/                  # Raw data from sources
│   │   ├── YYYY-MM-DD/       # Date-specific directories
│   │   │   ├── nba/          # Sport-specific directories
│   │   │   ├── nfl/
│   │   │   └── ...
│   ├── processed/            # Processed and feature-engineered data
│   │   ├── YYYY-MM-DD/
│   │   │   ├── nba/
│   │   │   ├── nfl/
│   │   │   └── ...
│   └── external/             # External data sources
│       ├── weather/
│       ├── betting_lines/
│       └── news/
├── models/                   # Saved models
│   ├── nba/
│   │   ├── YYYY-MM-DD/       # Date-specific model versions
│   │   │   ├── base_model.h5
│   │   │   ├── ensemble_models/
│   │   │   └── normalizer.pkl
│   ├── nfl/
│   └── ...
└── output/                   # System outputs
    ├── predictions/
    │   ├── YYYY-MM-DD/
    │   │   ├── nba_predictions.json
    │   │   ├── nfl_predictions.json
    │   │   └── ...
    ├── monitoring/
    │   ├── performance/
    │   ├── data_drift/
    │   └── visualizations/
    └── logs/
```

## Implementation Details

### Data Collection

#### API Integration

The system integrates with various sports data APIs:

- **SportRadar**: Primary source for game data, player stats, and team information
- **Weather API**: For outdoor sports weather conditions
- **News API**: For player news and updates
- **Twitter API**: For social media sentiment analysis
- **Betting APIs**: For PrizePicks lines and other betting market data

Example API integration (simplified):

```python
def fetch_player_stats(player_id, date_range):
    """Fetch player statistics from SportRadar API."""
    url = f"{BASE_URL}/players/{player_id}/stats"
    params = {
        "api_key": API_KEY,
        "start_date": date_range[0],
        "end_date": date_range[1]
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"API error: {response.status_code}")
        return None
```

#### Web Scraping

For data not available through APIs, the system uses web scraping with appropriate rate limiting and error handling:

```python
def scrape_prizepicks_lines():
    """Scrape PrizePicks lines from website."""
    url = "https://prizepicks.com/lines"
    
    headers = {
        "User-Agent": "Mozilla/5.0 ..."
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract lines from HTML
        lines = []
        for element in soup.select('.player-prop'):
            player = element.select_one('.player-name').text
            stat = element.select_one('.stat-type').text
            line = float(element.select_one('.line-value').text)
            
            lines.append({
                'player': player,
                'stat': stat,
                'line': line
            })
        
        return lines
    except Exception as e:
        logger.error(f"Scraping error: {str(e)}")
        return []
```

### Neural Network Implementation

#### Model Definition

The neural network model is implemented using TensorFlow/Keras:

```python
def build_model(config):
    """Build the neural network model."""
    # Input layers
    static_input = Input(shape=(config['static_features'],), name='static_input')
    sequence_input = Input(shape=(config['sequence_length'], config['sequence_features']), name='sequence_input')
    player_input = Input(shape=(1,), name='player_id')
    team_input = Input(shape=(1,), name='team_id')
    opponent_input = Input(shape=(1,), name='opponent_id')
    
    # Embedding layers
    player_embedding = Embedding(
        config['num_players'], config['embedding_dim'],
        name='player_embedding'
    )(player_input)
    player_embedding = Flatten()(player_embedding)
    
    team_embedding = Embedding(
        config['num_teams'], config['embedding_dim'],
        name='team_embedding'
    )(team_input)
    team_embedding = Flatten()(team_embedding)
    
    opponent_embedding = Embedding(
        config['num_teams'], config['embedding_dim'],
        name='opponent_embedding'
    )(opponent_input)
    opponent_embedding = Flatten()(opponent_embedding)
    
    # Static features processing
    static_features = Dense(128, activation='relu')(static_input)
    static_features = BatchNormalization()(static_features)
    static_features = Dropout(0.3)(static_features)
    static_features = Dense(64, activation='relu')(static_features)
    
    # Sequence processing (LSTM or Transformer)
    if config['sequence_model'] == 'lstm':
        sequence_features = LSTM(64, return_sequences=True)(sequence_input)
        sequence_features = LSTM(32)(sequence_features)
    else:  # Transformer
        sequence_features = TransformerBlock(
            embed_dim=config['sequence_features'],
            num_heads=4,
            ff_dim=64
        )(sequence_input)
        sequence_features = GlobalAveragePooling1D()(sequence_features)
    
    sequence_features = Dropout(0.3)(sequence_features)
    
    # Combine features
    combined = Concatenate()([
        static_features, sequence_features,
        player_embedding, team_embedding, opponent_embedding
    ])
    
    # Shared layers
    shared = Dense(128, activation='relu')(combined)
    shared = BatchNormalization()(shared)
    shared = Dropout(0.3)(shared)
    shared = Dense(64, activation='relu')(shared)
    shared = Dropout(0.3)(shared)
    
    # Output heads
    regression_output = Dense(1, name='regression_output')(shared)
    classification_output = Dense(1, activation='sigmoid', name='classification_output')(shared)
    
    # Create model
    model = Model(
        inputs=[static_input, sequence_input, player_input, team_input, opponent_input],
        outputs=[regression_output, classification_output]
    )
    
    # Compile model
    model.compile(
        optimizer=Adam(learning_rate=config['learning_rate']),
        loss={
            'regression_output': 'mse',
            'classification_output': 'binary_crossentropy'
        },
        metrics={
            'regression_output': ['mae'],
            'classification_output': ['accuracy', AUC()]
        }
    )
    
    return model
```

#### Transformer Block Implementation

```python
class TransformerBlock(Layer):
    """Transformer block with multi-head self-attention."""
    
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = Sequential([
            Dense(ff_dim, activation="relu"),
            Dense(embed_dim),
        ])
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(rate)
        self.dropout2 = Dropout(rate)
    
    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)
```

### Feature Engineering

The system implements sophisticated feature engineering to enhance prediction accuracy:

```python
def engineer_player_features(player_data):
    """Engineer features from player data."""
    # Convert to DataFrame
    df = pd.DataFrame(player_data)
    
    # Sort by date
    df['game_date'] = pd.to_datetime(df['game_date'])
    df = df.sort_values('game_date')
    
    # Create rolling averages
    for window in [3, 5, 10]:
        for stat in ['points', 'reboun<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>