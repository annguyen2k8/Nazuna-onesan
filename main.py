import sys
import json
import asyncio
import warnings

from base import start_bot

if __name__ == '__main__':
    # Filter warnings
    warnings.filterwarnings('ignore')
    
    # Load config and start bot
    config = json.loads(open('config.json').read())
    
    # Set event loop policy for Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    start_bot(config)