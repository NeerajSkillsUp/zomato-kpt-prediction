import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

class KitchenSimulator:
    def __init__(self, merchant_profile):
        self.merchant = merchant_profile
        self.base_kpt = merchant_profile['base_kpt_minutes']
        self.capacity = merchant_profile['concurrent_capacity']
        self.for_accuracy = merchant_profile['for_accuracy']
        
    def generate_order(self, order_id, timestamp):
        """Generate a single order with realistic parameters"""
        hour = timestamp.hour
        
        # Rush hour multiplier
        is_rush = hour in self.merchant['rush_hours']
        rush_multiplier = np.random.uniform(1.3, 1.8) if is_rush else 1.0
        
        # True KPT with variation
        true_kpt = self.base_kpt * rush_multiplier * np.random.uniform(0.8, 1.2)
        
        # Current order queue load
        concurrent_orders = np.random.randint(1, self.capacity + 3) if is_rush else np.random.randint(1, self.capacity)
        
        # Queue delay
        queue_delay = max(0, (concurrent_orders - self.capacity) * 5)
        true_kpt += queue_delay
        
        return {
            'order_id': order_id,
            'merchant_id': self.merchant['merchant_id'],
            'timestamp': timestamp,
            'hour': hour,
            'is_rush': is_rush,
            'true_kpt': true_kpt,
            'concurrent_orders': concurrent_orders,
            'rush_multiplier': rush_multiplier
        }
    
    def simulate_current_for_marking(self, order, rider_arrival_time):
        """Simulate current (noisy) FOR marking behavior"""
        true_ready_time = order['timestamp'] + timedelta(minutes=order['true_kpt'])
        
        # Merchant FOR accuracy determines if they mark accurately
        if np.random.random() < self.for_accuracy:
            # Accurate marking (within 2 minutes)
            marked_time = true_ready_time + timedelta(minutes=np.random.uniform(-2, 2))
        else:
            # Rider-influenced marking (when rider arrives)
            marked_time = rider_arrival_time + timedelta(minutes=np.random.uniform(-1, 1))
        
        # Calculate marked KPT
        marked_kpt = (marked_time - order['timestamp']).total_seconds() / 60
        
        return marked_kpt, marked_time
    
    def calculate_rider_wait(self, true_ready_time, rider_arrival_time):
        """Calculate how long rider waits"""
        wait_seconds = (true_ready_time - rider_arrival_time).total_seconds()
        return max(0, wait_seconds / 60)  # Convert to minutes

def generate_dataset(num_orders=10000):
    """Generate complete synthetic dataset"""
    
    # Load merchant profiles
    with open('data/merchant_profiles.json', 'r') as f:
        merchants = json.load(f)
    
    all_orders = []
    
    # Distribution: 30% cloud, 50% mid, 20% small
    merchant_distribution = [0.3, 0.5, 0.2]
    
    start_date = datetime(2026, 1, 1, 8, 0)
    
    for i in range(num_orders):
        # Select merchant type
        merchant_type_idx = np.random.choice(len(merchants), p=merchant_distribution)
        merchant = merchants[merchant_type_idx]
        
        # Random timestamp over 30 days
        random_minutes = np.random.randint(0, 30 * 24 * 60)
        timestamp = start_date + timedelta(minutes=random_minutes)
        
        # Create simulator for this merchant
        sim = KitchenSimulator(merchant)
        
        # Generate order
        order = sim.generate_order(f"ORD_{i:05d}", timestamp)
        all_orders.append(order)
    
    df = pd.DataFrame(all_orders)
    df.to_csv('data/synthetic_orders.csv', index=False)
    print(f"Generated {num_orders} orders")
    return df

if __name__ == "__main__":
    df = generate_dataset(10000)
    print(df.head())
    print(f"\nDataset shape: {df.shape}")
    print(f"Rush orders: {df['is_rush'].sum()} ({df['is_rush'].mean()*100:.1f}%)")
    print(f"Avg true KPT: {df['true_kpt'].mean():.2f} minutes")