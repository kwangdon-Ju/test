import pyupbit
import numpy as np
import pandas as pd

class upbit():

    def __init__(self):
        super().__init__()
        print('------------------------ upbit class 시작-------------------------')
        self.fee = 0.0005
        access = 'Sxxt8Nxa9pZS2Z0bqjWXqslLnH7fgIFyd7VSNQq5'
        secret = 'upa02I9UCgoRx6XMVc1JEGQZ79L9wHYvZFI0x3TK'
        upbit = pyupbit.Upbit(access, secret)                   # 로그인

        df_bal = pd.DataFrame.from_dict(upbit.get_balances())   # 잔고 조회
        print(df_bal)
        df_bal.to_excel('./status/result.xlsx')

        ticker = 'KRW-DOGE'

        BestK = self.get_best_k(ticker)                                   # 최적 K값 구하기

        self.BackTest(BestK,ticker)                                         # 백테스트

        df = pyupbit.get_ohlcv(ticker, interval="minute1")
        cName = 'close'
        self.calcStochastic(df, cName, 20, 15, 'FastK', 'FastD', 'SlowK', 'SlowD')

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
        best_k = dic[max(key)]
        print(list(dic))
        print('%s : Max ror is %s when K is %s.' % ( ticker, max(dic.values()), best_k))
        return best_k

    def BackTest(self,k,ticker):
        print('--------------------------- Back Test 함수 시작 ---------------------------')
        df = pyupbit.get_ohlcv(ticker, interval="minute1")
        df['range'] = (df['high'] - df['low']) * k

        # 매수가
        df['target'] = df['open'] + df['range'].shift(1)
        df['ror'] = np.where(df['high'] > df['target'], df['close'] / df['target'] - self.fee, 1)
        df['hpr'] = df['ror'].cumprod()
        df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100
        print("MDD(%): ", df['dd'].max())

        print(df.tail(10))
        df.to_excel("./status/backtest_"+ ticker + ".xlsx")
        print('--------------------------- Back Test 함수 끝 ---------------------------')


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

        print(m_Df.tail(50))

        print('-------------------------- calcStochastic 함수 끝 입니다 --------------------------')

        return m_Df
