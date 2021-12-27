import time
import pyupbit
import numpy as np
import pandas as pd

class Doge_trade():

    def __init__(self):
        print('Doge 코인 자동 매매 시작 합니다.')

        self.fee = 0.0005

        self.access = 'Sxxt8Nxa9pZS2Z0bqjWXqslLnH7fgIFyd7VSNQq5'
        self.secret = 'upa02I9UCgoRx6XMVc1JEGQZ79L9wHYvZFI0x3TK'
        self.upbit = pyupbit.Upbit(self.access, self.secret)                   # 로그인

        print("Successfully Log-in => autotrade start")

        self.ticker = 'KRW-DOGE'

        df_bal = pd.DataFrame.from_dict(self.upbit.get_balances())   # 잔고 조회

        print(df_bal)

        self.interval_k = 20
        self.interval_d = 15
        trade_price = 0

        # 자동매매 시작
        while True:
            try:
                df = pyupbit.get_ohlcv(self.ticker, interval="minute3")
                cName = 'close'

                self.calcStochastic(df, cName, self.interval_k, self.interval_d, 'FastK', 'FastD', 'SlowK', 'SlowD')
                print(df.tail(3))
                fastk_buy = df['FastK'][-1]
                fastd_buy = df['FastD'][-1]

                print('FK : %s, FD : %s, 평균매입가 : %s ' % (fastk_buy, fastd_buy, float(df_bal['avg_buy_price'][2])))

                if fastk_buy < 25 :
                    print('매수조건1(FastK < 25)을 만족 했습니다. ')
                    if fastd_buy < 25:
                        print('매수조건2(FastD < 25)를 만족 했습니다. ')
                        if df['close'][-1] < float(df_bal['avg_buy_price'][2])*0.99:
                            print('매수조건3(현재가 < 평균매수가)을 만족 했습니다. ')
                            krw = self.get_balance('KRW')
                            print(df_bal)
                            if krw > 5000:
                                self.upbit.buy_market_order(self.ticker, krw * 0.9995*0.1)
                                print('%s를 %만큼 주문 했습니다.' % (self.ticker, krw * 0.9995))
                            else:
                                print('매수조건4 원화가 부족합니다.\n\n')
                        else:
                            print('매수조건3(현재가 < 평균 매입가*0.99)을 만족하지 못 했습니다. \n\n ')
                    else:
                        print('매수조건2(FastD < 25)를 만족하지 못 했습니다.\n\n')

                elif fastk_buy > 75:
                    print('매도조건1 만족 : FastK > 75')
                    if fastd_buy > 75:
                        print('매도조건2 만족 : FastD > 75')

                        if df['close'][-1] > float(df_bal['avg_buy_price'][2])*1.03:
                            print('매도조건3 만족 : 수익 > 3% ')

                            sell_ticker = self.get_balance('DOGE')
                            print('매도시간 진입 합니다. \n%s 잔고 : %s' % ('DOGE', sell_ticker))
                            sell_amount = int(sell_ticker * 0.1 * 0.9995)
                            print('sell amount : %s\n\n' % sell_amount)
                            self.sell_order(self.ticker, sell_amount)
                            print(df_bal)
                            print('%s 매도 성공 : %s / %s\n\n\n' % ("DOGE", sell_amount, sell_ticker))

                            time.sleep(1)
                        else:
                            print(df_bal)
                            print('매도조건3(수익 +3%) 만족 실패\n\n')

                    else:
                        print(df_bal)
                        print('매도조건2(FastD > 75) 만족 실패\n\n')


                else:
                    print(df_bal)
                    print('매도조건1(FastK > 75) 만족 실패\n\n')

                time.sleep(30)

            except Exception as e:
                print(e)
                time.sleep(1)

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

        print('-------------------------- calcStochastic 함수 끝 입니다 --------------------------')

        return m_Df
