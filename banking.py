import random
import sqlite3


class Card:
    def __init__(self, card_nr, pin_nr, money):
        self.card = card_nr
        self.pin = pin_nr
        self.balance = money


conn = sqlite3.connect("card.s3db")  # CREATE DATABASE
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, "
            "number TEXT, pin TEXT, balance INTEGER);")
conn.commit()


def luhn(check_sum):  # gives the last digit in accordance with Luhn
    check_sum = list(check_sum)
    for i, o in enumerate(check_sum):
        check_sum[i] = int(check_sum[i])  # turn values into integers
        if i % 2 == 0:  # odd number indexes multiplied by 2
            check_sum[i] *= 2
            if check_sum[i] > 9:  # 9 subtracted from numbers over 9
                check_sum[i] -= 9
    summed = sum(check_sum)  # numbers added
    if summed % 10 != 0:
        return str(10 - summed % 10)  # returns last digit
    else:
        return "0"


def check_luhn(number):  # checks if number passes Luhn verification
    number = list(str(number))
    for i in range(len(number)):
        number[i] = int(number[i])
    last_digit = number[-1]
    number.pop(-1)
    for i, o in enumerate(number):
        if i % 2 == 0:
            number[i] *= 2
            if number[i] > 9:
                number[i] -= 9
    number.append(last_digit)
    if sum(number) % 10 == 0:
        return True
    else:
        return False


accounts = []


def add_accounts():
    cards = cur.execute("SELECT * FROM card")
    for row in cards:
        db_number = row[1]
        db_pin = row[2]
        db_balance = row[3]
        existing_card = Card(db_number, db_pin, db_balance)
        accounts.append(existing_card)


add_accounts()


def check_numbers(entry):  # checks if account number exists in database
    check = 0
    for i in range(len(accounts)):
        if accounts[i].card == entry:
            check += 1
    if check == 1:
        return True
    elif check == 0:
        return False


def check_account_number_position(entry):
    account_number = 0
    for i in range(len(accounts)):
        if accounts[i].card == entry:
            account_number = i
    return account_number



def main_loop():
    while True:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
        choice = input()
        if choice == "1":
            number = "400000" + str(random.randint(100000000, 999999999))  # account number
            last_digit = luhn(number)  # apply Luhn
            number = number + last_digit
            pin = str(random.randint(1000, 9999))  # pin number

            print("Your card has been created")
            print("Your card number:")
            print(number)

            print("Your card PIN:")
            print(pin)

            new_card = Card(number, pin, 0)
            accounts.append(new_card)

            cur.execute("INSERT INTO card (number, pin, balance) VALUES (?, ?, ?);",
                        (number, pin, 0))  # DATABASE ENTRY
            conn.commit()

        elif choice == "2":
            print("Enter your card number:")
            num_ent = input()
            print("Enter your PIN:")
            pin_ent = input()
            counter = 0
            logout_check = 0
            for i in range(len(accounts)):  # check if entry is an existing account
                if accounts[i].card == num_ent and accounts[i].pin == pin_ent:
                    print("You have successfully logged in!")
                    counter = 0
                    while True:
                        print("1. Balance")
                        print("2. Add income")
                        print("3. Do transfer")
                        print("4. Close account")
                        print("5. Log out")
                        print("0. Exit")
                        decision = input()
                        if decision == "1":  # check balance
                            print("Balance: {}".format(accounts[i].balance))
                        elif decision == "2":
                            print("Enter income: ")
                            addition = int(input())
                            accounts[i].balance += addition
                            cur.execute("UPDATE card SET balance = (?) WHERE number = (?);",
                                        (accounts[i].balance, num_ent))
                            conn.commit()
                            print("Income was added!")
                        elif decision == "3":
                            print("Transfer")
                            print("Enter card number: ")
                            transfer_number = input()
                            if check_luhn(transfer_number) == False:
                                print("Probably you made a mistake in the card number. Please try again!")
                            elif check_numbers(transfer_number) == False:
                                print("Such a card does not exist.")
                            elif transfer_number == accounts[i].card:
                                print("You can't transfer money to the same account!")
                            else:
                                print("Enter how much money you want to transfer: ")
                                transfer_amount = int(input())
                                if transfer_amount > accounts[i].balance:
                                    print("Not enough money!")
                                else:
                                    accounts[i].balance -= transfer_amount
                                    target = cur.execute("SELECT id FROM card WHERE number = (?);", [transfer_number])
                                    accounts[check_account_number_position(transfer_number)].balance += transfer_amount
                                    cur.execute("UPDATE card SET balance = (?) WHERE number = (?);",
                                                (accounts[i].balance, num_ent))
                                    cur.execute("UPDATE card SET balance = (?) WHERE number = (?);",
                                                (accounts[check_account_number_position(transfer_number)].balance,
                                                 transfer_number))
                                    conn.commit()
                                    print("Success!")
                        elif decision == "4":
                            cur.execute("DELETE FROM card WHERE number = (?);", [num_ent])
                            conn.commit()
                            print("Your account has been closed.")
                            logout_check = 1
                            break
                        elif decision == "5":  # log out
                            print("You have successfully logged out!")
                            logout_check = 1
                            break
                        elif decision == "0":  # exit program
                            return
                else:
                    counter += 1
            if counter != 0 and logout_check != 1:
                print("Wrong card number or pin!")
                counter = 0
            elif logout_check == 1:
                logout_check = 0
        elif choice == "0":  # exit program
            return


main_loop()
print("Bye!")
