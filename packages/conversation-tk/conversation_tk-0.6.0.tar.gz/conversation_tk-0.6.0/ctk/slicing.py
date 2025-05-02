import argparse
from rich.console import Console
import logging

console = Console()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def parse_index_range(arg_value):
    """
    Parse index specifications including ranges like '1:10' and individual indices.
    Supports full Python slicing syntax: start:stop:step
    
    Examples:
    - '5' -> [5]
    - '1:10' -> [1, 2, 3, 4, 5, 6, 7, 8, 9]
    - '1:10:2' -> [1, 3, 5, 7, 9]
    - ':5' -> [0, 1, 2, 3, 4]
    - '5:' -> [5, 6, 7, ...] (interpreted at runtime)
    - '-5:' -> last 5 elements to the end
    """
    try:
        # Check if the argument is a simple integer
        return [int(arg_value)]
    except ValueError:
        # It's not a simple integer, try to parse it as a range
        if ':' in arg_value:
            parts = arg_value.split(':')
            if len(parts) == 2:
                # Handle start:stop format
                start = int(parts[0]) if parts[0] else None
                stop = int(parts[1]) if parts[1] else None
                return {'slice': (start, stop, None)}
            elif len(parts) == 3:
                # Handle start:stop:step format
                start = int(parts[0]) if parts[0] else None
                stop = int(parts[1]) if parts[1] else None
                step = int(parts[2]) if parts[2] else None
                return {'slice': (start, stop, step)}
            else:
                raise argparse.ArgumentTypeError(f"Invalid range format: {arg_value}")
        else:
            raise argparse.ArgumentTypeError(f"Invalid index or range: {arg_value}")

def parse_indices(arg_values):
    """
    Parse a list of index specifications into a list of indices.
    Handles both individual indices and range specifications.
    
    @param arg_values: List of index specifications
    @return: List of indices
    """
    indices = []
    slices = []
    
    # First pass: collect all individual indices and slices
    for arg in arg_values:
        result = parse_index_range(arg)
        if isinstance(result[0], dict) and 'slice' in result[0]:
            slices.append(result[0]['slice'])
        else:
            indices.extend(result)
    
    return {'indices': indices, 'slices': slices}

def resolve_indices(args, convs):
    """
    Resolve index arguments into a concrete list of indices.
    Handles both individual indices and range specifications.
    
    @param args: The parsed arguments containing indices
    @param convs: The conversation list to determine length for slices
    @return: List of resolved indices
    """
    if not hasattr(args, 'indices') or args.indices is None:
        return list(range(len(convs)))
    
    # Parse the index specifications
    parsed = []
    for arg in args.indices:
        # Handle special "end-relative" notation e.g., "~5" means "from the end minus 5"
        if arg.startswith('~'):
            try:
                offset = int(arg[1:])
                idx = len(convs) - offset
                parsed.append(idx)
                continue
            except ValueError:
                pass
                
        try:
            # Try as a simple integer
            idx = int(arg)
            # Handle negative index for individual integers
            if idx < 0:
                idx = len(convs) + idx  # Convert to positive index
            parsed.append(idx)
        except ValueError:
            # Try as a slice
            if ':' in arg:
                parts = arg.split(':')
                
                # Handle special "end-relative" notation in slices (~5:~1)
                try:
                    if parts[0].startswith('~'):
                        parts[0] = str(len(convs) - int(parts[0][1:]))
                    if len(parts) >= 2 and parts[1] and parts[1].startswith('~'):
                        parts[1] = str(len(convs) - int(parts[1][1:]))
                except (ValueError, IndexError):
                    pass
                
                start = int(parts[0]) if parts[0] else 0
                
                if len(parts) >= 2:
                    stop = int(parts[1]) if parts[1] else len(convs)
                else:
                    stop = len(convs)
                    
                step = int(parts[2]) if len(parts) == 3 and parts[2] else 1
                
                # Handle negative indices
                if start < 0:
                    start = len(convs) + start
                if stop < 0:
                    stop = len(convs) + stop
                    
                parsed.extend(range(start, stop, step))
            else:
                # Invalid format
                console.print(f"[yellow]Warning: Invalid index format '{arg}'. Skipping.[/yellow]")
    
    # Filter to valid indices
    return [i for i in parsed if 0 <= i < len(convs)]
