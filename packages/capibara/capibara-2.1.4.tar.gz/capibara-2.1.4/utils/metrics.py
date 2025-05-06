# metrics.py
class TrainingMetrics:
    def __init__(self):
        self.metrics = {
            "loss": [],
            "perplexity": [],
            "accuracy": [],
            "tpu_utilization": [],
            "memory_usage": []
        }
    
    def update(self, batch_metrics):
        for key, value in batch_metrics.items():
            self.metrics[key].append(value)
    
    def get_summary(self):
        return {
            key: {
                "mean": np.mean(values),
                "std": np.std(values),
                "min": np.min(values),
                "max": np.max(values)
            }
            for key, values in self.metrics.items()
        }