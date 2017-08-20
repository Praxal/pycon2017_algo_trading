import datetime as dt
import pandas
from matplotlib import animation
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from IPython.display import HTML
import time


class plot_algotrading:
    
    def __init__(self):
        self.path = r'pycon-tatasteel-data.csv'
        self.collect_data()
        self.plot_initialize()
        self.animate()

    def collect_data(self): 
        self.csv = pandas.read_csv(self.path)
        self.dates = [dt.datetime.strptime(date,'%d/%m/%y %H:%M') for date in self.csv['Date']][::-1]
        self.closing_values_tatasteel = self.csv['TATASTEEL-EQ C'].tolist()[::-1]

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
        for i in xrange(1,13):
            j = i*1000
            self.plot(j)
            plt.pause(0.05)


class Indicators:
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




if __name__ == "__main__":
    plot_algotrading()
    while True:
        1 ==1 

