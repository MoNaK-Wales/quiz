from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import QuizSession, Question
from channels.db import database_sync_to_async


active_players = {}  # {room_code: [player1, player2, ...]}

class QuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"][
            "room_code"
        ]  # Получение room_code из URL
        self.room_group_name = (
            f"quiz_{self.room_code}"  # Название отдельной группы для каждого квиза
        )

        # Присоединение пользователя к группе квиза
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name  # Канал текущего пользователя
        )
        await self.accept()

        if self.room_group_name not in active_players:
            active_players[self.room_group_name] = []
        print(
            f"[CONNECT] quiz {self.room_code} | active: {len(active_players[self.room_group_name])}"
        )

    async def disconnect(self, close_code):
        if hasattr(self, "player_name") and self.player_name in active_players.get(
            self.room_group_name, []
        ):
            active_players[self.room_group_name].remove(self.player_name)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "players_update",
                    "players": active_players[self.room_group_name],
                },
            )
            print(
                f"[DISCONNECT] {self.player_name} left quiz {self.room_code} | active: {len(active_players[self.room_group_name])}"
            )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):         # Получение сообщения (ответа) от пользователя
        data = json.loads(text_data)

        if data.get("type") == "join":
            self.player_name = data.get("name")

            if (
                self.player_name
                and self.player_name not in active_players[self.room_group_name]
            ):
                active_players[self.room_group_name].append(self.player_name)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "players_update",
                    "players": active_players[self.room_group_name],
                },
            )

        elif data.get("type") == "answer":
            # Отправка ответа всем участникам квиза
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "quiz_message",  # У всех консумеров вызывается функция quiz_message
                    "message": data["answer"],
                },
            )

        elif data.get("type") == "start_quiz":
            question_data = await self.get_next_question()

            if question_data:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "new_question",
                        "question": question_data["text"],
                        "answers": question_data["answers"],
                    },
                )

    async def quiz_message(self, event):        # Получение сообщения из группы квиза (функция называется как 'type' в group_send)
        message = event['message']

        # Отправка сообщения обратно пользователю
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def players_update(self, event):
        await self.send(
            text_data=json.dumps(
                {"type": "players_update", "players": event["players"]}
            )
        )

    async def new_question(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "new_question",
                    "question": event["question"],
                    "answers": event["answers"],
                }
            )
        )

    @database_sync_to_async
    def get_next_question(self):
        try:
            session = QuizSession.objects.select_related("quiz").get(
                code=self.room_code
            )
            all_questions = list(session.quiz.questions.all())

            if session.current_question_index < len(all_questions):
                question = all_questions[session.current_question_index]
                answers = list(question.answers.all())

                # для следующего раза
                session.current_question_index += 1
                session.save()

                return {
                    "text": question.text,
                    "answers": {
                        "A": answers[0].text,
                        "B": answers[1].text,
                        "C": answers[2].text,
                        "D": answers[3].text,
                    },
                }
            else:
                return None
        except QuizSession.DoesNotExist:
            return None
