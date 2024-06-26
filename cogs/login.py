# hunt.py
import discord
from discord.ext import commands, tasks
# from utils.db import DBase
from utils.db2 import DBase
import datetime



# A cog for storing login info and google links for team
# !login
# !login update


class LoginCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    def check_role(self,member,role):
        ''' member: ctx.author, role: integer discord ID '''

        return True
        #if isinstance(role,int):
        #    return discord.utils.get(member.roles, id=role)


    async def infofetch(self,ctx):        
        ''' fetch and display team login and links info '''
        
        # db fields  = hunt_url, hunt_username, hunt_password, hunt_folder, hunt_nexus, hunt_role_id
        # bot fields = site, user, pswd, folder, nexus, role

        db = DBase(ctx)
        try:
            res = db.hunt_get_row(ctx.guild.id, ctx.message.channel.category.id)
        except Exception as e:
            await ctx.send(str(e))
            return False
        
        # parse results
        field0 = '**Team**: '+str(res['hunt_team_name'])+'\n'
        field1 = '**Website**: '+str(res['hunt_url'])+'\n'
        field2 = '**Username**: '+str(res['hunt_username'])+'\n'
        field3 = '**Password**: '+str(res['hunt_password'])+'\n'
        if res['hunt_folder'].find('http') != -1:
            field4 = '**Folder**: [Link here]('+str(res['hunt_folder'])+')\n'
        else: 
            field4 = '**Folder**: '+str(res['hunt_folder'])+'\n'
        if res['hunt_nexus'].find('http') != -1:
            field5 = '**Nexus**: [Link here]('+str(res['hunt_nexus'])+')\n'
        else: 
            field5 = '**Nexus**: '+str(res['hunt_nexus'])+'\n'
        final = field0+field1+field2+field3+field4+field5
        role = res['hunt_role_id']

        # set up embed
        embed = discord.Embed(
                colour=discord.Colour.gold(),
                description=final
            )

        # role should be either 'none' or numeric ID       
        if role == 'none':
            embed.set_footer(text='Role: '+role)
            await ctx.send(embed=embed)
            return
        roleID = int(role)
        if self.check_role(ctx.author, roleID):
            roleName = discord.utils.get(ctx.guild.roles, id=roleID)
            embed.set_footer(text='Role: '+str(roleName))
            await ctx.send(embed=embed)
        else:
            await ctx.send('Missing role for the current hunt.')



    async def infoupdate(self,ctx,query):
        '''
        query: list of arguments to update in form ['field1=text1','field2=text2'] \n
        '''

        updatedata = []
        for item in query:
            field,value = item.split('=',1)

            if field == 'role' or field == 'r':
                if value == 'none':
                    updatedata.append(('hunt_role_id','none'))
                else:
                    try:
                        roleID = int(value)
                    except:
                        await ctx.send('Role must be either `none` or id number.')
                        return
                    updatedata.append(('hunt_role_id',roleID))
            elif field == 'username' or field == 'user' or field == 'uname' or field == 'u':
                updatedata.append(('hunt_username',str(value)))
            elif field == 'password' or field == 'pswd' or field == 'pass' or field == 'p':
                updatedata.append(('hunt_password',str(value)))
            elif field == 'website' or field == 'site' or field == 'w':
                updatedata.append(('hunt_url',str(value)))
            elif field == 'folder' or field == 'f':
                updatedata.append(('hunt_folder',str(value)))
            elif field == 'nexus' or field == 'n':
                updatedata.append(('hunt_nexus',str(value)))
            elif field == 'teamname' or field == 'team' or field == 'name' or field == 't':
                updatedata.append(('hunt_team_name', str(value)))
            elif field == 'logfeed' or field == 'l':
                updatedata.append(('hunt_logfeed', str(value)))
            else:
                await ctx.send('Flag does not exist: '+field)


        # update db
        db = DBase(ctx)
        await db.hunt_update_row(updatedata, ctx.guild.id, ctx.message.channel.category.id)
            


    @commands.command(aliases=['info','login'])
    @commands.guild_only()
    async def huntinfo(self, ctx, *, query=None):
        helpstate = '`!login update '\
                    '[-role=<id>] [-username=<username>] [-password=<password>] [-website=<url>] [-folder=<url>] [-nexus=<url>] [-teamname=<teamname>]`'

        # fetch hunt info
        if not query:
            await self.infofetch(ctx)
            return

        # update hunt info
        quers = query.split(' -')
        if quers[0] in ['update','set']:
            
            # return help
            if len(quers) == 1:
                await ctx.send(helpstate)
                return

            await self.infoupdate(ctx,quers[1:])
            
        else:
            await ctx.send('I don\'t understand that...\n'+helpstate)


async def setup(bot):
    await bot.add_cog(LoginCog(bot))

