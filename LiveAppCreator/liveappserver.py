from flask import Flask, request
import json

app = Flask(__name__)
data = ""

@app.route('/')
def editor():
	return 'hello, world!'

@app.route('/submit', methods=['POST'])
def submit():
	global data
	data=request.get_json()
	# print(data)
	return "Thank You"
	
@app.route('/rules')
def rules():
	print('printing rules')
	try:
		return json.dumps(data)
	except Exception as e:
		print('error: ' + e)
	# return """[
	# {"condition": "1 forward", "type": "firebase", "method": "concatenate", "URL": "https://fbhack-9a7bd.firebaseio.com/robot1.json", "param": "forward"},
	# {"condition": "1 back", "type": "firebase", "method": "concatenate", "URL": "https://fbhack-9a7bd.firebaseio.com/robot1.json", "param": "back"},
	# {"condition": "1 left", "type": "firebase", "method": "concatenate", "URL": "https://fbhack-9a7bd.firebaseio.com/robot1.json", "param": "left"},
	# {"condition": "1 right", "type": "firebase", "method": "concatenate", "URL": "https://fbhack-9a7bd.firebaseio.com/robot1.json", "param": "right"},
	# {"condition": "1 attack", "type": "firebase", "method": "concatenate", "URL": "https://fbhack-9a7bd.firebaseio.com/robot1.json", "param": "attack"},
	# {"condition": "2 forward", "type": "firebase", "method": "concatenate", "URL": "https://fbhack-9a7bd.firebaseio.com/robot2.json", "param": "forward"},
	# {"condition": "2 back", "type": "firebase", "method": "concatenate", "URL": "https://fbhack-9a7bd.firebaseio.com/robot2.json", "param": "back"},
	# {"condition": "2 left", "type": "firebase", "method": "concatenate", "URL": "https://fbhack-9a7bd.firebaseio.com/robot2.json", "param": "left"},
	# {"condition": "2 right", "type": "firebase", "method": "concatenate", "URL": "https://fbhack-9a7bd.firebaseio.com/robot2.json", "param": "right"},
	# {"condition": "2 attack", "type": "firebase", "method": "concatenate", "URL": "https://fbhack-9a7bd.firebaseio.com/robot2.json", "param": "attack"}
	# ]"""

	
	
app.run()