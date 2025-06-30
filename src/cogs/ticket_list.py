import discord
from discord.ext import commands
import sqlite3

ALLOWED_USER_IDS = [1384859365349003264, 1069364135084687391]

class TicketList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Connect to the database
        self.conn = sqlite3.connect('data/moderation.db')
        self.cursor = self.conn.cursor()

        # Create a table to store ticket information if it doesn't exist
        # Removed DROP TABLE to keep logs persistent
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ticket_logs (
                channel_id INTEGER PRIMARY KEY,
                creator_id INTEGER,
                open_time TEXT,
                closed_time TEXT,
                closer_id INTEGER
            )
        ''')
        self.conn.commit()


    @commands.command(name="list_tickets")
    @commands.check(lambda ctx: ctx.author.id in ALLOWED_USER_IDS)
    async def list_tickets(self, ctx):
        """Lists all created and closed tickets."""

        self.cursor.execute('SELECT channel_id, creator_id, open_time, closed_time, closer_id FROM ticket_logs')
        results = self.cursor.fetchall()

        if not results:
            await ctx.send("Nenhum ticket encontrado.")
            return

        message = "Lista de Tickets:\n"
        for channel_id, creator_id, open_time, closed_time, closer_id in results:
            try:
                creator = await self.bot.fetch_user(creator_id)
                creator_name = creator.name
            except discord.NotFound:
                creator_name = "Usuário Desconhecido"

            channel_mention = f"<#{channel_id}>"

            if closed_time:
                try:
                    closer = await self.bot.fetch_user(closer_id)
                    closer_name = closer.name
                except discord.NotFound:
                    closer_name = "Usuário Desconhecido"
                status = f"Fechado por {closer_name} em {closed_time}"
            else:
                status = "Aberto"

            message += f"Ticket no canal {channel_mention} | Aberto por: {creator_name} em {open_time} | Status: {status}\n"

        # Splitting message into chunks if it's too long
        # Discord message limit is 2000 characters
        chunks = [message[i:i+1900] for i in range(0, len(message), 1900)]
        for chunk in chunks:
            await ctx.send(chunk)

    @commands.command(name="clear_tickets")
    @commands.check(lambda ctx: ctx.author.id in ALLOWED_USER_IDS)
    async def clear_tickets(self, ctx):
        """Clears all ticket data from the database."""
        self.cursor.execute('DELETE FROM ticket_logs')
        self.conn.commit()
        await ctx.send("Todos os dados de tickets foram limpos.")

async def setup(bot):
    await bot.add_cog(TicketList(bot))
