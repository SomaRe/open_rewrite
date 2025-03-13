import logging

class RewriteManager:
    def __init__(self, llm_manager, settings_manager, clipboard_handler):
        logging.debug('RewriteManager.__init__ called')
        self.llm_manager = llm_manager
        self.settings_manager = settings_manager
        self.clipboard_handler = clipboard_handler
        logging.debug('RewriteManager.__init__ finished')

    def rewrite_text(self, text, prompt, on_success, on_error):
        """Rewrite the text using the provided prompt"""
        if text.strip() == '':
            on_error('No text selected or found, please try again!')
            return

        logging.debug(f'RewriteManager.rewrite_text called with text: {text}, prompt: {prompt}')
        api_key = self.settings_manager.get('api_key')
        base_url = self.settings_manager.get('base_url')
        model = self.settings_manager.get('model')
        system_message = self.settings_manager.get('system_message')

        self.llm_manager.generate_response(api_key, base_url, model, system_message,
            prompt, text, on_success, on_error)
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

    def handle_custom_request(self, text, custom_prompt, on_success, on_error):
        """Handle custom user requests with dedicated system message"""
        if text.strip() == '':
            on_error('No text selected or found, please try again!')
            return

        logging.debug(f'Handling custom request with text: {text}, prompt: {custom_prompt}')
        
        # Get custom system message from settings
        custom_system_message = self.settings_manager.get('custom_system_message')
        
        api_key = self.settings_manager.get('api_key')
        base_url = self.settings_manager.get('base_url')
        model = self.settings_manager.get('model')

        self.llm_manager.generate_response(
            api_key=api_key,
            base_url=base_url,
            model=model,
            system_message=custom_system_message,
            prompt=custom_prompt,
            selected_text=text,
            on_success=on_success,
            on_error=on_error
        )
