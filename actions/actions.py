import sqlite3
import random

from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime
import pytz
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, SessionStarted, EventType
from rasa_sdk.events import Restarted

# collections db
DB_PATH = './server/database/db/collection.sqlite'

VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
now = datetime.now(VN_TZ)
month = now.strftime('%m')


# action get food
class ActionGetSuggestFood(Action):
    def name(self) -> Text:
        return 'action_get_suggest_food'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        sqlite_connection = sqlite3.connect(DB_PATH)
        cursor = sqlite_connection.cursor()
        print("[Action][DB][Foods] Databases Connected Successfully")
        food_sql = "SELECT * FROM foods WHERE type = {} ".format(1)

        # get now temp & doAm
        # temp = kel_to_cel(get_temp()['temp'])
        # humidity = get_temp()['humidity']
        # fake data info
        temp = 19
        humidity = 90
        print("[Action][Temp] temp: {}, humidity: {}%".format(temp, humidity))

        food_sql += "AND delivery_rating >= 4 ORDER BY delivery_rating DESC"
        print("[Action][DB][Foods][SQL] RUN {}".format(food_sql))
        cursor.execute(food_sql)
        foods = cursor.fetchall()
        print("[Action][DB][Foods] Get foods success")
        sqlite_connection.close()

        # haven't food
        if len(foods) == 0:
            dispatcher.utter_message(text='Hiện tại tôi không tìm được món nào phù hợp, để tôi tìm thêm nhé!')
            return [Restarted()]

        # get best food by random
        food_index = random.randint(0, len(foods))
        suggest_food = foods[food_index]
        print(suggest_food)
        text_response = 'Tôi tìm được món này: {}\n'.format(suggest_food[1])
        # dispatcher.utter_message(text='Tôi tìm được món này: {}'.format(suggest_food[1]))
        if suggest_food[3]:
            text_response += '- Địa chỉ: {}\n'.format(suggest_food[3])
            # dispatcher.utter_message(text='Địa chỉ: {}'.format(suggest_food[3]))
        if suggest_food[8]:
            text_response += '- Mức đánh giá: {}*\n'.format(suggest_food[8])
            # dispatcher.utter_message(text='Mức đánh giá: {}*'.format(suggest_food[8]))
        if suggest_food[6]:
            text_response += '- Giảm giá: {} (theo shopee food)\n'.format(suggest_food[6])
            # dispatcher.utter_message(text='Giảm giá: {} (theo shopee food)'.format(suggest_food[6]))
        if suggest_food[5]:
            text_response += '[{link}]({link})\n'.format(link=suggest_food[5])
            # dispatcher.utter_message(text='[{link}]({link})'.format(link=suggest_food[5]))
        if suggest_food[8] and suggest_food[8] >= 4.5:
            response = [
                'Có vẻ món này ngon đó.',
                'Điểm đánh giá rất cao, có vẻ ngon',
                'yummy!',
                'delicious foods!',
            ]
            text_response += random.choice(response)
            # dispatcher.utter_message(text=random.choice(response))
        else:
            response = [
                'Món này có vẻ ok',
                'Điểm đánh giá cũng không thấp, có vẻ ổn',
                'Cũng được đó',
                'Cũng đáng để thử',
            ]
            text_response += random.choice(response)
            # dispatcher.utter_message(text=random.choice(response))

        dispatcher.utter_message(text=text_response)

        return [SlotSet('suggest_food', suggest_food)]


# action restart story
class ActionRefreshStory(Action):
    def name(self) -> Text:
        return 'action_refresh_story'

    @staticmethod
    def fetch_slots(tracker: Tracker) -> List[EventType]:
        """Collect slots that contain the user's name and phone number."""

        slots = []
        for key in ("name", "phone_number"):
            value = tracker.get_slot(key)
            if value is not None:
                slots.append(SlotSet(key=key, value=value))
        return slots

    async def run(
            self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        # the session should begin with a `session_started` event
        events = [SessionStarted()]

        return events


# action default fallback
class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return 'action_default_fallback'

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        response = [
            'Hiện tại tôi chưa được dạy, nhưng tôi sẽ quay lại thông minh hơn để trả lời câu này.',
            'Tôi chưa hiểu ý bạn. Tôi sẽ học tập thêm.',
            'Vấn đề này có vẻ khó. Tôi sẽ học tập thêm.',
            'Chịu. Tôi chưa hiều bạn nói. Để tôi học tập thêm nhé.',
            'Tôi không hiểu. Tôi sẽ tìm hiểu thêm.',
        ]
        dispatcher.utter_message(text=random.choice(response))

        # Revert user message which led to fallback.
        return [Restarted()]
