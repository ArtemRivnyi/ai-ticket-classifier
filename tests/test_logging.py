# test_logging.py
import logging
import sys
import os

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    # Initialize logging like in app.py
    logging.basicConfig(level=logging.INFO)
    from classify import logger
    
    print(f"Logger level: {logger.level}")
    print(f"Handlers: {len(logger.handlers)}")
    
    # Test message
    logger.info("Test logging from classify.py")
    print("✅ Logging test completed")
    
except Exception as e:
    print(f"❌ Logging test failed: {e}")