"""
@file cli.py
@brief ctk command-line tool for managing and analyzing chat logs.

This script provides subcommands to import, list, merge, run jmespath queries, etc.
"""

import argparse
import json
import sys
import AlgoTree
from rich.console import Console
from rich.json import JSON
from importlib.metadata import version
import webbrowser
import logging

from .utils import (load_conversations, save_conversations, pretty_print_conversation,
                    query_conversations_search, query_conversations_jmespath, path_value,
                    list_conversations, ensure_libdir_structure, generate_conversation_json, print_json_as_table)
from .merge import union_libs, intersect_libs, diff_libs
from .stats import get_conversation_tree_stats
from .export import (export_conversations_to_zip, export_conversations_to_markdown,
                     export_conversations_to_ctk, export_conversations_to_json)

from .slicing import resolve_indices

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()


################################################################################
# COMMAND-LINE INTERFACE (argparse)
################################################################################


def main():
    """
    @brief Main entry point for the ctk CLI.
    @return None
    """
    parser = argparse.ArgumentParser(
        description="ctk: A command-line tool for chat log management and analysis."
    )
    parser.add_argument("--version", action="version",
                        version=version("conversation-tk"))

    subparsers = parser.add_subparsers(
        dest="command", help="Subcommand to run")

    # Subcommand: search
    regex_parser = subparsers.add_parser(
        "search", help="Run a search using regex against the ctk lib on the specified fields")
    regex_parser.add_argument(
        "libdir", help="Path to the conversation library directory")
    regex_parser.add_argument("expression", help="Regex expression")
    regex_parser.add_argument(
        "--fields", nargs="+", help="Field paths to apply the regex", default=["title"])
    regex_parser.add_argument(
        "--json", action="store_true", help="Output as JSON. Default: False", default=False)
    regex_parser.add_argument(
        "--indices", type=str, nargs="+", default=None,
        help="Indices of conversations to include. Supports ranges. Default: all")
    regex_parser.add_argument(
        "--indices-only", action="store_true",
        help="Only show matching indices without other fields (useful for scripting)")

    # Subcommand: conv-stats
    tree_parser = subparsers.add_parser(
        "conv-stats", help="Compute conversation tree statistics")
    tree_parser.add_argument(
        "libdir", help="Path to the conversation library directory")
    tree_parser.add_argument(
        "index", type=int, help="Index of conversation tree")
    tree_parser.add_argument(
        "--json", action="store_true", help="Output as JSON. Default: False")
    tree_parser.add_argument("--payload", action="store_true",
                             help="Show payload in the output, otherwise just show a short preview. Default: False")

    # Subcommand: tree
    tree_parser = subparsers.add_parser(
        "tree", help="Conversation tree visualization")
    tree_parser.add_argument(
        "libdir", help="Path to the conversation library directory")
    tree_parser.add_argument(
        "index", type=int, help="Index of conversation tree to visualize")
    tree_parser.add_argument("--label-fields", nargs="+",
                             type=str, default=['id', 'message.content.parts'],
                             help="When showing the tree, use this field as the node's label")
    tree_parser.add_argument("--label-lambda", type=str, default=None,
                             help="Lambda function to apply to a node to determine its label")
    tree_parser.add_argument(
        "--truncate", type=int, default=8, help="Truncate each field to this length. Default: 8")

    # Subcommand: conv
    conv_parser = subparsers.add_parser(
        "conv", help="Print conversation based on a particular node id. Defaults to using `current_node` for the corresponding conversation tree.")
    conv_parser.add_argument(
        "libdir", help="Path to the conversation library directory")
    conv_parser.add_argument(
        "index", type=int, help="Index of conversation tree to retrieve")
    conv_parser.add_argument(
        "--node", default=None, help="Node id that indicates the terminal node of a conversation path")
    conv_parser.add_argument(
        "--json", action="store_true", help="Output as JSON")
    conv_parser.add_argument("--msg-limit", type=int, default=1000,
                             help="Limit the number of messages to display. Default: 1000")
    conv_parser.add_argument("--msg-roles", type=str, nargs="+", default=[
                             "user", "assistant"], help="Roles to include in message output. Default: user, assistant")
    conv_parser.add_argument("--msg-start-index", type=int, default=0,
                             help="Start index for messages to display. Default: 0")
    conv_parser.add_argument("--msg-end-index", type=int, default=-1,
                             help="End index for messages to display. Default: -1 (end of list). Use negative values to count from the end.")

    # Subcommand: remove
    remove_parser = subparsers.add_parser(
        "remove", help="Remove a conversation from the ctk lib")
    remove_parser.add_argument(
        "libdir", help="Path to the conversation library directory")
    remove_parser.add_argument(
        "indices", type=str, nargs="+", 
        help="Indices of conversations to remove. Supports individual indices (0, 5), "
             "ranges (1:10), negative indices (-1 for last), and end-relative indices with ~ "
             "(~5 means '5th from end'). Examples: 0 1:10 -1 ~5:~1")

    # Subcommand: export (with subcommands for different formats)
    export_parser = subparsers.add_parser(
        "export", help="Export conversations from the ctk lib")
    export_parser.add_argument(
        "libdir", help="Path to the conversation library directory")
    
    # Create subparsers for different export formats
    export_formats = export_parser.add_subparsers(
        dest="format", help="Export format", required=True)
    
    # Markdown export format
    markdown_parser = export_formats.add_parser(
        "markdown", help="Export conversations as Markdown files")
    markdown_parser.add_argument(
        "--indices", type=str, nargs="+", default=None,
        help="Indices of conversations to export. Supports individual indices (0, 5), "
             "ranges (1:10), negative indices (-1 for last), and end-relative indices with ~ "
             "(~5 means '5th from end'). Examples: 0 1:10 -1 ~5:~1. Default: all")
    markdown_parser.add_argument(
        '-o', '--output-dir', type=str, help='Output directory for markdown files (default: auto-generated)', default=None)
    markdown_parser.add_argument(
        '--no-metadata', action='store_true', default=False, 
        help='Do not include metadata in output. Default: False')
    markdown_parser.add_argument(
        '--all-conversation-paths', action='store_true', default=False,
        help='Export all conversation paths. Default: False')
    markdown_parser.add_argument(
        '--msg-limit', type=int, default=None,
        help='Limit the number of messages to export. Default: None (all messages)')
    markdown_parser.add_argument(
        '--msg-roles', type=str, nargs="+", default=["user", "assistant"],
        help='Roles to include in message output. Default: user, assistant')
    markdown_parser.add_argument(
        '--msg-start-index', type=int, default=0,
        help='Start index for messages to export. Default: 0')
    markdown_parser.add_argument(
        '--msg-end-index', type=int, default=-1,
        help='End index for messages to export. Default: -1 (end of list)')
    
    # JSON export format
    json_parser = export_formats.add_parser(
        "json", help="Export conversations as JSON files")
    json_parser.add_argument(
        "--indices", type=str, nargs="+", default=None,
        help="Indices of conversations to export. Supports individual indices (0, 5), "
             "ranges (1:10), negative indices (-1 for last), and end-relative indices with ~ "
             "(~5 means '5th from end'). Examples: 0 1:10 -1 ~5:~1. Default: all")
    json_parser.add_argument(
        '-o', '--output-dir', type=str, default=None,
        help='Output directory for JSON files (default: auto-generated)')
    json_parser.add_argument("--all-conversation-paths", action='store_true', default=False,
                                help="Export all conversation paths. Default: False")
    json_parser.add_argument(
        '--msg-limit', type=int, default=None,
        help='Limit the number of messages to export. Default: None (all messages)')
    json_parser.add_argument(
        '--msg-roles', type=str, nargs="+", default=["user", "assistant"],
        help='Roles to include in message output. Default: user, assistant')
    json_parser.add_argument(
        '--msg-start-index', type=int, default=0,
        help='Start index for messages to export. Default: 0')
    json_parser.add_argument(
        '--msg-end-index', type=int, default=-1,
        help='End index for messages to export. Default: -1 (end of list)')
    
    # ZIP export format
    zip_parser = export_formats.add_parser(
        "zip", help="Export conversations as ZIP archive")
    zip_parser.add_argument(
        "--indices", type=str, nargs="+", default=None,
        help="Indices of conversations to export. Supports individual indices (0, 5), "
             "ranges (1:10), negative indices (-1 for last), and end-relative indices with ~ "
             "(~5 means '5th from end'). Examples: 0 1:10 -1 ~5:~1. Default: all")
    zip_parser.add_argument(
        '-o', '--output-file', type=str, default=None,
        help='Output ZIP file path (default: auto-generated)')
    zip_parser.add_argument(
        '--compression-level', type=int, default=9, choices=range(0, 10),
        help='ZIP compression level (0-9). Default: 9')
    
    # CTK export format
    ctk_parser = export_formats.add_parser(
        "ctk", help="Export conversations as CTK library")
    ctk_parser.add_argument(
        "--indices", type=str, nargs="+", default=None,
        help="Indices of conversations to export. Supports individual indices (0, 5), "
             "ranges (1:10), negative indices (-1 for last), and end-relative indices with ~ "
             "(~5 means '5th from end'). Examples: 0 1:10 -1 ~5:~1. Default: all")
    ctk_parser.add_argument(
        '-o', '--output-dir', type=str, default=None,
        help='Output directory for CTK library (default: auto-generated)')
    ctk_parser.add_argument(
        '--overwrite', action='store_true',
        help='Overwrite existing files. Default: False')

    # Subcommand: list
    list_parser = subparsers.add_parser(
        "list", help="List conversations in the ctk lib")
    list_parser.add_argument("libdir", help="Path to the ctk library")
    list_parser.add_argument("--indices", nargs="+", default=None,
                             type=str, help="Indices of conversations to list. Supports individual indices (0, 5), "
                                            "ranges (1:10), negative indices (-1 for last), and end-relative indices with ~ "
                                            "(~5 means '5th from end'). Examples: 0 1:10 -1 ~5:~1. Default: all")
    list_parser.add_argument("--fields", nargs="+", default=[
                             "title"], help="Path fields to include in the output")
    list_parser.add_argument(
        "--json", action="store_true", help="Output as JSON. Default: False")
    
    # Subcommand: merge (union, intersection, difference)
    merge_parser = subparsers.add_parser(
        "merge", help="Merge multiple ctk libs into one")
    merge_parser.add_argument("operation", choices=["union", "intersection", "difference"],
                              help="Type of merge operation")
    merge_parser.add_argument("libdirs", nargs="+",
                              help="List of library directories")
    merge_parser.add_argument(
        "-o", "--output", required=True, help="Output library directory")

    # Subcommand: jmespath
    jmespath_parser = subparsers.add_parser(
        "jmespath", help="Run a JMESPath query on the ctk lib")
    jmespath_parser.add_argument(
        "libdir", help="Path to the conversation library directory")
    jmespath_parser.add_argument("query", help="JMESPath expression")

    # Subcommand: purge
    purge_parser = subparsers.add_parser(
        'purge', help='Purge dead links from the conversation library')
    purge_parser.add_argument(
        'libdir', type=str, help='Directory of the ctk library to purge')

    # Subcommand: web
    web_parser = subparsers.add_parser(
        'web', help='View a conversation in the OpenAI chat interface')
    web_parser.add_argument(
        'libdir', type=str, help='Directory of the ctk library to visit')
    web_parser.add_argument('index', type=int, nargs='+',
                            help='Indices of the conversations to view in the browser')

    # Subcommand: about
    about_parser = subparsers.add_parser(
        'about', help='Print information about ctk')

    # Subcommand: filter
    filter_parser = subparsers.add_parser(
        "filter", help="Filter conversations with user-friendly criteria")
    filter_parser.add_argument(
        "libdir", help="Path to the conversation library directory")
    filter_parser.add_argument(
        "--after", type=str, help="Only include conversations after this date (YYYY-MM-DD)")
    filter_parser.add_argument(
        "--before", type=str, help="Only include conversations before this date (YYYY-MM-DD)")
    filter_parser.add_argument(
        "--model", type=str, help="Only include conversations using this model")
    filter_parser.add_argument(
        "--contains", type=str, help="Only include conversations containing this text")
    filter_parser.add_argument(
        "--min-messages", type=int, help="Only include conversations with at least this many messages")
    filter_parser.add_argument(
        "--max-messages", type=int, help="Only include conversations with at most this many messages")
    filter_parser.add_argument(
        "--sort", type=str, default="create_time", choices=["create_time", "update_time", "title"],
        help="Sort by this field. Default: create_time")
    filter_parser.add_argument(
        "--reverse", action="store_true", help="Sort in reverse order. Default: False")
    filter_parser.add_argument(
        "--indices", type=str, nargs="+", default=None,
        help="Indices of conversations to include. Supports ranges. Default: all")
    filter_parser.add_argument(
        "--fields", nargs="+", default=["title", "create_time"], 
        help="Path fields to include in the output. Default: title, create_time")
    filter_parser.add_argument(
        "--json", action="store_true", help="Output as JSON instead of a table")
    filter_parser.add_argument(
        "--show-indices-only", action="store_true", 
        help="Only show matching indices without other fields (useful for scripting)")
    filter_parser.add_argument(
        "--cumulative", action="store_true",
        help="For time-based filters, include all conversations up to the specified date")

    args = parser.parse_args()

    if args.command == "list":
        # Load conversations to get length for resolving indices
        convs = load_conversations(args.libdir)
        # Use the resolve_indices function to convert string indices to integers
        indices = resolve_indices(args, convs) if args.indices else None
        list_conversations(args.libdir, args.fields, indices, args.json)

    elif args.command == "search":
        convs = load_conversations(args.libdir)
        indices = resolve_indices(args, convs) if args.indices else None

        results = query_conversations_search(
            convs, indices, args.expression, args.fields)

        if not args.indices_only:
            new_results = []
            for result in results:
                title = convs[result]["title"]
                new_results.append({"index": result, "title": title})
            results = new_results

        if args.json:
            console.print(JSON(json.dumps(results, indent=2)))
        else:
            # Print the results in a table format
            console.print("[bold green]Search Results:[/bold green]")
            print_json_as_table(results, "Search Results")
            

    elif args.command == "remove":
        # Load conversations to get length for resolving indices
        convs = load_conversations(args.libdir)
        indices = resolve_indices(args, convs)
        # Sort in reverse to preserve the correct indices while removing
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(convs):
                del convs[index]
        save_conversations(args.libdir, convs, overwrite=True)
        console.print(f"[green]Removed {len(indices)} conversations.[/green]")

    elif args.command == "filter":
        from .filter_conv import filter_conversations
        filter_conversations(args)

    elif args.command == "export":
        convs = load_conversations(args.libdir)
        indices = resolve_indices(args, convs)
        
        if args.format == "zip":
            export_conversations_to_zip(
                libdir=args.libdir, indices=indices, zipfile_name=args.output_file,
                compression_level=args.compression_level)
        elif args.format == "ctk":
            export_conversations_to_ctk(
                libdir=args.libdir, indices=indices, output_dir=args.output_dir,
                overwrite=args.overwrite)
        elif args.format == "json":
            export_conversations_to_json(
                libdir=args.libdir, indices=indices, output_dir=args.output_dir,
                all_conversation_paths=args.all_conversation_paths,
                msg_limit=args.msg_limit, msg_roles=args.msg_roles,
                msg_start_index=args.msg_start_index, msg_end_index=args.msg_end_index)
        else:  # args.format == "markdown"
            export_conversations_to_markdown(
                libdir=args.libdir, indices=indices, output_dir=args.output_dir,
                metadata=not args.no_metadata, all_conversation_paths=args.all_conversation_paths,
                msg_limit=args.msg_limit, msg_roles=args.msg_roles,
                msg_start_index=args.msg_start_index, msg_end_index=args.msg_end_index)

    elif args.command == "jmespath":
        result = query_conversations_jmespath(args.libdir, args.query)
        # pretty print
        console.print(JSON(json.dumps(result, indent=2)))

    elif args.command == "conv-stats":
        get_conversation_tree_stats(args.libdir, args.index, args.payload, args.json)

    elif args.command == "tree":
        convs = load_conversations(args.libdir)
        if args.index >= len(convs):
            console.print(f"[red]Error: Index {index} out of range.[/red]")
            sys.exit(1)
        conv = convs[args.index]
        tree_map = conv.get("mapping", {})
        t = AlgoTree.FlatForest(tree_map)

        def generate_label_fn():
            paths = []
            for field in args.label_fields:
                paths.append(field.split('.'))

            def label_fn(node):
                results = []
                for path in paths:
                    value = path_value(node.payload, path)
                    value = value[:args.truncate]
                    results.append(value)

                label = " ".join(results)
                return label

            return label_fn

        if args.label_lambda is None:
            label_fn = generate_label_fn()
            console.print(AlgoTree.pretty_tree(t, node_name=label_fn))
        else:
            label_fn = eval(args.label_lambda)
            label_fallback_fn = generate_label_fn()

            def wrapper_lambda(node):
                try:
                    return label_fn(node)
                except Exception as e:
                    print("Error in label_fn:", e)
                    return label_fallback_fn(node)

            # label_fn should be a function that takes a conversation node and returns a string
            console.print(AlgoTree.pretty_tree(t, node_name=wrapper_lambda))

    elif args.command == "purge":
        print("TODO: Implement purge command. This swill remove any local files that are dead links in the library.")

    elif args.command == "conv":

        convs = load_conversations(args.libdir)

        if args.index >= len(convs):
            console.print(
                f"[red]Error:[/red] Specified index [gray]{args.index}[/gray] is not in range of [green]0 to {len(convs) - 1}[/green].")
            sys.exit(1)
        
        if args.json:
            result = generate_conversation_json(convs[args.index], 
                                                terminal_node=args.node,
                                                msg_limit=args.msg_limit,
                                                msg_roles=args.msg_roles,
                                                msg_start_index=args.msg_start_index,
                                                msg_end_index=args.msg_end_index)
            
            console.print(JSON(json.dumps(result, indent=2)))
        else:
            pretty_print_conversation(
                convs[args.index],
                terminal_node=args.node,
                msg_limit=args.msg_limit,
                msg_roles=args.msg_roles,
                msg_start_index=args.msg_start_index,
                msg_end_index=args.msg_end_index)


    elif args.command == "about":
        console.print("[bold cyan]ctk[/bold cyan]: A command-line toolkit for working with conversation trees, "
                      "typically derived from exported LLM interaction data.\n")
        console.print("[dim]Developed by:[/dim] [bold white]Alex Towell[/bold white]  \n"
                      "[dim]Contact:[/dim] [link=mailto:lex@metafunctor.com]lex@metafunctor.com[/link]  \n"
                      "[dim]Source Code:[/dim] [link=https://github.com/queelius/ctk]https://github.com/queelius/ctk[/link]\n")
        console.print("[bold]Features:[/bold]")
        console.print("• Parse and analyze LLM conversation trees.")
        console.print(
            "• Export, transform, and query structured conversation data.")
        console.print("• Visualize conversation trees and relationships.")
        console.print("• Query conversation trees using JMESPath.")
        console.print(
            "• Lightweight and designed for command-line efficiency.")
        console.print(
            "\n[bold green]Usage:[/bold green] Run `ctk --help` for available commands.")

    elif args.command == "web":
        convs = load_conversations(args.libdir)
        for idx in args.index:
            if idx < 0 or idx >= len(convs):
                console.print(
                    f"[red]Error: Index {idx} out of range.[/red]. Skipping.")
                continue

            conv = convs[idx]
            link = f"https://chat.openai.com/c/{conv['id']}"
            webbrowser.open_new_tab(link)

    elif args.command == "merge":
        ensure_libdir_structure(args.output)
        if args.operation == "union":
            union_libs(args.libdirs, args.output)
            logger.debug(f"Merged {len(args.libdirs)} libs into {args.output}")
        elif args.operation == "intersection":
            intersect_libs(args.libdirs, args.output)
            logger.debug(f"Merged {len(args.libdirs)} libs into {args.output}")
        elif args.operation == "difference":
            diff_libs(args.libdirs, args.output)
            logger.debug(f"Merged {len(args.libdirs)} libs into {args.output}")
        logger.debug(f"Merged {len(args.libdirs)} libs into {args.output}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
