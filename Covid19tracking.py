#!/usr/bin/env python
# coding: utf-8

# ## Assignment 1
# Qi Liu 
# 20201004

# In[1]:


# Import some necessary modules first
import requests
import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
get_ipython().run_line_magic('matplotlib', 'inline')


# # Part 1: Identify suitable web APIs and collect data
# 
# The first and main data which I choose is about COVID-19 situation in the U.S., and it is completely open, no need to apply for API.

# In[ ]:





# In[2]:


url = 'https://api.covidtracking.com/v1/us/daily.json'
# Using *try...except** statements to find errors
try: 
    get_data=requests.get(url).json()
    raw_data=pd.DataFrame(get_data)
except:
    print("Failed to retrieve %s" % url)


# In[5]:


# Show the first few rows of the data
raw_data.head(3)


# # Part 2: Parse the collected data, and store it in an appropriate file format

# In[7]:


# Show the attributes of all columns of this data
print(raw_data.columns.tolist())


# <font color=red size=3 >  Start pre-processing raw data:

# In[8]:


# according to the description on the website （https://covidtracking.com/data/api)
# the following items are not recommended: dateChecked, hospitalization, lastModified, total, posNeg, hash
# besides, I found that all the values in the column 'recovered' are none
raw_data['recovered'].notnull().sum() # looking for missing data


# In[11]:


# So delete these useless data
deprecated=["dateChecked","hospitalized","lastModified","recovered","total","posNeg","hash"]
data=raw_data.drop(deprecated,axis=1)
# Make data cleaner and easy to operate
data=data.fillna(0) # filling for missing data
data=data.astype(int) # converse the data format


# <font color= blue> Here is a simple small function which make convenient to check the specific daily situation.

# In[12]:


def case(date):
    try:
        case_data=data.set_index("date") # change the data index
        positive_case = case_data['positive'][date] # extract data that people are interested in
        death_case=case_data['death'][date]
        increase_positive=case_data['positiveIncrease'][date]
        increase_death=case_data['deathIncrease'][date]
        print("date:%s" % date) # print the results of this function
        print("total cases is %s" % positive_case)
        print("the new cases yesterday is %s" % increase_positive)
        print("total death case is %s" % death_case)
        print("the new death cases is %s" % increase_death)
    except KeyError:
        print("Please check the input date")


# In[13]:


case(20210301)


# # Part 3: Represent, analyse the data
# Load and represent the data using an appropriate data structure. Apply any pre-processing steps to clean/filter/combine the data. Analyse and summarise the cleaned dataset.

# <font color = blue size = 4> In the first part, I put forward and analyzed five aspects that I am interested in

# <font color= red> 01 Find the first day when COVID-19 appeared in half and all states/territories in the United States:

# In[33]:


# before that, find the first day of the case
data.query('positive==1').head(1)


# According to this data, the first case occurred in the United States on 01/19/2020

# In[32]:


data=data.sort_values('date') # change date sort
# the date when the cases appear to (more than) half region of the U.S.
data.query('states>27').head(1) # The data counts 56 states and territories in the United States


# Cases occurred in (more than) half of the states on 03/05/2020, the number is 305.

# In[29]:


data.query('states>55').head(1) # Find the first day in more than 55 states


# There have been cases in every state in the U.S. since 03/16/2020,the number is 7377.

# <font color = blue> As can be seen it took less than a month for the case to spread from one state to half of the country, and it took less than 10 days to spread to the whole country.

# <font color= red> 02 Find the days when cases are increasing quickly:

# In[17]:


data['speed']=data['positiveIncrease']/data['positive'] # define the speed of infection according to this formula
data.sort_values('speed',ascending=False).head(10)['date'] # sort in descending order and view the top ten


# It can be seen that the fastest increase in the five days of cases is as above.

# <font color = red> 03 Find the day when the number of cases in a single day is greater than 10000:

# In[404]:


TenThousand=data[data['positiveIncrease']>100000]


# In[405]:


TenThousand.sort_values(by=['positiveIncrease'],ascending=False)


# The number of new cases per day exceeds 10,000 in these total of 99 days, the detailed data is as above.

# <font color = red> 04 Find the day when the number of death cases in a single day is greater than 5000：

# In[406]:


data[data['deathIncrease']>5000]


# The number of death cases per day exceeds 5,000 in these two days, the detailed data is as above.

# <font color = red> 05 Calculate the number of days for cases with positive results more than cases with negative results:

# In[35]:


data.loc[lambda x:x['positiveIncrease']>x['negativeIncrease']]


# In[ ]:


data.loc[lambda x:x['positiveIncrease']>x['negativeIncrease']].date.count()


# In the past year or so, there were more positive cases than negative cases for 25 days.

# ## Part 4: Data visualization - Matplotlib and Pandas Graphing
# 
# In this section, mainly analyze and view data monthly

# <font color = red> Parse data as required:

# In[36]:


# Convert specific dates to months
data['month']=[x[:6] for x in data['date'].astype(str)]
month_data=data.groupby("month").sum() # summarize data group by month
month_data=month_data.drop(["date","states"],axis=1) # drop meaningless data
month_data=month_data.drop(['202103'],axis=0) # drop incomplete data: cannot be collected because it has not happened yet
month_data.head(5)


# <font color =red> Overview of monthly data:

# In[74]:


# Plot the cases and deaths for each month
month_data[['positive','death']].plot(figsize=(15,10),linewidth=2.5)
plt.ylabel('cases')
plt.title('monthly cases',fontsize=14)


# In[77]:


# Plot the number of cases admitted to hospital for treatment each month
# included in the number of  in ICUs and on ventilators
month_data_treatment=month_data[["hospitalizedCurrently","inIcuCurrently","onVentilatorCurrently"]] # collect the required data
month_data_treatment.plot(kind="bar",stacked=True,figsize=(15,10),color=['green','maroon','orange']) # plot stacked bar plots
plt.title('The number of cases admitted to hospital treatment each month',fontsize=14)


# In[79]:


# Plot small multiples for monthly increase cases of different types
# Visualise the relationship between all pairs of columns
month_data_increase=month_data[["deathIncrease","hospitalizedIncrease","negativeIncrease","positiveIncrease","totalTestResultsIncrease"]]
from pandas.plotting import scatter_matrix
scatter_matrix(month_data_increase,figsize=(15,15)) # show the distribution of values for each of the individual features


# <font color=red> Further analysis of monthly increase:

# The increase numbers and increase rates are plotted here since considering the difference in the number of basic cases, due to the two pandemic outbreak waves.
# 
# And plot the two kinds of data on one graph for comparison.

# In[69]:


# Define the increase rate
month_data['rate']=month_data['positiveIncrease']/month_data['positive']
month=month_data.index.get_level_values(0) # extract the index value, month, as the axis ticks of the graph
month=month.astype(int) # convert the data format
ax1 = month_data['rate'].plot(x="month", kind="line",figsize=(20,8),color='coral',linewidth=3) # plot the increase rate graph
ax1.set_xticks(month.values)
ax1.set_ylabel("Increase rate")
ax1.set_xlabel("Month")
plt.legend('rate',loc=2)
ax2 = ax1.twinx() # plot the second graph on the basis of the previous one, so need to share the x-axis
month_data['positiveIncrease'].plot(x="month", kind="bar", ax=ax2) # plot the increase graph
ax2.set_ylabel("Increase number")
plt.title("cases increase and its rate",fontsize=18) # make it clearer and more aesthetic
plt.legend('number',loc=3)
plt.show()


# The data in March and December have increased significantly. 
# 
# Verify whether these two months can be recognised as the key months for the two waves of pandemics:

# In[42]:


# Find the month with the highest increase rate
max_rate=month_data['rate'].max() 
month_data[month_data['rate']==max_rate]


# In[415]:


# Find the month with the highest increase number
max_increase=month_data['positiveIncrease'].max() 
month_data[month_data['positiveIncrease']==max_increase]


# The data of March and December are indeed important.

# <font color=red> So specifically analyze the data of these two months:

# In[71]:


Mar=data[data["date"].between(20200301,20200331)] # extract data for March
Mar=Mar.set_index("date") # set date as the index
Dec=data[data["date"].between(20201201,20201231)] # extract data for December
Dec=Dec.set_index("date") # set date as the index


# In[73]:


# Analyze the number and rate of increase in cases in the past two months
Mar['increase_rate']=Mar['positiveIncrease']/Mar['positive'] # define the cases increase rate of March and then plot it
Mar[['positiveIncrease','deathIncrease','increase_rate']].plot(subplots=True,layout=(1,3),figsize=(15,4),sharey=False,linewidth=2.5,ylabel="numbers") # show the graphs separately, and do not share the y-axis
plt.suptitle("data of March")
Dec['increase_rate']=Dec['positiveIncrease']/Dec['positive'] # define the cases increase rate of March and then plot it
Dec[['positiveIncrease','deathIncrease','increase_rate']].plot(subplots=True,layout=(1,3),figsize=(15,4),sharey=False,linewidth=2.5,ylabel="numbers") # show the graphs separately, and do not share the y-axis
plt.suptitle("data of December")


# The increase in the number of cases in March is stable, and the increase rate is gradually decreasing.
# 
# The number of cases in December grew unstable, but the overall value was high. And the increase rate was also unstable, but the rate was lower than in March.
# 
# The reasons for these differences may be that the basic cases in the two months are different and they are in different stages of the pandemic respectively.

# # Part 5: Collect other data and compare
# 
# Obtain COVID-19 data from the UK government website: https://coronavirus.data.gov.uk/details/developers-guide

# In[81]:


# Collect data using recommended modules
from requests import get


def get_data(url):
    response = get(endpoint, timeout=10)
    
    if response.status_code >= 400:
        raise RuntimeError(f'Request failed: { response.text }')
        
    return response.json()
    

if __name__ == '__main__':
    endpoint = (
        'https://api.coronavirus.data.gov.uk/v1/data?'
        'filters=areaType=nation;areaName=england&'
        'structure={"date":"date","newCases":"newCasesByPublishDate"}'
    )
    
    data = get_data(endpoint)

dataUK=pd.DataFrame(data['data'])
dataUK.head(5)


# <font color=red> Compare UK data with US data by month:

# In[83]:


dataUK['month']=[x[:7] for x in dataUK['date'].astype(str)] # convert the data format and pre-processing
month_dataUK=dataUK.groupby("month").sum() # group data by month
month_dataUK=month_dataUK.drop(['2021-03'],axis=0) # drop incomplete data: cannot be collected because it has not happened yet


# In[96]:


# Unify the index of the two sets of data in order to merge the data
# Extract the index of UK data before that
compare_month=month_dataUK.index.get_level_values(0)


# In[97]:


# Represent the US data using the same data structure
month_dataUS=month_data['positiveIncrease']
month_dataUS.index=compare_month


# In[107]:


# Merge these two dataset
comparison=pd.concat([month_dataUS, month_dataUK], axis=1)
comparison.rename(columns={'positiveIncrease':'US', 'newCases':'UK'}, inplace = True) # rename the columns
comparison


# In[109]:


# Plot two data for comparison
vs=comparison.plot(figsize=(20,8),linewidth=3)
vs.set_title("Comaparison of New Cases in US and UK",fontsize=14)
vs.set(xlabel="Month", ylabel="New Cases")

