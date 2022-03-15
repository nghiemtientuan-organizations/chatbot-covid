# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import sqlite3
import random
import requests
from bs4 import BeautifulSoup as bs

from rasa_sdk.executor import CollectingDispatcher
from datetime import datetime
import pytz
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, SessionStarted, EventType
from rasa_sdk.events import Restarted

# foods db
DB_FOOD_PATH = './db/foods.db'

VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
now = datetime.now(VN_TZ)
month = now.strftime('%m')
seasons_name = [
    'mùa xuân',
    'mùa hè',
    'mùa thu',
    'mùa đông',
]
weather_org_url = 'https://api.openweathermap.org/data/2.5/weather?q=hanoi&appid=1cefc1d741a0e2bc1ce1728e91d651ec'
cook_food_search_url = 'https://www.google.com/search?q={}'

# Food temp 25-35 define
COLD_TEMP = 0       # < 25
MEDIUM_TEMP = 1     # 25 <= ... <= 35
HOT_TEMP = 2        # > 35
default_cold_temp = 25
default_hot_temp = 35

# Humidity
MEDIUM_HUMIDITY = 80
DRY_FOOD = 0    # >= 80%
WATER_FOOD = 1  # < 80%

# Food type
FOOD_TYPE = 1
DRINk_TYPE = 2


def now_season():
    switcher = {
        1: seasons_name[3],
        2: seasons_name[0],
        3: seasons_name[0],
        4: seasons_name[0],
        5: seasons_name[1],
        6: seasons_name[1],
        7: seasons_name[1],
        8: seasons_name[2],
        9: seasons_name[2],
        10: seasons_name[2],
        11: seasons_name[3],
        12: seasons_name[3],
    }

    return switcher.get(int(month), seasons_name[0])


def kel_to_cel(kelvin):
    return float(kelvin) - 273.15


def get_temp():
    try:
        response = requests.get(weather_org_url)
        data_json = response.json()

        return data_json['main']
    except Exception:
        return None


# action get date info
class ActionGetDate(Action):
    def name(self) -> Text:
        return 'action_get_date'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text_response = now.strftime('Bây giờ là: %H:%M.\nNgày %d/%m/%Y.')
        # dispatcher.utter_message(text=now.strftime('Bây giờ là: %H:%M.'))
        # dispatcher.utter_message(text=now.strftime('Ngày %d/%m/%Y.'))
        dispatcher.utter_message(text=text_response)

        return []


# action get season info
class ActionGetSeason(Action):
    def name(self) -> Text:
        return 'action_get_season'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text='Hiện tại là mùa {session}'.format(session=now_season()))

        return []


# action get temperature info
class ActionGetTemperature(Action):
    def name(self) -> Text:
        return 'action_get_temperature'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        try:
            response = requests.get(weather_org_url)
            data_json = response.json()
            main_data = data_json['main']
            temp, temp_min, temp_max = \
                kel_to_cel(main_data['temp']), kel_to_cel(main_data['temp_min']), kel_to_cel(main_data['temp_max'])
            win_data = data_json['wind']

            # response info
            text_response = 'Theo tôi biết hiện tại đang là {} độ.\n'.format(temp)
            # dispatcher.utter_message(text='Theo tôi biết hiện tại đang là {} độ.'.format(temp))
            if temp_min != temp_max:
                text_response += 'Cao nhất {} - thấp nhất {}.\n'.format(temp_min, temp_max)
                # dispatcher.utter_message(text='Cao nhất {} - thấp nhất {}.'.format(temp_min, temp_max))

            text_response += 'Tốc độ gió là {} km/h, độ ẩm {}%\n'.format(win_data['speed'], main_data['humidity'])
            # dispatcher.utter_message(
            #     text='Tốc độ gió là {} km/h, độ ẩm {}%'.format(win_data['speed'], main_data['humidity'])
            # )

            # response bot's feel
            if temp <= default_cold_temp:
                text_response += 'Trời lạnh thật, trời này mà ăn bát gì đó ấm ấm thì tuyệt cú mèo.'
                # dispatcher.utter_message(text='Trời lạnh thật, trời này mà ăn bát gì đó ấm ấm thì tuyệt cú mèo.')
            elif temp >= default_hot_temp:
                text_response += 'Thời tiết nóng nhỉ, làm chút gì đó mát mát nào vừa thanh lọc cơ thể.'
                # dispatcher.utter_message(text='Thời tiết nóng nhỉ, làm chút gì đó mát mát nào vừa thanh lọc cơ thể.')
            else:
                text_response += 'Thời tiết này ăn gì cũng ngon.'
                # dispatcher.utter_message(text='Thời tiết này ăn gì cũng ngon.')

            dispatcher.utter_message(text=text_response)
        except Exception:
            dispatcher.utter_message(
                text='Hiên tại tôi đang không lấy được dữ liệu về thời tiết. Phiền bạn thử lại sau.')

        return []


# action get food
class ActionGetSuggestFood(Action):
    def name(self) -> Text:
        return 'action_get_suggest_food'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # connect to db to get all foods
        sqlite_connection = sqlite3.connect(DB_FOOD_PATH)
        cursor = sqlite_connection.cursor()
        print("[Action][DB][Foods] Databases Connected Successfully")
        food_sql = "SELECT * FROM foods WHERE type = {} ".format(FOOD_TYPE)

        # get now temp & doAm
        # temp = kel_to_cel(get_temp()['temp'])
        # humidity = get_temp()['humidity']
        # fake data info
        temp = 19
        humidity = 90
        print("[Action][Temp] temp: {}, humidity: {}%".format(temp, humidity))
        if temp < default_cold_temp:
            # get hot food
            food_sql += "AND temperature_type = {} ".format(HOT_TEMP)
        elif temp > default_hot_temp:
            # get medium temp food
            food_sql += "AND temperature_type = {} ".format(MEDIUM_TEMP)
        else:
            # get medium and hot temp food
            food_sql += "AND temperature_type >= {} ".format(MEDIUM_TEMP)

        if humidity < MEDIUM_HUMIDITY:
            food_sql += "AND humidity_type = {} ".format(WATER_FOOD)

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


# action get drink
class ActionGetSuggestDrink(Action):
    def name(self) -> Text:
        return 'action_get_suggest_drink'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # connect to db to get all drinks
        sqlite_connection = sqlite3.connect(DB_FOOD_PATH)
        cursor = sqlite_connection.cursor()
        print("[Action][DB][Foods] Databases Connected Successfully")
        drink_sql = "SELECT * FROM foods WHERE type = {}".format(DRINk_TYPE)
        cursor.execute(drink_sql)
        drinks = cursor.fetchall()
        print("[Action][DB][Foods] Get drinks success")
        sqlite_connection.close()

        # haven't drinks
        if len(drinks) == 0:
            dispatcher.utter_message(text='Hiện tại tôi không tìm được đồ uống nào phù hợp, để tôi tìm thêm nhé!')
            return [Restarted()]

        # get best food by random
        food_index = random.randint(0, len(drinks))
        suggest_drink = drinks[food_index]
        print(suggest_drink)
        text_response = 'Đồ uống ở đây: {}\n'.format(suggest_drink[1])
        # dispatcher.utter_message(text='Đồ uống ở đây: {}'.format(suggest_drink[1]))
        if suggest_drink[3]:
            text_response += '- Địa chỉ: {}\n'.format(suggest_drink[3])
            # dispatcher.utter_message(text='Địa chỉ: {}'.format(suggest_drink[3]))
        if suggest_drink[8]:
            text_response += '- Đánh giá: {}*\n'.format(suggest_drink[8])
            # dispatcher.utter_message(text='Đánh giá: {}*'.format(suggest_drink[8]))
        if suggest_drink[6]:
            text_response += '- Giảm giá: {} (theo shopee food)\n'.format(suggest_drink[6])
            # dispatcher.utter_message(text='Giảm giá: {} (theo shopee food)'.format(suggest_drink[6]))
        if suggest_drink[5]:
            text_response += '[{link}]({link})'.format(link=suggest_drink[5])
            # dispatcher.utter_message(text='[{link}]({link})'.format(link=suggest_drink[5]))

        dispatcher.utter_message(text=text_response)

        return []


# action how to cook food
class ActionHowToCookFood(Action):
    def name(self) -> Text:
        return 'action_how_to_cook_food'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        suggest_food = tracker.get_slot('suggest_food')
        try:
            search_url = cook_food_search_url.format(
                requests.utils.quote('Cách nấu {} tại nhà'.format(suggest_food[1]))
            )
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
            }
            print('[Noti][Cook]Search {}'.format(search_url))
            foods_search_response = requests.get(search_url, headers=headers)
            body_search_page = bs(foods_search_response.content, "html.parser").body
            posts = body_search_page.select("[class='g'] a[href^='http'][data-ved]:has(h3)")
            if len(posts):
                cook_element = posts[0]
                cook_title = cook_element.select_one("h3").get_text(strip=True)
                cook_link = cook_element.get('href')
                text_response = 'Tôi tìm thấy cách nấu ở đây:\n[{cook_title}]({link})'.format(
                    cook_title=cook_title,
                    link=cook_link
                )
                # dispatcher.utter_message(text='Tôi tìm thấy cách nấu ở đây:')
                # dispatcher.utter_message(text='{}'.format(cook_title))
                # dispatcher.utter_message(text='[{link}]({link})'.format(link=cook_link))
                dispatcher.utter_message(text=text_response)
            else:
                dispatcher.utter_message(text='Hiện tại tôi chưa tìm thấy cách nấu món này, tôi sẽ thử lại sau nhé.')
        except Exception:
            print(str(Exception))
            dispatcher.utter_message(text='Hiện tại tôi chưa tìm thấy cách nấu món này, tôi sẽ thử lại sau nhé.')

        return []


# action find food by name
class ActionFindFood(Action):
    def name(self) -> Text:
        return 'action_find_food'

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        find_food = tracker.get_latest_entity_values('find_food').__next__()
        print(find_food)
        if find_food:
            # connect to db to get all foods
            sqlite_connection = sqlite3.connect(DB_FOOD_PATH)
            cursor = sqlite_connection.cursor()
            print("[Action][DB][Foods] Databases Connected Successfully")
            food_sql = "SELECT * FROM foods WHERE type = {} AND name LIKE '%{}%' LIMIT 5".format(FOOD_TYPE, find_food)
            cursor.execute(food_sql)
            foods = cursor.fetchall()

            # haven't food
            if len(foods) == 0:
                dispatcher.utter_message(text='Hiện tại tôi không tìm được món nào phù hợp, để tôi tìm thêm nhé!')
                return []

            text_response = 'Tôi tìm được {} chỗ:\n'.format(len(foods))
            # dispatcher.utter_message(text='Tôi tìm được {} chỗ:'.format(len(foods)))
            for food in foods:
                print(food)
                text_response += '- {food_name}, [{delivery_name}]({link}), {address}\n'.format(
                    food_name=food[1],
                    delivery_name=food[2],
                    address=food[3],
                    link=food[5]
                )
                # dispatcher.utter_message(
                #     text='{food_name}\n{delivery_name}\n{address}\n[{link}]({link})'.format(
                #         food_name=food[1],
                #         delivery_name=food[2],
                #         address=food[3],
                #         link=food[5]
                #     )
                # )

            dispatcher.utter_message(text=text_response)
        else:
            dispatcher.utter_message(text='Tôi không hiểu món mà bạn cần tìm. Bạn thử cú pháp "tìm bún cá" xem có được không!')

        return []


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
            'Vấn đề này có vẻ khó. Để tôi đi hỏi boss rồi lần tới tôi sẽ trả lời bạn nhé.',
            'Chịu. Tôi chưa hiều bạn nói. Để tôi học tập thêm nhé.',
            'Tôi không hiểu. Tôi sẽ tìm hiểu thêm',
        ]
        dispatcher.utter_message(text=random.choice(response))

        # Revert user message which led to fallback.
        return [Restarted()]
