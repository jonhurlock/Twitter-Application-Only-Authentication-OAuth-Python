#!/usr/bin/env python
# encoding: utf-8
"""
* 	OAuth.py
*
*	Created by Jon Hurlock on 2013-05-28.
* 	
*	Jon Hurlock's Twitter Application-only Authentication App by Jon Hurlock (@jonhurlock)
*	is licensed under a Creative Commons Attribution-ShareAlike 3.0 Unported License.
*	Permissions beyond the scope of this license may be available at http://www.jonhurlock.com/.
*
* 	Go to line 172 & 173 to insert your twitter specific details
"""
import sys # used for the storage class
import pycurl # used for curling
import base64 # used for encoding string
import urllib # used for enconding
import cStringIO # used for curl buffer grabbing
import json # used for decoding json token
import time # used for stuff to do with the rate limiting
from time import sleep # used for rate limiting

# Ignore this class, its just to do with handling of HTTP headers
class Storage:
    def __init__(self):
        self.contents = ''
        self.line = 0

    def store(self, buf):
        self.line = self.line + 1
        self.contents = "%s%i: %s" % (self.contents, self.line, buf)

    def __str__(self):
        return self.contents

# grabs the rate limit remaining from the headers
def grab_rate_limit_remaining(headers):
	limit = ''
	h = str(headers).split('\n')
	for line in h:
		if 'x-rate-limit-remaining:' in line:
			limit = line[28:-1]
	return limit

# grabs the time the rate limit expires
def grab_rate_limit_time(headers):
	x_time = ''
	h = str(headers).split('\n')
	for line in h:
		if 'x-rate-limit-reset:' in line:
			x_time = line[24:-1]
	return x_time

# obtains the bearer token
def get_bearer_token(consumer_key,consumer_secret):
	# enconde consumer key
	consumer_key = urllib.quote(consumer_key)
	# encode consumer secret
	consumer_secret = urllib.quote(consumer_secret)
	# create bearer token
	bearer_token = consumer_key+':'+consumer_secret
	# base64 encode the token
	base64_encoded_bearer_token = base64.b64encode(bearer_token)
	# set headers
	headers = [
	"POST /oauth2/token HTTP/1.1", 
	"Host: api.twitter.com", 
	"User-Agent: jonhurlock Twitter Application-only OAuth App Python v.1",
	"Authorization: Basic "+base64_encoded_bearer_token+"",
	"Content-Type: application/x-www-form-urlencoded;charset=UTF-8", 
	"Content-Length: 29"]
	# do the curl
	token_url = "https://api.twitter.com/oauth2/token"
	buf = cStringIO.StringIO()
	access_token = ''
	pycurl_connect = pycurl.Curl()
	pycurl_connect.setopt(pycurl_connect.URL, token_url) # used to tell which url to go to
	pycurl_connect.setopt(pycurl_connect.WRITEFUNCTION, buf.write) # used for generating output
	pycurl_connect.setopt(pycurl_connect.HTTPHEADER, headers) # sends the customer headers above
	pycurl_connect.setopt(pycurl_connect.POSTFIELDS, 'grant_type=client_credentials') # sends the post data
	#pycurl_connect.setopt(pycurl_connect.VERBOSE, True) # used for debugging, really helpful if you want to see what happens
	pycurl_connect.perform() # perform the curl
	access_token = buf.getvalue() # grab the data
	pycurl_connect.close() # stop the curl
	x = json.loads(access_token)
	bearer = x['access_token']
	return bearer

# invalidates a given bearer token
def invalidate_bearer_token(o_bearer_token,consumer_key,consumer_secret):
	# enconde consumer key
	consumer_key = urllib.quote(consumer_key)
	# encode consumer secret
	consumer_secret = urllib.quote(consumer_secret)
	# create bearer token
	bearer_token = consumer_key+':'+consumer_secret
	# base64 encode the token
	base64_encoded_bearer_token = base64.b64encode(bearer_token)
	# set headers
	headers = [ 
	"POST /oauth2/invalidate_token HTTP/1.1", 
	"Host: api.twitter.com", 
	"User-Agent: jonhurlock Twitter Application-only OAuth App Python v.1",
	"Authorization: Basic "+base64_encoded_bearer_token+"",
	"Accept: */*", 
	"Content-Type: application/x-www-form-urlencoded", 
	"Content-Length: "+str(len("access_token="+o_bearer_token+""))+""
	] 
	# do the curl
	# invalidate url
	invalidate_url = "https://api.twitter.com/oauth2/invalidate_token"
	pycurl_connect = pycurl.Curl()
	pycurl_connect.setopt(pycurl_connect.URL, invalidate_url) # used to tell which url to go to
	pycurl_connect.setopt(pycurl_connect.HTTPHEADER, headers) # sends the customer headers above
	pycurl_connect.setopt(pycurl_connect.POSTFIELDS, str("access_token="+o_bearer_token+"")) # sends the post data
	#pycurl_connect.setopt(pycurl_connect.VERBOSE, True) # used for debugging, really helpful if you want to see what happens
	pycurl_connect.perform() # perform the curl
	#print buf.getvalue() # grab the data
	pycurl_connect.close() # stop the curl

# performs a basic search for a given query
def search_for_a_tweet(bearer_token, query):
	# url to perform search
	url = "https://api.twitter.com/1.1/search/tweets.json"
	formed_url ='?q='+query+'&include_entities=true'
	headers = [ 
	str("GET /1.1/search/tweets.json"+formed_url+" HTTP/1.1"), 
	str("Host: api.twitter.com"), 
	str("User-Agent: jonhurlock Twitter Application-only OAuth App Python v.1"),
	str("Authorization: Bearer "+bearer_token+"")
	]
	buf = cStringIO.StringIO()
	results = ''
	pycurl_connect = pycurl.Curl()
	pycurl_connect.setopt(pycurl_connect.URL, url+formed_url) # used to tell which url to go to
	pycurl_connect.setopt(pycurl_connect.WRITEFUNCTION, buf.write) # used for generating output
	pycurl_connect.setopt(pycurl_connect.HTTPHEADER, headers) # sends the customer headers above
	#pycurl_connect.setopt(pycurl_connect.VERBOSE, True) # used for debugging, really helpful if you want to see what happens
	pycurl_connect.perform() # perform the curl
	results += buf.getvalue() # grab the data
	pycurl_connect.close() # stop the curl
	return results

# returns a tweet and a some extra info regarding rate limits
def grab_a_tweet(bearer_token, tweet_id):
	# url
	url = "https://api.twitter.com/1.1/statuses/show.json"
	formed_url ='?id='+tweet_id+'&include_entities=true'
	headers = [ 
	str("GET /1.1/statuses/show.json"+formed_url+" HTTP/1.1"), 
	str("Host: api.twitter.com"), 
	str("User-Agent: jonhurlock Twitter Application-only OAuth App Python v.1"),
	str("Authorization: Bearer "+bearer_token+"")
	]
	buf = cStringIO.StringIO()
	tweet = ''
	retrieved_headers = Storage()
	pycurl_connect = pycurl.Curl()
	pycurl_connect.setopt(pycurl_connect.URL, url+formed_url) # used to tell which url to go to
	pycurl_connect.setopt(pycurl_connect.WRITEFUNCTION, buf.write) # used for generating output
	pycurl_connect.setopt(pycurl_connect.HTTPHEADER, headers) # sends the customer headers above
	pycurl_connect.setopt(pycurl_connect.HEADERFUNCTION, retrieved_headers.store)
	#pycurl_connect.setopt(pycurl_connect.VERBOSE, True) # used for debugging, really helpful if you want to see what happens
	pycurl_connect.perform() # perform the curl
	tweet += buf.getvalue() # grab the data
	pycurl_connect.close() # stop the curl
	#print retrieved_headers
	pings_left = grab_rate_limit_remaining(retrieved_headers)
	reset_time = grab_rate_limit_time(retrieved_headers)
	current_time = time.mktime(time.gmtime())
	return {'tweet':tweet, '_current_time':current_time, '_reset_time':reset_time, '_pings_left':pings_left}


# examples of how to use the code
consumer_key = '' # put your apps consumer key here
consumer_secret = '' # put your apps consumer secret here

bearer_token = get_bearer_token(consumer_key,consumer_secret) # generates a bearer token
search_results = search_for_a_tweet(bearer_token, 'test') # does a very basic search
tweet = grab_a_tweet(bearer_token, '339309066792878080') # grabs a single tweet & some extra bits
#invalidate_bearer_token(bearer_token,consumer_key,consumer_secret) # invalidates the token

print search_results # prints results form the search
print tweet['tweet'] # prints the tweet from the single tweet grabbed