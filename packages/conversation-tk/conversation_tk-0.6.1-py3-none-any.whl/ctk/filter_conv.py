import datetime
import time
import json
import jmespath
from rich.console import Console
from .slicing import resolve_indices
from .utils import load_conversations, print_json_as_table

console = Console()

def filter_conversations(args):
    """
    Filter conversations based on various criteria and display the results.

    Args:
        args (Namespace): Command-line arguments containing filter options.
    """
    # Load all conversations
    convs = load_conversations(args.libdir)
    
    # Track original indices throughout the filtering process
    filtered_items = []  # Will contain (index, conv) pairs
    
    # Apply indices filter if specified
    if args.indices:
        indices = resolve_indices(args, convs)
        filtered_items = [(i, convs[i]) for i in indices if 0 <= i < len(convs)]
    else:
        filtered_items = list(enumerate(convs))  # (index, conversation) pairs
    
    # Apply date filters
    if args.after:
        after_timestamp = int(datetime.datetime.strptime(args.after, "%Y-%m-%d").timestamp())
        filtered_items = [(idx, conv) for idx, conv in filtered_items 
                          if conv.get("create_time", 0) >= after_timestamp]
        
    if args.before:
        before_timestamp = int(datetime.datetime.strptime(args.before, "%Y-%m-%d").timestamp())
        filtered_items = [(idx, conv) for idx, conv in filtered_items 
                          if conv.get("create_time", 0) <= before_timestamp]
    
    # Apply model filter
    if args.model:
        filtered_items = [(idx, conv) for idx, conv in filtered_items 
                         if args.model.lower() in conv.get("default_model_slug", "").lower()]
    
    # Apply text content filter
    if args.contains:
        text_matches = []
        search_term = args.contains.lower()
        
        for idx, conv in filtered_items:
            # Check title first (fastest)
            if search_term in conv.get("title", "").lower():
                text_matches.append((idx, conv))
                continue
                
            # Check message content if needed
            found = False
            for node_id, node in conv.get("mapping", {}).items():
                message = node.get("message", {})
                if message.get("content", {}).get("parts"):
                    for part in message["content"]["parts"]:
                        if isinstance(part, str) and search_term in part.lower():
                            found = True
                            break
                if found:
                    break
            
            if found:
                text_matches.append((idx, conv))
        
        filtered_items = text_matches
    
    # Apply message count filters
    if args.min_messages:
        filtered_items = [(idx, conv) for idx, conv in filtered_items 
                         if len(conv.get("mapping", {})) >= args.min_messages]
    
    if args.max_messages:
        filtered_items = [(idx, conv) for idx, conv in filtered_items 
                         if len(conv.get("mapping", {})) <= args.max_messages]
    
    # Sort the results
    if args.sort:
        filtered_items.sort(key=lambda item: item[1].get(args.sort, ""), reverse=args.reverse)
    
    # Format and display results
    result_data = []
    for idx, conv in filtered_items:
        entry = {"index": idx}
        for field in args.fields:
            value = jmespath.search(field, conv)
            
            # Format timestamps consistently
            if isinstance(value, (int, float)) and (field.endswith('_time')):
                value = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(value))
                
            entry[field] = value
        result_data.append(entry)

    # Output in requested format
    if args.show_indices_only:
        # Return indices as JSON array of integers
        indices = [idx for idx, _ in filtered_items]
        if args.json:
            console.print(json.dumps(indices))
        else:
            # For better command line usability, still allow plain text output by default
            console.print(" ".join(map(str, indices)))
    elif args.json:
        console.print(json.dumps(result_data, indent=2, ensure_ascii=False))
    else:
        title = f"Filtered Conversations ({len(filtered_items)} of {len(convs)})"
        print_json_as_table(result_data, table_title=title)