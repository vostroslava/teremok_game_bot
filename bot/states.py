from aiogram.fsm.state import State, StatesGroup


class LeadForm(StatesGroup):
    """States for lead collection form"""
    waiting_for_name = State()
    waiting_for_role = State()
    waiting_for_company = State()
    waiting_for_team_size = State()
    waiting_for_contacts = State()
    waiting_for_request = State()
