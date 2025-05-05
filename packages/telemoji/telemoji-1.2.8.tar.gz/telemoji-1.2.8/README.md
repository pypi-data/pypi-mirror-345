# Telemoji Library

Advanced custom emoji handler for Telethon .

## Installation
```bash
pip install telemoji
```

## Usage

### Basic Setup
```python
import telemoji
from telethon import TelegramClient

client = TelegramClient('session', api_id, api_hash)
```

### Golden Method (Emoji Conversion)
```python
emoji_map = {
    '✨': '5280790529565536648',
    '💃🏻': '5280790529565536648'
}

telemoji.Golden(client, emoji_map)
```

### Emoji Extraction
```python
@client.on(events.NewMessage)
async def handler(event):
    emoji_ids = telemoji.Emoji(event.message)
    if emoji_ids:
        print("Found custom emojis:", emoji_ids)
```

## Features
- Convert regular emojis to custom emojis
- Extract custom emoji IDs from messages
- Works with all Telethon send methods