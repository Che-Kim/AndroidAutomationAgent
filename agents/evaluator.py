"""
AndroidWorld Evaluator

Multi-episode evaluation system for testing Android automation tasks.
Provides comprehensive metrics collection and result analysis.
"""

import time
import json
import random
from typing import Dict, Any, List
from pathlib import Path

from .agent import AndroidWorldAgent
from .observability import start_trace, add_span, end_trace, record_metric, save_observability_data

class AndroidWorldEvaluator:
    """Evaluator for running multiple test episodes"""
    
    def __init__(self):
        """Initialize the evaluator"""
        self.agent = AndroidWorldAgent()
        self.results = []
    
    def evaluate(self, task_prompt: str, episodes: int = 5) -> Dict[str, Any]:
        """
        Run evaluation with multiple episodes
        
        Args:
            task_prompt: Task to evaluate
            episodes: Number of episodes to run
            
        Returns:
            Evaluation results
        """
        # Start observability trace
        trace_id = start_trace(f"evaluation_{task_prompt}_{episodes}")
        add_span(trace_id, "evaluation_start", {"task": task_prompt, "episodes": episodes})
        
        print(f"🧪 Starting evaluation: {episodes} episodes")
        print(f"📝 Task: {task_prompt}")
        
        start_time = time.time()
        
        # Run episodes
        for i in range(episodes):
            print(f"  Episode {i+1}/{episodes}...")
            
            episode_trace = start_trace(f"episode_{i+1}")
            add_span(episode_trace, "episode_start", {"episode": i+1})
            
            result = self.agent.execute_task(task_prompt)
            result['episode_id'] = i + 1
            result['task_prompt'] = task_prompt
            
            self.results.append(result)
            
            # Record episode metrics
            record_metric("episode_duration", result.get('duration', 0), {"episode": i+1})
            record_metric("episode_success", 1 if result.get('success') else 0, {"episode": i+1})
            
            end_trace(episode_trace, result.get('success', False))
            
            # Small delay between episodes
            time.sleep(0.5)
        
        # Calculate summary
        total_time = time.time() - start_time
        summary = self._calculate_summary(total_time)
        
        # Record evaluation metrics
        record_metric("total_evaluation_time", total_time)
        record_metric("success_rate", summary['success_rate'])
        record_metric("avg_duration", summary['average_duration'])
        
        # Prepare final results
        evaluation_results = {
            'evaluation': {
                'task_prompt': task_prompt,
                'episodes': episodes,
                'episode_results': self.results,
                'summary': summary
            }
        }
        
        print(f"✅ Evaluation completed in {total_time:.2f}s")
        print(f"📊 Success rate: {summary['success_rate']:.1%}")
        
        # End main trace
        end_trace(trace_id, True)
        
        return evaluation_results
    
    def _calculate_summary(self, total_time: float) -> Dict[str, Any]:
        """Calculate summary metrics"""
        if not self.results:
            return {
                'total_episodes': 0,
                'successful_episodes': 0,
                'success_rate': 0.0,
                'average_duration': 0.0,
                'total_time': total_time
            }
        
        # Count successes
        successful = sum(1 for r in self.results if r.get('success', False))
        total = len(self.results)
        
        # Calculate average duration
        durations = [r.get('duration', 0) for r in self.results]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            'total_episodes': total,
            'successful_episodes': successful,
            'failed_episodes': total - successful,
            'success_rate': successful / total if total > 0 else 0.0,
            'average_duration': avg_duration,
            'total_time': total_time
        }
    
    def save_results(self, results: Dict[str, Any], filename: str = "results/results.json"):
        """Save results to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"💾 Results saved to {filename}")
            
            # Also generate report.md
            report = self.generate_report(results)
            report_filename = filename.replace('.json', '_report.md')
            with open(report_filename, 'w') as f:
                f.write(report)
            print(f"📄 Report saved to {report_filename}")
            
            # Generate main report.md (as expected by reviewers)
            main_report_path = "results/report.md"
            with open(main_report_path, 'w') as f:
                f.write(report)
            print(f"📄 Main report saved to {main_report_path}")
            
            # Save observability data
            save_observability_data()
            print("📊 Observability data saved")
            
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate text report"""
        evaluation = results.get('evaluation', {})
        summary = evaluation.get('summary', {})
        
        report = f"""
# AndroidWorld Agent Evaluation Report

**Task**: {evaluation.get('task_prompt', 'N/A')}
**Episodes**: {summary.get('total_episodes', 0)}
**Success Rate**: {summary.get('success_rate', 0):.1%}
**Average Duration**: {summary.get('average_duration', 0):.2f}s
**Total Time**: {summary.get('total_time', 0):.2f}s

## Episode Results
"""
        
        for result in evaluation.get('episode_results', []):
            status = "✅" if result.get('success') else "❌"
            duration = result.get('duration', 0)
            report += f"- Episode {result.get('episode_id')}: {status} {duration:.2f}s\n"
        
        report += "\n## Summary\n"
        report += f"- **Successful**: {summary.get('successful_episodes', 0)}\n"
        report += f"- **Failed**: {summary.get('failed_episodes', 0)}\n"
        report += f"- **Success Rate**: {summary.get('success_rate', 0):.1%}\n"
        
        return report

# Evaluation function
def evaluate_task(task_prompt: str, episodes: int = 5) -> Dict[str, Any]:
    """Global evaluation function"""
    evaluator = AndroidWorldEvaluator()
    return evaluator.evaluate(task_prompt, episodes)

# Main execution for command line
def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python evaluator.py <task_prompt> [episodes]")
        return
    
    task_prompt = sys.argv[1]
    episodes = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    evaluator = AndroidWorldEvaluator()
    results = evaluator.evaluate(task_prompt, episodes)
    
    # Save results
    evaluator.save_results(results, "results/results.json")
    
    # Generate and display report
    print("Evaluation completed successfully")
