# Contributing to acceptance-bench

We welcome contributions! Here's how to help:

## Development Setup

```bash
git clone https://github.com/ellydee/acceptance-bench.git
cd acceptance-bench
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
pytest tests/
```

## Code Style

We use:
- Black for formatting
- Flake8 for linting
- MyPy for type checking

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Adding Tasks

See `acceptance_bench/tasks/task_sets/v1/` for examples.

## Questions?

Open an issue or discussion!