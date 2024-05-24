#!/usr/bin/python3
# -*-coding:utf-8-*-
# Author: Yang Wang
# CreatDate: 2024/5/24 21:40
# Description:

import pandas
import uuid
import random


class User:
    def __init__(self, name: str, balance: int):
        self.name = name
        self.balance = balance


class BankBiz:
    def __init__(self):
        self.USER_TABLE = 'tb_user.csv'

    def _create_account_check_user_(self, user: User):
        if not isinstance(user.balance, int):
            print('User balance type is not int.')
            return False
        if user.balance < 0:
            print('User balance must be greater than or equal to 0.')
            return False
        if self.get_user_by_name(user.name) is not None:
            print('User has already exist.')
            return False
        return True

    def _opt_balance_check_user_(self, user: User):
        if not isinstance(user.balance, int):
            print(type(user.balance))
            print('User balance type is not int.')
            return False
        if user.balance <= 0:
            print('User balance must be greater than 0.')
            return False
        if self.get_user_by_name(user.name) is None:
            print('User does not exist.')
            return False
        return True

    def _transfer_check_(self, from_user_name: str, to_user_name: str, amount: int):
        if from_user_name == to_user_name:
            print('Can not transfer to yourself.')
        if amount <= 0:
            print('The amount must be greater than 0')
            return False
        from_user = self.get_user_by_name(from_user_name)
        if from_user is None:
            print('From user does not exist.')
            return False
        to_user = self.get_user_by_name(to_user_name)
        if to_user is None:
            print('To user does not exist.')
            return False
        return True

    def get_user_by_name(self, name: str) -> User:
        data_frame = pandas.read_csv(self.USER_TABLE)
        search_user = data_frame.loc[data_frame['name'] == name]
        user = None
        if not search_user.empty:
            user = User(name, int(search_user.iloc[0]['balance']))
        return user

    def create_account(self, user: User):
        if not self._create_account_check_user_(user):
            return False
        data = {'name': [user.name], 'balance': [user.balance]}
        data_frame = pandas.DataFrame(data)
        data_frame.to_csv(self.USER_TABLE, mode='a', index=False, header=False)
        return True

    def deposit(self, user: User):
        if not self._opt_balance_check_user_(user):
            return False
        user_from_db = self.get_user_by_name(user.name)
        user.balance += user_from_db.balance
        data_frame = pandas.read_csv(self.USER_TABLE)
        data_frame.loc[data_frame['name'] == user.name, 'balance'] = user.balance
        data_frame.to_csv(self.USER_TABLE, index=False)
        return True

    def withdraw(self, user: User):
        if not self._opt_balance_check_user_(user):
            return False
        user_from_db = self.get_user_by_name(user.name)
        if user.balance > user_from_db.balance:
            print('User are not allowed to overdraft their accounts.')
            return False
        user.balance = user_from_db.balance - user.balance
        data_frame = pandas.read_csv(self.USER_TABLE)
        data_frame.loc[data_frame['name'] == user.name, 'balance'] = user.balance
        data_frame.to_csv(self.USER_TABLE, index=False)
        return True

    def transfer(self, from_user_name: str, to_user_name: str, amount: int):
        if not self._transfer_check_(from_user_name, to_user_name, amount):
            return False

        from_user = User(from_user_name, amount)
        to_user = User(to_user_name, amount)

        if self.withdraw(from_user):
            self.deposit(to_user)
        return True


if __name__ == "__main__":
    test_bank = BankBiz()

    print('#############create account#############')
    # create account failed, balance must be int type
    test_user = User('Mark', 'asdf')
    test_bank.create_account(test_user)

    # create account failed, user duplicate
    test_user = User('Mark', 200)
    test_bank.create_account(test_user)

    # create account failed, user balance must be greater than or equal to 0
    test_user = User('Mark', -1)
    test_bank.create_account(test_user)

    # create account success
    test_user = User(f"test_{str(uuid.uuid4()).replace('-', '')}", random.randint(0, 10000))
    test_bank.create_account(test_user)
    new_user = test_bank.get_user_by_name(test_user.name)
    print(f'create account => name:{new_user.name}   balance:{new_user.balance}')

    print('#############deposit 100#############')
    # deposit failed, user does not exist
    test_user = User('notexist', 100)
    test_bank.deposit(test_user)

    # deposit success
    before_balacne = test_bank.get_user_by_name('Mark').balance
    print(f'before_deposit_balacne: {before_balacne}')

    test_user = User('Mark', 100)
    test_bank.deposit(test_user)

    after_balacne = test_bank.get_user_by_name('Mark').balance
    print(f'after_deposit_balacne: {after_balacne}')

    print('#############withdraw 50#############')
    # withdraw failed, overdraft
    test_user = User('Mark', 1000000)
    test_bank.withdraw(test_user)

    # withdraw failed, user does not exist
    test_user = User('notexist', 50)
    test_bank.withdraw(test_user)

    # withdraw success
    before_balacne = test_bank.get_user_by_name('Mark').balance
    print(f'before_withdraw_balacne: {before_balacne}')

    test_user = User('Mark', 50)
    test_bank.withdraw(test_user)

    after_balacne = test_bank.get_user_by_name('Mark').balance
    print(f'after_withdraw_balacne: {after_balacne}')

    print('#############transfer 10#############')
    # transfer success
    before_from_balance = test_bank.get_user_by_name('Mark').balance
    before_to_balance = test_bank.get_user_by_name('Zhangsan').balance
    print(f"before transfer: Mark:{before_from_balance}   Zhangsan:{before_to_balance}")

    test_bank.transfer('Mark', 'Zhangsan', 10)

    after_from_balance = test_bank.get_user_by_name('Mark').balance
    after_to_balance = test_bank.get_user_by_name('Zhangsan').balance
    print(f"after transfer: Mark:{after_from_balance}   Zhangsan:{after_to_balance}")
