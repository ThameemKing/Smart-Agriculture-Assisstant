"""GPIO interface for button input"""

import logging
import time

logger = logging.getLogger(__name__)


class GPIOInterface:
    """Handle GPIO button input"""
    
    def __init__(self, config):
        """Initialize GPIO interface
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.button_pin = config.get('button_pin', 17)
        self.debounce_time = config.get('debounce_time', 0.2)
        self.last_pressed = 0
        
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setup(self.button_pin, self.GPIO.IN)
            logger.info(f"GPIO initialized on pin {self.button_pin}")
        except ImportError:
            logger.warning("RPi.GPIO not available (not running on Raspberry Pi)")
            self.GPIO = None
    
    def wait_for_button(self, timeout=None):
        """Wait for button press
        
        Args:
            timeout: Timeout in seconds (None for infinite)
            
        Returns:
            True if button pressed, False if timeout
        """
        try:
            if not self.GPIO:
                logger.warning("GPIO not available")
                return False
            
            start_time = time.time()
            while True:
                if timeout and (time.time() - start_time) > timeout:
                    return False
                
                if self.GPIO.input(self.button_pin) == self.GPIO.LOW:
                    current_time = time.time()
                    if current_time - self.last_pressed > self.debounce_time:
                        self.last_pressed = current_time
                        logger.info("Button pressed")
                        return True
                
                time.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Error waiting for button: {e}")
            return False
    
    def cleanup(self):
        """Cleanup GPIO"""
        if self.GPIO:
            self.GPIO.cleanup()
            logger.info("GPIO cleaned up")
