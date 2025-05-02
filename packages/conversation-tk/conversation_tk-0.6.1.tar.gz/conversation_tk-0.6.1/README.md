# `ctk`: Conversation Tree Toolkit

**`ctk`** (Conversation Tree Toolkit) is a powerful command-line tool designed to manage, analyze, and engage with conversation logs exported from OpenAI's platforms (e.g., ChatGPT). Whether you're looking to filter conversations, perform advanced queries, merge multiple conversation libraries, or leverage Large Language Models (LLMs) for deeper insights, `ctk` provides a comprehensive suite of tools to streamline your workflow.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Available Commands](#available-commands)
    - [`list`](#1-list)
    - [`search`](#2-search)
    - [`jmespath`](#3-jmespath)
    - [`conversation`](#4-conversation)
    - [`merge`](#5-merge)
    - [`export`](#6-export)
- [Examples](#examples)
- [Structure of `conversations.json`](#structure-of-conversationsjson)
- [Notes](#notes)
- [Getting Help](#getting-help)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **List Conversations**: Display a list of all conversations with selected fields.
- **Search with Regex**: Filter conversations based on regex patterns applied to specific fields.
- **Advanced Queries with JMESPath**: Perform complex queries for data retrieval.
- **Conversation Details**: View detailed information about specific conversations.
- **Merge Libraries**: Combine multiple conversation libraries using set operations.
- **Export Conversations**: Export conversations in various formats like JSON, Markdown, or Hugo.
- **Interactive Dashboard**: Launch a Streamlit-based dashboard for visual exploration.

---

## Installation

### Prerequisites

- **Python 3.7+**
- **pip** (Python package installer)

### Local Development Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/queelius/ctk.git
   cd ctk
   ```

2. **Create a Virtual Environment (Optional but Recommended)**

   Using `venv`:

   ```bash
   python3 -m venv ctk-env
   source ctk-env/bin/activate
   ```

   Using `conda`:

   ```bash
    conda create --name ctk-env python=3.8
    conda activate ctk-env
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Make the `ctk` Command Accessible**

   Ensure that the `ctk` script is executable and added to your PATH. You can achieve this by installing the package or setting up an alias.

   ```bash
   chmod +x ctk/cli.py
   ln -s $(pwd)/ctk/cli.py /usr/local/bin/ctk
   ```

   *Alternatively, you can install `ctk` as a package if a `setup.py` is provided.*

---

### End-User Installation Using `pypi`:

1. **Install the Package**

   ```bash
   pip install conversation_tk
   ```

---

## Usage

The `ctk` tool offers various subcommands to perform different operations on your conversation libraries. The general syntax is:

```bash
ctk <command> [options] <arguments>
```

### Available Commands

#### 1. `list`

**Description:**  
Lists all conversations in the specified library directory.

**Usage:**

```bash
ctk list <libdir> [--indices <indices>] [--fields <fields>]
```

**Arguments:**
- `<libdir>`: Path to the conversation library directory.

**Options:**
- `--indices`: Specify the indices of conversations to list. If omitted, all conversations are listed.
- `--fields`: Specify which fields to include in the output (default: `title`, `update_time`).

**Example:**

```bash
ctk list ./conversations --fields title update_time model
```

---

#### 2. `search`

**Description:**  
Runs a regex query on the conversations to filter results based on specified patterns.

**Usage:**

```bash
ctk search <libdir> <expression> --fields <fields>
```

**Arguments:**
- `<libdir>`: Path to the conversation library directory.
- `<expression>`: The regex pattern to search for.

**Options:**
- `--fields`: One or more JMESPath expressions specifying the fields to apply the regex to (default: `title`).
- `--json`: Output the results in JSON format.

**Example:**

```bash
ctk search ./conversations "C\+\+" --fields title --json
```

*Note: To search for the literal string "C++", ensure you escape the plus signs as shown.*

---

#### 3. `jmespath`

**Description:**  
Executes a JMESPath query on the conversations for advanced data retrieval.

**Usage:**

```bash
ctk jmespath <libdir> <query>
```

**Arguments:**
- `<libdir>`: Path to the conversation library directory.
- `<query>`: The JMESPath expression to execute.

**Example:**

```bash
ctk jmespath ./conversations "conversations[?status=='active']"
```

---

#### 4. `conv`

**Description:**  
Prints detailed conversation information based on conversation indices or specific node IDs.

**Usage:**

```bash
ctk conv <libdir> <indices> [--node <node_id>] [--json]
```

**Arguments:**
- `<libdir>`: Path to the conversation library directory.
- `<indices>`: One or more indices of conversations to display.

**Options:**
- `--node`: Specify the node ID to indicate the terminal node of a conversation path.
- `--json`: Output the conversation in JSON format instead of a formatted table.

**Example:**

```bash
ctk conversation ./conversations 0 1 2 --node node123 --json
```

---

#### 5. `merge`

**Description:**  
Merges multiple `ctk` libraries into a single library using specified operations.

**Usage:**

```bash
ctk merge <operation> <libdirs> -o <output_dir>
```

**Arguments:**
- `<operation>`: Type of merge operation (`union`, `intersection`, `difference`).
- `<libdirs>`: List of library directories to merge.

**Options:**
- `-o, --output`: Specify the output library directory.

**Example:**

```bash
ctk merge union ./lib1 ./lib2 -o ./merged_lib
```

---

#### 6. `export`

**Description:**  
Exports conversations from the library in specified formats.

**Usage:**

```bash
ctk export <libdir> <indices> [--format <format>]
```

**Arguments:**
- `<libdir>`: Path to the conversation library directory.
- `<indices>`: One or more indices of conversations to export. If omitted, all conversations are exported.

**Options:**
- `--format`: Output format (`json`, `markdown`, `hugo`). Default is `json`.

**Example:**

```bash
ctk export ./conversations 0 1 --format markdown
```

---

## Examples

1. **Listing All Conversations:**

   ```bash
   ctk list ./conversations
   ```

2. **Listing Specific Fields:**

   ```bash
   ctk list ./conversations --fields title update_time model
   ```

3. **Filtering Conversations with Regex Search:**

   ```bash
   ctk search ./conversations "C\+\+" --fields title --json
   ```

4. **Running a JMESPath Query:**

   ```bash
   ctk jmespath ./conversations "conversations[?status=='active']"
   ```

5. **Merging Two Libraries with Union Operation:**

   ```bash
   ctk merge union ./lib1 ./lib2 -o ./merged_lib
   ```

6. **Exporting Conversations to Markdown:**

   ```bash
   ctk export ./conversations 0 1 --format markdown
   ```


---

## Structure of `conversations.json`

The `ctk` library stores conversation data in a JSON file named `conversations.json` located within your specified library directory (`libdir`). This file contains structured data representing ChatGPT chat sessions, organized as conversation trees.

### Example `conversations.json`:

```json
[
  {
    "id": "conversation_1",
    "title": "Project Discussion",
    "create_time": 1633072800,
    "update_time": 1633076400,
    "default_model_slug": "gpt-3.5-turbo",
    "safe_urls": ["https://example.com"],
    "mapping": {
      "node_1": {
        "text": "Hello, how can I assist you today?",
        "payload": {
          "message": {
            "content": {
              "content_type": "text",
              "parts": ["Hello, how can I assist you today?"]
            },
            "author": {
              "role": "assistant",
              "name": "ChatGPT"
            },
            "create_time": 1633072800
          }
        }
      },
      "node_2": {
        "text": "I need help with my project.",
        "payload": {
          "message": {
            "content": {
              "content_type": "text",
              "parts": ["I need help with my project."]
            },
            "author": {
              "role": "user",
              "name": "Alice"
            },
            "create_time": 1633072860
          }
        }
      }
    },
    "current_node": "node_2"
  }
]
```

*This is a simplified example. The actual structure may vary based on your specific data.*

---

## Notes

- **Library Directory (`libdir`)**: Ensure that the specified library directory exists and contains a valid `conversations.json` file before performing operations.

- **Indices**: Conversation indices start at `0`. Use the `list` command to view available indices before performing operations on specific conversations.

- **Regex Patterns**: When using regex patterns, escape special characters as needed. For example, to search for "C++", use `C\+\+`.

- **Conflict Resolution in Merges**: When merging libraries, duplicate conversation IDs can be handled using strategies like `skip`, `overwrite-old`, or `error` based on your requirements.

- **JSON Output**: Utilize the `--json` flag in commands like `list` and `conversation` for machine-readable output, which is useful for further processing or integration with other tools.

- **Error Handling**: The tool provides informative error messages. Ensure to read them carefully to troubleshoot issues related to missing files, incorrect indices, or invalid configurations.

- **Performance**: For large libraries, some operations might take longer. Consider optimizing your queries and using efficient patterns to enhance performance.

---

## Getting Help

For more information on using the `ctk` tool, access the help documentation for each command using the `--help` flag. For example:

```bash
ctk list --help
```

This command will display detailed information about the `list` command, including its usage, arguments, and options.

---

## Contributing

Contributions are welcome! If you'd like to contribute to the `ctk` project, please follow these steps:

1. **Fork the Repository**

   Click the "Fork" button at the top right of the repository page to create your own fork.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/queelius/ctk.git
   cd ctk
   ```

3. **Create a New Branch**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes**

   Implement your feature or bug fix.

5. **Commit Your Changes**

   ```bash
   git commit -m "Add feature: YourFeatureName"
   ```

6. **Push to Your Fork**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Create a Pull Request**

   Navigate to the original repository and click the "New Pull Request" button. Provide a clear description of your changes.

**Please ensure that your contributions adhere to the project's coding standards and include appropriate tests where applicable.**

---

## License

This project is licensed under the [MIT License](LICENSE).

---


## Contact

For questions, suggestions, or support, please open an issue on the [GitHub repository](https://github.com/queelius/ctk/issues) or contact the maintainer at [lex@metafunctor.com](mailto:lex@metafunctor.com).
