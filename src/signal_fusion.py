import numpy as np
import pandas as pd

class SignalFusion:
    """Multi-signal fusion for rush detection"""
    
    def __init__(self):
        self.weights = {
            'zomato_density': 0.40,
            'rider_wait_history': 0.25,
            'external_proxy': 0.15,
            'tablet_behavior': 0.10,
            'time_context': 0.10
        }
    
    def calculate_zomato_density(self, concurrent_orders, capacity):
        """Signal A: Current order load"""
        density = concurrent_orders / capacity
        return min(1.0, density / 2)  # Normalize to 0-1
    
    def calculate_rider_wait_history(self, merchant_id, historical_waits):
        """Signal B: Historical rider wait patterns"""
        if merchant_id not in historical_waits:
            return 0.5  # Neutral
        
        avg_wait = np.mean(historical_waits[merchant_id])
        # Higher wait = higher rush
        return min(1.0, avg_wait / 10)  # Normalize
    
    def calculate_external_proxy(self, hour, neighborhood_rush_pattern):
        """Signal C: External platform indicators"""
        # Simulate external rush based on time patterns
        if hour in neighborhood_rush_pattern:
            return np.random.uniform(0.6, 0.9)
        return np.random.uniform(0.1, 0.4)
    
    def calculate_tablet_behavior(self, session_duration, acceptance_rate):
        """Signal D: Merchant app behavior"""
        # Longer session + high acceptance = busy
        session_score = min(1.0, session_duration / 60)  # Normalize to hour
        behavior_score = (session_score * 0.6 + acceptance_rate * 0.4)
        return behavior_score
    
    def calculate_time_context(self, hour, day_of_week):
        """Signal E: Temporal patterns"""
        # Rush hours and weekends
        is_lunch = 12 <= hour <= 14
        is_dinner = 19 <= hour <= 22
        is_weekend = day_of_week >= 5
        
        score = 0.0
        if is_lunch or is_dinner:
            score += 0.6
        if is_weekend:
            score += 0.3
        
        return min(1.0, score)
    
    def fuse_signals(self, signals):
        """Combine all signals with weights"""
        rush_score = (
            signals['zomato_density'] * self.weights['zomato_density'] +
            signals['rider_wait_history'] * self.weights['rider_wait_history'] +
            signals['external_proxy'] * self.weights['external_proxy'] +
            signals['tablet_behavior'] * self.weights['tablet_behavior'] +
            signals['time_context'] * self.weights['time_context']
        )
        return rush_score
    
    def predict_kpt_with_rush(self, base_kpt, rush_score):
        """Apply rush multiplier to base KPT"""
        final_kpt = base_kpt * (1 + rush_score)
        return final_kpt