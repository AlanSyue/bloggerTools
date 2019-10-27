import requests
import json
import facebook
import re

def get_config():
	with open('config.txt') as config_file:
		data = json.load(config_file)

	return data

def get_posts_id(apiKey, blogId, pageToken,postIdArray):
	
	domain = 'https://www.googleapis.com/blogger/v3/blogs/'

	if pageToken =='none':
		apiUrl = domain + blogId + '/posts?key=' + apiKey
	else:
		apiUrl = domain + blogId + '/posts?key=' + apiKey + '&pageToken=' + pageToken

	res = requests.get(apiUrl)
	
	datas = res.json()

	for data in datas['items']:
		postId = data['id']
		postIdArray.append(int(postId))

	if datas.get('nextPageToken') != None:
		return get_posts_id(apiKey, blogId, datas['nextPageToken'], postIdArray)
	else:
		return postIdArray

def get_posted_id():
	with open('postId.txt') as json_file:
	    data = json.load(json_file)

	return data['posted']

def get_not_postId_data(apiKey, blogId, postId):
	domain = 'https://www.googleapis.com/blogger/v3/blogs/'

	apiUrl = domain + blogId + '/posts/' + str(postId) + '?key=' + apiKey

	res = requests.get(apiUrl)

	data = res.json()

	# get the url and add the utm to track
	postUrl = data['url'] + "?utm_source=facebook&utm_medium=post&utm_campaign=" + data['url'].split("/")[-1]
	
	# to combine title and content for facebook post content
	title = data['title']
	content = data['content'].split('>')[1].split('<')[0]
	postContent = "🔥" + title + "🔥" + "\n" + "-" + "\n" + content

	result = {"url":postUrl, "postContent":postContent}
	return result

def facebook_post(facebookId, accessToken, postLink, postMessage):
	cfg = {
	 "page_id" : facebookId ,
	 "access_token" : accessToken 
	}

	graph = facebook.GraphAPI(cfg['access_token'])
	graph.put_object(cfg['page_id'],"feed",message=postMessage,link=postLink)

def record_post_id(postIdArray):
	with open('postId.txt', 'w') as outfile:
		dataJson = {"posted" : postIdArray}
		json.dump(dataJson, outfile, ensure_ascii=False, indent=2)


if __name__ == '__main__':
	# open config.txt and get google, facebook apikey n token
	config = get_config()

	apiKey = config['google']['apiKey']
	blogId = config['google']['blogId']
	pageToken = 'none'

	facebookId = config['facebook']['facebookId']
	accessToken = config['facebook']['accessToken']
	
	# for putting post id 
	postIdArray = []

	# use google blogger api to get all post ids
	postIds = get_posts_id(apiKey, blogId, pageToken, postIdArray)

	# read the postId.txt and get all posts which have already been posted
	alreadyPostId = get_posted_id()

	# get the post ids which have not been posted
	notPostIds = list(set(postIds) - set(alreadyPostId))

	for notPostId in notPostIds:
		# get the url, content from the posts which have not been posted
		post_data = get_not_postId_data(apiKey, blogId, notPostId)
		postLink = post_data['url']
		postMessage = post_data['postContent']

		# post to facebook fanpage
		facebook_post(facebookId, accessToken, postLink, postMessage)
		print( str(notPostId) + '：成功發布')

	# write the post ids which is posting  into the postId.txt
	newPostIdsArray = alreadyPostId + notPostIds
	record_post_id(newPostIdsArray)

	print('auto post success')



