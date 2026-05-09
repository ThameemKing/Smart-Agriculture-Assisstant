"""LCD display interface"""

import logging
import time

logger = logging.getLogger(__name__)


class LCDDisplay:
    """Handle 16x2 LCD I2C display"""
    
    def __init__(self, config):
        """Initialize LCD display
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.address = config.get('lcd_address', 0x27)
        self.cols = config.get('lcd_cols', 16)
        self.rows = config.get('lcd_rows', 2)
        
        try:
            from adafruit_circuitpython_charlcd import character_lcd_i2c
            import board
            import busio
            
            i2c = busio.I2C(board.SCL, board.SDA)
            self.lcd = character_lcd_i2c.Character_LCD_I2C(
                i2c, self.cols, self.rows, self.address
            )
            self.lcd.clear()
            logger.info("LCD initialized successfully")
        except ImportError:
            logger.warning("adafruit_circuitpython_charlcd not available")
            self.lcd = None
    
    def display(self, message, duration=None):
        """Display message on LCD
        
        Args:
            message: Message to display
            duration: Duration to display (None for persistent)
        """
        try:
            if not self.lcd:
                logger.info(f"[LCD] {message}")
                return
            
            self.lcd.clear()
            
            # Split message into lines if needed
            lines = message.split('\n')[:self.rows]
            for i, line in enumerate(lines):
                if i < self.rows:
                    # Truncate if too long
                    line = line[:self.cols]
                    self.lcd.cursor_position(0, i)
                    self.lcd.print(line)
            
            if duration:
                time.sleep(duration)
                self.lcd.clear()
            
            logger.info(f"LCD displayed: {message}")
            
        except Exception as e:
            logger.error(f"Error displaying on LCD: {e}")
    
    def clear(self):
        """Clear LCD display"""
        if self.lcd:
            self.lcd.clear()
    
    def cleanup(self):
        """Cleanup LCD"""
        try:
            if self.lcd:
                self.lcd.clear()
                logger.info("LCD cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up LCD: {e}")
