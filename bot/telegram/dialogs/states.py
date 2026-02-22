from aiogram.fsm.state import State, StatesGroup




class PollSG(StatesGroup):
    welcome = State()
    check_subscription = State()
    subscription_required = State()
    start_poll = State()
    question = State()
    answer_feedback = State()
    retry_question = State()
    mid_poll_reminder = State()
    last_question = State()
    poll_completed = State()
    referral_screen = State()
    my_chances = State()
    already_completed = State()



