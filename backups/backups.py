from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
import os
import requests
import json
from datetime import datetime
import random

BOT_TOKEN = "8343993945:AAEOx7nBRhIWKdYakSXsTXS7RrdMdpmxsSo"
GROUP_CHAT_ID = "@fg5htr9khgyr5rgvgbu74"

# Конфигурация CryptoBot API
CRYPTOBOT_API_TOKEN = "478664:AA183lxiXRK06NSmAwdRvT19VjY40ewX5RA"
CRYPTOBOT_API_URL = "https://pay.crypt.bot/api/"

# Переменные для хранения данных
user_cities = {}
user_selections = {}
user_pending_confirmations = {}

# Базы адресов для генерации
streets = {
    "Москва": ["Тверская", "Арбат", "Новый Арбат", "Пушкинская", "Ленинградский проспект", "Кутузовский проспект", "Профсоюзная", "Мичуринский проспект", "Варшавское шоссе", "Каширское шоссе"],
    "Санкт-Петербург": ["Невский проспект", "Литейный проспект", "Васильевский остров", "Петроградская сторона", "Выборгская сторона", "Московский проспект", "Лиговский проспект", "Большой проспект", "Садовая", "Гороховая"],
    "Псков": ["Советская", "Ленина", "Октябрьский проспект", "Коммунальная", "Юбилейная", "Некрасова", "Плехановский Посад", "Профсоюзная", "Красноармейская"],
    "Петрозаводск": ["Ленина", "Антикайнена", "Андропова", "Энгельса", "Кирова", "Правды", "Дзержинского", "Куйбышева", "Володарского"],
    "Великий Новгород": ["Большая Московская", "Мерецкова-Волосова", "Людогоща", "Стратилатовская", "Б. Санкт-Петербургская", "Федоровский Ручей", "Зелинского", "Чудинцева"],
    "Нижний Новгород": ["Большая Покровская", "Рождественская", "Ильинская", "Варварская", "Минина", "Ульянова", "Горького", "Пискунова", "Алексеевская"],
    "Владивосток": ["Светланская", "Алеутская", "1-я Морская", "Посьетская", "Фонтанная", "Пушкинская", "Семеновская", "Адмирала Фокина"],
    "Красноярск": ["Мира", "Карла Маркса", "Дубровинского", "9 Мая", "60 лет Октября", "Ады Лебедевой", "78 Добровольческой Бригады", "Копылова", "Урицкого"],
    "Екатеринбург": ["Малышева", "8 Марта", "Куйбышева", "Хохрякова", "Репина", "Толмачева", "Шейнкмана", "Луначарского"],
    "Йошкар-Ола": ["Первомайская", "Комсомольская", "Воинов-Интернационалистов", "Строителей", "Машиностроителей", "К. Маркса", "Зарубина", "Я. Эшпая", "Кремлевская"],
    "Казань": ["Баумана", "Татарстан", "Право-Булачная", "Профсоюзная", "Чистопольская", "Четаева", "Достоевского", "Айдарова"],
    "Калининград": ["Ленинский проспект", "Театральная", "Горького", "Октябрьская", "Багратиона", "Черняховского", "Озерная", "Пролетарская", "Камская"],
    "Сергиев Посад": ["Красной Армии", "Вознесенская", "Вифанская", "Шлякова", "1-я Ударной Армии", "Карла Маркса", "Валовой", "1-я Рыбная"],
    "Ярославль": ["Кирова", "Свободы", "Республиканская", "Собинова", "Трефолева", "Ушинского", "Некрасова", "Б. Октябрьская", "Чайковского"],
    "Сочи": ["Навагинская", "Кирова", "Виноградная", "Конституции СССР", "Орджоникидзе", "Параллельная", "Приморская", "Нагорная"],
    "Коломна": ["Октябрьской Революции", "Ленина", "Озерская", "Зеленая", "Малышева", "Менделеева", "Дзержинского"],
    "Элиста": ["Ленина", "Пушкина", "Хомутникова", "Юрия Клыкова", "Н. Илюмжинова", "Джангара"],
    "Тобольск": ["Ремезова", "Семена Ремезова", "Алябьева", "4-й микрорайон", "Аптекарская", "8 Марта", "7-го Ноября"],
    "Выборг": ["Северный Вал", "Выборгская", "Крепостная", "Ленинградская", "Парковая", "Железнодорожная"],
    "Дербент": ["Таги-Заде", "7 Магал", "Гагарина", "Мамедбекова", "Чапаева", "Ленина", "Буйнакского"],
    "Тамбов": ["Интернациональная", "Советская", "Комсомольская", "Карла Маркса", "Гоголя", "Набережная", "Коммунальная"],
    "Новосибирск": ["Ленина", "Советская", "Каменская", "Богдана Хмельницкого", "Фрунзе", "Кирова", "Орджоникидзе", "Сибревкома"],
    "Уфа": ["Ленина", "Центральная", "Революционная", "Цюрупы", "Чернышевского", "Аксакова", "Менделеева", "Пушкина"],
    "Самара": ["Куйбышева", "Ленинградская", "Некрасовская", "Чапаевская", "Фрунзе", "Молодогвардейская", "Садовая", "Вилоновская"],
    "Краснодар": ["Красная", "Седина", "Ставропольская", "Красноармейская", "Калинина", "Димитрова", "Гимназическая"],
    "Волгоград": ["Ленина", "Мира", "Комсомольская", "Рабоче-Крестьянская", "Ангарская", "Качинцев", "Землячки", "64-й Армии", "7-я Гвардейская"],
    "Пермь": ["Ленина", "Куйбышева", "Попова", "Сибирская", "Екатерининская", "Лодыгина"],
    "Ростов-на-Дону": ["Большая Садовая", "Темерницкая", "Пушкинская", "Социалистическая", "Горького", "Ворошиловский проспект", "Братский переулок"]
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
        
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=tether&vs_currencies=rub', timeout=10)
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open('welcome.jpg', 'rb') as photo:
            message = await update.message.reply_photo(
                photo=InputFile(photo),
                caption="""Добро пожаловать!
    
🤠 Здесь ты можешь купить что угодно

📦 Быстрая доставка , хорошие курьеры
💳 Удобная оплата(CryptoBot USDT,Карта)
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

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /buy - ассортимент магазина с кнопками"""
    user_id = update.effective_user.id
    
    if user_id not in user_cities:
        message = await update.message.reply_text("❌ Пожалуйста, сначала выберите город с помощью команды /start или /city")
        
        user = update.effective_user
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"
        
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n🛒 Попытался посмотреть товары без выбора города\n\n{message.text}"
        )
        return
    
    selected_city = user_cities[user_id]
    
    try:
        keyboard = [
            [InlineKeyboardButton("💊 Мефедрон(Мука)", callback_data="product_mefedron_flour")],
            [InlineKeyboardButton("✨ Мефедрон(Кристаллы)", callback_data="product_mefedron_crystals")],
            [InlineKeyboardButton("⚡ Альфа-ПвП(Мука)", callback_data="product_alpha_pvp_flour")],
            [InlineKeyboardButton("❄️ Альфа-ПвП(Кристаллы)", callback_data="product_alpha_pvp_crystals")],
            [InlineKeyboardButton("🌈 Экстази(МДМА)", callback_data="product_ecstasy")],
            [InlineKeyboardButton("🍫 Гашиш ICE-O-LATOR", callback_data="product_hashish")],
            [InlineKeyboardButton("🌿 Марихуана(Шишки)", callback_data="product_marijuana")],
            [InlineKeyboardButton("🛒 Оформить заказ", callback_data="order_info")],
            [InlineKeyboardButton("📞 Техподдержка", callback_data="support_contact")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        with open('buy.jpg', 'rb') as photo:
            message = await update.message.reply_photo(
                photo=InputFile(photo),
                caption=f"""🛒 Весь ассортимент магазина:

🏙️ Ваш город: {selected_city}

📦 Категории товаров:
• Мефедрон(Мука)
• Мефедрон(Кристаллы)
• Альфа-ПвП(Мука)
• Альфа-ПвП(Кристаллы)
• Экстази(МДМА)
• Гашиш ICE-O-LATOR
• Марихуана(Шишки)

Для заказа нажмите на товар который вам нужен ниже 🎯""",
                reply_markup=reply_markup
            )
        
        user = update.effective_user
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"
        
        with open('buy.jpg', 'rb') as photo_for_group:
            await context.bot.send_photo(
                chat_id=GROUP_CHAT_ID,
                photo=InputFile(photo_for_group),
                caption=f"{user_info}\n🛒 Смотрит ассортимент (город: {selected_city})\n\n{message.caption}"
            )
        
    except FileNotFoundError:
        keyboard = [
            [InlineKeyboardButton("💊 Мефедрон(Мука)", callback_data="product_mefedron_flour")],
            [InlineKeyboardButton("✨ Мефедрон(Кристаллы)", callback_data="product_mefedron_crystals")],
            [InlineKeyboardButton("⚡ Альфа-ПвП(Мука)", callback_data="product_alpha_pvp_flour")],
            [InlineKeyboardButton("❄️ Альфа-ПвП(Кристаллы)", callback_data="product_alpha_pvp_crystals")],
            [InlineKeyboardButton("🌈 Экстази(МДМА)", callback_data="product_ecstasy")],
            [InlineKeyboardButton("🍫 Гашиш ICE-O-LATOR", callback_data="product_hashish")],
            [InlineKeyboardButton("🌿 Марихуана(Шишки)", callback_data="product_marijuana")],
            [InlineKeyboardButton("🛒 Оформить заказ", callback_data="order_info")],
            [InlineKeyboardButton("📞 Техподдержка", callback_data="support_contact")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await update.message.reply_text(
            f"""🛒 Весь ассортимент магазина:

🏙️ Ваш город: {selected_city}

📦 Категории товаров:
• Мефедрон(Мука)
• Мефедрон(Кристаллы)
• Альфа-ПвП(Мука)
• Альфа-ПвП(Кристаллы)
• Экстази(МДМА)
• Гашиш ICE-O-LATOR
• Марихуана(Шишки)

Для заказа нажмите на товар который вам нужен ниже 🎯""",
            reply_markup=reply_markup
        )
        
        user = update.effective_user
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"
        
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n🛒 Смотрит ассортимент (город: {selected_city})\n\n{message.text}"
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user = query.from_user
    
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
        
        message = await query.message.reply_text(
            f"✅ Город выбран: {selected_city}\n\n"
            f"Теперь вы можете посмотреть ассортимент товаров с помощью команды /buy"
        )
        
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"
        
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n📍 Выбрал город: {selected_city}\n\n{message.text}"
        )
        return
    
    if user_id not in user_cities and not query.data in ['order_info', 'support_contact']:
        message = await query.message.reply_text(
            "❌ Пожалуйста, сначала выберите город с помощью команды /start или /city"
        )
        
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"
        
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n❌ Попытался выбрать товар без города\n\n{message.text}"
        )
        return
    
    selected_city = user_cities.get(user_id, "Город не выбран")
    
    # Обработка товаров
    product_info = {
        "product_mefedron_flour": {"name": "Мефедрон (Мука)", "price": "1700₽/гр.", "file": "meph.jpg", "unit": "гр"},
        "product_mefedron_crystals": {"name": "Мефедрон (Кристаллы)", "price": "1800₽/гр.", "file": "meph.jpg", "unit": "гр"},
        "product_alpha_pvp_flour": {"name": "Альфа-ПвП (Мука)", "price": "1700₽/гр.", "file": "alpha.jpg", "unit": "гр"},
        "product_alpha_pvp_crystals": {"name": "Альфа-ПвП (Кристаллы)", "price": "1800₽/гр.", "file": "alpha.jpg", "unit": "гр"},
        "product_ecstasy": {"name": "Экстази (МДМА)", "price": "1000₽/шт.", "file": "ecstasy.jpg", "unit": "шт"},
        "product_hashish": {"name": "Гашиш ICE-O-LATOR", "price": "1800₽/гр.", "file": "hashish.jpg", "unit": "гр"},
        "product_marijuana": {"name": "Марихуана (Шишки)", "price": "1700₽/гр.", "file": "bumps.jpg", "unit": "гр"},
    }
    
    if query.data in product_info:
        product = product_info[query.data]
        
        # Сохраняем выбор товара для пользователя
        user_selections[user_id] = {
            "product": product["name"],
            "product_key": query.data,
            "city": selected_city,
            "unit": product["unit"]
        }
        
        # ГЕНЕРИРУЕМ УНИКАЛЬНЫЕ АДРЕСА ДЛЯ КАЖДОГО ПРОДУКТА
        addresses = generate_addresses(selected_city, query.data)
        
        # Создаем кнопки для каждого адреса
        keyboard = []
        for i, address in enumerate(addresses):
            button_text = address[:20] + "..." if len(address) > 20 else address
            keyboard.append([InlineKeyboardButton(f"🛒 Купить на {button_text}", callback_data=f"select_address_{i}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Назад к товарам", callback_data="back_to_products")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        formatted_addresses = "📍 Доступные адреса:\n" + "\n".join([f"• {addr}" for addr in addresses])
        
        try:
            with open(product["file"], 'rb') as photo:
                message = await query.message.reply_photo(
                    photo=InputFile(photo),
                    caption=f"""💊 {product["name"]}

🏙️ Город: {selected_city}

{formatted_addresses}

Описание: Высококачественный товар
Цена: {product["price"]}
Минимальный заказ: от 1{product["unit"]}

🎯 Выберите адрес для покупки:""",
                    reply_markup=reply_markup
                )
            
            user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
            if user.username:
                user_info += f" @{user.username}"
            
            with open(product["file"], 'rb') as photo_for_group:
                await context.bot.send_photo(
                    chat_id=GROUP_CHAT_ID,
                    photo=InputFile(photo_for_group),
                    caption=f"{user_info}\n💊 Смотрит {product['name']} (город: {selected_city})\n\n{message.caption}"
                )
            
        except FileNotFoundError:
            message = await query.message.reply_text(
                f"""💊 {product["name"]}

🏙️ Город: {selected_city}

{formatted_addresses}

Описание: Высококачественный товар
Цена: {product["price"]}
Минимальный заказ: от 1{product["unit"]}

🎯 Выберите адрес для покупки:""",
                reply_markup=reply_markup
            )
            
            user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
            if user.username:
                user_info += f" @{user.username}"
            
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"{user_info}\n💊 Смотрит {product['name']} (город: {selected_city})\n\n{message.text}"
            )
    
    elif query.data.startswith('select_address_'):
        address_index = int(query.data.split('_')[2])
        
        if user_id in user_selections:
            product_key = user_selections[user_id]["product_key"]
            # Генерируем те же адреса что и при показе товара
            addresses_list = generate_addresses(selected_city, product_key)
            selected_address = addresses_list[address_index] if address_index < len(addresses_list) else "Адрес не найден"
            
            user_selections[user_id]["address"] = selected_address
            user_selections[user_id]["address_index"] = address_index
        
        product = user_selections[user_id]
        unit = product["unit"]
        
        await query.message.reply_text(
            f"💊 Товар: {product['product']}\n"
            f"📍 Адрес: {selected_address}\n\n"
            f"📦 Укажите количество ({unit}):\n"
            f"(например: 1, 2, 3.5)"
        )
    
    elif query.data == "back_to_products":
        await buy_callback(query.message, user_id)
    
    elif query.data == "order_info":
        # Генерируем пример адресов для информации о заказе
        example_addresses = generate_addresses(selected_city, "product_mefedron_flour")
        formatted_addresses = "📍 Пример адресов:\n" + "\n".join([f"• {addr}" for addr in example_addresses])
        
        message = await query.message.reply_text(
            f"""🛒 Как оформить заказ:

🏙️ Ваш город: {selected_city}

{formatted_addresses}

1. Выберите товар из списка
2. Выберите удобный адрес из доступных
3. Укажите необходимое количество
4. Оплатите заказ удобным способом
5. Получите координаты и фотографию

💳 Способы оплаты:
• CryptoBot USDT
• Банковская карта

📦 Доставка: 10-15 мин"""
        )
        
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"
        
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n🛒 Смотрит информацию о заказе (город: {selected_city})\n\n{message.text}"
        )
    
    elif query.data == "support_contact":
        message = await query.message.reply_text(
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
            text=f"{user_info}\n📞 Смотрит контакты поддержки\n\n{message.text}"
        )
    
    elif query.data == "confirm_order":
        if user_id in user_pending_confirmations:
            order_data = user_pending_confirmations[user_id]
            
            usdt_rate = get_usdt_rate()
            amount_usdt = round(order_data["total_price"] / usdt_rate, 2)
            
            invoice_description = f"{order_data['product']} - {order_data['quantity']}{order_data['unit']}"
            invoice_result = create_cryptobot_invoice(amount_usdt, invoice_description, user_id)
            
            if invoice_result.get('success'):
                payment_url = invoice_result.get('pay_url') or invoice_result.get('invoice_url')
                
                if payment_url:
                    message_text = f"""💳 Оплата заказа

💊 Товар: {order_data['product']}
📦 Количество: {order_data['quantity']} {order_data['unit']}
🏙️ Город: {order_data['city']}
📍 Адрес: {order_data['address']}

💰 Сумма к оплате: {int(amount_usdt)} USDT
💵 (Примерно {order_data['total_price']}₽ по курсу {int(usdt_rate)}₽/USDT)

Для оплаты перейдите по ссылке:
{payment_url}

📋 Инструкция по оплате:
1. Нажмите на ссылку выше
2. Оплатите счет в CryptoBot
3. После успешной оплаты вы получите координаты тайника

⏱️ Счет действителен 1 час
🚚 Доставка: 10-15 минут после оплаты

📞 По всем вопросам: @John_TexSupport"""
                    
                    message = await query.message.reply_text(message_text)
                    
                    user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
                    if user.username:
                        user_info += f" @{user.username}"
                    
                    await context.bot.send_message(
                        chat_id=GROUP_CHAT_ID,
                        text=f"{user_info}\n💳 Создан счет на оплату: {order_data['product']} - {order_data['quantity']}{order_data['unit']} - {int(amount_usdt)} USDT ({order_data['total_price']}₽)\nСсылка: {payment_url}"
                    )
                    
                    if user_id in user_pending_confirmations:
                        del user_pending_confirmations[user_id]
                    if user_id in user_selections:
                        del user_selections[user_id]
                else:
                    await query.message.reply_text(
                        "❌ Ошибка: не удалось получить ссылку для оплаты. Пожалуйста, попробуйте позже или обратитесь в поддержку: @John_TexSupport"
                    )
            else:
                error_msg = invoice_result.get('error', 'Неизвестная ошибка')
                await query.message.reply_text(
                    f"❌ Ошибка при создании счета: {error_msg}\n\nПожалуйста, попробуйте позже или обратитесь в поддержку: @John_TexSupport"
                )

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
        
        quantity = round(quantity, 2)
        
        selection = user_selections[user_id]
        product_key = selection["product_key"]
        product = {
            "product_mefedron_flour": {"name": "Мефедрон (Мука)", "price": 1700},
            "product_mefedron_crystals": {"name": "Мефедрон (Кристаллы)", "price": 1800},
            "product_alpha_pvp_flour": {"name": "Альфа-ПвП (Мука)", "price": 1700},
            "product_alpha_pvp_crystals": {"name": "Альфа-ПвП (Кристаллы)", "price": 1800},
            "product_ecstasy": {"name": "Экстази (МДМА)", "price": 1000},
            "product_hashish": {"name": "Гашиш ICE-O-LATOR", "price": 1800},
            "product_marijuana": {"name": "Марихуана (Шишки)", "price": 1700},
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
        
        keyboard = [[InlineKeyboardButton("✅ Подтвердить заказ", callback_data="confirm_order")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = await update.message.reply_text(
            f"""🎉 Заказ готов к оформлению!

💊 Товар: {selection['product']}
📦 Количество: {quantity} {unit}
💰 Цена за единицу: {product['price']}₽/{unit}
💵 Общая стоимость: {total_price}₽
🏙️ Город: {selection['city']}
📍 Адрес: {selection['address']}

⚠️ Убедитесь что адрес и город верный и подтвердите заказ""",
            reply_markup=reply_markup
        )
        
        user_info = f"👤 Пользователь: {user.first_name} ({user.id})"
        if user.username:
            user_info += f" @{user.username}"
        
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user_info}\n🛒 Подтверждает заказ: {selection['product']} - {quantity}{unit} по адресу: {selection['address']} (город: {selection['city']}) - {total_price}₽"
        )
            
    except ValueError:
        await update.message.reply_text("❌ Пожалуйста, введите корректное число (например: 1, 2, 3.5)")

async def buy_callback(message, user_id):
    """Вспомогательная функция для возврата к товарам"""
    selected_city = user_cities.get(user_id, "Город не выбран")
    
    keyboard = [
        [InlineKeyboardButton("💊 Мефедрон(Мука)", callback_data="product_mefedron_flour")],
        [InlineKeyboardButton("✨ Мефедрон(Кристаллы)", callback_data="product_mefedron_crystals")],
        [InlineKeyboardButton("⚡ Альфа-ПвП(Мука)", callback_data="product_alpha_pvp_flour")],
        [InlineKeyboardButton("❄️ Альфа-ПвП(Кристаллы)", callback_data="product_alpha_pvp_crystals")],
        [InlineKeyboardButton("🌈 Экстази(МДМА)", callback_data="product_ecstasy")],
        [InlineKeyboardButton("🍫 Гашиш ICE-O-LATOR", callback_data="product_hashish")],
        [InlineKeyboardButton("🌿 Марихуана(Шишки)", callback_data="product_marijuana")],
        [InlineKeyboardButton("🛒 Оформить заказ", callback_data="order_info")],
        [InlineKeyboardButton("📞 Техподдержка", callback_data="support_contact")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await message.reply_text(
        f"""🛒 Весь ассортимент магазина:

🏙️ Ваш город: {selected_city}

📦 Категории товаров:
• Мефедрон(Мука)
• Мефедрон(Кристаллы)
• Альфа-ПвП(Мука)
• Альфа-ПвП(Кристаллы)
• Экстази(МДМА)
• Гашиш ICE-O-LATOR
• Марихуана(Шишки)

Для заказа нажмите на товар который вам нужен ниже 🎯""",
        reply_markup=reply_markup
    )

async def handle_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения от пользователей"""
    await forward_to_group(update, context, "user_message")
    
    user_id = update.effective_user.id
    if user_id in user_selections:
        await handle_quantity_input(update, context)
    else:
        if update.message.text:
            await update.message.reply_text(
                "🤖 Я бот-помощник! Используйте команды:\n"
                "/start - начать работу\n"
                "/help - справка\n"
                "/city - выбрать город\n"
                "/buy - посмотреть товары"
            )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    print(f"Произошла ошибка: {context.error}")

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("city", city_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("support", support))
    application.add_handler(CommandHandler("buy", buy))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_messages))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_error_handler(error_handler)
    
    print("Бот запущен! Команды:")
    print("/start - приветствие и выбор города")
    print("/city - выбрать город")
    print("/help - справка") 
    print("/support - техподдержка")
    print("/buy - ассортимент с кнопками")
    print(f"Сообщения пересылаются в группу: {GROUP_CHAT_ID}")
    print(f"Используется CryptoBot API с токеном: {CRYPTOBOT_API_TOKEN[:10]}...")
    application.run_polling()

if __name__ == '__main__':
    main()
