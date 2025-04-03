import threading
from openai import OpenAI

import logging
logger = logging.getLogger(__name__)

class OpenAIManager:
    # def __init__(self):
    #     logger.debug('OpenAIManager.__init__ called')
    #     self.settings_manager = settings_manager
    #     self.load_settings()
    #     logger.debug('OpenAIManager.__init__ finished')

    # def load_settings(self):
    #     logger.debug('OpenAIManager.load_settings called')
    #     """Load OpenAI settings from the settings manager"""
    #     self.api_key = self.settings_manager.get('api_key', '')
    #     self.base_url = self.settings_manager.get('base_url', 'https://api.openai.com/v1/')
    #     self.model = self.settings_manager.get('model', 'gpt-4o-mini')
    #     self.system_message = self.settings_manager.get('system_message', '')
    #     logger.debug('OpenAIManager.load_settings finished')

    def generate_response(self, api_key, base_url, model, system_message,
            prompt, selected_text, on_success, on_error):
        logger.debug('OpenAIManager.generate_response called')
        """Generate a response from OpenAI"""
        def run_openai_call():
            try:
                logger.debug('run_openai_call try block')
                client = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )

                messages = [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"<prompt>{prompt}</prompt>\n<text>{selected_text}</text>"}
                ]

                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                )

                reply = response.choices[0].message.content

                logger.debug(f"response: {reply[:20]+'...'}")

                # Call the success callback with the response
                on_success(reply)
                logger.debug('run_openai_call success callback finished')

            except Exception as e:
                logger.error(f'OpenAI API error: {e}')
                # Call the error callback with the error
                on_error(e)

        # Run in a separate thread to not block the UI
        thread = threading.Thread(target=run_openai_call)
        thread.daemon = True
        thread.start()
        logger.debug('OpenAIManager.generate_response finished')
