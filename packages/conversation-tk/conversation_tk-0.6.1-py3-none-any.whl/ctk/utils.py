import json
import os
import jmespath
import re
import AlgoTree
import time
from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

console = Console()

def path_value(data, path):

    for p in path:
        data = data.get(p)
        if data is None:
            break

    last = path[-1].lower()
    if last == "create_time":
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data))
    elif isinstance(data, (int, float)):
        return str(data)
    elif isinstance(data, (list, dict)):
        return json.dumps(data)
    elif data is None:
        return "N/A"
    else:
        return data


def load_conversations(libdir):
    """
    @brief Load all conversations from `<libdir>/conversations.json`.
    @param libdir Path to the conversation library directory.
    @return A Python object (usually a list) of conversations.
    """
    conv_path = os.path.join(libdir, "conversations.json")
    if not os.path.isfile(conv_path):
        return []

    with open(conv_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_conversations(libdir, conversations, overwrite=False):
    """
    @brief Save conversation data to `<libdir>/conversations.json`.
    @param libdir Path to the conversation library directory.
    @param conversations Python list/dict containing conversation data.
    @param overwrite If True, overwrite the existing file.
    @return None
    """
    conv_path = os.path.join(libdir, "conversations.json")
    if os.path.isfile(conv_path) and not overwrite:
        console.print(f"[red]File {conv_path} already exists. Use overwrite=True to overwrite.[/red]")
        return

    ensure_libdir_structure(libdir)
    if not isinstance(conversations, list):
        console.print("[red]Conversations should be a list.[/red]")
        return
    if not conversations:
        console.print("[red]No conversations to save.[/red]")
        return
    if not all(isinstance(conv, dict) for conv in conversations):
        console.print("[red]All conversations should be dictionaries.[/red]")
        return
    if not all("id" in conv for conv in conversations):
        console.print("[red]All conversations should have an 'id' field.[/red]")
        return
    if not all("title" in conv for conv in conversations):
        console.print("[red]All conversations should have a 'title' field.[/red]")
        return

    with open(conv_path, "w", encoding="utf-8") as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)

def ensure_libdir_structure(libdir):
    """
    @brief Ensure that the specified library directory contains expected structure.
    @param libdir Path to the conversation library directory.
    @details Creates the directory if it doesn't exist, as well as placeholders.
    """
    if not os.path.isdir(libdir):
        os.makedirs(libdir)


def list_conversations(libdir, path_fields, indices=None, json_output=False):
    """
    @brief List all conversations found in `<libdir>/conversations.json`.

    @param libdir Path to the conversation library directory.
    @param path_fields A list of JMESPath query strings to include in the output.
    @param indices A list of indices to list. If None, list all.
    @param json_output If True, output as JSON instead of a table.
    @return List of conversation data with requested fields
    """
    conversations = load_conversations(libdir)
    if not conversations:
        console.print("[red]No conversations found.[/red]")
        return []

    max_index = len(conversations)
    if indices is None:
        indices = list(range(max_index))
    else:
        # Filter out invalid indices
        indices = [i for i in indices if 0 <= i < max_index]
    
    if not indices:
        console.print("[yellow]No valid conversation indices specified.[/yellow]")
        return []

    # Build a structured representation for output
    result_data = []
    for i in indices:
        conv = conversations[i]
        entry = {"index": i}
        
        for field in path_fields:
            value = jmespath.search(field, conv)
            
            # Format timestamps consistently
            if isinstance(value, (int, float)) and (field.endswith('_time') or field == 'create_time' or field == 'update_time'):
                value = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))
            
            entry[field] = value
        result_data.append(entry)

    # Handle JSON output option
    if json_output:
        console.print(json.dumps(result_data, indent=2, ensure_ascii=False))
        return result_data
    
    # Create a table with the same style as the original
    table = Table(title=f"Conversations ({len(result_data)} of {len(conversations)})")
    color_cycle = ["cyan", "magenta", "green", "yellow", "blue"]
    
    # Add columns with cycling colors
    table.add_column("#", justify="right", style=color_cycle[0])
    for idx, field in enumerate(path_fields):
        table.add_column(field, style=color_cycle[(idx + 1) % len(color_cycle)])
    
    # Add rows to the table
    for entry in result_data:
        i = entry["index"]
        
        # Format each value for display
        row_values = []
        for field in path_fields:
            value = entry[field]
            
            if value is None:
                formatted = "N/A"
            elif isinstance(value, (list, dict)):
                formatted = str(value)
            else:
                formatted = str(value)
                
            row_values.append(formatted)
            
        table.add_row(str(i), *row_values)
        
    console.print(table)
    return result_data


def query_conversations_jmespath(libdir, expression):
    """
    @brief Query the conversations with a JMESPath expression.

    @param libdir Path to the conversation library directory.
    @param expression A JMESPath query string.
    @return The result of the JMESPath query.
    """
    conversations = load_conversations(libdir)
    return jmespath.search(expression, conversations)


def query_conversations_search(conversations, indices, expression, fields):
    """
    @brief Query the conversations with a regex expression.

    @param conversastions List of conversations.
    @param indices A list of indices to search.
    @param expression A regex expression.
    @param fields A list of JMESPath query strings to apply the regex to.
    @return A list of conversations that satisfy the regex expression.

    """
    results = []
    pattern = re.compile(expression, re.IGNORECASE)

    for i, conv in enumerate(conversations):
        if indices is not None and i not in indices:
            continue
        for field in fields:
            out = jmespath.search(field, conv)
            if isinstance(out, (int, float)):
                out = str(out)
            elif isinstance(out, (list, dict)):
                out = json.dumps(out)  # Convert complex types to JSON string
            elif out is None:
                continue  # Skip if the field is None
            else:
                out = str(out)

            if pattern.search(out):
                results.append(i)
                break  # Move to the next conversation after a match

    return results
        

def generate_conversation_json(
        conv,
        terminal_node=None,
        msg_limit=None,
        msg_roles=['user', 'assistant'],
        msg_start_index=0,
        msg_end_index=-1):
    """
    Generate a conversation from a conversation tree. The conversation is defined by the
    terminal node of the conversation tree. The conversation is a list of messages.
    
    @param conv: The conversation tree object.
    @param terminal_node: The terminal node of the conversation. This determines which conversation path in the conversation tree to generate.
    @param msg_limit: The maximum number of messages to show. Default is None, which means all messages.
    @param msg_roles: The roles of the messages to show. Default is ['user', 'assistant'].
    @param msg_start_index: The starting index of the messages to show. Default is 0.
    @param msg_end_index: The ending index of the messages to show. Default is -1, which means the end of the conversation.
    @return: JSON object of the conversation.
    """
    if terminal_node is None:
        terminal_node = conv.get("current_node")

    t = AlgoTree.FlatForest(conv.get("mapping", {}))
    n = t.node(terminal_node)
    ancestors = reversed(AlgoTree.ancestors(n))
    msgs = [node.payload.get('message')
            for node in ancestors] + [n.payload.get('message')]
    if msg_end_index < 0:
        msg_end_index += len(msgs)
    if msg_start_index < 0:
        msg_start_index += len(msgs)

    msgs = [msg for i, msg in enumerate(
        msgs) if i >= msg_start_index and i <= msg_end_index and msg is not None]
    msgs = [msg for msg in msgs if msg.get(
        "author", {}).get("role", "") in msg_roles]
    msgs = [msg for msg in msgs if msg.get(
        "content", {}).get("content_type") == "text"]
    msgs = msgs[:msg_limit]

    clean_msgs = []
    for msg in msgs:
        # Convert the message to a JSON object
        new_msg = {}
        new_msg['content'] = "".join(
            [part for part in msg.get('content', {}).get("parts", [])])
        new_msg['create_time'] = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(msg.get('create_time')))
        
        author = msg.get('author', {})
        if author.get('name'):
            new_msg['name'] = author.get('name')
        new_msg['role'] = author.get('role', 'N/A')
        
        clean_msgs.append(new_msg)

    title = conv.get("title", "Untitled")
    created = conv.get("create_time")
    updated = conv.get("update_time")
    model = conv.get("default_model_slug")
    safe_urls = conv.get("safe_urls", [])
    conversation_id = conv.get("id")
    if created is not None:
        created = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(created))
    if updated is not None:
        updated = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(updated))
    openai_link = f"https://chat.openai.com/c/{conversation_id}"

    return {
        "title": title,
        "created": created,
        "updated": updated,
        "model": model,
        "safe_urls": safe_urls,
        "id": conversation_id,
        "openai_url": openai_link,
        "messages": clean_msgs
    }

def pretty_print_conversation(conv, terminal_node=None, msg_limit=None, msg_roles=['user', 'assistant'], msg_start_index=0, msg_end_index=-1):
    # Get conversation data using generate_conversation_json
    conv_json = generate_conversation_json(
        conv,
        terminal_node=terminal_node,
        msg_limit=msg_limit,
        msg_roles=msg_roles,
        msg_start_index=msg_start_index,
        msg_end_index=msg_end_index
    )
    print_json_as_table(conv_json, table_title=conv['title'])

def print_json_as_table(data, table_title=None):
    """
    Pretty print JSON data as a table using Rich.

    Args:
        data: JSON data to print (dict, list, or other)
        table_title: Optional title for the table
        indent: Indentation level for nested tables
    """
    console.print(create_table_from_json(data, table_title))
    

def create_table_from_json(data, title=""):
    """
    Create a Rich Table for list data.

    Args:
        data: List of items
        title: Optional title for the nested list

    Returns:
        A Renderable object representing the nested list
    """

    table = None

    if isinstance(data, list):
        table = Table(show_header=False, show_lines=False, show_edge=True)
        for index, item in enumerate(data):
            table.add_row(str(index), create_table_from_json(item, title))
    
    elif isinstance(data, dict):
        table = Table(show_header=False, show_edge=True, show_lines=False)
        for key, value in data.items():
            table.add_row(key, create_table_from_json(value, title))

    elif isinstance(data, str):
        table = Table(show_header=False, show_lines=False, show_edge=False)
        table.add_row(Markdown(data))

    elif data is None:
        table = Table(show_header=False, show_lines=False, show_edge=False)
        table.add_row("N/A")

    else:
        table = Table(show_header=False, show_lines=False, show_edge=False)
        table.add_row(str(data))

    return table


def generate_unique_filename(preferred_name):
    """
    Generate a unique filename by appending an integer suffix if the file already exists
    such that `preferred_name_n` is used if `preferred_name`, `preferred_name_2`, ...,
    `preferred_name_{n-1}` already exist.
    """
    base, ext = os.path.splitext(preferred_name)
    n = 1
    while os.path.exists(preferred_name):
        preferred_name = f"{base}_{n}{ext}"
        n += 1
    return preferred_name


