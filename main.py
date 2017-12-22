#Author: Diego Sisalima

from AssisBot import AssisBot
from optparse import OptionParser
import logging
import time

def main():
    parser = OptionParser()
    parser.add_option('-a','--auto',dest='auto_init',help='Iniciar automaticamente Bot', action='store_true', default=False)
    parser.add_option('-v','--verbose',dest='verbose',help='Opción logs info en consola', action='store_true', default=False)
    (options, args) = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(asctime)s:%(message)s')
    else:
        logging.basicConfig(filename='LOGS.log',level=logging.DEBUG, format='%(levelname)s:%(asctime)s:%(message)s')

    Bot = AssisBot()
    Connection = Bot.Telegram
    Connection.update_bot_info().wait()
    option = '1' if options.auto_init else '-1'

    while option != '0':
        if option == '1':
            logging.info('Enter to opcion 1')
            Bot.startToListen()
        elif option == '2':
            logging.info('Enter to opcion 2')
            Bot.stopToListen()
        elif option == '0':
            logging.info('Exit program')
            Bot.stopToListen()
            exit()
        print('------------Menu principal AssisBot--------------')
        print('1. Start NocBot')
        print('2. Pause NocBot')
        print('0. Exit')
        option = input()

if __name__ == "__main__":
    main()
