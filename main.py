#Author: Diego Sisalima

from AssisBot import AssisBot
import time

def main():
    Bot = AssisBot()
    Connection = Bot.Telegram
    Connection.update_bot_info().wait()
    option = 'x'
    while option != '0':
        print('------------Menu principal AssisBot--------------')
        print('1. Start NocBot')
        print('2. Pause NocBot')
        print('0. Exit')
        option = input()
        if option == '1':
            Bot.startToListen()
        elif option == '2':
            Bot.stopToListen()
        elif option == '0':
            Bot.stopToListen()
            exit()

if __name__ == "__main__":
    main()
