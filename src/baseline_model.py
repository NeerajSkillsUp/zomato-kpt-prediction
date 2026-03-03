import numpy as np
import pandas as pd
from datetime import timedelta
from kitchen_simulator import KitchenSimulator

class BaselineModel:
    """Simulates current system with noisy FOR marking"""
    
    def __init__(self):
        self.historical_kpts = {}
    
    def predict_kpt(self, order, merchant):
        """Predict KPT using historical average (current approach)"""
        merchant_id = merchant['merchant_id']
        
        # Use historical average or default
        if merchant_id in self.historical_kpts:
            predicted = np.mean(self.historical_kpts[merchant_id])
        else:
            predicted = merchant['base_kpt_minutes']
        
        # Add some noise
        predicted *= np.random.uniform(0.9, 1.1)
        return predicted
    
    def simulate_order(self, order, merchant):
        """Simulate complete order lifecycle with current system"""
        
        # Predict KPT
        predicted_kpt = self.predict_kpt(order, merchant)
        
        # Assign rider based on prediction
        rider_arrival = order['timestamp'] + timedelta(minutes=predicted_kpt)
        
        # True food ready time
        true_ready = order['timestamp'] + timedelta(minutes=order['true_kpt'])
        
        # Simulate FOR marking (noisy)
        sim = KitchenSimulator(merchant)
        marked_kpt, marked_time = sim.simulate_current_for_marking(order, rider_arrival)
        
        # Calculate rider wait
        rider_wait = sim.calculate_rider_wait(true_ready, rider_arrival)
        
        # Calculate errors
        eta_error = abs(predicted_kpt - order['true_kpt'])
        
        # Update historical data with noisy label
        if merchant['merchant_id'] not in self.historical_kpts:
            self.historical_kpts[merchant['merchant_id']] = []
        self.historical_kpts[merchant['merchant_id']].append(marked_kpt)
        
        return {
            'predicted_kpt': predicted_kpt,
            'true_kpt': order['true_kpt'],
            'marked_kpt': marked_kpt,
            'rider_wait': rider_wait,
            'eta_error': eta_error,
            'is_delayed': rider_wait > 3
        }