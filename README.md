## Ash Herald 🔮

A magical assistant for working with Tarot, Lenormand, and lunar cycles.        

The bot combines ancient esoteric traditions with modern technology for accurate and insightful interpretations.        

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
BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
MOON_API_URL=your_moon_api_endpoint
```

#### 4. Obtaining Keys:

- **Telegram Bot Token**: via @BotFather        
- **Groq API Key**: on [platform.groq.com](https://console.groq.com/keys)       
- **Moon API**: on https://github.com/prostraction/moon     

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

---

### Project Structure:

```
ash_herald/
├── src/
│   ├── ash_herald/
│   │   ├── actions/                 # Functional Modules
│   │   │   ├── moon/
│   │   │   │   └── moon_day.py
│   │   │   └── spreads/
│   │   │   │   ├── deck/
│   │   │   │   │   ├── deck.py
│   │   │   │   │   └── change_deck.py
│   │   │   │   ├── interpretation.py
│   │   │   │   ├── cards_add.py
│   │   │   │   ├── cards_daily.py
│   │   │   │   └── cards_three.py
│   │   ├── handlers/                # Message handlers
│   │   │   ├── main_handler.py
│   │   │   └── spreads_handler.py
│   │   ├── utils/                   # Helper Utilities
│   │   │   ├── utils.py
│   │   │   └── keyboard.py
│   │   ├── database.py              # Database Initialization
│   │   ├── sessions.py              # Session Management
│   │   └── texts.py                 # Text Resources
│   ├── resources/                   # Media Resources
│   │   ├── deviant_img/
│   │   ├── lenorman_img/
│   │   ├── muerte_img/
│   │   └── tarot_img/
│   ├── bot.py                       # Main Bot
│   └── main.py                      # Entry Point
├── .env
├── requirements.txt
└── README.md
```

---


### Enjoy your journey! 🪬
