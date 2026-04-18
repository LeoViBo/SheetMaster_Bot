import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os


class SheetMasterBot(commands.Bot):
    def __init__(self) -> None:
        intents: discord.Intents = discord.Intents.all()
        super().__init__(
            command_prefix="!",
            intents=intents)

    async def setup_hook(self) -> None:
        filename: str
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                print(f"Loading {filename}")
                await self.load_extension(f"cogs.{filename[:-3]}")
        # Modo temporário é necessário colocar o server ID para o bot funcionar instantaneamente
        guild: discord.Object = discord.Object(id=int(os.getenv("SERVER_ID")))
        await self.tree.sync(guild=guild)

    async def on_ready(self) -> None:
        print(f"Login de {self.user}")


load_dotenv()
if not os.path.exists(".env"):
    print("Crie um arquivo '.env'")
    print("Coloque 'DISCORD_TOKEN=' no '.env' e preencha com o seu token")
    print("Coloque 'SERVER_ID=' no '.env' e preencha com o codigo do servidor onde o bot foi colocado")
    exit()

token: str | None = os.getenv("DISCORD_TOKEN")
server_id: str | None = os.getenv("SERVER_ID")
if not token:
    print("Coloque 'DISCORD_TOKEN=' no '.env' e preencha com o seu token")
    exit()
if not server_id:
    print("Coloque 'SERVER_ID=' no '.env' e preencha com o codigo do servidor onde o bot foi colocado")
    exit()

bot: SheetMasterBot = SheetMasterBot()

handler: logging.FileHandler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
bot.run(token, log_handler=handler, log_level=logging.INFO)