# Nexstem Instinct Nodes

A Python package for creating distributed nodes using ZeroMQ for communication.

## Features

- Abstract base class for creating distributed nodes
- ZeroMQ-based communication between nodes
- Support for multiple producers and consumers
- Lifecycle management (start, stop, shutdown)
- Support for different message formats (JSON and multipart strings)

## Installation

```bash
pip install instinct-py-nodes
```

## Usage

```python
from instinct_py_nodes import Node, ESignalType, LifeCycleState

class MyNode(Node):
    def onStart(self):
        # Your startup logic here
        pass
    
    def onStop(self):
        # Your stop logic here
        pass
    
    def onShutdown(self):
        # Your shutdown logic here
        pass
    
    def onSignal(self):
        # Your signal handling logic here
        pass

# Create and start your node
node = MyNode()
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 