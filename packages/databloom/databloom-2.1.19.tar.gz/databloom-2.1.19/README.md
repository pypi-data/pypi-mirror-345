# DataBloom SDK Client

A Python SDK client for data integration with PostgreSQL, MySQL, Nessie, and S3.

## Quick Start

```bash
# Setup environment
conda create -n data_bloom python=3.11
conda activate data_bloom

# Install
pip install -e ".[dev]"
```

## Configuration

Create `.env` file with your credentials:

## Testing

```bash
# Run all tests
make test
```

## Development

```bash
make format          # Format code
make lint           # Run linter
make doc            # Build docs
```

## License

VNG License
