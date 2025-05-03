"""
Workflow system for defining complex agent execution patterns.
"""
from typing import List, Dict, Any, Optional, Callable, Union
from .agent import Agent

class Task:
    """A unit of work to be performed by an agent."""
    
    def __init__(
        self,
        name: str,
        agent: Agent,
        instruction: str
    ):
        """
        Initialize a task.
        
        Args:
            name: Task name
            agent: The agent to perform the task
            instruction: The task instruction template
        """
        self.name = name
        self.agent = agent
        self.instruction = instruction
    
    def execute(self, context: Dict[str, Any]) -> str:
        """
        Execute the task with the given context.
        
        Args:
            context: Variables to format the instruction
            
        Returns:
            The task result
        """
        # Format instruction with context variables
        formatted_instruction = self.instruction.format(**context)
        # Run the agent
        return self.agent.run(formatted_instruction)

class Condition:
    """A decision point in a workflow."""
    
    def __init__(
        self,
        name: str,
        condition: Callable[[str], bool],
        success: Union['Task', 'Condition'],
        failure: Union['Task', 'Condition']
    ):
        """
        Initialize a condition.
        
        Args:
            name: Condition name
            condition: Function that evaluates the previous result
            success: Next step if condition is true
            failure: Next step if condition is false
        """
        self.name = name
        self.condition = condition
        self.success = success
        self.failure = failure
    
    def evaluate(self, result: str) -> Union['Task', 'Condition']:
        """
        Evaluate the condition and return the next step.
        
        Args:
            result: The result from the previous step
            
        Returns:
            The next task or condition
        """
        if self.condition(result):
            return self.success
        return self.failure

class Workflow:
    """
    Defines a sequence of tasks and conditions for complex workflows.
    """
    
    def __init__(
        self,
        name: str,
        tasks: List[Union[Task, Condition]]
    ):
        """
        Initialize a workflow.
        
        Args:
            name: Workflow name
            tasks: List of tasks and conditions in execution order
        """
        self.name = name
        self.tasks = tasks
    
    def run(self, **initial_context) -> str:
        """
        Run the workflow with initial context variables.
        
        Args:
            **initial_context: Initial variables for the workflow
            
        Returns:
            The final workflow result
        """
        context = initial_context.copy()
        current_step = self.tasks[0]  # Start with the first task
        step_index = 0
        results = {}
        
        # Maximum steps to prevent infinite loops
        max_steps = 20
        step_count = 0
        
        while step_count < max_steps:
            step_count += 1
            
            if isinstance(current_step, Task):
                # Execute the task
                task_name = current_step.name
                print(f"Executing task: {task_name}")
                
                result = current_step.execute(context)
                results[task_name] = result
                
                # Store result in context with the task name
                context[task_name.lower() + "_results"] = result
                
                # Also store some common variable names for convenience
                if task_name.lower() == "research":
                    context["research_results"] = result
                elif task_name.lower() == "writing":
                    context["draft"] = result
                
                # Move to the next step if there is one
                step_index += 1
                if step_index < len(self.tasks):
                    current_step = self.tasks[step_index]
                else:
                    # End of workflow
                    break
                    
            elif isinstance(current_step, Condition):
                # Evaluate the condition on the previous result
                last_result = list(results.values())[-1] if results else ""
                next_step = current_step.evaluate(last_result)
                
                # Find the index of the next step
                for i, step in enumerate(self.tasks):
                    if step == next_step:
                        step_index = i
                        current_step = step
                        break
                else:
                    # If next_step not found in tasks, move to the next step
                    step_index += 1
                    if step_index < len(self.tasks):
                        current_step = self.tasks[step_index]
                    else:
                        # End of workflow
                        break
        
        # Return the result of the last executed task
        if results:
            return list(results.values())[-1]
        return f"Workflow {self.name} completed with no results"