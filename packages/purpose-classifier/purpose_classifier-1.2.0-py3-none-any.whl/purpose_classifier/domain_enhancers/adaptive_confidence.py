"""
Adaptive Confidence Calibration for Purpose Code Classification.

This module provides adaptive confidence calibration to improve the accuracy
of purpose code classification by adjusting confidence scores based on
historical performance and context.
"""

import os
import json
import logging
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class AdaptiveConfidenceCalibrator:
    """
    Adaptive confidence calibrator for purpose code classification.

    This class provides adaptive confidence calibration to improve the accuracy
    of purpose code classification by adjusting confidence scores based on
    historical performance and context.
    """

    def __init__(self, calibration_file=None):
        """
        Initialize the adaptive confidence calibrator.

        Args:
            calibration_file: Optional path to calibration file
        """
        # Default calibration file path
        if calibration_file is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            calibration_file = os.path.join(base_dir, 'models', 'confidence_calibration.json')

        self.calibration_file = calibration_file

        # Initialize calibration data
        self.calibration_data = {
            'enhancer_scaling': {},
            'purpose_code_scaling': {},
            'confidence_bin_scaling': {},
            'global_scaling_factor': 1.0,
            'min_confidence': 0.0,
            'max_confidence': 0.99,
            'version': '1.0.0',
            'last_updated': None
        }

        # Initialize performance tracking
        self.performance_tracking = {
            'enhancer_accuracy': defaultdict(lambda: {'correct': 0, 'total': 0}),
            'purpose_code_accuracy': defaultdict(lambda: {'correct': 0, 'total': 0}),
            'confidence_bin_accuracy': defaultdict(lambda: {'correct': 0, 'total': 0}),
            'total_predictions': 0,
            'correct_predictions': 0
        }

        # Load calibration data if file exists
        self._load_calibration_data()

    def _load_calibration_data(self):
        """Load calibration data from file."""
        if os.path.exists(self.calibration_file):
            try:
                with open(self.calibration_file, 'r') as f:
                    self.calibration_data = json.load(f)
                logger.info(f"Loaded confidence calibration data from {self.calibration_file}")
            except Exception as e:
                logger.error(f"Error loading calibration data: {str(e)}")

    def save_calibration_data(self):
        """Save calibration data to file."""
        try:
            # Update timestamp
            from datetime import datetime
            self.calibration_data['last_updated'] = datetime.now().isoformat()

            # Save to file
            with open(self.calibration_file, 'w') as f:
                json.dump(self.calibration_data, f, indent=2)
            logger.info(f"Saved confidence calibration data to {self.calibration_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving calibration data: {str(e)}")
            return False

    def calibrate_confidence(self, result):
        """
        Calibrate confidence score based on calibration data.

        Args:
            result: Classification result

        Returns:
            dict: Calibrated classification result
        """
        # Make a copy of the result
        calibrated_result = result.copy()

        # Get original confidence
        original_confidence = result.get('confidence', 0.5)
        purpose_code = result.get('purpose_code', 'OTHR')
        enhancer = result.get('enhancer', 'unknown')

        # Determine confidence bin (rounded to nearest 0.1)
        confidence_bin = str(round(original_confidence * 10) / 10)

        # Apply scaling factors
        scaling_factors = []

        # Enhancer-specific scaling
        if enhancer in self.calibration_data['enhancer_scaling']:
            enhancer_scaling = self.calibration_data['enhancer_scaling'][enhancer]
            scaling_factors.append(enhancer_scaling)

        # Purpose code-specific scaling
        if purpose_code in self.calibration_data['purpose_code_scaling']:
            purpose_code_scaling = self.calibration_data['purpose_code_scaling'][purpose_code]
            scaling_factors.append(purpose_code_scaling)

        # Confidence bin scaling
        if confidence_bin in self.calibration_data['confidence_bin_scaling']:
            confidence_bin_scaling = self.calibration_data['confidence_bin_scaling'][confidence_bin]
            scaling_factors.append(confidence_bin_scaling)

        # Global scaling
        scaling_factors.append(self.calibration_data['global_scaling_factor'])

        # Calculate combined scaling factor (geometric mean)
        if scaling_factors:
            # Filter out zero and negative values to avoid log(0) and log(negative)
            positive_factors = [f for f in scaling_factors if f > 0]
            if positive_factors:
                combined_scaling = np.exp(np.mean(np.log(positive_factors)))
            else:
                combined_scaling = 1.0
        else:
            combined_scaling = 1.0

        # Apply scaling
        calibrated_confidence = original_confidence * combined_scaling

        # Ensure confidence is within bounds
        calibrated_confidence = max(
            self.calibration_data['min_confidence'],
            min(self.calibration_data['max_confidence'], calibrated_confidence)
        )

        # Update result
        calibrated_result['confidence'] = calibrated_confidence
        calibrated_result['original_confidence'] = original_confidence
        calibrated_result['confidence_calibrated'] = True
        calibrated_result['scaling_factor'] = combined_scaling

        return calibrated_result

    def update_performance(self, result, was_correct):
        """
        Update performance tracking with a prediction result.

        Args:
            result: Classification result
            was_correct: Whether the prediction was correct
        """
        # Update total predictions
        self.performance_tracking['total_predictions'] += 1
        if was_correct:
            self.performance_tracking['correct_predictions'] += 1

        # Get result details
        purpose_code = result.get('purpose_code', 'OTHR')
        enhancer = result.get('enhancer', 'unknown')
        confidence = result.get('confidence', 0.5)

        # Determine confidence bin (rounded to nearest 0.1)
        confidence_bin = str(round(confidence * 10) / 10)

        # Update enhancer accuracy
        self.performance_tracking['enhancer_accuracy'][enhancer]['total'] += 1
        if was_correct:
            self.performance_tracking['enhancer_accuracy'][enhancer]['correct'] += 1

        # Update purpose code accuracy
        self.performance_tracking['purpose_code_accuracy'][purpose_code]['total'] += 1
        if was_correct:
            self.performance_tracking['purpose_code_accuracy'][purpose_code]['correct'] += 1

        # Update confidence bin accuracy
        self.performance_tracking['confidence_bin_accuracy'][confidence_bin]['total'] += 1
        if was_correct:
            self.performance_tracking['confidence_bin_accuracy'][confidence_bin]['correct'] += 1

    def recalibrate(self, min_samples=100):
        """
        Recalibrate confidence scaling factors based on performance tracking.

        Args:
            min_samples: Minimum number of samples required for recalibration

        Returns:
            bool: True if recalibration was performed
        """
        # Check if we have enough samples
        if self.performance_tracking['total_predictions'] < min_samples:
            logger.info(f"Not enough samples for recalibration ({self.performance_tracking['total_predictions']} < {min_samples})")
            return False

        # Calculate global accuracy
        global_accuracy = (
            self.performance_tracking['correct_predictions'] /
            self.performance_tracking['total_predictions']
        ) if self.performance_tracking['total_predictions'] > 0 else 0.5

        # Recalibrate enhancer scaling
        for enhancer, data in self.performance_tracking['enhancer_accuracy'].items():
            if data['total'] >= min_samples / 10:  # Require at least 10% of min_samples
                accuracy = data['correct'] / data['total'] if data['total'] > 0 else 0.5
                # Calculate scaling factor (accuracy / average confidence)
                scaling_factor = accuracy / 0.5  # Assuming average confidence is 0.5
                self.calibration_data['enhancer_scaling'][enhancer] = scaling_factor

        # Recalibrate purpose code scaling
        for purpose_code, data in self.performance_tracking['purpose_code_accuracy'].items():
            if data['total'] >= min_samples / 20:  # Require at least 5% of min_samples
                accuracy = data['correct'] / data['total'] if data['total'] > 0 else 0.5
                # Calculate scaling factor (accuracy / average confidence)
                scaling_factor = accuracy / 0.5  # Assuming average confidence is 0.5
                self.calibration_data['purpose_code_scaling'][purpose_code] = scaling_factor

        # Recalibrate confidence bin scaling
        for confidence_bin, data in self.performance_tracking['confidence_bin_accuracy'].items():
            if data['total'] >= min_samples / 10:  # Require at least 10% of min_samples
                accuracy = data['correct'] / data['total'] if data['total'] > 0 else 0.5
                # Calculate scaling factor (accuracy / confidence bin)
                bin_value = float(confidence_bin)
                scaling_factor = accuracy / bin_value if bin_value > 0 else 1.0
                self.calibration_data['confidence_bin_scaling'][confidence_bin] = scaling_factor

        # Update global scaling factor
        self.calibration_data['global_scaling_factor'] = global_accuracy / 0.5

        # Save calibration data
        self.save_calibration_data()

        # Reset performance tracking
        self._reset_performance_tracking()

        return True

    def _reset_performance_tracking(self):
        """Reset performance tracking."""
        self.performance_tracking = {
            'enhancer_accuracy': defaultdict(lambda: {'correct': 0, 'total': 0}),
            'purpose_code_accuracy': defaultdict(lambda: {'correct': 0, 'total': 0}),
            'confidence_bin_accuracy': defaultdict(lambda: {'correct': 0, 'total': 0}),
            'total_predictions': 0,
            'correct_predictions': 0
        }

    def get_calibration_stats(self):
        """
        Get calibration statistics.

        Returns:
            dict: Calibration statistics
        """
        return {
            'enhancer_scaling': self.calibration_data['enhancer_scaling'],
            'purpose_code_scaling': self.calibration_data['purpose_code_scaling'],
            'confidence_bin_scaling': self.calibration_data['confidence_bin_scaling'],
            'global_scaling_factor': self.calibration_data['global_scaling_factor'],
            'total_predictions': self.performance_tracking['total_predictions'],
            'correct_predictions': self.performance_tracking['correct_predictions'],
            'accuracy': (
                self.performance_tracking['correct_predictions'] /
                self.performance_tracking['total_predictions']
            ) if self.performance_tracking['total_predictions'] > 0 else 0.0
        }
