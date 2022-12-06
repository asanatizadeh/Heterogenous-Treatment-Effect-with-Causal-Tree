import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tqdm import tqdm
import numpy as np

tqdm.pandas()

# load vader analyzer
analyzer = SentimentIntensityAnalyzer()

# read review file
all_reviews = pd.read_excel('L0- all reviews.xlsx')
# read links to review and merge them with the reviews
all_links = pd.read_csv('L0- User Review Links.csv', delimiter="|")
reviews_with_username = all_reviews.merge(all_links, left_on='url', right_on='user_review_links')

# load the activity data
L0_match = pd.read_csv('L0.csv')

# drop useless variables
reviews_with_username.drop(columns='user_review_links', inplace=True)
# drop missing text reviews
reviews_with_username.dropna(subset=['review_text'], inplace=True)
# reset index
reviews_with_username.reset_index(drop=True, inplace=True)
# calcuate the sentiment of review text
reviews_with_username['sentiment'] = \
    reviews_with_username['review_text'].progress_apply(lambda x: analyzer.polarity_scores(x))
# normalize and merge the sentiment json
reviews_with_sentiment = reviews_with_username.join(pd.json_normalize(reviews_with_username['sentiment']))
reviews_final = reviews_with_sentiment.merge(L0_match[['user_profile', 'activity', 'propensity_score','propensity_logit', 'matched_id', 'gender_c','user_id','member_y','treated'
                                                       ,'user_location_c', 'index']], on='user_profile')
reviews_final.sort_values(by=['username', 'review_date'], inplace=True)
reviews_final.reset_index(drop=True, inplace=True)
reviews_final['accu_reviews'] = reviews_final.groupby(['username']).cumcount().apply(lambda x: x+1)
reviews_final['event'] = 1
reviews_final['event'] = reviews_final['event'].where(reviews_final['accu_reviews'] > reviews_final['activity'], 0)

reviews_final['event'].value_counts()

#reviews_final.to_csv("L0_review_sent.csv")

# balance prior event number of reviews with post event
l0_review_sent = pd.read_csv('l0_review_sent.csv')

l0_review_sent.sort_values(by=['user_profile', 'event'], inplace=True)

l0_review_sent['accu_review_0'] = l0_review_sent.groupby(['user_profile', 'event']).cumcount().apply(lambda x: x+1)

l0_review_sent2 = l0_review_sent.loc[l0_review_sent['accu_review_0'] <= l0_review_sent['activity']]
l0_review_sent2.user_profile.nunique()

l0_review_sent2.to_csv("l0_review_sent2.csv")
