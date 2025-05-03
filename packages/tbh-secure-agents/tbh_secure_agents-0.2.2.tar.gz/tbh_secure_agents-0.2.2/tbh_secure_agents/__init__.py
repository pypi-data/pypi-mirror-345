# tbh_secure_agents - Secure Multi-Agent Framework by TBH.AI
# Author: Saish

import logging
import sys

__version__ = "0.2.2"

# --- Basic Logging Setup ---
# Configure logging to output to console
logging.basicConfig(
    level=logging.INFO, # Set default level (e.g., INFO, DEBUG, WARNING)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout # Log to standard output
)
# You might want to make this configurable later (e.g., file logging, different levels)
# --- /Basic Logging Setup ---


# Expose core classes
from .agent import Expert
from .task import Operation
from .crew import Squad

__all__ = ['Expert', 'Operation', 'Squad', '__version__']
