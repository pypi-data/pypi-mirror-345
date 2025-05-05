# Tzafon Waypoint

A Python client for interacting with the tzafon.ai API for web automation.

## Installation

```bash
pip install tzafon
```

## Usage

```python
import asyncio
from tzafon import Waypoint

async def main():
    async with Waypoint(token="wpk_your_token_here") as wp:
        # Navigate to a website
        await wp.goto("https://example.com")

        # Take a screenshot
        image_bytes = await wp.screenshot("screenshot.jpg")

        # Click at a specific position
        await wp.click(100, 200)

        # Type some text
        await wp.type("Hello world")

        # Scroll down
        await wp.scroll(dy=200)

if __name__ == "__main__":
    asyncio.run(main())
```

## Features

- Web navigation
- Screenshots
- Clicking and typing
- Scrolling
- Viewport control

## License

MIT
