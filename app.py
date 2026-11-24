    
import re
from io import BytesIO
from pathlib import Path

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="ScamDetector AI",
    page_icon="🛡️",
    layout="centered"
)


# =====================================================
# 2. LANGUAGE SELECTION
# =====================================================

LANGUAGES = {
    "🇰🇿 Қазақша": "Қазақша",
    "🇷🇺 Русский": "Русский",
    "🇺🇸 English": "English",
}

if "language" not in st.session_state:
    st.session_state.language = "Қазақша"

language_names = list(LANGUAGES.values())

current_index = language_names.index(
    st.session_state.language
)

selected_flag = st.sidebar.radio(
    "🌐 Интерфейс тілі / Тіл / Language",
    options=list(LANGUAGES.keys()),
    index=current_index
)

lang = LANGUAGES[selected_flag]

st.session_state.language = lang


# =====================================================
# 3. TRANSLATION DICTIONARY
# =====================================================

T = {

    "subtitle": {
        "Қазақша": "Интернет алаяқтықты анықтау жүйесі",
        "Русский": "Система обнаружения интернет-мошенничества",
        "English": "Internet Fraud Detection System"
    },

    "description": {
        "Қазақша": "Қазақша және орысша SMS, WhatsApp хабарламаларын тексеріңіз.",
        "Русский": "Проверяйте SMS и сообщения WhatsApp на казахском и русском языках.",
        "English": "Check SMS and WhatsApp messages in Kazakh and Russian."
    },

    "input": {
        "Қазақша": "📩 Хабарламаны енгізіңіз:",
        "Русский": "📩 Введите сообщение:",
        "English": "📩 Enter your message:"
    },

    "placeholder": {
        "Қазақша": "Мысалы: Сіздің картаңыз бұғатталды...",
        "Русский": "Например: Ваша карта заблокирована...",
        "English": "Example: Your card has been blocked..."
    },

    "button": {
        "Қазақша": "🔍 Хабарламаны тексеру",
        "Русский": "🔍 Проверить сообщение",
        "English": "🔍 Check message"
    },

    "empty_input": {
        "Қазақша": "Алдымен хабарламаны енгізіңіз.",
        "Русский": "Сначала введите сообщение.",
        "English": "Please enter a message first."
    },

    "result": {
        "Қазақша": "📊 Талдау нәтижесі",
        "Русский": "📊 Результат анализа",
        "English": "📊 Analysis result"
    },

    "risk_score": {
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

    "found_title": {
        "Қазақша": "### Анықталған белгілер",
        "Русский": "### Обнаруженные признаки",
        "English": "### Detected indicators"
    },

    "no_signs": {
        "Қазақша": "Белгілі қауіп белгілері табылған жоқ.",
        "Русский": "Известные признаки риска не обнаружены.",
        "English": "No known risk indicators were found."
    },

    "links_title": {
        "Қазақша": "### Күмәнді сілтемелер",
        "Русский": "### Подозрительные ссылки",
        "English": "### Suspicious links"
    },

    "advice_title": {
        "Қазақша": "### 💡 Қауіпсіздік кеңесі",
        "Русский": "### 💡 Советы по безопасности",
        "English": "### 💡 Safety advice"
    },

    "advice_risky": {
        "Қазақша": "Сілтемелерге өтпеңіз, құпия кодтарды және банк деректерін ешкімге бермеңіз. Ақпаратты ресми сайт немесе банк арқылы тексеріңіз.",
        "Русский": "Не переходите по ссылкам и никому не сообщайте коды и банковские данные. Проверьте информацию через официальный сайт или банк.",
        "English": "Do not open suspicious links or share verification codes or banking details. Verify the information through the official website or your bank."
    },

    "advice_safe": {
        "Қазақша": "Белгілі алаяқтық белгілері аз. Дегенмен жіберушіні және ақпараттың дұрыстығын тексеріңіз.",
        "Русский": "Обнаружено мало известных признаков мошенничества. Тем не менее проверьте отправителя и достоверность информации.",
        "English": "Few known fraud indicators were detected. Still, verify the sender and the information."
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

    "message_label": {
        "Қазақша": "Хабарлама:",
        "Русский": "Сообщение:",
        "English": "Message:"
    },

    "risk_label": {
        "Қазақша": "Қауіп деңгейі:",
        "Русский": "Уровень риска:",
        "English": "Risk level:"
    },

    "score_label": {
        "Қазақша": "Балл:",
        "Русский": "Баллы:",
        "English": "Score:"
    },

    "pdf_button": {
        "Қазақша": "📄 PDF есебін жүктеу",
        "Русский": "📄 Скачать PDF-отчёт",
        "English": "📄 Download PDF report"
    },

    "pdf_error": {
        "Қазақша": "PDF жасау кезінде қате шықты:",
        "Русский": "Ошибка при создании PDF:",
        "English": "Error creating PDF:"
    },

    "footer": {
        "Қазақша": "ScamDetector AI | Киберқауіпсіздік жобасы",
        "Русский": "ScamDetector AI | Проект по кибербезопасности",
        "English": "ScamDetector AI | Cybersecurity Project"
    },

    "risk_names": {
        "Қазақша": {
            "HIGH": "ЖОҒАРЫ",
            "MEDIUM": "ОРТАША",
            "LOW": "ТӨМЕН"
        },
        "Русский": {
            "HIGH": "ВЫСОКИЙ",
            "MEDIUM": "СРЕДНИЙ",
            "LOW": "НИЗКИЙ"
        },
        "English": {
            "HIGH": "HIGH",
            "MEDIUM": "MEDIUM",
            "LOW": "LOW"
        }
    },

    "categories": {
        "Қазақша": {
            "urgency": "Шұғыл әрекетке мәжбүрлеу",
            "bank_threat": "Банк атынан қорқыту",
            "money_transfer": "Ақша аударуды талап ету",
            "private_data": "Құпия деректерді сұрау",
            "prize": "Жүлде немесе сыйлық уәдесі",
            "suspicious_link": "Күмәнді сілтеме",
            "data_confirmation": "Жеке деректерді растауды талап ету"
        },

        "Русский": {
            "urgency": "Принуждение к срочным действиям",
            "bank_threat": "Угрозы от имени банка",
            "money_transfer": "Требование перевести деньги",
            "private_data": "Запрос конфиденциальных данных",
            "prize": "Обещание приза или подарка",
            "suspicious_link": "Подозрительная ссылка",
            "data_confirmation": "Требование подтвердить личные данные"
        },

        "English": {
            "urgency": "Pressure to act urgently",
            "bank_threat": "Threats in the name of a bank",
            "money_transfer": "Request to transfer money",
            "private_data": "Request for confidential information",
            "prize": "Promise of a prize or gift",
            "suspicious_link": "Suspicious link",
            "data_confirmation": "Request to confirm personal data"
        }
    }
}


def tr(key):
    return T[key][lang]


def category_name(category_key):
    return T["categories"][lang][category_key]


# =====================================================
# 4. SESSION STATE
# =====================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# =====================================================
# 5. DESIGN AND CSS
# =====================================================

st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)


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


# =====================================================
# 6. MESSAGE ANALYSIS
# =====================================================

RULES = {

    "urgency": [
        "срочно",
        "немедленно",
        "шұғыл",
        "тез арада",
        "сейчас же",
        "сегодня",
        "последний шанс",
        "дереу",
        "бірден"
    ],

    "bank_threat": [
        "карта заблокирована",
        "картаңыз бұғатталды",
        "банк қауіпсіздік қызметі",
        "счет заблокирован",
        "аккаунт заблокирован",
        "ваш счет будет закрыт",
        "шотыңыз бұғатталады"
    ],

    "money_transfer": [
        "переведите деньги",
        "ақша аударыңыз",
        "оплатите",
        "төлем жасаңыз",
        "перевод на карту",
        "отправьте деньги",
        "ақша жіберіңіз"
    ],

    "private_data": [
        "пароль",
        "құпиясөз",
        "код из sms",
        "смс код",
        "cvv",
        "pin-код",
        "карта деректерін",
        "кодты жіберіңіз",
        "введите данные карты",
        "подтвердите личность",
        "введите пароль"
    ],

    "prize": [
        "вы выиграли",
        "сіз ұттыңыз",
        "получите приз",
        "сыйлық ұтып алдыңыз",
        "бесплатный подарок",
        "вам начислен бонус",
        "вы стали победителем"
    ],

    "suspicious_link": [
        "http://",
        "https://",
        "www.",
        "bit.ly",
        "tinyurl.com",
        "cutt.ly",
        "t.co",
        "is.gd",
        "rb.gy",
        "goo.su"
    ],

    "data_confirmation": [
        "подтвердите данные",
        "растаңыз деректеріңізді",
        "перейдите по ссылке",
        "сілтеме арқылы өтіңіз",
        "обновите данные",
        "деректеріңізді жаңартыңыз"
    ]
}


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
        "private_data": 35,
        "money_transfer": 30,
        "bank_threat": 25,
        "suspicious_link": 25,
        "prize": 20,
        "urgency": 10,
        "data_confirmation": 10
    }

    score = min(
        sum(weights[item] for item in found),
        100
    )

    if score >= 60:
        level = "HIGH"

    elif score >= 30:
        level = "MEDIUM"

    else:
        level = "LOW"

    return score, level, found, links


# =====================================================
# 7. PDF REPORT
# =====================================================

def make_pdf(result, selected_lang):

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

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


    pdf_labels = {

        "Қазақша": {
            "heading": "Интернет алаяқтықты анықтау есебі",
            "score": "Қауіп көрсеткіші",
            "level": "Қауіп деңгейі",
            "indicators": "Анықталған белгілер",
            "none": "Белгілі қауіп белгілері табылған жоқ.",
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
            "none": "Известные признаки риска не обнаружены.",
            "message": "Проверенное сообщение",
            "links": "Найденные ссылки",
            "advice": "Совет по безопасности",
            "advice_text": "Не переходите по подозрительным ссылкам и никому не сообщайте конфиденциальные коды."
        },

        "English": {
            "heading": "Internet Fraud Detection Report",
            "score": "Risk score",
            "level": "Risk level",
            "indicators": "Detected indicators",
            "none": "No known risk indicators were found.",
            "message": "Checked message",
            "links": "Detected links",
            "advice": "Safety advice",
            "advice_text": "Do not open suspicious links or share confidential codes."
        }

    }

    labels = pdf_labels[selected_lang]

    risk_text = T["risk_names"][selected_lang][result["level"]]

    y = page_height - 55


    def write_line(text, font=regular_font, size=10):

        nonlocal y

        pdf.setFont(font, size)

        max_chars = 90

        chunks = []

        text = str(text)

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

            pdf.drawString(
                45,
                y,
                chunk
            )

            y -= size + 9


    write_line(
        "SCAMDETECTOR AI",
        bold_font,
        18
    )

    write_line(
        labels["heading"],
        bold_font,
        13
    )

    y -= 8

    write_line(
        f'{labels["score"]}: {result["score"]}/100'
    )

    write_line(
        f'{labels["level"]}: {risk_text}'
    )

    y -= 8

    write_line(
        labels["indicators"],
        bold_font,
        11
    )

    if result["found"]:

        for category in result["found"]:

            write_line(
                "- " + T["categories"][selected_lang][category]
            )

    else:

        write_line(labels["none"])

    y -= 8

    write_line(
        labels["message"],
        bold_font,
        11
    )

    write_line(result["message"])

    if result["links"]:

        y -= 8

        write_line(
            labels["links"],
            bold_font,
            11
        )

        for link in result["links"]:
            write_line(link)

    y -= 8

    write_line(
        labels["advice"],
        bold_font,
        11
    )

    write_line(labels["advice_text"])

    y -= 12

    write_line(
        "ScamDetector AI",
        regular_font,
        9
    )

    pdf.save()

    buffer.seek(0)

    return buffer.getvalue()


# =====================================================
# 8. MESSAGE INPUT
# =====================================================

message = st.text_area(
    tr("input"),
    placeholder=tr("placeholder"),
    height=180
)


if st.button(
    tr("button"),
    use_container_width=True
):

    if not message.strip():

        st.warning(tr("empty_input"))

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


# =====================================================
# 9. ANALYSIS RESULT
# =====================================================

result = st.session_state.last_result


if result:

    st.divider()

    st.subheader(tr("result"))

    st.metric(
        tr("risk_score"),
        f'{result["score"]}/100'
    )

    if result["level"] == "HIGH":

        st.error(tr("high"))

    elif result["level"] == "MEDIUM":

        st.warning(tr("medium"))

    else:

        st.success(tr("low"))

    st.progress(
        result["score"] / 100
    )

    if result["found"]:

        st.markdown(tr("found_title"))

        for item in result["found"]:

            st.write(
                "🔴",
                category_name(item)
            )

    else:

        st.info(tr("no_signs"))

    if result["links"]:

        st.markdown(tr("links_title"))

        for link in result["links"]:

            st.write(
                "🔗",
                link
            )

    st.markdown(tr("advice_title"))

    if result["score"] >= 30:

        st.warning(
            T["advice_risky"][lang]
        )

    else:

        st.info(
            T["advice_safe"][lang]
        )

    try:

        pdf_data = make_pdf(
            result,
            lang
        )

        st.download_button(

            label=tr("pdf_button"),

            data=pdf_data,

            file_name="ScamDetector_Report.pdf",

            mime="application/pdf",

            use_container_width=True

        )

    except Exception as error:

        st.error(
            f'{tr("pdf_error")} {error}'
        )


# =====================================================
# 10. CHECK HISTORY
# =====================================================

st.divider()

st.subheader(tr("history"))


if st.session_state.history:

    for item in reversed(st.session_state.history):

        st.write(
            tr("message_label"),
            item["message"]
        )

        st.write(
            tr("risk_label"),
            T["risk_names"][lang][item["level"]]
        )

        st.write(
            tr("score_label"),
            f'{item["score"]}/100'
        )

        st.divider()

else:

    st.info(tr("no_history"))


# =====================================================
# 11. FOOTER
# =====================================================

st.caption(tr("footer"))
