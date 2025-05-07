# Factchecker SDK

Factchecker SDK is a Python package that verifies factual statements in text using multiple verification models. It supports streaming and non-streaming responses to suit different accuracy and speed needs.

## Installation

You can install the Factchecker SDK via pip:

```bash
pip install hurix-ai
```

## Features

- **Multiple Verification Models:**
  - `verify_with_chunks`
  - `verify_with_snippets` (Fast but low accuracy)
  - `verify_with_snippets_and_chunks`
  - `verify_with_snippets_and_chunks_and_partial_claude_entailment` (Most accurate but slow)
- **Methods:**
  - `fact_check` - Standard fact-checking method.
  - `fact_check_streaming` - Provides a streaming response.

## Usage

```python
from hurix_ai.factchecker import FactChecker

# Initialize the FactChecker object
obj = FactChecker(api_key="xxxxx", base_url='xxxx', model_name='verify_with_snippets')

# Perform fact-checking
res = obj.fact_check("The capital of India is Delhi")
print(res)
```

### Streaming Fact-Checking
```python
for response in obj.fact_check_streaming("The capital of India is Delhi"):
    print(response)
```

## License

This package is licensed under the MIT License.
