from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import InputPeerChannel
import asyncio

class Scraper:
	def __init__(self, api_id: int, api_hash: str):
		self.api_id = api_id
		self.api_hash = api_hash
		self.client = TelegramClient('scraper_session', api_id, api_hash)
		
	async def _connect(self):
		if not self.client.is_connected():
			await self.client.connect()
			if not await self.client.is_user_authorized():
				await self.client.start()
	
	async def get_last_messages(self, channel_link: str, count: int = 100):
		count = int(count)
		await self._connect()
		
		try:
			channel = await self.client.get_entity(channel_link)
			
			messages = await self.client(GetHistoryRequest(
				peer=channel,
				limit=count,
				offset_date=None,
				offset_id=0,
				max_id=0,
				min_id=0,
				add_offset=0,
				hash=0
			))
			
			return messages.messages
			
		except Exception as e:
			print(f"Error getting messages: {str(e)}")
			return []
	
	async def close(self):
		await self.client.disconnect()
