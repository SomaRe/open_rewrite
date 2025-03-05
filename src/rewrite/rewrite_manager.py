import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class RewriteManager:
    def __init__(self, llm_manager, clipboard_handler):
        logging.debug('RewriteManager.__init__ called')
        self.llm_manager = llm_manager
        self.clipboard_handler = clipboard_handler
        logging.debug('RewriteManager.__init__ finished')

    def rewrite_text(self, text, prompt, on_success, on_error):
        logging.debug(f'RewriteManager.rewrite_text called with text: {text}, prompt: {prompt}')
        """Rewrite the text using the provided prompt"""
        self.llm_manager.generate_response(prompt, text, on_success, on_error)
        logging.debug('RewriteManager.rewrite_text finished')

    def copy_result(self, text):
        logging.debug(f'RewriteManager.copy_result called with text: {text}')
        """Copy the rewritten text to the clipboard"""
        self.clipboard_handler.copy_text(text)
        logging.debug('RewriteManager.copy_result finished')

    def replace_text(self, text):
        logging.debug(f'RewriteManager.replace_text called with text: {text}')
        """Replace the selected text with the rewritten text"""
        self.clipboard_handler.replace_text(text)
        logging.debug('RewriteManager.replace_text finished')
