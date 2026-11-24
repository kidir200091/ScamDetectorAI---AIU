
import re
from io import BytesIO
from pathlib import Path

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="ScamDetector AI",
    page_icon="🛡️",
    layout="centered"
)

# ==================================================
# 2. LANGUAGES
# ==================================================

LANGUAGES = {
    "🇰🇿 Қазақша": "Қазақша",
    "🇷🇺 Русский": "Русский",
    "🇺🇸 English": "English"
}

if "language" not in st.session_state:
    st.session_state.language = "Қазақша"

if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

selected_flag = st.sidebar.radio(
    "🌐 Тіл / Язык / Language",
    list(LANGUAGES.keys()),
    index=list(LANGUAGES.values()).index(
        st.session_state.language
    )
)

lang = LANGUAGES[selected_flag]
st.session_state.language = lang

# ==================================================
# 3. TRANSLATIONS
# ==================================================

T = {
    "subtitle": {
        "Қазақша": "Интернет алаяқтықты анықтау жүйесі",
        "Русский": "Система обнаружения интернет-мошенничества",
        "English": "Internet Fraud Detection System"
    },
    "description": {
        "Қазақша": "SMS, WhatsApp және басқа хабарламаларды тексеріңіз.",
        "Русский": "Проверяйте SMS, WhatsApp и другие сообщения.",
        "English": "Check SMS, WhatsApp and other messages."
    },
    "input": {
        "Қазақша": "📩 Хабарламаны енгізіңіз:",
        "Русский": "📩 Введите сообщение:",
        "English": "📩 Enter your message:"
    },
    "placeholder": {
        "Қазақша": "Мысалы: Сіздің картаңыз бұғатталды...",
        "Русский": "Например: Ваша карта заблокирована...",
        "English": "Example: Your bank card has been blocked..."
    },
    "button": {
        "Қазақша": "🔍 Хабарламаны тексеру",
        "Русский": "🔍 Проверить сообщение",
        "English": "🔍 Check message"
    },
    "empty": {
        "Қазақша": "Алдымен хабарламаны енгізіңіз.",
        "Русский": "Сначала введите сообщение.",
        "English": "Please enter a message first."
    },
    "result": {
        "Қазақша": "📊 Талдау нәтижесі",
        "Русский": "📊 Результат анализа",
        "English": "📊 Analysis result"
    },
    "score": {
        "Қазақша": "Қауіп көрсеткіші",
        "Русский": "Показатель риска",
        "English": "Risk score"
    },
    "high": {
        "Қазақша": "🚨 ЖОҒАРЫ ҚАУІП",
        "Русский": "🚨 ВЫСОКИЙ РИСК",
        "English": "🚨 HIGH RISK"
    },
    "medium": {
        "Қазақша": "⚠️ ОРТАША ҚАУІП",
        "Русский": "⚠️ СРЕДНИЙ РИСК",
        "English": "⚠️ MEDIUM RISK"
    },
    "low": {
        "Қазақша": "✅ ТӨМЕН ҚАУІП",
        "Русский": "✅ НИЗКИЙ РИСК",
        "English": "✅ LOW RISK"
    },
    "found": {
        "Қазақша": "### Анықталған белгілер",
        "Русский": "### Обнаруженные признаки",
        "English": "### Detected indicators"
    },
    "no_signs": {
        "Қазақша": "Қауіп белгілері табылған жоқ.",
        "Русский": "Признаки риска не обнаружены.",
        "English": "No risk indicators were detected."
    },
    "links": {
        "Қазақша": "### Күмәнді сілтемелер",
        "Русский": "### Подозрительные ссылки",
        "English": "### Suspicious links"
    },
    "advice": {
        "Қазақша": "### 💡 Қауіпсіздік кеңесі",
        "Русский": "### 💡 Советы по безопасности",
        "English": "### 💡 Safety advice"
    },
    "advice_risky": {
        "Қазақша": "Күмәнді сілтемелерге өтпеңіз. SMS-код, CVV, PIN және банк деректерін ешкімге бермеңіз.",
        "Русский": "Не переходите по подозрительным ссылкам. Никому не сообщайте SMS-коды, CVV, PIN и банковские данные.",
        "English": "Do not open suspicious links or share SMS codes, CVV, PIN or banking details."
    },
    "advice_safe": {
        "Қазақша": "Белгілі қауіп белгілері аз. Дегенмен жіберушіні тексеріңіз.",
        "Русский": "Обнаружено мало признаков мошенничества. Проверьте отправителя.",
        "English": "Few fraud indicators were detected. Still, verify the sender."
    },
    "history": {
        "Қазақша": "📋 Тексеру тарихы",
        "Русский": "📋 История проверок",
        "English": "📋 Check history"
    },
    "no_history": {
        "Қазақша": "Әзірге тексерілген хабарламалар жоқ.",
        "Русский": "Пока нет проверенных сообщений.",
        "English": "No messages have been checked yet."
    },
    "message": {
        "Қазақша": "Хабарлама:",
        "Русский": "Сообщение:",
        "English": "Message:"
    },
    "risk": {
        "Қазақша": "Қауіп деңгейі:",
        "Русский": "Уровень риска:",
        "English": "Risk level:"
    },
    "points": {
        "Қазақша": "Балл:",
        "Русский": "Баллы:",
        "English": "Score:"
    },
    "pdf": {
        "Қазақша": "📄 PDF есебін жүктеу",
        "Русский": "📄 Скачать PDF-отчёт",
        "English": "📄 Download PDF report"
    },
    "pdf_error": {
        "Қазақша": "PDF жасау қатесі:",
        "Русский": "Ошибка создания PDF:",
        "English": "PDF creation error:"
    },
    "footer": {
        "Қазақша": "ScamDetector AI | Киберқауіпсіздік жобасы",
        "Русский": "ScamDetector AI | Проект по кибербезопасности",
        "English": "ScamDetector AI | Cybersecurity Project"
    }
}

def tr(key):
    return T[key][lang]

# ==================================================
# 4. CATEGORY TRANSLATIONS
# ==================================================

CATEGORIES = {
    "urgency": {
        "Қазақша": "Шұғыл әрекетке мәжбүрлеу",
        "Русский": "Принуждение к срочным действиям",
        "English": "Pressure to act urgently"
    },
    "bank_threat": {
        "Қазақша": "Банк атынан қорқыту",
        "Русский": "Угрозы от имени банка",
        "English": "Bank-related threats"
    },
    "money_transfer": {
        "Қазақша": "Ақша аударуды талап ету",
        "Русский": "Требование перевести деньги",
        "English": "Request to transfer money"
    },
    "private_data": {
        "Қазақша": "Құпия деректерді сұрау",
        "Русский": "Запрос конфиденциальных данных",
        "English": "Request for private information"
    },
    "prize": {
        "Қазақша": "Жүлде немесе сыйлық уәдесі",
        "Русский": "Обещание приза или подарка",
        "English": "Promise of a prize or gift"
    },
    "suspicious_link": {
        "Қазақша": "Күмәнді сілтеме",
        "Русский": "Подозрительная ссылка",
        "English": "Suspicious link"
    },
    "data_confirmation": {
        "Қазақша": "Жеке деректерді растауды талап ету",
        "Русский": "Требование подтвердить личные данные",
        "English": "Request to confirm personal data"
    }
}

def category_name(key):
    return CATEGORIES[key][lang]

# ==================================================
# 5. DESIGN
# ==================================================

st.markdown("""
<style>
.block-container {
    max-width: 850px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.main-title {
    text-align: center;
    font-size: 35px;
    font-weight: bold;
}
.subtitle {
    text-align: center;
    color: #777;
    font-size: 16px;
}
div.stButton > button,
div.stDownloadButton > button {
    width: 100%;
    border-radius: 10px;
    min-height: 45px;
    font-weight: 600;
}
@media (max-width: 600px) {
    .main-title {
        font-size: 27px;
    }
    .block-container {
        padding: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🛡️ ScamDetector AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="subtitle">{tr("subtitle")}</div>',
    unsafe_allow_html=True
)

st.write(tr("description"))
st.divider()

# ==================================================
# 6. FRAUD DETECTION RULES
# ==================================================

RULES = {
    "urgency": [
        "срочно", "немедленно", "шұғыл",
        "тез арада", "сейчас же", "сегодня",
        "последний шанс", "дереу", "бірден",
        "immediately", "urgent", "right now",
        "within 5 minutes", "act now"
    ],
    "bank_threat": [
        "карта заблокирована", "картаңыз бұғатталды",
        "банк қауіпсіздік қызметі", "счет заблокирован",
        "аккаунт заблокирован", "шотыңыз бұғатталады",
        "your account is blocked", "your card is blocked",
        "account will be suspended", "bank security"
    ],
    "money_transfer": [
        "переведите деньги", "ақша аударыңыз",
        "оплатите", "төлем жасаңыз",
        "перевод на карту", "отправьте деньги",
        "ақша жіберіңіз", "transfer money",
        "send money", "make a payment"
    ],
    "private_data": [
        "пароль", "құпиясөз", "код из sms",
        "смс код", "cvv", "pin-код",
        "карта деректерін", "кодты жіберіңіз",
        "введите данные карты", "подтвердите личность",
        "введите пароль", "card number",
        "security code", "verification code",
        "password", "one-time password"
    ],
    "prize": [
        "вы выиграли", "сіз ұттыңыз",
        "получите приз", "сыйлық ұтып алдыңыз",
        "бесплатный подарок", "вам начислен бонус",
        "вы стали победителем", "you have won",
        "claim your prize", "free gift",
        "congratulations winner"
    ],
    "suspicious_link": [
        "http://", "https://", "www.",
        "bit.ly", "tinyurl.com", "cutt.ly",
        "t.co", "is.gd", "rb.gy", "goo.su"
    ],
    "data_confirmation": [
        "подтвердите данные", "растаңыз деректеріңізді",
        "перейдите по ссылке", "сілтеме арқылы өтіңіз",
        "обновите данные", "деректеріңізді жаңартыңыз",
        "confirm your details", "verify your account",
        "update your information"
    ]
}

# ==================================================
# 7. MESSAGE ANALYSIS
# ==================================================

def analyze_message(message):
    text = message.lower()

    found = []

    for category, words in RULES.items():
        if any(word in text for word in words):
            found.append(category)

    links = re.findall(
        r"https?://[^\s]+|www\.[^\s]+",
        text
    )

    weights = {
        "private_data": 40,
        "money_transfer": 30,
        "bank_threat": 30,
        "suspicious_link": 20,
        "prize": 15,
        "urgency": 10,
        "data_confirmation": 15
    }

    score = sum(weights.get(item, 0) for item in found)

    # Critical requests for confidential codes
    critical_patterns = [
        r"\bcvv\b",
        r"\bpin[- ]?код\b",
        r"\bкод из sms\b",
        r"\bsms[- ]?код\b",
        r"смс код",
        r"растау код",
        r"verification code",
        r"one[- ]time password",
        r"одноразов(ый|ого) код"
    ]

    if any(re.search(pattern, text) for pattern in critical_patterns):
        score += 20

    # Multiple independent indicators
    if len(found) >= 3:
        score += 10

    if len(found) >= 5:
        score += 10

    score = min(score, 100)

    if score >= 75:
        level = "HIGH"
    elif score >= 35:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level, found, links

# ==================================================
# 8. PDF REPORT
# ==================================================

def make_pdf(result, selected_lang):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    page_width, page_height = A4
    regular_font = "Helvetica"
    bold_font = "Helvetica-Bold"

    font_candidates = [
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        ),
        (
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf"
        )
    ]

    for regular_path, bold_path in font_candidates:
        if Path(regular_path).exists():
            try:
                pdfmetrics.registerFont(
                    TTFont("ReportFont", regular_path)
                )
                regular_font = "ReportFont"

                if Path(bold_path).exists():
                    pdfmetrics.registerFont(
                        TTFont("ReportFontBold", bold_path)
                    )
                    bold_font = "ReportFontBold"

                break
            except Exception:
                pass

    labels = {
        "Қазақша": {
            "heading": "Интернет алаяқтықты анықтау есебі",
            "score": "Қауіп көрсеткіші",
            "level": "Қауіп деңгейі",
            "indicators": "Анықталған белгілер",
            "none": "Қауіп белгілері табылған жоқ.",
            "message": "Тексерілген хабарлама",
            "links": "Табылған сілтемелер",
            "advice": "Қауіпсіздік кеңесі",
            "advice_text": "Күмәнді сілтемелерге өтпеңіз және құпия кодтарды ешкімге бермеңіз."
        },
        "Русский": {
            "heading": "Отчёт об обнаружении интернет-мошенничества",
            "score": "Показатель риска",
            "level": "Уровень риска",
            "indicators": "Обнаруженные признаки",
            "none": "Признаки риска не обнаружены.",
            "message": "Проверенное сообщение",
            "links": "Найденные ссылки",
            "advice": "Совет по безопасности",
            "advice_text": "Не переходите по подозрительным ссылкам и никому не сообщайте коды."
        },
        "English": {
            "heading": "Internet Fraud Detection Report",
            "score": "Risk score",
            "level": "Risk level",
            "indicators": "Detected indicators",
            "none": "No risk indicators were detected.",
            "message": "Checked message",
            "links": "Detected links",
            "advice": "Safety advice",
            "advice_text": "Do not open suspicious links or share confidential codes."
        }
    }

    pdf_labels = labels[selected_lang]
    risk_text = {
        "HIGH": {
            "Қазақша": "ЖОҒАРЫ",
            "Русский": "ВЫСОКИЙ",
            "English": "HIGH"
        },
        "MEDIUM": {
            "Қазақша": "ОРТАША",
            "Русский": "СРЕДНИЙ",
            "English": "MEDIUM"
        },
        "LOW": {
            "Қазақша": "ТӨМЕН",
            "Русский": "НИЗКИЙ",
            "English": "LOW"
        }
    }[result["level"]][selected_lang]

    y = page_height - 55

    def write_line(text, font=None, size=10):
        nonlocal y

        if font is None:
            font = regular_font

        text = str(text)
        max_chars = 85

        chunks = []
        while len(text) > max_chars:
            split_at = text.rfind(" ", 0, max_chars)
            if split_at <= 0:
                split_at = max_chars
            chunks.append(text[:split_at])
            text = text[split_at:].lstrip()

        chunks.append(text)

        for chunk in chunks:
            if y < 55:
                pdf.showPage()
                y = page_height - 55

            pdf.setFont(font, size)
            pdf.drawString(45, y, chunk)
            y -= size + 9

    write_line("SCAMDETECTOR AI", bold_font, 18)
    write_line(pdf_labels["heading"], bold_font, 13)
    y -= 8

    write_line(
        f'{pdf_labels["score"]}: {result["score"]}/100'
    )
    write_line(
        f'{pdf_labels["level"]}: {risk_text}'
    )

    y -= 8
    write_line(pdf_labels["indicators"], bold_font, 11)

    if result["found"]:
        for category in result["found"]:
            write_line("- " + CATEGORIES[category][selected_lang])
    else:
        write_line(pdf_labels["none"])

    y -= 8
    write_line(pdf_labels["message"], bold_font, 11)
    write_line(result["message"])

    if result["links"]:
        y -= 8
        write_line(pdf_labels["links"], bold_font, 11)
        for link in result["links"]:
            write_line(link)

    y -= 8
    write_line(pdf_labels["advice"], bold_font, 11)
    write_line(pdf_labels["advice_text"])

    pdf.save()
    buffer.seek(0)

    return buffer.getvalue()

# ==================================================
# 9. MESSAGE INPUT
# ==================================================

message = st.text_area(
    tr("input"),
    placeholder=tr("placeholder"),
    height=180
)

if st.button(tr("button"), use_container_width=True):

    if not message.strip():
        st.warning(tr("empty"))

    else:
        score, level, found, links = analyze_message(message)

        result = {
            "message": message,
            "score": score,
            "level": level,
            "found": found,
            "links": links
        }

        st.session_state.last_result = result

        st.session_state.history.append({
            "message": message[:100],
            "level": level,
            "score": score
        })

# ==================================================
# 10. ANALYSIS RESULT
# ==================================================

result = st.session_state.last_result

if result:
    st.divider()
    st.subheader(tr("result"))

    st.metric(
        tr("score"),
        f'{result["score"]}/100'
    )

    if result["level"] == "HIGH":
        st.error(tr("high"))

    elif result["level"] == "MEDIUM":
        st.warning(tr("medium"))

    else:
        st.success(tr("low"))

    st.progress(result["score"] / 100)

    if result["found"]:
        st.markdown(tr("found"))

        for item in result["found"]:
            st.write("🔴", category_name(item))
    else:
        st.info(tr("no_signs"))

    if result["links"]:
        st.markdown(tr("links"))

        for link in result["links"]:
            st.write("🔗", link)

    st.markdown(tr("advice"))

    if result["score"] >= 35:
        st.warning(T["advice_risky"][lang])
    else:
        st.info(T["advice_safe"][lang])

    try:
        pdf_data = make_pdf(result, lang)

        st.download_button(
            label=tr("pdf"),
            data=pdf_data,
            file_name="ScamDetector_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    except Exception as error:
        st.error(f'{tr("pdf_error")} {error}')

# ==================================================
# 11. CHECK HISTORY
# ==================================================

st.divider()
st.subheader(tr("history"))

if st.session_state.history:
    for item in reversed(st.session_state.history):
        st.write(tr("message"), item["message"])

        risk_names = {
            "HIGH": {
                "Қазақша": "ЖОҒАРЫ",
                "Русский": "ВЫСОКИЙ",
                "English": "HIGH"
            },
            "MEDIUM": {
                "Қазақша": "ОРТАША",
                "Русский": "СРЕДНИЙ",
                "English": "MEDIUM"
            },
            "LOW": {
                "Қазақша": "ТӨМЕН",
                "Русский": "НИЗКИЙ",
                "English": "LOW"
            }
        }

        st.write(
            tr("risk"),
            risk_names[item["level"]][lang]
        )

        st.write(
            tr("points"),
            f'{item["score"]}/100'
        )

        st.divider()

else:
    st.info(tr("no_history"))

# ==================================================
# 12. FOOTER
# ==================================================

st.caption(tr("footer"))
