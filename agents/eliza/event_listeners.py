
import asyncio

class ElizaEventListeners:
    def __init__(self, mesh_client):
        self.mesh_client = mesh_client

    async def on_node_join(self, event):
        print(f"[Node Event] Node joined: {event['node_id']}")

    async def on_node_leave(self, event):
        print(f"[Node Event] Node left: {event['node_id']}")

    async def on_node_health(self, event):
        print(f"[Node Health] {event}")

    async def on_topology_change(self, event):
        print(f"[Network] Topology changed: {event}")

    async def on_service_event(self, event):
        print(f"[Service Event] {event}")

    async def on_security_event(self, event):
        print(f"[Security] {event}")

    async def on_data_event(self, event):
        print(f"[Data] {event}")

    async def on_user_command(self, event):
        print(f"[User Command] {event}")

    def register(self):
        # Register all handlers with your mesh_client/event bus
        self.mesh_client.on("node_join", self.on_node_join)
        self.mesh_client.on("node_leave", self.on_node_leave)
        self.mesh_client.on("node_health", self.on_node_health)
        self.mesh_client.on("topology_change", self.on_topology_change)
        self.mesh_client.on("service_event", self.on_service_event)
        self.mesh_client.on("security_event", self.on_security_event)
        self.mesh_client.on("data_event", self.on_data_event)
        self.mesh_client.on("user_command", self.on_user_command)
