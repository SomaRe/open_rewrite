class RewriteManager:
    def __init__(self, llm_manager, clipboard_handler):
        self.llm_manager = llm_manager
        self.clipboard_handler = clipboard_handler

    def rewrite_text(self, text, prompt, on_success, on_error):
        """Rewrite the text using the provided prompt"""
        self.llm_manager.generate_response(prompt, text, on_success, on_error)

    def copy_result(self, text):
        """Copy the rewritten text to the clipboard"""
        self.clipboard_handler.copy_text(text)

    def replace_text(self, text):
        """Replace the selected text with the rewritten text"""
        self.clipboard_handler.replace_text(text)
