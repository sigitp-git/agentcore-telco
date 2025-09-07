# Agent Workflows: Building Multi-Agent Systems with Strands Agents SDK[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#agent-workflows-building-multi-agent-systems-with-strands-agents-sdk "Permanent link")

## Understanding Workflows[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#understanding-workflows "Permanent link")

### What is an Agent Workflow?[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#what-is-an-agent-workflow "Permanent link")

An agent workflow is a structured coordination of tasks across multiple AI agents, where each agent performs specialized functions in a defined sequence or pattern. By breaking down complex problems into manageable components and distributing them to specialized agents, workflows provide explicit control over task execution order, dependencies, and information flow, ensuring reliable outcomes for processes that require specific execution patterns.

### Components of a Workflow Architecture[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#components-of-a-workflow-architecture "Permanent link")

A workflow architecture consists of three key components:

#### 1\. Task Definition and Distribution[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#1-task-definition-and-distribution "Permanent link")

-   **Task Specification**: Clear description of what each agent needs to accomplish
-   **Agent Assignment**: Matching tasks to agents with appropriate capabilities
-   **Priority Levels**: Determining which tasks should execute first when possible

#### 2\. Dependency Management[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#2-dependency-management "Permanent link")

-   **Sequential Dependencies**: Tasks that must execute in a specific order
-   **Parallel Execution**: Independent tasks that can run simultaneously
-   **Join Points**: Where multiple parallel paths converge before continuing

#### 3\. Information Flow[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#3-information-flow "Permanent link")

-   **Input/Output Mapping**: Connecting one agent's output to another's input
-   **Context Preservation**: Maintaining relevant information throughout the workflow
-   **State Management**: Tracking the overall workflow progress

### When to Use a Workflow[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#when-to-use-a-workflow "Permanent link")

Workflows excel in scenarios requiring structured execution and clear dependencies:

-   **Complex Multi-Step Processes**: Tasks with distinct sequential stages
-   **Specialized Agent Expertise**: Processes requiring different capabilities at each stage
-   **Dependency-Heavy Tasks**: When certain tasks must wait for others to complete
-   **Resource Optimization**: Running independent tasks in parallel while managing dependencies
-   **Error Recovery**: Retrying specific failed steps without restarting the entire process
-   **Long-Running Processes**: Tasks requiring monitoring, pausing, or resuming capabilities
-   **Audit Requirements**: When detailed tracking of each step is necessary

Consider other approaches (swarms, agent graphs) for simple tasks, highly collaborative problems, or situations requiring extensive agent-to-agent communication.

## Implementing Workflow Architectures[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#implementing-workflow-architectures "Permanent link")

### Creating Workflows with Strands Agents[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#creating-workflows-with-strands-agents "Permanent link")

Strands Agents SDK allows you to create workflows using existing Agent objects, even when they use different model providers or have different configurations.

#### Sequential Workflow Architecture[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#sequential-workflow-architecture "Permanent link")

In a sequential workflow, agents process tasks in a defined order, with each agent's output becoming the input for the next:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-2)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-3)# Create specialized agents
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-4)researcher = Agent(system_prompt="You are a research specialist. Find key information.", callback_handler=None)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-5)analyst = Agent(system_prompt="You analyze research data and extract insights.", callback_handler=None)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-6)writer = Agent(system_prompt="You create polished reports based on analysis.")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-7)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-8)# Sequential workflow processing
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-9)defprocess_workflow(topic):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-10)    # Step 1: Research
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-11)    research_results = researcher(f"Research the latest developments in {topic}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-12)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-13)    # Step 2: Analysis
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-14)    analysis = analyst(f"Analyze these research findings: {research_results}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-15)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-16)    # Step 3: Report writing
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-17)    final_report = writer(f"Create a report based on this analysis: {analysis}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-18)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-0-19)    return final_report

```

This sequential workflow creates a pipeline where each agent's output becomes the input for the next agent, allowing for specialized processing at each stage. For a functional example of sequential workflow implementation, see the [agents\_workflows.md](https://github.com/strands-agents/docs/blob/main/docs/examples/python/agents_workflows.md) example in the Strands Agents SDK documentation.

## Quick Start with the Workflow Tool[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#quick-start-with-the-workflow-tool "Permanent link")

The Strands Agents SDK provides a built-in workflow tool that simplifies multi-agent workflow implementation by handling task creation, dependency resolution, parallel execution, and information flow automatically.

### Using the Workflow Tool[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#using-the-workflow-tool "Permanent link")

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-2)fromstrands_toolsimport workflow
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-3)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-4)# Create an agent with workflow capability
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-5)agent = Agent(tools=[workflow])
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-6)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-7)# Create a multi-agent workflow
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-8)agent.tool.workflow(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-9)    action="create",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-10)    workflow_id="data_analysis",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-11)    tasks=[
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-12)        {
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-13)            "task_id": "data_extraction",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-14)            "description": "Extract key financial data from the quarterly report",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-15)            "system_prompt": "You extract and structure financial data from reports.",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-16)            "priority": 5
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-17)        },
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-18)        {
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-19)            "task_id": "trend_analysis",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-20)            "description": "Analyze trends in the data compared to previous quarters",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-21)            "dependencies": ["data_extraction"],
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-22)            "system_prompt": "You identify trends in financial time series.",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-23)            "priority": 3
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-24)        },
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-25)        {
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-26)            "task_id": "report_generation",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-27)            "description": "Generate a comprehensive analysis report",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-28)            "dependencies": ["trend_analysis"],
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-29)            "system_prompt": "You create clear financial analysis reports.",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-30)            "priority": 2
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-31)        }
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-32)    ]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-33))
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-34)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-35)# Execute workflow (parallel processing where possible)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-36)agent.tool.workflow(action="start", workflow_id="data_analysis")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-37)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-38)# Check results
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-1-39)status = agent.tool.workflow(action="status", workflow_id="data_analysis")

```

The full implementation of the workflow tool can be found in the [Strands Tools repository](https://github.com/strands-agents/tools/blob/main/src/strands_tools/workflow.py).

### Key Parameters and Features[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#key-parameters-and-features "Permanent link")

**Basic Parameters:**

-   **action**: Operation to perform (create, start, status, list, delete)
-   **workflow\_id**: Unique identifier for the workflow
-   **tasks**: List of tasks with properties like task\_id, description, system\_prompt, dependencies, and priority

**Advanced Features:**

1.  **Persistent State Management**
    
      3.   Pause and resume workflows
      4.   Recover from failures automatically
      5.   Inspect intermediate results
          
          ```
          [](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-2-1)# Pause and resume example
          [](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-2-2)agent.tool.workflow(action="pause", workflow_id="data_analysis")
          [](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-2-3)agent.tool.workflow(action="resume", workflow_id="data_analysis")
          
          ```
    
2.  **Dynamic Resource Management**
    
      16.   Scales thread allocation based on available resources
      17.   Implements rate limiting with exponential backoff
      18.   Prioritizes tasks based on importance
    
3.  **Error Handling and Monitoring**
    
      22.   Automatic retries for failed tasks
      23.   Detailed status reporting with progress percentage
      24.   Task-level metrics (status, execution time, dependencies)
          
          ```
          [](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-3-1)# Get detailed status
          [](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-3-2)status = agent.tool.workflow(action="status", workflow_id="data_analysis")
          [](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-3-3)print(status["content"])
          
          ```

### Enhancing Workflow Architectures[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#enhancing-workflow-architectures "Permanent link")

While the sequential workflow example above demonstrates the basic concept, you may want to extend it to handle more complex scenarios. To build more robust and flexible workflow architectures based on this foundation, you can begin with two key components:

#### 1\. Task Management and Dependency Resolution[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#1-task-management-and-dependency-resolution "Permanent link")

Task management provides a structured way to define, track, and execute tasks based on their dependencies:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-1)# Task management example
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-2)tasks = {
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-3)    "data_extraction": {
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-4)        "description": "Extract key financial data from the quarterly report",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-5)        "status": "pending",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-6)        "agent": financial_agent,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-7)        "dependencies": []
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-8)    },
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-9)    "trend_analysis": {
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-10)        "description": "Analyze trends in the extracted data",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-11)        "status": "pending",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-12)        "agent": analyst_agent,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-13)        "dependencies": ["data_extraction"]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-14)    }
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-15)}
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-16)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-17)defget_ready_tasks(tasks, completed_tasks):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-18)"""Find tasks that are ready to execute (dependencies satisfied)"""
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-19)    ready_tasks = []
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-20)    for task_id, task in tasks.items():
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-21)        if task["status"] == "pending":
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-22)            deps = task.get("dependencies", [])
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-23)            if all(dep in completed_tasks for dep in deps):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-24)                ready_tasks.append(task_id)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-4-25)    return ready_tasks

```

**Benefits of Task Management:**

-   **Centralized Task Tracking**: Maintains a single source of truth for all tasks
-   **Dynamic Execution Order**: Determines the optimal execution sequence based on dependencies
-   **Status Monitoring**: Tracks which tasks are pending, running, or completed
-   **Parallel Optimization**: Identifies which tasks can safely run simultaneously

#### 2\. Context Passing Between Tasks[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#2-context-passing-between-tasks "Permanent link")

Context passing ensures that information flows smoothly between tasks, allowing each agent to build upon previous work:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-1)defbuild_task_context(task_id, tasks, results):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-2)"""Build context from dependent tasks"""
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-3)    context = []
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-4)    for dep_id in tasks[task_id].get("dependencies", []):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-5)        if dep_id in results:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-6)            context.append(f"Results from {dep_id}: {results[dep_id]}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-7)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-8)    prompt = tasks[task_id]["description"]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-9)    if context:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-10)        prompt = "Previous task results:\n" + "\n\n".join(context) + "\n\nTask:\n" + prompt
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-11)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#__codelineno-5-12)    return prompt

```

**Benefits of Context Passing:**

-   **Knowledge Continuity**: Ensures insights from earlier tasks inform later ones
-   **Reduced Redundancy**: Prevents agents from repeating work already done
-   **Coherent Outputs**: Creates a consistent narrative across multiple agents
-   **Contextual Awareness**: Gives each agent the background needed for its specific task

## Conclusion[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/workflow/#conclusion "Permanent link")

Multi-agent workflows provide a structured approach to complex tasks by coordinating specialized agents in defined sequences with clear dependencies. The Strands Agents SDK supports both custom workflow implementations and a built-in workflow tool with advanced features for state management, resource optimization, and monitoring. By choosing the right workflow architecture for your needs, you can create efficient, reliable, and maintainable multi-agent systems that handle complex processes with clarity and control.