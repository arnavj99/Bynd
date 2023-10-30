# Import necessary libraries
import pandas as pd
from openbb_terminal.sdk import openbb

# Set up API key for openbb
def setup_openbb_key():
    openbb.keys.fmp(key='7DmAtMm8HX92DK5aLmWyGKoav9nwoNhL', persist=True)
    # openbb.keys.av(key = 'L2UCH15H6QKUXZPY', persist = True)


