#Author: Diego Sisalima

from AssisBot import AssisBot
import time
import sys

def main():
    Bot = AssisBot()
    Connection = Bot.Telegram
    Connection.update_bot_info().wait()
    option = sys.argv[1] if len(sys.argv)>1 else 'x'
    while option != '0':
        if option == '1':
            Bot.startToListen()
        elif option == '2':
            Bot.stopToListen()
        elif option == '0':
            Bot.stopToListen()
            exit()
        print('------------Menu principal AssisBot--------------')
        print('1. Start NocBot')
        print('2. Pause NocBot')
        print('0. Exit')
        option = input()


if __name__ == "__main__":
    main()
