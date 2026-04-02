import re
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# ===================== CONFIGURATION =====================
USERNAME = "your_username_here"      # <-- replace with your login.
PASSWORD = "your_password_here"      # <-- replace with your password.
BASE_URL = ""                        #LINK UR UNI MY UNI CALLED САМГТУ.
LOGIN_URL = f"{BASE_URL}/site/login"
API_URL = f"{BASE_URL}/distancelearning/distancelearning/calendar-data"

session = requests.Session()
# ==========================================================

def login():
    """Авторизация с получением CSRF-токена"""
    resp = session.get(LOGIN_URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    csrf_input = soup.find("input", {"name": "_csrf"})
    if not csrf_input:
        return False
    csrf = csrf_input.get("value")

    payload = {
        "_csrf": csrf,
        "LoginForm[username]": USERNAME,
        "LoginForm[password]": PASSWORD,
        "LoginForm[rememberMe]": "1",
    }
    resp = session.post(LOGIN_URL, data=payload, allow_redirects=True)
    soup = BeautifulSoup(resp.text, "html.parser")
    login_form = soup.find("form", {"id": "login-form"}) or soup.find("input", {"name": "LoginForm[username]"})
    return login_form is None

def fetch_events(start_date, end_date):
    params = {
        "start": start_date.strftime("%Y-%m-%dT00:00:00+04:00"),
        "end": end_date.strftime("%Y-%m-%dT23:59:59+04:00")
    }
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{BASE_URL}/distancelearning/distancelearning/index"
    }
    resp = session.get(API_URL, params=params, headers=headers)
    resp.raise_for_status()
    text = resp.text
    if text.startswith("\ufeff"):
        text = text[1:]
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data
    except json.JSONDecodeError as e:
        print(f"Ошибка JSON: {e}")
        print(text[:500])
        raise

def clean_html(text):
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def parse_event(event):
    start_str = event.get("start", "")
    if not start_str:
        return None
    try:
        dt = datetime.fromisoformat(start_str.replace("Z", "+00:00").replace("+04:00", ""))
    except:
        return None
    date_str = dt.strftime("%d.%m.%Y")
    time_str = dt.strftime("%H:%M")

    title = event.get("title", "")
    description = event.get("description", "")
    clean_desc = clean_html(description)

    lesson_type = "Другое"
    if "лекц" in clean_desc.lower() or "лекция" in clean_desc.lower():
        lesson_type = "лекция"
    elif "лаб" in clean_desc.lower() or "лабораторная" in clean_desc.lower():
        lesson_type = "лабораторная"
    elif "практ" in clean_desc.lower() or "практика" in clean_desc.lower():
        lesson_type = "практика"

    teacher = ""
    group = ""
    if clean_desc:
        lines = [line.strip() for line in clean_desc.split("\n") if line.strip()]
        for line in lines:
            if "Гаспаров" in line or "Трофим" in line or "Панфилова" in line:
                teacher = line
            elif "2-ИАИТ" in line or "2-ИМИТ" in line:
                group = line

    room = re.search(r"ауд\.?\s*(\d+)", clean_desc, re.IGNORECASE)
    room = room.group(1) if room else ""

    return {
        "date": date_str,
        "time": time_str,
        "subject": title,
        "type": lesson_type,
        "teacher": teacher,
        "room": room,
        "group": group,
        "url": event.get("url", "")
    }

def get_schedule_for_period(start_date, end_date):
    events = fetch_events(start_date, end_date)
    parsed = []
    for ev in events:
        p = parse_event(ev)
        if p:
            parsed.append(p)
    return parsed

def print_lesson(lesson, index=None):
    prefix = f"{index}. " if index else ""
    print(f"{prefix}{lesson['time']} | {lesson['type']} | {lesson['subject']}")
    if lesson['teacher']:
        print(f"  Преподаватель: {lesson['teacher']}")
    if lesson['room']:
        print(f"  Аудитория: {lesson['room']}")
    if lesson['group']:
        print(f"  Группа: {lesson['group']}")
    if lesson['url']:
        print(f"  Ссылка: {BASE_URL}{lesson['url']}")
    print("-" * 50)

def main():
    print("=" * 60)
    print("ЭМУЛЯТОР РАСПИСАНИЯ САМГТУ")
    print("=" * 60)

    print("Авторизация...", end=" ", flush=True)
    if not login():
        print("ОШИБКА! Проверьте логин/пароль.")
        return
    print("УСПЕШНО")

    now = datetime.now()
    start_date = now.replace(day=1)
    if start_date.month == 12:
        end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)

    print(f"Загрузка расписания за {start_date.strftime('%B %Y')}...", end=" ", flush=True)
    try:
        schedule = get_schedule_for_period(start_date, end_date)
    except Exception as e:
        print(f"\nОшибка загрузки: {e}")
        return
    print(f"{len(schedule)} занятий")

    if not schedule:
        print("Нет данных.")
        return

    while True:
        print("\nВыберите действие:")
        print("1. Расписание на день")
        print("2. Поиск по предмету")
        print("3. Поиск по преподавателю")
        print("0. Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("До свидания!")
            break
        elif choice == "1":
            day_str = input("Введите дату (ДД.ММ.ГГГГ): ").strip()
            day_lessons = [l for l in schedule if l['date'] == day_str]
            if not day_lessons:
                print(f"Занятий на {day_str} не найдено.")
                continue
            print(f"\nРасписание на {day_str}:")
            for i, l in enumerate(day_lessons, 1):
                print_lesson(l, i)
        elif choice == "2":
            subject_query = input("Введите название предмета (или его часть): ").strip().lower()
            matches = [l for l in schedule if subject_query in l['subject'].lower()]
            if not matches:
                print("Ничего не найдено.")
                continue
            teachers = set(l['teacher'] for l in matches if l['teacher'])
            print(f"\nНайдено {len(matches)} занятий по предмету '{subject_query}':")
            if teachers:
                print("Преподаватели:", ", ".join(teachers))
            print()
            for i, l in enumerate(matches, 1):
                print_lesson(l, i)
        elif choice == "3":
            teacher_query = input("Введите фамилию преподавателя (или его имя): ").strip().lower()
            matches = [l for l in schedule if teacher_query in l['teacher'].lower()]
            if not matches:
                print("Ничего не найдено.")
                continue
            subjects = set(l['subject'] for l in matches)
            print(f"\nПреподаватель: {matches[0]['teacher']} (пример)")
            print(f"Всего занятий: {len(matches)}")
            print("Предметы:")
            for subj in sorted(subjects):
                print(f"  - {subj}")
            print("\nРасписание:")
            for i, l in enumerate(matches, 1):
                print_lesson(l, i)
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()    """Удаляет HTML-теги и возвращает чистый текст"""
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)

def parse_event(event):
    start_str = event.get("start", "")
    if not start_str:
        return None
    try:
        dt = datetime.fromisoformat(start_str.replace("Z", "+00:00").replace("+04:00", ""))
    except:
        return None
    date_str = dt.strftime("%d.%m.%Y")
    time_str = dt.strftime("%H:%M")

    title = event.get("title", "")
    description = event.get("description", "")
    clean_desc = clean_html(description)

    # Определяем тип занятия
    lesson_type = "Другое"
    if "лекц" in clean_desc.lower() or "лекция" in clean_desc.lower():
        lesson_type = "лекция"
    elif "лаб" in clean_desc.lower() or "лабораторная" in clean_desc.lower():
        lesson_type = "лабораторная"
    elif "практ" in clean_desc.lower() or "практика" in clean_desc.lower():
        lesson_type = "практика"

    # Извлекаем преподавателя и группу из описания
    teacher = ""
    group = ""
    if clean_desc:
        lines = [line.strip() for line in clean_desc.split("\n") if line.strip()]
        for line in lines:
            if "Гаспаров" in line or "Трофим" in line or "Панфилова" in line:
                teacher = line
            elif "2-ИАИТ" in line or "2-ИМИТ" in line:
                group = line

    # Аудитория (если есть)
    room = re.search(r"ауд\.?\s*(\d+)", clean_desc, re.IGNORECASE)
    room = room.group(1) if room else ""

    return {
        "date": date_str,
        "time": time_str,
        "subject": title,
        "type": lesson_type,
        "teacher": teacher,
        "room": room,
        "group": group,
        "url": event.get("url", "")
    }

def get_schedule_for_period(start_date, end_date):
    events = fetch_events(start_date, end_date)
    parsed = []
    for ev in events:
        p = parse_event(ev)
        if p:
            parsed.append(p)
    return parsed

def print_lesson(lesson, index=None):
    prefix = f"{index}. " if index else ""
    print(f"{prefix}{lesson['time']} | {lesson['type']} | {lesson['subject']}")
    if lesson['teacher']:
        print(f"  Преподаватель: {lesson['teacher']}")
    if lesson['room']:
        print(f"  Аудитория: {lesson['room']}")
    if lesson['group']:
        print(f"  Группа: {lesson['group']}")
    if lesson['url']:
        print(f"  Ссылка: {BASE_URL}{lesson['url']}")
    print("-" * 50)

def main():
    print("=" * 60)
    print("ЭМУЛЯТОР РАСПИСАНИЯ САМГТУ")
    print("=" * 60)

    print("Авторизация...", end=" ", flush=True)
    if not login():
        print("ОШИБКА! Проверьте логин/пароль.")
        return
    print("УСПЕШНО")

    now = datetime.now()
    start_date = now.replace(day=1)
    if start_date.month == 12:
        end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)

    print(f"Загрузка расписания за {start_date.strftime('%B %Y')}...", end=" ", flush=True)
    try:
        schedule = get_schedule_for_period(start_date, end_date)
    except Exception as e:
        print(f"\nОшибка загрузки: {e}")
        return
    print(f"{len(schedule)} занятий")

    if not schedule:
        print("Нет данных.")
        return

    while True:
        print("\nВыберите действие:")
        print("1. Расписание на день")
        print("2. Поиск по предмету")
        print("3. Поиск по преподавателю")
        print("0. Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("До свидания!")
            break

        elif choice == "1":
            day_str = input("Введите дату (ДД.ММ.ГГГГ): ").strip()
            day_lessons = [l for l in schedule if l['date'] == day_str]
            if not day_lessons:
                print(f"Занятий на {day_str} не найдено.")
                continue
            print(f"\nРасписание на {day_str}:")
            for i, l in enumerate(day_lessons, 1):
                print_lesson(l, i)

        elif choice == "2":
            subject_query = input("Введите название предмета (или его часть): ").strip().lower()
            matches = [l for l in schedule if subject_query in l['subject'].lower()]
            if not matches:
                print("Ничего не найдено.")
                continue
            teachers = set(l['teacher'] for l in matches if l['teacher'])
            print(f"\nНайдено {len(matches)} занятий по предмету '{subject_query}':")
            if teachers:
                print("Преподаватели:", ", ".join(teachers))
            print()
            for i, l in enumerate(matches, 1):
                print_lesson(l, i)

        elif choice == "3":
            teacher_query = input("Введите фамилию преподавателя (или его имя): ").strip().lower()
            matches = [l for l in schedule if teacher_query in l['teacher'].lower()]
            if not matches:
                print("Ничего не найдено.")
                continue

            subjects = set(l['subject'] for l in matches)
            print(f"\nПреподаватель: {matches[0]['teacher']} (пример)")
            print(f"Всего занятий: {len(matches)}")
            print("Предметы:")
            for subj in sorted(subjects):
                print(f"  - {subj}")
            print("\nРасписание:")
            for i, l in enumerate(matches, 1):
                print_lesson(l, i)

        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()
