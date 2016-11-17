import facebook
import urllib, urllib2
import urlparse
import subprocess
import warnings
import dateutil.parser
import io
import datetime

import pygame, math, random, pygame.gfxdraw, imutils, json, threading, time
import pygame.camera, pygame.display
from pygame.locals import *
from PIL import Image, ImageOps

load_rlock = threading.RLock()

mask = Image.open('images/mask.png').convert('L')

# SCREEN
FPS = 15

PIC_SIZE = 100

PHASE_UPDATE = 50

profilePicturesDict = {}

pygame.init()
pygame.font.init()
pygame.camera.init()

screen = pygame.display.set_mode((1028, 720))
#screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, 0)
WIDTH, HEIGHT = screen.get_size()
clock = pygame.time.Clock()
font = pygame.font.SysFont("Tahoma", 40, False, False)

CONTROLLER1 = (10, 500)
CONTROLLER2 = (WIDTH - 10 - PIC_SIZE, 20)

# Hide deprecation warnings. The facebook module isn't that up-to-date (facebook.GraphAPIError).
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Parameters of your app and the id of the profile you want to mess with.
FACEBOOK_APP_ID     = '300827270282284'
FACEBOOK_APP_SECRET = '08dff50d3f19c3f1a7a5862a2c4ff2b1'
FACEBOOK_PROFILE_ID = '10154758587264341'

# Trying to get an access token. Very awkward.
oauth_args = dict(client_id	 = FACEBOOK_APP_ID,
				client_secret = FACEBOOK_APP_SECRET,
				grant_type	= 'client_credentials')
oauth_curl_cmd = ['curl',
				'https://graph.facebook.com/oauth/access_token?' + urllib.urlencode(oauth_args)]
oauth_response = subprocess.Popen(oauth_curl_cmd,
								stdout = subprocess.PIPE,
								stderr = subprocess.PIPE).communicate()[0]

try:
	oauth_access_token = urlparse.parse_qs(str(oauth_response))['access_token'][0]
except KeyError:
	print('Unable to grab an access token!')
	exit()

facebook_graph = facebook.GraphAPI(oauth_access_token)

user_access_token = 'EAAERmc6VfCwBAGpwcFPZCF1UBwnxYVhfh347ZAWMGNvTDQ9aFnFzpPjtZB45wenzjgegRxJNKzIaVrQn70BZBBwcEJ1wgi12bh19pYiKDMFYCRrVNgNELu47liXZAiTr4G5EfZAji75pP1l7feln5HYVZCDqf0Pvq4AIiK3ZBpj4gAZDZD'

last_post = facebook_graph.request("/1283318901687249/feed", args={'access_token':user_access_token})['data'][0]["id"]

try:
	list_comments = facebook_graph.request('/%s/comments' % (last_post), args={'access_token':user_access_token})["data"]
	last_comment_time = dateutil.parser.parse(max(list_comments, key = lambda x: dateutil.parser.parse(x["created_time"]))["created_time"]) - datetime.timedelta(1)
except Exception as ex:
	print(ex)
	last_comment_time = dateutil.parser.parse(facebook_graph.request("/1283318901687249/feed", args={'access_token':user_access_token})['data'][0]["created_time"])
	
done = False
	
def game_main():
	global last_comment_time
	global profilePicturesDict
	global done
	
	comments = []
	
	robot1_commands = []
	robot2_commands = []
	
	robot1_to_firebase = []
	robot2_to_firebase = []
	
	pending_commands = []
	
	phase1 = -1
	phase2 = -1
	
	cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
	
	active = {}
	start_loading_comments(last_post, comments, last_comment_time)
	start_pushing_commands(robot1_to_firebase, 'https://fbhack-9a7bd.firebaseio.com/robot1.json')
	start_pushing_commands(robot2_to_firebase, 'https://fbhack-9a7bd.firebaseio.com/robot2.json')
	
	while not done:
		img = cam.get_image()
		img = pygame.transform.scale(img, (WIDTH, HEIGHT))
		screen.blit(img, (0, 0))
		pygame.draw.circle(screen, (200, 0, 0), (WIDTH / 2, HEIGHT / 2), (HEIGHT - 10) / 2, 5)
		
		new_comments = list(comments)
		[comments.pop() for i in range(len(comments))]
		for comment in new_comments:
			user = comment['from']['id']
			content = comment['message']
			pending_commands.append((user, content))
			
		new_pending_commands = []
		for pending in pending_commands:
			user = pending[0]
			content = pending[1]
			
			if user not in profilePicturesDict:
				getProfilePicAsync(user)
				new_pending_commands.append(pending)
			elif profilePicturesDict[user] == 'dummy':
				new_pending_commands.append(pending)
			else:
				parse_command(pending, robot1_commands, robot2_commands, robot1_to_firebase, robot2_to_firebase)
		
		pending_commands = new_pending_commands
		
		if (phase1 == PHASE_UPDATE - 1):
			if (len(robot1_commands) > 0):
				robot1_commands.pop(0)
				
		if (phase2 == PHASE_UPDATE - 1):
			if (len(robot2_commands) > 0):
				robot2_commands.pop(0)
		
		if (phase1 >= 0):
			phase1 = (phase1 + 1) % PHASE_UPDATE
		if (phase2 >= 0):
			phase2 = (phase2 + 1) % PHASE_UPDATE
		
		if (len(robot1_commands) > 0):
			command = robot1_commands[0]
			screen.blit(profilePicturesDict[command[0]], CONTROLLER1)
			if (phase1 < 0):
				phase1 = 0
		else:
			phase1 = -1
			
		if (len(robot2_commands) > 0):
			command = robot2_commands[0]
			screen.blit(profilePicturesDict[command[0]], CONTROLLER2)
			if (phase2 < 0):
				phase2 = 0
		else:
			phase2 = -1
		
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				active[event.key] = True
			elif event.type == pygame.KEYUP and event.key in active:
				del active[event.key]
			elif event.type == pygame.QUIT:
				done = True

		for key in active.keys():
			if key == pygame.K_ESCAPE:
				done = True
				
		pygame.display.flip()
		clock.tick(FPS)

def parse_command(command, robot1_commands, robot2_commands, robot1_firebase, robot2_firebase):
	robot, direction = command[1].split()[:2]
	l = []
	firebase_l = []
	if (robot == 'robot1'):
		l = robot1_commands
		firebase_l = robot1_firebase
	elif (robot == 'robot2'):
		l = robot2_commands
		firebase_l = robot2_firebase
	l.append((command[0], direction))
	firebase_l.append(direction)
	
		
# get profile pic by id
def getProfilePicAsync( profileId ):
	global profilePicturesDict
	if profileId in profilePicturesDict: return
	def async_action():
		profilePicturesDict[profileId] = 'dummy'
		with load_rlock:
			image_str = facebook_graph.request("/%s/picture?height=60" % (profileId),  args={'access_token':user_access_token})
			image_file = io.BytesIO(image_str["data"])
			try:
				profilePicturesDict[profileId] = transform_image(pygame.image.load(image_file))
			except Exception as ex:
				print(ex)
				if profileId in profilePicturesDict:
					del profilePicturesDict[profileId]

	t = threading.Thread(target=async_action)
	t.start()
		
def transform_image(img):
	pil_string = pygame.image.tostring(img, "RGBA", False)
	pil_img = Image.frombytes("RGBA", tuple(img.get_rect()[2:]), pil_string)
	output = ImageOps.fit(pil_img, mask.size, centering=(0.5, 0.5))
	output.putalpha(mask)
	
	output = pygame.image.fromstring(output.tobytes('raw', 'RGBA'), output.size, 'RGBA')
	return pygame.transform.scale(output, (PIC_SIZE, PIC_SIZE))
		
def start_loading_comments(post, where_to_save_to, last_comment_time):
	global done
	def load(last_comment_time):
		while not done:
			comments = facebook_graph.request('/%s/comments' % (post), args={'access_token':user_access_token})["data"]
			comments = filter(lambda c: dateutil.parser.parse(c["created_time"]) > last_comment_time, comments)
			if(len(comments) > 0):
					#last_comment_time = dateutil.parser.parse(comments[0]["created_time"])
					last_comment_time = max(map(lambda c: dateutil.parser.parse(c['created_time']), comments))
			for new_comment in comments:
				where_to_save_to.append(new_comment)
			time.sleep(1)

	t = threading.Thread(target=load, args=(last_comment_time,))
	t.start()

def start_pushing_commands(commands_list, url):
	global done
	def push():
		while not done:
			if (len(commands_list) > 0):
				data = json.loads(urllib2.urlopen(url).read())
				if not data:
					data = ''
				else:
					data += ','
				data += ','.join(commands_list)
				
				[commands_list.pop() for i in range(len(commands_list))]
				
				opener = urllib2.build_opener(urllib2.HTTPHandler)
				request = urllib2.Request(url, data='"' + data + '"')
				request.add_header('Content-Type', 'text/json')
				request.get_method = lambda: 'PUT'
				res = opener.open(request)
	t = threading.Thread(target=push)
	t.start()
		
game_main()

exit()