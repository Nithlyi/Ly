import discord
from discord.ext import commands
import discord.ui
import sqlite3
from datetime import datetime

MOD_ROLES = []
ADMIN_ROLES = []

class ConfirmCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.button(label="Sim", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Fechando ticket...", ephemeral=True)
        channel_id = interaction.channel.id
        closer_id = interaction.user.id
        close_time = datetime.now().isoformat()

        try:
            conn = sqlite3.connect('data/moderation.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE ticket_logs SET closed_time = ?, closer_id = ? WHERE channel_id = ?", (close_time, closer_id, channel_id))
            conn.commit()
        except Exception as e:
            print(f"Erro ao atualizar o ticket no banco de dados: {e}")
        finally:
            if conn:
                conn.close()

        await interaction.channel.delete()

    @discord.ui.button(label="Não", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Fechamento cancelado.", ephemeral=True)
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(content="Fechamento do ticket cancelado.", view=self)

class TicketActionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.red)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Tem certeza que deseja fechar este ticket?", view=ConfirmCloseView(), ephemeral=True)

class SupportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Denúncia", style=discord.ButtonStyle.red, custom_id="support_denuncia")
    async def denuncia_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "denuncia")

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        await interaction.response.send_message(f"Criando ticket de {ticket_type}...", ephemeral=True)
        guild = interaction.guild
        member = interaction.user
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        for role_id in MOD_ROLES + ADMIN_ROLES:
            role = guild.get_role(role_id)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")
        channel_name = f"ticket-{ticket_type}-{member.name}".lower().replace(" ", "-")
        ticket_channel = await guild.create_text_channel(
            channel_name,
            overwrites=overwrites,
            category=category
        )
        embed = discord.Embed(
            title=f"Ticket de {ticket_type.capitalize()}",
            description=f"Olá {member.mention}, bem-vindo(a) ao seu ticket de {ticket_type}. Descreva seu problema ou solicitação aqui.\nUm membro da equipe de suporte logo estará com você.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(content=f"{member.mention}", embed=embed, view=TicketActionsView())

        try:
            conn = sqlite3.connect('data/moderation.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ticket_logs (channel_id, creator_id, open_time, closed_time, closer_id) VALUES (?, ?, ?, NULL, NULL)", (ticket_channel.id, member.id, datetime.now().isoformat()))
            conn.commit()
        except Exception as e:
            print(f"Erro ao salvar o ticket no banco de dados: {e}")
        finally:
            if conn:
                conn.close()

        await interaction.followup.send(f"Seu ticket de {ticket_type} foi criado em {ticket_channel.mention}", ephemeral=True)

class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_view(SupportView())

    @commands.command(name="setup_support")
    @commands.check(lambda ctx: ctx.author.guild_permissions.administrator or any(role.id in MOD_ROLES for role in ctx.author.roles))
    async def setup_support_command(self, ctx):
        embed = discord.Embed(
            title="✧༺✦✮✦ Tickets  !✦✮",
            description=(
                "˙ .ᶻ 𝗓 𐰁 Caso precise contatar o suporte ou fazer uma denúncia, clique no botão abaixo: .˙—"
            ),
            color=0xa2a6ff
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1386861605228253216/1389353699054452947/IMG_2741.jpg?ex=68644ff6&is=6862fe76&hm=1dfccfdb8058dfd4ebd8916ecc8b5852376f5fc35079afbb5c0210e6b200479a&")
        await ctx.send(embed=embed, view=SupportView())

async def setup(bot):
    await bot.add_cog(Support(bot))
