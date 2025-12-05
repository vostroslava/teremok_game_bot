from aiogram import Router, F, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards import diagnostics_keyboard, back_to_menu_keyboard
from core.logic import DIAGNOSTIC_QUESTIONS, calculate_result
from core.texts import TYPES_DATA

router = Router()

class DiagnosticState(StatesGroup):
    question_1 = State()
    question_2 = State()
    question_3 = State()
    question_4 = State()
    question_5 = State()
    finished = State()

# Mapping question ID to State
QUESTION_STATES = {
    1: DiagnosticState.question_1,
    2: DiagnosticState.question_2,
    3: DiagnosticState.question_3,
    4: DiagnosticState.question_4,
    5: DiagnosticState.question_5
}

@router.callback_query(F.data == "start_diagnostic")
async def cb_start_diagnostic(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(DiagnosticState.question_1)
    await state.update_data(scores={})
    
    q = DIAGNOSTIC_QUESTIONS[0]
    await callback.message.edit_text(
        f"❓ **Вопрос 1/{len(DIAGNOSTIC_QUESTIONS)}**\n\n{q.text}",
        reply_markup=diagnostics_keyboard(q.id, q.options),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("ans_"))
async def cb_answer(callback: CallbackQuery, state: FSMContext):
    # Data: ans_{question_id}_{option_index}
    parts = callback.data.split("_")
    q_id = int(parts[1])
    opt_index = int(parts[2])
    
    # Get current scores
    data = await state.get_data()
    scores = data.get("scores", {})
    
    # Update scores
    question = next((q for q in DIAGNOSTIC_QUESTIONS if q.id == q_id), None)
    if question:
        option_score = question.options[opt_index]['score']
        for type_key, pts in option_score.items():
            scores[type_key] = scores.get(type_key, 0) + pts
    
    await state.update_data(scores=scores)
    
    # Next question
    next_q_id = q_id + 1
    if next_q_id > len(DIAGNOSTIC_QUESTIONS):
        # Finish
        result_id = calculate_result(scores)
        type_data = TYPES_DATA.get(result_id)
        
        await state.clear()
        
        res_text = (
            f"✅ **Диагностика завершена!**\n\n"
            f"По вашим ответам вы ближе всего к типажу: **{type_data.emoji} {type_data.name_ru}**.\n\n"
            f"{type_data.short_desc}\n\n"
            f"_Это лишь гипотеза, для точного результата нужны глубокие собеседования._"
        )
        await callback.message.edit_text(res_text, reply_markup=back_to_menu_keyboard(), parse_mode="Markdown")
        return

    # Show next question
    next_q = next((q for q in DIAGNOSTIC_QUESTIONS if q.id == next_q_id), None)
    if next_q:
        # Set stat
        # Note: In aiogram FSM, setting state manually isn't strictly required if we just flow, 
        # but good practice if we want to handle input text later. 
        # Here we only use buttons so state is less critical for logic flow but good for persistence.
        # However, since we defined StatesGroup, let's use it.
        # But wait, logic to map ID to State is a bit redundant if we just iterate.
        # Let's just update text.
        
        await callback.message.edit_text(
            f"❓ **Вопрос {next_q_id}/{len(DIAGNOSTIC_QUESTIONS)}**\n\n{next_q.text}",
            reply_markup=diagnostics_keyboard(next_q.id, next_q.options),
            parse_mode="Markdown"
        )
