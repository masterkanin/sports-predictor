"""
Main entry point for the neural network-based sports predictor.
This script provides a command-line interface to run the system.
"""

import os
import sys
import argparse
import logging
from datetime import datetime

from src.data_collection import DataCollectionManager
from src.training import TrainingPipeline, PredictionPipeline
from src.automation import AutomationSystem, MonitoringSystem

def setup_logging():
    """Set up logging configuration"""
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'main_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Create logger
    logger = logging.getLogger('main')
    logger.setLevel(logging.INFO)
    
    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create formatter and add to handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger if not already added
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description='Neural Network-Based Sports Predictor for PrizePicks')
    
    parser.add_argument('--mode', type=str, default='predict',
                        choices=['collect', 'train', 'predict', 'full', 'daemon', 'monitor'],
                        help='Operation mode')
    
    parser.add_argument('--sport', type=str, default=None,
                        help='Sport to process (default: all)')
    
    parser.add_argument('--date', type=str, default=None,
                        help='Date to process in YYYY-MM-DD format (default: today)')
    
    parser.add_argument('--config', type=str, default=None,
                        help='Path to configuration directory')
    
    parser.add_argument('--output', type=str, default=None,
                        help='Path to output directory')
    
    return parser.parse_args()

def main():
    """Main entry point"""
    # Parse arguments
    args = parse_args()
    
    # Setup logging
    logger = setup_logging()
    logger.info(f"Starting Neural Network-Based Sports Predictor in {args.mode} mode")
    
    # Set configuration directory
    config_dir = args.config or os.path.join(os.path.dirname(__file__), 'config')
    
    # Set date
    date = args.date or datetime.now().strftime('%Y-%m-%d')
    
    try:
        if args.mode == 'collect':
            # Run data collection
            logger.info("Running data collection")
            data_manager = DataCollectionManager(config_dir)
            
            if args.sport:
                data = data_manager.collect_data_for_sport(args.sport)
            else:
                data = data_manager.run_daily_collection()
            
            logger.info(f"Data collection completed for {len(data)} sports")
            
        elif args.mode == 'train':
            # Run model training
            logger.info("Running model training")
            training_pipeline = TrainingPipeline(config_dir)
            
            # Load data
            data_dir = os.path.join(os.path.dirname(__file__), 'output', 'data', date)
            
            if not os.path.exists(data_dir):
                logger.error(f"No data found for {date}")
                return 1
            
            # Load data for each sport
            data = {}
            for filename in os.listdir(data_dir):
                if filename.endswith('_data.json'):
                    sport = filename.split('_')[0]
                    if args.sport and sport != args.sport:
                        continue
                        
                    with open(os.path.join(data_dir, filename), 'r') as f:
                        import json
                        data[sport] = json.load(f)
            
            if not data:
                logger.error(f"No data loaded for training")
                return 1
            
            # Train models
            results = training_pipeline.train_all_sports(data)
            logger.info(f"Model training completed for {len(results)} sports")
            
        elif args.mode == 'predict':
            # Run prediction generation
            logger.info("Running prediction generation")
            prediction_pipeline = PredictionPipeline(config_dir)
            
            if args.sport:
                predictions = prediction_pipeline.generate_daily_predictions(date)
                predictions = {args.sport: predictions.get(args.sport, [])}
            else:
                predictions = prediction_pipeline.generate_daily_predictions(date)
            
            # Save predictions
            output_path = prediction_pipeline.save_predictions(predictions, date)
            logger.info(f"Predictions saved to {output_path}")
            
        elif args.mode == 'full':
            # Run full pipeline
            logger.info("Running full pipeline")
            automation_system = AutomationSystem(config_dir)
            success = automation_system.run_full_pipeline()
            
            if success:
                logger.info("Full pipeline completed successfully")
            else:
                logger.error("Full pipeline failed")
                return 1
            
        elif args.mode == 'daemon':
            # Run as daemon
            logger.info("Starting automation system in daemon mode")
            automation_system = AutomationSystem(config_dir)
            automation_system.start()
            
            try:
                # Keep running until interrupted
                import time
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                logger.info("Stopping automation system")
                automation_system.stop()
            
        elif args.mode == 'monitor':
            # Run monitoring
            logger.info("Running monitoring system")
            monitoring_system = MonitoringSystem(config_dir)
            
            # Generate performance report
            report = monitoring_system.generate_performance_report()
            
            # Visualize performance
            output_dir = args.output or os.path.join(os.path.dirname(__file__), 
                                                    'output', 'monitoring', 'visualizations')
            vis_dir = monitoring_system.visualize_performance(report, output_dir)
            
            logger.info(f"Performance visualizations saved to {vis_dir}")
        
        logger.info(f"Neural Network-Based Sports Predictor completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error in Neural Network-Based Sports Predictor: {str(e)}", exc_info=True)
        return 1

if __name__ == '__main__':
    sys.exit(main())
