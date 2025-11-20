
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.append(os.getcwd())

try:
    from providers.multi_provider import MultiProvider
    print("Import successful")
    
    classifier = MultiProvider()
    print("Initialization successful")
    
    ticket = "Nice to have: add animation to the loading screen"
    print(f"Classifying: {ticket}")
    
    result = classifier.classify(ticket)
    print(f"Result: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
