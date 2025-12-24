## Ash Herald 🔮

A magical assistant for working with Tarot and Lenormand cards, lunar cycles, and weather forecasts.         

The bot combines ancient esoteric traditions with modern technology for accurate and insightful interpretations.        

Current version: [**Yule** - v1.2.0](https://github.com/AshLeigh-Fraxinus/ash_herald_bot/releases/tag/v1.2.0)

---

### Features:       

🎴 **Working with cards**       

- **Deck selection** — Tarot (78 cards) or Lenormand (36 cards). A choice of deck designs is available for Tarot.       
- **Revelation Card of the Day** — Daily prediction and advice      
- **Three Faces of Fate** — In-depth analysis of your question      
- **Additional Explanatory Card** — clarification of an existing spread     
- **Professional Interpretation** — detailed analysis based on esoteric knowledge       

🌙 **Moon Magic**       

- **Current Moon Phase** with visualization     
- **Lunar Day**     
- **Position in Zodiac Sign**       
- **Moon Visibility Percentage**        

⛅ **Weather Magic**

- **Weather Forecast** for Today and Tomorrow               
- **Change City** at Any Time           
- **Detailed Data** Including Atmospheric Pressure, Wind Strength and Direction, as Well as Sunset and Sunrise Times        

---

### Installation and Run:       

#### 1. Clone the repository:       

```
git clone https://github.com/AshLeigh-Fraxinus/ash_herald
cd ash_herald
```

#### 2. Installation Dependencies:      

```
pip install -r requirements.txt
```

#### 3. Environment Setup:

Create a .env file in the project root and add the following variables:     

```
BOT_TOKEN=<your_telegram_bot_token>
GROQ_API_KEY=<your_groq_api_key>
MOON_API_URL=https://moon-api.ru/v1/moonPhaseDate?lang=ru

WEATHER_API_URL=https://api.openweathermap.org/data/2.5/forecast?units=metric&lang=ru&q=
WEATHER_API_KEY=<your_openerathermap_key>
```

#### 4. Obtaining Keys:

- **Telegram Bot Token**: via @BotFather        
- **Groq API Key**: on [platform.groq.com](https://console.groq.com/keys)       
- **Weather API**: on [openweathermap.org](https://openweathermap.org/)  

#### 5. Run

```
python src/main.py
```

---

### Technical Features:

- Asynchronous architecture — high performance and responsiveness       
- Relational database — secure storage of user data and spreads     
- Three unique decks — advanced fortune-telling capabilities        
- Modular system — flexible architecture with clear separation of responsibilities      
- Professional logging — detailed monitoring of all operations      
- Fault tolerance — automatic recovery system in case of failures       
- Personalization – customize your bot to your preferences!     

---

### Project Structure:

```
ash_herald/
│   .env 
│   README.md
│   README_ru.md
│   requirements.txt
├───database
│       sessions.db
│       tarot.db
├───resources
│   ├───deviant_moon_deck
│   ├───lenorman_deck
│   ├───persona3_deck
│   ├───santa_muerte_deck
│   └───tarot_deck
└───src
    │   bot.py
    │   main.py
    ├───actions
    │   ├───cards
    │   │   │   cards_add.py
    │   │   │   cards_daily.py
    │   │   │   cards_three.py
    │   │   │   db_interpretation.py
    │   │   │   interpretation.py
    │   │   └───deck
    │   │           deck.py
    │   ├───moon
    │   │       day.py
    │   ├───settings
    │   │       change_city.py
    │   │       change_deck.py
    │   │       change_name.py
    │   └───weather
    │           weather_data.py
    │           weather_message.py
    ├───handlers
    │       handler.py
    │       handle_admin.py
    │       handle_cards.py
    │       handle_change.py
    │       handle_common.py
    │       handle_weather.py
    ├───service
    │       database.py
    │       migrations.py
    │       sessions.py
    └───utils
            keyboards.py
            logging_config.py
            texts.py
```

---


### Enjoy your journey! 🪬
