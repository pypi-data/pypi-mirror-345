from telethon import TelegramClient
from telethon.tl import types
from telethon.extensions import markdown

def Golden(client, emoji_map):
    def parse_text(text):
        text, entities = markdown.parse(text)
        new_entities = []
        for entity in entities:
            if (isinstance(entity, types.MessageEntityTextUrl) and 
                entity.url.startswith('emoji/')):
                new_entities.append(
                    types.MessageEntityCustomEmoji(
                        offset=entity.offset,
                        length=entity.length,
                        document_id=int(entity.url.split('/')[1])
                ))
            else:
                new_entities.append(entity)
        return text, new_entities

    def unparse_text(text, entities):
        new_entities = []
        for entity in entities or []:
            if isinstance(entity, types.MessageEntityCustomEmoji):
                new_entities.append(
                    types.MessageEntityTextUrl(
                        offset=entity.offset,
                        length=entity.length,
                        url=f'emoji/{entity.document_id}')
                )
            else:
                new_entities.append(entity)
        return markdown.unparse(text, new_entities)

    class CustomParseMode:
        def __init__(self, parse, unparse):
            self.parse = parse
            self.unparse = unparse

    def format_text(text):
        for emoji, emoji_id in emoji_map.items():
            text = text.replace(emoji, f'[{emoji}](emoji/{emoji_id})')
        return text

    client.parse_mode = CustomParseMode(parse_text, unparse_text)
    client.format_with_custom_emojis = format_text
    return client

def Emoji(message):
    if not message.entities:
        return []
    
    emoji_ids = []
    for entity in message.entities:
        if isinstance(entity, types.MessageEntityCustomEmoji):
            emoji_ids.append(str(entity.document_id))
    
    return emoji_ids