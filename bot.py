import discord
from discord.ext import commands, tasks
from discord.ui import Select, View, Button, Modal, TextInput
import asyncio
import datetime
import json
import os

# Bot configuration
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Data storage
TICKETS_FILE = "tickets.json"
CONFIG_FILE = "config.json"

# Default configuration
default_config = {
    "staff_role_id": None,
    "ticket_category_id": None,
    "log_channel_id": None,
    "support_team_role_id": None,
    "panel_channel_id": None
}

# Load configuration
def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return default_config.copy()

def save_config(config):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

# Load tickets data
def load_tickets():
    try:
        if os.path.exists(TICKETS_FILE):
            with open(TICKETS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading tickets: {e}")
    return {"tickets": {}, "user_timeouts": {}}

def save_tickets(data):
    try:
        with open(TICKETS_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving tickets: {e}")

# Global variables
config = load_config()
tickets_data = load_tickets()
start_time = None

# Custom emojis from your server
class Emojis:
    ANIMATED_YES = "<a:CheckYes_mg1btcu1_c3ft:1421240078000455772>"
    VERIFY = "<:verify_mg1cda9k_rwrc:1421243976240857312>"
    BUYER = "<:gift_mg1ebqya_97tn:1421257766034735306>"  # Updated to gift emoji
    DRAGON = "<:dragons_mfzxft2b_rp1x:1420885183975915664>"
    WARNING = "<a:warning_mfzxh3kk_x2od:1420885437542694963>"
    SUPPORT = "<:headphones_mg1bmvx2_1pff:1421238809852383272>"
    MODS = "<:Dev_mg1ck3ji_cpm4:1421245309631332392>"
    SERVER = "<:authorized_mg1chryl_8s6p:1421244854884896862>"
    LOADING = "<a:blackLoading_mg0cl0sp_3adm:1420991877771034778>"
    IGNORE = "<:ignorechannels_mg0cnx6i_v9n1:1420992444186628156>"
    WELCOMER = "<:Welcomer_mg0cnkb4_bepv:1420992374032826410>"
    CHECK_NO = "<a:CheckNo_mg0cph5t_2qwv:1420992748890226858>"
    DOT = "<a:black_dot_mg1blbz0_pea8:1421238506012938264>"
    INFO = "<:info_mg1cxrq2_ksx8:1421247984569417810>"
    SETTINGS = "<:settings_mg1cys5a_ou3h:1421248182951608461>"

# Enhanced color scheme (updated to more distinguishable colors for better UX)
COLORS = {
    "primary": 0x000000,      # Black (main color)
    "secondary": 0x000000,    # Black for secondary
    "success": 0x57F287,      # Green for success
    "warning": 0xFEE75C,      # Yellow for warning
    "error": 0xED4245,        # Red for error
    "info": 0x000000,         # Black for info
    "premium": 0x000000       # Black for premium
}

# Modals for different ticket types
class BuyTicketModal(Modal, title="Purchase Information"):
    def __init__(self, original_interaction):
        super().__init__()
        self.original_interaction = original_interaction
        self.item = TextInput(
            label="What do you want to buy?",
            placeholder="e.g., Discord members, boosts, hosting, etc.",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.budget = TextInput(
            label="What is your budget?",
            placeholder="e.g., $50, 100€, etc.",
            required=True
        )
        self.add_item(self.item)
        self.add_item(self.budget)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            await create_ticket(interaction, "buy", f"**Purchase Request:**\n{Emojis.BUYER} Item: {self.item.value}\n💰 Budget: {self.budget.value}")
            # Reset the select menu after modal submit
            new_view = View(timeout=None)
            new_view.add_item(TicketDropdown())
            await self.original_interaction.message.edit(view=new_view)
        except Exception as e:
            print(f"Error in BuyTicketModal on_submit: {e}")

class OtherTicketModal(Modal, title="Ticket Details"):
    def __init__(self, original_interaction):
        super().__init__()
        self.original_interaction = original_interaction
        self.reason = TextInput(
            label="Why did you open this ticket?",
            placeholder="Please describe your issue or request in detail...",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            await create_ticket(interaction, "other", f"**Reason:** {self.reason.value}")
            # Reset the select menu after modal submit
            new_view = View(timeout=None)
            new_view.add_item(TicketDropdown())
            await self.original_interaction.message.edit(view=new_view)
        except Exception as e:
            print(f"Error in OtherTicketModal on_submit: {e}")

class StaffApplicationModal(Modal, title="Staff Application"):
    def __init__(self, original_interaction):
        super().__init__()
        self.original_interaction = original_interaction
        self.experience = TextInput(
            label="What's your experience with moderation?",
            placeholder="Describe your previous experience...",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.availability = TextInput(
            label="What's your availability?",
            placeholder="e.g., 5-10 PM EST weekdays",
            required=True
        )
        self.why = TextInput(
            label="Why do you want to be staff?",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.experience)
        self.add_item(self.availability)
        self.add_item(self.why)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            details = f"**Staff Application:**\n{Emojis.MODS} Experience: `{self.experience.value}`\n<a:VoidTimer_mg1i8jwb_kh8b:1421285319210438798> Availability: `{self.availability.value}`\n<:messagechat_mg1i6mv5_vssp:1421284943077707788> Why: `{self.why.value}`"
            await create_ticket(interaction, "staff_application", details)
            # Reset the select menu after modal submit
            new_view = View(timeout=None)
            new_view.add_item(TicketDropdown())
            await self.original_interaction.message.edit(view=new_view)
        except Exception as e:
            print(f"Error in StaffApplicationModal on_submit: {e}")

# Ticket dropdown menu with custom emojis
class TicketDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Staff Report", 
                description="Report a staff member", 
                emoji=Emojis.MODS
            ),
            discord.SelectOption(
                label="Buy Services", 
                description="Purchase members, boosts, etc.", 
                emoji=Emojis.BUYER  # Now uses the gift emoji
            ),
            discord.SelectOption(
                label="Community Support", 
                description="Get help with community issues", 
                emoji=Emojis.SUPPORT
            ),
            discord.SelectOption(
                label="Apply for Staff", 
                description="Apply to become a staff member", 
                emoji=Emojis.WELCOMER
            ),
            discord.SelectOption(
                label="Other", 
                description="Any other issues or inquiries", 
                emoji=Emojis.IGNORE
            )
        ]
        super().__init__(placeholder="Choose a ticket type...", options=options, custom_id="ticket_dropdown")
    
    async def callback(self, interaction: discord.Interaction):
        try:
            ticket_type = self.values[0]
            user_id = str(interaction.user.id)
            
            # Check for timeout (10 seconds cooldown)
            if user_id in tickets_data["user_timeouts"]:
                timeout_end = datetime.datetime.fromisoformat(tickets_data["user_timeouts"][user_id])
                if datetime.datetime.now() < timeout_end:
                    remaining = timeout_end - datetime.datetime.now()
                    embed = discord.Embed(
                        title=f"{Emojis.WARNING} Timeout Active",
                        description=f"Please wait {int(remaining.total_seconds())} seconds before creating another ticket.",
                        color=COLORS["warning"]
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            
            # Check if user already has an open ticket
            for ticket_id, ticket_info in tickets_data["tickets"].items():
                if ticket_info["user_id"] == user_id and ticket_info["status"] == "open":
                    embed = discord.Embed(
                        title=f"{Emojis.WARNING} Already Have Open Ticket",
                        description="You already have an open ticket! Please close it before creating a new one.",
                        color=COLORS["warning"]
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            
            if ticket_type == "Staff Report":
                embed = discord.Embed(
                    title=f"{Emojis.MODS} Staff Report",
                    description="Please describe the staff member and the issue in your ticket after it's created.",
                    color=COLORS["warning"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                await create_ticket(interaction, "staff-report", "**Type:** Staff Report")
                # Reset select menu
                new_view = View(timeout=None)
                new_view.add_item(TicketDropdown())
                await interaction.message.edit(view=new_view)
            
            elif ticket_type == "Buy Services":
                modal = BuyTicketModal(interaction)
                await interaction.response.send_modal(modal)
            
            elif ticket_type == "Community Support":
                embed = discord.Embed(
                    title=f"{Emojis.SUPPORT} Community Support",
                    description="Please describe your community issue in the ticket after it's created.",
                    color=COLORS["info"]
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                await create_ticket(interaction, "community-support", "**Type:** Community Support")
                # Reset select menu
                new_view = View(timeout=None)
                new_view.add_item(TicketDropdown())
                await interaction.message.edit(view=new_view)
            
            elif ticket_type == "Apply for Staff":
                modal = StaffApplicationModal(interaction)
                await interaction.response.send_modal(modal)
            
            elif ticket_type == "Other":
                modal = OtherTicketModal(interaction)
                await interaction.response.send_modal(modal)
        except Exception as e:
            embed = discord.Embed(
                title=f"{Emojis.CHECK_NO} Error",
                description=f"An error occurred while processing your selection: {str(e)}",
                color=COLORS["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            print(f"Error in TicketDropdown callback: {e}")

# Enhanced ticket view with custom emojis
class TicketControls(View):
    def __init__(self, ticket_id):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id
    
    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger, custom_id="close_ticket", emoji=Emojis.CHECK_NO)
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        try:
            await close_ticket_handler(interaction, self.ticket_id)
        except Exception as e:
            embed = discord.Embed(
                title=f"{Emojis.CHECK_NO} Error",
                description=f"An error occurred while closing the ticket: {str(e)}",
                color=COLORS["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            print(f"Error in close_ticket: {e}")
    
    @discord.ui.button(label="Add Member", style=discord.ButtonStyle.success, custom_id="add_member", emoji=Emojis.VERIFY)
    async def add_member(self, interaction: discord.Interaction, button: Button):
        try:
            await add_member_handler(interaction, self.ticket_id)
        except Exception as e:
            embed = discord.Embed(
                title=f"{Emojis.CHECK_NO} Error",
                description=f"An error occurred while adding member: {str(e)}",
                color=COLORS["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            print(f"Error in add_member: {e}")
    
    @discord.ui.button(label="Remove Member", style=discord.ButtonStyle.secondary, custom_id="remove_member", emoji=Emojis.IGNORE)
    async def remove_member(self, interaction: discord.Interaction, button: Button):
        try:
            await remove_member_handler(interaction, self.ticket_id)
        except Exception as e:
            embed = discord.Embed(
                title=f"{Emojis.CHECK_NO} Error",
                description=f"An error occurred while removing member: {str(e)}",
                color=COLORS["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            print(f"Error in remove_member: {e}")
    
    @discord.ui.button(label="Rename", style=discord.ButtonStyle.primary, custom_id="rename_ticket", emoji=Emojis.MODS)
    async def rename_ticket(self, interaction: discord.Interaction, button: Button):
        try:
            await rename_ticket_handler(interaction, self.ticket_id)
        except Exception as e:
            embed = discord.Embed(
                title=f"{Emojis.CHECK_NO} Error",
                description=f"An error occurred while renaming ticket: {str(e)}",
                color=COLORS["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            print(f"Error in rename_ticket: {e}")

# Create ticket function
async def create_ticket(interaction, ticket_type, details):
    try:
        guild = interaction.guild
        user = interaction.user
        category = guild.get_channel(config["ticket_category_id"]) if config["ticket_category_id"] else None
        if not category:
            raise ValueError("Ticket category not configured. Please run /setup first.")
        
        # Create ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }
        
        # Add staff role if configured
        if config["staff_role_id"]:
            staff_role = guild.get_role(config["staff_role_id"])
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        
        ticket_channel = await guild.create_text_channel(
            name=f"{ticket_type}-{user.display_name}".lower().replace(" ", "-"),
            category=category,
            overwrites=overwrites
        )
        
        # Generate ticket ID
        ticket_id = f"{user.id}-{int(datetime.datetime.now().timestamp())}"
        
        # Store ticket data
        tickets_data["tickets"][ticket_id] = {
            "channel_id": ticket_channel.id,
            "user_id": str(user.id),
            "type": ticket_type,
            "status": "open",
            "created_at": datetime.datetime.now().isoformat(),
            "details": details
        }
        save_tickets(tickets_data)
        
        # Create beautiful embed message
        embed = discord.Embed(
            title=f"{Emojis.DRAGON} Blazing Ticket System",
            description=f"{Emojis.VERIFY} **Welcome to your ticket, {user.mention}!**\n\nOur support team will assist you shortly. Please be patient and describe your issue clearly.",
            color=COLORS["primary"],
            timestamp=datetime.datetime.now()
        )
        
        # Add decorative fields
        embed.add_field(
            name=f"{Emojis.SERVER} Ticket Information",
            value=f"**Type:** {ticket_type.replace('-', ' ').title()}\n**ID:** `{ticket_id}`\n**Created:** <t:{int(datetime.datetime.now().timestamp())}:R>",
            inline=False
        )
        
        embed.add_field(
            name=f"{Emojis.LOADING} Details Provided",
            value=details,
            inline=False
        )
        
        embed.add_field(
            name=f"{Emojis.WARNING} Available Controls",
            value=f"{Emojis.CHECK_NO} **Close** - Close this ticket\n{Emojis.VERIFY} **Add Member** - Add someone to ticket (staff only)\n{Emojis.IGNORE} **Remove Member** - Remove someone (staff only)\n{Emojis.SETTINGS} **Rename** - Change ticket name",
            inline=False
        )
        
        embed.set_footer(text="Blazing Ticket System • Support Experience")
        
        # Send ticket message with controls
        controls = TicketControls(ticket_id)
        message = await ticket_channel.send(
            content=f"{Emojis.VERIFY} {user.mention} {'<@&' + str(config['support_team_role_id']) + '>' if config['support_team_role_id'] else ''}",
            embed=embed,
            view=controls
        )
        
        # Pin the ticket message
        await message.pin()
        
        # Send rules reminder with beautiful embed
        rules_embed = discord.Embed(
            title=f"{Emojis.WARNING} Ticket Rules & Guidelines",
            description="To ensure the best experience for everyone, please follow these rules:",
            color=COLORS["secondary"]
        )
        
        rules_embed.add_field(
            name=f"{Emojis.ANIMATED_YES} Do's",
            value=f"{Emojis.DOT} Describe your issue clearly\n{Emojis.DOT} Be patient and respectful\n{Emojis.DOT} Provide all necessary information\n{Emojis.DOT} Follow staff instructions",
            inline=True
        )
        
        rules_embed.add_field(
            name=f"{Emojis.CHECK_NO} Don'ts",
            value=f"{Emojis.DOT} Don't ping support members\n{Emojis.DOT} Don't create tickets for fun\n{Emojis.DOT} Don't spam or be rude\n{Emojis.DOT} Don't share personal info",
            inline=True
        )
        
        rules_embed.set_footer(text="Violating rules may result in timeout or ban from ticket system")
        
        await ticket_channel.send(embed=rules_embed)
        
        # Send confirmation to user
        success_embed = discord.Embed(
            title=f"{Emojis.ANIMATED_YES} Ticket Created Successfully!",
            description=f"Your ticket has been created: {ticket_channel.mention}",
            color=COLORS["success"]
        )
        await interaction.followup.send(embed=success_embed, ephemeral=True)
        
        # Log ticket creation with more info
        log_message = f"{Emojis.DRAGON} Ticket Created\n**ID:** `{ticket_id}`\n**User:** {user} ({user.id})\n**Type:** {ticket_type}\n**Details:** {details[:200]}..."
        await log_ticket_action(log_message)
    except Exception as e:
        embed = discord.Embed(
            title=f"{Emojis.CHECK_NO} Error",
            description=f"An error occurred while creating the ticket: {str(e)}",
            color=COLORS["error"]
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        print(f"Error in create_ticket: {e}")

# Ticket control handlers
async def close_ticket_handler(interaction, ticket_id):
    try:
        if ticket_id not in tickets_data["tickets"]:
            embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description="Ticket not found!", color=COLORS["error"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        ticket = tickets_data["tickets"][ticket_id]
        channel = interaction.guild.get_channel(ticket["channel_id"])
        
        if not channel:
            embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description="Ticket channel not found!", color=COLORS["error"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Generate transcript
        transcript = f"Ticket ID: {ticket_id}\nType: {ticket['type']}\nUser: {ticket['user_id']}\n\n"
        async for msg in channel.history(limit=1000, oldest_first=True):
            transcript += f"[{msg.created_at.isoformat()}] {msg.author.display_name}: {msg.content}\n"
        
        transcript_file = f"{ticket_id}.txt"
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        
        # Update ticket status
        ticket["status"] = "closed"
        ticket["closed_at"] = datetime.datetime.now().isoformat()
        ticket["closed_by"] = str(interaction.user.id)
        save_tickets(tickets_data)
        
        # Add timeout to prevent spam (10 seconds cooldown)
        user_id = ticket["user_id"]
        timeout_end = datetime.datetime.now() + datetime.timedelta(seconds=10)
        tickets_data["user_timeouts"][user_id] = timeout_end.isoformat()
        save_tickets(tickets_data)
        
        # Send beautiful closing message
        embed = discord.Embed(
            title=f"{Emojis.CHECK_NO} Ticket Closed",
            description=f"This ticket has been closed by {interaction.user.mention}",
            color=COLORS["error"],
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name=f"{Emojis.SERVER} Ticket Summary",
            value=f"**Type:** {ticket['type'].replace('-', ' ').title()}\n**Duration:** Open for <t:{int(datetime.datetime.now().timestamp())}:R>",
            inline=False
        )
        
        embed.set_footer(text="Thank you for using Blazing Ticket System!")
        
        await channel.send(embed=embed)
        
        # Send transcript to log
        log_channel = bot.get_channel(config["log_channel_id"])
        if log_channel:
            await log_channel.send(file=discord.File(transcript_file))
        
        os.remove(transcript_file)
        
        # Delete channel after delay
        await asyncio.sleep(5)
        await channel.delete()
        
        success_embed = discord.Embed(title=f"{Emojis.ANIMATED_YES} Success", description="Ticket closed successfully!", color=COLORS["success"])
        await interaction.response.send_message(embed=success_embed, ephemeral=True)
        
        # Enhanced log
        log_message = f"{Emojis.CHECK_NO} Ticket Closed\n**ID:** `{ticket_id}`\n**Closed By:** {interaction.user} ({interaction.user.id})\n**Type:** {ticket['type']}\n**User:** {ticket['user_id']}\n**Created At:** {ticket['created_at']}\n**Closed At:** {ticket['closed_at']}"
        await log_ticket_action(log_message)
    except Exception as e:
        embed = discord.Embed(
            title=f"{Emojis.CHECK_NO} Error",
            description=f"An error occurred while closing the ticket: {str(e)}",
            color=COLORS["error"]
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"Error in close_ticket_handler: {e}")

async def add_member_handler(interaction, ticket_id):
    try:
        staff_role = interaction.guild.get_role(config["staff_role_id"])
        if not staff_role or staff_role not in interaction.user.roles:
            embed = discord.Embed(title=f"{Emojis.CHECK_NO} Permission Denied", description="Only staff members can add members to tickets!", color=COLORS["error"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if ticket_id not in tickets_data["tickets"]:
            embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description="Ticket not found!", color=COLORS["error"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create modal for member input
        class AddMemberModal(Modal, title="Add Member to Ticket"):
            def __init__(self):
                super().__init__()
                self.member_id = TextInput(
                    label="Member ID or Mention",
                    placeholder="Enter the member's ID or @mention them",
                    required=True
                )
                self.add_item(self.member_id)
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    # Extract member ID
                    member_input = self.member_id.value
                    if member_input.startswith('<@') and member_input.endswith('>'):
                        member_id = int(member_input[2:-1].replace('!', ''))
                    else:
                        member_id = int(member_input)
                    
                    member = modal_interaction.guild.get_member(member_id)
                    if not member:
                        embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description="Member not found!", color=COLORS["error"])
                        await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                    
                    # Add member to ticket channel
                    ticket = tickets_data["tickets"][ticket_id]
                    channel = modal_interaction.guild.get_channel(ticket["channel_id"])
                    
                    await channel.set_permissions(member, view_channel=True, send_messages=True, read_message_history=True)
                    
                    embed = discord.Embed(
                        title=f"{Emojis.ANIMATED_YES} Member Added",
                        description=f"{member.mention} has been added to the ticket by {modal_interaction.user.mention}",
                        color=COLORS["success"]
                    )
                    await channel.send(embed=embed)
                    
                    success_embed = discord.Embed(title=f"{Emojis.ANIMATED_YES} Success", description=f"Added {member} to the ticket!", color=COLORS["success"])
                    await modal_interaction.response.send_message(embed=success_embed, ephemeral=True)
                    
                    # Enhanced log
                    log_message = f"{Emojis.VERIFY} Member Added to Ticket\n**ID:** `{ticket_id}`\n**Added Member:** {member} ({member.id})\n**By:** {modal_interaction.user} ({modal_interaction.user.id})\n**Type:** {ticket['type']}"
                    await log_ticket_action(log_message)
                    
                except ValueError:
                    embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description="Invalid member ID!", color=COLORS["error"])
                    await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                except Exception as sub_e:
                    embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred: {str(sub_e)}", color=COLORS["error"])
                    await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                    print(f"Error in AddMemberModal on_submit: {sub_e}")
        
        modal = AddMemberModal()
        await interaction.response.send_modal(modal)
    except Exception as e:
        embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred while opening add member modal: {str(e)}", color=COLORS["error"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"Error in add_member_handler: {e}")

async def remove_member_handler(interaction, ticket_id):
    try:
        staff_role = interaction.guild.get_role(config["staff_role_id"])
        if not staff_role or staff_role not in interaction.user.roles:
            embed = discord.Embed(title=f"{Emojis.CHECK_NO} Permission Denied", description="Only staff members can remove members from tickets!", color=COLORS["error"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if ticket_id not in tickets_data["tickets"]:
            embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description="Ticket not found!", color=COLORS["error"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create modal for member input
        class RemoveMemberModal(Modal, title="Remove Member from Ticket"):
            def __init__(self):
                super().__init__()
                self.member_id = TextInput(
                    label="Member ID or Mention",
                    placeholder="Enter the member's ID or @mention them",
                    required=True
                )
                self.add_item(self.member_id)
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    # Extract member ID
                    member_input = self.member_id.value
                    if member_input.startswith('<@') and member_input.endswith('>'):
                        member_id = int(member_input[2:-1].replace('!', ''))
                    else:
                        member_id = int(member_input)
                    
                    member = modal_interaction.guild.get_member(member_id)
                    if not member:
                        embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description="Member not found!", color=COLORS["error"])
                        await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                        return
                    
                    # Remove member from ticket channel
                    ticket = tickets_data["tickets"][ticket_id]
                    channel = modal_interaction.guild.get_channel(ticket["channel_id"])
                    
                    await channel.set_permissions(member, overwrite=None)  # Reset to default (hidden)
                    
                    embed = discord.Embed(
                        title=f"{Emojis.IGNORE} Member Removed",
                        description=f"{member.mention} has been removed from the ticket by {modal_interaction.user.mention}",
                        color=COLORS["warning"]
                    )
                    await channel.send(embed=embed)
                    
                    success_embed = discord.Embed(title=f"{Emojis.ANIMATED_YES} Success", description=f"Removed {member} from the ticket!", color=COLORS["success"])
                    await modal_interaction.response.send_message(embed=success_embed, ephemeral=True)
                    
                    # Enhanced log
                    log_message = f"{Emojis.IGNORE} Member Removed from Ticket\n**ID:** `{ticket_id}`\n**Removed Member:** {member} ({member.id})\n**By:** {modal_interaction.user} ({modal_interaction.user.id})\n**Type:** {ticket['type']}"
                    await log_ticket_action(log_message)
                    
                except ValueError:
                    embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description="Invalid member ID!", color=COLORS["error"])
                    await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                except Exception as sub_e:
                    embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred: {str(sub_e)}", color=COLORS["error"])
                    await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                    print(f"Error in RemoveMemberModal on_submit: {sub_e}")
        
        modal = RemoveMemberModal()
        await interaction.response.send_modal(modal)
    except Exception as e:
        embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred while opening remove member modal: {str(e)}", color=COLORS["error"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"Error in remove_member_handler: {e}")

async def rename_ticket_handler(interaction, ticket_id):
    try:
        if ticket_id not in tickets_data["tickets"]:
            embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description="Ticket not found!", color=COLORS["error"])
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        class RenameModal(Modal, title="Rename Ticket"):
            def __init__(self):
                super().__init__()
                self.new_name = TextInput(
                    label="New Ticket Name",
                    placeholder="Enter a new name for this ticket...",
                    required=True,
                    max_length=100
                )
                self.add_item(self.new_name)
            
            async def on_submit(self, modal_interaction: discord.Interaction):
                try:
                    ticket = tickets_data["tickets"][ticket_id]
                    channel = modal_interaction.guild.get_channel(ticket["channel_id"])
                    
                    await channel.edit(name=self.new_name.value)
                    embed = discord.Embed(
                        title=f"{Emojis.VERIFY} Ticket Renamed",
                        description=f"Ticket renamed to `{self.new_name.value}` by {modal_interaction.user.mention}",
                        color=COLORS["success"]
                    )
                    await channel.send(embed=embed)
                    
                    success_embed = discord.Embed(title=f"{Emojis.ANIMATED_YES} Success", description="Ticket renamed successfully!", color=COLORS["success"])
                    await modal_interaction.response.send_message(embed=success_embed, ephemeral=True)
                    
                    # Enhanced log
                    log_message = f"Ticket Renamed\n**ID:** `{ticket_id}`\n**New Name:** {self.new_name.value}\n**By:** {modal_interaction.user} ({modal_interaction.user.id})\n**Type:** {ticket['type']}"
                    await log_ticket_action(log_message)
                except discord.HTTPException as http_e:
                    embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"Failed to rename ticket: {str(http_e)}", color=COLORS["error"])
                    await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                except Exception as sub_e:
                    embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred: {str(sub_e)}", color=COLORS["error"])
                    await modal_interaction.response.send_message(embed=embed, ephemeral=True)
                    print(f"Error in RenameModal on_submit: {sub_e}")
        
        modal = RenameModal()
        await interaction.response.send_modal(modal)
    except Exception as e:
        embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred while opening rename modal: {str(e)}", color=COLORS["error"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"Error in rename_ticket_handler: {e}")

# Logging function - upgraded to use embed with more structure
async def log_ticket_action(message):
    try:
        if config["log_channel_id"]:
            channel = bot.get_channel(config["log_channel_id"])
            if channel:
                embed = discord.Embed(
                    description=message,
                    color=COLORS["info"],
                    timestamp=datetime.datetime.now()
                )
                embed.set_footer(text="Blazing Ticket Log")
                await channel.send(embed=embed)
    except Exception as e:
        print(f"Error in log_ticket_action: {e}")

# Status watching task
@tasks.loop(minutes=1)
async def status_task():
    try:
        open_tickets = len([t for t in tickets_data["tickets"].values() if t["status"] == "open"])
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{open_tickets} open tickets | /help"
        ))
    except Exception as e:
        print(f"Error in status_task: {e}")

# Bot events
@bot.event
async def on_ready():
    global start_time
    start_time = datetime.datetime.now()
    print(f'{bot.user} is now online!')
    print(f'Serving {len(bot.guilds)} guild(s)')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    
    status_task.start()

@bot.event
async def on_guild_join(guild):
    try:
        # Create default category for tickets
        category = await guild.create_category("Tickets")
        config["ticket_category_id"] = category.id
        
        # Create log channel
        log_channel = await guild.create_text_channel("ticket-logs", category=category)
        config["log_channel_id"] = log_channel.id
        
        save_config(config)
        
        # Send welcome message
        embed = discord.Embed(
            title=f"{Emojis.DRAGON} Blazing Ticket System",
            description="Thank you for adding Blazing Ticket System to your server!",
            color=COLORS["primary"]
        )
        embed.add_field(name=f"{Emojis.VERIFY} Quick Setup", value="Use `/setup` to configure the bot", inline=False)
        embed.add_field(name=f"{Emojis.SUPPORT} Create Panel", value="Use `/panel` to create the ticket panel", inline=False)
        
        # Find a channel to send welcome message
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(embed=embed)
                break
        
        print(f"Joined {guild.name}, setup complete!")
    except Exception as e:
        print(f"Error in on_guild_join: {e}")

# SLASH COMMANDS (Admin Only for some)
@bot.tree.command(name="panel", description="Create the ticket panel")
@discord.app_commands.checks.has_permissions(administrator=True)
async def panel(interaction: discord.Interaction):
    try:
        if not config["ticket_category_id"] or not config["log_channel_id"]:
            embed = discord.Embed(
                title=f"{Emojis.WARNING} Setup Required",
                description="Please run `/setup` first to configure the ticket system before creating the panel!",
                color=COLORS["warning"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"{Emojis.DRAGON} Blazing Ticket System",
            description=f"{Emojis.VERIFY} **Ticket System Activated!**\n\nChoose an option from the dropdown menu below to create a ticket.",
            color=COLORS["primary"],
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name=f"{Emojis.SUPPORT} Ticket Types",
            value=f"""{Emojis.MODS} **Staff Report** - Report a staff member
{Emojis.BUYER} **Buy Services** - Purchase members, boosts, hosting
{Emojis.SUPPORT} **Community Support** - Get help with community issues  
{Emojis.WELCOMER} **Apply for Staff** - Apply to become staff member
{Emojis.IGNORE} **Other** - Any other inquiries or issues""",
            inline=False
        )
        
        embed.add_field(
            name=f"{Emojis.WARNING} Rules & Guidelines",
            value=f"{Emojis.DOT} Be clear and concise with your issue\n{Emojis.DOT} Don't ping support members directly\n{Emojis.DOT} Be patient and respectful\n{Emojis.DOT} No spam or fun tickets",
            inline=False
        )
        
        embed.set_footer(text="Blazing Ticket System • Support Experience")
        
        view = View(timeout=None)
        view.add_item(TicketDropdown())
        
        await interaction.response.send_message(embed=embed, view=view)
        
        # Save panel channel for future reference
        config["panel_channel_id"] = interaction.channel.id
        save_config(config)
    except Exception as e:
        embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred: {str(e)}", color=COLORS["error"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"Error in panel command: {e}")

@bot.tree.command(name="setup", description="Setup the ticket system")
@discord.app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction, staff_role: discord.Role = None, support_team_role: discord.Role = None):
    try:
        # Create ticket category if not exists
        category = interaction.guild.get_channel(config["ticket_category_id"])
        if not category:
            category = await interaction.guild.create_category("Tickets")
            config["ticket_category_id"] = category.id
        
        # Create log channel if not exists
        log_channel = interaction.guild.get_channel(config["log_channel_id"])
        if not log_channel:
            log_channel = await interaction.guild.create_text_channel("ticket-logs", category=category)
            config["log_channel_id"] = log_channel.id
        
        # Update roles
        if staff_role:
            config["staff_role_id"] = staff_role.id
        if support_team_role:
            config["support_team_role_id"] = support_team_role.id
        
        save_config(config)
        
        embed = discord.Embed(
            title=f"{Emojis.VERIFY} Setup Complete",
            description=f"{Emojis.DRAGON} **Blazing Ticket System** has been configured successfully!",
            color=COLORS["primary"]
        )
        
        embed.add_field(name=f"{Emojis.INFO} Ticket Category", value=category.mention, inline=True)
        embed.add_field(name=f"{Emojis.SERVER} Log Channel", value=log_channel.mention, inline=True)
        if staff_role:
            embed.add_field(name=f"{Emojis.MODS} Staff Role", value=staff_role.mention, inline=True)
        if support_team_role:
            embed.add_field(name=f"{Emojis.SUPPORT} Support Team", value=support_team_role.mention, inline=True)
        
        embed.add_field(
            name=f"Next Steps", 
            value="Use `/panel` to create the ticket panel in your desired channel!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred: {str(e)}", color=COLORS["error"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"Error in setup command: {e}")

@bot.tree.command(name="ticket_stats", description="View ticket statistics")
@discord.app_commands.checks.has_permissions(administrator=True)
async def ticket_stats(interaction: discord.Interaction):
    try:
        open_tickets = len([t for t in tickets_data["tickets"].values() if t["status"] == "open"])
        closed_tickets = len([t for t in tickets_data["tickets"].values() if t["status"] == "closed"])
        total_tickets = len(tickets_data["tickets"])
        
        embed = discord.Embed(
            title=f"{Emojis.SERVER} Ticket Statistics",
            color=COLORS["info"],
            timestamp=datetime.datetime.now()
        )
        
        # Main stats with styling
        embed.add_field(name=f"{Emojis.DRAGON} Open Tickets", value=f"**{open_tickets}**", inline=True)
        embed.add_field(name=f"{Emojis.CHECK_NO} Closed Tickets", value=f"**{closed_tickets}**", inline=True)
        embed.add_field(name=f"{Emojis.SERVER} Total Tickets", value=f"**{total_tickets}**", inline=True)
        
        if tickets_data["tickets"]:
            # Get most common ticket type
            types = {}
            for ticket in tickets_data["tickets"].values():
                types[ticket["type"]] = types.get(ticket["type"], 0) + 1
            
            if types:
                most_common = max(types.items(), key=lambda x: x[1])
                embed.add_field(name=f"{Emojis.INFO} Most Common Type", value=most_common[0].replace("-", " ").title(), inline=True)
                embed.add_field(name=f"{Emojis.LOADING} Count", value=most_common[1], inline=True)
        
        # System status
        status_color = COLORS["success"] if open_tickets < 10 else COLORS["warning"]
        status_emoji = Emojis.VERIFY if open_tickets < 10 else Emojis.WARNING
        
        embed.add_field(
            name=f"{status_emoji} System Status", 
            value=f"**{'Optimal' if open_tickets < 10 else 'Busy'}**\nSystem running smoothly!",
            inline=False
        )
        
        embed.set_footer(text="Blazing Ticket System • Analytics")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred: {str(e)}", color=COLORS["error"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"Error in ticket_stats command: {e}")

@bot.tree.command(name="ping", description="Check bot status")
async def ping(interaction: discord.Interaction):
    try:
        latency = round(bot.latency * 1000)
        
        # Determine status based on latency
        if latency < 100:
            status_emoji = Emojis.ANIMATED_YES
            status = "Excellent"
            color = COLORS["primary"]
        elif latency < 200:
            status_emoji = Emojis.WARNING
            status = "Good"
            color = COLORS["warning"]
        else:
            status_emoji = Emojis.CHECK_NO
            status = "Slow"
            color = COLORS["error"]
        
        embed = discord.Embed(
            title=f"{Emojis.INFO} Bot Status",
            color=color,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(name=f"{Emojis.SETTINGS} WebSocket Latency", value=f"**{latency}ms**", inline=True)
        embed.add_field(name=f"{Emojis.INFO} Connection Status", value=status, inline=True)
        embed.add_field(name=f"{Emojis.DRAGON} Open Tickets", value=f"**{len([t for t in tickets_data['tickets'].values() if t['status'] == 'open'])}**", inline=True)
        embed.add_field(name=f"{Emojis.SERVER} Servers", value=f"**{len(bot.guilds)}**", inline=True)
        embed.add_field(name=f"{Emojis.LOADING} Uptime", value=f"<t:{int(start_time.timestamp())}:R>", inline=True)
        
        embed.set_footer(text="Blazing Ticket System • Monitoring")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred: {str(e)}", color=COLORS["error"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"Error in ping command: {e}")

@bot.tree.command(name="help", description="Show help menu")
async def help_command(interaction: discord.Interaction):
    try:
        embed = discord.Embed(
            title=f"{Emojis.DRAGON} Ticket System Help",
            description=f"{Emojis.VERIFY} Everything you need to know about our ticket system!",
            color=COLORS["primary"]
        )
        
        embed.add_field(
            name=f"{Emojis.SUPPORT} For Users",
            value=f"{Emojis.DOT} Use the ticket panel\n{Emojis.DOT} Choose the correct ticket type\n{Emojis.DOT} Describe your issue clearly\n{Emojis.DOT} Be patient for responses\n{Emojis.DOT} Use ticket controls when needed",
            inline=True
        )
        
        embed.add_field(
            name=f"{Emojis.MODS} For Staff", 
            value=f"{Emojis.DOT} Monitor ticket channels\n{Emojis.DOT} Use control buttons to manage\n{Emojis.DOT} Close tickets when resolved\n{Emojis.DOT} Add/remove members as needed\n{Emojis.DOT} Rename tickets for organization",
            inline=True
        )
        
        embed.add_field(
            name=f"{Emojis.SETTINGS} Commands",
            value=f"{Emojis.DRAGON} `/panel` - Create panel\n{Emojis.VERIFY} `/setup` - Configure system\n{Emojis.SERVER} `/ticket_stats` - View analytics\n{Emojis.LOADING} `/ping` - Check status\n{Emojis.SUPPORT} `/help` - This menu",
            inline=False
        )
        
        embed.set_footer(text="Need more help? Contact system administrators")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(title=f"{Emojis.CHECK_NO} Error", description=f"An error occurred: {str(e)}", color=COLORS["error"])
        await interaction.response.send_message(embed=embed, ephemeral=True)
        print(f"Error in help command: {e}")

# Error handling for slash commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    try:
        if isinstance(error, discord.app_commands.MissingPermissions):
            embed = discord.Embed(
                title=f"{Emojis.CHECK_NO} Permission Denied", 
                description="You need administrator permissions to use this command!",
                color=COLORS["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title=f"{Emojis.CHECK_NO} Error", 
                description=f"An unexpected error occurred: {str(error)}",
                color=COLORS["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            print(f"Slash command error: {error}")
    except Exception as e:
        print(f"Error in on_app_command_error: {e}")

# Run the bot
if __name__ == "__main__":
    # Load token from token.txt
    try:
        with open('token.txt', 'r') as f:
            token = f.read().strip()
    except FileNotFoundError:
        print("No token.txt file found! Please create token.txt with your bot token.")
        exit(1)
    
    bot.run(token)
