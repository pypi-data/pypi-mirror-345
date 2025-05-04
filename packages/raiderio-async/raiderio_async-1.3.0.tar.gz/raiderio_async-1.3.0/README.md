# raiderio-async

A simple async library for the [Raider.IO](https://raider.io/) API made primarily for a Discord bot.

# Example

```python
from raiderio_async import RaiderIO

async with RaiderIO() as rio:
    affixes = await rio.get_mythic_plus_affixes("eu")
```
