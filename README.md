# Blazing Ticket - Discord Bot
*A powerful and customizable ticket management system for Discord servers.*

> ⚠️ **Note:** This project is currently in beta. Some features may contain bugs or be subject to change.

## ✨ Features

- **🎫 Advanced Ticket System** - Create, manage, and resolve support tickets with ease
- **🔐 Role-Based Access Control** - Automatic role assignments and permission management
- **⚙️ Customizable Commands** - Tailor commands to fit your server's needs
- **📊 Comprehensive Logging** - Detailed activity logs for moderation and analytics
- **⚡ High Performance** - Optimized for servers of all sizes
- **🎨 Easy Customization** - Simple configuration and extensible architecture

## 🛠️ Tech Stack

- **Python 3.8+**
- **discord.py 2.0+**
- **SQLite/PostgreSQL** database support

## 📋 Prerequisites

Before you begin, ensure you have:
- Python 3.8 or higher installed
- A Discord Bot Token from the [Discord Developer Portal](https://discord.com/developers/applications)
- Appropriate permissions on your Discord server

## ⚙️ Configuration

Edit `config.py` or `bot.py` to customize the bot:

```python
# Bot Configuration
BOT_PREFIX = "/"
BOT_STATUS = "Managing support tickets"
BOT_VERSION = "1.0.0-beta"

# Channel Settings
TICKET_CATEGORY = "Support Tickets"
LOG_CHANNEL = "bot-logs"
```

## 📖 Command Reference

### `/help`
Displays a comprehensive help menu with all available commands.

**Usage:**
```bash
/help # list all commands
```

### `/panel`
Creates an interactive ticket creation panel in the specified channel.

**Usage:**
```bash
/panel  # Execute in the desired ticket channel
```

**Permissions Required:** Administrator

### `/setup`
Guides you through the initial server configuration process.

**Usage:**
```bash
/setup [support_role] [staff_role]
```

**Configuration Steps:**
1. Creates dedicated ticket category
2. Configures support and staff roles
3. Sets up logging channels
4. Establishes appropriate permissions

**Permissions Required:** Administrator

### `/ping`
Checks bot responsiveness and connection status.

**Usage:**
```bash
/ping
```

**Example Response:**
```
🏓 Pong! Latency: 45ms | API: 52ms
```

## 🗃️ Database Schema

The bot uses the following database structure:

### `tickets` Table
- `ticket_id` - Unique ticket identifier
- `user_id` - User who created the ticket
- `channel_id` - Dedicated ticket channel
- `status` - Current ticket status (open/closed/resolved)
- `created_at` - Ticket creation timestamp
- `closed_at` - Ticket closure timestamp

### `users` Table
- `user_id` - Discord user ID
- `preferences` - User-specific settings
- `ticket_count` - Number of tickets created

### `server_settings` Table
- `server_id` - Discord server ID
- `prefix` - Custom command prefix
- `log_channel` - Channel for bot logs
- `support_roles` - Configured support roles

## 🐛 Troubleshooting & Support

### Common Issues
1. **Bot not responding?** Check if it has proper permissions
2. **Commands not working?** Verify the bot has required intents
3. **Database errors?** Ensure write permissions in the bot directory

### Getting Help
1. Use the `/help` command for in-app guidance
2. Review the configuration settings
3. Check the GitHub repository for known issues
4. Open an issue on our GitHub page for bug reports

## 🔄 Version Information
- **Current Version:** 1.0.0-beta
- **Last Updated:** Saturday, 27 September 2025
- **Discord.py Version:** 2.0.0+

---

*For more information, contribute, or report issues, visit our GitHub repository.*
