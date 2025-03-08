import webview
import logging
import os
from dotenv import load_dotenv
from src.app import Application

load_dotenv()

def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.debug('main function called')
    app = Application()
    app.initialize()

    use_debug = os.environ.get('WEBVIEW_DEBUG', 'False').lower() == 'true'

    # Start the application
    if use_debug:
        logger.debug('Starting in debug mode')
        webview.start(debug=True)
    else:
        logger.debug('Starting in production mode')
        webview.start(ssl=True)
    logger.debug('webview.start finished')

if __name__ == '__main__':
    main()
    logger = logging.getLogger(__name__)
    logger.debug('main script finished')
