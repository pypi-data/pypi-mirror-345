import json
import yaml                    
import os
import time
import sys
from rich.console import Console
from importlib.metadata import version
import logging
import zipfile
from slugify import slugify
from .utils import (generate_unique_filename, generate_conversation_json,
                    load_conversations)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()
def export_conversations_to_zip(
        libdir,
        indices=None,
        zipfile_name=None,
        compression_level=9):
    """
    Export the specified indices in the ctk library to
    a zip file.
    
    @param libdir: The ctk library directory
    @param indices: The indices of the conversations to export. If None, all conversations are exported.
    @param zipfile_name: The name of the zip file. If None, a unique name is generated based on the library directory.
    @param 
    """
    if not os.path.exists(libdir):
        console.print(
            f"[red]Error: {libdir} does not exist.[/red]")
        sys.exit(1)

    if zipfile_name is None:
        zipfile_name = libdir + ".zip"

    zipfile_name = generate_unique_filename(zipfile_name)
    convs = load_conversations(libdir)
    if indices is None:
        indices = range(len(convs))

    convs = [convs[i] for i in indices if i < len(convs)]

    metadata = {
        "exported_at": int(time.time()),
        "exported_by": os.getlogin(),
        "exported_by_python": sys.version,
        "exported_from": libdir,
        "num_conversations": len(convs),
    }
    with zipfile.ZipFile(zipfile_name,
                         "w") as zf:
        options = {
            "compress_type": zipfile.ZIP_DEFLATED,
            "compresslevel": compression_level
        }

        zf.writestr("metadata.json", json.dumps(metadata, indent=2), **options)
        zf.writestr("conversations.json", json.dumps(convs, indent=2), **options)
        # now we copy the directory of the libdir, which contains the conversations.json, with the exception of copying the conversations.json file
        for root, dirs, files in os.walk(libdir):
            for file in files:
                if file == "conversations.json":
                    continue
                # write the file to the zip file in the zip file, replicating the same structure
                arcname = os.path.relpath(
                    os.path.join(root, file), start=libdir)
                zf.write(os.path.join(root, file), arcname=arcname, **options)

    console.print(
        f"[green]Exported {len(convs)} conversations to {zipfile_name}.[/green]")
    return None


def export_conversations_to_markdown(
        libdir,
        indices=None,                           
        output_dir=None,
        metadata=True,
        all_conversation_paths=False,
        msg_limit=None,
        msg_roles=['user', 'assistant'],
        msg_start_index=0,
        msg_end_index=-1):
    """
    Export the specified indices in the specified ctk library to
    independent markdown filles in the specified output directory.
    
    @param libdir: The ctk library
    @param output_dir: The directory to save the markdown file.
    @param metadata: Whether to show metadata, like `safe_links`, `model`, in a YAML header
    @param all_conversation_paths: Whether to export all conversations in the tree. Default is False, only show the currently active path.
    @param msg_limit: The maximum number of messages to show. Default is None, which means all messages.
    @param msg_roles: The roles of the messages to show. Default is ['user', 'assistant'].
    @param msg_start_index: The starting index of the messages to show. Default is 0.
    @param msg_end_index: The ending index of the messages to show. Default is -1, which means the end of the conversation.
    """
    convs = load_conversations(libdir)
    if indices is None:
        indices = range(len(convs))

    if output_dir is None:
        output_dir = generate_unique_filename(libdir + "_markdown")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.isdir(output_dir):
        console.print(
            f"[red]Error: {output_dir} is not a directory.[/red]")
        sys.exit(1)

    for idx in indices:
        if idx < 0 or idx >= len(convs):
            console.print(f"[red]Warning[/red]: Index {idx} out of range. Skipping.")
            continue
        try:
            conv = convs[idx]

            import AlgoTree
            t = AlgoTree.FlatForest(conv.get("mapping", {}))
            
            if all_conversation_paths:
                leaves = [n.name for n in AlgoTree.leaves(t.root)]
            else:
                leaves = [conv.get("current_node")]

            for leaf in leaves:
                conv_json = generate_conversation_json(
                    conv,
                    terminal_node=leaf,
                    msg_limit=msg_limit,
                    msg_roles=msg_roles,
                    msg_start_index=msg_start_index,
                    msg_end_index=msg_end_index)
                
                meta_dict = None
                title = conv_json["title"]

                if metadata:
                    meta_dict = {
                        "title": title,
                        "conversation_id": conv_json["id"],
                        "model": conv_json["model"],
                        "created": conv_json["created"],
                        "updated": conv_json["updated"],
                        "safe_urls": conv_json["safe_urls"],
                        "openai_url": [conv_json["openai_url"]]
                    }
                
                # Generate filename from title
                filename = slugify(title)
                if filename == "":
                    filename = "Untitled"
                
                file_path = generate_unique_filename(
                    os.path.join(output_dir, f"{filename}.md"))
                
                with open(file_path, "w", encoding="utf-8") as f:
                    # Handle metadata if requested
                    if metadata:
                        # Write YAML frontmatter
                        f.write("---\n")
                        yaml.dump(meta_dict, f, default_flow_style=False, sort_keys=False)
                        f.write("---\n\n")
                    else:
                        f.write(f"# {title}\n\n")
                    
                    # Write messages from cleaned JSON data
                    messages = conv_json["messages"]
                    for i, msg in enumerate(messages):
                        role = msg["role"]
                        
                        f.write(f"**Role:** {role}\n\n")
                        # name = msg.get("name")
                        # if name:
                            # f.write(f"**Name:** {name}\n")
                        
                        # Add message content
                        f.write(msg["content"])
                        f.write("\n\n---\n\n")
                            
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        

    console.print(
        f"[green]Exported {len(indices)} conversations to {output_dir}.[/green]")
    return None

def export_conversations_to_json(
        libdir,
        indices=None,                           
        output_dir=None,
        all_conversation_paths=False,
        msg_limit=None,
        msg_roles=['user', 'assistant'],
        msg_start_index=0,
        msg_end_index=-1):
    """
    Export the specified indices in the specified ctk library to
    independent json filles in the specified output directory.
    
    @param libdir: The ctk library
    @param output_dir: The directory to save the JSON files.
    @param all_conversation_paths: Whether to export all conversations in the tree. Default is False, only show the currently active path.
    @param msg_limit: The maximum number of messages to show. Default is None, which means all messages.
    @param msg_roles: The roles of the messages to show. Default is ['user', 'assistant'].
    @param msg_start_index: The starting index of the messages to show. Default is 0.
    @param msg_end_index: The ending index of the messages to show. Default is -1, which means the end of the conversation.
    """
    convs = load_conversations(libdir)
    if indices is None:
        indices = range(len(convs))

    if output_dir is None:
        output_dir = generate_unique_filename(libdir + "_json")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.isdir(output_dir):
        console.print(
            f"[red]Error: {output_dir} is not a directory.[/red]")
        sys.exit(1)

    for idx in indices:
        if idx < 0 or idx >= len(convs):
            console.print(f"[red]Warning[/red]: Index {idx} out of range. Skipping.")
            continue
        try:
            conv = convs[idx]

            import AlgoTree
            t = AlgoTree.FlatForest(conv.get("mapping", {}))
            
            if all_conversation_paths:
                leaves = [n.name for n in AlgoTree.leaves(t.root)]
            else:
                leaves = [conv.get("current_node")]

            for leaf in leaves:
                conv_json = generate_conversation_json(
                    conv,
                    terminal_node=leaf,
                    msg_limit=msg_limit,
                    msg_roles=msg_roles,
                    msg_start_index=msg_start_index,
                    msg_end_index=msg_end_index)
                
                title = conv_json["title"]
                new_json = {
                    "title": title,
                    "conversation_id": conv_json["id"],
                    "model": conv_json["model"],
                    "created": conv_json["created"],
                    "updated": conv_json["updated"],
                    "safe_urls": conv_json["safe_urls"],
                    "openai_url": [conv_json["openai_url"]]
                }
                
                
                # Write messages from cleaned JSON data
                messages = conv_json["messages"]
                new_json ["messages"] = []
                for i, msg in enumerate(messages):
                    role = msg["role"]
                    new_json["messages"].append({
                        "role": role,
                        "content": msg["content"],
                    })
                            
                # Generate filename from title
                filename = slugify(title)
                if filename == "":
                    filename = "Untitled"
                
                file_path = generate_unique_filename(
                    os.path.join(output_dir, f"{filename}.json"))
                
                with open(file_path, "w", encoding="utf-8") as f:
                    # Write JSON data
                    json.dump(new_json, f, indent=2)

        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")
        

    console.print(
        f"[green]Exported {len(indices)} conversations to {output_dir}.[/green]")
    return None


def export_conversations_to_ctk(
    libdir,
    indices=None,
    output_dir=None):
    """
    Export the specified indices in the library to a new ctk library.
    @param libdir: The ctk library directory
    @param indices: The indices of the conversations to export. If None, all conversations are exported.
    @param output_dir: The directory to save the ctk library. If None, the current directory is used.
    """

    if not os.path.exists(libdir):
        console.print(
            f"[red]Error: {libdir} does not exist.[/red]")
        sys.exit(1)

    if output_dir is None:
        output_dir = generate_unique_filename(libdir + "_exported")
    if os.path.exists(output_dir):
        console.print(
            f"[red]Error: {output_dir} already exists.[/red]")
        sys.exit(1)
    os.makedirs(output_dir)
    convs = load_conversations(libdir)
    if indices is None:
        indices = range(len(convs))
    convs = [convs[i] for i in indices if i < len(convs)]

    # copy all the files in the libdir to the output_dir
    for root, dirs, files in os.walk(libdir):
        for file in files:
            if file == "conversations.json":
                continue
            # write the file to the output_dir in the output_dir, replicating the same structure
            arcname = os.path.relpath(
                os.path.join(root, file), start=libdir)
            os.makedirs(os.path.dirname(os.path.join(output_dir, arcname)), exist_ok=True)
            with open(os.path.join(root, file), "rb") as f:
                with open(os.path.join(output_dir, arcname), "wb") as f_out:
                    f_out.write(f.read())
    # write the conversations.json file to the output_dir
    with open(os.path.join(output_dir, "conversations.json"), "w") as f:
        json.dump(convs, f, indent=2)

    metadata = {
        "exported_at": int(time.time()),
        "exported_by": os.getlogin(),
        "exported_by_python": sys.version,
        "exported_from": libdir,
        "num_conversations": len(convs),
    }
    with open(os.path.join(output_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    console.print(
        f"[green]Exported {len(convs)} conversations to {output_dir}.[/green]")
    return None
    