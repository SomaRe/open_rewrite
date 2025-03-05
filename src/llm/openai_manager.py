import threading
import logging
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class OpenAIManager:
    def __init__(self, settings_manager):
        logging.debug('OpenAIManager.__init__ called')
        self.settings_manager = settings_manager
        self.load_settings()
        logging.debug('OpenAIManager.__init__ finished')
        
    def load_settings(self):
        logging.debug('OpenAIManager.load_settings called')
        """Load OpenAI settings from the settings manager"""
        self.api_key = self.settings_manager.get('api_key', '')
        self.base_url = self.settings_manager.get('base_url', 'https://api.openai.com/v1/')
        self.model = self.settings_manager.get('model', 'gpt-4o-mini')
        self.system_message = self.settings_manager.get('system_message', '')
        logging.debug('OpenAIManager.load_settings finished')
        
    def generate_response(self, prompt, selected_text, on_success, on_error):
        logging.debug('OpenAIManager.generate_response called')
        """Generate a response from OpenAI"""
        def run_openai_call():
            try:
                logging.debug('run_openai_call try block')
                client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                
                messages = [
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": f"{prompt}\n{selected_text}"}
                ]
                
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                )
                
                # Call the success callback with the response
                on_success(response.choices[0].message.content)
                logging.debug('run_openai_call success callback finished')
                
            except Exception as e:
                logging.error(f'OpenAI API error: {e}')
                # Call the error callback with the error
                on_error(e)
                
        # Run in a separate thread to not block the UI
        thread = threading.Thread(target=run_openai_call)
        thread.daemon = True
        thread.start()
        logging.debug('OpenAIManager.generate_response finished')
