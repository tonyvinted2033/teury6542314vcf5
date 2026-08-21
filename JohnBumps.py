from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import os
import requests
import json
from datetime import datetime
import random

# ========== ТВОИ ТОКЕНЫ И ДАННЫЕ ==========
BOT_TOKEN = "8980877062:AAE2jNp8U9FO0c4ilPd8ozqZI4aMsm8C6XU"
GROUP_CHAT_ID = "@govnoverbluda13376767"
CRYPTOBOT_API_TOKEN = "623857:AAMUDzdcQ1OhWPFQrFnK71ae6AhiRztYYNz"
CRYPTOBOT_API_URL = "https://pay.crypt.bot/api/"
ADMIN_IDS = [7015434265, 7947689141]

# ========== РЕКВИЗИТЫ ДЛЯ ОПЛАТЫ ==========
CARD_NUMBER = "4100 1195 9945 9420"
SBP_PHONE = "+7 995 141 82 98"

# ========== ОСТАЛЬНЫЕ ПЕРЕМЕННЫЕ ==========
user_cities = {}
user_selections = {}
user_pending_confirmations = {}
user_balance = {}
user_purchases = {}

# Базы адресов для генерации
streets = {
    "Москва": ["Тверская", "Арбат", "Новый Арбат", "Пушкинская", "Ленинградский проспект", "Кутузовский проспект",
               "Профсоюзная", "Мичуринский проспект", "Варшавское шоссе", "Каширское шоссе"],
    "Санкт-Петербург": ["Невский проспект", "Литейный проспект", "Васильевский остров", "Петроградская сторона",
                        "Выборгская сторона", "Московский проспект", "Лиговский проспект", "Большой проспект",
                        "Садовая", "Гороховая"],
    "Псков": ["Советская", "Ленина", "Октябрьский проспект", "Коммунальная", "Юбилейная", "Некрасова",
              "Плехановский Посад", "Профсоюзная", "Красноармейская"],
    "Петрозаводск": ["Ленина", "Антикайнена", "Андропова", "Энгельса", "Кирова", "Правды", "Дзержинского", "Куйбышева",
                     "Володарского"],
    "Великий Новгород": ["Большая Московская", "Мерецкова-Волосова", "Людогоща", "Стратилатовская",
                         "Б. Санкт-Петербургская", "Федоровский Ручей", "Зелинского", "Чудинцева"],
    "Нижний Новгород": ["Большая Покровская", "Рождественская", "Ильинская", "Варварская", "Минина", "Ульянова",
                        "Горького", "Пискунова", "Алексеевская"],
    "Владивосток": ["Светланская", "Алеутская", "1-я Морская", "Посьетская", "Фонтанная", "Пушкинская", "Семеновская",
                    "Адмирала Фокина"],
    "Красноярск": ["Мира", "Карла Маркса", "Дубровинского", "9 Мая", "60 лет Октября", "Ады Лебедевой",
                   "78 Добровольческой Бригады", "Копылова", "Урицкого"],
    "Екатеринбург": ["Малышева", "8 Марта", "Куйбышева", "Хохрякова", "Репина", "Толмачева", "Шейнкмана",
                     "Луначарского"],
    "Йошкар-Ола": ["Первомайская", "Комсомольская", "Воинов-Интернационалистов", "Строителей", "Машиностроителей",
                   "К. Маркса", "Зарубина", "Я. Эшпая", "Кремлевская"],
    "Казань": ["Баумана", "Татарстан", "Право-Булачная", "Профсоюзная", "Чистопольская", "Четаева", "Достоевского",
               "Айдарова"],
    "Калининград": ["Ленинский проспект", "Театральная", "Горького", "Октябрьская", "Багратиона", "Черняховского",
                    "Озерная", "Пролетарская", "Камская"],
    "Сергиев Посад": ["Красной Армии", "Вознесенская", "Вифанская", "Шлякова", "1-я Ударной Армии", "Карла Маркса",
                      "Валовой", "1-я Рыбная"],
    "Ярославль": ["Кирова", "Свободы", "Республиканская", "Собинова", "Трефолева", "Ушинского", "Некрасова",
                  "Б. Октябрьская", "Чайковского"],
    "Сочи": ["Навагинская", "Кирова", "Виноградная", "Конституции СССР", "Орджоникидзе", "Параллельная", "Приморская",
             "Нагорная"],
    "Коломна": ["Октябрьской Революции", "Ленина", "Озерская", "Зеленая", "Малышева", "Менделеева", "Дзержинского"],
    "Элиста": ["Ленина", "Пушкина", "Хомутникова", "Юрия Клыкова", "Н. Илюмжинова", "Джангара"],
    "Тобольск": ["Ремезова", "Семена Ремезова", "Алябьева", "4-й микрорайон", "Аптекарская", "8 Марта", "7-го Ноября"],
    "Выборг": ["Северный Вал", "Выборгская", "Крепостная", "Ленинградская", "Парковая", "Железнодорожная"],
    "Дербент": ["Таги-Заде", "7 Магал", "Гагарина", "Мамедбекова", "Чапаева", "Ленина", "Буйнакского"],
    "Тамбов": ["Интернациональная", "Советская", "Комсомольская", "Карла Маркса", "Гоголя", "Набережная",
               "Коммунальная"],
    "Новосибирск": ["Ленина", "Советская", "Каменская", "Богдана Хмельницкого", "Фрунзе", "Кирова", "Орджоникидзе",
                    "Сибревкома"],
    "Уфа": ["Ленина", "Центральная", "Революционная", "Цюрупы", "Чернышевского", "Аксакова", "Менделеева", "Пушкина"],
    "Самара": ["Куйбышева", "Ленинградская", "Некрасовская", "Чапаевская", "Фрунзе", "Молодогвардейская", "Садовая",
               "Вилоновская"],
    "Краснодар": ["Красная", "Седина", "Ставропольская", "Красноармейская", "Калинина", "Димитрова", "Гимназическая"],
    "Волгоград": ["Ленина", "Мира", "Комсомольская", "Рабоче-Крестьянская", "Ангарская", "Качинцев", "Землячки",
                  "64-й Армии", "7-я Гвардейская"],
    "Пермь": ["Ленина", "Куйбышева", "Попова", "Сибирская", "Екатерининская", "Лодыгина"],
    "Ростов-на-Дону": ["Большая Садовая", "Темерницкая", "Пушкинская", "Социалистическая", "Горького",
                       "Ворошиловский проспект", "Братский переулок"]
}

locations = [
    " (подъезд {})", " (арка)", " (подвал)", " (кодовый замок)", " (гараж)", " (ниша)",
    " (клумба)", " (этаж {})", " (двор)", " (за углом)", " (у забора)", " (в тупике)",
    " (у трансформаторной будки)", " (за гаражами)", " (у детской площадки)", " (в парке)",
    " (у остановки)", " (за супермаркетом)", " (на стройке)", " (у реки)"
]


def generate_addresses(city, product_key):
    """Генерирует уникальные адреса для каждого продукта в городе"""
    random.seed(f"{city}_{product_key}")

    city_streets = streets.get(city, ["Центральная", "Ленина", "Советская"])
    addresses = []

    for i in range(2):
        street = random.choice(city_streets)
        house = random.randint(1, 150)
        location = random.choice(locations)

        if "{}" in location:
            if "подъезд" in location:
                location = location.format(random.randint(1, 10))
            elif "этаж" in location:
                location = location.format(random.randint(1, 20))

        address = f"{street}, {house}{location}"
        addresses.append(address)

    return addresses


# Функция для получения курса USDT к рублю
def get_usdt_rate():
    """Получает текущий курс USDT/RUB через биржевые API"""
    try:
        response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=USDTRUB', timeout=10)
        if response.status_code == 200:
            data = response.json()
            return float(data['price'])

        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=rub',
                                timeout=10)
        if response.status_code == 200:
            data = response.json()
            return float(data['tether']['rub'])

        return 90.0

    except Exception as e:
        print(f"Ошибка получения курса: {e}")
        return 90.0


# Функция для создания счета через CryptoBot
def create_cryptobot_invoice(amount_usdt, description, user_id):
    """Создает реальный счет через CryptoBot API"""
    try:
        headers = {
            'Crypto-Pay-API-Token': CRYPTOBOT_API_TOKEN,
            'Content-Type': 'application/json'
        }

        amount_usdt = int(round(float(amount_usdt)))

        payload = {
            'asset': 'USDT',
            'amount': str(amount_usdt),
            'description': description,
            'hidden_message': f'Заказ от пользователя {user_id}',
            'paid_btn_name': 'openBot',
            'paid_btn_url': f'https://t.me/{(BOT_TOKEN.split(":")[0])}bot',
            'payload': json.dumps({
                'user_id': user_id,
                'order_description': description,
                'timestamp': datetime.now().isoformat()
            }),
            'allow_comments': False,
            'allow_anonymous': False,
            'expires_in': 3600
        }

        response = requests.post(
            f'{CRYPTOBOT_API_URL}createInvoice',
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                invoice = data['result']
                return {
                    'success': True,
                    'invoice_url': invoice.get('bot_invoice_url'),
                    'pay_url': invoice.get('pay_url'),
                    'invoice_id': invoice.get('invoice_id'),
                    'amount': invoice.get('amount'),
                    'asset': invoice.get('asset')
                }
            else:
                error_msg = data.get('error', {}).get('name', 'Unknown error')
                return {
                    'success': False,
                    'error': error_msg
                }
        else:
            error_msg = f'HTTP {response.status_code}: {response.text}'
            return {
                'success': False,
                'error': error_msg
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


async def forward_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE, message_type="user_message"):
    """Пересылает сообщение в группу"""
    try:
        user = update.effective_user
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        if message_type == "user_message":
            await context.bot.forward_message(
                chat_id=GROUP_CHAT_ID,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"{user_info}\n💬 Отправил сообщение"
            )

    except Exception as e:
        print(f"Ошибка при пересылке в группу: {e}")


async def send_qr_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /sendqr - отправка QR-кода из файла пользователю (только для админов)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав для этой команды.")
        return

    try:
        args = context.args
        target_id = int(args[0])
        
        QR_FILE = "sbp_qr.jpg"
        
        try:
            with open(QR_FILE, 'rb') as qr_photo:
                await context.bot.send_photo(
                    chat_id=target_id,
                    photo=InputFile(qr_photo),
                    caption="✅ Ваш QR-код для оплаты готов."
                )
            await update.message.reply_text(f"✅ QR-код отправлен пользователю {target_id}")
        except FileNotFoundError:
            await update.message.reply_text(f"❌ Файл {QR_FILE} не найден. Положите его в папку с ботом.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open('welcome.jpg', 'rb') as photo:
            message = await update.message.reply_photo(
                photo=InputFile(photo),
                caption="""Добро пожаловать!

🤠 Здесь ты можешь купить что угодно

📦 Быстрая доставка , хорошие курьеры
💳 Удобная оплата(CryptoBot USDT, СБП, Карта)
🛡️ Гарантия качества.
✅ Мы гарантируем своим клиентам:
® Хорошее качество товара
👻 Полное отсутствие ненаходов
💬 Открытие диспута в случае ненахода в любое время
📍 Удобное место клада

Также у нас есть Тех.Поддержка 24/7 , где вы можете задать любой вопрос!

Откройте список команд командой /help"""
            )

        user = update.effective_user
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        with open('welcome.jpg', 'rb') as photo_for_group:
            await context.bot.send_photo(
                chat_id=GROUP_CHAT_ID,
                photo=InputFile(photo_for_group),
                caption=f"{user_info}\n🚀 Запустил бота\n\n{message.caption}"
            )

        await show_city_selection(update.message)

    except FileNotFoundError:
        message = await update.message.reply_text("Фото не найдено!")

        user = update.effective_user
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n🚀 Запустил бота (фото не найдено)\n\n{message.text}"
        )

        await show_city_selection(update.message)


async def city_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /city - выбор города"""
    user = update.effective_user
    user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
    if user.username:
        user_info += f" @{user.username}"

    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=f"{user_info}\n📍 Запросил выбор города командой /city"
    )

    await show_city_selection(update.message)


async def show_city_selection(message):
    """Показывает выбор города"""
    keyboard = [
        [InlineKeyboardButton("Москва", callback_data="city_moscow")],
        [InlineKeyboardButton("Санкт-Петербург", callback_data="city_spb")],
        [InlineKeyboardButton("Псков", callback_data="city_pskov")],
        [InlineKeyboardButton("Петрозаводск", callback_data="city_petrozavodsk")],
        [InlineKeyboardButton("Великий Новгород", callback_data="city_novgorod")],
        [InlineKeyboardButton("Нижний Новгород", callback_data="city_nizhny_novgorod")],
        [InlineKeyboardButton("Владивосток", callback_data="city_vladivostok")],
        [InlineKeyboardButton("Красноярск", callback_data="city_krasnoyarsk")],
        [InlineKeyboardButton("Екатеринбург", callback_data="city_ekaterinburg")],
        [InlineKeyboardButton("Йошкар-Ола", callback_data="city_yoshkar_ola")],
        [InlineKeyboardButton("Казань", callback_data="city_kazan")],
        [InlineKeyboardButton("Калининград", callback_data="city_kaliningrad")],
        [InlineKeyboardButton("Сергиев Посад", callback_data="city_sergiyev_posad")],
        [InlineKeyboardButton("Ярославль", callback_data="city_yaroslavl")],
        [InlineKeyboardButton("Сочи", callback_data="city_sochi")],
        [InlineKeyboardButton("Коломна", callback_data="city_kolomna")],
        [InlineKeyboardButton("Элиста", callback_data="city_elista")],
        [InlineKeyboardButton("Тобольск", callback_data="city_tobolsk")],
        [InlineKeyboardButton("Выборг", callback_data="city_vyborg")],
        [InlineKeyboardButton("Дербент", callback_data="city_derbent")],
        [InlineKeyboardButton("Тамбов", callback_data="city_tambov")],
        [InlineKeyboardButton("Новосибирск", callback_data="city_novosibirsk")],
        [InlineKeyboardButton("Уфа", callback_data="city_ufa")],
        [InlineKeyboardButton("Самара", callback_data="city_samara")],
        [InlineKeyboardButton("Краснодар", callback_data="city_krasnodar")],
        [InlineKeyboardButton("Волгоград", callback_data="city_volgograd")],
        [InlineKeyboardButton("Пермь", callback_data="city_perm")],
        [InlineKeyboardButton("Ростов-на-Дону", callback_data="city_rostov")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(
        "📍 Пожалуйста, выберите ваш город:",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help - список команд"""
    try:
        with open('help.jpg', 'rb') as photo:
            message = await update.message.reply_photo(
                photo=InputFile(photo),
                caption="""📋 Список команд:

/support - Обратиться в техподдержку
/buy - Посмотреть ассортимент магазина
/city - Выбрать город
/profile - Ваш профиль

💡 Выберите нужную команду из меню!"""
            )

        user = update.effective_user
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        with open('help.jpg', 'rb') as photo_for_group:
            await context.bot.send_photo(
                chat_id=GROUP_CHAT_ID,
                photo=InputFile(photo_for_group),
                caption=f"{user_info}\n❓ Запросил помощь\n\n{message.caption}"
            )

    except FileNotFoundError:
        message = await update.message.reply_text("Фото help.jpg не найдено!")

        user = update.effective_user
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n❓ Запросил помощь (фото не найдено)\n\n{message.text}"
        )


async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /support - техподдержка"""
    try:
        with open('support.jpg', 'rb') as photo:
            message = await update.message.reply_photo(
                photo=InputFile(photo),
                caption="""🛠️ Техническая поддержка

Обратиться к нашей Тех.Поддержке, которая работает 24/7 можно, написав:
👉 @John_TexSupport

📞 Мы всегда на связи и готовы помочь!"""
            )

        user = update.effective_user
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        with open('support.jpg', 'rb') as photo_for_group:
            await context.bot.send_photo(
                chat_id=GROUP_CHAT_ID,
                photo=InputFile(photo_for_group),
                caption=f"{user_info}\n🛠️ Запросил техподдержку\n\n{message.caption}"
            )

    except FileNotFoundError:
        message = await update.message.reply_text("Фото support.jpg не найдено!")

        user = update.effective_user
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n🛠️ Запросил техподдержку (фото не найдено)\n\n{message.text}"
        )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /profile - показать профиль пользователя"""
    user_id = update.effective_user.id
    user = update.effective_user
    
    balance = user_balance.get(user_id, 0)
    purchases = user_purchases.get(user_id, 0)
    city = user_cities.get(user_id, "Не выбран")
    
    text = f"""👤 **Ваш профиль**

**Имя:** {user.first_name}
**ID:** `{user_id}`
**Город:** {city}
**Баланс:** {balance} ₽
**Покупок:** {purchases}

💳 Для пополнения баланса используйте кнопку «💰 Пополнить баланс» в меню `/buy`"""
    
    await update.message.reply_text(text, parse_mode="Markdown")


async def profile_callback(message, user_id):
    """Показывает профиль (для кнопки)"""
    user = await message.get_chat()
    balance = user_balance.get(user_id, 0)
    purchases = user_purchases.get(user_id, 0)
    city = user_cities.get(user_id, "Не выбран")
    
    text = f"""👤 **Ваш профиль**

**Имя:** {user.first_name}
**ID:** `{user_id}`
**Город:** {city}
**Баланс:** {balance} ₽
**Покупок:** {purchases}

💳 Для пополнения баланса используйте кнопку «💰 Пополнить баланс» в меню `/buy`"""
    
    await message.reply_text(text, parse_mode="Markdown")


async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /buy - ассортимент магазина с кнопками по категориям"""
    user_id = update.effective_user.id

    if user_id not in user_cities:
        await update.message.reply_text("❌ Пожалуйста, сначала выберите город с помощью команды /start или /city")
        return

    selected_city = user_cities[user_id]

    keyboard = [
        [InlineKeyboardButton("💊 Дизайнерские", callback_data="category_designer")],
        [InlineKeyboardButton("🌈 Эйфоретики", callback_data="category_euphoriants")],
        [InlineKeyboardButton("🌿 Каннабис", callback_data="category_cannabis")],
        [InlineKeyboardButton("💊 Аптечные препараты", callback_data="category_apteka")],
        [InlineKeyboardButton("💰 Пополнить баланс", callback_data="balance")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton("🛒 Оформить заказ", callback_data="order_info")],
        [InlineKeyboardButton("📞 Техподдержка", callback_data="support_contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"""🛒 Категории товаров:

🏙️ Ваш город: {selected_city}

📦 Доступные категории:
• 💊 Дизайнерские - Мефедрон, Альфа-ПвП, Амфетамин PING AMG OMG!
• 🌈 Эйфоретики - MDMA (кристалл), ЭКСТАЗИ EXCLUSIVE RC
• 🌿 Каннабис - Gorilla Glue, AK-47, High Grade MIX, Гашиш ICE-O-LATOR
• 💊 Аптечные препараты - Трамадол, Золомакс, Прегабалин, Габапентин, Баклофен, Тропикамид, Феназепам, Кодеиновый сироп TOSIENA

Выберите категорию для просмотра товаров 🎯""",
        reply_markup=reply_markup
    )


async def show_category_products(message, category, user_id, selected_city):
    """Показывает товары выбранной категории"""
    if category == "designer":
        keyboard = [
            [InlineKeyboardButton("💊 Мефедрон(Мука)", callback_data="product_mefedron_flour")],
            [InlineKeyboardButton("✨ Мефедрон(Кристаллы)", callback_data="product_mefedron_crystals")],
            [InlineKeyboardButton("⚡ Альфа-ПвП(Мука)", callback_data="product_alpha_pvp_flour")],
            [InlineKeyboardButton("❄️ Альфа-ПвП(Кристаллы)", callback_data="product_alpha_pvp_crystals")],
            [InlineKeyboardButton("🔥 Амфетамин PING AMG OMG!", callback_data="product_amphetamine")],
            [InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_categories")]
        ]
        category_name = "Дизайнерские"
        category_desc = "💊 Дизайнерские стимуляторы высшего качества"

    elif category == "euphoriants":
        keyboard = [
            [InlineKeyboardButton("💎 MDMA (кристалл)", callback_data="product_mdma_crystal")],
            [InlineKeyboardButton("💊 ЭКСТАЗИ EXCLUSIVE RC", callback_data="product_ecstasy")],
            [InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_categories")]
        ]
        category_name = "Эйфоретики"
        category_desc = "🌈 Эйфоретики для особого настроения"

    elif category == "cannabis":
        keyboard = [
            [InlineKeyboardButton("🧬 Gorilla Glue", callback_data="product_gorilla_glue")],
            [InlineKeyboardButton("🔫 AK-47", callback_data="product_ak47")],
            [InlineKeyboardButton("⭐ High Grade MIX / ТГК ~ 27%", callback_data="product_high_grade_mix")],
            [InlineKeyboardButton("🍫 Гашиш ICE-O-LATOR", callback_data="product_hashish")],
            [InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_categories")]
        ]
        category_name = "Каннабис"
        category_desc = "🌿 Натуральный каннабис премиум качества"

    elif category == "apteka":
        keyboard = [
            [InlineKeyboardButton("💊 Трамадол 50мг", callback_data="product_tramadol")],
            [InlineKeyboardButton("💊 Золомакс 100мг", callback_data="product_zolomax")],
            [InlineKeyboardButton("💊 Прегабалин 300мг", callback_data="product_pregabalin")],
            [InlineKeyboardButton("💊 Габапентин 300мг", callback_data="product_gabapentin")],
            [InlineKeyboardButton("💊 Баклофен 10мг", callback_data="product_baclofen")],
            [InlineKeyboardButton("💊 Тропикамид 1%", callback_data="product_tropicamide")],
            [InlineKeyboardButton("💊 Феназепам 1мг", callback_data="product_phenazepam")],
            [InlineKeyboardButton("🧪 Кодеиновый сироп TOSIENA", callback_data="product_codeine_syrup")],
            [InlineKeyboardButton("🔙 Назад к категориям", callback_data="back_to_categories")]
        ]
        category_name = "Аптечные препараты"
        category_desc = "💊 Препараты для релаксации и сна"

    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(
        f"""🛒 {category_name}

🏙️ Ваш город: {selected_city}

{category_desc}

Выберите товар:""",
        reply_markup=reply_markup
    )


async def balance_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню пополнения баланса"""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("💳 Банковская карта", callback_data="pay_card")],
        [InlineKeyboardButton("📱 СБП перевод", callback_data="pay_sbp")],
        [InlineKeyboardButton("📲 СБП QR-код", callback_data="pay_qr")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.edit_text(
        "💰 Выберите способ пополнения:",
        reply_markup=reply_markup
    )


async def add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /addbalance - добавить баланс пользователю (только для админов)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав для этой команды.")
        return

    try:
        args = context.args
        target_id = int(args[0])
        amount = int(args[1])
        
        user_balance[target_id] = user_balance.get(target_id, 0) + amount
        
        await update.message.reply_text(f"✅ Баланс пользователя {target_id} увеличен на {amount} ₽. Текущий баланс: {user_balance[target_id]} ₽")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}. Использование: /addbalance ID СУММА")


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена заказа (очищает данные пользователя)"""
    user_id = update.effective_user.id
    
    if user_id in user_selections:
        del user_selections[user_id]
    if user_id in user_pending_confirmations:
        del user_pending_confirmations[user_id]
    
    await update.message.reply_text("❌ Заказ отменён. Все данные очищены.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = query.from_user
    selected_city = user_cities.get(user_id, "Город не выбран")

    if query.data.startswith('city_'):
        city_mapping = {
            'city_moscow': 'Москва', 'city_spb': 'Санкт-Петербург', 'city_pskov': 'Псков',
            'city_petrozavodsk': 'Петрозаводск', 'city_novgorod': 'Великий Новгород',
            'city_nizhny_novgorod': 'Нижний Новгород', 'city_vladivostok': 'Владивосток',
            'city_krasnoyarsk': 'Красноярск', 'city_ekaterinburg': 'Екатеринбург',
            'city_yoshkar_ola': 'Йошкар-Ола', 'city_kazan': 'Казань', 'city_kaliningrad': 'Калининград',
            'city_sergiyev_posad': 'Сергиев Посад', 'city_yaroslavl': 'Ярославль', 'city_sochi': 'Сочи',
            'city_kolomna': 'Коломна', 'city_elista': 'Элиста', 'city_tobolsk': 'Тобольск',
            'city_vyborg': 'Выборг', 'city_derbent': 'Дербент', 'city_tambov': 'Тамбов',
            'city_novosibirsk': 'Новосибирск', 'city_ufa': 'Уфа', 'city_samara': 'Самара',
            'city_krasnodar': 'Краснодар', 'city_volgograd': 'Волгоград', 'city_perm': 'Пермь',
            'city_rostov': 'Ростов-на-Дону',
        }

        selected_city = city_mapping.get(query.data, 'Неизвестный город')
        user_cities[user_id] = selected_city

        await query.message.reply_text(
            f"✅ Город выбран: {selected_city}\n\n"
            f"Теперь вы можете посмотреть ассортимент товаров с помощью команды /buy"
        )

        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n📍 Выбрал город: {selected_city}"
        )
        return

    if user_id not in user_cities and not query.data in ['order_info', 'support_contact', 'back_to_categories', 'profile']:
        await query.message.reply_text("❌ Пожалуйста, сначала выберите город с помощью команды /start или /city")
        return

    # Обработка категорий
    if query.data == "category_designer":
        await show_category_products(query.message, "designer", user_id, selected_city)
        return
    elif query.data == "category_euphoriants":
        await show_category_products(query.message, "euphoriants", user_id, selected_city)
        return
    elif query.data == "category_cannabis":
        await show_category_products(query.message, "cannabis", user_id, selected_city)
        return
    elif query.data == "category_apteka":
        await show_category_products(query.message, "apteka", user_id, selected_city)
        return
    elif query.data == "balance":
        await balance_menu(update, context)
        return
    elif query.data == "profile":
        await profile_callback(query.message, user_id)
        return
    elif query.data == "back_to_categories":
        await buy_callback(query.message, user_id)
        return

    # Обработка оплаты
    elif query.data == "pay_card":
        await query.message.edit_text(
            f"💳 Пополнение по карте:\n\n"
            f"Номер карты: {CARD_NUMBER}\n"
            f"Банк: ЮMoney\n"
            f"Получатель: Анна Мухометова.\n\n"
            f"После перевода отправьте чек в бота."
        )
        return

    elif query.data == "pay_sbp":
        await query.message.edit_text(
            f"📱 Пополнение по СБП:\n\n"
            f"Номер телефона: {SBP_PHONE}\n"
            f"Банк: ЮMoney\n"
            f"Получатель: Анна М.\n\n"
            f"После перевода отправьте чек в бота."
        )
        return

    elif query.data == "pay_qr":
        await query.message.edit_text(
            "📲 Вы выбрали оплату по QR-коду.\n\n"
            "Я сгенерирую QR-код в ближайшее время и отправлю его вам в этот чат.\n"
            "Пожалуйста, ожидайте."
        )
        return

    elif query.data == "cancel_order":
        if user_id in user_selections:
            del user_selections[user_id]
        if user_id in user_pending_confirmations:
            del user_pending_confirmations[user_id]
        await query.message.edit_text("❌ Заказ отменён. Все данные очищены.")
        return

    # Обработка товаров
    product_info = {
        "product_mefedron_flour": {"name": "Мефедрон (Мука)", "price": "1700₽/гр.", "file": "meph.jpg", "photo2": "meph1.jpg", "unit": "гр", "min_order": 1},
        "product_mefedron_crystals": {"name": "Мефедрон (Кристаллы)", "price": "1800₽/гр.", "file": "meph.jpg", "photo2": "meph1.jpg", "unit": "гр", "min_order": 1},
        "product_alpha_pvp_flour": {"name": "Альфа-ПвП (Мука)", "price": "1700₽/гр.", "file": "alpha.jpg", "photo2": "alpha1.jpg", "unit": "гр", "min_order": 1},
        "product_alpha_pvp_crystals": {"name": "Альфа-ПвП (Кристаллы)", "price": "1800₽/гр.", "file": "alpha.jpg", "photo2": "alpha1.jpg", "unit": "гр", "min_order": 1},
        "product_amphetamine": {"name": "Амфетамин PING AMG OMG!", "price": "1400₽/гр.", "file": "amphetamine.jpg", "photo2": "amphetamine1.jpg", "unit": "гр", "min_order": 1},
        "product_mdma_crystal": {"name": "MDMA (кристалл)", "price": "2000₽/гр.", "file": "mdma_crystal.jpg", "photo2": "mdma_crystal1.jpg", "unit": "гр", "min_order": 1},
        "product_ecstasy": {"name": "ЭКСТАЗИ EXCLUSIVE RC", "price": "1200₽/шт.", "file": "ecstasy.jpg", "photo2": "ecstasy1.jpg", "unit": "шт", "min_order": 2},
        "product_hashish": {"name": "Гашиш ICE-O-LATOR", "price": "1800₽/гр.", "file": "hashish.jpg", "photo2": "hashish1.jpg", "unit": "гр", "min_order": 1},
        "product_gorilla_glue": {"name": "Gorilla Glue", "price": "1800₽/гр.", "file": "gorilla_glue.jpg", "photo2": "gorilla_glue1.jpg", "unit": "гр", "min_order": 1},
        "product_ak47": {"name": "AK-47", "price": "1700₽/гр.", "file": "ak47.jpg", "photo2": "ak471.jpg", "unit": "гр", "min_order": 1},
        "product_high_grade_mix": {"name": "High Grade MIX / ТГК ~ 27%", "price": "2000₽/гр.", "file": "high_grade_mix.jpg", "photo2": "high_grade_mix1.jpg", "unit": "гр", "min_order": 1},
        "product_tramadol": {"name": "Трамадол 50мг", "price": "800₽/шт.", "file": "tramadol.jpg", "photo2": "tramadol1.jpg", "unit": "шт", "min_order": 2},
        "product_zolomax": {"name": "Золомакс 100мг", "price": "1200₽/шт.", "file": "zolomax.jpg", "photo2": "zolomax1.jpg", "unit": "шт", "min_order": 2},
        "product_pregabalin": {"name": "Прегабалин 300мг", "price": "1100₽/шт.", "file": "pregabalin.jpg", "photo2": "pregabalin1.jpg", "unit": "шт", "min_order": 2},
        "product_gabapentin": {"name": "Габапентин 300мг", "price": "900₽/шт.", "file": "gabapentin.jpg", "photo2": "gabapentin1.jpg", "unit": "шт", "min_order": 2},
        "product_baclofen": {"name": "Баклофен 10мг", "price": "750₽/шт.", "file": "baclofen.jpg", "photo2": "baclofen1.jpg", "unit": "шт", "min_order": 2},
        "product_tropicamide": {"name": "Тропикамид 1%", "price": "600₽/шт.", "file": "tropicamide.jpg", "photo2": "tropicamide1.jpg", "unit": "шт", "min_order": 2},
        "product_phenazepam": {"name": "Феназепам 1мг", "price": "900₽/шт.", "file": "phenazepam.jpg", "photo2": "phenazepam1.jpg", "unit": "шт", "min_order": 2},
        "product_codeine_syrup": {"name": "Кодеиновый сироп TOSIENA", "price": "1500₽/фл.", "file": "codeine_syrup.jpg", "photo2": "codeine_syrup1.jpg", "unit": "фл", "min_order": 1},
    }

    if query.data in product_info:
        product = product_info[query.data]

        user_selections[user_id] = {
            "product": product["name"],
            "product_key": query.data,
            "city": selected_city,
            "unit": product["unit"]
        }

        addresses = generate_addresses(selected_city, query.data)
        keyboard = []
        for i, address in enumerate(addresses):
            button_text = address[:20] + "..." if len(address) > 20 else address
            keyboard.append([InlineKeyboardButton(f"🛒 Купить на {button_text}", callback_data=f"select_address_{i}")])

        keyboard.append([InlineKeyboardButton("🔙 Назад к товарам", callback_data="back_to_products")])
        reply_markup = InlineKeyboardMarkup(keyboard)

        formatted_addresses = "📍 Доступные адреса:\n" + "\n".join([f"• {addr}" for addr in addresses])

        # Отправляем ПЕРВОЕ фото (описание товара), если есть
        try:
            with open(product["file"], 'rb') as photo:
                await query.message.reply_photo(photo=InputFile(photo))
        except FileNotFoundError:
            pass

        # Отправляем ВТОРОЕ фото (сам товар), если есть
        try:
            with open(product["photo2"], 'rb') as photo:
                await query.message.reply_photo(photo=InputFile(photo))
        except FileNotFoundError:
            pass

        # Отправляем основное сообщение с товаром
        await query.message.reply_text(
            f"""💊 {product["name"]}

🏙️ Город: {selected_city}

{formatted_addresses}

Описание: Высококачественный товар
Цена: {product["price"]}
Минимальный заказ: {product["min_order"]}{product["unit"]}
📏 Максимальный заказ: 20{product["unit"]}

🎯 Выберите адрес для покупки:""",
            reply_markup=reply_markup
        )

        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n💊 Смотрит {product['name']} (город: {selected_city})"
        )
        return

    elif query.data.startswith('select_address_'):
        address_index = int(query.data.split('_')[2])

        if user_id in user_selections:
            product_key = user_selections[user_id]["product_key"]
            addresses_list = generate_addresses(selected_city, product_key)
            selected_address = addresses_list[address_index] if address_index < len(
                addresses_list) else "Адрес не найден"
            user_selections[user_id]["address"] = selected_address
            user_selections[user_id]["address_index"] = address_index

        product = user_selections[user_id]
        unit = product["unit"]

        await query.message.reply_text(
            f"💊 Товар: {product['product']}\n"
            f"📍 Адрес: {selected_address}\n\n"
            f"📦 Укажите количество ({unit}):\n"
            f"(от {product.get('min_order', 1)} до 20 {unit})"
        )
        return

    elif query.data == "back_to_products":
        await show_category_products(query.message, "designer", user_id, selected_city)
        return

    elif query.data == "order_info":
        example_addresses = generate_addresses(selected_city, "product_mefedron_flour")
        formatted_addresses = "📍 Пример адресов:\n" + "\n".join([f"• {addr}" for addr in example_addresses])

        await query.message.reply_text(
            f"""🛒 Как оформить заказ:

🏙️ Ваш город: {selected_city}

{formatted_addresses}

1. Выберите товар из списка
2. Выберите удобный адрес из доступных
3. Укажите необходимое количество
4. Выберите способ оплаты
5. Оплатите заказ
6. Получите координаты и фотографию

💳 Способы оплаты:
• CryptoBot USDT
• СБП (Система быстрых платежей)
• Банковская карта (по реквизитам)
• 💰 С баланса аккаунта

📦 Доставка: 10-15 мин"""
        )

        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n🛒 Смотрит информацию о заказе (город: {selected_city})"
        )
        return

    elif query.data == "support_contact":
        await query.message.reply_text(
            """📞 Техническая поддержка

Обратиться к нашей Тех.Поддержке, которая работает 24/7 можно, написав:
👉 @John_TexSupport

Мы всегда на связи и готовы помочь! 🛠️"""
        )

        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n📞 Смотрит контакты поддержки"
        )
        return

    elif query.data == "payment_cryptobot":
        if user_id in user_pending_confirmations:
            order_data = user_pending_confirmations[user_id]
            usdt_rate = get_usdt_rate()
            amount_usdt = round(order_data["total_price"] / usdt_rate, 2)
            invoice_description = f"{order_data['product']} - {order_data['quantity']}{order_data['unit']}"
            invoice_result = create_cryptobot_invoice(amount_usdt, invoice_description, user_id)

            if invoice_result.get('success'):
                payment_url = invoice_result.get('pay_url') or invoice_result.get('invoice_url')
                if payment_url:
                    await query.message.reply_text(
                        f"""💳 Оплата заказа - CryptoBot USDT

💊 Товар: {order_data['product']}
📦 Количество: {order_data['quantity']} {order_data['unit']}
🏙️ Город: {order_data['city']}
📍 Адрес: {order_data['address']}

💰 Сумма к оплате: {int(amount_usdt)} USDT
💵 (Примерно {order_data['total_price']}₽ по курсу {int(usdt_rate)}₽/USDT)

Для оплаты перейдите по ссылке:
{payment_url}

⏱️ Счет действителен 1 час
🚚 Доставка: 10-15 минут после оплаты

📞 По всем вопросам: @John_TexSupport"""
                    )

                    user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
                    if user.username:
                        user_info += f" @{user.username}"

                    await context.bot.send_message(
                        chat_id=GROUP_CHAT_ID,
                        text=f"{user_info}\n💳 Создан счет CryptoBot: {order_data['product']} - {order_data['quantity']}{order_data['unit']} - {int(amount_usdt)} USDT ({order_data['total_price']}₽)"
                    )

                    if user_id in user_pending_confirmations:
                        del user_pending_confirmations[user_id]
                    if user_id in user_selections:
                        del user_selections[user_id]
                else:
                    await query.message.reply_text("❌ Ошибка: не удалось получить ссылку для оплаты. Попробуйте позже или обратитесь в поддержку.")
            else:
                error_msg = invoice_result.get('error', 'Неизвестная ошибка')
                await query.message.reply_text(f"❌ Ошибка при создании счета: {error_msg}")
        return

    elif query.data == "payment_sbp":
        if user_id in user_pending_confirmations:
            order_data = user_pending_confirmations[user_id]
            random_addition = random.randint(1, 5)
            final_price = order_data["total_price"] + random_addition

            await query.message.reply_text(
                f"""💳 Оплата заказа - СБП

💊 Товар: {order_data['product']}
📦 Количество: {order_data['quantity']} {order_data['unit']}
📍 Адрес: {order_data['address']}

💰 Сумма к оплате: {final_price}₽

📱 Реквизиты СБП:
+79951418298
ЮMoney
Получатель: Анна М.

⚠️ Внимание: оплачивайте ТОЧНУЮ сумму {final_price}₽
🚚 Доставка: 10-15 минут после подтверждения оплаты"""
            )

            user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
            if user.username:
                user_info += f" @{user.username}"

            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"{user_info}\n💳 Выбрал оплату СБП: {order_data['product']} - {order_data['quantity']}{order_data['unit']} - {final_price}₽"
            )

            if user_id in user_pending_confirmations:
                del user_pending_confirmations[user_id]
            if user_id in user_selections:
                del user_selections[user_id]
        return

    elif query.data == "payment_card":
        if user_id in user_pending_confirmations:
            order_data = user_pending_confirmations[user_id]
            random_addition = random.randint(1, 5)
            final_price = order_data["total_price"] + random_addition

            await query.message.reply_text(
                f"""💳 Оплата заказа - Банковская карта

💊 Товар: {order_data['product']}
📦 Количество: {order_data['quantity']} {order_data['unit']}
📍 Адрес: {order_data['address']}

💰 Сумма к оплате: {final_price}₽

🏦 Реквизиты карты:
4100 1195 9945 9420
ЮMoney
Получатель: Анна М.

⚠️ Внимание: оплачивайте ТОЧНУЮ сумму {final_price}₽
🚚 Доставка: 10-15 минут после подтверждения оплаты"""
            )

            user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
            if user.username:
                user_info += f" @{user.username}"

            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"{user_info}\n💳 Выбрал оплату картой: {order_data['product']} - {order_data['quantity']}{order_data['unit']} - {final_price}₽"
            )

            if user_id in user_pending_confirmations:
                del user_pending_confirmations[user_id]
            if user_id in user_selections:
                del user_selections[user_id]
        return

    elif query.data == "payment_balance":
        if user_id in user_pending_confirmations:
            order_data = user_pending_confirmations[user_id]
            
            if user_balance.get(user_id, 0) >= order_data["total_price"]:
                user_balance[user_id] = user_balance.get(user_id, 0) - order_data["total_price"]
                user_purchases[user_id] = user_purchases.get(user_id, 0) + 1
                
                await query.message.reply_text(
                    f"✅ Заказ оплачен с баланса!\n\n"
                    f"💊 Товар: {order_data['product']}\n"
                    f"📦 Количество: {order_data['quantity']} {order_data['unit']}\n"
                    f"📍 Адрес: {order_data['address']}\n"
                    f"💰 Списано: {order_data['total_price']} ₽\n"
                    f"💳 Остаток на балансе: {user_balance.get(user_id, 0)} ₽\n\n"
                    f"🚚 Доставка: 10-15 минут"
                )
                
                user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
                if user.username:
                    user_info += f" @{user.username}"
                
                await context.bot.send_message(
                    chat_id=GROUP_CHAT_ID,
                    text=f"{user_info}\n💳 Оплатил с баланса: {order_data['product']} - {order_data['quantity']}{order_data['unit']} - {order_data['total_price']}₽"
                )
                
                if user_id in user_pending_confirmations:
                    del user_pending_confirmations[user_id]
                if user_id in user_selections:
                    del user_selections[user_id]
            else:
                await query.message.reply_text(
                    f"❌ Недостаточно средств на балансе!\n"
                    f"💳 Ваш баланс: {user_balance.get(user_id, 0)} ₽\n"
                    f"💰 Нужно: {order_data['total_price']} ₽\n\n"
                    f"Пополните баланс через кнопку «💰 Пополнить баланс»"
                )
        return

    elif query.data == "choose_payment":
        if user_id in user_pending_confirmations:
            order_data = user_pending_confirmations[user_id]
            
            keyboard = [
                [InlineKeyboardButton("💎 CryptoBot USDT", callback_data="payment_cryptobot")],
                [InlineKeyboardButton("📱 СБП", callback_data="payment_sbp")],
                [InlineKeyboardButton("💳 Карта", callback_data="payment_card")],
                [InlineKeyboardButton("💰 С баланса", callback_data="payment_balance")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_categories")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(
                f"""💳 Выберите способ оплаты:

💊 Товар: {order_data['product']}
📦 Количество: {order_data['quantity']} {order_data['unit']}
💰 Сумма: {order_data['total_price']} ₽
📍 Адрес: {order_data['address']}

💳 Ваш баланс: {user_balance.get(user_id, 0)} ₽""",
                reply_markup=reply_markup
            )
        return


async def handle_quantity_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод количества товара"""
    user_id = update.effective_user.id
    user = update.effective_user

    if user_id not in user_selections:
        await update.message.reply_text("❌ Сначала выберите товар и адрес через меню /buy")
        return

    try:
        quantity_text = update.message.text.replace(',', '.')
        quantity = float(quantity_text)

        if quantity <= 0:
            await update.message.reply_text("❌ Количество должно быть больше 0")
            return

        unit = user_selections[user_id]["unit"]
        max_limit = 20
        
        product_key = user_selections[user_id]["product_key"]
        product_info_full = {
            "product_mefedron_flour": {"min_order": 1},
            "product_mefedron_crystals": {"min_order": 1},
            "product_alpha_pvp_flour": {"min_order": 1},
            "product_alpha_pvp_crystals": {"min_order": 1},
            "product_amphetamine": {"min_order": 1},
            "product_mdma_crystal": {"min_order": 1},
            "product_ecstasy": {"min_order": 2},
            "product_hashish": {"min_order": 1},
            "product_gorilla_glue": {"min_order": 1},
            "product_ak47": {"min_order": 1},
            "product_high_grade_mix": {"min_order": 1},
            "product_tramadol": {"min_order": 2},
            "product_zolomax": {"min_order": 2},
            "product_pregabalin": {"min_order": 2},
            "product_gabapentin": {"min_order": 2},
            "product_baclofen": {"min_order": 2},
            "product_tropicamide": {"min_order": 2},
            "product_phenazepam": {"min_order": 2},
            "product_codeine_syrup": {"min_order": 1},
        }
        
        min_order = product_info_full.get(product_key, {}).get("min_order", 1)

        if quantity < min_order:
            await update.message.reply_text(f"❌ Минимальный заказ: {min_order}{unit}")
            return

        if quantity > max_limit:
            await update.message.reply_text(f"❌ Превышен лимит заказа! Максимально можно заказать {max_limit}{unit}")
            return

        quantity = round(quantity, 2)
        selection = user_selections[user_id]
        product_key = selection["product_key"]
        product = {
            "product_mefedron_flour": {"name": "Мефедрон (Мука)", "price": 1700},
            "product_mefedron_crystals": {"name": "Мефедрон (Кристаллы)", "price": 1800},
            "product_alpha_pvp_flour": {"name": "Альфа-ПвП (Мука)", "price": 1700},
            "product_alpha_pvp_crystals": {"name": "Альфа-ПвП (Кристаллы)", "price": 1800},
            "product_amphetamine": {"name": "Амфетамин PING AMG OMG!", "price": 1400},
            "product_mdma_crystal": {"name": "MDMA (кристалл)", "price": 2000},
            "product_ecstasy": {"name": "ЭКСТАЗИ EXCLUSIVE RC", "price": 1200},
            "product_hashish": {"name": "Гашиш ICE-O-LATOR", "price": 1800},
            "product_gorilla_glue": {"name": "Gorilla Glue", "price": 1800},
            "product_ak47": {"name": "AK-47", "price": 1700},
            "product_high_grade_mix": {"name": "High Grade MIX / ТГК ~ 27%", "price": 2000},
            "product_tramadol": {"name": "Трамадол 50мг", "price": 800},
            "product_zolomax": {"name": "Золомакс 100мг", "price": 1200},
            "product_pregabalin": {"name": "Прегабалин 300мг", "price": 1100},
            "product_gabapentin": {"name": "Габапентин 300мг", "price": 900},
            "product_baclofen": {"name": "Баклофен 10мг", "price": 750},
            "product_tropicamide": {"name": "Тропикамид 1%", "price": 600},
            "product_phenazepam": {"name": "Феназепам 1мг", "price": 900},
            "product_codeine_syrup": {"name": "Кодеиновый сироп TOSIENA", "price": 1500},
        }.get(product_key, {"name": "Товар", "price": 0})

        total_price = product["price"] * quantity
        unit = selection["unit"]

        user_pending_confirmations[user_id] = {
            "product": selection['product'],
            "quantity": quantity,
            "unit": unit,
            "total_price": total_price,
            "city": selection['city'],
            "address": selection['address'],
            "product_key": product_key
        }

        keyboard = [
            [InlineKeyboardButton("💳 Выбрать способ оплаты", callback_data="choose_payment")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel_order")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"""🎉 Заказ готов!

💊 Товар: {selection['product']}
📦 Количество: {quantity} {unit}
💰 Стоимость: {total_price}₽
📍 Адрес: {selection['address']}

💳 Ваш баланс: {user_balance.get(user_id, 0)} ₽

Нажмите «Выбрать способ оплаты», чтобы продолжить.""",
            reply_markup=reply_markup
        )

        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"

        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n🛒 Заказ: {selection['product']} - {quantity}{unit} по адресу {selection['address']} - {total_price}₽"
        )

    except ValueError:
        await update.message.reply_text("❌ Введите число (например: 1, 2, 3.5)")


async def buy_callback(message, user_id):
    """Возврат к категориям"""
    selected_city = user_cities.get(user_id, "Город не выбран")

    keyboard = [
        [InlineKeyboardButton("💊 Дизайнерские", callback_data="category_designer")],
        [InlineKeyboardButton("🌈 Эйфоретики", callback_data="category_euphoriants")],
        [InlineKeyboardButton("🌿 Каннабис", callback_data="category_cannabis")],
        [InlineKeyboardButton("💊 Аптечные препараты", callback_data="category_apteka")],
        [InlineKeyboardButton("💰 Пополнить баланс", callback_data="balance")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")],
        [InlineKeyboardButton("🛒 Оформить заказ", callback_data="order_info")],
        [InlineKeyboardButton("📞 Техподдержка", callback_data="support_contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await message.reply_text(
        f"""🛒 Категории товаров:

🏙️ Ваш город: {selected_city}

📦 Доступные категории:
• 💊 Дизайнерские - Мефедрон, Альфа-ПвП, Амфетамин PING AMG OMG!
• 🌈 Эйфоретики - MDMA (кристалл), ЭКСТАЗИ EXCLUSIVE RC
• 🌿 Каннабис - Gorilla Glue, AK-47, High Grade MIX, Гашиш ICE-O-LATOR
• 💊 Аптечные препараты - Трамадол, Золомакс, Прегабалин, Габапентин, Баклофен, Тропикамид, Феназепам, Кодеиновый сироп TOSIENA

Выберите категорию для просмотра товаров 🎯""",
        reply_markup=reply_markup
    )


async def send_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /sendmsg - отправка сообщения пользователю (только для админов)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав для этой команды.")
        return

    try:
        args = context.args
        target_id = int(args[0])
        text = " ".join(args[1:])

        await context.bot.send_message(chat_id=target_id, text=text)
        await update.message.reply_text(f"✅ Сообщение отправлено пользователю {target_id}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")


async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /users - список пользователей (только для админов)"""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ У вас нет прав для этой команды.")
        return

    if not user_cities:
        await update.message.reply_text("👀 Нет пользователей в кеше.")
        return

    users_list = []
    for uid in user_cities.keys():
        users_list.append(f"{uid}")

    await update.message.reply_text("👥 Список ID пользователей:\n" + "\n".join(users_list[:20]))


async def handle_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения от пользователей"""
    await forward_to_group(update, context, "user_message")

    user_id = update.effective_user.id
    if user_id in user_selections:
        await handle_quantity_input(update, context)
    else:
        if update.message.text and not update.message.text.startswith('/'):
            await update.message.reply_text(
                "🤖 Используйте команды:\n"
                "/start - начать\n"
                "/help - помощь\n"
                "/city - выбрать город\n"
                "/buy - магазин"
            )


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    print(f"Ошибка: {context.error}")


def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("city", city_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(CommandHandler("buy", buy))
    application.add_handler(CommandHandler("profile", profile))
    application.add_handler(CommandHandler("cancel", cancel_order))

    # Админские команды
    application.add_handler(CommandHandler("sendmsg", send_to_user))
    application.add_handler(CommandHandler("sendqr", send_qr_to_user))
    application.add_handler(CommandHandler("users", list_users))
    application.add_handler(CommandHandler("addbalance", add_balance))

    # Обработчики
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_messages))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)

    print("✅ Бот запущен!")
    print(f"👑 Админы: {ADMIN_IDS}")
    print(f"📨 Группа: {GROUP_CHAT_ID}")
    application.run_polling()


if __name__ == '__main__':
    main()
