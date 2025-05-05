import requests
import json
from typing import Dict, List, Union, Optional

class DiscordWebhook:
    
    @staticmethod
    def send(webhook_url: str, content: str = None, embeds: List[Dict] = None, 
             username: str = None, avatar_url: str = None) -> requests.Response:
        payload = {}
        
        if content:
            payload["content"] = content
        
        if embeds:
            payload["embeds"] = embeds
            
        if username:
            payload["username"] = username
            
        if avatar_url:
            payload["avatar_url"] = avatar_url
            
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(webhook_url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()  
        return response
    
    @staticmethod
    def create_embed(title: str = None, description: str = None, color: int = None,
                    url: str = None, timestamp: str = None, footer: Dict = None,
                    image: Dict = None, thumbnail: Dict = None, author: Dict = None,
                    fields: List[Dict] = None) -> Dict:
        embed = {}
        
        if title:
            embed["title"] = title
            
        if description:
            embed["description"] = description
            
        if color:
            embed["color"] = color
            
        if url:
            embed["url"] = url
            
        if timestamp:
            embed["timestamp"] = timestamp
            
        if footer:
            embed["footer"] = footer
            
        if image:
            embed["image"] = image
            
        if thumbnail:
            embed["thumbnail"] = thumbnail
            
        if author:
            embed["author"] = author
            
        if fields:
            embed["fields"] = fields
            
        return embed

    
    @staticmethod
    def quick_embed(title: str = None, description: str = None, 
                   color: int = None, url: str = None) -> Dict:
        return DiscordWebhook.create_embed(title=title, description=description, color=color, url=url)
    
    @staticmethod
    def add_field(embed: Dict, name: str, value: str, inline: bool = False) -> Dict:
        if "fields" not in embed:
            embed["fields"] = []
            
        embed["fields"].append({
            "name": name,
            "value": value,
            "inline": inline
        })
        
        return embed
    
    @staticmethod
    def set_footer(embed: Dict, text: str, icon_url: str = None) -> Dict:
        footer = {"text": text}
        if icon_url:
            footer["icon_url"] = icon_url
            
        embed["footer"] = footer
        return embed
    
    @staticmethod
    def set_author(embed: Dict, name: str, url: str = None, icon_url: str = None) -> Dict:
        author = {"name": name}
        if url:
            author["url"] = url
        if icon_url:
            author["icon_url"] = icon_url
            
        embed["author"] = author
        return embed
    
    @staticmethod
    def set_image(embed: Dict, url: str) -> Dict:
        embed["image"] = {"url": url}
        return embed
    
    @staticmethod
    def set_thumbnail(embed: Dict, url: str) -> Dict:
        embed["thumbnail"] = {"url": url}
        return embed
    


"""
Example Usage:
"""
#from rescore09 import discordWebhook
#
## Create the base embed
#embed = discordWebhook.create_embed(
#    title="Rich Embed",
#    description="A more detailed embed example",
#    color=0x3498db  # Blue color
#)
#
## Add fields
#discordWebhook.add_field(embed, "Field 1", "This is a regular field")
#discordWebhook.add_field(embed, "Field 2", "This is an inline field", inline=True)
#discordWebhook.add_field(embed, "Field 3", "Another inline field", inline=True)
#
## Set footer, author, and image
#discordWebhook.set_footer(embed, "Footer text", "https://example.com/footer-icon.png")
#discordWebhook.set_author(embed, "Author Name", "https://example.com", "https://example.com/author-icon.png")
#discordWebhook.set_image(embed, "https://example.com/image.png")
#discordWebhook.set_thumbnail(embed, "https://example.com/thumbnail.png")
#
## Send message with embed
#discordWebhook.send(
#    "https://discord.com/api/webhooks/your-webhook-url",
#    content="Check out this embed!",
#    embeds=[embed]
#)