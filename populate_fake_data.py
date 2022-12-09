import os
import urllib.parse
import sqlalchemy as sa
from dotenv import load_dotenv
import pandas as pd
import names  # random name generator
import string
import random
import hashlib

counter = 1
accountNum = 51
minMatch = 39474
maxMatch = 42474


def create_users_wallets(df_user, df_wallet):
    global accountNum
    userInfo = []
    for i in range(1, accountNum):
        y = random.randint(1, 10)
        email = ''.join(random.choice(string.ascii_letters) for x in range(y)) + "@gmail.com"
        email = email.lower()

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

        salt = salt.hex()
        password = password.hex()

        user = {'id': [i],
                'firstName': [first],
                'lastName': [names.get_last_name()],
                'email': [email],
                'passwordHash': [password],
                'salt': [salt]}
        temp = pd.DataFrame(user)
        df_user = pd.concat([df_user, temp])
        userInfo.append([email, plainPassword])

        wallet = {'id': [i],
                  'userId': [i],
                  'name': [names.get_full_name()],
                  'amountStored': [0]}
        temp = pd.DataFrame(wallet)
        df_wallet = pd.concat([df_wallet, temp])

    df_user.drop_duplicates(subset=['email'], inplace=True)
    with open('data/userInfo', 'w') as f:
        f.write('email, password\n')
        for u in userInfo:
            f.write(', '.join(u) + '\n')

    return df_user, df_wallet


def simulate_deposit(u, df_wallet, df_transactions):
    global counter
    money = df_wallet[df_wallet['userId'] == u]['amountStored'].values[0]
    amount = round(random.uniform(5, random.randint(6, 1000)), 2)  # must deposit at least $5
    t = pd.DataFrame({'id': [counter], 'transactionTypeId': [2], 'walletId': [u], 'amount': [amount]})
    counter += 1
    df_wallet.loc[df_wallet['userId'] == u, 'amountStored'] = money + amount
    return df_wallet, pd.concat([df_transactions, t])


def simulate_withdraw(u, df_wallet, df_transactions):
    global counter
    money = df_wallet[df_wallet['userId'] == u]['amountStored'].values[0]
    if money >= 50:  # need at least $50 to withdraw
        amount = round(random.uniform(5, money), 2)
        t = pd.DataFrame({'id': [counter], 'transactionTypeId': [1], 'walletId': [u], 'amount': [amount]})
        counter += 1
        df_wallet.loc[df_wallet['userId'] == u, 'amountStored'] = money - amount
        return df_wallet, pd.concat([df_transactions, t])
    return df_wallet, df_transactions


def simulate_betting(i, u, df_wallet, df_bets, df_pool, df_transactions):
    global counter
    money = df_wallet[df_wallet['id'] == u]['amountStored'].values[0]
    bType = random.randint(1, 4)
    if money >= 5:
        bAmount = round(random.uniform(5, money), 2)
        guess = 0
        if bType in [3, 4]:
            guess = random.randint(0, 9)

        new_pool = pd.DataFrame({'matchId': [i], 'betTypeId': [bType], 'amount': [bAmount]})  # add to pool
        new_transactions = pd.DataFrame(
            {'id': [counter], 'transactionTypeId': [3], 'walletId': u, 'amount': [bAmount]})  # add to transaction
        counter += 1
        df_wallet.loc[df_wallet['userId'] == u, 'amountStored'] = money - bAmount  # subtract from wallet
        new_bets = pd.DataFrame({'transactionId': [counter],
                                 'matchId': [i],
                                 'betTypeId': [bType],
                                 'guess': [guess],
                                 'amount': [bAmount]})  # add to bets

        return (pd.concat([df_pool, new_pool]),
                pd.concat([df_transactions, new_transactions]),
                pd.concat([df_bets, new_bets]),
                df_wallet)
    return df_pool, df_transactions, df_bets, df_wallet


def simulate_payouts(i, df_results, df_wallet, df_transactions, df_bets):
    global counter
    df_filtered_bets = df_bets[df_bets['matchId'] == i]
    df_filtered_bets = df_filtered_bets[df_filtered_bets['amount'] != 0]
    for tId, bId, g, a in zip(df_filtered_bets['transactionId'],
                              df_filtered_bets['betTypeId'],
                              df_filtered_bets['guess'],
                              df_filtered_bets['amount']):
        wId = df_transactions[df_transactions['id'] == tId]['walletId'].values[0]
        money = df_wallet[df_wallet['id'] == wId]['amountStored'].values[0]
        payout = 0
        if bId == 1:
            score1 = df_results[df_results['i'] == i]['result_1'].values[0]
            score2 = df_results[df_results['i'] == i]['result_2'].values[0]
            if score1 > score2:
                payout = round(a * 1.5, 2)
        elif bId == 2:
            score1 = df_results[df_results['i'] == i]['result_1'].values[0]
            score2 = df_results[df_results['i'] == i]['result_2'].values[0]
            if score2 > score1:
                payout = round(a * 1.5, 2)
        elif bId == 3:
            last = df_results[df_results['i'] == i]['m1_kills'].values[0]
            if last % 10 == g:
                payout = round(a * 2.5, 2)
        elif bId == 4:
            last = df_results[df_results['i'] == i]['m1_hs'].values[0]
            if last % 10 == g:
                payout = round(a * 2.5, 2)

        if payout != 0:
            new_transactions = pd.DataFrame(
                {'id': counter, 'transactionTypeId': [4], 'walletId': [wId], 'amount': [payout]})  # add to transaction
            counter += 1
            df_wallet.loc[df_wallet['id'] == wId, 'amountStored'] = money + payout  # add from wallet
            df_transactions = pd.concat([df_transactions, new_transactions])
    return df_transactions, df_wallet


def simulation(df_wallet, df_bets, df_transactions, df_pool, df_results):
    global accountNum
    global minMatch
    global maxMatch
    for i in range(minMatch, maxMatch):  # for each match
        print(i)
        new_pool1 = pd.DataFrame({'matchId': [i], 'betTypeId': [1], 'amount': [0]})
        new_pool2 = pd.DataFrame({'matchId': [i], 'betTypeId': [2], 'amount': [0]})
        new_pool3 = pd.DataFrame({'matchId': [i], 'betTypeId': [3], 'amount': [0]})
        new_pool4 = pd.DataFrame({'matchId': [i], 'betTypeId': [4], 'amount': [0]})
        df_pool = pd.concat([df_pool, new_pool1, new_pool2, new_pool3, new_pool4])
        for u in range(1, accountNum):  # for each wallet (user)
            decision = random.randint(1, 5)
            if decision == 1:
                df_wallet, df_transactions = simulate_deposit(u, df_wallet, df_transactions)
            elif decision == 2:
                df_wallet, df_transactions = simulate_withdraw(u, df_wallet, df_transactions)
            elif decision == 3:
                df_pool, df_transactions, df_bets, df_wallet = simulate_betting(i, u, df_wallet, df_bets, df_pool,
                                                                                df_transactions)
            elif decision == 4:
                df_wallet, df_transactions = simulate_deposit(u, df_wallet, df_transactions)
                df_pool, df_transactions, df_bets, df_wallet = simulate_betting(i, u, df_wallet, df_bets, df_pool,
                                                                                df_transactions)
            else:
                df_wallet, df_transactions = simulate_withdraw(u, df_wallet, df_transactions)
                df_pool, df_transactions, df_bets, df_wallet = simulate_betting(i, u, df_wallet, df_bets, df_pool,
                                                                                df_transactions)
        df_transactions, df_wallet = simulate_payouts(i, df_results, df_wallet, df_transactions, df_bets)
    return df_wallet, df_bets, df_transactions, df_pool


def main():
    df_betType = pd.DataFrame(data={'team1win', 'team2win', 'guessKillsEnd', 'guessHsEnd'}, columns=['type'])
    df_transactionType = pd.DataFrame(data={'withdraw', 'deposit', 'placeBet', 'payoutBet'}, columns=['type'])

    df_bets = pd.DataFrame(columns=['transactionId', 'matchId', 'betTypeId', 'guess', 'amount'])
    df_transactions = pd.DataFrame(columns=['id', 'transactionTypeId', 'walletId', 'amount'])
    df_pool = pd.DataFrame(columns=['matchId', 'betTypeId', 'amount'])
    df_user = pd.DataFrame(columns=['id', 'firstName', 'lastName', 'email', 'passwordHash', 'salt', 'balance'])
    df_wallet = pd.DataFrame(columns=['id', 'userId', 'name', 'amountStored'])

    df_matches = pd.read_csv('data/matchesData.csv')
    df_matches.drop('Unnamed: 0', axis=1, inplace=True)

    df_results = pd.read_csv('data/resultsData.csv')
    df_results.drop('Unnamed: 0', axis=1, inplace=True)

    df_user, df_wallet = create_users_wallets(df_user, df_wallet)
    df_wallet, df_bets, df_transactions, df_pool = simulation(df_wallet, df_bets, df_transactions, df_pool, df_results)

    df_betType.to_csv('data/betTypeData.csv')
    df_transactionType.to_csv('data/transactionTypeData.csv')
    df_user.to_csv('data/userData.csv')
    df_wallet.to_csv('data/walletData.csv')
    df_transactions.to_csv('data/transactionsData.csv')
    df_pool.to_csv('data/poolData.csv')
    df_bets.to_csv('data/betsData.csv')


if __name__ == '__main__':
    main()
