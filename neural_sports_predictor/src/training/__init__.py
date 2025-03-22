"""
Module for initializing the training package.
"""

from .training_pipeline import TrainingPipeline
from .prediction_pipeline import PredictionPipeline

__all__ = [
    'TrainingPipeline',
    'PredictionPipeline'
]
