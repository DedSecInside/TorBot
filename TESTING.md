# Testing Documentation

This document provides comprehensive testing instructions for TorBot, including local development and Docker environments.

## Testing Framework

We use [`pytest`](https://docs.pytest.org/en/latest/) as our testing framework with the following structure:

```
tests/
├── __init__.py
├── test_api.py          # API endpoint tests
├── test_linktree.py     # Link tree functionality tests
└── conftest.py         # Pytest configuration (optional)
```

## Running Tests

### Local Development

1. **Install testing dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov pytest-mock
   ```

2. **Run all tests:**
   ```bash
   pytest
   ```

3. **Run with verbose output:**
   ```bash
   pytest -v
   ```

4. **Run with print statements:**
   ```bash
   pytest -s
   ```

5. **Run specific test file:**
   ```bash
   pytest tests/test_api.py
   ```

6. **Run with coverage:**
   ```bash
   pytest --cov=src/torbot tests/
   ```

### Docker Testing

1. **Test Docker build:**
   ```bash
   # Build test image
   docker build -t torbot:test .
   
   # Run tests in container
   docker run --rm torbot:test pytest tests/
   
   # Run tests with coverage
   docker run --rm torbot:test pytest --cov=src/torbot tests/
   ```

2. **Development testing with volume mounts:**
   ```bash
   # Run tests with live code changes
   docker run --rm \
     -v $(pwd)/src:/app/src \
     -v $(pwd)/tests:/app/tests \
     torbot:test pytest tests/ -v
   ```

3. **Test with Docker Compose:**
   ```bash
   # Create test service
   docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
   ```

## Test Categories

### Unit Tests
- **API Tests**: Test API endpoints and response formats
- **Link Tree Tests**: Test link extraction and tree building
- **Parser Tests**: Test HTML parsing and data extraction
- **Utility Tests**: Test helper functions and utilities

### Integration Tests
- **Network Tests**: Test actual HTTP requests (when safe)
- **Tor Integration**: Test SOCKS5 proxy functionality
- **File I/O Tests**: Test saving/loading functionality

### Mock Tests
We use [`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html) to patch:
- `httpx.Client` for network requests
- File system operations
- External API calls

## Writing Tests

### Test Structure
```python
# tests/test_example.py
import pytest
from unittest.mock import patch, MagicMock
from src.torbot.module import function_to_test

class TestFunctionality:
    """Test suite for specific functionality"""
    
    def test_success_case(self):
        """Test successful execution"""
        result = function_to_test("valid_input")
        assert result is not None
        
    def test_error_handling(self):
        """Test error conditions"""
        with pytest.raises(ValueError):
            function_to_test("invalid_input")
            
    @patch('src.torbot.module.httpx.Client')
    def test_with_mock(self, mock_client):
        """Test with mocked network calls"""
        mock_response = MagicMock()
        mock_response.text = "<html>test</html>"
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response
        
        result = function_to_test("http://example.com")
        assert result == expected_result
```

### Test Data
Place test data in `tests/data/` directory:
```
tests/
├── data/
│   ├── sample_html.html
│   ├── expected_results.json
│   └── mock_responses/
```

## Continuous Integration

### GitHub Actions
Our CI pipeline runs:
- **pytest**: All unit tests
- **flake8**: Code style checks
- **coverage**: Code coverage reports
- **docker**: Container build tests

### Local CI Simulation
```bash
# Run all checks locally
python -m pytest tests/
python -m flake8 src/ tests/
python -m mypy src/
docker build -t torbot:ci .
```

## Performance Testing

### Load Testing
```bash
# Test with multiple URLs
docker run --rm torbot:test python -c "
import time
from src.torbot.module import test_multiple_urls
start = time.time()
test_multiple_urls(urls, depth=2)
print(f'Duration: {time.time() - start}s')
"
```

### Memory Usage
```bash
# Monitor memory usage
docker run --rm --memory=256m torbot:test pytest tests/
```

## Debugging Tests

### Debug Mode
```bash
# Run with debugger
pytest --pdb tests/test_api.py::TestAPI::test_specific_endpoint

# Verbose output with details
pytest -vv -s tests/
```

### Test Isolation
```bash
# Run specific test
pytest tests/test_linktree.py::TestLinkTree::test_tree_building -v

# Run tests matching pattern
pytest -k "test_api" tests/
```

## Test Dependencies

### Required Packages
```txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-asyncio>=0.21.0
```

### Development Dependencies
```bash
pip install pytest-benchmark  # Performance testing
pip install pytest-xdist      # Parallel testing
pip install pytest-html       # HTML reports
```

## Troubleshooting

### Common Issues

1. **Import errors:**
   ```bash
   export PYTHONPATH=$PWD:$PYTHONPATH
   ```

2. **Network tests failing:**
   Use mock objects for network-dependent tests

3. **Permission errors:**
   Ensure proper file permissions for test data

4. **Docker test failures:**
   Check Docker daemon and resource limits

### Debug Commands
```bash
# Check test discovery
pytest --collect-only

# Run with coverage report
pytest --cov=src/torbot --cov-report=html tests/

# Generate test report
pytest --junitxml=test-results.xml tests/
```

## Contributing Tests

When adding new features:

1. **Write tests first** (TDD approach)
2. **Ensure 80%+ coverage** for new code
3. **Include edge cases** and error handling
4. **Test both positive and negative scenarios**
5. **Update this documentation** if testing procedures change

### Test Checklist
- [ ] Unit tests for new functions
- [ ] Integration tests for API endpoints
- [ ] Error handling tests
- [ ] Performance tests for heavy operations
- [ ] Docker compatibility tests
- [ ] Documentation updated
