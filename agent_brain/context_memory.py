class ContextMemory:
    def __init__(self):
        self.last_intent = None
        self.last_email = None
        self.last_event = None
        self.pending_action = None  # NEW


memory = ContextMemory()
