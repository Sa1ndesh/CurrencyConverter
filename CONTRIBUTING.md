# Contributing to Global Currency

Thank you for considering contributing to `global-currency`! We welcome bug reports, feature suggestions, documentation improvements, and code contributions.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Sa1ndesh/CurrencyConverter.git
   cd CurrencyConverter
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install editable package with development dependencies:
   ```bash
   pip install -e .[dev,charts]
   ```

4. Run tests:
   ```bash
   python -m pytest tests/
   ```

## Pull Request Guidelines

1. **Fork & Branch**: Create a feature branch off `main` (e.g., `feature/my-new-provider`).
2. **Code Style**: Ensure your code follows PEP 8 guidelines.
3. **Testing**: Add unit tests for any new feature or bugfix. Make sure all tests pass before submitting.
4. **Documentation**: Update docstrings and `README.md` if public API signatures change.
5. **Commit Messages**: Write clear, descriptive commit messages.

Thank you for building a better open-source currency converter!
