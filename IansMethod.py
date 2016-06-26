import numpy as np
from matplotlib import pyplot as plt
from yahoo_finance import Share
from datetime import date
import math
from scipy.stats import norm
from scipy.stats import t
from random import shuffle
n = 30	#global variable see line 151 
m = raw_input('"t" distributions or "z" distributions?\nhint: t is more conservative   ') #see line 148-156
#str = raw_input('what is your weighting funtion f(x)= ')
#^^ muted for now, but useful for versatility and felxeblity, this function could be optimized for accuracy, but i havent gotten around to it	
str = "1.22**(-x)"

def calc(val, func):	#evaluates string as mathematical function
    x = val
    return eval(func)

def summation(u,str):
    tot=[]  #defines new empty list
    for i in range(0,u+1):  #for every input, appends the f(input) to the list
        tval =calc(i,str)
        tot.append(tval)
    t=sum(tot)  #takes the sum of the list
    return t

def sign(val):
	if val == 0:
		return 0
	else:
		return val/abs(val)

def StockQuality(x,L,str,v):	#Algorith for measuring stock momentum
#This part is the actual algorithm, and as a coder you probly dont care, 
#also it works very poorly, I didnt come up with it
	ntot = 0
	for n in range(1,L):
		#print 'n = %d' %n
		itot = 0
		for i in range(n):
			ktot = 0
			j = calc(i,str)
			for k in range(0,L-i-n):
				try:
					tval = (v[x-k-i] - v[x-k-n-i]) / (v[x-k-i]*n)
				except IndexError:
					tval = 0
				ktot += tval
			itot += j*ktot
		ntot += itot/summation(n,str)
	mtot = 0
	for n in range(1,L):
		itot = 0
		for i in range(n):
			ktot = 0
			j = calc(i,str)
			for k in range(0,L-i-n):
				try:
					tval = (v[x-k-i] - v[x-k-n-i]) / (v[x-k-i]*n)
				except IndexError:
					yval = 0
				ktot += tval
			itot += j*abs(ktot)
		mtot += itot/summation(n,str)
	if mtot != 0:
		return sign(ntot)*ntot**2/mtot
	else:
		return 0.0

def SQT(x,v,L,val): #The algorithm runs many times for each day up to the chosen date, this "weights" those dates
	tot = 0
	for i in range(1,L):
		tot += StockQuality(x, i, str,v)*(calc(i,str))
	tot = tot*1/(summation(20,str))
	return math.erf(1/math.sqrt(val)*20*tot)*30+70

times = {	#allows user to examine days weeks months or years, 
				#by telling how many steps to take throught the data list,
				#before actually recording an entry
	'D' : 1,
	'W' : 5,
	'M' : 3,
	'Y' : 365,
}

row = "#####################################################"

Monte = raw_input('Run a Monte Carlo test on the data?') #A useful test, that compares the output with outputs of the same algorith acting on randomized data
def Ian():	#function that loops (like a main function)
	run = True	#runnning parameter, failsafe if i missed a break somewhere
	for i in range(50):	#clean things up a bit
		print ''
	print row
	stc = raw_input('Stock Abrieviation (ex= YHOO):   ') #which stock to examine
	print row
	for i in range(50):	#clean things up a bit
		print ''
	print row
	o = raw_input('Daily, Weekly, Monthly or Yearly (D, W, M, Y):   ') #chosing timescale
	print row
	for i in range(50):
		print ''
	print row
	stdate = raw_input('Start date (YYYY-MM-DD)      :   ') #start date of data set, using yahoo_finance module syntax
	print row
	for i in range(50):
		print ''
	print row
	endate = raw_input('End date (YYYY-MM-DD)        :   ')  #end date of data set, using yahoo_finance module syntax
	print row
	for i in range(50):
		print ''
	print row
	stock = Share(stc)	#declaring the stock "Share" is imported from yahoo_finance
	stock.refresh()
	print 'Gathering data, (about a second per month of data)'
	print 'Building Data Structure'
	List = stock.get_historical(stdate, endate)	#actual data gathering
	val = times[o]	
	l = len(List)/val
	v = [0]*l
	for i in range(l):	#reformats the data into a list called v
		v[i] = float(List[i*val]['Open'])
	v = v[::-1]
	while run == True:	#main while loop
		tdate = raw_input('Algorithm value for what day?:   ')	#chosen date to examine momentum on
		if tdate == 'end':	#allows user to break code, useful for diagnostics
			run = False
			break
		"""
		HELP ME:
		i cant find a better way to measure the number of days the stock martket
		is open between start date and chosen date, without making a whole new
		list and measuring it
		"""
		print 'Finding number of market days'
		xList = stock.get_historical(stdate, tdate)
		x = len(xList)/val
		print ''
		for i in range(50): 
			print ''
		print tdate
		print 'ALGORITHM OUTPUT:'
		oval = SQT(x, v, l, val)	#actual algorith usage
		print oval
		if Monte != 'y' or 'Y' or 'Yes' or 'yes':	#for some reason this needed to be here
			pass
		elif Monte == 'y' or 'Y' or 'Yes' or 'yes':	#runnng the monte carlo measurements
			newV = v
			oList = []
			for i in range(n):	#compares output against outputs of the same data set, but in a random order				newV = shuffle(v)
				shuffle(newV)
				oList.append(SQT(l-1, newV, l, val))
			std = np.std(oList)
			mu = np.average(oList)
			zscore = (oval - mu)/std
			tot = 0
			for i in range(l):
				if oval>oList[i]:
					tot += 1
			sampleP = float(tot)/l
			print 'Sample percent lower than original output'	#You wan this to be low for a negative output, or high for a positive output
			print sampleP	#uses sample (of 30) data see globaly defined 'n' to change this number, defined at top of page, 30 is generally safe
			print 'Population percent lower than original based on 1-sample z-test'
			if m == 'z':
				print norm.cdf(zscore)	#some statistics stuff, you probly dont care, unless you wanna chack my stats work
			if m == 't':
				print t.cdf(zscore,n+1)	#if you chose t distributions this one happens, t is probly the right choice given the circumstances
		print''
		print 'enter "end" on the next prompt to quit, and try a new share'
		print row

while 1 != 0:	#always runs!
	Ian()	#main function, named after algorith creator


