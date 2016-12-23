#!/usr/bin/python

import httplib2
import os
import sys
import unicodedata

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the {{ Google Cloud Console }} at
# {{ https://cloud.google.com/console }}.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the {{ Cloud Console }}
{{ https://cloud.google.com/console }}

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_READ_WRITE_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def subscriptions_list_my_subscribers(service, part, my_subscribers, subDic):
  results = service.subscriptions().list(mySubscribers=my_subscribers, part=part, maxResults=50).execute()
  nextPageToken = "0"
  try:
    nextPageToken = results['nextPageToken']
  except:
    print("No nextPage")
    nextPageToken = ""
  items = results['items']
  for item in items:
    subscriberSnippet = item['subscriberSnippet']
    channelId = subscriberSnippet['channelId']
    try:
      subscriberName = subscriberSnippet['title']
      print(subscriberName)
    except UnicodeEncodeError:
      subscriberName = subscriberSnippet['title'].encode('ascii', 'xmlcharrefreplace')
      print(subscriberName)
    try:
      subDic[channelId] = subscriberName
    except UnicodeEncodeError:
      subDic[channelId] = subscriberName.encode('ascii', 'xmlcharrefreplace')
  while len(nextPageToken) > 0:
    try:
      results = service.subscriptions().list(mySubscribers=my_subscribers, part=part, pageToken=nextPageToken, maxResults=50).execute()
    except:
      print("Failed request!")
    try:
      nextPageToken = results['nextPageToken']
      print("NPT: %s" % nextPageToken)
    except:
      print("Last page")
      nextPageToken = ""
    items = results['items']
    for item in items:
      subscriberSnippet = item['subscriberSnippet']
      channelId = subscriberSnippet['channelId']
      try:
        subscriberName = subscriberSnippet['title']
      except UnicodeEncodeError:
        subscriberName = subscriberSnippet['title'].encode('ascii', 'xmlcharrefreplace')
      subDic[channelId] = subscriberSnippet['title']
      try:
        subscriberName = subscriberSnippet['title']
        print(subscriberName)
      except UnicodeEncodeError:
        subscriberName = subscriberSnippet['title'].encode('ascii', 'xmlcharrefreplace')
      print(subscriberName)
      try:
        subDic[channelId] = subscriberName
      except UnicodeEncodeError:
        subDic[channelId] = subscriberName.encode('ascii', 'xmlcharrefreplace')

if __name__ == "__main__":
  youtube = get_authenticated_service(args)
  subscriberDict = {}
  try:
    subscriptions_list_my_subscribers(youtube, 'subscriberSnippet', True, subscriberDict)
    with open("SubscriberList.txt", "a") as subscriberList:
      for key, value in subscriberDict.items():
        print("%s ( youtube.com/channel/%s )" %(value, key))
        subscriberList.write("%s; https://www.youtube.com/channel/%s\n" % (value, key))
  except:
    print("Unexpected error:", sys.exc_info()[0])
  else:
    print("Get successful!")