#!/bin/evn python
import discord
import json
import asyncio
from utils import aiohttp_wrap as aw
from discord.ext import commands


class News:
    def __init__(self, bot):
        self.bot = bot
        self.redis_client = bot.redis_client
        self.aio_session = bot.aio_session
        self.uri = 'https://newsapi.org/v1/articles?source=google-news&sortBy=top&apiKey={}'
        with open('data/apikeys.json') as f:
            self.api_key = json.load(f)['news']

    def json_to_embed(json_dict):
        em = discord.Embed()
        em.title = json_dict['title']
        em.description = json_dict['description']
        em.url = json_dict['url']
        em.set_image(url=json_dict['urlToImage'])
        em.set_thumbnail(
            url='http://icons.iconarchive.com/icons/dtafalonso/android-lollipop/512/News-And-Weather-icon.png')

        return em

    @commands.command(name='news')
    async def get_news(self, ctx):
        """ Get the top 5 articles from Google News (http://newsapi.org) (Paginated) """

        """
        Here's my dream:
           1. Check whether cached response exists
           2. Return that information or make the API call
           3. Map each field of the json response to an embed field
                - Make the footer of the embed the page currently displayed
           - The bot sends the first article in this format from a list of pre-fabricated embeds
            - I can get the message object which was sent by assigning the ctx.send to a variable
                - Add 1 - 5 emoji reactions along with first/last buttons
                - When the user clicks on one (on_reaction_add / on_reaction_remove) go to that page with:
                    - discord.Message.edit
        """

        em_list = []

        if await self.redis_client.exists('news'):
            raw_json_string = await self.redis_client.get('news')
            raw_json_dict = json.loads(raw_json_string)
            article_list = raw_json_dict['articles']

            for article in article_list:
                em_list.append(News.json_to_embed(article))

        else:
            api_response = await aw.aio_get_json(self.aio_session, self.uri.format(self.api_key))
            article_list = api_response['articles']
            await self.redis_client.set('news', json.dumps(api_response), ex=300)

            for article in article_list:
                em_list.append(News.json_to_embed(article))


        current_em_index = 0

        bot_message = await ctx.send(embed=em_list[current_em_index])

        # Add Emojis for navigation
        emoji_map = ['1\U000020e3', '2\U000020e3', '3\U000020e3', '4\U000020e3', '5\U000020e3']
        for emoji in emoji_map:
            await bot_message.add_reaction(emoji)

        # Hacked together but works
        def check(reaction, user):
            return user == ctx.author and reaction.emoji in emoji_map

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                return await bot_message.clear_reactions()

            if reaction.emoji == emoji_map[0]:
                # Page 1
                current_em_index = 0
                await bot_message.edit(embed=em_list[0])
                await bot_message.remove_reaction(reaction.emoji, ctx.author)

            if reaction.emoji == emoji_map[1]:
                # Page 2
                current_em_index = 1
                await bot_message.edit(embed=em_list[1])
                await bot_message.remove_reaction(reaction.emoji, ctx.author)

            if reaction.emoji == emoji_map[2]:
                # Page 3
                current_em_index = 2
                await bot_message.edit(embed=em_list[2])
                await bot_message.remove_reaction(reaction.emoji, ctx.author)

            if reaction.emoji == emoji_map[3]:
                # Page 4
                current_em_index = 3
                await bot_message.edit(embed=em_list[3])
                await bot_message.remove_reaction(reaction.emoji, ctx.author)

            if reaction.emoji == emoji_map[4]:
                # Page 5
                current_em_index = 4
                await bot_message.edit(embed=em_list[4])
                await bot_message.remove_reaction(reaction.emoji, ctx.author)


def setup(bot):
    bot.add_cog(News(bot))
