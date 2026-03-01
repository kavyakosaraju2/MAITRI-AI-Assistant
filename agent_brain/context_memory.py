class Memory:
    def __init__(self):
        self.pending_action = None
        self.creds = None
        
        # NEW: conversation tracking
        self.last_user_query = None
        self.last_intent = None
        self.last_context_type = None
        self.conversation_mode = None
        self.last_email_set = None
        self.last_extracted_tasks = None
        self.last_meeting = None

memory = Memory()
