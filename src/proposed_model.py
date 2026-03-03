import numpy as np
import pandas as pd
from datetime import timedelta
from signal_fusion import SignalFusion

class ProposedModel:
    """Simulates our proposed multi-signal system"""
    
    def __init__(self):
        self.fusion = SignalFusion()
        self.historical_waits = {}
        self.neighborhood_rush = [12, 13, 19, 20, 21]
    
    def predict_kpt(self, order, merchant):
        """Predict KPT using multi-signal fusion"""
        
        # Collect all signals
        signals = {
            'zomato_density': self.fusion.calculate_zomato_density(
                order['concurrent_orders'], 
                merchant['concurrent_capacity']
            ),
            'rider_wait_history': self.fusion.calculate_rider_wait_history(
                merchant['merchant_id'],
                self.historical_waits
            ),
            'external_proxy': self.fusion.calculate_external_proxy(
                order['hour'],
                self.neighborhood_rush
            ),
            'tablet_behavior': self.fusion.calculate_tablet_behavior(
                session_duration=np.random.uniform(20, 80),
                acceptance_rate=np.random.uniform(0.7, 0.95)
            ),
            'time_context': self.fusion.calculate_time_context(
                order['hour'],
                order['timestamp'].weekday()
            )
        }
        
        # Fuse signals
        rush_score = self.fusion.fuse_signals(signals)
        
        # Predict KPT with rush adjustment
        base_kpt = merchant['base_kpt_minutes']
        predicted_kpt = self.fusion.predict_kpt_with_rush(base_kpt, rush_score)
        
        return predicted_kpt
    
    def simulate_order(self, order, merchant):
        """Simulate complete order lifecycle with proposed system"""
        
        # Predict KPT using multi-signal fusion
        predicted_kpt = self.predict_kpt(order, merchant)
        
        # Assign rider based on improved prediction
        rider_arrival = order['timestamp'] + timedelta(minutes=predicted_kpt)
        
        # True food ready time
        true_ready = order['timestamp'] + timedelta(minutes=order['true_kpt'])
        
        # Calculate rider wait (should be much less)
        wait_seconds = (true_ready - rider_arrival).total_seconds()
        rider_wait = max(0, wait_seconds / 60)
        
        # Update historical wait times (ground truth)
        if merchant['merchant_id'] not in self.historical_waits:
            self.historical_waits[merchant['merchant_id']] = []
        self.historical_waits[merchant['merchant_id']].append(rider_wait)
        
        # Calculate errors
        eta_error = abs(predicted_kpt - order['true_kpt'])
        
        return {
            'predicted_kpt': predicted_kpt,
            'true_kpt': order['true_kpt'],
            'rider_wait': rider_wait,
            'eta_error': eta_error,
            'is_delayed': rider_wait > 3
        }