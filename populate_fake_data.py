import os
import urllib.parse
import sqlalchemy as sa
from dotenv import load_dotenv
import pandas as pd
import names  # random name generator
import string
import random
import hashlib


def simulate_deposit():
    pass


def simulate_withdraw():
    pass


def simulate_betting():
    pass


def main():
    df_betType = pd.DataFrame(data={'team1win', 'team2win', 'guessKills', 'guessHs'}, columns=['type'])
    df_transactionType = pd.DataFrame(data={'withdraw', 'deposit'}, columns=['type'])

    df_bets = pd.DataFrame(data=['userId', 'matchId', 'betTypeId', 'amount', 'placedTime'])
    df_transactions = pd.DataFrame(columns=['transactionTypeId', 'userId', 'amount'])
    df_pool = pd.DataFrame(columns=['matchId', 'betType', 'amount'])
    df_user = pd.DataFrame(columns=['id', 'firstName', 'lastName', 'email', 'passwordHash', 'salt', 'balance'])
    df_wallet = pd.DataFrame(columns=['userId', 'name', 'amountStored'])

    # create users and wallets
    userInfo = []
    for i in range(10):
        y = random.randint(1, 10)
        email = ''.join(random.choice(string.ascii_letters) for x in range(y)) + "@gmail.com"

        # generate random password
        numchars = random.randint(5, 10)  # number of characters, upper and lower
        numdigits = random.randint(0, 8)  # number of digits
        numpunc = random.randint(0, 5)  # number of punctuation characters
        exclude = ["%", "&", "\"", "'", "`"]  # exclude character(s) as a list
        allchars = string.ascii_letters
        allnums = string.digits
        allpunc = string.punctuation

        for ex in exclude:
            allchars = allchars.replace(ex, '')
            allnums = allnums.replace(ex, '')
            allpunc = allpunc.replace(ex, '')

        combine = random.choices(allchars, k=numchars) + random.choices(allnums, k=numdigits) + random.choices(
            allpunc, k=numpunc)
        random.shuffle(combine)  # shuffle the characters

        plainPassword = ''.join(combine)
        salt = os.urandom(32)  # A new salt for this user
        password = hashlib.pbkdf2_hmac('sha256', plainPassword.encode('utf-8'), salt, 100000)

        male = random.randint(0, 1)
        if male:
            first = names.get_first_name('male')
        else:
            first = names.get_first_name('female')

        user = {'id': [i],
                'firstName': [first],
                'lastName': [names.get_last_name()],
                'email': [email],
                'passwordHash': [password],
                'salt': [salt]}
        temp = pd.DataFrame(user)
        df_user = pd.concat([df_user, temp])
        userInfo.append([email, plainPassword])

        wallet = {'userId': [i],
                  'name': [names.get_full_name()],
                  'amountStored': [0]}
        temp = pd.DataFrame(wallet)
        df_wallet = pd.concat([df_wallet, temp])

    df_user.drop_duplicates(subset=['email'], inplace=True)
    with open('data/userInfo', 'w') as f:
        f.write('email, password\n')
        for u in userInfo:
            f.write(', '.join(u) + '\n')

    df_betType.to_csv('data/betTypeData.csv')
    df_transactionType.to_csv('data/transactionTypeData.csv')
    df_user.to_csv('data/userData.csv')
    df_wallet.to_csv('data/walletData.csv')


if __name__ == '__main__':
    main()
