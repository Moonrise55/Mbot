# archive.py

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import gspread
import json
import asyncio

from gspread import WorksheetNotFound
from gspread.exceptions import APIError
from google.oauth2 import service_account


# A cog for archiving channels and categories
# !archive

class ArchiveCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
        # TODO: has to be a less silly way to organize this
        load_dotenv()
        self.key = os.getenv('GOOGLE_CLIENT_SECRETS')
        self.googledata = json.loads(self.key)
        self.googledata['private_key'] = self.googledata['private_key'].replace("\\n", "\n")
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.credentials = service_account.Credentials.from_service_account_info(self.googledata, scopes=scopes)

    def gclient(self):
        client = gspread.authorize(self.credentials)
        return client

    @commands.command(aliases=['arc'])
    @commands.has_role('organiser')
    @commands.guild_only()
    async def archive(self, ctx, *args):
        # ensure exactly two arguments
        if len(args) != 2:
            await ctx.send('`!archive <channel|category> <sheet>`')
            return

        # attempt an archive, catch any errors with the sheet link
        try:
            if args[0] == 'channel':
                await self.archive_channel(ctx, ctx.channel, args[1], True)
            elif args[0] == 'category' or args[0] == 'cat':
                await self.archive_category(ctx, args[1])
            else:
                await ctx.send('`!archive <channel|category> <sheet>`')
        # handle most common errors
        except APIError as e:
            code = json.loads(e.response.text)['error']['code']
            if code == 404:
                await ctx.send('An error occurred during archiving: Sheet does not exist.')
            elif code == 403:
                await ctx.send('An error occurred during archiving: M-Bot does not have access to the archive sheet.')
            elif code == 429:
                await ctx.send('An error occurred during archiving: Data quota exceeded.')
            else:
                await ctx.send('An unknown error occurred during archiving.')

    async def archive_category(self, ctx, sheet_url):
        category = ctx.message.channel.category
        status = await ctx.message.channel.send('Archiving category {}...'.format(category))
        # only archive text channels
        for channel in category.text_channels:
            await self.archive_channel(ctx, channel, sheet_url, False)
            # sleep for three seconds to dodge API data cap
            await asyncio.sleep(3)
        await status.edit(content='Category {} archived!'.format(category))

    async def archive_channel(self, ctx, channel, sheet_url, log):
        status = await ctx.message.channel.send('Archiving channel {}...'.format(channel.mention))

        messages = []
        images_all = []
        async for msg in channel.history(limit=None, oldest_first=True):
            # record each message
            messages.append([
                msg.created_at.strftime('%m-%d-%Y, %H:%M:%S'),
                msg.author.display_name,
                msg.clean_content
            ])

            # record attachments for each message
            for attachment in msg.attachments:
                messages.append([
                    '->',
                    '->',
                    '=IMAGE("' + attachment.url + '")'
                ])
                images_all.append('Image: <'+attachment.url+'>')
        
        # send links if attachments exist
        if images_all:
            images_all = '\n'.join(images_all)
            await ctx.send(images_all)

        # set up workbook information
        sheet_key = max(sheet_url.split('/'), key=len)
        gclient = self.gclient()
        wkbook = gclient.open_by_key(sheet_key)

        # replace channel sheet if it exists
        try:
            sheet = wkbook.worksheet(channel.name)
            sheet.delete_rows(1, sheet.row_count - 1)
        except WorksheetNotFound:
            sheet = wkbook.add_worksheet(channel.name, 1, 3)

        # JSON request for resizing columns
        resize_cols_request = {
            'requests': [{
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': sheet.id,
                        'dimension': "COLUMNS",
                        'startIndex': 0,
                        'endIndex': 3
                    }
                }
            }]
        }

        # input data into workbook
        sheet.insert_rows(messages, value_input_option='USER_ENTERED')
        wkbook.batch_update(resize_cols_request)

        await status.edit(content='Channel {} archived!'.format(channel.mention))
        if not log:
            await status.delete()


def setup(bot):
    bot.add_cog(ArchiveCog(bot))

