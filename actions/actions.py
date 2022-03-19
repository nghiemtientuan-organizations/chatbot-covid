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
COVID_LEVELS = {
    'no_symptoms': 'Không triệu chứng',
    'low': 'Nhẹ',
    'medium': 'Trung bình',
    'severity': 'Nặng',
    'critical': 'Nguy kịch',
}


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


# action default fallback
class ActionSubmitHealthDeclaration(Action):
    def name(self) -> Text:
        return 'action_submit_health_declaration'

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text='Khai báo y tế của bạn đã được ghi lại. Cùng nhau vượt qua đại dich.')

        return []


# action default fallback
class ActionSubmitCovidTreatmentForm(Action):
    def name(self) -> Text:
        return 'actions_submit_covid_treatment_form'

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        name = tracker.get_slot('100_patient_name').lower()
        age = tracker.get_slot('101_patient_age')
        phone_number = tracker.get_slot('102_patient_phone_number')
        address = tracker.get_slot('103_patient_address').lower()
        illness_time = tracker.get_slot('104_patient_illness_time')
        is_cough = tracker.get_slot('105_patient_is_cough').lower()
        is_conscious = tracker.get_slot('106_patient_is_conscious').lower()
        fever = tracker.get_slot('107_patient_what_fever')
        is_loss_of_taste = tracker.get_slot('108_patient_loss_of_taste').lower()
        is_loss_of_smell = tracker.get_slot('109_patient_loss_of_smell').lower()
        spo2 = tracker.get_slot('110_patient_what_spo2')
        breathing = tracker.get_slot('111_patient_what_breathing')
        other = tracker.get_slot('112_patient_other').lower()

        covid_level = None
        # Check no_symptoms level
        if is_cough in ' không ko khong no ' and is_conscious in ' không ko khong no ':
            if breathing not in 'không ko khong no ' and spo2 not in 'không ko khong no ' and (
                    breathing > 20 or spo2 < 96):
                covid_level = COVID_LEVELS.get('no_symptoms')

        if not covid_level:
            if is_cough in ' yes co có ' \
                    or is_conscious in ' yes co có ' \
                    or is_loss_of_taste in ' yes co có ' \
                    or is_loss_of_smell in ' yes co có ':
                if 10 < breathing < 20 and spo2 > 96:
                    covid_level = COVID_LEVELS.get('low')
                elif 20 < breathing < 25 and 94 < spo2 < 96:
                    covid_level = COVID_LEVELS.get('medium')
                elif 25 < breathing < 30 or 80 < spo2 < 94:
                    covid_level = COVID_LEVELS.get('severity')
                elif breathing > 30 or breathing < 10 or spo2 < 80:
                    covid_level = COVID_LEVELS.get('critical')

        dispatcher.utter_message(text='Mức độ của bệnh nhân: {}'.format(covid_level))
        if covid_level is COVID_LEVELS.get('no_symptoms') or covid_level is COVID_LEVELS.get('low'):
            dispatcher.utter_message(
                text='Người bệnh không có triệu chứng lâm sàng. Nhịp thở < 20 lần/phút,                         \
                            SpO2 > 96% khi thở khí trời.\n+Theo dõi, điều trị triệu chứng: giảm ho,             \
                            giảm đau (nếu đau ngực, đau đầu nhiều).\nKhông sử dụng kháng sinh (KS), kháng nấm.'
            )
            dispatcher.utter_message(
                text='Ăn 3 bữa chính trong ngày bằng thức ăn thông thường (như cơm, cháo, súp) phù              \
                            hợp. Có 1-2 bữa phụ (200- 250ml/ bữa phụ) với sữa/súp dinh dưỡng (dạng lỏng,dùng    \
                            ngay, chai, hộp) chuẩn (1ml=1kcal) hoặc cao năng lượng (1ml=1,25-1,5kcal), lượng    \
                            đạm cao (tối thiểu 4g protid/100kcal) để tăng thêm năng lượng, đạm, nâng cao thể    \
                            trạng, miễn dịch, ngừa hạ đường huyết:\n+Người bệnh bị suy dinh dưỡng: 2 bữa phụ/   \
                            ngày\n+Người bệnh không suy dinh dưỡng: 1 bữa phụ/ ngày.\n+Đủ nước (khoảng 2-2,5L/  \
                            ngày), nhiều hơn nếu có sốt cao, thở nhanh, tiêu chảy. Có thể bù dịch bằng Oresol.'
                )
        elif covid_level is COVID_LEVELS.get('medium'):
            dispatcher.utter_message(
                text='Xử trí: oxy kính: 2-5 lít/phút, nằm sấp nếu có thể. Cần theo dõi triệu chứng.'
            )
            dispatcher.utter_message(
                text='Ăn 3 bữa chính trong ngày bằng thức ăn thông thường (như cơm, cháo, súp) phù              \
                            hợp. Có 1-2 bữa phụ (200- 250ml/ bữa phụ) với sữa/súp dinh dưỡng (dạng lỏng,dùng    \
                            ngay, chai, hộp) chuẩn (1ml=1kcal) hoặc cao năng lượng (1ml=1,25-1,5kcal), lượng    \
                            đạm cao (tối thiểu 4g protid/100kcal) để tăng thêm năng lượng, đạm, nâng cao thể    \
                            trạng, miễn dịch, ngừa hạ đường huyết:\n+Người bệnh bị suy dinh dưỡng: 2 bữa phụ/   \
                            ngày\n+Người bệnh không suy dinh dưỡng: 1 bữa phụ/ ngày.\n+Đủ nước (khoảng 2-2,5L/  \
                            ngày), nhiều hơn nếu có sốt cao, thở nhanh, tiêu chảy. Có thể bù dịch bằng Oresol.'
            )
        elif covid_level is COVID_LEVELS.get('severity') or covid_level is COVID_LEVELS.get('critical'):
            dispatcher.utter_message(
                text='Cần thông báo nhân viên y tế phường xã'
            )

        dispatcher.utter_message(
            text='Thông tin của bệnh nhân đã được lưu lại. Nếu diễn biến bệnh thay đổi cần cập nhật.')

        return []
