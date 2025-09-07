# Agent-to-Agent (A2A) Protocol[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#agent-to-agent-a2a-protocol "Permanent link")

Strands Agents supports the [Agent-to-Agent (A2A) protocol](https://a2aproject.github.io/A2A/latest/), enabling seamless communication between AI agents across different platforms and implementations.

## What is Agent-to-Agent (A2A)?[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#what-is-agent-to-agent-a2a "Permanent link")

The Agent-to-Agent protocol is an open standard that defines how AI agents can discover, communicate, and collaborate with each other.

### Use Cases[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#use-cases "Permanent link")

A2A protocol support enables several powerful use cases:

-   **Multi-Agent Workflows**: Chain multiple specialized agents together
-   **Agent Marketplaces**: Discover and use agents from different providers
-   **Cross-Platform Integration**: Connect Strands agents with other A2A-compatible systems
-   **Distributed AI Systems**: Build scalable, distributed agent architectures

Learn more about the A2A protocol:

-   [A2A GitHub Organization](https://github.com/a2aproject/A2A)
-   [A2A Python SDK](https://github.com/a2aproject/a2a-python)
-   [A2A Documentation](https://a2aproject.github.io/A2A/latest/)

Complete Examples Available

Check out the [Native A2A Support samples](https://github.com/strands-agents/samples/tree/main/03-integrations/Native-A2A-Support) for complete, ready-to-run client, server and tool implementations.

## Installation[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#installation "Permanent link")

To use A2A functionality with Strands, install the package with the A2A extra:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-0-1)pipinstall'strands-agents[a2a]'

```

This installs the core Strands SDK along with the necessary A2A protocol dependencies.

## Creating an A2A Server[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#creating-an-a2a-server "Permanent link")

### Basic Server Setup[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#basic-server-setup "Permanent link")

Create a Strands agent and expose it as an A2A server:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-1)importlogging
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-2)fromstrands_tools.calculatorimport calculator
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-3)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-4)fromstrands.multiagent.a2aimport A2AServer
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-5)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-6)logging.basicConfig(level=logging.INFO)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-7)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-8)# Create a Strands agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-9)strands_agent = Agent(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-10)    name="Calculator Agent",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-11)    description="A calculator agent that can perform basic arithmetic operations.",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-12)    tools=[calculator],
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-13)    callback_handler=None
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-14))
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-15)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-16)# Create A2A server (streaming enabled by default)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-17)a2a_server = A2AServer(agent=strands_agent)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-18)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-19)# Start the server
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-1-20)a2a_server.serve()

```

> NOTE: the server supports both 
> ```
> SendMessageRequest
> ```
>  and 
> ```
> SendStreamingMessageRequest
> ```
>  client requests!

### Server Configuration Options[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#server-configuration-options "Permanent link")

The 
```
A2AServer
```
 constructor accepts several configuration options:

-   ```
    agent
    ```
    : The Strands Agent to wrap with A2A compatibility
-   ```
    host
    ```
    : Hostname or IP address to bind to (default: "127.0.0.1")
-   ```
    port
    ```
    : Port to bind to (default: 9000)
-   ```
    version
    ```
    : Version of the agent (default: "0.0.1")
-   ```
    skills
    ```
    : Custom list of agent skills (default: auto-generated from tools)
-   ```
    http_url
    ```
    : Public HTTP URL where this agent will be accessible (optional, enables path-based mounting)
-   ```
    serve_at_root
    ```
    : Forces server to serve at root path regardless of http\_url path (default: False)
-   ```
    task_store
    ```
    : Custom task storage implementation (defaults to InMemoryTaskStore)
-   ```
    queue_manager
    ```
    : Custom message queue management (optional)
-   ```
    push_config_store
    ```
    : Custom push notification configuration storage (optional)
-   ```
    push_sender
    ```
    : Custom push notification sender implementation (optional)

### Advanced Server Customization[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#advanced-server-customization "Permanent link")

The 
```
A2AServer
```
 provides access to the underlying FastAPI or Starlette application objects allowing you to further customize server behavior.

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-2)fromstrands.multiagent.a2aimport A2AServer
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-3)importuvicorn
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-4)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-5)# Create your agent and A2A server
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-6)agent = Agent(name="My Agent", description="A customizable agent", callback_handler=None)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-7)a2a_server = A2AServer(agent=agent)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-8)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-9)# Access the underlying FastAPI app
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-10)fastapi_app = a2a_server.to_fastapi_app()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-11)# Add custom middleware, routes, or configuration
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-12)fastapi_app.add_middleware(...)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-13)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-14)# Or access the Starlette app
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-15)starlette_app = a2a_server.to_starlette_app()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-16)# Customize as needed
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-17)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-18)# You can then serve the customized app directly
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-2-19)uvicorn.run(fastapi_app, host="127.0.0.1", port=9000)

```

#### Configurable Request Handler Components[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#configurable-request-handler-components "Permanent link")

The 
```
A2AServer
```
 supports configurable request handler components for advanced customization:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-2)fromstrands.multiagent.a2aimport A2AServer
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-3)froma2a.server.tasksimport TaskStore, PushNotificationConfigStore, PushNotificationSender
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-4)froma2a.server.eventsimport QueueManager
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-5)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-6)# Custom task storage implementation
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-7)classCustomTaskStore(TaskStore):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-8)    # Implementation details...
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-9)    pass
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-10)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-11)# Custom queue manager
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-12)classCustomQueueManager(QueueManager):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-13)    # Implementation details...
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-14)    pass
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-15)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-16)# Create agent with custom components
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-17)agent = Agent(name="My Agent", description="A customizable agent", callback_handler=None)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-18)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-19)a2a_server = A2AServer(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-20)    agent=agent,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-21)    task_store=CustomTaskStore(),
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-22)    queue_manager=CustomQueueManager(),
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-23)    push_config_store=MyPushConfigStore(),
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-24)    push_sender=MyPushSender()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-3-25))

```

**Interface Requirements:**

Custom implementations must follow these interfaces:

-   ```
    task_store
    ```
    : Must implement 
    ```
    TaskStore
    ```
     interface from 
    ```
    a2a.server.tasks
    ```
    
-   ```
    queue_manager
    ```
    : Must implement 
    ```
    QueueManager
    ```
     interface from 
    ```
    a2a.server.events
    ```
    
-   ```
    push_config_store
    ```
    : Must implement 
    ```
    PushNotificationConfigStore
    ```
     interface from 
    ```
    a2a.server.tasks
    ```
    
-   ```
    push_sender
    ```
    : Must implement 
    ```
    PushNotificationSender
    ```
     interface from 
    ```
    a2a.server.tasks
    ```

#### Path-Based Mounting for Containerized Deployments[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#path-based-mounting-for-containerized-deployments "Permanent link")

The 
```
A2AServer
```
 supports automatic path-based mounting for deployment scenarios involving load balancers or reverse proxies. This allows you to deploy agents behind load balancers with different path prefixes.

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-1)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-2)fromstrands.multiagent.a2aimport A2AServer
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-3)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-4)# Create an agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-5)agent = Agent(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-6)    name="Calculator Agent",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-7)    description="A calculator agent",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-8)    callback_handler=None
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-9))
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-10)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-11)# Deploy with path-based mounting
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-12)# The agent will be accessible at http://my-alb.amazonaws.com/calculator/
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-13)a2a_server = A2AServer(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-14)    agent=agent,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-15)    http_url="http://my-alb.amazonaws.com/calculator"
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-16))
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-17)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-18)# For load balancers that strip path prefixes, use serve_at_root=True
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-19)a2a_server_with_root = A2AServer(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-20)    agent=agent,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-21)    http_url="http://my-alb.amazonaws.com/calculator",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-22)    serve_at_root=True  # Serves at root even though URL has /calculator path
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-4-23))

```

This flexibility allows you to:

-   Add custom middleware
-   Implement additional API endpoints
-   Deploy agents behind load balancers with different path prefixes
-   Configure custom task storage and event handling components

## A2A Client Examples[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#a2a-client-examples "Permanent link")

### Synchronous Client[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#synchronous-client "Permanent link")

Here's how to create a client that communicates with an A2A server synchronously:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-1)importasyncio
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-2)importlogging
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-3)fromuuidimport uuid4
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-4)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-5)importhttpx
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-6)froma2a.clientimport A2ACardResolver, ClientConfig, ClientFactory
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-7)froma2a.typesimport Message, Part, Role, TextPart
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-8)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-9)logging.basicConfig(level=logging.INFO)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-10)logger = logging.getLogger(__name__)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-11)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-12)DEFAULT_TIMEOUT = 300 # set request timeout to 5 minutes
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-13)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-14)defcreate_message(*, role: Role = Role.user, text: str) -> Message:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-15)    return Message(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-16)        kind="message",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-17)        role=role,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-18)        parts=[Part(TextPart(kind="text", text=text))],
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-19)        message_id=uuid4().hex,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-20)    )
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-21)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-22)async defsend_sync_message(message: str, base_url: str = "http://127.0.0.1:9000"):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-23)    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as httpx_client:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-24)        # Get agent card
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-25)        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-26)        agent_card = await resolver.get_agent_card()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-27)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-28)        # Create client using factory
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-29)        config = ClientConfig(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-30)            httpx_client=httpx_client,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-31)            streaming=False,  # Use non-streaming mode for sync response
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-32)        )
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-33)        factory = ClientFactory(config)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-34)        client = factory.create(agent_card)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-35)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-36)        # Create and send message
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-37)        msg = create_message(text=message)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-38)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-39)        # With streaming=False, this will yield exactly one result
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-40)        async for event in client.send_message(msg):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-41)            if isinstance(event, Message):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-42)                logger.info(event.model_dump_json(exclude_none=True, indent=2))
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-43)                return event
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-44)            elif isinstance(event, tuple) and len(event) == 2:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-45)                # (Task, UpdateEvent) tuple
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-46)                task, update_event = event
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-47)                logger.info(f"Task: {task.model_dump_json(exclude_none=True,indent=2)}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-48)                if update_event:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-49)                    logger.info(f"Update: {update_event.model_dump_json(exclude_none=True,indent=2)}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-50)                return task
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-51)            else:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-52)                # Fallback for other response types
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-53)                logger.info(f"Response: {str(event)}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-54)                return event
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-55)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-56)# Usage
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-5-57)asyncio.run(send_sync_message("what is 101 * 11"))

```

### Streaming Client[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#streaming-client "Permanent link")

For streaming responses, use the streaming client:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-1)importasyncio
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-2)importlogging
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-3)fromuuidimport uuid4
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-4)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-5)importhttpx
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-6)froma2a.clientimport A2ACardResolver, ClientConfig, ClientFactory
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-7)froma2a.typesimport Message, Part, Role, TextPart
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-8)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-9)logging.basicConfig(level=logging.INFO)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-10)logger = logging.getLogger(__name__)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-11)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-12)DEFAULT_TIMEOUT = 300 # set request timeout to 5 minutes
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-13)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-14)defcreate_message(*, role: Role = Role.user, text: str) -> Message:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-15)    return Message(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-16)        kind="message",
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-17)        role=role,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-18)        parts=[Part(TextPart(kind="text", text=text))],
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-19)        message_id=uuid4().hex,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-20)    )
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-21)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-22)async defsend_streaming_message(message: str, base_url: str = "http://127.0.0.1:9000"):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-23)    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as httpx_client:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-24)        # Get agent card
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-25)        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-26)        agent_card = await resolver.get_agent_card()
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-27)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-28)        # Create client using factory
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-29)        config = ClientConfig(
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-30)            httpx_client=httpx_client,
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-31)            streaming=True,  # Use streaming mode
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-32)        )
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-33)        factory = ClientFactory(config)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-34)        client = factory.create(agent_card)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-35)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-36)        # Create and send message
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-37)        msg = create_message(text=message)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-38)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-39)        async for event in client.send_message(msg):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-40)            if isinstance(event, Message):
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-41)                logger.info(event.model_dump_json(exclude_none=True, indent=2))
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-42)            elif isinstance(event, tuple) and len(event) == 2:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-43)                # (Task, UpdateEvent) tuple
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-44)                task, update_event = event
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-45)                logger.info(f"Task: {task.model_dump_json(exclude_none=True,indent=2)}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-46)                if update_event:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-47)                    logger.info(f"Update: {update_event.model_dump_json(exclude_none=True,indent=2)}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-48)            else:
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-49)                # Fallback for other response types
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-50)                logger.info(f"Response: {str(event)}")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-51)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-52)# Usage
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-6-53)asyncio.run(send_streaming_message("what is 101 * 11"))

```

## Strands A2A Tool[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#strands-a2a-tool "Permanent link")

### Installation[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#installation_1 "Permanent link")

To use the A2A client tool, install strands-agents-tools with the A2A extra:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-7-1)pipinstall'strands-agents-tools[a2a_client]'

```

Strands provides this tool for discovering and interacting with A2A agents without manually writing client code:

```
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-1)importasyncio
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-2)importlogging
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-3)fromstrandsimport Agent
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-4)fromstrands_tools.a2a_clientimport A2AClientToolProvider
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-5)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-6)logging.basicConfig(level=logging.INFO)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-7)logger = logging.getLogger(__name__)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-8)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-9)# Create A2A client tool provider with known agent URLs
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-10)# Assuming you have an A2A server running on 127.0.0.1:9000
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-11)# known_agent_urls is optional
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-12)provider = A2AClientToolProvider(known_agent_urls=["http://127.0.0.1:9000"])
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-13)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-14)# Create agent with A2A client tools
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-15)agent = Agent(tools=provider.tools)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-16)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-17)# The agent can now discover and interact with A2A servers
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-18)# Standard usage
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-19)response = agent("pick an agent and make a sample call")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-20)logger.info(response)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-21)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-22)# Alternative Async usage
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-23)# async def main():
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-24)#     response = await agent.invoke_async("pick an agent and make a sample call")
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-25)#     logger.info(response)
[](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#__codelineno-8-26)# asyncio.run(main())

```

This approach allows your Strands agent to:

-   Automatically discover available A2A agents
-   Interact with them using natural language
-   Chain multiple agent interactions together

## Troubleshooting[¶](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/multi-agent/agent-to-agent/#troubleshooting "Permanent link")

If you encounter bugs or need to request features for A2A support:

1.  Check the [A2A documentation](https://a2aproject.github.io/A2A/latest/) for protocol-specific issues
2.  Report Strands-specific issues on [GitHub](https://github.com/strands-agents/sdk-python/issues/new/choose)
3.  Include relevant error messages and code samples in your reports