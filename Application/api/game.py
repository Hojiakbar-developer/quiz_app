import asyncio

from quiz_app.locales.messages import msg
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from quiz_app.service.profile_service import get_user_played, get_user_lang
from quiz_app.service.game_service import (start_session, get_current_question,
                                           help_change_quest_used, get_current_score,
                                           update_current_score, update_current_question,
                                           finish_game, get_help, save_answer, is_winner,
                                           help_50_50_used, check_current_help_50_50,
                                           check_current_help_change_quest)

from quiz_app.service.question_service import (check_answer_correctness, get_answers_id,
                                               get_question_and_answers, get_correct_answer,
                                               get_translated_question_and_answers)

async def start_game(update, user, context):
    user_id = user.id
    real_name = user.first_name
    played = get_user_played(user_id)

    session_id, start_time = start_session(user)

    context.user_data["session_id"] = session_id
    context.user_data["start_time"] = start_time
    lang = get_user_lang(user_id)

    mssg = await update.message.reply_text(text=f"\n{msg(lang, 'played')}: {played}\n{msg(lang, 'dear')} {real_name}, {msg(lang, 'game_started')}!")
    await asyncio.sleep(2)
    await mssg.delete()

    await first_question(update, user, context)

async def first_question(update, user, context):
    session_id = context.user_data["session_id"]
    lang = get_user_lang(user.id)

    current_score = get_current_score(session_id)

    quest, question_id = get_quests(current_score, lang)

    update_current_question(session_id, question_id)

    answers_id = get_answers_id(question_id)
    answer_buttons = answers_inline_buttons(answers_id, user, context)

    await update.message.reply_text(text=quest, reply_markup=InlineKeyboardMarkup(answer_buttons))

async def next_quests(query, user, context):
    session_id = context.user_data["session_id"]
    lang = get_user_lang(user.id)

    current_score = get_current_score(session_id)

    quest, question_id = get_quests(current_score, lang)

    update_current_question(session_id, question_id)

    answers_id = get_answers_id(question_id)
    answer_buttons = answers_inline_buttons(answers_id, user, context)

    await query.edit_message_text(text=quest, reply_markup=InlineKeyboardMarkup(answer_buttons))

async def check_answer_flow(query, answer_id, user, context):
    session_id = context.user_data["session_id"]
    lang = get_user_lang(user.id)

    question_id = get_current_question(session_id)

    current_score = get_current_score(session_id)

    is_correct = check_answer_correctness(answer_id)

    save_answer(session_id, question_id, answer_id, is_correct)

    if is_correct:
        current_score += 1
        update_current_score(session_id, current_score)

        mssg = await query.message.reply_text(text=f"{msg(lang, 'correct')} ✅")
        await asyncio.sleep(2)
        await mssg.delete()

    else:
        final_score = current_score
        started_at = context.user_data["start_time"]

        spent = finish_game(session_id, user, final_score, started_at)

        msg1 = await query.message.reply_text(text=f"{msg(lang, 'wrong')} ❌")

        correct_one = context.user_data["correct_answer"]
        msg2 = await query.message.reply_text(text=f"{msg(lang, 'correct_answer_was')}"
                                             f"\n{correct_one}")

        await asyncio.sleep(3)
        await query.message.delete()
        await msg1.delete()
        await msg2.delete()

        await show_final_result(query, user, final_score, spent)
        context.user_data["session_id"] = None
        context.user_data["start_time"] = None

        return

    if is_winner(current_score):
        final_score = current_score
        started_at = context.user_data["start_time"]

        spent = finish_game(session_id, user, final_score, started_at)

        await query.message.delete()

        asyncio.create_task(show_final_result(query, user, final_score, spent))

        mssg = await query.message.reply_text(text=f"{msg(lang, 'you_won').upper()}!!!")
        context.user_data["session_id"] = None
        context.user_data["start_time"] = None
        await asyncio.sleep(2)
        await mssg.delete()
        return

    await next_quests(query, user, context)

def answers_inline_buttons(answers, user, context):
    lang = get_user_lang(user.id)

    context.user_data["a"] = answers[0][0]
    context.user_data["b"] = answers[1][0]
    context.user_data["c"] = answers[2][0]
    context.user_data["d"] = answers[3][0]

    save_correct_variant(user, context)

    inline_buttons = [
        [InlineKeyboardButton(text="A", callback_data=f"game:{answers[0][0]}"),
         InlineKeyboardButton(text="B", callback_data=f"game:{answers[1][0]}")],
        [InlineKeyboardButton(text="C", callback_data=f"game:{answers[2][0]}"),
         InlineKeyboardButton(text="D", callback_data=f"game:{answers[3][0]}")],
        [InlineKeyboardButton(text=f"{msg(lang, 'help').upper()}", callback_data="game:help")]
    ]
    return inline_buttons

def help_50_50_variants_buttons(new_variants):
    new_buttons = []

    for k, v in new_variants.items():
        new_buttons.append([InlineKeyboardButton(text=k, callback_data=f"game:{v}")])

    return new_buttons

async def request_help_50_50(query, user, context):
    session_id = context.user_data["session_id"]
    lang = get_user_lang(user.id)
    help_50_50, count = check_current_help_50_50(session_id)

    if not help_50_50:
        raise ValueError(f"{msg(lang, 'help_50_50_used')}!")

    question_id = get_current_question(session_id)

    current_answers = {
        "A": context.user_data["a"],
        "B": context.user_data["b"],
        "C": context.user_data["c"],
        "D": context.user_data["d"]
    }

    new_variants = get_help(current_answers, question_id)
    buttons = help_50_50_variants_buttons(new_variants)

    help_50_50_used(session_id, user)
    await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))

async def request_help_change_quest(query, user, context):
    session_id = context.user_data["session_id"]
    lang = get_user_lang(user.id)
    change_quest, count = check_current_help_change_quest(session_id)

    if not change_quest:
        raise ValueError(f"{msg(lang, 'change_quest_used')}!")

    help_change_quest_used(session_id, user)
    await next_quests(query, user, context)

def help_buttons(user, context):
    lang = get_user_lang(user.id)
    session_id = context.user_data["session_id"]
    change_quest, change_count = check_current_help_change_quest(session_id)
    help_50_50, fifty_fifty_count = check_current_help_50_50(session_id)

    buttons = [
        [InlineKeyboardButton(f"{msg(lang, 'change_quest')} ({change_count})", callback_data="game:change_quest"),
         InlineKeyboardButton(f"{msg(lang, '50_50')} ({fifty_fifty_count})", callback_data="game:help_50_50")],
        [InlineKeyboardButton(f"⬅️ {msg(lang, 'back')}", callback_data="game:back_to_question")]
    ]
    return buttons

def save_correct_variant(user, context):
    session_id = context.user_data["session_id"]
    question_id = get_current_question(session_id)

    answer_variants = {
        "A": context.user_data["a"],
        "B": context.user_data["b"],
        "C": context.user_data["c"],
        "D": context.user_data["d"]
    }

    lang = get_user_lang(user.id)

    correct = get_correct_answer(question_id, answer_variants, lang)

    context.user_data["correct_answer"] = correct

async def show_final_result(query, user, final_score, spent_time):
    minutes, seconds = divmod(spent_time, 60)
    lang = get_user_lang(user.id)

    final_result = (f"⭐ {msg(lang, 'dear')} {user.first_name}"
                    f"\n🏆 {msg(lang, 'final_result')}: {final_score}"
                    f"\n⌛ {msg(lang, 'spent_time')}: {minutes} {msg(lang, 'minutes')} "
                                                       f"{seconds} {msg(lang, 'seconds')}")

    mssg = await query.message.reply_text(text=final_result)
    await asyncio.sleep(5)
    await mssg.delete()

def get_quests(current_score, lang):
    if lang == "en":
        quests, question_id = prepare_questions(current_score, lang)
        return quests, question_id
    else:
        quests, question_id = prepare_translated_questions(current_score, lang)
        return quests, question_id

def prepare_questions(current_score, lang):
    next_question = current_score + 1
    question_id, question, answers = get_question_and_answers(next_question)

    quest = (f"{msg(lang, 'question')} {current_score + 1}/10"
                f"\n{question}\n"
                f"\nA) {answers[0][1]}"
                f"\nB) {answers[1][1]}"
                f"\nC) {answers[2][1]}"
                f"\nD) {answers[3][1]}")

    return quest, question_id

def prepare_translated_questions(current_score, lang):
    next_question = current_score + 1
    question_id, question, answers = get_translated_question_and_answers(next_question, lang)

    quest = (f"{msg(lang, 'question')} {current_score + 1}/10"
                f"\n{question}\n"
                f"\nA) {answers[0][0]}"
                f"\nB) {answers[1][0]}"
                f"\nC) {answers[2][0]}"
                f"\nD) {answers[3][0]}")

    return quest, question_id