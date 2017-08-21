import datetime as dt
import pandas
from matplotlib import animation
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from IPython.display import HTML
import time


PATH_DATA_POINTS = r'pycon-tatasteel-data.csv'

class plot_algotrading:
    
    def __init__(self, sampling_points = -1):
        self.sampling_points = sampling_points
        self.collect_data()
        self.plot_initialize()
#        self.animate()

    def collect_data(self): 
        self.csv = pandas.read_csv(PATH_DATA_POINTS)
        self.dates = [dt.datetime.strptime(date,'%d/%m/%y %H:%M') for date in self.csv['Date']][::-1][:self.sampling_points]
        self.closing_values_tatasteel = self.csv['TATASTEEL-EQ C'].tolist()[::-1][:self.sampling_points]

    def plot_initialize(self):
        plt.xlim([self.dates[0], self.dates[-1]])
        plt.ylim([min(self.closing_values_tatasteel), max(self.closing_values_tatasteel)])
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%y'))  # will show date in this format
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())   # Will only show months
        plt.gca().grid()
        #plt.gca().set_xticks(xrange(0,len(dates), 5)) 
        #plt.gca().set_xticklabels(dates)     # set the ticklabels to the list of datetimes
        plt.xticks(rotation=30)       # rotate the xticklabels by 30 deg
        plt.ion()

    def plot(self, len_data):
        dates_for_plotting = self.dates[:len_data]
        values = self.closing_values_tatasteel[:len_data]
        plt.plot(dates_for_plotting, values, color='b')

    def animate(self):
        for i in xrange(1,130):
            j = i*100
            self.plot(j)
            plt.pause(0.05)

    def check_buy(self):
        pass

    def check_sell(self):
        pass


class AlgoTrading:
    def __init__(self, sampling_points=-1):
        self.sampling_points = sampling_points
        self.buy_trades = []
        self.sell_trades = []
        self.collect_data()
        self.initialize_crossover1()
        self.initialize_crossover2()

    def collect_data(self):
        self.csv = pandas.read_csv(PATH_DATA_POINTS)
        self.data_points = self.csv['TATASTEEL-EQ C'].tolist()[::-1][:self.sampling_points]

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

    def initialize_crossover1(self):
        self.prev_val1 = 0
        self.prev_val2 = 0

    def crossover1(self, val1, val2):
        cmp1 = cmp(val1, val2)
        cmp2 = cmp(self.prev_val1, self.prev_val2)
        if (not (self.prev_val1 == 0 and self.prev_val2 == 0)):         # don't trigger crossover when called first time
            self.prev_val1, self.prev_val2 = val1, val2
            if cmp1 > cmp2:
                return True
            else:
                return False
        else:
            self.prev_val1, self.prev_val2 = val1, val2
            return False

    def initialize_crossover2(self):
        self.prev_val3 = 0
        self.prev_val4 = 0

    def crossover2(self, val3, val4):
        cmp1 = cmp(val3, val4)
        cmp2 = cmp(self.prev_val3, self.prev_val4)
        if (not (self.prev_val3 == 0 and self.prev_val4 == 0)):         # don't trigger crossover when called first time
            self.prev_val3, self.prev_val4 = val3, val4
            if cmp1 > cmp2:
                return True
            else:
                return False
        else:
            self.prev_val3, self.prev_val4 = val3, val4
            return False

    def trade(self):
        for i,data in enumerate(self.data_points):
            if i >=29:      # ema(15) needs atleast 30 points
                # Buy crossover
                if self.crossover1(self.ema(self.data_points[:i+1], 3), self.ema(self.data_points[:i+1], 15)):
                    print "Buy (Value: %.2f)" % data
                    self.buy_trades.append(data)

                # Sell crossover
                if self.crossover2(self.ema(self.data_points[:i+1], 15), self.ema(self.data_points[:i+1], 3)):
                    print "Sell (Value: %.2f)" % data
                    self.sell_trades.append(data)

#        print 'Final numbers:'
        buy_qty = len(self.buy_trades)
        sell_qty = len(self.sell_trades)
        qty = min(buy_qty, sell_qty)
        sell = sum(self.sell_trades[:qty])
        buy = sum(self.buy_trades[:qty])
        profit = sell - buy
        profit_percent = profit*100.0/(buy/len(self.buy_trades))
        print 'Buy_qty:%s, Sell qty:%s, Min qty:%s' %(buy_qty, sell_qty, qty)
        print 'Buy trades:', [("%.2f" % trade) for trade in self.buy_trades[:qty]]
        print 'Sell trades:', [("%.2f" % trade) for trade in self.sell_trades[:qty]]
        print 'Total buy: %s' % buy
        print 'Total sell: %s' % sell
        print 'Total profit: %s' % profit
        print 'Total profit_percent: %s' % profit_percent

        return profit_percent


if __name__ == "__main__":
    #    import sys
    #no = int(sys.argv[1])
    #    p = plot_algotrading(1125)

    
    algotrading = AlgoTrading()
    print algotrading.trade()
    raise SystemExit
    y = []
    x = xrange(101,15001, 100)
    for x_ in x:
        algotrading = AlgoTrading(x_)
        profit = algotrading.trade()
        y.append(profit)
        print profit
    
    plt.plot(x,y)
    plt.show()


#    while True:
#        time.sleep(100)

