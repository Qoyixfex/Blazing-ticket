# Blazing Ticket - Discord Bot
**Reminder, this is still beta, so might be a little bug.

![Python](https://files.catbox.moe/5o6hb6.gif)
A customizable Discord bot for ticket management and support systems.

## Features

- 🎫 **Ticket System**: Create and manage support tickets
- 🔐 **Role Management**: Automatic role assignments
- 📊 **Custom Commands**: Fully customizable command system
- 📝 **Logging**: Comprehensive activity logging
- 📁 **File Support**: Handle attachments in tickets
- ⚡ **Fast & Efficient**: Optimized for large servers
- 🎨 **Customizable**: Easy to configure and extend

## Tech Stack

- **Python 3.8+**
- **discord.py 2.0+**
- **SQLite/PostgreSQL** database
- **asyncio** for async operations

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Discord Developer Application

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd blazing-ticket-bot
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the bot**
   ```bash
   cp config.example.py config.py
   # Edit config.py with your settings
   ```

5. **Set up environment variables**
   ```bash
   # Create token.txtfile
  echo "token" # i recommend change it to env, so u can hide your discord bot token.
   ```

6. **Run the bot**
   ```bash
   python bot.py
   ```

## Configuration

Edit `config.py` to customize:

```python
# Bot Configuration
BOT_PREFIX = "/"
BOT_STATUS = "Can customize."

# List of commands
/setup # for role setup only
/panel # run it on ticket channel

# Customization
can custome codes, and stuff.
```

## Project Structure

## Command Usage

### `/help`
Displays the help menu with all available commands and their descriptions.

**Usage:**
```
/help 
```

**Examples:**
```
/help          # Shows all commands
```

### `/panel`
Creates an interactive ticket panel where users can open new tickets.

**Usage:**
```
/panel [support role] [staff role]
```

**Examples:**
```
/help <list of commands.>
```

**Permissions Required:** Administrator

### `/setup`
Initial setup wizard for configuring the bot on your server.

**Usage:**
```
/setup
```

**Setup Steps:**
1. Configures ticket category
2. Sets up support roles
3. Creates log channels
4. Sets permissions

**Permissions Required:** Administrator

### `/ping`
Checks the bot's latency and response time.

**Usage:**
```
/ping
```

**Response:**
```
Latency: 45ms | API: 52ms
```

## Database Schema

The bot uses SQLite with the following tables:
- `tickets` - Ticket information and status
- `users` - User preferences and data
- `settings` - Server configuration settings

## Support

For issues and questions:
1. Check the `/help` command
2. Review the configuration guide
3. Open an issue on GitHub
