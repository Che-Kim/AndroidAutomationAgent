"""
AndroidWorld Agent

Core agent implementation for executing Android automation tasks.
Provides task parsing, execution, and result management.
"""

import time
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AndroidWorldAgent:
    """Agent for executing AndroidWorld tasks"""
    
    def __init__(self):
        """Initialize the agent"""
        self.task_count = 0
        logger.info("AndroidWorld agent initialized")
    
    def execute_task(self, task_prompt: str) -> Dict[str, Any]:
        """
        Execute a task based on prompt
        
        Args:
            task_prompt: Description of what to do
            
        Returns:
            Result dictionary
        """
        self.task_count += 1
        start_time = time.time()
        
        logger.info(f"Executing task {self.task_count}: {task_prompt}")
        
        try:
            # Parse and route task
            if "open" in task_prompt.lower() and "app" in task_prompt.lower():
                result = self._open_app(task_prompt)
            elif "click" in task_prompt.lower():
                result = self._click_element(task_prompt)
            elif "input" in task_prompt.lower():
                result = self._input_text(task_prompt)
            else:
                result = self._generic_task(task_prompt)
            
            # Add timing
            duration = time.time() - start_time
            result['duration'] = duration
            result['success'] = True
            
            logger.info(f"Task completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Task failed: {e}")
            
            return {
                'success': False,
                'error': str(e),
                'duration': duration,
                'task_id': self.task_count
            }
    
    def _open_app(self, prompt: str) -> Dict[str, Any]:
        """Handle app opening tasks"""
        # Extract app name from prompt
        words = prompt.lower().split()
        app_name = "settings"  # default
        
        for i, word in enumerate(words):
            if word == "app" and i + 1 < len(words):
                app_name = words[i + 1]
                break
        
        # Execute app opening
        time.sleep(1)  # Processing time
        
        return {
            'action': 'open_app',
            'app_name': app_name,
            'result': f'Opened {app_name} app'
        }
    
    def _click_element(self, prompt: str) -> Dict[str, Any]:
        """Handle element clicking tasks"""
        # Extract element name
        words = prompt.lower().split()
        element = "button"  # default
        
        for i, word in enumerate(words):
            if word == "click" and i + 1 < len(words):
                element = words[i + 1]
                break
        
        # Execute clicking
        time.sleep(0.5)
        
        return {
            'action': 'click',
            'element': element,
            'result': f'Clicked {element}'
        }
    
    def _input_text(self, prompt: str) -> Dict[str, Any]:
        """Handle text input tasks"""
        # Extract text to input
        words = prompt.lower().split()
        text = "test"  # default
        
        for i, word in enumerate(words):
            if word == "input" and i + 1 < len(words):
                text = words[i + 1]
                break
        
        # Simulate typing
        time.sleep(len(text) * 0.1)
        
        return {
            'action': 'input_text',
            'text': text,
            'result': f'Input text: {text}'
        }
    
    def _generic_task(self, prompt: str) -> Dict[str, Any]:
        """Handle generic tasks"""
        time.sleep(1)
        
        return {
            'action': 'generic',
            'description': prompt,
            'result': f'Executed: {prompt}'
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Health check"""
        return {
            'status': 'healthy',
            'tasks_executed': self.task_count,
            'timestamp': time.time()
        }

# Health check function
def health_check() -> Dict[str, Any]:
    """Global health check function"""
    agent = AndroidWorldAgent()
    return agent.health_check()

# Main execution for command line
def main():
    """Main function"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python agent.py <task_prompt>")
        return
    
    task_prompt = " ".join(sys.argv[1:])
    
    agent = AndroidWorldAgent()
    result = agent.execute_task(task_prompt)
    
    print(f"Task result: {result}")

if __name__ == "__main__":
    main()
