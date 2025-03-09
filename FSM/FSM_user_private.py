from aiogram.fsm.state import StatesGroup, State

class MainStates(StatesGroup):
    before_registration = State()
    after_registration = State()

class RegistrationUser(StatesGroup):
    name_user = State()
    user_id = State()
    school = State()
    phone_number = State()
    mail = State()
    name_mentor = State()
    status_mentor = State()
    post_mentor = State()
    input_status_mentor = State()