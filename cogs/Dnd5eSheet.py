from discord.ext import commands
from discord import app_commands
import discord
import random
import os
import json


# ==== COMBAT UI ====
class CombatView(discord.ui.View):

    def __init__(self, cog: "Sheet", user_id: str, damage: int) -> None:
        super().__init__()
        self.cog: "Sheet" = cog
        self.user_id: str = user_id
        self.damage: int = damage

    def get_sheet(self) -> dict:
        return self.cog.data[self.user_id]

    @discord.ui.button(label="Full Damage", style=discord.ButtonStyle.red)
    async def full_damage(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:

        sheet: dict = self.get_sheet()
        self.cog.take_damage_direct(sheet, self.damage)

        await interaction.response.send_message("Full damage applied!", ephemeral=True)

    @discord.ui.button(label="Half Damage", style=discord.ButtonStyle.blurple)
    async def half_damage(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:

        sheet: dict = self.get_sheet()
        self.cog.take_damage_direct(sheet, self.damage // 2)

        await interaction.response.send_message("Half damage applied!", ephemeral=True)

    @discord.ui.button(label="Heal", style=discord.ButtonStyle.green)
    async def heal(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:

        sheet: dict = self.get_sheet()
        sheet["current hp"] += self.damage

        await interaction.response.send_message("Healed!", ephemeral=True)

    @discord.ui.button(label="Temp HP", style=discord.ButtonStyle.gray)
    async def temp_hp(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:

        sheet: dict = self.get_sheet()
        sheet["temporary hp"] += self.damage

        await interaction.response.send_message("Temp HP added!", ephemeral=True)


# ==== SHEET CLASS ====
class Sheet(commands.Cog):

    # region ==== SETUP ====
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.data: dict[str, dict] = {}
        self.load_data()

    def load_data(self) -> None:
        if os.path.exists("data/data.json"):
            with open("data/data.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def save_data(self) -> None:
        os.makedirs("data", exist_ok=True)
        with open("data/data.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    # endregion

    # region ==== FUNCTIONS ====

    # --- ATRIBUTE MODIFIER
    def get_modifier(self, attribute_value: int) -> int:
        return (attribute_value - 10) // 2

    # --- UPDATE SKILLS
    def update_skills(self, sheet: dict) -> None:
        attribute: dict[str, int] = sheet["attribute"]
        prof_bonus: int = sheet["proficiency bonus"]

        for skill_name, skill_data in sheet["skills"].items():
            attr: str = skill_data["attr"]
            base_mod: int = self.get_modifier(attribute[attr])

            if skill_data["proficient"]:
                total: int = base_mod + prof_bonus
            else:
                total: int = base_mod

            skill_data["mod"] = total

    # --- CHECK IF PLAYER HAS SHEET
    async def has_sheet(self, interaction: discord.Interaction) -> dict | None:
        user_id: str = str(interaction.user.id)
        if user_id not in self.data:
            await self.safe_send(interaction, "You need to create a sheet first!")
            return None
        return self.data[user_id]

    # --- TAKE DAMAGE CALCULATION
    def take_damage_direct(self, sheet: dict, amount: int) -> None:

        if sheet["temporary hp"] > 0:
            if amount <= sheet["temporary hp"]:
                sheet["temporary hp"] -= amount
                return
            else:
                amount -= sheet["temporary hp"]
                sheet["temporary hp"] = 0

        sheet["current hp"] = max(0, sheet["current hp"] - amount)
        self.save_data()

    # --- SAFE SEND A MESSAGE
    async def safe_send(self, interaction: discord.Interaction, message: str, ephemeral: bool = True) -> None:
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=ephemeral)
            else:
                await interaction.response.send_message(message, ephemeral=ephemeral)
        except discord.errors.HTTPException as e:
            print(f"[safe_send] Erro ao responder interaction: {e}")

    # --- CAPTURE ERRORS IN SLASH COMANDS
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        print(f"[ERROR] Command '{interaction.command.name}' failed: {error}")
        await self.safe_send(interaction, f"An error occurred: `{error}`")

    # endregion

    # region ==== SHEET ====

    # --- CREATE SHEET
    @app_commands.command(name="create_sheet", description="Create a new cheet")
    async def create_sheet(self, interaction: discord.Interaction,
                           char_name: str,
                           char_class: str,
                           race: str,
                           background: str,
                           strenght: int,
                           dexterity: int,
                           constitution: int,
                           inteligence: int,
                           wisdom: int,
                           charisma: int) -> None:

        user_id: str = str(interaction.user.id)
        if user_id in self.data:
            await self.safe_send(interaction, "You already have a sheet!")
            return

        self.data[user_id] = {
            "name": char_name,
            "class": char_class,
            "race": race,
            "background": background,
            "level": 1,
            "max hp": 10,
            "current hp": 10,
            "temporary hp": 0,
            "armor class": 10,
            "initiative bonus": self.get_modifier(dexterity),
            "speed": 30,
            "attribute": {
                "STR": strenght,
                "DEX": dexterity,
                "CON": constitution,
                "INT": inteligence,
                "WIS": wisdom,
                "CHA": charisma
            },
            "proficiency bonus": 2,
            "skills": {
                "Strenght Saving Throw":     {"attr": "STR", "mod": 0, "proficient": False},
                "Dexterity Saving Throw":    {"attr": "DEX", "mod": 0, "proficient": False},
                "Constitution Saving Throw": {"attr": "CON", "mod": 0, "proficient": False},
                "Inteligence Saving Throw":  {"attr": "INT", "mod": 0, "proficient": False},
                "Wisdom Saving Throw":       {"attr": "WIS", "mod": 0, "proficient": False},
                "Charisma Saving Throw":     {"attr": "CHA", "mod": 0, "proficient": False},
                "Acrobatics":      {"attr": "DEX", "mod": 0, "proficient": False},
                "Animal Handling": {"attr": "WIS", "mod": 0, "proficient": False},
                "Arcana":          {"attr": "INT", "mod": 0, "proficient": False},
                "Athletics":       {"attr": "STR", "mod": 0, "proficient": False},
                "History":         {"attr": "INT", "mod": 0, "proficient": False},
                "Insight":         {"attr": "WIS", "mod": 0, "proficient": False},
                "Intimidation":    {"attr": "CHA", "mod": 0, "proficient": False},
                "Investigation":   {"attr": "INT", "mod": 0, "proficient": False},
                "Medicine":        {"attr": "WIS", "mod": 0, "proficient": False},
                "Nature":          {"attr": "INT", "mod": 0, "proficient": False},
                "Perception":      {"attr": "WIS", "mod": 0, "proficient": False},
                "Performance":     {"attr": "CHA", "mod": 0, "proficient": False},
                "Persuasion":      {"attr": "CHA", "mod": 0, "proficient": False},
                "Religion":        {"attr": "INT", "mod": 0, "proficient": False},
                "Sleight of Hand": {"attr": "DEX", "mod": 0, "proficient": False},
                "Stealth":         {"attr": "DEX", "mod": 0, "proficient": False},
                "Survival":        {"attr": "WIS", "mod": 0, "proficient": False}
            },
            "death saves": {
                "success": 0,
                "failure": 0
            },
            "other proficiencies": [],
            "abilities": [],
            "traits": [],
            "inventory": [],
        }

        self.update_skills(self.data[user_id])
        self.save_data()

        await self.safe_send(interaction, f"{char_name} was created!", ephemeral=False)

    # --- SHOW SHEET
    @app_commands.command(name="show_sheet", description="Show your character sheet")
    async def show_sheet(self, interaction: discord.Interaction) -> None:

        sheet: dict | None = await self.has_sheet(interaction)
        if not sheet:
            return

        # Header
        hp_ui: str = (f"{sheet['current hp'] + sheet['temporary hp']} "
                      f"({sheet['current hp']}+{sheet['temporary hp']})"
                      if sheet["temporary hp"] > 0
                      else str(sheet["current hp"]))

        embed: discord.Embed = discord.Embed(
            title=f"{sheet['name']}",
            description=f"Level {sheet['level']} • {sheet['race']} • {sheet['class']}\n"
                        f" -----------------===----------------- \n"
                        f"HP: {hp_ui} • AC[{sheet['armor class']}] • Speed[{sheet['speed']}] • Initiative[{sheet['initiative bonus']}]\n"
                        f"Succeeded Death Saves: {sheet['death saves']['success']}\n"
                        f"Failed Death Saves: {sheet['death saves']['failure']}\n"
                        f" -----------------===----------------- \n"
                        f"Background: {sheet['background']}  • Player: {interaction.user.display_name}\n",

            color=discord.Color.blue())


        # Attributes — um field por atributo
        for k, v in sheet["attribute"].items():
            mod: int = self.get_modifier(v)
            embed.add_field(
                name=k,
                value=f"{v} ({mod:+})",
                inline=True)

        # Saving Throws
        saving_throws: dict = {k: v for k, v in sheet["skills"].items() if "Saving Throw" in k}
        st_text: str = "\n".join([
            f"{'X' if data['proficient'] else 'O'} {name.replace(' Saving Throw', '')} [{data['attr']}]: {data['mod']:+}"
            for name, data in saving_throws.items()])
        embed.add_field(name="Saving Throws", value=st_text, inline=False)

        # Skills
        skills_only: dict = {k: v for k, v in sheet["skills"].items() if "Saving Throw" not in k}
        skills_text: str = "\n".join([
            f"{'[X]' if data['proficient'] else '[O]'} {name} [{data['attr']}]: {data['mod']:+}"
            for name, data in skills_only.items()])
        embed.add_field(name="Skills", value=skills_text, inline=False)

        # Other Proficiencies
        if sheet["other proficiencies"]:
            for item in sheet["other proficiencies"]:
                embed.add_field(
                    name="Other Proficiency",
                    value=item,
                    inline=False)

        # Abilities
        if sheet["abilities"]:
            for item in sheet["abilities"]:
                embed.add_field(
                    name="Ability",
                    value=item,
                    inline=False)

        # Traits
        if sheet["traits"]:
            for item in sheet["traits"]:
                embed.add_field(
                    name="Trait",
                    value=item,
                    inline=False)

        # Inventory
        if sheet["inventory"]:
            for item in sheet["inventory"]:
                embed.add_field(
                    name="Inventory item",
                    value=item,
                    inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- DELETE SHEET
    @app_commands.command(name="delete_sheet", description="Permanently delete your character sheet")
    async def delete_sheet(self, interaction: discord.Interaction) -> None:

        sheet: dict | None = await self.has_sheet(interaction)
        if sheet is None:
            return

        user_id: str = str(interaction.user.id)
        name: str = sheet["name"]
        del self.data[user_id]
        self.save_data()

        await self.safe_send(interaction, f"{name} was permanently deleted.", ephemeral=False)

    # endregion

    # region ==== SET ====

    # --- SET ATRIBUTES
    @app_commands.command(name="set_atribute", description="Change atribute")
    @app_commands.choices(stat=[
        app_commands.Choice(name="Strenght (STR)", value="STR"),
        app_commands.Choice(name="Dexterity (DEX)", value="DEX"),
        app_commands.Choice(name="Constitution (CON)", value="CON"),
        app_commands.Choice(name="Inteligence (INT)", value="INT"),
        app_commands.Choice(name="Wisdom (WIS)", value="WIS"),
        app_commands.Choice(name="Charisma (CHA)", value="CHA"),
    ])
    async def set_atribute(self, interaction: discord.Interaction,
                           stat: app_commands.Choice[str],
                           value: int) -> None:

        sheet: dict | None = await self.has_sheet(interaction)
        if sheet is None:
            return

        sheet["attribute"][stat.value] = value
        self.update_skills(sheet)
        self.save_data()

        await interaction.response.send_message(f"{stat.name} uptdate to {value}!")

    # --- SET PROFICIENCY
    @app_commands.command(name="give_proficiency", description="Activate/deactivate a specific proficiency")
    @app_commands.choices(skill=[
        app_commands.Choice(name="Strenght Saving Throw", value="Strenght Saving Throw"),
        app_commands.Choice(name="Dexterity Saving Throw", value="Dexterity Saving Throw"),
        app_commands.Choice(name="Constitution Saving Throw", value="Constitution Saving Throw"),
        app_commands.Choice(name="Inteligence Saving Throw", value="Inteligence Saving Throw"),
        app_commands.Choice(name="Wisdom Saving Throw", value="Wisdom Saving Throw"),
        app_commands.Choice(name="Charisma Saving Throw", value="Charisma Saving Throw"),
        app_commands.Choice(name="Acrobatics", value="Acrobatics"),
        app_commands.Choice(name="Animal Handling", value="Animal Handling"),
        app_commands.Choice(name="Arcana", value="Arcana"),
        app_commands.Choice(name="Athletics", value="Athletics"),
        app_commands.Choice(name="Deception", value="Deception"),
        app_commands.Choice(name="History", value="History"),
        app_commands.Choice(name="Insight", value="Insight"),
        app_commands.Choice(name="Intimidation", value="Intimidation"),
        app_commands.Choice(name="Investigation", value="Investigation"),
        app_commands.Choice(name="Medicine", value="Medicine"),
        app_commands.Choice(name="Nature", value="Nature"),
        app_commands.Choice(name="Perception", value="Perception"),
        app_commands.Choice(name="Performance", value="Performance"),
        app_commands.Choice(name="Persuasion", value="Persuasion"),
        app_commands.Choice(name="Religion", value="Religion"),
        app_commands.Choice(name="Sleight of Hand", value="Sleight of Hand"),
        app_commands.Choice(name="Stealth", value="Stealth"),
        app_commands.Choice(name="Survival", value="Survival"),
    ])
    async def give_proficiency(self, interaction: discord.Interaction,
                               skill: app_commands.Choice[str]) -> None:

        sheet: dict | None = await self.has_sheet(interaction)
        if sheet is None:
            return

        skills: dict = sheet["skills"]

        # Toggle
        skills[skill.value]["proficient"] = not skills[skill.value]["proficient"]

        self.update_skills(sheet)
        self.save_data()

        status: str = f"You are proficient in {skill}" \
            if skills[skill.value]["proficient"] \
            else f"You are no more proficient in {skill}"

        await interaction.response.send_message(f"{skill.name} {status}!")

    # --- SET COMBAT ATRIBUTES
    @app_commands.command(name="set_combat", description="Change your AC/Initiative Bonus/Speed")
    @app_commands.choices(stat=[
        app_commands.Choice(name="Armor Class", value="armor class"),
        app_commands.Choice(name="Initiative Bonus", value="initiative bonus"),
        app_commands.Choice(name="Speed", value="speed"),
    ])
    async def set_combat(self, interaction: discord.Interaction,
                         stat: app_commands.Choice[str],
                         value: int) -> None:

        sheet: dict | None = await self.has_sheet(interaction)
        if sheet is None:
            return

        sheet[stat.value] = value
        self.save_data()

        await interaction.response.send_message(f"{stat.name} updated to {value}!")

    # --- ADD NEW ITEM IN LIST
    @app_commands.command(name="add_item", description="Add a new Ability/Trait/Item/Other Proficiency in the list")
    @app_commands.choices(field=[
        app_commands.Choice(name="Other Proficiencies", value="other proficiencies"),
        app_commands.Choice(name="Abilities", value="abilities"),
        app_commands.Choice(name="Traits", value="traits"),
        app_commands.Choice(name="Inventory", value="inventory"),
    ])
    async def add_item(self, interaction: discord.Interaction,
                       field: app_commands.Choice[str],
                       text: str) -> None:

        sheet: dict | None = await self.has_sheet(interaction)
        if sheet is None:
            return

        sheet[field.value].append(text)
        self.save_data()

        await interaction.response.send_message(f"Added {field.name}: {text}")

    # --- REMOVE ITEM FROM LIST
    @app_commands.command(name="remove_item", description="Remove Abilitie/Trait/Item/Other Proficiency in the list")
    @app_commands.choices(field=[
        app_commands.Choice(name="Other Proficiencies", value="other proficiencies"),
        app_commands.Choice(name="Abilities", value="abilities"),
        app_commands.Choice(name="Traits", value="traits"),
        app_commands.Choice(name="Inventory", value="inventory"),
    ])
    async def remove_item(self, interaction: discord.Interaction,
                          field: app_commands.Choice[str],
                          text: str) -> None:

        sheet: dict | None = await self.has_sheet(interaction)
        if sheet is None:
            return

        lista: list[str] = sheet[field.value]

        if text not in lista:
            return await interaction.response.send_message("Not Found")

        lista.remove(text)
        self.save_data()

        await interaction.response.send_message(f"Removed {field.name}: {text}")

    # endregion

    # region ==== DICE ====

    # --- ROLL 1D20
    def roll_d20(self) -> int:
        return random.randint(1, 20)

    # --- ROLL A TIPE OF DICE
    @app_commands.command(name="roll_skill", description="Roll 1d20 for Skill, Iniciative or Raw atribute modifier with respective bonuses")
    @app_commands.choices(mode=[
        app_commands.Choice(name="Attribute", value="attribute"),
        app_commands.Choice(name="Skill", value="skills"),
    ])
    async def roll_skill(self, interaction: discord.Interaction,
                         mode: app_commands.Choice[str],
                         name: str = None) -> None:

        ficha: dict | None = await self.has_sheet(interaction)
        if not ficha:
            return

        label: str = ""
        d20: int = self.roll_d20()
        bonus: int = 0

        if mode.value == "attribute":
            if name not in ficha["attribute"]:
                await interaction.response.send_message(f"ERROR: There is no {name} in {mode.value}")
                return
            label = "raw atribute bonus"
            bonus = self.get_modifier(ficha["attribute"][name])

        elif mode.value == "skills":
            if name not in ficha["skills"]:
                await interaction.response.send_message(f"ERROR: There is no {name} in {mode.value}")
                return
            label = f"{name}"
            skill: dict = ficha["skills"][name]
            bonus = skill["mod"]

        total: int = d20 + bonus

        await interaction.response.send_message(
            f"Rolling {label}\n"
            f"Roll: {d20}\n"
            f"Bonus: {bonus:+}\n"
            f"Total: {total}")

    @app_commands.command(name="roll_initiative", description="Roll for initiative")
    async def roll_initiative(self, interaction: discord.Interaction) -> None:

        ficha: dict | None = await self.has_sheet(interaction)
        if not ficha:
            return

        d20: int = self.roll_d20()
        bonus: int = ficha["initiative bonus"]
        total: int = d20 + bonus

        await interaction.response.send_message(
            f"Rolling initiative\n"
            f"Roll: {d20}\n"
            f"Bonus: {bonus:+}\n"
            f"Total: {total}")

    @app_commands.command(name="roll_combat", description="Roll xDx and choose: take full damage/take half damage/heal/gain temporary hp")
    async def roll_combat(self, interaction: discord.Interaction, dice_amount: int, dice_face: int) -> None:

        sheet: dict | None = await self.has_sheet(interaction)
        if not sheet:
            return

        dice_results: list[int] = [random.randint(1, dice_face) for _ in range(dice_amount)]
        total_value: int = sum(dice_results)

        view: CombatView = CombatView(self, str(interaction.user.id), total_value)

        rolled_text: str = " + ".join(str(x) for x in dice_results)
        await interaction.response.send_message(
            f"Rolled: {rolled_text} = {total_value}\n",
            view=view)

    @app_commands.command(name="roll_death_save", description="Roll a death saving throw")
    async def roll_death_save(self, interaction: discord.Interaction):

        sheet = await self.has_sheet(interaction)
        if sheet is None:
            return

        roll = self.roll_d20()

        result_text = ""
        death_saves = sheet["death saves"]

        #  Nat 1
        if roll == 1:
            death_saves["failure"] += 2
            result_text = "Critical Failure! (+2 failures)"

        # Nat 20
        elif roll == 20:
            death_saves["success"] += 2
            result_text = "Critical Success! (+2 successes)"

        # Fail
        elif roll < 10:
            death_saves["failure"] += 1
            result_text = "Failure (+1)"

        # Sucess
        else:
            death_saves["success"] += 1
            result_text = "Success (+1)"

        # clamp amount of death saves
        death_saves["success"] = min(death_saves["success"], 3)
        death_saves["failure"] = min(death_saves["failure"], 3)

        self.save_data()

        await interaction.response.send_message(
            f"Death Saving Throw\n"
            f"Roll: {roll}\n"
            f"{result_text}\n\n"
            f"Successes: {death_saves['success']}/3\n"
            f"Failures: {death_saves['failure']}/3"
        )

    @app_commands.command(name="reset_death_save", description="Reset the values of death saving throw")
    async def roll_death_save(self, interaction: discord.Interaction):

        sheet = await self.has_sheet(interaction)
        if sheet is None:
            return

        sheet["death saves"]["success"] = 0
        sheet["death saves"]["failure"] = 0

        await self.safe_send(interaction, "Death Saves have been reseted")

    # endregion


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Sheet(bot))