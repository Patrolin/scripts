from fake_useragent import UserAgent
CHROME = f'{UserAgent().chrome}'
from requests import Session
import urllib3
urllib3.disable_warnings()
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from bs4 import BeautifulSoup as _BeautifulSoup
from collections import defaultdict
from pprint import pprint, pformat
import re
from datetime import datetime, timedelta
from random import randrange

import discord
import asyncio



def BeautifulSoup(*args, **kwargs):
	return _BeautifulSoup(*args, features="lxml", **kwargs)

def decodeTable(e):
	if e.name == 'table':
		return [decodeTable(tr) for tr in e.select('tr')]
	elif e.name == 'tr':
		return [decodeTable(thtd) for thtd in e.select('th,td')]
	elif e.name in {'th', 'td', 'a', 'li'}:
		c = e.select(':not(.tooltip)')
		return decodeTable(c[0] if c else e.contents[0])
	elif e.name == 'ul':
		return ''.join([decodeTable(li) for li in e.select('li')])
	elif e.name == 'img':
		return e['alt'].strip()
	elif e.name == None:
		return e.strip()
	else:
		return str(e)

def decodeMsg(msg):
	prev_data_filtered = [re.split(r'\s{2,}', s.strip()) for s in msg.content[3:-3].split('\n')[1:]]
	for i in range(len(prev_data_filtered)):
		prev_data_filtered[0] = prev_data_filtered[0][:-1]
	return prev_data_filtered

class BlacklistRetry(Retry):
	def is_retry(self, method, status_code, has_retry_after=False):
		if not self._is_method_retryable(method):
			return False
		
		if self.status_forcelist and status_code not in self.status_forcelist:
			return True
		
		return (self.total and self.respect_retry_after_header and
			has_retry_after and (status_code in self.RETRY_AFTER_STATUS_CODES))

s = Session()
s.headers.update({'User-Agent': CHROME})
s.verify = False
retries = BlacklistRetry(total=5,
		          backoff_factor=8,
		          status_forcelist=[ 200, *range(300, 309)])
s.mount('https://', HTTPAdapter(max_retries=retries))

def log_response(r):
	print(f'[{r.status_code}] {r.url}')

async def login():
	r1 = s.get('https://www.stargate-game.cz/')
	log_response(r1)
	await asyncio.sleep(randrange(10, 15))
	
	html = BeautifulSoup(r1.text)
	data = defaultdict(lambda: '')
	for e in html.select('input[name]'):
		attrs = defaultdict(lambda: None, e.attrs)
		if (attrs['checked'] != None if attrs['type'] == 'radio' else attrs['value']):
			data[attrs['name']] = attrs['value']
		else:
			data[attrs['name']]
	
	data[html.select('input[type="text"]')[0]['name']] = 'Patrolin'
	data[html.select('input[type="password"]')[0]['name']] = 'Heslo114'
	pprint(data)
	
	r2 = s.post(f'https://www.stargate-game.cz/', data=data)
	log_response(r2)
	await asyncio.sleep(randrange(5, 10))

async def vesmir():
	r3 = s.get('https://www.stargate-game.cz/vesmir.php?page=1&id_rasa=11')
	log_response(r3)
	await asyncio.sleep(randrange(5, 10))
	return r3



stargating = False

class MyClient(discord.Client):
	async def get_last_own_msg(self, channel):
		return await channel.history().find(lambda m: m.author.id == self.user.id)
	
	async def on_ready(self):
		global stargating
		print(f'Logged on as {self.user}')
		activity = discord.Activity(name='You', type=discord.ActivityType.watching)
		await client.change_presence(status=discord.Status.online, activity=activity)
		if not stargating:
			stargating = True
			stargateGame = self.get_channel(737031567162998864)
			stargateSleep = False
			while True:
				now = datetime.now()
				target = now + timedelta(hours=1 if now.minute >= 1 else 0, minutes=-now.minute, seconds=randrange(16, 32)-now.second, microseconds=-now.microsecond)
				T = (target - now).total_seconds()
				if stargateSleep:
					print(target)
					await asyncio.sleep(T)
				else:
					print(now)
				stargateSleep = True
				
				try:
					r3 = await vesmir()
				except:
					exit()
				html = BeautifulSoup(r3.text)
				if html.find(text=re.compile('údržba')):
					print('Údržba...')
					await stargateGame.send('Údržba...')
					continue
				elif html.find(text=re.compile('přihlašovací')):
					try:
						await login()
						r3 = await vesmir()
						html = BeautifulSoup(r3.text)
					except:
						exit()
				elif not html.select('table'):
					stargateSleep = bool(randrange(2))
					print('Bot error')
					await stargateGame.send('Bot error')
					continue
				html = BeautifulSoup(r3.text)
				data = decodeTable(html.select('table')[0])
				data_filtered = [data[0]] + [row for row in data[1:] if row[6] != 'nelze' and 'D' in row[6]]
				pprint(data_filtered)
				last_own_msg = await self.get_last_own_msg(stargateGame)
				if last_own_msg == None:
					send_msg = True
				else:
					curr_names = {row[1] for row in data_filtered[1:]}
					prev_data_filtered = decodeMsg(last_own_msg)
					prev_names = {m[1] for m in prev_data_filtered}
					send_msg = curr_names != prev_names
				print(last_own_msg.content)
				pprint(prev_names)
				pprint(curr_names)
				s = []
				for row in data_filtered:
					i, jmeno, planety, populace, sila, dobyt, utok, _ = row
					s.append(f'{i: >4}  {jmeno: <16}  {planety: <7}  {populace: <8}  {sila: <11}  {dobyt: <5}  {utok}')
				s = '\n'.join(s)
				if send_msg:
					await stargateGame.send(f'```{s}```')
				await asyncio.sleep(61)
	
	async def on_message(self, message):
		if message.author == self.user:
			return

		if message.content == 'ping':
			await message.channel.send('pong')

TOKEN = # ...
client = MyClient()
client.run(TOKEN)
