import os
import re
import json
from difflib import SequenceMatcher

KNOWLEDGE_FOLDER = "knowledge"
MEMORY_FILE = "memory.json"

SYSTEM_PERSONALITY = """
Sen AI Tarbiya Ustozi nomli aqlli, odobli, muloyim va chuqur fikrlaydigan yordamchisan.
Sen o‘quvchilarga tarbiya, odob-axloq, ota-onaga hurmat, ustozga ehtirom,
do‘st tanlash, vaqtni qadrlash, mas’uliyat va bilim olish haqida foydali javob berasan.
Javoblaring o‘zbek tilida bo‘lsin.
Javoblaring qisqa emas, mazmunli, tushunarli va tarbiyaviy bo‘lsin.
"""

TOPIC_KEYWORDS = {
    "tarbiya.txt": [
        "tarbiya", "tarbiyali", "xulq", "muomala", "inson", "yaxshi inson",
        "mehr", "sabr", "mas'uliyat", "mas’uliyat", "kelajak"
    ],
    "odob_axloq.txt": [
        "odob", "axloq", "odobli", "axloqli", "hurmat", "halollik",
        "kamtarlik", "yolg'on", "yolg‘on", "qo'pol", "qo‘pol",
        "internet odobi", "maktab odobi"
    ],
    "ota_ona_hurmat.txt": [
        "ota", "ona", "ota-ona", "onam", "otam", "duo", "rozilik",
        "oilam", "uy", "hurmat qilish"
    ],
    "ustozga_hurmat.txt": [
        "ustoz", "muallim", "o'qituvchi", "o‘qituvchi", "dars",
        "bilim", "ehtirom", "tinglash"
    ],
    "motivatsiya.txt": [
        "motivatsiya", "ruhlantir", "charchadim", "o'qigim kelmayapti",
        "o‘qigim kelmayapti", "maqsad", "harakat", "muvaffaqiyat",
        "dangasa", "umid", "kuch"
    ],
    "dost_tanlash.txt": [
        "do'st", "do‘st", "dost", "yomon do'st", "yaxshi do'st",
        "o'rtoq", "o‘rtoq", "jamoa"
    ],
    "vaqt_qadri.txt": [
        "vaqt", "kechikish", "reja", "kun tartibi", "bekor",
        "telefon", "vaqtni qadrlash"
    ]
}


def normalize(text):
    text = text.lower()
    text = text.replace("’", "'").replace("‘", "'").replace("`", "'")
    text = re.sub(r"[^a-zA-Z0-9а-яА-ЯўқғҳЎҚҒҲ' \-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory[-20:], f, ensure_ascii=False, indent=2)
    except:
        pass


def load_knowledge():
    data = []

    if not os.path.exists(KNOWLEDGE_FOLDER):
        os.makedirs(KNOWLEDGE_FOLDER)

    for file_name in os.listdir(KNOWLEDGE_FOLDER):
        if file_name.endswith(".txt"):
            file_path = os.path.join(KNOWLEDGE_FOLDER, file_name)

            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read().strip()

            clean_text = normalize(text)

            data.append({
                "file": file_name,
                "text": text,
                "clean": clean_text
            })

    return data


knowledge = load_knowledge()
memory = load_memory()


def keyword_score(question, item):
    score = 0
    q = normalize(question)
    words = q.split()
    text = item["clean"]
    file_name = item["file"]

    for word in words:
        if len(word) > 2 and word in text:
            score += 1

    if file_name in TOPIC_KEYWORDS:
        for key in TOPIC_KEYWORDS[file_name]:
            key_norm = normalize(key)

            if key_norm in q:
                score += 15

            for word in words:
                similarity = SequenceMatcher(None, word, key_norm).ratio()
                if similarity > 0.82:
                    score += 4

    title_name = file_name.replace(".txt", "").replace("_", " ")
    if title_name in q:
        score += 20

    return score


def search_knowledge(question, top_k=3):
    results = []

    for item in knowledge:
        score = keyword_score(question, item)

        results.append({
            "file": item["file"],
            "score": score,
            "text": item["text"]
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]


def detect_intent(question):
    q = normalize(question)

    if any(x in q for x in ["salom", "assalomu", "hello", "hi"]):
        return "greeting"

    if any(x in q for x in ["rahmat", "tashakkur"]):
        return "thanks"

    if any(x in q for x in ["kim san", "kimsan", "isming", "sen nima"]):
        return "identity"

    if any(x in q for x in ["maslahat", "nima qilay", "qanday qilay"]):
        return "advice"

    return "normal"


def build_answer(question):
    intent = detect_intent(question)
    results = search_knowledge(question, top_k=3)

    best = results[0] if results else None

    if intent == "greeting":
        answer = (
            "Assalomu alaykum, aziz o‘quvchim. Men AI Tarbiya Ustozi bo‘laman. "
            "Siz bilan odob-axloq, tarbiya, bilim, vaqtni qadrlash va yaxshi inson bo‘lish haqida "
            "suhbatlashishga tayyorman."
        )

    elif intent == "thanks":
        answer = (
            "Arzimaydi. Har doim yaxshi niyat, odob va bilim yo‘lida yordam berishga tayyorman. "
            "Yana savolingiz bo‘lsa, bemalol so‘rang."
        )

    elif intent == "identity":
        answer = (
            "Men AI Tarbiya Ustozi nomli shaxsiy sun’iy intellektman. "
            "Vazifam — o‘quvchilarga tarbiya, odob-axloq, ota-onaga hurmat, ustozga ehtirom "
            "va hayotiy maslahatlar bo‘yicha yordam berish."
        )

    else:
        if best is None or best["score"] <= 0:
            answer = (
                "Bu savol bo‘yicha aniq bilim bazamda ma’lumot kamroq. "
                "Lekin umumiy maslahat shuki: har qanday holatda odob, sabr, hurmat va halollikni "
                "yo‘qotmaslik kerak. Muammoni shoshilmasdan, yaxshi niyat bilan hal qilish foydaliroq."
            )
        else:
            answer = generate_explained_answer(question, results)

    memory.append({
        "question": question,
        "answer": answer
    })
    save_memory(memory)

    return answer


def generate_explained_answer(question, results):
    main = results[0]
    text = main["text"]

    short_text = text.strip()
    if len(short_text) > 900:
        short_text = short_text[:900] + "..."

    answer = ""
    answer += "Savolingiz juda muhim.\n\n"
    answer += "Men buni shunday tushuntiraman:\n"
    answer += short_text + "\n\n"
    answer += "Hayotiy xulosa:\n"
    answer += (
        "Inson har bir vaziyatda avvalo odob, hurmat, sabr va aql bilan ish tutishi kerak. "
        "Yaxshi xulq insonni boshqalar orasida hurmatli qiladi, bilim esa kelajagini yoritadi."
    )

    return answer


def chat(question):
    return build_answer(question)


if __name__ == "__main__":
    print("=== AI TARBIYA USTOZI BRAIN SYSTEM ===")
    print("Knowledge fayllar soni:", len(knowledge))
    print("Chiqish uchun: exit")
    print()

    while True:
        q = input("Siz: ")

        if q.lower().strip() == "exit":
            break

        ans = chat(q)

        print()
        print("AI:", ans)
        print()