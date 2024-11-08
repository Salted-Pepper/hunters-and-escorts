import os
import datetime
import logging

if not os.path.exists("logs"):
    os.makedirs("logs")

from game import Game

date = datetime.date.today()

logging.basicConfig(level=logging.DEBUG, filename=os.path.join(os.getcwd(), 'logs/navy_log_' + str(date) + '.log'),
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt="%H:%M:%S", filemode='w')
logger = logging.getLogger("WORLD")
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    Game()
