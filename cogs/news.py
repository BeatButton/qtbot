#!/bin/evn python
import discord
import json
import asyncio
from utils import aiohttp_wrap as aw
from discord.ext import commands

async def on_reaction_add(reaction, user):
    # def check():
    #     if user == ctx.author:
    #         if str(r) == 'BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR':
    #             return {'index_add': 1}
    #         if str(r) == 'BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR':
    #             return {'index_sub': 1}
    #         if str(r) == 'DIGIT ONE':
    #             return {'index_set': 1}
    #         if str(r) == 'DIGIT TWO':
    #             return {'index_set': 2}
    #         if str(r) == 'DIGIT THREE':
    #             return {'index_set': 3}
    #         if str(r) == 'DIGIT FOUR':
    #             return {'index_set': 4}
    #         if str(r) == 'DIGIT FIVE':
    #             return {'index_set': 5}

    def check():
        print('Wew lad')

    await self.bot.wait_for('reaction_add', check=check, timeout=120)

    # await self.bot.wait_for('reaction_add', check=check, timeout=120)

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
        """ Get the top 5 articles from Google News (http://newsapi.org """

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
        emoji_map = ['\U000023ee', '\U000023ed', '1\U000020e3', '2\U000020e3', '3\U000020e3', '4\U000020e3', '5\U000020e3']
        for emoji in emoji_map:
            await bot_message.add_reaction(emoji)


def setup(bot):
    bot.add_cog(News(bot))
