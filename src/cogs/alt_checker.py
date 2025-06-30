import discord
from discord.ext import commands
import difflib

class AltChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def check_alts(self, ctx):
        await ctx.send("Verificando nomes de usuário parecidos...")

        guild = ctx.guild
        if not guild:
            await ctx.send("Este comando só pode ser usado em um servidor.")
            return

        members = guild.members
        usernames = [member.name for member in members]
        similar_names = {}

        # Definir um limite de similaridade (ajuste conforme necessário)
        # Um valor mais próximo de 1.0 significa uma correspondência mais exata
        similarity_threshold = 0.8 # Ajuste este valor

        for name in usernames:
            # Encontra nomes parecidos, excluindo o próprio nome
            matches = difflib.get_close_matches(name, usernames, n=10, cutoff=similarity_threshold)

            # Remove o nome original da lista de correspondências (se estiver presente)
            matches = [match for match in matches if match != name]

            if matches:
                # Armazena as correspondências encontradas para este nome
                # Evitamos duplicatas garantindo que o nome original é sempre o 'menor' na tupla (name, match)
                for match in matches:
                    pair = tuple(sorted((name, match)))
                    similar_names[pair] = True # Usamos um dicionário para garantir pares únicos

        if similar_names:
            report = "Nomes de usuário parecidos encontrados:\n"
            for name1, name2 in similar_names.keys():
                report += f"- `{name1}` e `{name2}`\n"

            # Divide a mensagem em partes menores se for muito longa
            if len(report) > 2000:
                for i in range(0, len(report), 2000):
                    await ctx.send(report[i:i+2000])
            else:
                await ctx.send(report)

        else:
            await ctx.send("Nenhum nome de usuário parecido encontrado com o limite atual.")

async def setup(bot):
    await bot.add_cog(AltChecker(bot))
