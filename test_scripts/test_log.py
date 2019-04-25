import logging
import otherMod
 
def main():
    """
    The main entry point of the application
    """
    
    logging.basicConfig(filename="mySnake.log", level=logging.INFO)
    logging.info("Program started")
    result = otherMod.add(7, 8)
    logging.info("Done!")
 
if __name__ == "__main__":
    main()

'''
import logging
 
logging.basicConfig(filename="sample.log", level=logging.INFO)
log = logging.getLogger("ex")
 
try:
    raise RuntimeError
except RuntimeError:
    log.exception("Error!")
'''

'''
import logging
 
# add filemode="w" to overwrite
logging.basicConfig(filename="sample.log", filemode="w", level=logging.INFO)
 
logging.debug("This is a debug message")
logging.info("Informational message")
logging.error("An error has happened!")
'''