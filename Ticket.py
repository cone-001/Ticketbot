import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ui import View, Select, Modal, TextInput
import random
import asyncio

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

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
    def __init__(self, category):
        super().__init__(title=f"고객센터")
        self.category = category
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
        channel_name = f"{self.category}-{random_number}"

        category = discord.utils.get(interaction.guild.categories, name='티켓')
        if category is None:
            category = await interaction.guild.create_category(name='티켓')

        admin_role_id = int(os.getenv('ADMIN_ROLE_ID'))
        manager_role_id = int(os.getenv('MANAGER_ROLE_ID'))

        admin_role = interaction.guild.get_role(admin_role_id)
        manager_role = interaction.guild.get_role(manager_role_id)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
        }

        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True)
        if manager_role:
            overwrites[manager_role] = discord.PermissionOverwrite(read_messages=True)

        channel = await interaction.guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )

        await channel.send(f"{interaction.user.mention} 님의 {self.category} " f"문제:\n{description}")
        await interaction.response.send_message(
            f"채널이 생성되었습니다: {channel.mention}", ephemeral=True
        )

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='🚨버그 신고', value='🚨버그 신고'),
            discord.SelectOption(label='✅문의 상황', value='✅문의 상황'),
            discord.SelectOption(label='⚙️개발 요청', value='⚙️개발 요청'),
        ]
        super().__init__(placeholder='문의 유형을 선택해 주세요', options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        selected_category = self.values[0]
        await interaction.response.send_modal(TicketModal(selected_category))

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    channel_id = int(os.getenv('CHANNEL_ID'))
    channel = bot.get_channel(channel_id)

    if channel is not None:
        await channel.send(
            embed=get_ticket_embed(),
            view=TicketView()
        )
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

bot.run(os.getenv('BOT_TOKEN'))