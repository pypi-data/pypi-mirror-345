# H Message Bus

A message bus integration for HAI applications based on NATS.io

## Overview

H Message Bus provides a robust, asynchronous messaging infrastructure built on NATS.io for HAI applications. It enables seamless communication between components through a publish-subscribe pattern, supporting both fire-and-forget messaging and request-response patterns.

## Features

- **Asynchronous Communication**: Built for modern, non-blocking I/O operations
- **Flexible Message Routing**: Publish and subscribe to specific topics
- **High Reliability**: Automatic reconnection handling and configurable timeouts
- **Simple API**: Focus on core messaging functionality with minimal dependencies

## Installation

```bash
pip install h_message_bus
```

## Requirements

- Python 3.10+
- NATS.io server (can be run via Docker)

## Topics

H Message Bus includes predefined topics following the convention: `hai.[source].[destination].[action]`

Available topics:

| Topic Constant                  | Topic String           | Description                         |
|---------------------------------|------------------------|-------------------------------------|
| `Topic.AI_SEND_TG_CHAT_MESSAGE` | `hai.ai.tg.chat.send`  | AI sending message to Telegram chat |
| `Topic.AI_VECTORS_SAVE`         | `hai.ai.vectors.save`  | AI saving data to vector database   |
| `Topic.AI_VECTORS_QUERY`        | `hai.ai.vectors.query` | AI querying vector database         |
| `Topic.TG_SEND_AI_CHAT_MESSAGE` | `hai.tg.ai.chat.send`  | Telegram sending message to AI      |

You can use these predefined topics or create your own topic strings.

## Quick Start

### Start a NATS Server

The easiest way to get started is with Docker:

```bash
docker-compose up -d
```

### Create a Publisher

```python
import asyncio
import uuid
from h_message_bus import NatsConfig, NatsPublisherAdapter, HaiMessage, Topic

async def main():
    # Configure NATS connection
    config = NatsConfig(server="nats://localhost:4222")
    
    # Create publisher adapter
    publisher = NatsPublisherAdapter(config)
    
    # Connect to NATS
    await publisher.connect()
    
    # Create and publish a message using a predefined topic
    message = HaiMessage(
        message_id=str(uuid.uuid4()),
        sender="service-a",
        topic=Topic.TG_SEND_AI_CHAT_MESSAGE,
        payload={"text": "Hello AI, this is a message from Telegram", "chat_id": 12345}
    )
    
    # Publish message
    await publisher.publish(message)
    
    # Clean up
    await publisher.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Create a Subscriber

```python
import asyncio
from h_message_bus import NatsConfig, NatsSubscriberAdapter, HaiMessage, Topic

async def message_handler(message: HaiMessage):
    print(f"Received message: {message.message_id}")
    print(f"From: {message.sender}")
    print(f"Topic: {message.topic}")
    print(f"Payload: {message.payload}")

async def main():
    # Configure NATS connection
    config = NatsConfig(server="nats://localhost:4222")
    
    # Create subscriber
    subscriber = NatsSubscriberAdapter(config)
    
    # Connect to NATS
    await subscriber.connect()
    
    # Subscribe to a topic
    await subscriber.subscribe(Topic.TG_SEND_AI_CHAT_MESSAGE, message_handler)
    
    # Keep the application running
    try:
        print("Subscriber running. Press Ctrl+C to exit.")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Clean up
        await subscriber.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Usage

### Request-Response Pattern

```python
import asyncio
import uuid
from h_message_bus import NatsConfig, NatsPublisherAdapter, HaiMessage, Topic

async def main():
    config = NatsConfig(server="nats://localhost:4222")
    publisher = NatsPublisherAdapter(config)
    
    # Connect to NATS
    await publisher.connect()
    
    request_message = HaiMessage(
        message_id=str(uuid.uuid4()),
        sender="client-service",
        topic=Topic.AI_VECTORS_QUERY,
        payload={"query": "find similar documents", "limit": 10}
    )
    
    # Send request and wait for response (with timeout)
    response = await publisher.request(request_message, timeout=5.0)
    
    if response:
        print(f"Received response: {response.payload}")
    else:
        print("Request timed out")
    
    await publisher.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Creating a Service with Request Handler

```python
import asyncio
import uuid
from h_message_bus import NatsConfig, NatsSubscriberAdapter, NatsPublisherAdapter, HaiMessage, Topic

async def request_handler(request: HaiMessage):
    print(f"Received request: {request.message_id}")
    print(f"Payload: {request.payload}")
    
    # Process the request
    result = {"status": "success", "data": {"result": 42}}
    
    # Create a response message
    return HaiMessage(
        message_id=str(uuid.uuid4()),
        sender="service-b",
        topic=f"{request.topic}.response",
        payload=result,
        correlation_id=request.message_id
    )

async def main():
    # Configure NATS connection
    config = NatsConfig(server="nats://localhost:4222")
    
    # Create subscriber for handling requests
    subscriber = NatsSubscriberAdapter(config)
    publisher = NatsPublisherAdapter(config)
    
    # Connect to NATS
    await subscriber.connect()
    await publisher.connect()
    
    # Register request handler for vector database queries
    await subscriber.subscribe_with_response(Topic.AI_VECTORS_QUERY, request_handler, publisher)
    
    # Keep the application running
    try:
        print("Service running. Press Ctrl+C to exit.")
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Clean up
        await subscriber.close()
        await publisher.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration Options

The `NatsConfig` class allows you to customize your NATS connection:

| Parameter                | Description                                  | Default       |
|--------------------------|----------------------------------------------|---------------|
| `server`                 | NATS server address                          | Required      |
| `max_reconnect_attempts` | Maximum reconnection attempts                | 10            |
| `reconnect_time_wait`    | Time between reconnection attempts (seconds) | 2             |
| `connection_timeout`     | Connection timeout (seconds)                 | 2             |
| `ping_interval`          | Interval for ping frames (seconds)           | 20            |
| `max_outstanding_pings`  | Maximum unanswered pings before disconnect   | 5             |
| `max_payload`            | Maximum size of the payload in bytes         | 1048576 (1MB) |

## API Reference

### Exported Classes

The following classes are exported directly from the package:

- `NatsConfig` - Configuration for the NATS connection
- `HaiMessage` - Message structure for HAI communication
- `NatsPublisherAdapter` - Adapter for publishing messages
- `NatsSubscriberAdapter` - Adapter for subscribing to messages
- `MessageProcessor` - Processing incoming messages
- `NatsClientRepository` - Low-level NATS client operations
- `Topic` - Enumeration of predefined topic strings

### HaiMessage Structure

The `HaiMessage` class is the core data structure used for all messaging:

```python
class HaiMessage:
    message_id: str       # Unique identifier for the message
    sender: str           # Identifier of the sender
    topic: str            # The topic or channel for the message
    payload: dict         # Actual message data
    correlation_id: str = None  # Optional reference to a related message
    timestamp: float = None     # Optional message creation timestamp
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.