from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from .models import QuizSession, Question
from channels.db import database_sync_to_async


active_players = {}  # {room_code: [player1, player2, ...]}
session_answers = {}
room_processing = {}

class QuizConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"][
            "room_code"  # Получение room_code из URL
        ]
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
            session_answers[self.room_group_name] = {}
            room_processing[self.room_group_name] = False
        print(
            f"[CONNECT] quiz {self.room_code} | active: {len(active_players[self.room_group_name])}"
        )

    async def disconnect(self, close_code):
        if hasattr(self, "player_name") and self.player_name in active_players.get(
            self.room_group_name, []
        ):
            active_players[self.room_group_name].remove(self.player_name)
            if self.player_name in session_answers.get(self.room_group_name, {}):
                del session_answers[self.room_group_name][self.player_name]

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
        session_players = active_players.get(self.room_group_name)

        print(data.get("type"))

        if data.get("type") == "join":
            self.player_name = data.get("name")

            if self.player_name and self.player_name not in session_players:
                session_players.append(self.player_name)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "players_update",
                    "players": active_players[self.room_group_name],
                },
            )

        elif data.get("type") == "answer":
            # Отправка ответа всем участникам квиза
            if hasattr(self, "player_name"):
                session_answers[self.room_group_name][self.player_name] = data["answer"]
                print(f"[ANSWER] {self.player_name} answered: {data['answer']}")
                print(f"[ANSWERS] Current answers: {session_answers[self.room_group_name]}")

            current_answers_count = len(session_answers[self.room_group_name])
            active_players_count = len(active_players[self.room_group_name])
            print(f"[CHECK] Answers: {current_answers_count}/{active_players_count}")
            
            if current_answers_count >= active_players_count and active_players_count > 0 and not room_processing[self.room_group_name]:
                room_processing[self.room_group_name] = True
                await self.process_end()

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

    # async def quiz_message(self, event):        # Получение сообщения из группы квиза (функция называется как 'type' в group_send)
    #     message = event['message']

    #     # Отправка сообщения обратно пользователю
    #     await self.send(text_data=json.dumps({
    #         'message': message
    #     }))

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

    @database_sync_to_async
    def check_answer(self, player_answer, is_setup=False):
        try:
            session = QuizSession.objects.get(code=self.room_code)
            question_index = session.current_question_index - 1

            question = list(session.quiz.questions.all())[question_index]
            correct_answer_obj = question.answers.get(is_correct=True)
            correct_answer_char = correct_answer_obj.option_char

            if is_setup:
                return correct_answer_char

            return player_answer == correct_answer_char
        except Exception:
            return None if is_setup else False

    async def process_end(self):
        asyncio.create_task(self._process_end_async())

    async def _process_end_async(self):
        try:
            correct_answer = await self.check_answer(None, is_setup=True)

            current_answers = session_answers.get(self.room_group_name, {})
            results = {}
            for player, answer in current_answers.items():
                results[player] = answer == correct_answer

            print(f"[RESULTS] Sending results: {results}")

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "round_results", 
                    "results": results,
                    "correct_answer": correct_answer
                },
            )

            await asyncio.sleep(3)
            
            room_processing[self.room_group_name] = False

            question_data = await self.get_next_question()
            session_answers[self.room_group_name] = {}

            if question_data:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "new_question",
                        "question": question_data["text"],
                        "answers": question_data["answers"],
                    },
                )
            else:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "quiz_end", "message": "The quiz has finished!"},
                )
        except Exception as e:
            print(f"[ERROR in _process_end_async] {e}")
            room_processing[self.room_group_name] = False


    async def round_results(self, event):
        await self.send(text_data=json.dumps(event))

    async def quiz_end(self, event):
        await self.send(text_data=json.dumps(event))
