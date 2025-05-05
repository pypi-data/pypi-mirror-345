# ScreenScout UI Testing Framework

A Python-based UI testing framework that allows you to create and execute UI tests using natural language descriptions.

## Prerequisites

- Python 3.x
- OpenAI API key (for test generation)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The script supports two main modes of operation: comprehensive testing and custom test creation.

# 1) Comprehensive multi‑page run
screen-scout --url ycombinator.com --comprehensive --test-depth 4 --key $OPENAI_API_KEY

# 2) Requirement → tests → execution
screen-scout                                  \
  --url ycombinator.com                       \
  --test-description "Verify Apply button works" \
  --num-tests 2                               \
  --key $OPENAI_API_KEY

# 3) Run a single, fully‑written prompt
screen-scout                                  \
  --url ycombinator.com                       \
  --execute "$(cat one_test_prompt.txt)"      \
  --record                                    \
  --key $OPENAI_API_KEY

### Basic Usage

```bash
python src/main.py --url <website_url> [options]
```

### Required Arguments

- `--url`: The URL of the website to test (required)

### Optional Arguments

- `--port`: Port for local communication (default: 3000)
- `--test-description`: Description of the UI test to perform
- `--num-tests`: Number of tests to generate (default: 1)
- `--comprehensive`: Enable comprehensive testing mode
- `--test-depth`: Depth of the test to perform (default: 4)
- `--key`: OpenAI API key for test generation

### Examples

1. Run a comprehensive test:
```bash
python src/main.py --url https://example.com --comprehensive --key your-api-key
```

2. Create a custom test:
```bash
python src/main.py --url https://example.com --test-description "Test the login form" --key your-api-key
```

3. Generate multiple tests:
```bash
python src/main.py --url https://example.com --test-description "Test navigation menu" --num-tests 3 --key your-api-key
```

4. Run with custom port and test depth:
```bash
python src/main.py --url https://example.com --comprehensive --port 4000 --test-depth 5 --key your-api-key
```

## Environment Variables

You can set the browser logging level from the command line:
```bash
BROWSER_USE_LOGGING_LEVEL=result python src/main.py [arguments]
```

## Output

The script will output:
- Generated test cases
- Test execution results
- Execution time (in seconds)

## Building a Binary
pyinstaller --onefile src/main.py --name screen_scout

