![Holfy Logo](https://holfuy.com/image/logo/holfuy-logo.png)

# PyHolfuy
A Python library for talking to [Holfuy Weather Stations](https://holfuy.com/).

You need an API key to access the service. To obtain one, please visit the [Holfuy API](https://api.holfuy.com/live/) pages.

The Library only access live data.

## Example Code
Here is an example of how to use the library.

```python
import aiohttp
import asyncio
from holfuy import HolfuyService

async def main():
    async with aiohttp.ClientSession() as session:
    s = HolfuyService("", session)
    data = await s.fetch_data(["101"])
    print(data)

if __name__ == "__main__":
    asyncio.run(main())
```
