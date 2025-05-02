"""Utility functions for the mlfastflow package."""

def validate_flow(flow):
    """Validate the structure of a flow.
    
    Args:
        flow: The flow to validate.
        
    Returns:
        bool: True if the flow is valid, False otherwise.
    """
    if not hasattr(flow, 'nodes') or not isinstance(flow.nodes, list):
        return False
    
    # Check if all nodes have a process method
    for node in flow.nodes:
        if not hasattr(node, 'process') or not callable(node.process):
            return False
    
    return True
