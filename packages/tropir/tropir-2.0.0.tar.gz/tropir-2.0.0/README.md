# Tropir

Tropir is a lightweight client for tracking and analyzing your LLM API calls across multiple providers. It automatically logs requests and responses, helping you monitor usage, debug issues, and optimize your AI applications.

## Features

- 🔍 **Zero-config monitoring** - Track all LLM API calls without changing your code
- 📊 **Multi-provider support** - Monitor OpenAI, Anthropic, and AWS Bedrock API calls
- 📈 **Usage analytics** - Monitor token usage, costs, and API performance across providers
- 🐞 **Debugging** - Inspect full request/response payloads for troubleshooting
- 🔄 **Provider comparison** - Compare performance and costs across different LLM providers

## Installation

```bash
pip install tropir
```

## Usage

### Command Line Interface (Recommended)

Simply prefix your normal Python commands with `tropir`:

```bash
# Run a Python script with Tropir tracking
tropir python your_script.py

# Run a Python module with Tropir tracking
tropir python -m your_module

# Pass arguments as usual
tropir python your_script.py --arg1 value1 --arg2 value2
```

No code changes required! The Tropir agent automatically tracks all LLM API calls in your code.

### Advanced: As a Python Library

For more control, you can also use Tropir as a library:

```python
# Import and initialize the agent at the start of your program
from tropir import initialize
initialize()

# Your regular LLM code - all calls will be tracked automatically
import openai
client = openai.OpenAI()

# OpenAI example
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello world"}]
)

# Anthropic example
import anthropic
client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-3-opus-20240229",
    messages=[{"role": "user", "content": "Hello world"}]
)

# AWS Bedrock example
import boto3
bedrock = boto3.client('bedrock-runtime')
response = bedrock.invoke_model(
    modelId="anthropic.claude-3-sonnet-20240229-v1:0",
    body=json.dumps({
        "prompt": "Hello world",
        "max_tokens_to_sample": 300
    })
)
```

## Example Use Cases

### Debugging AI Applications

Instead of adding print statements throughout your code, Tropir provides visibility into every API interaction:

```bash
tropir python debug_my_chatbot.py
```

Then view detailed logs including prompts, completions, and error responses in the Tropir dashboard.

### Cost Management and Provider Comparison

Identify which parts of your application are consuming the most tokens and compare performance across providers:

```python
# Run your application with Tropir
tropir python your_app.py

# Later, analyze the logged data to find optimization opportunities
# Compare costs and performance between OpenAI, Anthropic, and Bedrock
```

## Configuration

Configuration is done via environment variables:

- `TROPIR_ENABLED`: Set to "0" to disable tracking (defaults to "1")
- `TROPIR_API_URL`: Custom API URL (defaults to "https://api.tropir.com/")
- `TROPIR_PROJECT`: Optional project identifier for organizing logs
- `TROPIR_PROVIDERS`: Comma-separated list of providers to track (defaults to "openai,anthropic,bedrock")

Example:
```bash
TROPIR_PROJECT="chatbot-prod" TROPIR_PROVIDERS="openai,anthropic" tropir python my_chatbot.py
```

## License

MIT 