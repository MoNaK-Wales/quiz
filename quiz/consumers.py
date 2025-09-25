from channels.generic.websocket import AsyncWebsocketConsumer
import json

class QuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.quiz_id = self.scope['url_route']['kwargs']['quiz_id']     # Получение quiz_id из URL
        self.room_group_name = f'quiz_{self.quiz_id}'                   # Название отдельной группы для каждого квиза

        # Присоединение пользователя к группе квиза
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name                   # Канал текущего пользователя
        )
        print("CONNECT", self.scope['url_route']['kwargs']['quiz_id'])
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):         # Получение сообщения (ответа) от пользователя
        data = json.loads(text_data)
        answer = data.get('answer')

        # Отправка ответа всем участникам квиза
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'quiz_message',         # У всех консумеров вызывается функция quiz_message
                'message': answer
            }
        )
    
    async def quiz_message(self, event):        # Получение сообщения из группы квиза (функция называется как 'type' в group_send)
        message = event['message']

        # Отправка сообщения обратно пользователю
        await self.send(text_data=json.dumps({
            'message': message
        }))