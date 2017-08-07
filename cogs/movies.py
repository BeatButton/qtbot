#!/bin/env python

import discord
import json
from discord.ext import commands
import tmdbsimple as tmdb

# TMDb info
with open("data/apikeys.json") as f:
    tmdb.API_KEY = json.load(f)["tmdb"]


class Movies:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="movie", aliases=['mov'])
    async def get_movie(self, ctx, *args):
        """ Get movie information """
        search = tmdb.Search()

        response = search.movie(query=" ".join(args))

        s_results = search.results

        if not s_results:
            return await ctx.send("Sorry, couldn't find that one.")

        rating = float(s_results[0]['vote_average'])
        if (rating < 7.0):
            rec = "This is not a qtbot™ recommmended film."
        else:
            rec = "This is a qtbot™ recommended film."

        # For getting poster
        base_image_uri = "https://image.tmdb.org/t/p/w185{}"

        # Create embed
        em = discord.Embed()
        em.title = "{} ({})".format(
            s_results[0]["title"], s_results[0]["release_date"].split('-')[0])
        em.description = s_results[0]["overview"]
        em.set_thumbnail(url=base_image_uri.format(
            s_results[0]["poster_path"]))
        em.add_field(name="Rating", value=str(rating))
        em.set_footer(text=rec)

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Movies(bot))
