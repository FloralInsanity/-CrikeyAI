# crikey.py
# testing

import os
import json
import discord
from dotenv import load_dotenv
from discord.ext import commands
import asyncio
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all(), help_command=None)

servers = {
    # uni server
    '1076982138999685251': {
        'main_id': '1076982139641409621', 
        'welcome_role': '1078593910449913859',
        'logs_id': '1078610446791221268',
        'mod_role': '1076990530182975618',
        'mute_role': '1226496573769515018'
    },

    # snaf's server
    '1224692655724822528': {
        'main_id': '1224692655724822530', 
        'welcome_role': '1224706218250211369',
        'logs_id': '1225703344413085758',
        'mod_role': '1224702973142372466',
        'mute_role': '1225779640866443264'
    },
}

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to disk cord!')
    global message_1, message_2
    channel = bot.get_channel(1224698778154434581) #colour-roles channel
    message_1 = await channel.fetch_message(1225021798844727386) #colour roles msg 1
    message_2 = await channel.fetch_message(1225021831690326079) #colour roles msg 2

@bot.event
async def on_member_join(member):

    embed = discord.Embed(
        title="Member joined the server",
        description=f"**{member.display_name}** has joined the server.",
        color=0xa31013
    )

    embed.set_thumbnail(url=member.avatar.url)
    
    server = servers.get(str(member.guild.id))
    main_channel = bot.get_channel(int(server.get('main_id')))
    logs_channel = bot.get_channel(int(server.get('logs_id')))
    welcome_role = server.get('welcome_role')

    if main_channel:
        await main_channel.send(embed=embed)
        await main_channel.send(f'Man, how the floor is made out of floor. Anyway, say hi to to my new mate {member.mention}.')     
    else:
        print("can't find the main channel")

    if logs_channel:
        await logs_channel.send(embed=embed) 
    else:
        print("can't find the logs channel")

    if welcome_role:
        await member.add_roles(welcome_role)
    else:
        print("can't find the welcome role")


@bot.event
async def on_member_remove(member):

    embed = discord.Embed(
        title="Member did a Bamo and left the server",
        description=f"**{member.display_name}** has left the server.",
        color=0xFF0000
    )
    
    embed.set_thumbnail(url=member.avatar.url)

    server = servers.get(str(member.guild.id))
    logs_channel = bot.get_channel(int(server.get('logs_id')))

    if logs_channel:
        await logs_channel.send(embed=embed)
    else:
        print(f"can't find the logs channel")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('you never passed in all the requirements kiddo :rolling_eyes:')
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("you don't have permission to use this command :angry:")

previous_role = None
previous_reaction = None
message_ids = [1225021798844727386, 1225021831690326079]

@bot.event
async def on_raw_reaction_add(payload):
    global previous_reaction

    if payload.message_id in message_ids:
        channel_id = payload.channel_id
        message_id = payload.message_id
        user_id = payload.user_id
        emoji = str(payload.emoji)

        channel = bot.get_channel(channel_id)
        user = bot.get_user(user_id)
        message = await channel.fetch_message(message_id)

        if previous_reaction:
            for msg_id in message_ids:
                msg = await channel.fetch_message(msg_id)
                await msg.remove_reaction(previous_reaction, user)

        previous_reaction = emoji

@bot.event
async def on_message_delete(message):

    embed = discord.Embed(
        color=0xFF0000
    )
    
    if isinstance(message.author, discord.Member):
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
    else:
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)

    embed.add_field(name="Message", value=message.content, inline=False)
    embed.add_field(name="Channel", value=message.channel.mention)
    embed.add_field(name="Deleted by", value=message.author.mention)

    server = servers.get(message.guild.id)
    logs_channel = bot.get_channel(int(server.get('logs_id')))

    if logs_channel:
        await logs_channel.send(embed=embed)
    else:
        print("can't find the logs channel")

@bot.event
async def on_message_edit(before, after):

    if before.content == after.content or "http://" in after.content or "https://" in after.content:
        return 

    embed = discord.Embed(
        color=0xFFFF00
    )

    if isinstance(after.author, discord.Member):
        embed.set_author(name=after.author.display_name, icon_url=after.author.avatar.url)
    else:
        embed.set_author(name=after.author.display_name, icon_url=after.author.avatar_url)

    embed.add_field(name="Before", value=before.content, inline=False)
    embed.add_field(name="After", value=after.content, inline=False)
    embed.add_field(name="Edited by", value=after.author.mention)

    server = servers.get(before.guild.id)
    logs_channel = bot.get_channel(int(server.get('logs_id')))

    if logs_channel:
        await logs_channel.send(embed=embed)
    else:
        print(f"can't find the logs channel")

@bot.event
async def on_member_update(before, after):
    if before.nick != after.nick:
 
        embed = discord.Embed(
            description="**Before:** {}\n**After:** {}".format(before.nick, after.nick),
            color=0xFFA500
        )
        
        embed.set_author(name=after.display_name, icon_url=after.avatar.url)

        server = servers.get(after.guild.id)
        logs_channel = bot.get_channel(int(server.get('logs_id')))

        if logs_channel:
            embed.add_field(name="Changed by", value=after.mention)
            await logs_channel.send(embed=embed)
        else:
            print(f"can't find the logs channel")

@bot.command()
@commands.check_any(commands.has_role(servers.get('mod_role')), commands.has_permissions(administrator=True))
async def ban(ctx, member: discord.Member, *, reason=None):

    has_mod_role = any(role.id == servers['mod_role'] for role in member.roles)

    if (has_mod_role or member.guild_permissions.administrator):
        await ctx.send("can't ban that user fam.")
        return

    if str(ctx.guild.id) in servers:
        logs_id = servers[str(ctx.guild.id)].get('logs_id')
        if logs_id:
            logs_channel = bot.get_channel(int(logs_id))
            if logs_channel:
                embed = discord.Embed(
                    title="Member Banned",
                    color=0xFF0000
                )
                
                if isinstance(member, discord.Member):
                    embed.set_author(name=member.display_name, icon_url=member.avatar.url)
                else:
                    embed.set_author(name=member.display_name, icon_url=member.avatar_url)

                embed.add_field(name="User", value=member.mention, inline=True)
                embed.add_field(name="Mod", value=ctx.author.mention, inline=True)
                embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)

                await logs_channel.send(embed=embed)
            else:
                print("Logs channel not found.")
                return
        else:
            print("Logs channel ID not in dictionary.")
            return
    else:
        print("Server not found in dictionary.")
        return
        
    await ctx.guild.ban(member, reason=reason)
    await ctx.send(f"{member.display_name} has been banned from the server.")

@bot.command()
@commands.check_any(commands.has_role(servers.get('mod_role')), commands.has_permissions(administrator=True))
async def unban(ctx, user: discord.User, *, reason=None):
    if str(ctx.guild.id) in servers:
        logs_id = servers[str(ctx.guild.id)].get('logs_id')
        if logs_id:
            logs_channel = bot.get_channel(int(logs_id))
            if logs_channel:
                try:
                    ban_entry = await ctx.guild.fetch_ban(user)
                    await ctx.guild.unban(user)
                    embed = discord.Embed(
                        title="Member Unbanned",
                        color=0x00FF00
                    )
                    embed.add_field(name="User", value=user.mention, inline=True)
                    embed.add_field(name="Mod", value=ctx.author.mention, inline=True)
                    embed.add_field(name="Reason", value=reason, inline=False)
                    await logs_channel.send(embed=embed)
                    await ctx.send(f"{user.name}#{user.discriminator} has been unbanned from the server.")
                except discord.NotFound:
                    await ctx.send("That user's not banned mate.")
                except discord.HTTPException:
                    await ctx.send("Failed to unban the user.")
            else:
                print("Logs channel not found.")
                return
        else:
            print("Logs channel ID not found in dictionary")
            return
    else:
        print("Server not found in dictionary.")
        return

@bot.command()
@commands.check_any(commands.has_role(servers.get('mod_role')), commands.has_permissions(administrator=True))
async def mute(ctx, member: discord.Member, duration: str, *, reason=None):

    has_mod_role = any(role.id == servers['mod_role'] for role in member.roles)
    
    if (has_mod_role or member.guild_permissions.administrator):
        await ctx.send("Can't mute that user fam.")
        return

    if duration[-1] == 'm':
        try:
            duration_minutes = int(duration[:-1])
        except ValueError:
            await ctx.send("Invalid duration format. Please use 'm' for minutes or 'h' for hours.")
            return
    elif duration[-1] == 'h':
        try:
            duration_minutes = int(duration[:-1]) * 60
        except ValueError:
            await ctx.send("Invalid duration format. Please use 'm' for minutes or 'h' for hours.")
            return
    else:
        await ctx.send("Invalid duration format. Please use 'm' for minutes or 'h' for hours.")
        return

    mute_role = ctx.guild.get_role(1225779640866443264)  # Replace with actual mute role ID
    if not mute_role:
        await ctx.send("Mute role not found.")
        return

    try:
        await member.add_roles(mute_role, reason=reason)
    except discord.Forbidden:
        await ctx.send("I don't have permission to mute members.")
        return

    logs_id = servers.get(str(ctx.guild.id), {}).get('logs_id')
    if not logs_id:
        await ctx.send("Logs id not found in dictionary.")
        return

    logs_channel = bot.get_channel(int(logs_id))
    if not logs_channel:
        await ctx.send("Logs channel not found.")
        return

    embed = discord.Embed(
        title="Member Muted",
        color=0xFFA500
    )
    embed.set_author(name=member.display_name, icon_url=member.avatar.url)
    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="Mod", value=ctx.author.mention, inline=True)
    embed.add_field(name="Duration", value=duration, inline=True)
    embed.add_field(name="Reason", value=reason if reason else "No reason provided", inline=False)

    await logs_channel.send(embed=embed)

    # Schedule automatic unmute after the specified duration
    await asyncio.sleep(duration_minutes * 60)  # Convert duration to seconds
    await member.remove_roles(mute_role, reason="Automatic unmute")

@bot.command()
@commands.check_any(commands.has_role(servers.get('mod_role')), commands.has_permissions(administrator=True))
async def unmute(ctx, member: discord.Member, *, reason="Manual unmute"):

    mute_role_id = servers.get('mute_role')
    if mute_role_id is not None:
        mute_role = ctx.guild.get_role(mute_role_id)

    if not mute_role:
        await ctx.send("Mute role not found.")
        return
    
    if mute_role not in member.roles:
        await ctx.send("This member is not muted.")
        return

    try:
        await member.remove_roles(mute_role, reason=reason)
    except discord.Forbidden:
        await ctx.send("Can't unmute member, fam.")
        return

    logs_id = servers.get(str(ctx.guild.id), {}).get('logs_id')
    if not logs_id:
        await ctx.send("Logs id not found in dictionary.")
        return

    logs_channel = bot.get_channel(int(logs_id))
    if not logs_channel:
        await ctx.send("Logs channel not found.")
        return

    embed = discord.Embed(
        title="Member Unmuted",
        color=0xFFFF00
    )
    embed.set_author(name=member.display_name, icon_url=member.avatar.url)
    embed.add_field(name="User", value=member.mention, inline=True)
    embed.add_field(name="Mod", value=ctx.author.mention, inline=True)
    embed.add_field(name="Reason", value=reason, inline=False)

    await logs_channel.send(embed=embed)

    await ctx.send(f"{member.display_name} has been unmuted.")

@bot.command()
@commands.check_any(commands.has_role(servers.get('mod_role')), commands.has_permissions(administrator=True))
async def purge(ctx, amount: int):
    if amount <= 0 or amount > 100:
        await ctx.send("Please specify a number between 1 and 100.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1) 
    print(f"Deleted {len(deleted) - 1} messages.")

'''
@bot.command(name="react")
@commands.has_permissions(administrator=True)
async def react_to_message(ctx, message_id, emoji):
    try:
        # Fetch the message using the provided message_id
        guild = ctx.guild
        text_channel = guild.get_channel(1163072988682403891)  # Replace with your channel ID
        message = await text_channel.fetch_message(int(message_id))

        # Add a reaction to the message with the specified emoji
        await message.add_reaction(emoji)
        
        await ctx.send(f"Reacted with {emoji} to the specified message.")
    except Exception as e:
        print(f"Failed to react to the message: {e}")
        await ctx.send("Failed to react to the message.")

@bot.command(name="roles") # post a message to the roles channel
@commands.has_permissions(administrator=True)
async def rules(ctx, *, post=None):
    if post is None:
        await ctx.send("Please provide a description for the rule.")
        return

    channel = bot.get_channel(1163072988682403891)
    await channel.send(post)

@bot.command(name="rules") # post a message to the rules channel
@commands.has_permissions(administrator=True)
async def rules(ctx, *, post=None):
    if post is None:
        await ctx.send("Please provide a description for the rule.")
        return

    channel = bot.get_channel(1076982139641409617)
    await channel.send(post)

@bot.command(name="rules_embed") # post an embed to the rules channel
@commands.has_permissions(administrator=True)
async def rules(ctx, *, post=None):
    if post is None:
        await ctx.send("Please provide a description for the rule.")
        return
    # Create an embed with the provided description
    embed = discord.Embed(description=post, color=0xFF0000)
    # Send the embed to the current channel
    channel = bot.get_channel(1076982139641409617)
    await channel.send(embed=embed)

@bot.command(name="resources") # post a message to the resources channel
@commands.has_permissions(administrator=True)
async def resources(ctx, *, post = None):
    channel = bot.get_channel(1076982139641409619)
    await channel.send(post)

@bot.command(name="announcements") # post a message to the announcements channel
@commands.has_permissions(administrator=True)
async def announcements(ctx, *, post = None):
    channel = bot.get_channel(1077344251190444033)
    await channel.send(post)

# channel used to log message edit/delete
global logging_channel
logging_channel = 1078610446791221268

# defines blacklisted words that can't be used in the server
with open("blacklist.txt") as file: # blacklist.txt contains one phrase per line
    bad_words = [bad_word.strip().lower() for bad_word in file.readlines()]

@bot.event
async def on_message(message): # tells off the user if they use a blacklisted word, captures messages sent to crikey bot, reacts tomatoes to fool role
    message_content = message.content.strip().lower()
    if any(bad_word in message_content for bad_word in bad_words):
        await message.channel.send("{}, can't say that around here chum!".format(message.author.mention))
        await message.delete()
    guild = message.guild
    if not guild: 
        embed = discord.Embed(title='{}'.format(message.author), description="", color=0x11FF60)
        embed.add_field(name='Message:', value="{}".format(message.content), inline=False)
        channel = bot.get_channel(1079121876850323559) #crikey-bot-dms
        await channel.send(embed=embed)
    fool_role = discord.utils.get(message.guild.roles, name="Fool")
    if fool_role in message.author.roles:
        # React to the message with the :tomato: emote
        await message.add_reaction("🍅")
    # Overriding the default provided on_message forbids any extra commands from running. Fix:
    await bot.process_commands(message)

@bot.command(name="inventory_all") # checks inventory of all users
@commands.has_permissions(administrator=True)
async def inventory_all(ctx):
    inventory_info = {}
    with open('inventory.txt', 'r') as file:
        for line in file:
            user_id, *items = line.strip().split(',')
            member = ctx.guild.get_member(int(user_id))
            if member is None or member.bot:
                continue
            inventory_info[member] = items
    inventory_str = '\n'.join(f"{member.name}: {', '.join(items)}" for member, items in inventory_info.items())
    await ctx.send(inventory_str)

@bot.command(name='give') # gives any user an item
@commands.has_permissions(administrator=True)
async def give(ctx, user: discord.User, *, item_name: str):
    with open('inventory.txt', 'r+') as file:
        lines = file.readlines()
        file.seek(0)
        for i, line in enumerate(lines):
            if line.startswith(str(user.id)):
                fields = line.strip().split(",")
                fields.append(f'{item_name}')
                lines[i] = ", ".join(fields) + "\n"
                break
        else:
            lines.append(f"{user.id},{item_name}\n")
        file.truncate(0)
        file.writelines(lines)
    await ctx.send(f"{user.name}, something has been added to your inventory!")
    # make changes to the file
    with open('inventory.txt', 'w') as file:
        file.writelines(lines)
    
@bot.command(name='file') # reads the contents of a file
@commands.has_permissions(administrator=True)
async def filecontents(ctx, filename: str):
    try:
        with open(filename, 'r') as file:
            contents = file.read()
            await ctx.send(f"File contents:\n```{contents}```")
    except FileNotFoundError:
        await ctx.send(f"File '{filename}' not found.")
    
@bot.command(name="inventory") # a user can display their own inventory using this command
async def inventory(ctx):
    # Try to find the user's inventory in the file
    with open('inventory.txt', 'r') as file:
        for line in file:
            if line.startswith(str(ctx.author.id)):
                # Parse the user's inventory from the line and create an embed
                found = True
                parts = [p.strip() for p in line.split(',')]
                num_parts = len(parts)
                embed = discord.Embed(title="Inventory", color=discord.Color.blue())
                balance = parts[1]
                embed.add_field(name="Balance", value=balance, inline=False)
                for i in range(2, num_parts):
                    field_name = f"Item {i-1}"
                    quantity = parts[i]
                    embed.add_field(name=field_name, value=quantity, inline=True)
                await ctx.send(embed=embed)
                break
        else:
            # If the user doesn't have an inventory, ask them to create one
            await ctx.send("No inventory found. Ask Sana to help!")

    user_properties = {}
    station_properties = []

    with open('properties.txt', 'r') as file:
        prop_lines = [line.strip() for line in file.readlines()]

    for i, line in enumerate(prop_lines):
        property_info = line.split(', ')
        if len(property_info) == 10:
            if int(property_info[9]) == ctx.author.id:
                property_name = property_info[0]
                colour = property_info[1]
                initial_cost = int(property_info[2])
                houses = int(property_info[3])
                house_cost = int(property_info[4])
                hotels = int(property_info[5])
                hotel_cost = int(property_info[6])
                colour_group = int(property_info[8])
                owner_id = property_info[9]
                owner = await bot.fetch_user(int(owner_id))
                owner_name = owner.name
                total_money_spent = round((initial_cost + (houses * house_cost) + (hotels * hotel_cost)) * colour_group)
                property_info[7] = str(total_money_spent)
                total_value = property_info[7]
                user_properties[property_name] = (owner_name, colour, initial_cost, houses, house_cost, hotels, hotel_cost, colour_group, total_value)
                prop_lines[i] = ", ".join(property_info)
        elif len(property_info) == 6:
            if int(property_info[5]) == ctx.author.id:
                property_name = property_info[0]
                colour = property_info[1]
                initial_cost = int(property_info[2])
                number_of_stations = int(property_info[4])
                total_money_spent = round((initial_cost * number_of_stations))
                property_info[3] = str(total_money_spent)
                total_value = property_info[3]
                owner_id = property_info[5]
                owner = await bot.fetch_user(int(owner_id))
                owner_name = owner.name
                station_properties.append((property_name, owner_name, colour, initial_cost, total_value, number_of_stations))
                prop_lines[i] = ", ".join(property_info)

    with open("properties.txt", "w") as file:
        file.write('\n'.join(prop_lines))

    for property_name, (owner_name, colour, initial_cost, houses, house_cost, hotels, hotel_cost, colour_group, total_value) in user_properties.items():
        if property_name == "Onyx" or property_name == "STEAMHouse":
            embed = discord.Embed(title=property_name, description=f"Initial Cost: {initial_cost}\nHouses: {houses}/4 --- House Cost: {house_cost}\nHotels: {hotels}/1 --- Hotel Cost: {hotel_cost}\nColour Group Owned: {colour_group}/2\nTotal Value: {total_value}", color=int(colour, 16))
        else:
            embed = discord.Embed(title=property_name, description=f"Initial Cost: {initial_cost}\nHouses: {houses}/4 --- House Cost: {house_cost}\nHotels: {hotels}/1 --- Hotel Cost: {hotel_cost}\nColour Group Owned: {colour_group}/3\nTotal Value: {total_value}", color=int(colour, 16))
        await ctx.send(embed=embed)

    for property_name, owner_name, colour, initial_cost, total_value, number_of_stations in station_properties:
        if property_name == "New Street" or property_name == "Moor Street" or property_name == "National Express" or property_name == "Snow Hill":
            embed = discord.Embed(title=property_name, description=f"Initial Cost: {initial_cost}\nStations Owned: {number_of_stations}/4\nTotal Value: {total_value}", color=int(colour, 16))
            await ctx.send(embed=embed)

@bot.command(name="member_ids") # shows each member's username and their id
@commands.has_permissions(administrator=True)
async def member_ids(ctx):
    # Loop through all members in the server and print their ID
    for member in ctx.guild.members:
        await ctx.send(f"{member.name}: {member.id}")                   

global ban_channel
ban_channel = 1078708113588375572

@bot.command(name="ban") # bans a member
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = None):
    guild = bot.get_guild(1076982138999685251)
    role = discord.utils.get(guild.roles, id=1076990530182975618)
    if (role in member.roles):
        await ctx.send('Can\'t ban that person!')
        return
    await member.ban(reason = reason)
    await ctx.send(f"{member.mention} has been banned!")
    embed = discord.Embed(title='Banned.. Forever?', description="", color=0x2d9ad4)
    embed.add_field(name='Member: {}'.format(member), value="{}, the ban hammer has been cast upon you!".format(member.mention), inline=False)
    embed.add_field(name='Mod: {}'.format(ctx.author), value="{}'s reason: {}".format(ctx.author.mention, reason), inline=False)
    channel = bot.get_channel(ban_channel)
    await channel.send(embed=embed)

@bot.command(name="unban") # unbans a member
@commands.has_permissions(administrator = True)
async def unban(ctx, user : discord.User, *, reason = None):
    await ctx.guild.unban(user)
    await ctx.send(f"{user.mention} has been unbanned!")
    embed = discord.Embed(title='Unbanned.. For Now?', description="", color=0x00ff00)
    embed.add_field(name='Member: {}'.format(user), value="{}, you have been forgiven for your sins!".format(user.mention), inline=False)
    embed.add_field(name='Mod: {}'.format(ctx.author), value="{}'s reason: {}".format(ctx.author.mention, reason), inline=False)
    channel = bot.get_channel(ban_channel)
    await channel.send(embed=embed)

global cup_channel
cup_channel = 1163234236992602123

@bot.command(name="cup") # adds an instance to the cup log
@commands.has_permissions(ban_members = True)
async def cup(ctx, member : discord.Member, *, reason = None):
    await ctx.send(f"{member.mention} has been posted about!")
    embed = discord.Embed(title='Another Fool Enters the Cup...', description="", color=0x2d9ad4)
    embed.add_field(name='Member: {}'.format(member), value="{}, you have suffered the wrath of the cup!".format(member.mention), inline=False)
    embed.add_field(name='Mod: {}'.format(ctx.author), value="{}'s reason: {}".format(ctx.author.mention, reason), inline=False)
    channel = bot.get_channel(cup_channel)
    await channel.send(embed=embed)

# command to give coins to a user
#@bot.command(name="give_credits")
#@commands.has_permissions(administrator = True)
#async def give_credits(ctx, user : discord.User, amount: int):
#    # add the currency to the user's balance
#    currency[user.id] += amount
#    await ctx.send(f"Gave {amount} coins to {user.name}.")
    
# command to reset coins for all users
#@bot.command(name="reset_coins")
#@commands.has_permissions(administrator = True)
#async def reset_coins(ctx):
#    # loop through all members in the server and set their balance to 0
#    for member in ctx.guild.members:
#        currency[member.id] = 0
#    await ctx.send("Reset coins for all users.")

# command to reset inventory for all users
#@bot.command(name="reset_inventory")
#@commands.has_permissions(administrator = True)
#async def reset_inventory(ctx):
#    # loop through all members in the server and set their inventory to an empty list
#    for member in ctx.guild.members:
#        inventory[str(member.id)] = {}
#    await ctx.send("Reset inventory for all users.")

# command to reset shop
#@bot.command(name="reset_shop")
#@commands.has_permissions(administrator = True)
#async def reset_shop(ctx):
#    # sets shop to empty
#    shop = []
#    await ctx.send("Reset shop")   
            
# command to add items to the shop
#@bot.command()
#@commands.has_permissions(administrator = True)
#async def add_item(ctx, item: str, price: int):
#    # add the item to the shop
#    shop[item] = {"price": price, "quantity": 1}
#    await ctx.send(f"Added {item} to the shop for {price} coins.")

@bot.command(name="properties")
async def properties(ctx):
    embed = discord.Embed()#title="Monopoly Board")#, description="This embed contains a Monopoly board image.")
    # Attach the image file
    file = discord.File("monopoly_board.png", filename="monopoly_board.png")  # Replace with the correct image file path
    # Set the image in the embed
    embed.set_image(url="attachment://monopoly_board.png")  # Update the URL to match the filename in discord.File
    # Send the embed with the attached image
    await ctx.send(file=file, embed=embed)

    owned_properties = {}
    unowned_properties = {}

    with open('properties.txt', 'r') as file:
        for line in file:
            property_info = line.strip().split(',')
            if len(property_info) == 10:
                property_name = property_info[0]
                colour = property_info[1]
                initial_price = property_info[2]
                owner_id = property_info[9]
                owner = await bot.fetch_user(int(owner_id))
                owner_name = owner.name 
                owned_properties[property_name] = (owner_name, colour)
            elif len(property_info) == 6:
                property_name = property_info[0]
                colour = property_info[1]
                initial_price = property_info[2]
                owner_id = property_info[5]
                owner = await bot.fetch_user(int(owner_id))
                owner_name = owner.name 
                owned_properties[property_name] = (owner_name, colour)
            else:
                property_name = property_info[0]
                colour = property_info[1]
                initial_price = property_info[2]
                unowned_properties[property_name] = (colour, initial_price)
    
    owned_embed = discord.Embed(title="Owned Properties", color=discord.Color.green())
    for property_name, (owner_name, colour) in owned_properties.items():
        owned_embed.add_field(name=property_name, value=f"{owner_name}", inline=True)

    unowned_embed = discord.Embed(title="Unowned Properties", color=discord.Color.red())
    for property_name, (colour, initial_price) in unowned_properties.items():
        unowned_embed.add_field(name=property_name, value=f"{initial_price} credits", inline=True)

    await ctx.send(embed=owned_embed)
    await ctx.send(embed=unowned_embed)

@bot.command(name="buy")
async def buy(ctx, *, word):   
    properties = []
    word = word.replace(" ", "").replace("'", "")
    with open("properties.txt", "r") as f:
        for l in f:
            parts = l.strip().split(",")
            if len(parts) >= 1:
                property_name = parts[0].replace("'", "").replace(" ", "").upper()
            properties.append(property_name)
    print("check 1")
    print(properties)
    letters = list(word)
    with open("inventory.txt", "r+") as inv_file:
        inv_lines = inv_file.readlines()
        inv_file.seek(0)
        for i, line in enumerate(inv_lines):
            if line.startswith(str(ctx.author.id)):
                print("check 2")
                print(word.upper())
                if word.upper() in properties:
                    parts = [p.strip().replace(" ", "").replace("'", "") for p in line.split(',')]
                    print("check 3")
                    print(parts)
                    num_parts = len(parts)
                    found_letters = [letter for letter in letters if letter in parts]
                    print("check 4")
                    print(found_letters)
                    print(letters)
                    if len(found_letters) == len(letters):
                        print("check5")
                        for letter in found_letters:
                            parts.remove(letter)
                        inv_lines[i] = ", ".join(parts) + "\n"
                        with open("properties.txt", "r+") as prop_file:
                            prop_lines = prop_file.readlines()
                            prop_file.seek(0)
                            #word = word.replace(" ", "").upper()
                            for j, prop_line in enumerate(prop_lines):
                                prop_parts_og = prop_line.strip().split(", ")
                                prop_parts = [part.replace(" ", "").replace("'", "") for part in prop_line.strip().split(", ")]
                                print(word.upper())
                                print(prop_parts[0].upper())
                                if word.upper() == prop_parts[0].upper() and len(prop_parts) == 6:
                                    await ctx.send(f"{owner_name} already owns that property!")
                                    return
                                elif word.upper() == prop_parts[0].upper() and len(prop_parts) == 5:
                                    print("check10")
                                    print(prop_parts[0])
                                    if int(inv_lines[i].split(', ')[1]) >= int(prop_parts[2]):
                                        print("check last")
                                        prop_parts[0] = prop_parts_og[0]
                                        colour = prop_parts[1]
                                        print(prop_parts[0])
                                        # test
                                        print("test")
                                        joints = {}
                                        prop_file.seek(0)
                                        for k, pk in enumerate(prop_lines):
                                            kparts = pk.strip().split(", ")
                                            joints[prop_parts[0]] = colour
                                            if len(kparts) >= 6 and kparts[5] == str(ctx.author.id) and kparts[1] == colour:
                                                joints[kparts[0]] = kparts[1]
                                        print(joints)
                                        #editing
                                        prop_file.seek(0)
                                        for l, pl in enumerate(prop_lines):
                                            lparts = pl.strip().split(", ")
                                            print(lparts[1])
                                            if lparts[0] in joints:
                                                print("yes")
                                                print("checker")
                                                lparts[4] = str(len(joints))
                                                prop_lines[l] = ", ".join(lparts) + "\n"
                                                print("changed number of properties in one colour")
                                        prop_parts[4] = str(len(joints))
                                        print("changed number of properties in og colour")
                                        print("test end")
                                        #test end
                                        inv_value = int(inv_lines[i].split(', ')[1])
                                        inv_value -= int(prop_parts[2])
                                        inv_lines[i] = inv_lines[i].replace(str(inv_value + int(prop_parts[2])), str(inv_value))
                                        inv_file.writelines(inv_lines)  # Update inventory.txt
                                        inv_file.truncate()
                                        inv_file.flush()  # Flush changes to the file
                                        prop_parts.append(str(ctx.author.id))
                                        prop_lines[j] = ", ".join(prop_parts) + "\n"  # Update properties line
                                        prop_file.writelines(prop_lines)  # Update properties.txt
                                        prop_file.truncate()
                                        prop_file.flush()  # Flush changes to the file
                                        await ctx.send(f"You have obtained {prop_parts[0]}!")
                                        break
                                if word.upper() == prop_parts[0].upper() and len(prop_parts) == 10:
                                    print("check6")
                                    print("word")
                                    owner_id = prop_parts[9]
                                    owner = await bot.fetch_user(int(owner_id))
                                    owner_name = owner.name
                                    await ctx.send(f"{owner_name} already owns that property!")
                                    return
                                if (word.upper() == prop_parts[0].upper() and len(prop_parts) == 9):
                                    print("check7")
                                    print(prop_parts[0])
                                    if int(inv_lines[i].split(', ')[1]) >= int(prop_parts[2]):
                                        inv_value = int(inv_lines[i].split(', ')[1])
                                        inv_value -= int(prop_parts[2])
                                        inv_lines[i] = inv_lines[i].replace(str(inv_value + int(prop_parts[2])), str(inv_value))
                                        print("check last")
                                        prop_parts[0] = prop_parts_og[0]
                                        colour = prop_parts[1]
                                        print(prop_parts[0])
                                        # test
                                        print("test")
                                        joints = {}
                                        prop_file.seek(0)
                                        for k, pk in enumerate(prop_lines):
                                            kparts = pk.strip().split(", ")
                                            joints[prop_parts[0]] = colour
                                            if len(kparts) >= 10 and kparts[9] == str(ctx.author.id) and kparts[1] == colour:
                                                joints[kparts[0]] = kparts[1]
                                        print(joints)
                                        #editing
                                        prop_file.seek(0)
                                        for l, pl in enumerate(prop_lines):
                                            lparts = pl.strip().split(", ")
                                            print(lparts[1])
                                            if lparts[0] in joints:
                                                print("yes")
                                                lparts[8] = str(len(joints))
                                                prop_lines[l] = ", ".join(lparts) + "\n"
                                                print("changed number of properties in one colour")
                                        prop_parts[8] = str(len(joints))
                                        print("changed number of properties in og colour")
                                        print("test end")
                                        #test end
                                        inv_file.writelines(inv_lines)  # Update inventory.txt
                                        inv_file.truncate()
                                        inv_file.flush()  # Flush changes to the file
                                        prop_parts.append(str(ctx.author.id))
                                        prop_lines[j] = ", ".join(prop_parts) + "\n"  # Update properties line
                                        prop_file.writelines(prop_lines)  # Update properties.txt
                                        prop_file.truncate()
                                        prop_file.flush()  # Flush changes to the file
                                        await ctx.send(f"You have obtained {prop_parts[0]}!")
                                        break
                                    await ctx.send("Don't try buying stuff when you're broke, ok :rolling_eyes:")
                    else: 
                        await ctx.send("You don't have the right letters to buy this property :rolling_eyes:")
                    break  # Exit the outer loop
                else:
                    await ctx.send("That is not a property :sob:")
                    return
            #else:
            #    await ctx.send("Did you make a mistake of some kind? For me to specify, I'd have to.. do work :sob:")
            #    return
    return
    
@bot.command(name="play")
async def play(ctx, word):
    letters = list(word)

    # Check if the word is in the scrabble dictionary
    with open("scrabble_dictionary.txt", "r") as f:
        if not any(word.lower() in line.lower().split() for line in f):
            await ctx.send("Invalid word.")
            return

    letter_scores = {
        'A': 5, 'E': 5, 'I': 5, 'O': 5, 'U': 5, 'L': 5, 'N': 5, 'S': 5, 'T': 5, 'R': 5,
        'D': 10, 'G': 10,
        'B': 15, 'C': 15, 'M': 15, 'P': 15,
        'F': 20, 'H': 20, 'V': 20, 'W': 20, 'Y': 20,
        'K': 25,
        'J': 40, 'X': 40,
        'Q': 50, 'Z': 50
    }
    
    count = 0
    for letter in letters:
        letter = letter.upper()
        count += letter_scores.get(letter, 0)
    
    if 5 <= len(letters) <= 6:
        count *= 2
    
    if 7 <= len(letters) <= 8:
        count *= 3
        
    if 9 <= len(letters) <= 10:
        count *= 4
    
    if len(letters) >= 11:
        count *= 5
            
    # Read the inventories.txt file line-by-line
    with open('inventory.txt', 'r+') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith(str(ctx.author.id)):
                # parse the user's inventory from the line and create an embed
                parts = [p.strip() for p in line.split(',')]
                num_parts = len(parts)
                found_letters = []
                for letter in letters:
                    if letter in parts:
                        parts.remove(letter)
                        found_letters.append(letter)
                
                if len(found_letters) == len(letters):
                    print(count)
                    await ctx.send("All letters found!")
                    await ctx.send("Credits Earned: " + str(count))
                    parts[1] = str(int(parts[1]) + count)
                else:
                    await ctx.send("You don't have the right letters for this word.")
                    return

                lines[i] = ", ".join(parts) + "\n"
                file.seek(0)
                file.writelines(lines)
                file.truncate()
                return  # Exit the function after processing the inventory

    await ctx.send("Couldn't find your inventory.")

@bot.command(name="letter") 
async def letter(ctx):
    import random
    letters = ['A', 'E', 'I', 'O', 'U', 'L', 'N', 'S', 'T', 'R', 'D', 'G', 'B', 'C', 'M', 'P', 'F', 'H', 'V', 'W', 'Y', 'K', 'J', 'X', 'Q', 'Z']
    chances = [8, 8, 7, 7, 4, 5, 7, 6, 7, 8, 3, 3, 2, 5, 3, 3, 2, 3, 1, 1, 2, 1, 1, 1, 1, 1]
    # Read the inventories.txt file line-by-line
    with open('inventory.txt', 'r+') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.startswith(str(ctx.author.id)):
                # parse the user's inventory from the line and create an embed
                parts = [p.strip() for p in line.split(',')]
                if int(parts[1]) >= 10 and len(parts) < 22:
                    random_letter = random.choices(letters, weights=chances)[0]
                    #await ctx.send(random_letter)
                    await ctx.send("The letter: '" + random_letter.lower() + "' has been added to your inventory!")
                    parts[1] = str(int(parts[1]) - 10)
                    parts.append(random_letter.lower())
                elif len(parts) == 22:
                    await ctx.send("Max letters reached!")
                else:
                    await ctx.send("You don't have enough credits to buy a letter!")
                lines[i] = ", ".join(parts) + "\n"
                file.seek(0)
                file.write("".join(lines))
                file.truncate()
                return  # Exit the function after processing the inventory
    
@bot.command(name="daily")
@commands.has_permissions(administrator = True)
async def daily(ctx):
    with open('inventory.txt', 'r+') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            parts = [p.strip() for p in line.split(',')]
            parts[1] = str(int(parts[1]) + 200)
            lines[i] = ", ".join(parts) + "\n"
        file.seek(0)
        file.writelines(lines)
        file.truncate()
        await ctx.send("200 credits added to every user!")

    user_properties = {}
    
    with open('properties.txt', 'r') as file:
        for line in file:
            property_info = line.strip().split(',')
            if len(property_info) >= 10:
                if int(property_info[9]) == ctx.author.id:
                    property_name = property_info[0]
                    colour = property_info[1]
                    initial_cost = float(property_info[2])
                    houses = int(property_info[3])
                    house_cost = float(property_info[4])
                    hotels = int(property_info[5])
                    hotel_cost = float(property_info[6])
                    colour_group = float(property_info[8])
                    owner_id = property_info[9]
                    owner = await bot.fetch_user(int(owner_id))
                    owner_name = owner.name 

                    # Calculate total_money_spent
                    total_money_spent = (initial_cost + (houses * house_cost) + (hotels * hotel_cost)) * colour_group
                    property_info[7] = str(total_money_spent)
                
                    # Calculate 10% of the value
                    ten_percent = round(0.1 * total_money_spent)

                    with open('inventory.txt', 'r+') as inventory_file:
                        inv_lines = inventory_file.readlines()
                        for i, inv_line in enumerate(inv_lines):
                            inv_parts = [p.strip() for p in inv_line.split(',')]
                            if inv_parts[0].strip() == str(owner_id).strip():
                                inv_parts[1] = str(round(float(inv_parts[1]) + ten_percent))
                                print(f"inv_parts[1]: {inv_parts[1]}, type: {type(inv_parts[1])}")
                                print(f"ten_percent: {ten_percent}, type: {type(ten_percent)}")
                                inv_lines[i] = ", ".join(inv_parts) + "\n"
                                await ctx.send(f"Owner of {property_name}, {owner_name}, just got {ten_percent} credits!")

@bot.command(name="stats")
async def stats(ctx):
    inventory = {}  # Dictionary to store the values
    
    with open('inventory.txt', 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if len(parts) >= 2:
                owner_id = parts[0]
                owner = await bot.fetch_user(int(owner_id))
                owner_name = owner.name 
                key = owner_name.strip()
                value = int(parts[1].strip())
                inventory[key] = value
    
    sorted_inventory = sorted(inventory.items(), key=lambda x: x[1], reverse=True)
    
    embed = discord.Embed(title="Ranks", color=0x00ff00)
    position = 1
    for key, value in sorted_inventory:
        embed.add_field(name=f"{position}. {key}", value=str(value), inline=True)
        position += 1
    
    await ctx.send(embed=embed)

@bot.command(name="house")
async def buy_house(ctx, *, word):
    properties = []
    word = word.replace(" ", "").replace("'", "")

    with open("properties.txt", "r") as prop_file:
        prop_lines = prop_file.readlines()

        for line in prop_lines:
            parts = line.strip().split(", ")
            if len(parts) >= 1:
                property_name = parts[0].replace("'", "").replace(" ", "").upper()
                properties.append(property_name)
                print("check 1")
                print(str(property_name))
                print(str(word.upper()))
                if str(property_name) == str(word.upper()):
                    print("same")
                    if len(parts) == 6:  # Incorrect ownership
                        await ctx.send("You can't build a house on a station, silly! :rolling_eyes:")
                        return
                    if len(parts) < 10 or parts[9] != str(ctx.author.id):  # Incorrect ownership
                        await ctx.send("You don't own this property, silly! :rolling_eyes:")
                        return
                    else:
                        print("same 2")
                        with open("inventory.txt", "r+") as inv_file:
                            inv_lines = inv_file.readlines()

                            for i, line in enumerate(inv_lines):
                                if line.startswith(str(ctx.author.id)):
                                    inv_parts = [p.strip().replace(" ", "").replace("'", "") for p in line.split(',')]
                                    for j, prop_line in enumerate(prop_lines):
                                        prop_parts_og = prop_line.strip().split(", ")
                                        prop_parts = [p.strip().replace(" ", "").replace("'", "") for p in prop_line.split(",")]
                                        print("check1")
                                        print(prop_parts[0].upper())
                                        print(property_name)
                                        if prop_parts[0].upper() == property_name:
                                            print("same3")
                                            if int(inv_parts[1]) < int(prop_parts[4]):
                                                await ctx.send("You don't have enough money to buy a house!")
                                                return
                                            elif int(prop_parts[3]) >= 4:
                                                await ctx.send("You already have the maximum number of houses!")
                                                return
                                            else:
                                                print("same4")
                                                inv_parts[1] = str(int(inv_parts[1]) - int(prop_parts[4]))
                                                prop_parts[3] = str(int(prop_parts[3]) + 1)
                                                print("check 7")
                                                print(prop_parts[0])
                                                print(prop_parts_og[0])
                                                prop_parts[0] = prop_parts_og[0]
                                                
                                                inv_lines[i] = ", ".join(inv_parts) + "\n"
                                                prop_lines[j] = ", ".join(prop_parts) + "\n"

                                                with open("inventory.txt", "w") as inv_file:
                                                    inv_file.writelines(inv_lines)

                                                with open("properties.txt", "w") as prop_file:
                                                    prop_file.writelines(prop_lines)

                                                print("Updated inventory and properties.")
                                                await ctx.send(f"You have bought a house at {prop_parts[0]}!")
                                                return

                            print("Property not found!")
                            await ctx.send("Property not found!")
                            return

        print("Word not found!")
        await ctx.send("That property does not exist!")
        return

@bot.command(name="hotel")
async def hotel(ctx, *, word):
    properties = []
    word = word.replace(" ", "").replace("'", "")

    with open("properties.txt", "r") as prop_file:
        prop_lines = prop_file.readlines()

        for line in prop_lines:
            parts = line.strip().split(", ")
            if len(parts) >= 1:
                property_name = parts[0].replace("'", "").replace(" ", "").upper()
                properties.append(property_name)
                print("check 1")
                print(str(property_name))
                print(str(word.upper()))
                if str(property_name) == str(word.upper()):
                    print("same")
                    if len(parts) == 6:  # Incorrect ownership
                        await ctx.send("You can't build a hotel on a station, silly! :rolling_eyes:")
                        return
                    if len(parts) < 10 or parts[9] != str(ctx.author.id):  # Incorrect ownership
                        await ctx.send("You don't own this property, silly! :rolling_eyes:")
                        return
                    else:
                        print("same 2")
                        with open("inventory.txt", "r+") as inv_file:
                            inv_lines = inv_file.readlines()

                            for i, line in enumerate(inv_lines):
                                if line.startswith(str(ctx.author.id)):
                                    inv_parts = [p.strip().replace(" ", "").replace("'", "") for p in line.split(',')]
                                    for j, prop_line in enumerate(prop_lines):
                                        prop_parts_og = prop_line.strip().split(", ")
                                        prop_parts = [p.strip().replace(" ", "").replace("'", "") for p in prop_line.split(",")]
                                        print("check1")
                                        print(prop_parts[0].upper())
                                        print(property_name)
                                        if prop_parts[0].upper() == property_name:
                                            print("same3")
                                            if int(inv_parts[1]) < int(prop_parts[6]):
                                                await ctx.send("You don't have enough money to buy a hotel!")
                                                return
                                            elif int(prop_parts[5]) >= 1:
                                                await ctx.send("You already have the maximum number of hotels!")
                                                return
                                            elif int(prop_parts[3]) < 4:
                                                await ctx.send("You still have houses left to buy!")
                                                return
                                            else:
                                                print("same4")
                                                inv_parts[1] = str(int(inv_parts[1]) - int(prop_parts[6]))
                                                prop_parts[5] = str(int(prop_parts[5]) + 1)
                                                print("check 7")
                                                print(prop_parts[0])
                                                print(prop_parts_og[0])
                                                prop_parts[0] = prop_parts_og[0]
                                                
                                                inv_lines[i] = ", ".join(inv_parts) + "\n"
                                                prop_lines[j] = ", ".join(prop_parts) + "\n"

                                                with open("inventory.txt", "w") as inv_file:
                                                    inv_file.writelines(inv_lines)

                                                with open("properties.txt", "w") as prop_file:
                                                    prop_file.writelines(prop_lines)

                                                print("Updated inventory and properties.")
                                                await ctx.send(f"You have bought a hotel at {prop_parts[0]}!")
                                                return

                            print("Property not found!")
                            await ctx.send("Property not found!")
                            return

        print("Word not found!")
        await ctx.send("That property does not exist!")
        return

@bot.command(name="scrabble")
async def scrabble(ctx):
    with open("inventory.txt", "r") as inv_file:
        for line in inv_file:
            parts = line.strip().split(", ")
            if len(parts) >= 2 and parts[0] == str(ctx.author.id):
                letters = " ".join(parts[2:]).upper()
                await ctx.send(f"Your Scrabble letters:\n{letters}")
                return
    await ctx.send("No letters found in your inventory.")   
'''

# EXECUTES THE BOT WITH THE SPECIFIED TOKEN.
bot.run(TOKEN)
