# PyInsurance

A Python library for insurance portfolio management, featuring advanced portfolio protection strategies.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![Type Checker](https://img.shields.io/badge/type%20checker-mypy-blue)](http://mypy-lang.org/)

## Features

- **TIPP Strategy**: Time Invariant Portfolio Protection implementation
- **High Performance**: Cython-optimized core calculations
- **Type Safety**: Full type hints and static type checking
- **Documentation**: Comprehensive docstrings and examples

## Installation

```bash
pip install pyinsurance
```

For development:
```bash
git clone https://github.com/yourusername/pyinsurance.git
cd pyinsurance
pip install -e ".[dev]"
```

## Quick Start

```python
import numpy as np
from pyinsurance.portfolio import TIPP

# Initialize parameters
capital = 100.0
multiplier = 10.0
rr = np.array([0.01, 0.02, -0.01])  # Return rates
rf = np.array([0.001, 0.002, 0.001])  # Risk-free rates
lock_in = 0.05  # 5% lock-in rate
min_risk_req = 0.40  # 40% minimum risk requirement
min_capital_req = 0.80  # 80% minimum capital requirement

# Create TIPP model
tipp = TIPP(
    capital=capital,
    multiplier=multiplier,
    rr=rr,
    rf=rf,
    lock_in=lock_in,
    min_risk_req=min_risk_req,
    min_capital_req=min_capital_req
)

# Run the strategy
tipp.run()

# View results
print(tipp)
```

## Documentation

### TIPP Strategy

The Time Invariant Portfolio Protection (TIPP) strategy is designed to protect investment capital while maintaining upside potential. Key features:

- Dynamic floor adjustment
- Capital protection mechanism
- Risk allocation optimization
- Liquidity injection management

### API Reference

#### TIPP Class

```python
class TIPP:
    def __init__(
        self,
        capital: float,
        multiplier: float,
        rr: NDArray[np.float64],
        rf: NDArray[np.float64],
        lock_in: float,
        min_risk_req: float,
        min_capital_req: float,
        freq: float = 252
    ) -> None:
        """Initialize TIPP model with parameters."""
```

#### Properties

- `portfolio`: Current portfolio values
- `ref_capital`: Reference capital values
- `margin_trigger`: Margin trigger values
- `floor`: Floor values
- `min_risk_req`: Minimum risk requirement
- `min_capital_req`: Minimum capital requirement
- `lock_in`: Lock-in rate
- `multiplier`: Risk multiplier
- `rr`: Return rate array
- `rf`: Risk-free rate array

## Development

### Setup

1. Clone the repository
2. Create a virtual environment
3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Testing

```bash
pytest
```

### Type Checking

```bash
mypy .
```

### Code Style

```bash
black .
isort .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and type checking
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by academic research in portfolio insurance
- Built with Python and Cython
- Uses NumPy for numerical computations 