import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import random
import asyncio

load_dotenv()

REQUIRED_ENV_VARS = (
    "BOT_TOKEN",
    "ADMIN_ROLE_ID",
    "MANAGER_ROLE_ID",
    "CHANNEL_ID",
    "CATEGORY_ID",
)


def get_required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f".env에 {name} 값이 필요합니다.")
    return value


def get_required_int_env(name):
    value = get_required_env(name)
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f".env의 {name} 값은 숫자 ID여야 합니다.") from exc


def validate_env():
    get_required_env("BOT_TOKEN")
    for name in ("ADMIN_ROLE_ID", "MANAGER_ROLE_ID", "CHANNEL_ID", "CATEGORY_ID"):
        get_required_int_env(name)


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

TICKET_TYPES = {
    "bug": "🚨버그 신고",
    "status": "✅문의 상황",
    "dev": "⚙️개발 요청",
}

def get_ticket_embed():
    embed = discord.Embed(
        title="고객센터 안내",
        description=(
            "**1. 카테고리를 선택하면 관리자만 볼 수 있는 채널이 생성됩니다.**\n"
            "**2. 이 채널은 디스코드와 마인크래프트 버그에만 관련된 내용으로만 운영됩니다.**\n"
            "**3. 불필요한 사유로 방을 생성할 경우 제재 처리될 수 있습니다.**\n\n"
        ),
        color=discord.Color.red()
    )
    return embed

class TicketModal(Modal):
    def __init__(self, ticket_type):
        super().__init__(title=f"고객센터")
        self.ticket_type = ticket_type
        self.category_label = TICKET_TYPES[ticket_type]
        self.add_item(TextInput(
            label="문제를 설명해주세요",
            style=discord.TextStyle.paragraph,
            required=True,
            min_length=5,
            max_length=50
        ))

    async def on_submit(self, interaction: discord.Interaction):
        description = self.children[0].value
        random_number = random.randint(1000, 9999)
        channel_name = f"ticket-{self.ticket_type}-{random_number}"

        category_id = get_required_int_env('CATEGORY_ID')
        category = interaction.guild.get_channel(category_id)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message(
                ".env의 CATEGORY_ID에 해당하는 카테고리를 찾을 수 없습니다.",
                ephemeral=True
            )
            return

        admin_role_id = get_required_int_env('ADMIN_ROLE_ID')
        manager_role_id = get_required_int_env('MANAGER_ROLE_ID')

        admin_role = interaction.guild.get_role(admin_role_id)
        manager_role = interaction.guild.get_role(manager_role_id)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        if manager_role:
            overwrites[manager_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        await channel.send(f"{interaction.user.mention} 님의 {self.category_label} " f"문제:\n{description}")
        await interaction.response.send_message(
            f"채널이 생성되었습니다: {channel.mention}", ephemeral=True
        )

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='🚨버그 신고', value='bug'),
            discord.SelectOption(label='✅문의 상황', value='status'),
            discord.SelectOption(label='⚙️개발 요청', value='dev'),
        ]
        super().__init__(
            placeholder='문의 유형을 선택해 주세요',
            options=options,
            min_values=1,
            max_values=1,
            custom_id='ticketbot:ticket_select'
        )

    async def callback(self, interaction: discord.Interaction):
        selected_category = self.values[0]
        await interaction.response.send_modal(TicketModal(selected_category))

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.event
async def setup_hook():
    bot.add_view(TicketView())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    channel_id = get_required_int_env('CHANNEL_ID')
    channel = bot.get_channel(channel_id)

    if channel is not None:
        try:
            async for message in channel.history(limit=25):
                if message.author == bot.user and message.embeds:
                    if message.embeds[0].title == "고객센터 안내":
                        return
        except discord.Forbidden:
            print("채널 기록을 읽을 권한이 없어 안내 메시지 중복 여부를 확인할 수 없습니다.")

        await channel.send(embed=get_ticket_embed(), view=TicketView())
    else:
        print("채널을 찾을 수 없습니다.")

@bot.tree.command(name="문제_해결", description="생성된 티켓 채널을 삭제합니다.")
async def delete_ticket(interaction: discord.Interaction):
    if interaction.channel.category and interaction.channel.category.name == '티켓':
        await interaction.response.send_message("티켓 채널이 5초 후에 삭제됩니다.", ephemeral=True)
        await asyncio.sleep(5)
        await interaction.channel.delete()
    else:
        await interaction.response.send_message("이 명령어는 티켓 채널에서만 사용할 수 있습니다.", ephemeral=True)

validate_env()
bot.run(get_required_env('BOT_TOKEN'))