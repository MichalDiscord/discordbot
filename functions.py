from role import command_role
from db import command_db
from discord.message import Message
from discord.embeds import Embed
from discord.channel import Channel
from discord.server import Server
from discord import Client
from typing import List
from random import shuffle
import re
import discord

QUOTE_URL_BASE = 'https://discordapp.com/channels/'


async def run_command(r, client, message):
    """コマンドを実行する"""
    msg, reply, no_reply, embed = None, None, None, None
    remark = message.content
    if remark == '/ping':
        msg = 'pong'
    if re.fullmatch('/[0-9]+', remark):
        no_reply = await grouping(message, int(remark[1:]))
    if remark.startswith('/echo '):
        if message.author == discord.User(id='314387921757143040'):
            arg = remark.split('/echo ')[1]
            await client.delete_message(message)
            await client.send_message(message.channel, arg)
        else:
            msg = 'コマンドを実行する権限がありません'
    if remark == '/member_status':
        msg = member_status(message)
    if remark == '/member':
        arg = message.server.member_count
        msg = f'このサーバーには{arg}人のメンバーがいます'
    if remark == '/debug_role':
        embed = discord.Embed(title="role name", description="role id")
        for role in message.server.roles:
            embed.add_field(name=role.name, value=role.id, inline=False)
    if remark == '/debug_server':
        msg = message.server.id
    if remark == '/debug_on':
        msg = toggle_debug_mode(True)
    if remark == '/debug_off':
        msg = toggle_debug_mode(False)
    if remark == '/help':
        embed = get_help(client)
    if remark.startswith('/role'):
        reply = command_role(message)
    if remark.startswith('/create_role'):
        reply = '-> /role -create Role'
    if remark.startswith('/delete_role'):
        reply = '-> /role -delete Role'
    if remark.startswith('/db '):
        reply = command_db(r, message)
    if msg:
        mention = str(message.author.mention) + ' '
        await client.send_message(message.channel, mention + msg)
    if reply:
        mention = str(message.author.mention) + ' '
        await client.send_message(message.channel, mention + reply)
    if no_reply:
        await client.send_message(message.channel, no_reply)
    if embed:
        await client.send_message(
            message.channel,
            message.author.mention,
            embed=embed
        )


async def expand_quote(client: Client, msg: Message) -> None:
    for url in get_urls(msg.content):
        embed = await discordurl2embed(client, msg.server, url)
        await client.send_message(msg.channel, embed=embed)


def compose_embed(channel: Channel, message: Message) -> Embed:
    embed = discord.Embed(
        description=message.content,
        timestamp=message.timestamp)
    embed.set_thumbnail(
        url=message.author.avatar_url)
    embed.set_author(
        name=message.author.display_name)
    embed.set_footer(
        text=message.channel.name,
        icon_url=message.server.icon_url)
    return embed


def get_urls(text: str) -> List[str]:
    pattern = QUOTE_URL_BASE + '[0-9]{18}/[0-9]{18}/[0-9]{18}'
    return re.findall(pattern, text)


async def discordurl2embed(client: Client, server: Server, url: str) -> Embed:
    s_id, c_id, m_id = url.split(QUOTE_URL_BASE)[1].split('/')
    if server.id == s_id:
        channel = server.get_channel(c_id)
        message = await client.get_message(channel, m_id)
        return compose_embed(channel, message)
    else:
        return discord.Embed(title='404')


async def grouping(message: Message, n: int) -> str:
    """ボイスチャットメンバーを班分けする"""
    voicechannel = message.author.voice.voice_channel
    if not voicechannel:
        return 'ボイスチャンネルに入ってコマンドを入力してください'
    members = [m.mention for m in voicechannel.voice_members]
    if len(members) == 0:
        return 'ボイスチャンネルにメンバーがいません'
    shuffle(members)
    groups, g = [], []
    rest = []
    rest_number = len(members) % n
    if rest_number != 0:
        for _ in range(rest_number):
            rest.append(members.pop())
    for i, m in enumerate(members):
        if len(g) < n-1:
            g.append(m)
        else:
            g.append(m)
            tmp = ' '.join(g)
            groups.append(f'{(i+1)//n}班 {tmp}')
            g = []
    if rest:
        groups.append('余り {}'.format(' '.join(rest)))
    return '\n'.join(groups)


def toggle_debug_mode(mode: bool) -> str:
    """デバッグモードのON/OFFを切り替える"""
    global debug_mode
    debug_mode = mode
    return 'デバッグモードを{}にしました'.format('ON' if mode else 'OFF')


def member_status(message: Message) -> str:
    """メンバーが入っているボイスチャンネル名を返す"""
    return message.author.voice.voice_channel.name


def get_help(client: Client) -> Embed:
    """コマンドの一覧と詳細をembedで返す"""
    helps = {
        '`/role`':
            'サーバーの役職一覧を教えます',
        '`/role ROLENAME(s)`':
            '指定した(空白区切り複数の)役職を付与/解除します',
        '`/create_role ROLENAME`':
            '指定した役職を作成します(管理者のみ)',
        '`/delete_role ROLENAME`':
            '指定した役職を削除します(管理者のみ)',
        '`/member`':
            'サーバーのメンバー人数を教えます',
        '`/help`':
            'コマンドの一覧と詳細を表示します',
    }
    embed = discord.Embed(
        title=client.user.name,
        url='https://github.com/1ntegrale9/discordbot',
        description='discord bot w/ discord.py',
        color=0x3a719f)
    embed.set_thumbnail(
        url=client.user.avatar_url)
    for k, v in helps.items():
        embed.add_field(name=k, value=v, inline=False)
    return embed
