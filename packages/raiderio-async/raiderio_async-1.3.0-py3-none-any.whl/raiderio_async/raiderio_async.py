from datetime import timedelta

from aiohttp_client_cache import SQLiteBackend
from aiohttp_client_cache.session import CachedSession
from aiolimiter import AsyncLimiter


class RaiderIO:
    def __init__(self, api_key: str | None = None):
        self.limiter = AsyncLimiter(max_rate=300, time_period=60)
        self.api_key = api_key
        if self.api_key:
            self.limiter.max_rate = 1000

        self.session = CachedSession(
            cache=SQLiteBackend(
                "raiderio-cache",
                use_temp=True,
                expire_after=timedelta(minutes=1),
                allowed_codes=(200,),
            )
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.session.delete_expired_responses()
        await self.session.close()

    async def _get_resource(self, resource: str, params: dict):
        base = "https://raider.io"
        resource_url = f"{base}{resource}"

        # As of 03/05/2025 the API key isn't required and is only there if the user wants a higher rate limit.
        if self.api_key:
            params["access_key"] = self.api_key

        async with self.limiter:
            async with self.session.get(resource_url, params=params) as response:
                if response.from_cache:
                    await self.limiter.acquire(-1)
                return await response.json()

    # Character APIs

    async def get_character_profile(
        self, region: str, realm: str, name: str, fields: list | None = None
    ) -> dict:
        """
        Retrieve information about a character.

        :param region: Name of region to look up character in.
        :param realm: Name of realm that character is on.
        :param name: Name of the character to look up.
        :param fields: List of fields to retrieve for this character.
        :return: A dictionary containing information about a character.
        """
        resource = "/api/v1/characters/profile"
        query_params = {
            "region": region,
            "realm": realm,
            "name": name,
        }
        if fields:
            query_params["fields"] = ",".join(fields)
        return await self._get_resource(resource, query_params)

    # Guild APIs

    async def get_guild_boss_kill(
        self, region: str, realm: str, guild: str, raid: str, boss: str, difficulty: str
    ) -> dict:
        """
        Retrieve information about a guild's boss kill.

        :param region: Name of region to look up guild in.
        :param realm: Name of realm that guild is on.
        :param guild: Name of the guild to look up.
        :param raid: Raid slug to look up.
        :param boss: Boss slug to look up
        :param difficulty: Raid difficulty to look up.
        :return: A dictionary containing information about a guild's boss kill.
        """
        resource = "/api/v1/guilds/boss-kill"
        query_params = {
            "region": region,
            "realm": realm,
            "guild": guild,
            "raid": raid,
            "boss": boss,
            "difficulty": difficulty,
        }
        return await self._get_resource(resource, query_params)

    async def get_guild_profile(
        self, region: str, realm: str, name: str, fields: list | None = None
    ) -> dict:
        """
        Retrieve information about a guild.

        :param region: Name of region to look up guild in.
        :param realm: Name of realm that guild is on.
        :param name: Name of the guild to look up.
        :param fields: List of fields to retrieve for this guild.
        :return: A dictionary containing information about a guild.
        """
        resource = "/api/v1/guilds/profile"
        query_params = {
            "region": region,
            "realm": realm,
            "name": name,
        }
        if fields:
            query_params["fields"] = ",".join(fields)
        return await self._get_resource(resource, query_params)

    async def get_guild_roster(self, region: str, realm: str, guild: str) -> dict:
        """
        Retrieve information about a guild's roster.

        :param region: Name of region to look up guild in.
        :param realm: Name of realm that guild is on.
        :param guild: Name of the guild to look up.
        :return: A dictionary containing information about a guild's roster.
        """
        resource = "/api/guilds/roster"
        query_params = {
            "region": region,
            "realm": realm,
            "guild": guild,
        }
        return await self._get_resource(resource, query_params)

    # Mythic Plus APIs

    async def get_mythic_plus_affixes(self, region: str, locale: str | None = None) -> dict:
        """
        Retrieve the affixes for a specific region.

        :param region: Name of region to look up affixes for.
        :param locale: Language to return name and description of affixes in.
        :return: A dictionary containing information about affixes.
        """
        resource = "/api/v1/mythic-plus/affixes"
        query_params = {"region": region}
        if locale:
            query_params["locale"] = locale
        return await self._get_resource(resource, query_params)

    async def get_mythic_plus_leaderboard_capacity(
        self, region: str, scope: str | None = None, realm: str | None = None
    ) -> dict:
        """
        Retrieve the leaderboard capacity for a region including the
        lowest level and time to qualify.

        :param region: Name of region to retrieve runs for.
        :param scope: Week to retrieve the capacity info for.
        :param realm: Name of realm to retrieve runs for.
        :return: A dictionary containing information about the leaderboard capacity.
        """
        resource = "/api/v1/mythic-plus/leaderboard-capacity"
        query_params = {"region": region}
        if scope:
            query_params["scope"] = scope
        if realm:
            query_params["realm"] = realm
        return await self._get_resource(resource, query_params)

    async def get_mythic_plus_runs(
        self,
        season: str | None = None,
        region: str | None = None,
        dungeon: str | None = None,
        affixes: list | None = None,
        page: int | None = None,
    ) -> dict:
        """
        Retrieve information about the top runs that match the given criteria.

        :param season: Name of season to request data for.
        :param region: Name of region to request runs for
        :param dungeon: Name of dungeon to filter by.
        :param affixes: List of affixes to restrict the results to.
        :param page: Page number
        :return: A dictionary containing information about the top runs.
        """
        resource = "/api/v1/mythic-plus/runs"
        query_params = {}
        if season:
            query_params["season"] = season
        if region:
            query_params["region"] = region
        if dungeon:
            query_params["dungeon"] = dungeon
        if affixes:
            query_params["affixes"] = "-".join(affixes)
        if page:
            query_params["page"] = page
        return await self._get_resource(resource, query_params)

    async def get_mythic_plus_score_tiers(self, season: str | None = None) -> list:
        """
        Retrieve the colors used for score tiers in the given season.

        :param season: Name of the season to retrieve.
        :return: A list of colors used for score tiers.
        """
        resource = "/api/v1/mythic-plus/score-tiers"
        query_params = {}
        if season:
            query_params["season"] = season
        return await self._get_resource(resource, query_params)

    async def get_mythic_plus_season_cutoffs(self, region: str, season: str) -> dict:
        """
        Retrieve the Mythic+ Season cutoffs for a region.

        :param region: Region to receive cutoffs for.
        :param season: Season to retrieve cutoffs for.
        :return: A dictionary containing information about the Mythic+ Season cutoffs.
        """
        resource = "/api/v1/mythic-plus/season-cutoffs"
        query_params = {"region": region, "season": season}
        return await self._get_resource(resource, query_params)

    async def get_mythic_plus_static_data(self, expansion_id: int) -> dict:
        """
        Retrieve mythic plus season and dungeon static data for a
        specific expansion (slugs, names, etc.)

        :param expansion_id: Expansion ID to get slugs for.
        :return: A dictionary containing season and dungeon static data.
        """
        resource = "/api/v1/mythic-plus/static-data"
        query_params = {"expansion_id": expansion_id}
        return await self._get_resource(resource, query_params)

    # Raiding APIs

    async def get_raid_boss_rankings(
        self, raid: str, boss: str, difficulty: str, region: str, realm: str | None = None
    ) -> dict:
        """
        Retrieve the boss rankings for a given raid and region.

        :param raid: Raid to look up.
        :param boss: Slug of boss to look up
        :param difficulty: Raid difficulty to look up.
        :param region: Name of region to restrict to.
        :param realm: Name of realm to restrict to.
        :return: A dictionary containing information about the boss rankings.
        """
        resource = "/api/v1/raiding/boss-rankings"
        query_params = {
            "raid": raid,
            "boss": boss,
            "difficulty": difficulty,
            "region": region,
        }
        if realm:
            query_params["realm"] = realm
        return await self._get_resource(resource, query_params)

    async def get_raid_hall_of_fame(self, raid: str, difficulty: str, region: str) -> dict:
        """
        Retrieve the hall of fame for a given raid.

        :param raid: Raid to look up.
        :param difficulty: Raid difficulty to look up.
        :param region: Name of region to restrict to.
        :return: A dictionary containing information about the hall of fame.
        """
        resource = "/api/v1/raiding/hall-of-fame"
        query_params = {"raid": raid, "difficulty": difficulty, "region": region}
        return await self._get_resource(resource, query_params)

    async def get_raid_progression(self, raid: str, difficulty: str, region: str) -> dict:
        """
        Retrieve details of raiding progression for a raid.

        :param raid: Raid to look up.
        :param difficulty: Raid difficulty to look up.
        :param region: Name of region to restrict to.
        :return: A dictionary containing information about the raiding progression of a region.
        """
        resource = "/api/v1/raiding/progression"
        query_params = {"raid": raid, "difficulty": difficulty, "region": region}
        return await self._get_resource(resource, query_params)

    async def get_raid_rankings(
        self,
        raid: str,
        difficulty: str,
        region: str,
        realm: str | None = None,
        guilds: list | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> dict:
        """
        Retrieve the raid rankings for a given raid and region.

        :param raid: Raid to look up.
        :param difficulty: Raid difficulty to look up.
        :param region: Name of region to restrict to.
        :param realm: Name of realm to restrict to.
        :param guilds: Guild IDs of guilds to restrict the results to.
        :param limit: Number of results to limit to.
        :param page: Page number.
        :return: A dictionary containing the raid rankings.
        """
        resource = "/api/v1/raiding/raid-rankings"
        query_params = {
            "raid": raid,
            "difficulty": difficulty,
            "region": region,
        }
        if realm:
            query_params["realm"] = realm
        if guilds:
            query_params["guilds"] = ",".join(guilds)
        if limit:
            query_params["limit"] = limit
        if page:
            query_params["page"] = page
        return await self._get_resource(resource, query_params)

    async def get_raid_static_data(self, expansion_id: int) -> dict:
        """
        Retrieve raid and boss static data for a specific expansion (slugs, names, etc.)

        :param expansion_id: Expansion ID to get slugs for.
        :return: A dictionary containing raid and boss static data.
        """
        resource = "/api/v1/raiding/static-data"
        query_params = {"expansion_id": expansion_id}
        return await self._get_resource(resource, query_params)
