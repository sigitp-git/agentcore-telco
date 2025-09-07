# Graph Multi-Agent Pattern[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#graph-multi-agent-pattern "Permanent link")

A Graph is a deterministic Directed Acyclic Graph (DAG) based agent orchestration system where agents, custom nodes, or other multi-agent systems (like [Swarm](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/swarm/) or nested Graphs) are nodes in a graph. Nodes are executed according to edge dependencies, with output from one node passed as input to connected nodes.

-   **Deterministic execution order** based on DAG structure
-   **Output propagation** along edges between nodes
-   **Clear dependency management** between agents
-   **Supports nested patterns** (Graph as a node in another Graph)
-   **Custom node types** for deterministic business logic and hybrid workflows
-   **Conditional edge traversal** for dynamic workflows
-   **Multi-modal input support** for handling text, images, and other content types

## How Graphs Work[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#how-graphs-work "Permanent link")

The Graph pattern operates on the principle of structured, deterministic workflows where:

1.  Nodes represent agents, custom nodes, or multi-agent systems
2.  Edges define dependencies and information flow between nodes
3.  Execution follows a topological sort of the graph
4.  Output from one node becomes input for dependent nodes
5.  Entry points receive the original task as input

## Graph Components[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#graph-components "Permanent link")

### 1\. GraphNode[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#1-graphnode "Permanent link")

A [
```
GraphNode
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.graph.GraphNode) represents a node in the graph with:

-   **node\_id**: Unique identifier for the node
-   **executor**: The Agent or MultiAgentBase instance to execute
-   **dependencies**: Set of nodes this node depends on
-   **execution\_status**: Current status (PENDING, EXECUTING, COMPLETED, FAILED)
-   **result**: The NodeResult after execution
-   **execution\_time**: Time taken to execute the node in milliseconds

### 2\. GraphEdge[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#2-graphedge "Permanent link")

A [
```
GraphEdge
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.graph.GraphEdge) represents a connection between nodes with:

-   **from\_node**: Source node
-   **to\_node**: Target node
-   **condition**: Optional function that determines if the edge should be traversed

### 3\. GraphBuilder[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#3-graphbuilder "Permanent link")

The [
```
GraphBuilder
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.graph.GraphBuilder) provides a simple interface for constructing graphs:

-   **add\_node()**: Add an agent or multi-agent system as a node
-   **add\_edge()**: Create a dependency between nodes
-   **set\_entry\_point()**: Define starting nodes for execution
-   **build()**: Validate and create the Graph instance

## Creating a Graph[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#creating-a-graph "Permanent link")

To create a [
```
Graph
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.graph.Graph), you use the [
```
GraphBuilder
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.graph.GraphBuilder) to define nodes, edges, and entry points:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-1)importlogging
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-2)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-3)fromstrands.multiagentimport GraphBuilder
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-4)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-5)# Enable debug logs and print them to stderr
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-6)logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-7)logging.basicConfig(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-8)    format="%(levelname)s | %(name)s | %(message)s",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-9)    handlers=[logging.StreamHandler()]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-10))
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-11)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-12)# Create specialized agents
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-13)researcher = Agent(name="researcher", system_prompt="You are a research specialist...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-14)analyst = Agent(name="analyst", system_prompt="You are a data analysis specialist...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-15)fact_checker = Agent(name="fact_checker", system_prompt="You are a fact checking specialist...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-16)report_writer = Agent(name="report_writer", system_prompt="You are a report writing specialist...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-17)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-18)# Build the graph
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-19)builder = GraphBuilder()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-20)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-21)# Add nodes
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-22)builder.add_node(researcher, "research")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-23)builder.add_node(analyst, "analysis")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-24)builder.add_node(fact_checker, "fact_check")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-25)builder.add_node(report_writer, "report")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-26)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-27)# Add edges (dependencies)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-28)builder.add_edge("research", "analysis")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-29)builder.add_edge("research", "fact_check")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-30)builder.add_edge("analysis", "report")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-31)builder.add_edge("fact_check", "report")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-32)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-33)# Set entry points (optional - will be auto-detected if not specified)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-34)builder.set_entry_point("research")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-35)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-36)# Build the graph
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-37)graph = builder.build()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-38)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-39)# Execute the graph on a task
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-40)result = graph("Research the impact of AI on healthcare and create a comprehensive report")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-41)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-42)# Access the results
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-43)print(f"\nStatus: {result.status}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-0-44)print(f"Execution order: {[node.node_idfornodeinresult.execution_order]}")

```

## Conditional Edges[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#conditional-edges "Permanent link")

You can add conditional logic to edges to create dynamic workflows:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-1)defonly_if_research_successful(state):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-2)"""Only traverse if research was successful."""
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-3)    research_node = state.results.get("research")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-4)    if not research_node:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-5)        return False
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-6)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-7)    # Check if research result contains success indicator
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-8)    result_text = str(research_node.result)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-9)    return "successful" in result_text.lower()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-10)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-11)# Add conditional edge
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-1-12)builder.add_edge("research", "analysis", condition=only_if_research_successful)

```

## Nested Multi-Agent Patterns[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#nested-multi-agent-patterns "Permanent link")

You can use a [
```
Graph
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.graph.Graph) or [
```
Swarm
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.swarm.Swarm) as a node within another Graph:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-2)fromstrands.multiagentimport GraphBuilder, Swarm
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-3)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-4)# Create a swarm of research agents
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-5)research_agents = [
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-6)    Agent(name="medical_researcher", system_prompt="You are a medical research specialist..."),
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-7)    Agent(name="technology_researcher", system_prompt="You are a technology research specialist..."),
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-8)    Agent(name="economic_researcher", system_prompt="You are an economic research specialist...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-9)]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-10)research_swarm = Swarm(research_agents)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-11)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-12)# Create a single agent node too
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-13)analyst = Agent(system_prompt="Analyze the provided research.")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-14)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-15)# Create a graph with the swarm as a node
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-16)builder = GraphBuilder()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-17)builder.add_node(research_swarm, "research_team")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-18)builder.add_node(analyst, "analysis")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-19)builder.add_edge("research_team", "analysis")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-20)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-21)graph = builder.build()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-22)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-23)result = graph("Research the impact of AI on healthcare and create a comprehensive report")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-24)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-25)# Access the results
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-2-26)print(f"\n{result}")

```

## Custom Node Types[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#custom-node-types "Permanent link")

You can create custom node types by extending [
```
MultiAgentBase
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.base.MultiAgentBase) to implement deterministic business logic, data processing pipelines, and hybrid workflows.

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-1)fromstrands.multiagent.baseimport MultiAgentBase, NodeResult, Status, MultiAgentResult
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-2)fromstrands.agent.agent_resultimport AgentResult
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-3)fromstrands.types.contentimport ContentBlock, Message
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-4)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-5)classFunctionNode(MultiAgentBase):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-6)"""Execute deterministic Python functions as graph nodes."""
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-7)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-8)    def__init__(self, func, name: str = None):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-9)        super().__init__()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-10)        self.func = func
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-11)        self.name = name or func.__name__
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-12)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-13)    async definvoke_async(self, task, **kwargs):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-14)        # Execute function and create AgentResult
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-15)        result = self.func(task if isinstance(task, str) else str(task))
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-16)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-17)        agent_result = AgentResult(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-18)            stop_reason="end_turn",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-19)            message=Message(role="assistant", content=[ContentBlock(text=str(result))]),
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-20)            # ... metrics and state
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-21)        )
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-22)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-23)        # Return wrapped in MultiAgentResult
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-24)        return MultiAgentResult(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-25)            status=Status.COMPLETED,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-26)            results={self.name: NodeResult(result=agent_result, ...)},
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-27)            # ... execution details
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-28)        )
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-29)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-30)# Usage example
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-31)defvalidate_data(data):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-32)    if not data.strip():
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-33)        raise ValueError("Empty input")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-34)    return f"✅ Validated: {data[:50]}..."
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-35)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-36)validator = FunctionNode(func=validate_data, name="validator")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-3-37)builder.add_node(validator, "validator")

```

Custom nodes enable:

-   **Deterministic processing**: Guaranteed execution for business logic
-   **Performance optimization**: Skip LLM calls for deterministic operations
-   **Hybrid workflows**: Combine AI creativity with deterministic control
-   **Business rules**: Implement complex business logic as graph nodes

## Multi-Modal Input Support[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#multi-modal-input-support "Permanent link")

Graphs support multi-modal inputs like text and images using [
```
ContentBlocks
```
](https://strandsagents.com/latest/documentation/docs/api-reference/types/#strands.types.content.ContentBlock):

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-2)fromstrands.multiagentimport GraphBuilder
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-3)fromstrands.types.contentimport ContentBlock
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-4)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-5)# Create agents for image processing workflow
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-6)image_analyzer = Agent(system_prompt="You are an image analysis expert...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-7)summarizer = Agent(system_prompt="You are a summarization expert...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-8)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-9)# Build the graph
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-10)builder = GraphBuilder()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-11)builder.add_node(image_analyzer, "image_analyzer")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-12)builder.add_node(summarizer, "summarizer")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-13)builder.add_edge("image_analyzer", "summarizer")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-14)builder.set_entry_point("image_analyzer")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-15)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-16)graph = builder.build()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-17)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-18)# Create content blocks with text and image
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-19)content_blocks = [
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-20)    ContentBlock(text="Analyze this image and describe what you see:"),
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-21)    ContentBlock(image={"format": "png", "source": {"bytes": image_bytes}}),
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-22)]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-23)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-24)# Execute the graph with multi-modal input
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-4-25)result = graph(content_blocks)

```

## Asynchronous Execution[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#asynchronous-execution "Permanent link")

You can also execute a Graph asynchronously by calling the [
```
invoke_async
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.graph.Graph.invoke_async) function:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-5-1)importasyncio
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-5-2)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-5-3)async defrun_graph():
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-5-4)    result = await graph.invoke_async("Research and analyze market trends...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-5-5)    return result
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-5-6)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-5-7)result = asyncio.run(run_graph())

```

## Graph Results[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#graph-results "Permanent link")

When a Graph completes execution, it returns a [
```
GraphResult
```
](https://strandsagents.com/latest/documentation/docs/api-reference/multiagent/#strands.multiagent.graph.GraphResult) object with detailed information:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-1)result = graph("Research and analyze...")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-2)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-3)# Check execution status
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-4)print(f"Status: {result.status}")  # COMPLETED, FAILED, etc.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-5)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-6)# See which nodes were executed and in what order
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-7)for node in result.execution_order:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-8)    print(f"Executed: {node.node_id}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-9)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-10)# Get results from specific nodes
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-11)analysis_result = result.results["analysis"].result
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-12)print(f"Analysis: {analysis_result}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-13)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-14)# Get performance metrics
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-15)print(f"Total nodes: {result.total_nodes}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-16)print(f"Completed nodes: {result.completed_nodes}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-17)print(f"Failed nodes: {result.failed_nodes}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-18)print(f"Execution time: {result.execution_time}ms")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-6-19)print(f"Token usage: {result.accumulated_usage}")

```

## Input Propagation[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#input-propagation "Permanent link")

The Graph automatically builds input for each node based on its dependencies:

1.  **Entry point nodes** receive the original task as input
2.  **Dependent nodes** receive a combined input that includes:
3.  The original task
4.  Results from all dependency nodes that have completed execution

This ensures each node has access to both the original context and the outputs from its dependencies.

The formatted input for dependent nodes looks like:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-7-1)Original Task: [The original task text]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-7-2)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-7-3)Inputs from previous nodes:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-7-4)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-7-5)From [node_id]:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-7-6)  - [Agent name]: [Result text]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-7-7)  - [Agent name]: [Another result text]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-7-8)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-7-9)From [another_node_id]:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-7-10)  - [Agent name]: [Result text]

```

## Graphs as a Tool[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#graphs-as-a-tool "Permanent link")

Agents can dynamically create and orchestrate graphs by using the 
```
graph
```
 tool available in the [Strands tools package](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/tools/community-tools-package/).

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-8-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-8-2)fromstrands_toolsimport graph
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-8-3)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-8-4)agent = Agent(tools=[graph], system_prompt="Create a graph of agents to solve the user's query.")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-8-5)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-8-6)agent("Design a TypeScript REST API and then write the code for it")

```

In this example:

1.  The agent uses the 
    ```
    graph
    ```
     tool to dynamically create nodes and edges in a graph. These nodes might be architect, coder, and reviewer agents with edges defined as architect -> coder -> reviewer
2.  Next the agent executes the graph
3.  The agent analyzes the graph results and then decides to either create another graph and execute it, or answer the user's query

## Common Graph Topologies[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#common-graph-topologies "Permanent link")

### 1\. Sequential Pipeline[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#1-sequential-pipeline "Permanent link")

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-9-1)builder = GraphBuilder()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-9-2)builder.add_node(researcher, "research")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-9-3)builder.add_node(analyst, "analysis")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-9-4)builder.add_node(reviewer, "review")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-9-5)builder.add_node(report_writer, "report")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-9-6)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-9-7)builder.add_edge("research", "analysis")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-9-8)builder.add_edge("analysis", "review")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-9-9)builder.add_edge("review", "report")

```

### 2\. Parallel Processing with Aggregation[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#2-parallel-processing-with-aggregation "Permanent link")

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-1)builder = GraphBuilder()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-2)builder.add_node(coordinator, "coordinator")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-3)builder.add_node(worker1, "worker1")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-4)builder.add_node(worker2, "worker2")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-5)builder.add_node(worker3, "worker3")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-6)builder.add_node(aggregator, "aggregator")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-7)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-8)builder.add_edge("coordinator", "worker1")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-9)builder.add_edge("coordinator", "worker2")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-10)builder.add_edge("coordinator", "worker3")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-11)builder.add_edge("worker1", "aggregator")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-12)builder.add_edge("worker2", "aggregator")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-10-13)builder.add_edge("worker3", "aggregator")

```

### 3\. Branching Logic[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#3-branching-logic "Permanent link")

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-1)defis_technical(state):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-2)    classifier_result = state.results.get("classifier")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-3)    if not classifier_result:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-4)        return False
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-5)    result_text = str(classifier_result.result)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-6)    return "technical" in result_text.lower()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-7)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-8)defis_business(state):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-9)    classifier_result = state.results.get("classifier")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-10)    if not classifier_result:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-11)        return False
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-12)    result_text = str(classifier_result.result)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-13)    return "business" in result_text.lower()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-14)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-15)builder = GraphBuilder()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-16)builder.add_node(classifier, "classifier")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-17)builder.add_node(tech_specialist, "tech_specialist")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-18)builder.add_node(business_specialist, "business_specialist")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-19)builder.add_node(tech_report, "tech_report")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-20)builder.add_node(business_report, "business_report")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-21)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-22)builder.add_edge("classifier", "tech_specialist", condition=is_technical)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-23)builder.add_edge("classifier", "business_specialist", condition=is_business)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-24)builder.add_edge("tech_specialist", "tech_report")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#__codelineno-11-25)builder.add_edge("business_specialist", "business_report")

```

## Best Practices[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/graph/#best-practices "Permanent link")

1.  **Design for acyclicity**: Ensure your graph has no cycles
2.  **Use meaningful node IDs**: Choose descriptive names for nodes
3.  **Validate graph structure**: The builder will check for cycles and validate entry points
4.  **Handle node failures**: Consider how failures in one node affect the overall workflow
5.  **Use conditional edges**: For dynamic workflows based on intermediate results
6.  **Consider parallelism**: Independent branches can execute concurrently
7.  **Nest multi-agent patterns**: Use Swarms within Graphs for complex workflows
8.  **Leverage multi-modal inputs**: Use ContentBlocks for rich inputs including images
9.  **Create custom nodes for deterministic logic**: Use 
    ```
    MultiAgentBase
    ```
     for business rules and data processing