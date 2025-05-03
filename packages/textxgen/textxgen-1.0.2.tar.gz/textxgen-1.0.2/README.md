

<div align="center">
  <img src="assets/logo_new.png" alt="TextxGen Logo" width="400"/>

  <h1>TextxGen</h1>
  <p>A powerful Python package for seamless interaction with Large Language Models</p>

  <div align="center" style="margin: 20px 0">
    <a href="https://pystack.site/" target="_blank">
      <img src="https://custom-icon-badges.demolab.com/badge/-PyStack_Site-5D4F85?style=for-the-badge&logoColor=white&logo=rocket&labelColor=4B32C3&color=6E5494" alt="PyStack" />
    </a>
    &nbsp;
    <a href="https://t.me/sohails_07" target="_blank">
      <img src="https://img.shields.io/badge/-Telegram-26A5E4?style=for-the-badge&logo=telegram&logoColor=white&labelColor=0088CC&color=26A5E4" alt="Telegram" />
    </a>
    &nbsp;
    <a href="https://www.instagram.com/sohails_07" target="_blank">
      <img src="https://img.shields.io/badge/-Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white&labelColor=C13584&color=E4405F" alt="Instagram" />
    </a>
    &nbsp;
    <a href="https://pypi.org/project/textxgen/" target="_blank">
      <img src="https://img.shields.io/badge/-PyPI_Package-0073B7?style=for-the-badge&logo=pypi&logoColor=white&labelColor=006DAD&color=0073B7" alt="PyPI" />
    </a>
    &nbsp;
    <a href="https://www.python.org" target="_blank">
      <img src="https://img.shields.io/badge/-Python-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=306998&color=FFD43B" alt="Python" />
    </a>
  </div>

  <div align="center" style="margin-top: 15px">
    <a href="https://pepy.tech/project/textxgen" target="_blank">
      <img src="https://static.pepy.tech/badge/textxgen?style=for-the-badge&color=6E5494&labelColor=4B32C3" alt="Total Downloads" width="140" />
    </a>
  </div>
</div>

---

**TextxGen** is a Python package that provides a seamless interface to interact with **Large Language Models**. It supports chat-based conversations and text completions using predefined models. The package is designed to be simple, modular, and easy to use, making it ideal for developers who want to integrate LLM models into their applications.

---

## Features

- **Predefined API Key**: No need to provide your own API key—TextxGen uses a predefined key internally.
- **Chat and Completions**: Supports both chat-based conversations and text completions.
- **System Prompts**: Add system-level prompts to guide model interactions.
- **Error Handling**: Robust exception handling for API failures, invalid inputs, and network issues.
- **Modular Design**: Easily extendable to support additional models in the future.

---

## Installation

You can install TextxGen in one of two ways:

### Option 1: Install via `pip`

```bash
pip install textxgen
```

### Option 2: Clone the Repository

1. Clone the repository from GitHub:
   ```bash
   git clone https://github.com/Sohail-Shaikh-07/textxgen.git
   ```
2. Navigate to the project directory:
   ```bash
   cd textxgen
   ```
3. Install the package locally:
   ```bash
   pip install .
   ```

---

## API Reference

### Chat Endpoint

The Chat Endpoint provides chat-based interactions with the model.

#### Parameters

| Parameter     | Type  | Default  | Description                                 |
| ------------- | ----- | -------- | ------------------------------------------- |
| messages      | list  | required | List of chat messages with role and content |
| model         | str   | "llama3" | Model identifier to use                     |
| system_prompt | str   | None     | Optional system prompt to set context       |
| temperature   | float | 0.7      | Sampling temperature (0.0 to 1.0)           |
| max_tokens    | int   | 100      | Maximum tokens to generate                  |
| stream        | bool  | False    | Whether to stream the response              |
| raw_response  | bool  | False    | Whether to return raw JSON response         |

#### Message Format

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},  # Optional
    {"role": "user", "content": "Hello, how are you?"},
    {"role": "assistant", "content": "I'm doing well, thank you!"}
]
```

#### Example Usage

```python
from textxgen.endpoints.chat import ChatEndpoint

# Initialize the chat endpoint
chat = ChatEndpoint()

# Simple chat completion
messages = [{"role": "user", "content": "What is artificial intelligence?"}]
response = chat.chat(
    messages=messages,
    model="gpt4o_mini",
    temperature=0.7,
    max_tokens=100,
)
print(f"AI: {response}")

# Chat with system prompt
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "Explain quantum computing in simple terms."},
]
response = chat.chat(
    messages=messages,
    model="gpt4o_mini",
    temperature=0.7,
    max_tokens=150,
)
print(f"AI: {response}")

# Streaming chat completion
messages = [{"role": "user", "content": "Write a short story about a robot."}]
for content in chat.chat(
    messages=messages,
    model="gpt4o_mini",
    temperature=0.8,
    max_tokens=100,
    stream=True,
):
    print(content, end="", flush=True)
```

### Completions Endpoint

The Completions Endpoint provides text completion functionality.

#### Parameters

| Parameter    | Type     | Default  | Description                         |
| ------------ | -------- | -------- | ----------------------------------- |
| prompt       | str      | required | Input prompt for text completion    |
| model        | str      | "llama3" | Model identifier to use             |
| temperature  | float    | 0.7      | Sampling temperature (0.0 to 1.0)   |
| max_tokens   | int      | 100      | Maximum tokens to generate          |
| stream       | bool     | False    | Whether to stream the response      |
| stop         | list/str | None     | Stop sequences to end generation    |
| n            | int      | 1        | Number of completions to generate   |
| top_p        | float    | 1.0      | Nucleus sampling parameter          |
| raw_response | bool     | False    | Whether to return raw JSON response |

#### Example Usage

```python
from textxgen.endpoints.completions import CompletionsEndpoint

# Initialize the completion endpoint
completions = CompletionsEndpoint()

# Simple text completion
response = completions.complete(
    prompt="Write a haiku about nature:",
    model="gpt4o_mini",
    temperature=0.7,
    max_tokens=50,
)
print(f"Completion: {response}")

# Text completion with stop sequences
response = completions.complete(
    prompt="Once upon a time,",
    model="gpt4o_mini",
    temperature=0.8,
    max_tokens=100,
    stop=["The End", "END"],
    top_p=0.9,
)
print(f"Completion: {response}")

# Streaming text completion
for content in completions.complete(
    prompt="Write a short poem about technology",
    model="gpt4o_mini",
    temperature=0.8,
    max_tokens=100,
    stream=True,
):
    print(content, end="", flush=True)

# Multiple completions with raw response
response = completions.complete(
    prompt="Give me three different ways to say 'hello':",
    model="gpt4o_mini",
    temperature=0.9,
    max_tokens=50,
    n=3,
    raw_response=True,
)
print("Raw Response:", response)
```

---

## Usage

### 1. Chat Example

Use the `ChatEndpoint` to interact with chat-based models.

```python
from textxgen.endpoints.chat import ChatEndpoint

def main():
    # Initialize the ChatEndpoint
    chat = ChatEndpoint()

    # Define the conversation messages with system prompt
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What is the capital of France?"},
    ]

    # Send the chat request
    response = chat.chat(
        messages=messages,
        model="llama3",  # Use the LLaMA 3 model
        temperature=0.7,  # Adjust creativity
        max_tokens=100,   # Limit response length
    )

    # Print the response
    print("User: What is the capital of France?")
    print(f"AI: {response}")

if __name__ == "__main__":
    main()
```

**Output:**

```
User: What is the capital of France?
AI: The capital of France is Paris.
```

### 2. Completions Example

Use the `CompletionsEndpoint` to generate text completions.

```python
from textxgen.endpoints.completions import CompletionsEndpoint

def main():
    # Initialize the CompletionsEndpoint
    completions = CompletionsEndpoint()

    # Send the completion request
    response = completions.complete(
        prompt="Write a haiku about nature:",
        model="llama3",      # Use the LLaMA 3 model
        temperature=0.7,     # Adjust creativity
        max_tokens=50,       # Limit response length
        top_p=0.9,          # Nucleus sampling
    )

    # Print the response
    print("Prompt: Write a haiku about nature:")
    print(f"Completion: {response}")

if __name__ == "__main__":
    main()
```

**Output:**

```
Prompt: Write a haiku about nature:
Completion: Gentle breeze whispers,
Leaves dance in golden sunlight,
Nature's quiet song.
```

### 3. Streaming Examples

#### Chat Streaming

```python
from textxgen.endpoints.chat import ChatEndpoint

# Initialize the ChatEndpoint
chat = ChatEndpoint()

# Define the conversation messages with system prompt
messages = [
    {"role": "system", "content": "You are a helpful AI assistant."},
    {"role": "user", "content": "Write a short story about a robot."},
]

# Send the chat request with streaming
print("User: Write a short story about a robot.")
print("AI: ", end="", flush=True)
for content in chat.chat(
    messages=messages,
    model="llama3",
    temperature=0.8,
    max_tokens=100,
    stream=True,  # Enable streaming
):
    print(content, end="", flush=True)
print("\n")
```

**Output:**

```
User: Write a short story about a robot.
AI: In a bustling city of tomorrow, a small robot named Spark spent its days cleaning the streets. Unlike other robots, Spark had developed a curious habit of collecting lost items and trying to return them to their owners. One day, while cleaning a park bench, it found a small music box. As it played the melody, people gathered around, and for the first time, the city's residents saw robots not just as machines, but as beings capable of bringing joy and wonder to their lives.
```

#### Completion Streaming

```python
from textxgen.endpoints.completions import CompletionsEndpoint

# Initialize the CompletionsEndpoint
completions = CompletionsEndpoint()

# Send the completion request with streaming
print("Prompt: Write a poem about technology")
print("Completion: ", end="", flush=True)
for content in completions.complete(
    prompt="Write a poem about technology",
    model="llama3",
    temperature=0.8,
    max_tokens=100,
    stream=True,  # Enable streaming
):
    print(content, end="", flush=True)
print("\n")
```

**Output:**

```
Prompt: Write a poem about technology
Completion: In circuits deep and silicon bright,
Machines dance in digital light.
From simple tools to AI's might,
Human dreams take flight.
Each byte a story, each code a song,
In this world where we belong.
```

### 4. Listing Supported Models

Use the `ModelsEndpoint` to list and retrieve supported models.

```python
from textxgen.endpoints.models import ModelsEndpoint

def main():
    """
    Example usage of the ModelsEndpoint to list and retrieve supported models.
    """
    # Initialize the ModelsEndpoint
    models = ModelsEndpoint()

    # List all supported models
    print("=== Supported Models ===")
    for model_name, display_name in models.list_display_models().items():
        print(f"{model_name}: {display_name}")

if __name__ == "__main__":
    main()
```

---

## Supported Models

TextxGen currently supports the following models:

| Model Name                              | Model ID        | Description                                                       |
| --------------------------------------- | --------------- | ----------------------------------------------------------------- |
| LLaMA 3 (8B Instruct)                   | `llama3`        | A powerful 8-billion parameter model for general-purpose tasks.   |
| Phi-3 Mini (128K Instruct)              | `phi3`          | A lightweight yet capable model optimized for efficiency.         |
| DeepSeek Chat                           | `deepseek`      | A conversational model designed for interactive chat.             |
| Qwen 2.5 (3B Parameters)                | `qwen2_5`       | A versatile 3B parameter model with vision-language capabilities. |
| DeepSeek Chat V3                        | `deepseek_v3`   | The latest version of DeepSeek's conversational model.            |
| Google Gemma 3 (4B Parameters)          | `gemma3_4b`     | Google's 4B parameter model optimized for various tasks.          |
| Google Gemma 3 (1B Parameters)          | `gemma3_1b`     | A lightweight 1B parameter version of Google's Gemma model.       |
| Qwen 3 (14B Parameters)                 | `qwen3`         | A powerful 14B parameter model for advanced tasks.                |
| DeepSeek R1-T (Chimera)                 | `deepseek_r1_t` | A specialized model from DeepSeek's R1 series.                    |
| Deepcoder (14B Parameters)              | `deepcoder_14b` | A 14B parameter model focused on coding tasks.                    |
| Llama 4 Maverick (17B Instruct)         | `llama4`        | Meta's latest 17B parameter model for instruction following.      |
| Qwerky (72B Parameters)                 | `qwerky_72b`    | A massive 72B parameter model for complex tasks.                  |
| HuggingFace Zephyr (7B Parameters Beta) | `huggingface_4` | HuggingFace's 7B parameter model in beta testing.                 |
| OpenAI GPT 4.1 Nano                     | `gpt4_1_nano`   | OpenAI's compact version of GPT 4.1.                              |
| OpenAI GPT 4o Mini                      | `gpt4o_mini`    | OpenAI's mini version of GPT 4o.                                  |
|                                         |

---

## Error Handling

TextxGen provides robust error handling for common issues:

- **Invalid Input**: Raised when invalid input is provided (e.g., empty messages or prompts).
- **API Errors**: Raised when the API returns an error (e.g., network issues or invalid requests).
- **Unsupported Models**: Raised when an unsupported model is requested.

**Example:**

```python
from textxgen.exceptions import InvalidInputError

try:
    response = chat.chat(messages=[])
except InvalidInputError as e:
    print("Error:", str(e))
```

---

## Contributing

Contributions are welcome! To contribute to TextxGen:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

---

## License

TextxGen is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Buy Me a Coffee

If you find TextxGen useful and would like to support its development, you can buy me a coffee! Your support helps maintain and improve the project.

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/sohails07)

---

## Support

If you encounter any issues or have questions, please open an issue on the [GitHub repository](https://github.com/Sohail-Shaikh-07/textxgen).
