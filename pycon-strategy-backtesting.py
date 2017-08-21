import datetime as dt
import pandas
from matplotlib import animation
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from IPython.display import HTML
import time


PATH_DATA_POINTS = r'pycon-tatasteel-data.csv'

class AlgoTrading:
    def __init__(self, sampling_points=-1):
        self.sampling_points = sampling_points
        self.buy_trades = []
        self.sell_trades = []
        self.collect_data()
        self.initialize_crossover()
        self.trade_history = []
        self.qty = 0
        self.previous_profit_percent = 0

    def collect_data(self):
        self.csv = pandas.read_csv(PATH_DATA_POINTS)
        self.dates = [dt.datetime.strptime(date,'%d/%m/%y %H:%M') for date in self.csv['Date']][::-1][:self.sampling_points]
        self.data_points = self.csv['TATASTEEL-EQ C'].tolist()[::-1][:self.sampling_points]

    def update_trade_history(self, stock_price, trade_buy=False, trade_sell=False, profit_percent=-1):
        "Should be called on every data point processed"
        if trade_buy:
            self.qty += 1
            pp = profit_percent
        elif trade_sell:
            self.qty -= 1
            pp = profit_percent
        else:
            pp = self.previous_profit_percent
        self.trade_history.append({'stock_price': stock_price,
                                   'quantity': self.qty,
                                   'profit_percent': pp
                                    })
        self.previous_profit_percent = pp

    def sma(self, data, window):
        """
        Calculates Simple Moving Average
        http://fxtrade.oanda.com/learn/forex-indicators/simple-moving-average
        """
        if len(data) < window:
            return None
        return sum(data[-window:]) / float(window)
    
    def ema(self, data, window):
        if len(data) < 2 * window:
            raise ValueError("data is too short")
        c = 2.0 / (window + 1)
        current_ema = self.sma(data[-window*2:-window], window)
        for value in data[-window:]:
            current_ema = (c * value) + ((1 - c) * current_ema)
        return current_ema

    def initialize_crossover(self):
        self.prev_val1 = 0
        self.prev_val2 = 0

    def crossover(self, val1, val2):
        cmp1 = cmp(val1, val2)
        cmp2 = cmp(self.prev_val1, self.prev_val2)
        if (not (self.prev_val1 == 0 and self.prev_val2 == 0)):         # don't trigger crossover when called first time
            self.prev_val1, self.prev_val2 = val1, val2
            if cmp1 > cmp2:
                return 1
            elif cmp1 < cmp2:
                return -1
            else:
                return 0
        else:
            self.prev_val1, self.prev_val2 = val1, val2
            return 0

    def strategy1(self):
        for i, data in enumerate(self.data_points):
            crossover = 0
            profit_percent = 0
            if i >= 29:      # ema(15) needs atleast 30 points
                crossover = self.crossover(self.ema(self.data_points[:i+1], 3), self.ema(self.data_points[:i+1], 15))
                if (crossover == 1):
                    # Buy crossover
                    print "Buy (Value: %.2f)" % data
                    self.buy_trades.append(data)
                elif (crossover == -1):
                    # Sell crossover
                    print "Sell (Value: %.2f)" % data
                    self.sell_trades.append(data)

                # If crossover happens...
                if (crossover is not 0):
                    buy_qty = len(self.buy_trades)
                    sell_qty = len(self.sell_trades)
                    qty = min(buy_qty, sell_qty)
                    if qty:
                        sell = sum(self.sell_trades[:qty])
                        buy = sum(self.buy_trades[:qty])
                        profit = sell - buy
                        profit_percent = profit*100.0/(buy/len(self.buy_trades))
    #                    self.profit_percents.append(profit_percent)
    #                print 'Buy_qty:%s, Sell qty:%s, Min qty:%s' %(buy_qty, sell_qty, qty)
    #                print 'Buy trades:', [("%.2f" % trade) for trade in self.buy_trades[:qty]]
    #                print 'Sell trades:', [("%.2f" % trade) for trade in self.sell_trades[:qty]]
    #                print 'Total buy: %s' % buy
    #                print 'Total sell: %s' % sell
    #                print 'Total profit: %s' % profit
    #                print 'Total profit_percent: %s' % profit_percent
                        yield profit_percent

            # update history
            self.update_trade_history(data, crossover == 1, crossover == -1, profit_percent)

    def trade(self):
        for profit_percent in self.strategy1():
            print profit_percent

    def animate(self):
        """
        Animates 2 plots -
        1. Stock Price vs Date
        2. Profit percentage vs Date

        Speed of animation can be controlle by playing with 3rd argument of xrange
        """
        df = pandas.DataFrame(self.trade_history)

        plt.ion()
        plt.figure(1)
        plt.hold(True)
        ylim1_min = min(df['stock_price'])
        ylim1_max = max(df['stock_price'])
        ylim2_min = min(df['profit_percent'])
        ylim2_max = max(df['profit_percent'])

        for i in xrange(0, df.shape[0], df.shape[0]/100):
            # Stock price
            plt.subplot(211).cla()
            plt.ylabel('Stock price')
            plt.xlim([self.dates[0], self.dates[-1]])
            plt.ylim([ylim1_min, ylim1_max])
            plt.plot(self.dates[:i], df['stock_price'][:i], color='b')

            # Percentage profit
            plt.subplot(212).cla()
            plt.xlim([self.dates[0], self.dates[-1]])
            plt.ylim([ylim2_min, ylim2_max])
            plt.ylabel('Percentage profit')
            plt.xlabel('Date')
            plt.plot(self.dates[:i], df['profit_percent'][:i], color='b')

            plt.pause(0.01)

            if i == 0:
                time.sleep(5)

        while True:
            time.sleep(1)

    def plot(self):
        """
        Creates 2 plots -
        1. Stock Price vs Date
        2. Profit percentage vs Date
        """

        df = pandas.DataFrame(self.trade_history)

        ylim1_min = min(df['stock_price'])
        ylim1_max = max(df['stock_price'])
        ylim2_min = min(df['profit_percent'])
        ylim2_max = max(df['profit_percent'])

        # Stock price
        plt.subplot(211)
        plt.ylabel('Stock price')
        plt.xlim([self.dates[0], self.dates[-1]])
        plt.ylim([ylim1_min, ylim1_max])
        plt.plot(self.dates, df['stock_price'], color='b')

        # Percentage profit
        plt.subplot(212).cla()
        plt.xlim([self.dates[0], self.dates[-1]])
        plt.ylim([ylim2_min, ylim2_max])
        plt.ylabel('Percentage profit')
        plt.xlabel('Date')
        plt.plot(self.dates, df['profit_percent'], color='b')

        plt.show()


if __name__ == "__main__":
    algotrading = AlgoTrading()
    algotrading.trade()
    algotrading.plot()
#    algotrading.animate()
