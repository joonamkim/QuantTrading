import numpy as np


class TechnicalIndicators:

    def temp(self):
        print("hello")
        return 0

    def MACD(self, DF, slow, fast, signal):
        df = DF.copy()
        df['MA_Fast'] = df['Adj Close'].ewm(span=fast, min_periods=fast).mean()
        df['MA_Slow'] = df['Adj Close'].ewm(span=slow, min_periods=slow).mean()
        df['MACD'] = df['MA_Fast'] - df['MA_Slow']
        df['Signal'] = df['MACD'].ewm(span=signal, min_periods=signal).mean()
        df.dropna(inplace=True)
        df['MACD'].plot()

        return df

    def ATR(self, DF, n):
        df = DF.copy()
        df['H-L'] = abs(df["High"] - df["Low"])
        df['H-PC'] = abs(df['High'] - df['Adj Close'].shift(1))
        df['L-PC'] = abs(df['Low'] - df['Adj Close'].shift(1))
        df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)

        df['ATR'] = df['TR'].rolling(n).mean()

        df2 = df.drop(['H-L', 'H-PC', 'L-PC'], axis=1)

        return df2

    def BollingerBands(self, dataframe, n):
        df = dataframe.copy()
        df['MA'] = df['Adj Close'].rolling(n).mean()
        df['BB_up'] = df['MA'] + 2 * df['MA'].rolling(n).std()
        df['BB_down'] = df['MA'] - 2 * df['MA'].rolling(n).std()
        df['BB_range'] = df['BB_up'] - df['BB_down']
        return df

    def slope(self, ser, n):
        "function to calculate the slope of regression line for n consecutive points on a plot"
        ser = (ser - ser.min()) / (ser.max() - ser.min())
        x = np.array(range(len(ser)))
        x = (x - x.min()) / (x.max() - x.min())
        slopes = [i * 0 for i in range(n - 1)]
        for i in range(n, len(ser) + 1):
            y_scaled = ser[i - n:i]
            x_scaled = x[i - n:i]
            x_scaled = sm.add_constant(x_scaled)
            model = sm.OLS(y_scaled, x_scaled)
            results = model.fit()
            slopes.append(results.params[-1])
        slope_angle = (np.rad2deg(np.arctan(np.array(slopes))))
        return np.array(slope_angle)

    def CAGR(self, DF):
        "function to calculate the Cumulative Annual Growth Rate of a trading strategy"
        df = DF.copy()
        df["daily_ret"] = DF["Adj Close"].pct_change()
        df["cum_return"] = (1 + df["daily_ret"]).cumprod()
        n = len(df) / 252  # trading day
        CAGR = (df["cum_return"][-1]) ** (1 / n) - 1
        return CAGR

    def volatility(self, DF):
        "function to calculate annualized volatility of a trading strategy"
        df = DF.copy()
        df["daily_ret"] = DF["Adj Close"].pct_change()
        vol = df["daily_ret"].std() * np.sqrt(252)
        return vol

    def sharpe(self, DF, rf):
        "function to calculate sharpe ratio ; rf is the risk free rate"
        df = DF.copy()
        sr = (CAGR(df) - rf) / volatility(df)
        return sr

    def sortino(self, DF, rf):
        "function to calculate sortino ratio ; rf is the risk free rate"
        df = DF.copy()
        df["daily_ret"] = DF["Adj Close"].pct_change()
        df["neg_ret"] = np.where(df["daily_ret"] < 0, df["daily_ret"], 0)
        neg_vol = df["neg_ret"].std() * np.sqrt(252)
        sr = (CAGR(df) - rf) / neg_vol
        return sr

    def max_dd(DF):
        "function to calculate max drawdown"
        df = DF.copy()
        df["daily_ret"] = DF["Adj Close"].pct_change()
        df["cum_return"] = (1 + df["daily_ret"]).cumprod()
        df["cum_roll_max"] = df["cum_return"].cummax()
        df["drawdown"] = df["cum_roll_max"] - df["cum_return"]
        df["drawdown_pct"] = df["drawdown"] / df["cum_roll_max"]
        max_dd = df["drawdown_pct"].max()
        return max_dd

    def calmar(DF):
        "function to calculate calmar ratio"
        df = DF.copy()
        clmr = CAGR(df) / max_dd(df)
        return clmr

    def OBV(DF):
        """function to calculate On Balance Volume"""
        df = DF.copy()
        df['daily_ret'] = df['Adj Close'].pct_change()
        df['direction'] = np.where(df['daily_ret'] >= 0, 1, -1)
        df['direction'][0] = 0
        df['vol_adj'] = df['Volume'] * df['direction']
        df['obv'] = df['vol_adj'].cumsum()
        return df['obv']

    def renko_DF(DF):
        "function to convert ohlc data into renko bricks"
        df = DF.copy()
        df.reset_index(inplace=True)
        df = df.iloc[:, [0, 1, 2, 3, 5, 6]]
        df.rename(columns={"Date": "date", "High": "high", "Low": "low", "Open": "open", "Adj Close": "close",
                           "Volume": "volume"}, inplace=True)
        df2 = Renko(df)
        df2.brick_size = round(ATR(DF, 120)["ATR"][-1], 0)
        renko_df = df2.get_ohlc_data()  # if using older version of the library please use get_bricks() instead
        return renko_df

    def RSI(DF, n):
        df = DF.copy()
        df['delta'] = df['Adj Close'] - df['Adj Close'].shift(1)
        df['gain'] = np.where(df['delta'] >= 0, df['delta'], 0)
        df['loss'] = np.where(df['delta'] < 0, df['delta'], 0)
        avg_gain = []
        avg_loss = []
        gain = df['gain'].tolist()
        loss = df['loss'].tolist()

        for i in range(len(df)):
            if i < n:
                avg_gain.append(np.NaN)
                avg_loss.append(np.NaN)
            elif i == n:
                avg_gain.append(df['gain'].rolling(n).mean().tolist()[n])
                avg_loss.append(df['loss'].rolling(n).mean().tolist()[n])
            elif i > n:
                avg_gain.append(((n - 1) * avg_gain[i - 1] + gain[i]) / n)
                avg_loss.append(((n - 1) * avg_loss[i - 1] + loss[i]) / n)

        df['avg_gain'] = np.array(avg_gain)
        df['avg_loss'] = np.array(avg_loss)
        df['RS'] = df['avg_gain'] / df['avg_loss']
        df['RSI'] = 100 - (100 / (1 + df['RS']))
        return df['RSI']
