import webview
import logging
from src.app import Application

def main():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.debug('main function called')
    app = Application()
    app.initialize()

    # Start the application
    webview.start(ssl=True)
    logger.debug('webview.start finished')

if __name__ == '__main__':
    main()
    logger = logging.getLogger(__name__)
    logger.debug('main script finished')
