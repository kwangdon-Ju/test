import time
import datetime
import pyupbit
import numpy as np
import pandas as pd
# from upbit.upbit import *

class AutoTrade():

    def __init__(self):
        print('자동 매매 시작 합니다.')

        self.fee = 0.0005

        self.access = 'Sxxt8Nxa9pZS2Z0bqjWXqslLnH7fgIFyd7VSNQq5'
        self.secret = 'upa02I9UCgoRx6XMVc1JEGQZ79L9wHYvZFI0x3TK'
        self.upbit = pyupbit.Upbit(self.access, self.secret)                   # 로그인

        print("Successfully Log-in => autotrade start")

        self.ticker = 'KRW-DOGE'

        df = pyupbit.get_ohlcv(self.ticker, interval="minute3")
        cName = 'close'
        self.interval_k = 20
        self.interval_d = 15

        self.calcStochastic(df, cName, self.interval_k, self.interval_d, 'FastK', 'FastD', 'SlowK', 'SlowD')

        print('FastK: %s, FastD : %s' % (df['FastK'][-1],df['FastD'][-1]))

        df_bal = pd.DataFrame.from_dict(self.upbit.get_balances())   # 잔고 조회
        print(df_bal)

        stage = None

        # 자동매매 시작
        while True:
            try:
                if df['FastK'][-1] < 25 and df['FastD'][-1] < 25:
                    krw = self.get_balance('KRW')
                    print('%s, 한화 잔고 : %s' % (type(krw), krw))
                    if krw > 5000:
                        self.upbit.buy_market_order(self.ticker, krw * 0.9995)
                        print('%s를 %만큼 주문 했습니다.' % (self.ticker, krw * 0.9995))
                    else:
                        print('원화가 부족합니다.\n\n')

                elif df['FastK'][-1] > 80 and df['FastD'][-1] > 80:
                    sell_ticker = self.get_balance('DOGE')
                    print('매도 시간 진입 합니다. \n%s 잔고 : %s' % ('DOGE', sell_ticker))
                    sell_amount = int(sell_ticker * 0.1 * 0.9995)
                    print('sell amount : %s\n\n' % sell_amount)
                    self.sell_order(self.ticker, sell_amount)

                    print('%s 매도 성공 : %s / %s\n\n\n' % ("DOGE", sell_amount, sell_ticker))

                    time.sleep(5)

                else:
                    print('매매 조건을 만족하지 못합니다\n\n')

                        # now = datetime.datetime.now()
                # print('stage : %s' % stage)
                # stage = 'buy'
                # print('stage : %s' % stage)

                # if stage == 'sell':
                #     start_time = self.get_start_time(self.ticker)
                #     end_time = start_time + datetime.timedelta(minutes=10)
                #     print('       now : %s\nstart_time : %s\n  end_time : %s.' % (now, start_time, end_time))
                #     stage = 'sell'

                    # BestK = self.get_best_k(ticker)  # 최적 K값 구하기
                    # BestK = 0.1

                    # if start_time < now < end_time - datetime.timedelta(seconds=10):
                    #     print('조건1 시작')
                    #     self.target_price = self.get_target_price(self.ticker, BestK)
                    #     print('target_price : %s, type : %s' % (self.target_price,type(self.target_price)))
                    #     self.current_price = self.get_current_price(self.ticker)
                    #     print('current_price : %s, type: %s' % (self.current_price,type(self.target_price)))

                        # if self.target_price < self.current_price:
                        #     print('조건2 시작')
                        #     krw = self.get_balance('KRW')
                        #     print(type(krw))
                        #     print('한화 잔고 : %s' % krw)
                        #     if krw > 5000:
                        #         self.upbit.buy_market_order(self.ticker, krw*0.9995)
                        #         print('%s를 %만큼 주문 했습니다.' % (self.ticker, krw*0.9995))
                        #     else:
                        #         print('원화가 부족합니다.\n\n')

                        # else:
                        #     print('매수 가격 조건을 만족하지 못합니다\n\n')

                    # else:
                    #     sell_ticker = self.get_balance('DOGE')
                    #     print('매도 시간 진입 합니다. \n%s 잔고 : %s' % ('DOGE',sell_ticker))
                    #     if sell_ticker > 25 and self.target_price < self.current_price:
                    #         sell_amount = int(sell_ticker*0.1*0.9995)
                    #         print('sell amount : %s\n\n' % sell_amount)
                    #         # self.upbit.sell_market_order("DOGE", sell_amount)
                    #         self.sell_order(self.ticker,sell_amount)
                    #
                    #         print('%s 매도 성공 : %s / %s\n\n\n' % ("DOGE", sell_amount, sell_ticker ))
                    #     else:
                    #         print('매도실패 : 매도 가격 조건이 맞지 않습니다.\n\n')

                    time.sleep(180)
                # else:
                #     break

            except Exception as e:
                print(e)
                time.sleep(5)

    # 매도 주문
    def sell_order(self, ticker, volume):
        try:
            while True:
                sell_result = self.upbit.sell_market_order(ticker, volume)
                if sell_result == None or 'error' in sell_result:
                    print(f"{sell_result}, 매도 재 주문")
                    time.sleep(1)
                else:
                    return sell_result
        except:
            print("매도 주문 이상")

    def get_target_price(self, ticker, BestK ):
        """변동성 돌파 전략으로 매수 목표가 조회"""
        df = pyupbit.get_ohlcv(ticker, interval='minute1', count=20)
        target_price = float(df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * BestK )
        print('df.iloc[0][close]: %s \n df.iloc[0][high]: %s \n df.iloc[0][low]: %s' % (df.iloc[0]['close'],df.iloc[0]['high'],df.iloc[0]['low'] ))

        return target_price

    def get_buy_price(ticker, k):
        df = pyupbit.get_ohlcv(ticker, interval='minute1', count=20)
        buy_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
        return buy_price

    def get_start_time(self,ticker):
        """시작 시간 조회"""
        df = pyupbit.get_ohlcv(ticker, interval="minute1", count=1)
        start_time = df.index[0]
        return start_time

    def get_balance(self,ticker):
        """잔고 조회"""
        balances = self.upbit.get_balances()
        for b in balances:
            if b['currency'] == ticker:
                if b['balance'] is not None:
                    return float(b['balance'])
                else:
                    return 0
        return 0


    def get_current_price(self,ticker):
        """현재가 조회"""
        return pyupbit.get_orderbook(ticker)["orderbook_units"][0]["ask_price"]


    def get_best_k(self,ticker):
        누적 = []
        df = pyupbit.get_ohlcv(ticker, interval='minute1')
        for n in range(1, 10):
            k = float(0.1 * n)
            df['range'] = (df['high'] - df['low']) * k
            df['target'] = df['open'] + df['range'].shift(1)
            df['ror'] = np.where(df['high'] > df['target'],df['close'] / df['target'] - self.fee, 1)
            ror = df['ror'].cumprod()[-2]
            누적.append(ror)

        key = []
        for n in range(1, 10):
            i = 0.1 * n
            i = round(i, 1)
            key.append(i)

        dic = dict(zip(key, 누적))
        # BestK = dic[max(누적)]
        BestK = pd.DataFrame.from_dict(dic, orient='index')
        # BestK = BestK[max(['0'])]

        print('%s : Max ror is %s.' % ( ticker, max(dic.values())))
        return BestK

    def calcStochastic(self, m_Df, cName, m_Period, m_Ma, strFk, strFd, strSk, strSd):

        print('-------------------------- calcStochastic 함수 시작 입니다 --------------------------')

        max5 = m_Df[cName].rolling(window=m_Period).max()
        min5 = m_Df[cName].rolling(window=m_Period).min()
        max5.fillna(0)
        min5.fillna(0)

        m_Df[strFk] = (((m_Df[cName] - min5) / (max5 - min5)) * 100).round(2)
        fastD = pd.DataFrame(m_Df['FastK'].rolling(window=m_Ma).mean()).round(2)

        m_Df.insert(len(m_Df.columns), strFd, fastD)
        # SLow Stochastic ( 슬로우 스토캐스틱 Slow%K3)
        slowK = pd.DataFrame(m_Df['FastD'].rolling(window=m_Ma).mean()).round(2)

        m_Df.insert(len(m_Df.columns), strSk, slowK)
        # SLow Stochastic ( 슬로우 스토캐스틱 Slow%D3)
        slowD = pd.DataFrame(m_Df[strSk].rolling(window=m_Ma).mean()).round(2)

        m_Df.insert(len(m_Df.columns), strSd, slowD)

        print(m_Df.tail(10))

        print('-------------------------- calcStochastic 함수 끝 입니다 --------------------------')

        return m_Df
