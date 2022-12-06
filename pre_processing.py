import pandas as pd
from psmpy import PsmPy
from psmpy.functions import cohenD
from psmpy.plotting import *
from sklearn.preprocessing import OrdinalEncoder
from sklearn.linear_model import LogisticRegression

from sklearn.neighbors import NearestNeighbors
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
from pymatch.Matcher import Matcher

ord_enc = OrdinalEncoder()

df = pd.read_csv("all_sentiments_press_no_text2_2.csv")
df_1= df.groupby('ReviewerProfile').mean()
df_1= df_1.reset_index()
######

df2= pd.read_csv("Alluser_info_complete.csv")
df2.rename(columns= {'reviewerprofile': "ReviewerProfile"},inplace=True)
df2.rename(columns= {'firsname': "firstname"},inplace=True)

#data= df2.merge(df_1, on= 'ReviewerProfile', how='left')
data=df2
data['gender'].nunique()
data['gender'].unique()

data.columns
data["activity"]= None

# for matching only
data1 = data[['user_profile','joined_y', 'user_location', 'gender', "activity"]]

#data1['treated']= 0gender_c
data1['member_y']= 2022- data1['joined_y']

data1['gender_c'] = None
for i in range(len(data1['gender'])):
    if data1['gender'][i] == "unknown":
        data1['gender_c'][i] =0

    elif data1['gender'][i] == "mostly_male":
        data1['gender_c'][i] =1
    elif data1['gender'][i] == "male":
        data1['gender_c'][i] =1

    elif data1['gender'][i] == "mostly_female":
        data1['gender_c'][i] =2
    elif data1['gender'][i] == "female":
        data1['gender_c'][i] =2

    elif data1['gender'][i] == "andy":
        data1['gender_c'][i] =1

    elif data1['gender'][i] == "nan":
        data1['gender_c'][i] =0

    else:
        pass

data1.drop('gender', inplace=True, axis=1)
data1['gender_c'].unique()

data1['treated']= 0



####################################################################

df3 = pd.read_csv("treated_users.csv")
df3= df3[df3['treated']==0] #choose only previous control as treated
df3['ReviewerProfile'] = df3['user_profile'].apply(lambda x: "/Profile/"+x)

data2= df3.merge(df_1, on= 'ReviewerProfile', how='left')
data2.columns

data2_1 = data2[['user_profile', 'user_location','joined_y', 'gender2', "activity"]]

data2_1['member_y']= 2022- data2_1['joined_y']

data2_1['gender_c'] = None

for i in range(len(data2_1['gender2'])):
    if data2_1['gender2'][i] == "unknown":
        data2_1['gender_c'][i] =0

    elif data2_1['gender2'][i] == "male":
        data2_1['gender_c'][i] =1

    elif data2_1['gender2'][i] == "female":
        data2_1['gender_c'][i] = 2

    elif data2_1['gender2'][i] == "nan":
        data2_1['gender_c'][i] =0
    else:
        pass

data2_1['gender2'].unique()
data2_1.drop('gender2', inplace=True, axis=1)

data2_1['treated']= 1


################################################################################################
# start the matching based on users' characteristics
#https://matheusfacure.github.io/python-causality-handbook/11-Propensity-Score.html
#https://towardsdatascience.com/psmpy-propensity-score-matching-in-python-a3e0cd4d2631

## sanity check: remove overlap
for i in data2_1['user_profile']:
    if i in data1['user_profile']:
        print(i)
    else:
        pass

######

df_20 = pd.concat((data2_1, data1), axis= 0)
df_20.reset_index(inplace=True)
df_20= df_20.iloc[: , 1:]
df_20.reset_index(inplace=True)
df_20.rename(columns={'index': 'user_id'}, inplace=True)
df_20.reset_index(inplace=True)

df_20["user_location"].nunique()
df_20["user_location_c"] = ord_enc.fit_transform(df_20[["user_location"]])

len(df_20['user_id'])
df_20['user_id'].nunique()
#df_20.to_csv("df_20.csv")
df_20.treated.unique()

categ= df_20[['user_profile','member_y', 'treated', 'gender_c', 'user_location_c']]
categ.dropna(inplace=True)
categ= categ.reset_index()

T = 'treated'
X= ['member_y', 'gender_c']
ps_model = LogisticRegression(C=1e6).fit(categ[X], categ[T])
df_ps= categ.assign(propensity_score=ps_model.predict_proba(categ[X])[:, 1])

df_ps['propensity_score'].nunique()

### Algorithm 2

categ1 = df_20[['member_y', 'treated', 'gender_c','user_location_c', 'user_id']]
categ1.dropna(inplace=True)
categ1['user_id'] = categ1['user_id'].apply(lambda x: int(x))
categ1['treated'] = categ1['treated'].apply(lambda x: int(x))
categ1['gender_c'] = categ1['gender_c'].apply(lambda x: int(x))
categ1['member_y'] = categ1['member_y'].apply(lambda x: int(x))
categ1['user_location_c'] = categ1['user_location_c'].apply(lambda x: int(x))

psm = PsmPy(categ1, treatment='treated', indx='user_id')
psm.logistic_ps(balance = True)
psm.predicted_data

#psm.knn_matched(matcher='propensity_logit', replacement=False, caliper=0.25)
#l=psm.df_matched

psm.knn_matched_12n(matcher='propensity_logit', how_many=1)
categ2= psm.df_matched
categ2[categ2['user_id']==2049]
categ2['propensity_score'][0]
categ2[categ2['propensity_score'] == 0.25678909625103746]

l1= psm.matched_ids # all ids matched
l1.reset_index(inplace=True)
l1.rename(columns={'index': 'matched_id'}, inplace=True)

list= l1['user_id'].append(l1['largerclass_0group'])
list2= l1['matched_id'].append(l1['matched_id'])

list= pd.DataFrame(list)
list.rename(columns={0: 'user_id'}, inplace=True)
list2= pd.DataFrame(list2)

list3= pd.concat((list, list2), axis=1).reset_index()
list3.drop('index', axis=1, inplace=True)


categ3 =categ2.merge(list3, on= 'user_id', how='left')
categ3[categ3['matched_id']==1]


categ4= categ3.merge(df_20[['user_id', 'user_profile', 'activity']], on= 'user_id', how='left')
categ4.to_csv('categ4.csv')

#############
categ4= pd.read_csv("categ4.csv")
categ4['user_url_review']= categ4['user_profile'].apply(lambda x: "https://www.tripadvisor.com/Profile/" + str(x)+"?tab=reviews")
categ4['user_url_review'][0]

L1= categ4[categ4['treated']==1].reset_index()
L0= categ4[categ4['treated']==0].reset_index()


for i in range(len(L1)):
    for j in range(len(L0)):
        #print(i,j)
        if L1.matched_id[i]== L0.matched_id[j]:
            L0['activity'][j]= L1['activity'][i]
        else:
            "None"

L0.to_csv("L0.csv")
L1.to_csv("L1.csv")
##############################################
#collect reviews for l0
L0_sent= pd.read_csv("L0_review_sent2.csv", encoding="utf-8")

l0_review = L0_sent[['review_date','matched_id'
       , 'review_rating', 'user_profile',
       'Review_ID',
        'neg', 'neu', 'pos', 'compound','event', 'treated',
                     'propensity_score', 'gender_c', 'member_y', 'user_location_c']]

l0_review.rename(columns= {'Review_ID': 'reviewid'}, inplace=True)
l0_review.treated.unique()

unique_matched= l0_review['matched_id'].unique()
unique_matched=pd.DataFrame(unique_matched)
unique_matched.rename(columns={0: "matched_id"}, inplace=True)

L1=pd.read_csv("L1.csv")

#drop matched id not exist in l1:
l1_user= L1.merge(unique_matched, on='matched_id', how='inner')
l1_user.user_profile.nunique()

#l1_user.drop('Unnamed: 0', inplace=True, axis=1)
# collect all reviews for l1
df= pd.read_csv("treated.csv")
df= df[['user_profile',
         'reviewid','neg', 'neu', 'pos', 'compound',
       'review_dateMDY','review_rating', 'event', 'treated', 'activity']]
df.treated.unique()
l1_review= df.merge(l1_user[['user_profile', 'matched_id',
                     'propensity_score', 'gender_c', 'member_y', 'user_location_c']], on= 'user_profile', how='right')
l1_review.user_profile.nunique()
l1_review.event.value_counts()
l1_review.rename(columns={'review_dateMDY': 'review_date'}, inplace=True)


#make balance between pre and post number of reviews

l1_review.sort_values(by=['user_profile', 'event'], inplace=True)

l1_review['accu_review_0'] = l1_review.groupby(['user_profile', 'event']).cumcount().apply(lambda x: x+1)

l1_review2 = l1_review.loc[l1_review['accu_review_0'] <= l1_review['activity']]
l1_review2.user_profile.nunique()

l1_review2.drop('activity', inplace=True, axis=1)
l1_review2.drop('accu_review_0', inplace=True, axis=1)


l1_review = l1_review2


l1_review.columns
l0_review.columns

l1_review.user_profile.nunique()
len(l1_review)

l0_review.user_profile.nunique()
len(l0_review)

final_data= pd.concat((l1_review, l0_review), axis=0)
final_data.event.value_counts()
final_data.describe()

final_data['user_id']= final_data['user_profile'].rank(method= 'dense').astype(int)
final_data.to_csv("final_data2.csv")

