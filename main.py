import sys
import webview
from src.app import Application

def main():
    app = Application()
    app.initialize()
    
    # Start the application
    webview.start(debug=True)
    
if __name__ == '__main__':
    main()