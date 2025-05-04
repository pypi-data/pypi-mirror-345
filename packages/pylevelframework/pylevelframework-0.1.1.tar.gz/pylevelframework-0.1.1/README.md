# PyLevel

A Python-based command-line server with controller management, configuration handling, and process management capabilities.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/py-level/py-level.git
cd py-level
```

2. Install the package:
```bash
pip install -e .
```

## Quick Start

1. Start the server:
```bash
pylevel serve --port 8000 --workers 4
```

2. Create a controller:
```bash
pylevel make:controller UserController
```

3. Check server status:
```bash
pylevel status
```

For a complete list of commands and their options, see [COMMANDS.md](COMMANDS.md).

## Environment Variables

You can configure the server using environment variables prefixed with `PYLEVEL_`:

```bash
export PYLEVEL_PORT=8000
export PYLEVEL_WORKERS=4
export PYLEVEL_HOST=127.0.0.1
```

## Development

### Project Structure

```
slave/
├── __init__.py         # Package initialization
├── __main__.py        # Entry point
├── cli.py             # Command-line interface
├── config.py          # Configuration management
├── controllers.py     # Controller management
├── process.py         # Process management
└── app/
    └── controllers/   # Controller implementations
        └── base_controller.py
```

### Creating a Custom Controller

```python
from typing import Dict, Any
from slave.app.controllers.base_controller import BaseController

class UserController(BaseController):
    async def get(self, request: Dict[str, Any]) -> Dict[str, Any]:
        # Validate request
        rules = {
            'id': {'required': True, 'type': int}
        }
        if not self.validate(rules):
            return self.get_response()
            
        # Process request
        user_id = request['id']
        return self.success({'id': user_id, 'name': 'John Doe'})
```

## Documentation

- [Commands Documentation](COMMANDS.md) - Detailed information about all available commands
- [Contributing Guidelines](CONTRIBUTING.md) - Guidelines for contributing to the project
- [API Documentation](docs/API.md) - API reference and examples

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 