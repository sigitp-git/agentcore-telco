# Swarm Multi-Agent Pattern[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#swarm-multi-agent-pattern "Permanent link")

A Swarm is a collaborative agent orchestration system where multiple agents work together as a team to solve complex tasks. Unlike traditional sequential or hierarchical multi-agent systems, a Swarm enables autonomous coordination between agents with shared context and working memory.

-   **Self-organizing agent teams** with shared working memory
-   **Tool-based coordination** between agents
-   **Autonomous agent collaboration** without central control
-   **Dynamic task distribution** based on agent capabilities
-   **Collective intelligence** through shared context
-   **Multi-modal input support** for handling text, images, and other content types

## How Swarms Work[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#how-swarms-work "Permanent link")

Swarms operate on the principle of emergent intelligence - the idea that a group of specialized agents working together can solve problems more effectively than a single agent. Each agent in a Swarm:

1.  Has access to the full task context
2.  Can see the history of which agents have worked on the task
3.  Can access shared knowledge contributed by other agents
4.  Can decide when to hand off to another agent with different expertise

## Creating a Swarm[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#creating-a-swarm "Permanent link")

To create a Swarm, you need to define a collection of agents with different specializations. The first agent in the list will receive the initial user request and act as the entry point for the swarm:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-1)importlogging
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-2)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-3)fromstrands.multiagentimport Swarm
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-4)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-5)# Enable debug logs and print them to stderr
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-6)logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-7)logging.basicConfig(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-8)    format="%(levelname)s | %(name)s | %(message)s",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-9)    handlers=[logging.StreamHandler()]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-10))
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-11)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-12)# Create specialized agents
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-13)researcher = Agent(name="researcher", system_prompt="You are a research specialist...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-14)coder = Agent(name="coder", system_prompt="You are a coding specialist...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-15)reviewer = Agent(name="reviewer", system_prompt="You are a code review specialist...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-16)architect = Agent(name="architect", system_prompt="You are a system architecture specialist...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-17)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-18)# Create a swarm with these agents
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-19)swarm = Swarm(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-20)    [researcher, coder, reviewer, architect],
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-21)    max_handoffs=20,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-22)    max_iterations=20,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-23)    execution_timeout=900.0,  # 15 minutes
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-24)    node_timeout=300.0,       # 5 minutes per agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-25)    repetitive_handoff_detection_window=8,  # There must be >= 3 unique agents in the last 8 handoffs
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-26)    repetitive_handoff_min_unique_agents=3
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-27))
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-28)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-29)# Execute the swarm on a task
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-30)result = swarm("Design and implement a simple REST API for a todo app")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-31)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-32)# Access the final result
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-33)print(f"Status: {result.status}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-0-34)print(f"Node history: {[node.node_idfornodeinresult.node_history]}")

```

In this example:

1.  The 
    ```
    researcher
    ```
     receives the initial request and might start by handing off to the 
    ```
    architect
    ```
    
2.  The 
    ```
    architect
    ```
     designs an API and system architecture
3.  Handoff to the 
    ```
    coder
    ```
     to implement the API and architecture
4.  The 
    ```
    coder
    ```
     writes the code
5.  Handoff to the 
    ```
    reviewer
    ```
     for code review
6.  Finally, the 
    ```
    reviewer
    ```
     provides the final result

## Swarm Configuration[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#swarm-configuration "Permanent link")

The [
```
Swarm
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.swarm.Swarm) constructor allows you to control the behavior and safety parameters:

 Parameter | Description | Default |
| --- | --- | --- |
 
```
max_handoffs
```
 | Maximum number of agent handoffs allowed | 20 |
 
```
max_iterations
```
 | Maximum total iterations across all agents | 20 |
 
```
execution_timeout
```
 | Total execution timeout in seconds | 900.0 (15 min) |
 
```
node_timeout
```
 | Individual agent timeout in seconds | 300.0 (5 min) |
 
```
repetitive_handoff_detection_window
```
 | Number of recent nodes to check for ping-pong behavior | 0 (disabled) |
 
```
repetitive_handoff_min_unique_agents
```
 | Minimum unique nodes required in recent sequence | 0 (disabled) |

## Multi-Modal Input Support[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#multi-modal-input-support "Permanent link")

Swarms support multi-modal inputs like text and images using [
```
ContentBlocks
```
](https://strandsagents.com/latest/documentation/docs/api-reference/types/#strands.types.content.ContentBlock):

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-2)fromstrands.multiagentimport Swarm
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-3)fromstrands.types.contentimport ContentBlock
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-4)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-5)# Create agents for image processing workflow
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-6)image_analyzer = Agent(name="image_analyzer", system_prompt="You are an image analysis expert...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-7)report_writer = Agent(name="report_writer", system_prompt="You are a report writing expert...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-8)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-9)# Create the swarm
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-10)swarm = Swarm([image_analyzer, report_writer])
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-11)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-12)# Create content blocks with text and image
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-13)content_blocks = [
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-14)    ContentBlock(text="Analyze this image and create a report about what you see:"),
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-15)    ContentBlock(image={"format": "png", "source": {"bytes": image_bytes}}),
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-16)]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-17)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-18)# Execute the swarm with multi-modal input
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-1-19)result = swarm(content_blocks)

```

## Swarm Coordination Tools[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#swarm-coordination-tools "Permanent link")

When you create a Swarm, each agent is automatically equipped with special tools for coordination:

### Handoff Tool[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#handoff-tool "Permanent link")

Agents can transfer control to another agent when they need specialized help:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-2-1)handoff_to_agent(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-2-2)    agent_name="coder",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-2-3)    message="I need help implementing this algorithm in Python",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-2-4)    context={"algorithm_details": "..."}
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-2-5))

```

## Shared Context[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#shared-context "Permanent link")

The Swarm maintains a shared context that all agents can access. This includes:

-   The original task description
-   History of which agents have worked on the task
-   Knowledge contributed by previous agents
-   List of available agents for collaboration

The formatted context for each agent looks like:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-1)Handoff Message: The user needs help with Python debugging - I've identified the issue but need someone with more expertise to fix it.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-2)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-3)User Request: My Python script is throwing a KeyError when processing JSON data from an API
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-4)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-5)Previous agents who worked on this: data_analyst → code_reviewer
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-6)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-7)Shared knowledge from previous agents:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-8)• data_analyst: {"issue_location": "line 42", "error_type": "missing key validation", "suggested_fix": "add key existence check"}
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-9)• code_reviewer: {"code_quality": "good overall structure", "security_notes": "API key should be in environment variable"}
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-10)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-11)Other agents available for collaboration:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-12)Agent name: data_analyst. Agent description: Analyzes data and provides deeper insights
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-13)Agent name: code_reviewer.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-14)Agent name: security_specialist. Agent description: Focuses on secure coding practices and vulnerability assessment
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-15)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-3-16)You have access to swarm coordination tools if you need help from other agents.

```

## Asynchronous Execution[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#asynchronous-execution "Permanent link")

You can also execute a Swarm asynchronously by calling the [
```
invoke_async
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.swarm.Swarm.invoke_async) function:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-4-1)importasyncio
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-4-2)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-4-3)async defrun_swarm():
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-4-4)    result = await swarm.invoke_async("Design and implement a complex system...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-4-5)    return result
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-4-6)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-4-7)result = asyncio.run(run_swarm())

```

## Swarm Results[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#swarm-results "Permanent link")

When a Swarm completes execution, it returns a [
```
SwarmResult
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.swarm.SwarmResult) object with detailed information:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-1)result = swarm("Design a system architecture for...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-2)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-3)# Access the final result
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-4)print(f"Status: {result.status}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-5)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-6)# Check execution status
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-7)print(f"Status: {result.status}")  # COMPLETED, FAILED, etc.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-8)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-9)# See which agents were involved
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-10)for node in result.node_history:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-11)    print(f"Agent: {node.node_id}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-12)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-13)# Get results from specific nodes
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-14)analyst_result = result.results["analyst"].result
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-15)print(f"Analysis: {analyst_result}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-16)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-17)# Get performance metrics
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-18)print(f"Total iterations: {result.execution_count}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-19)print(f"Execution time: {result.execution_time}ms")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-5-20)print(f"Token usage: {result.accumulated_usage}")

```

## Swarm as a Tool[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#swarm-as-a-tool "Permanent link")

Agents can dynamically create and orchestrate swarms by using the 
```
swarm
```
 tool available in the [Strands tools package](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/community-tools-package/).

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-6-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-6-2)fromstrands_toolsimport swarm
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-6-3)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-6-4)agent = Agent(tools=[swarm], system_prompt="Create a swarm of agents to solve the user's query.")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-6-5)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#__codelineno-6-6)agent("Research, analyze, and summarize the latest advancements in quantum computing")

```

In this example:

1.  The agent uses the 
    ```
    swarm
    ```
     tool to dynamically create a team of specialized agents. These might include a researcher, an analyst, and a technical writer
2.  Next the agent executes the swarm
3.  The swarm agents collaborate autonomously, handing off to each other as needed
4.  The agent analyzes the swarm results and provides a comprehensive response to the user

## Safety Mechanisms[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#safety-mechanisms "Permanent link")

Swarms include several safety mechanisms to prevent infinite loops and ensure reliable execution:

1.  **Maximum handoffs**: Limits how many times control can be transferred between agents
2.  **Maximum iterations**: Caps the total number of execution iterations
3.  **Execution timeout**: Sets a maximum total runtime for the Swarm
4.  **Node timeout**: Limits how long any single agent can run
5.  **Repetitive handoff detection**: Prevents agents from endlessly passing control back and forth

## Best Practices[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/#best-practices "Permanent link")

1.  **Create specialized agents**: Define clear roles for each agent in your Swarm
2.  **Use descriptive agent names**: Names should reflect the agent's specialty
3.  **Set appropriate timeouts**: Adjust based on task complexity and expected runtime
4.  **Enable repetitive handoff detection**: Set appropriate values for 
    ```
    repetitive_handoff_detection_window
    ```
     and 
    ```
    repetitive_handoff_min_unique_agents
    ```
     to prevent ping-pong behavior
5.  **Include diverse expertise**: Ensure your Swarm has agents with complementary skills
6.  **Provide agent descriptions**: Add descriptions to your agents to help other agents understand their capabilities
7.  **Leverage multi-modal inputs**: Use ContentBlocks for rich inputs including images