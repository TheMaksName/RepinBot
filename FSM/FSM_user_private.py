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

class EditProfile(StatesGroup):
    edit_name = State()
    edit_school = State()
    edit_phone_number = State()
    edite_mail = State()
    edit_name_mentor = State()
    edit_post_mentor = State()

