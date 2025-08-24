"""
Basic Observability Module
Provides logging, metrics, and tracing for the AndroidWorld agent system
"""

import time
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ObservabilityManager:
    """Manages observability features: logging, metrics, and tracing"""
    
    def __init__(self, service_name: str = "androidworld-agent"):
        self.service_name = service_name
        self.traces = []
        self.metrics = {}
        self.start_time = time.time()
        
        # Create results directory for observability data
        Path("results").mkdir(exist_ok=True)
        
        logger.info(f"Observability manager initialized for {service_name}")
    
    def start_trace(self, operation: str, trace_id: Optional[str] = None) -> str:
        """Start a new trace for an operation"""
        if not trace_id:
            trace_id = f"{self.service_name}-{int(time.time() * 1000)}"
        
        trace = {
            "trace_id": trace_id,
            "operation": operation,
            "start_time": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "spans": []
        }
        
        self.traces.append(trace)
        logger.info(f"Started trace {trace_id} for operation: {operation}")
        
        return trace_id
    
    def add_span(self, trace_id: str, span_name: str, metadata: Dict[str, Any] = None):
        """Add a span to an existing trace"""
        trace = next((t for t in self.traces if t["trace_id"] == trace_id), None)
        if not trace:
            logger.warning(f"Trace {trace_id} not found")
            return
        
        span = {
            "span_id": f"{trace_id}-{len(trace['spans'])}",
            "name": span_name,
            "start_time": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        trace["spans"].append(span)
        logger.info(f"Added span {span_name} to trace {trace_id}")
    
    def end_trace(self, trace_id: str, success: bool = True, error: Optional[str] = None):
        """End a trace and record the result"""
        trace = next((t for t in self.traces if t["trace_id"] == trace_id), None)
        if not trace:
            logger.warning(f"Trace {trace_id} not found")
            return
        
        trace["end_time"] = datetime.utcnow().isoformat()
        trace["success"] = success
        trace["error"] = error
        trace["duration"] = (
            datetime.fromisoformat(trace["end_time"]) - 
            datetime.fromisoformat(trace["start_time"])
        ).total_seconds()
        
        logger.info(f"Ended trace {trace_id} - Success: {success}, Duration: {trace['duration']:.2f}s")
    
    def record_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Record a metric value"""
        metric_key = f"{name}_{json.dumps(labels or {}, sort_keys=True)}"
        
        if metric_key not in self.metrics:
            self.metrics[metric_key] = []
        
        metric_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "value": value,
            "labels": labels or {}
        }
        
        self.metrics[metric_key].append(metric_data)
        logger.info(f"Recorded metric {name}: {value}")
    
    def record_evaluation_metrics(self, results: Dict[str, Any]):
        """Record metrics from evaluation results"""
        evaluation = results.get("evaluation", {})
        summary = evaluation.get("summary", {})
        
        # Record success rate
        self.record_metric("success_rate", summary.get("success_rate", 0.0))
        
        # Record average duration
        self.record_metric("avg_duration", summary.get("average_duration", 0.0))
        
        # Record total episodes
        self.record_metric("total_episodes", summary.get("total_episodes", 0))
        
        # Record total time
        self.record_metric("total_time", summary.get("total_time", 0.0))
        
        logger.info("Recorded evaluation metrics")
    
    def save_traces(self, filename: str = "results/traces.json"):
        """Save traces to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.traces, f, indent=2, default=str)
            logger.info(f"Saved {len(self.traces)} traces to {filename}")
        except Exception as e:
            logger.error(f"Failed to save traces: {e}")
    
    def save_metrics(self, filename: str = "results/metrics.json"):
        """Save metrics to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.metrics, f, indent=2, default=str)
            logger.info(f"Saved metrics to {filename}")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def generate_observability_report(self) -> str:
        """Generate a human-readable observability report"""
        total_traces = len(self.traces)
        successful_traces = sum(1 for t in self.traces if t.get("success", False))
        total_metrics = sum(len(metric_list) for metric_list in self.metrics.values())
        
        report = f"""
# Observability Report

**Service**: {self.service_name}
**Generated**: {datetime.utcnow().isoformat()}
**Uptime**: {time.time() - self.start_time:.2f}s

## Traces
- **Total Traces**: {total_traces}
- **Successful**: {successful_traces}
- **Failed**: {total_traces - successful_traces}
        - **Success Rate**: {successful_traces/total_traces*100:.1f}% if total_traces > 0 else 0%

## Metrics
- **Total Metric Records**: {total_metrics}
- **Metric Types**: {len(self.metrics)}

## Recent Traces
"""
        
        # Add recent traces
        for trace in self.traces[-5:]:  # Last 5 traces
            status = "✅" if trace.get("success") else "❌"
            duration = trace.get("duration", 0)
            report += f"- {status} {trace['operation']} ({duration:.2f}s)\n"
        
        return report
    
    def save_observability_report(self, filename: str = "results/observability_report.md"):
        """Save observability report to file"""
        try:
            report = self.generate_observability_report()
            with open(filename, 'w') as f:
                f.write(report)
            logger.info(f"Saved observability report to {filename}")
        except Exception as e:
            logger.error(f"Failed to save observability report: {e}")

# Global observability manager instance
observability = ObservabilityManager()

# Convenience functions
def start_trace(operation: str, trace_id: Optional[str] = None) -> str:
    """Start a new trace"""
    return observability.start_trace(operation, trace_id)

def add_span(trace_id: str, span_name: str, metadata: Dict[str, Any] = None):
    """Add a span to a trace"""
    observability.add_span(trace_id, span_name, metadata)

def end_trace(trace_id: str, success: bool = True, error: Optional[str] = None):
    """End a trace"""
    observability.end_trace(trace_id, success, error)

def record_metric(name: str, value: float, labels: Dict[str, str] = None):
    """Record a metric"""
    observability.record_metric(name, value, labels)

def save_observability_data():
    """Save all observability data"""
    observability.save_traces()
    observability.save_metrics()
    observability.save_observability_report()
