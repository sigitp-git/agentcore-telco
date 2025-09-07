# Agents as Tools with Strands Agents SDK[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#agents-as-tools-with-strands-agents-sdk "Permanent link")

## The Concept: Agents as Tools[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#the-concept-agents-as-tools "Permanent link")

"Agents as Tools" is an architectural pattern in AI systems where specialized AI agents are wrapped as callable functions (tools) that can be used by other agents. This creates a hierarchical structure where:

1.  **A primary "orchestrator" agent** handles user interaction and determines which specialized agent to call
2.  **Specialized "tool agents"** perform domain-specific tasks when called by the orchestrator

This approach mimics human team dynamics, where a manager coordinates specialists, each bringing unique expertise to solve complex problems. Rather than a single agent trying to handle everything, tasks are delegated to the most appropriate specialized agent.

## Key Benefits and Core Principles[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#key-benefits-and-core-principles "Permanent link")

The "Agents as Tools" pattern offers several advantages:

-   **Separation of concerns**: Each agent has a focused area of responsibility, making the system easier to understand and maintain
-   **Hierarchical delegation**: The orchestrator decides which specialist to invoke, creating a clear chain of command
-   **Modular architecture**: Specialists can be added, removed, or modified independently without affecting the entire system
-   **Improved performance**: Each agent can have tailored system prompts and tools optimized for its specific task

## Strands Agents SDK Best Practices for Agent Tools[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#strands-agents-sdk-best-practices-for-agent-tools "Permanent link")

When implementing the "Agents as Tools" pattern with Strands Agents SDK:

1.  **Clear tool documentation**: Write descriptive docstrings that explain the agent's expertise
2.  **Focused system prompts**: Keep each specialized agent tightly focused on its domain
3.  **Proper response handling**: Use consistent patterns to extract and format responses
4.  **Tool selection guidance**: Give the orchestrator clear criteria for when to use each specialized agent

## Implementing Agents as Tools with Strands Agents SDK[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#implementing-agents-as-tools-with-strands-agents-sdk "Permanent link")

Strands Agents SDK provides a powerful framework for implementing the "Agents as Tools" pattern through its 
```
@tool
```
 decorator. This allows you to transform specialized agents into callable functions that can be used by an orchestrator agent.

### Creating Specialized Tool Agents[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#creating-specialized-tool-agents "Permanent link")

First, define specialized agents as tool functions using Strands Agents SDK's 
```
@tool
```
 decorator:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-1)fromstrandsimport Agent, tool
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-2)fromstrands_toolsimport retrieve, http_request
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-3)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-4)# Define a specialized system prompt
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-5)RESEARCH_ASSISTANT_PROMPT = """
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-6)You are a specialized research assistant. Focus only on providing
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-7)factual, well-sourced information in response to research questions.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-8)Always cite your sources when possible.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-9)"""
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-10)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-11)@tool
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-12)defresearch_assistant(query: str) -> str:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-13)"""
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-14)    Process and respond to research-related queries.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-15)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-16)    Args:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-17)        query: A research question requiring factual information
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-18)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-19)    Returns:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-20)        A detailed research answer with citations
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-21)    """
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-22)    try:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-23)        # Strands Agents SDK makes it easy to create a specialized agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-24)        research_agent = Agent(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-25)            system_prompt=RESEARCH_ASSISTANT_PROMPT,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-26)            tools=[retrieve, http_request]  # Research-specific tools
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-27)        )
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-28)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-29)        # Call the agent and return its response
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-30)        response = research_agent(query)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-31)        return str(response)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-32)    except Exception as e:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-0-33)        return f"Error in research assistant: {str(e)}"

```

You can create multiple specialized agents following the same pattern:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-1)@tool
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-2)defproduct_recommendation_assistant(query: str) -> str:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-3)"""
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-4)    Handle product recommendation queries by suggesting appropriate products.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-5)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-6)    Args:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-7)        query: A product inquiry with user preferences
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-8)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-9)    Returns:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-10)        Personalized product recommendations with reasoning
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-11)    """
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-12)    try:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-13)        product_agent = Agent(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-14)            system_prompt="""You are a specialized product recommendation assistant.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-15)            Provide personalized product suggestions based on user preferences.""",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-16)            tools=[retrieve, http_request, dialog],  # Tools for getting product data
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-17)        )
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-18)        # Implementation with response handling
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-19)        # ...
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-20)        return processed_response
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-21)    except Exception as e:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-22)        return f"Error in product recommendation: {str(e)}"
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-23)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-24)@tool
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-25)deftrip_planning_assistant(query: str) -> str:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-26)"""
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-27)    Create travel itineraries and provide travel advice.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-28)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-29)    Args:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-30)        query: A travel planning request with destination and preferences
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-31)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-32)    Returns:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-33)        A detailed travel itinerary or travel advice
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-34)    """
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-35)    try:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-36)        travel_agent = Agent(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-37)            system_prompt="""You are a specialized travel planning assistant.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-38)            Create detailed travel itineraries based on user preferences.""",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-39)            tools=[retrieve, http_request],  # Travel information tools
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-40)        )
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-41)        # Implementation with response handling
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-42)        # ...
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-43)        return processed_response
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-44)    except Exception as e:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-1-45)        return f"Error in trip planning: {str(e)}"

```

### Creating the Orchestrator Agent[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#creating-the-orchestrator-agent "Permanent link")

Next, create an orchestrator agent that has access to all specialized agents as tools:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-2)from.specialized_agentsimport research_assistant, product_recommendation_assistant, trip_planning_assistant
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-3)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-4)# Define the orchestrator system prompt with clear tool selection guidance
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-5)MAIN_SYSTEM_PROMPT = """
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-6)You are an assistant that routes queries to specialized agents:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-7)- For research questions and factual information → Use the research_assistant tool
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-8)- For product recommendations and shopping advice → Use the product_recommendation_assistant tool
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-9)- For travel planning and itineraries → Use the trip_planning_assistant tool
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-10)- For simple questions not requiring specialized knowledge → Answer directly
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-11)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-12)Always select the most appropriate tool based on the user's query.
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-13)"""
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-14)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-15)# Strands Agents SDK allows easy integration of agent tools
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-16)orchestrator = Agent(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-17)    system_prompt=MAIN_SYSTEM_PROMPT,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-18)    callback_handler=None,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-19)    tools=[research_assistant, product_recommendation_assistant, trip_planning_assistant]
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-2-20))

```

### Real-World Example Scenario[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#real-world-example-scenario "Permanent link")

Here's how this multi-agent system might handle a complex user query:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-1)# Example: E-commerce Customer Service System
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-2)customer_query = "I'm looking for hiking boots for a trip to Patagonia next month"
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-3)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-4)# The orchestrator automatically determines that this requires multiple specialized agents
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-5)response = orchestrator(customer_query)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-6)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-7)# Behind the scenes, the orchestrator will:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-8)# 1. First call the trip_planning_assistant to understand travel requirements for Patagonia
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-9)#    - Weather conditions in the region next month
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-10)#    - Typical terrain and hiking conditions
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-11)# 2. Then call product_recommendation_assistant with this context to suggest appropriate boots
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-12)#    - Waterproof options for potential rain
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-13)#    - Proper ankle support for uneven terrain
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-14)#    - Brands known for durability in harsh conditions
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-15)# 3. Combine these specialized responses into a cohesive answer that addresses both the
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#__codelineno-3-16)#    travel planning and product recommendation aspects of the query

```

This example demonstrates how Strands Agents SDK enables specialized experts to collaborate on complex queries requiring multiple domains of knowledge. The orchestrator intelligently routes different aspects of the query to the appropriate specialized agents, then synthesizes their responses into a comprehensive answer. By following the best practices outlined earlier and leveraging Strands Agents SDK's capabilities, you can build sophisticated multi-agent systems that handle complex tasks through specialized expertise and coordinated collaboration.

## Complete Working Example[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agents-as-tools/#complete-working-example "Permanent link")

For a fully implemented example of the "Agents as Tools" pattern, check out the ["Teacher's Assistant"](https://github.com/strands-agents/docs/blob/main/docs/examples/python/multi_agent_example/multi_agent_example.md) example in our repository. This example demonstrates a practical implementation of the concepts discussed in this document, showing how multiple specialized agents can work together to provide comprehensive assistance in an educational context.