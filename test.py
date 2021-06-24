
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

combinedDataFrame = pd.DataFrame()


item1 = {'PLTR': 244, 'ARVL': 22, 'WKHS': 20743, 'TLRY': 755}
item2 = {'PLTR': 344, 'ARVL': 233, 'WKHS': 2074, 'TLRY': 75234}
item3 = {'PLTR': 2342, 'ARVL': 2342, 'WKHS': 203, 'TLRY': 7234}
item4 = {'PLTR': 24, 'ARVL': 34, 'WKHS': 20, 'TLRY': 7544}

itemList = [item1,item2,item3,item4]

concatenatedDf = pd.DataFrame()

for item in itemList:
    df = pd.DataFrame(item, index = [0])
    concatenatedDf = pd.concat([concatenatedDf, df], axis=1)

df = (pd.melt(concatenatedDf)
.rename(columns={
'variable' : 'Stock Ticker',
'value' : 'Number of Occurences'}))

aggregation_functions = {'Stock Ticker': 'first' , 'Number of Occurences': 'sum'}

df = df.groupby('Stock Ticker', as_index=False).agg(aggregation_functions)

highestOccuring = df.sort_values('Number of Occurences', ascending = False).head()

print(highestOccuring)

plt.bar(highestOccuring['Stock Ticker'], highestOccuring['Number of Occurences'])
plt.show()


print(str(date.today()) + ' hi')



#df.pivot(columns = 'val')
#print(emptyDataFrame.head())