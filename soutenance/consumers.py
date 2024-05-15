import json 
from channels.generic.websocket import WebsocketConsumer 
from asgiref.sync import async_to_sync

class DocConsumer(WebsocketConsumer): 
	def connect(self):
		self.group_name = "public_room"
		self.room_group_name = self.group_name

		async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
		self.accept() 

	def disconnect(self, close_code):
		
		async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        ) 
		self.close() 	

	def receive(self, text_data): 
		text_data_json = json.loads(text_data) 
		self.content=text_data_json['expression']
		# print(self.content)
		async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "update_notice", "result": self.content}
        )
		self.send(text_data=json.dumps({ 
			'result': self.content 
		}))
		"""text_data_json = json.loads(text_data) 
		expression = text_data_json['expression'] 
		try: 
			result = eval(expression) 
		except Exception as e: 
			result = "Invalid Expression"
		self.send(text_data=json.dumps({ 
			'result': result 
		}))"""
	def update_notice(self, event):
		self.content=event.get('result',None)
		# print(self.content)
		self.send(text_data=json.dumps({
			'result':self.content
		}))
    