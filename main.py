import webview
import logging
from src.app import Application

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.debug('main function called')
    app = Application()
    app.initialize()
    
    # Start the application
    webview.start(debug=True)
    logging.debug('webview.start finished')
    
if __name__ == '__main__':
    main()
    logging.debug('main script finished')
