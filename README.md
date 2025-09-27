# Blazing Ticket - Discord Bot
***Reminder, this is still beta, so might be a little bug.***

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

### Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Discord Developer Application

## Configuration

Edit `bot.py` to customize:

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

# commands:

### `/help`
Displays the help menu with all available commands and their descriptions.

### `/panel`
Creates an interactive ticket panel where users can open new tickets.

**Usage:**
```
/panel # use it on ticket channel
```

**Examples:**
```
/help <list of commands.>
```

**Permissions Required:** Administrator

### `/setup`
Initial setup for configuring the bot on your server.

**Usage:**
```
/setup  [support role] [staff role]
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
