from quiz_app.repository.user_repo import (fetch_user_profile_by_id, fetch_user_profiles,
                                           update_user_language, fetch_user_language,
                                           fetch_user_played, fetch_users_by_rating)
from quiz_app.locales.messages import msg
from quiz_app.logger import logger
from quiz_app.validation import validate_language

def get_user_profile(user_id):
    lang = get_user_lang(user_id)
    profile = fetch_user_profile_by_id(user_id)

    user_profile = f"======= {msg(lang, 'your_profile')} =======\n"

    u_id = profile[0]
    r_name = profile[1]
    u_name = profile[2]

    best_score = profile[3]
    overall_score = profile[4]
    played = profile[5]
    won = profile[6]
    active = profile[7]
    top = get_user_rating(user_id)
    rete = top_ratings(top)

    lang = get_user_lang(user_id)

    if not u_name:
        user_name = f"{msg(lang, 'unknown')}"
    else:
        user_name = "@" + u_name

    if not active:
        activeness = f"{msg(lang, 'inactive')}"
        signal = "🔴"
    else:
        activeness = f"{msg(lang, 'active')}"
        signal = "🟢"

    user_profile += (f"\n---------- 👤 {msg(lang, 'identity')} ----------"
                     f"\n🆔 - {u_id}"
                     f"\n👤 {msg(lang, 'name')}: {r_name}"
                     f"\n🏷 {msg(lang, 'nick')}: {user_name}"
                     f"\n🌐 {msg(lang, 'language')}: {lang}\n"
                     f"\n-------- 📊 {msg(lang, 'statistics')} --------"
                     f"\n🏆 {msg(lang, 'best_score')}: {best_score}"
                     f"\n⭐ {msg(lang, 'overall_score')}: {overall_score}"
                     f"\n🎮 {msg(lang, 'played')}: {played}"
                     f"\n🎯 {msg(lang, 'win')}: {won}"
                     f"\n{signal} {msg(lang, 'status')}: {activeness}"
                     f"\n🔝 {msg(lang, 'rating')}: TOP {rete}")

    return user_profile

def get_users_profiles():
    profiles = fetch_user_profiles()

    user_profiles = "======== Profiles ========\n"

    user = 0
    for u_id, r_name, u_name, best_score, ov_score, played, won, active in profiles:
        user += 1
        top = get_user_rating(u_id)
        rate = top_ratings(top)

        lang = get_user_lang(u_id)

        if not u_name:
            user_name = "Unknown"
        else:
            user_name = "@" + u_name

        if not active:
            activeness = "Inactive"
            signal = "🔴"
        else:
            activeness = "Active"
            signal = "🟢"

        user_profiles += (f"\n======== User {user} ========"
                          f"\n--------- 👤 Identity ---------"
                          f"\n🆔 - {u_id}"
                          f"\n👤 Name: {r_name}"
                          f"\n🏷 Nick: {user_name}"
                          f"\n🌐 Language: {lang}\n"
                          f"\n-------- Statistics --------"
                          f"\n🏆 Record: {best_score}"
                          f"\n⭐ Overall score: {ov_score}"
                          f"\n🎮 Played: {played}"
                          f"\n🎯 Win: {won}"
                          f"\n{signal} Status: {activeness}"
                          f"\n🔝 Rating: TOP {rate}"
                          f"\n======================\n")
    return user_profiles

def get_user_rating(user_id):
    users = get_all_users_by_rating()

    user_rating = 0

    top = 0
    for uid, f_name, u_name, played, ov_score, won in users:
        top += 1
        if uid == user_id:
            user_rating = top
            break

    return user_rating

def get_rating(user_id):
    lang = get_user_lang(user_id)
    users = get_all_users_by_rating()
    rating_list = f"========= {msg(lang, 'rating').upper()} =========\n"

    user_rating = 0

    top = 0
    for uid, f_name, u_name, played, ov_score, won in users:
        top += 1
        if uid == user_id:
            rate = top_ratings(top)
            user_rating = rate

        if top <= 10:
            rate = top_ratings(top)

            if not u_name:
                u_name = f"{msg(lang, 'unknown')}"
            else:
                u_name = "@" + u_name

            rating_list += (f"\n------------ TOP {rate} ------------"
                            f"\n👤 {msg(lang, 'name')}: {f_name}"
                            f"\n🏷 {msg(lang, 'nick')}: {u_name}\n"
                            f"\n------- 📊 {msg(lang, 'statistics')} -------\n"
                            f"\n🏆 {msg(lang, 'overall_score')}: {ov_score}"
                            f"\n🎯 {msg(lang, 'win')}: {won}"
                            f"\n🎮 {msg(lang, 'played')}: {played}\n")

    rating_list += (f"\n--------------------------------"
                    f"\n{msg(lang, 'your_rating')} TOP {user_rating}")
    return rating_list

def top_ratings(top):
    if top == 1:
        rate = "🥇"
    elif top == 2:
        rate = "🥈"
    elif top == 3:
        rate = "🥉"
    else:
        rate = top

    return rate

def get_all_users_by_rating():
    users = fetch_users_by_rating()
    return users

def get_user_played(user_id):
    played = fetch_user_played(user_id)[0]

    return played

def update_user_lang(user, lang):
    validate_language(lang)

    user_lang = get_user_lang(user.id)

    if lang == user_lang:
        logger.warning(f"User {user.id} ({user.first_name}) tried to change language {user_lang} to {lang}")
        raise ValueError(f"{msg(user_lang, 'your_lang_already')}")

    update_user_language(lang, user.id)

    logger.info(f"User {user.id} ({user.first_name}) changed language to {lang}")

def get_user_lang(user_id):
    lang = fetch_user_language(user_id)[0]
    return lang

def get_settings(user_id):
    user_lang = get_user_lang(user_id)

    user_setting = f"====== {msg(user_lang, 'settings')} ======\n"
    if user_lang == "en":
         user_setting += f"\n🌐 {msg(user_lang, 'language')}: English"
    elif user_lang == "uz":
        user_setting += f"\n🌐 {msg(user_lang, 'language')}: Uzbek"

    return user_setting