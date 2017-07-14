#!/bin/env python

import discord
import wikipedia
import textwrap
from discord.ext import commands


class Wiki():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command(name="wiki", aliases=['wi'])
    async def wiki_search(self, *args):
        """ Get the closest matching Wikipedia article for query """

        query = " ".join(args)

        # Create initial embed
        em = discord.Embed()

        # Neat wiki icon
        em.set_thumbnail(
            url="https://lh5.ggpht.com/1Erjb8gyF0RCc9uhnlfUdbU603IgMm-G-Y3aJuFcfQpno0N4HQIVkTZERCTo65Iz2II=w300")

        # No query input
        # Returns random article
        if not args:
            em.title = wikipedia.random(pages=1)
            page = wikipedia.page(title=em.title)
            em.description = textwrap.shorten(
                page.summary, width=240, placeholder="...")
            em.url = page.url
            return await self.bot.say(embed=em)

        # Search for page name
        page_title = wikipedia.search(query)[0]

        # No pages found
        if not page_title:
            return await self.bot.say("Sorry, couldn't find anything for `{}`".format(query))

        # Page object
        page = wikipedia.page(title=page_title)

        # Create embed
        em.title = page.title
        em.description = textwrap.shorten(
            page.summary, width=240, placeholder="...")
        em.url = page.url

        return await self.bot.say(embed=em)


def setup(bot):
    bot.add_cog(Wiki(bot))
