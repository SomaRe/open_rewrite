import sys
import webview
import os
from src.app import Application
from src.utils.resource_path import resource_path

def main():
    app = Application()
    app.initialize()
    
    # Start the application
    webview.start(debug=True)
    
if __name__ == '__main__':
    main()