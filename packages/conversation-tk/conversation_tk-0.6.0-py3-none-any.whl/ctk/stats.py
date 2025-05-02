import logging
import json
from ctk.utils import load_conversations, print_json_as_table
import AlgoTree
from rich.console import Console

logger = logging.getLogger(__name__)

console = Console()

def get_conversation_tree_stats(libdir, index, payload=False, json_output=False):
        convs = load_conversations(libdir)
        if index >= len(convs):
            console.print(f"[red]Error: Index {index} out of range.[/red]")
        conv = convs[index]

        cur_node_name = conv.get("current_node")

        tree_map = conv.get("mapping")
        t = AlgoTree.FlatForest(tree_map)
        cur_node = t.node(cur_node_name)
        ancestors = AlgoTree.utils.ancestors(cur_node)
        cur_conv_ids = [node.name for node in ancestors] + [cur_node_name]

        stats = {}
        metadata = conv
        metadata.pop("mapping", None)

        stats['metadata'] = metadata
        stats["num_paths"] = len(AlgoTree.utils.leaves(t.root))
        stats["num_nodes"] = AlgoTree.utils.size(t.root)
        stats["max_path"] = AlgoTree.utils.height(t.root)
        numeric_ids = {}
        the_id = 0
        for node in t.nodes():
            numeric_ids[node.name] = the_id
            the_id += 1

        stats['tree'] = []
        def walk(node):
            node_dict = {}
            
            # Format siblings as a string
            siblings = [numeric_ids[node.name] for node in AlgoTree.utils.siblings(node)]
            if siblings:
                node_dict["siblings"] = ' '.join(map(str, siblings))
            else:
                node_dict["siblings"] = "none"
            
            # Format children as a string
            children = [numeric_ids[child.name] for child in node.children]
            if children:
                node_dict["children"] = ' '.join(map(str, children))
            else:
                node_dict["children"] = "none"
            
            # Remove redundant num_siblings and num_children since they're in the string now
            node_dict["is_leaf"] = AlgoTree.utils.is_leaf(node)
            node_dict["is_root"] = AlgoTree.utils.is_root(node)
            node_dict["is_current"] = node.name in cur_conv_ids
            node_dict["depth"] = AlgoTree.utils.depth(node)
            node_dict["num_descendants"] = AlgoTree.utils.size(node)
            node_dict["num_ancestors"] = len(AlgoTree.utils.ancestors(node))
            node_dict["parent_id"] = numeric_ids.get(
                node.parent.name) if node.parent else "none"
            node_dict["id"] = numeric_ids[node.name]
            
            if node.payload and node.payload.get('message'):
                
                if not payload:
                    msg = node.payload['message']
                    if msg.get('content') and msg['content'].get('parts'):
                        content = msg['content']['parts']
                        if content and isinstance(content[0], str):
                            preview = content[0][:50].replace('\n', ' ')
                            if len(content[0]) > 50:
                                preview += "..."
                            node_dict["preview"] = preview
                    
                else:
                    node_dict['payload'] = node.payload['message']

            stats["tree"].append(node_dict)
            for child in node.children:
                walk(child)

        walk(t.root)
        if json_output:
            print(json.dumps(stats, indent=2, ensure_ascii=True))
        else:
            print_json_as_table(stats, table_title=conv['title'])

