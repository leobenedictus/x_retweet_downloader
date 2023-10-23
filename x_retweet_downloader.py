# from twitter.scraper import Scraper
import requests
import pandas as pd
import streamlit as st


# WARNING

st.header("X retweet downloader")

# tweet url needs to have the id number at the end (you can see this url by clicking on the date of the tweet)
url = st.text_input("", "tweet url")

st.write("Currently does not include quote-tweets. Please check reweets before using. ")

# Waits for an input with a tweet 
while "twitter.com" not in url:
     continue

## sign-in with credentials
email, username, password = st.secrets["email", "username", "password"]

scraper = Scraper(email, username, password)

# receive tweet address and strip off any query string
tweet_address = url.split("?")[0]

# get tweet id
tweet_id = tweet_address.split("/")[-1]

# get data
retweeters = scraper.retweeters([tweet_id])

# Pulls out all the items in the API response
raw_user_list = []
for x in retweeters:
    for y in x["data"]['retweeters_timeline']["timeline"]["instructions"][0]["entries"]:
        user = y["content"]
        raw_user_list.append(user)

# Removes all the non-user items
filtered = [i for i in raw_user_list if i['entryType'] == 'TimelineTimelineItem'] 

# Removes the empty items
filtered_again = [i for i in filtered if i['itemContent']["user_results"]] 
filtered_yet_again = [i for i in filtered_again if i['itemContent']["user_results"]["result"]["__typename"] == "User"] 

# extract data on each retweeter
rts_dict = {"screen_name":[], "name":[], "description":[], "url":[], "followers":[], "tweets":[], "verified":[]}

counter = 0
for f in filtered_yet_again:
    rts_dict['screen_name'].append(f["itemContent"]["user_results"]["result"]["legacy"]["screen_name"])
    rts_dict["name"].append(f["itemContent"]["user_results"]["result"]["legacy"]["name"])
    rts_dict["description"].append(f["itemContent"]["user_results"]["result"]["legacy"]["description"])
    rts_dict["followers"].append(f["itemContent"]["user_results"]["result"]["legacy"]["followers_count"])
    rts_dict["tweets"].append(f["itemContent"]["user_results"]["result"]["legacy"]["statuses_count"])
    rts_dict["verified"].append(f["itemContent"]["user_results"]["result"]["legacy"]["verified"])
    if f["itemContent"]["user_results"]["result"]["legacy"]["entities"]["description"]["urls"]:
        rts_dict["url"].append(f["itemContent"]["user_results"]["result"]["legacy"]["entities"]["description"]["urls"][0]["display_url"])
    else:
        rts_dict["url"].append(0)
    counter += 1
    # rts_dict[f"{id}"] = {"name":name, "screen_name":screen_name, "followers":followers, "tweets":tweets, "verified":verified}
    
# create dataframe
df = pd.DataFrame(rts_dict)
df_sorted = df.sort_values(by='followers', ascending=False)

# access mps data and create list of mps by twitter handle 
mps_df = pd.read_csv("mp_twitters2.csv")
mps = [name for name in mps_df.twitter_handle if name != "Unknown field"] 

# add column to dataframe with test for mp
def mp_test(name):
    if name in mps:
        return True
    else:
        return False

df_sorted["MP"] = df_sorted.screen_name.apply(mp_test)

# create csv file with dataframe in it
df_sorted.to_csv(f"{tweet_id}.csv")
