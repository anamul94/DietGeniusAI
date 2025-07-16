active_connections = {}

def add_connection(session_id: str):
    """Add a new connection to the active connections."""
    active_connections[session_id] = True
    
def remove_connection(session_id: str):
    """Remove a connection from the active connections."""
    if session_id in active_connections:
        del active_connections[session_id]