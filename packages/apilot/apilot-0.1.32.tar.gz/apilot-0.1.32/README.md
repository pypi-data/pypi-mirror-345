# APilot - AI-Driven Quantitative Trading Platform

<p align="center">
    <img src ="https://img.shields.io/badge/version-0.1.2-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/python-3.10|3.11|3.12-blue.svg" />
    <img src ="https://img.shields.io/badge/license-MIT-green.svg" />
</p>

## Overview

APilot is a high-performance quantitative trading framework focused on cryptocurrency and stock markets, developed by the AlphaPilot.tech team. The framework supports both strategy backtesting and live trading, providing a comprehensive solution for quantitative traders.

Official website: [www.alphapilot.tech](https://www.alphapilot.tech)

## Key Features

- **Event-driven architecture**: Built for high-performance, real-time trading systems
- **Multiple trading strategies**: Price Action strategies, Factor strategies (in development)
- **Professional execution algorithms**: BestLimit, TWAP algorithms
- **Comprehensive backtesting**: Accurate simulation with detailed performance analytics
- **Multi-exchange support**: Currently focusing on Binance, with more to come
- **Live trading capability**: Execute strategies in real-time with risk management
- **Extensible framework**: Easy to add new strategies, data sources, and exchanges

## Strategy Types

- **Price Action (PA) strategies**: Support for trend following, mean reversion, and other classic price action strategies
- **Factor strategies**: Quantitative strategies based on multi-factor models (in development)

## Technical Architecture

### Design Principles

- **Core Module**: Contains all abstract interfaces and core data structures
  - Abstract base classes (BaseEngine, BaseGateway, etc.)
  - Data models (OrderData)
  - Constant definitions (Direction, Interval, etc.)
  - Basic event system

- **Feature Modules**: Specific implementations for different domains
  - `execution/gateway/` - Exchange API implementations
  - `engine/` - Specific engine implementations
  - `strategy/` - Trading strategy templates and implementations
  - `performance/` - Performance calculation and reporting

## Installation



## Quick Start

### Backtesting a Strategy




### Running Live Trading


## Getting Started with Development

For detailed documentation on developing with APilot, please refer to our [Development Guide](docs/development_guide.md).

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_bar_generator.py
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
