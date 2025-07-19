from meshtastic import SerialInterface

def fetch_mesh_data(port):
    interface = SerialInterface(port)
    return {"nodes": len(interface.nodes)}  # Example data
