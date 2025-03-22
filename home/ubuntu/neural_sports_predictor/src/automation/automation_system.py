"""
Automation module for the neural network-based sports predictor.
This module handles scheduling and orchestration of the daily pipeline.
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
import schedule
import threading
from typing import Dict, List, Tuple, Any, Optional, Union

from ..data_collection import DataCollectionManager
from ..training import TrainingPipeline, PredictionPipeline

class AutomationSystem:
    """
    Automation system for the sports prediction pipeline.
    Handles scheduling and orchestration of data collection, model training, and prediction generation.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the automation system.
        
        Args:
            config_path: Path to the configuration directory
        """
        self.config_dir = config_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                                     'config')
        
        # Load automation configuration
        automation_config_path = os.path.join(self.config_dir, 'pipeline', 'automation.json')
        if os.path.exists(automation_config_path):
            with open(automation_config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "data_collection_time": "01:00",
                "training_time": "02:00",
                "prediction_time": "08:00",
                "monitoring_interval_hours": 6,
                "logging": {
                    "level": "INFO",
                    "file_path": "logs/automation.log"
                }
            }
            
        # Setup logging
        self._setup_logging()
        
        # Initialize components
        self.data_manager = DataCollectionManager(self.config_dir)
        self.training_pipeline = TrainingPipeline(self.config_dir)
        self.prediction_pipeline = PredictionPipeline(self.config_dir)
        
        # Initialize scheduler
        self.scheduler = schedule
        self.running = False
        self.scheduler_thread = None
        
        self.logger.info("Automation system initialized")
    
    def _setup_logging(self):
        """Set up logging configuration"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_config = self.config.get('logging', {})
        log_level = getattr(logging, log_config.get('level', 'INFO'))
        log_file = log_config.get('file_path', os.path.join(log_dir, 'automation.log'))
        
        # Create logger
        self.logger = logging.getLogger('automation_system')
        self.logger.setLevel(log_level)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        
        # Create formatter and add to handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
    
    def run_data_collection(self):
        """Run the daily data collection process"""
        self.logger.info("Starting daily data collection")
        
        try:
            # Run data collection for all sports
            data = self.data_manager.run_daily_collection()
            
            # Save data to output directory
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     'output', 'data', datetime.now().strftime('%Y-%m-%d'))
            os.makedirs(output_dir, exist_ok=True)
            
            for sport, sport_data in data.items():
                sport_output_path = os.path.join(output_dir, f"{sport}_data.json")
                with open(sport_output_path, 'w') as f:
                    json.dump(sport_data, f, indent=2)
            
            self.logger.info("Daily data collection completed successfully")
            return data
        except Exception as e:
            self.logger.error(f"Error in daily data collection: {str(e)}")
            return None
    
    def run_model_training(self):
        """Run the daily model training process"""
        self.logger.info("Starting daily model training")
        
        try:
            # Load latest data
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   'output', 'data')
            
            # Get most recent data directory
            data_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
            if not data_dirs:
                self.logger.error("No data directories found")
                return None
            
            latest_data_dir = max(data_dirs)
            latest_data_path = os.path.join(data_dir, latest_data_dir)
            
            # Load data for each sport
            data = {}
            for filename in os.listdir(latest_data_path):
                if filename.endswith('_data.json'):
                    sport = filename.split('_')[0]
                    with open(os.path.join(latest_data_path, filename), 'r') as f:
                        data[sport] = json.load(f)
            
            # Train models for all sports
            results = self.training_pipeline.train_all_sports(data)
            
            # Save training results
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                     'output', 'training', datetime.now().strftime('%Y-%m-%d'))
            os.makedirs(output_dir, exist_ok=True)
            
            results_path = os.path.join(output_dir, 'training_results.json')
            with open(results_path, 'w') as f:
                # Convert non-serializable objects to strings
                serializable_results = {}
                for sport, sport_results in results.items():
                    serializable_results[sport] = {
                        'sport': sport,
                        'model_path': sport_results.get('model_path', ''),
                        'evaluation': sport_results.get('evaluation', {})
                    }
                
                json.dump(serializable_results, f, indent=2)
            
            self.logger.info("Daily model training completed successfully")
            return results
        except Exception as e:
            self.logger.error(f"Error in daily model training: {str(e)}")
            return None
    
    def run_prediction_generation(self):
        """Run the daily prediction generation process"""
        self.logger.info("Starting daily prediction generation")
        
        try:
            # Generate predictions for today
            date = datetime.now().strftime('%Y-%m-%d')
            predictions = self.prediction_pipeline.generate_daily_predictions(date)
            
            # Save predictions
            output_path = self.prediction_pipeline.save_predictions(predictions, date)
            
            self.logger.info(f"Daily prediction generation completed successfully, saved to {output_path}")
            return predictions
        except Exception as e:
            self.logger.error(f"Error in daily prediction generation: {str(e)}")
            return None
    
    def run_monitoring(self):
        """Run the monitoring process to check system health and performance"""
        self.logger.info("Running monitoring checks")
        
        try:
            # Check data collection status
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                   'output', 'data')
            data_dirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
            
            if data_dirs:
                latest_data_dir = max(data_dirs)
                latest_data_date = datetime.strptime(latest_data_dir, '%Y-%m-%d')
                days_since_data = (datetime.now() - latest_data_date).days
                
                if days_since_data > 1:
                    self.logger.warning(f"Data collection may be failing. Last data from {days_since_data} days ago")
            
            # Check model training status
            training_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                       'output', 'training')
            training_dirs = [d for d in os.listdir(training_dir) if os.path.isdir(os.path.join(training_dir, d))]
            
            if training_dirs:
                latest_training_dir = max(training_dirs)
                latest_training_date = datetime.strptime(latest_training_dir, '%Y-%m-%d')
                days_since_training = (datetime.now() - latest_training_date).days
                
                if days_since_training > 1:
                    self.logger.warning(f"Model training may be failing. Last training from {days_since_training} days ago")
            
            # Check prediction generation status
            prediction_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                         'output', 'predictions')
            prediction_files = [f for f in os.listdir(prediction_dir) if f.startswith('predictions_')]
            
            if prediction_files:
                latest_prediction_file = max(prediction_files)
                latest_prediction_date = datetime.strptime(latest_prediction_file.split('_')[1].split('.')[0], '%Y-%m-%d')
                days_since_prediction = (datetime.now() - latest_prediction_date).days
                
                if days_since_prediction > 1:
                    self.logger.warning(f"Prediction generation may be failing. Last predictions from {days_since_prediction} days ago")
            
            # Check model performance (if we have recent predictions and outcomes)
            # This would require comparing predictions to actual outcomes
            # Placeholder for future implementation
            
            self.logger.info("Monitoring checks completed")
        except Exception as e:
            self.logger.error(f"Error in monitoring: {str(e)}")
    
    def setup_schedule(self):
        """Set up the daily schedule for all processes"""
        self.logger.info("Setting up daily schedule")
        
        # Get schedule times from config
        data_collection_time = self.config.get('data_collection_time', '01:00')
        training_time = self.config.get('training_time', '02:00')
        prediction_time = self.config.get('prediction_time', '08:00')
        monitoring_interval = self.config.get('monitoring_interval_hours', 6)
        
        # Schedule data collection
        self.scheduler.every().day.at(data_collection_time).do(self.run_data_collection)
        self.logger.info(f"Scheduled daily data collection at {data_collection_time}")
        
        # Schedule model training
        self.scheduler.every().day.at(training_time).do(self.run_model_training)
        self.logger.info(f"Scheduled daily model training at {training_time}")
        
        # Schedule prediction generation
        self.scheduler.every().day.at(prediction_time).do(self.run_prediction_generation)
        self.logger.info(f"Scheduled daily prediction generation at {prediction_time}")
        
        # Schedule monitoring
        self.scheduler.every(monitoring_interval).hours.do(self.run_monitoring)
        self.logger.info(f"Scheduled monitoring every {monitoring_interval} hours")
    
    def _run_scheduler(self):
        """Run the scheduler in a loop"""
        self.logger.info("Starting scheduler loop")
        
        while self.running:
            self.scheduler.run_pending()
            time.sleep(60)  # Check every minute
    
    def start(self):
        """Start the automation system"""
        if self.running:
            self.logger.warning("Automation system is already running")
            return
        
        self.logger.info("Starting automation system")
        
        # Set up schedule
        self.setup_schedule()
        
        # Start scheduler in a separate thread
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        self.logger.info("Automation system started")
    
    def stop(self):
        """Stop the automation system"""
        if not self.running:
            self.logger.warning("Automation system is not running")
            return
        
        self.logger.info("Stopping automation system")
        
        # Stop scheduler
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        # Clear all scheduled jobs
        self.scheduler.clear()
        
        self.logger.info("Automation system stopped")
    
    def run_full_pipeline(self):
        """Run the full pipeline once (data collection, training, prediction)"""
        self.logger.info("Running full pipeline")
        
        # Run data collection
        data = self.run_data_collection()
        if not data:
            self.logger.error("Data collection failed, aborting pipeline")
            return False
        
        # Run model training
        results = self.run_model_training()
        if not results:
            self.logger.error("Model training failed, aborting pipeline")
            return False
        
        # Run prediction generation
        predictions = self.run_prediction_generation()
        if not predictions:
            self.logger.error("Prediction generation failed, aborting pipeline")
            return False
        
        self.logger.info("Full pipeline completed successfully")
        return True
