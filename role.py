import discord
from random import randint
import re

NOTICE_INVALID = '不正な形式です。'
NOTICE_404 = '404 Not Found'


def command_role(msg):
    """
    /role
    /role Member
    /role -help
    /role -self
    /role -list
    /role -server
    /role -member Role
    /role -create Role
    /role -delete Role
    /role -give Member *Role
    /role *Role
    """
    if msg.content == '/role':
        return get_rolenames(msg.server.roles)
    args = msg.content.split()
    len_args = len(args)
    if len_args == 2:
        if args[1] == '-self':
            return get_rolenames(msg.author.roles)
        if args[1] == '-list' or args[1] == '-server':
            return get_rolenames(msg.server.roles)
        if args[1] == '-help':
            return get_help()
        if is_mention(args[1]):
            member = mention2member(args[1], msg.server.members)
            return get_rolenames(member.roles)
        return NOTICE_INVALID
    if len_args == 3:
        if args[1] == '-member':
            role = rolename2role(msg.server.roles, args[2])
            if role:
                members = get_members_have_role(msg.server, role)
                if members:
                    return members2membernames(members)
            return NOTICE_404
        if args[1] == '-create':
            return NOTICE_INVALID
            # return await requires_admin(client, message, create_role)
        if args[1] == '-delete':
            return NOTICE_INVALID
            # return await requires_admin(client, message, delete_role)
        return NOTICE_INVALID
    if args[1] == '-give' and is_mention(args[2]):
        return NOTICE_INVALID
    return NOTICE_INVALID
    # return await set_roles(client, message)


def join_strlist(list, sep):
    return sep.join(list)


def members2membernames(members):
    return sorted([m.display_name for m in members])


def is_mention(str):
    return re.fullmatch('<@![0-9]{18}>', str)


def mention2member(mention, members):
    id = re.search('[0-9]{18}', mention).group()
    return discord.utils.get(members, id=id)


def rolename2role(roles, rolename):
    role = discord.utils.find(
        lambda r: r.name.lower() == rolename.lower(), roles)
    return role if role else None


def get_members_have_role(server, role):
    members = sorted([m for m in server.members if role in m.roles])
    return members if members else None


def get_rolenames(roles):
    rolenames = sorted([r.name for r in roles if is_common(r)])
    if rolenames:
        return join_strlist(rolenames, ', ')
    return NOTICE_404


def get_help():
    return NOTICE_404


def is_common(role):
    """役職の権限が通常かどうかをチェックする"""
    if role.is_everyone:
        return False
    if role.managed:
        return False
    if role.permissions.administrator:
        return False
    return True


async def create_role(client, message):
    """役職を作成する"""
    arg = message.content.split('/create_role ')[1]
    if arg.lower() in [role.name.lower() for role in message.server.roles]:
        return 'その役職は既に存在します'
    await client.create_role(
        message.server,
        name=arg,
        mentionable=True,
        color=discord.Colour(generate_random_color()),
    )
    return f'役職 {arg} を作成しました'


async def delete_role(client, message):
    """役職を削除する"""
    arg = message.content.split('/delete_role ')[1].lower()
    role_names = [role.name.lower() for role in message.server.roles]
    if arg in role_names:
        index = role_names.index(arg)
        role = message.server.roles[index]
        await client.delete_role(message.server, role)
        return f'役職 {role.name} を削除しました'
    return f'役職 {arg} は存在しません'


async def set_roles(client, message):
    """指定された役職を付与する"""
    add, rm, pd, nt = [], [], [], []
    role_names = [role.name.lower() for role in message.server.roles]
    for role_name in message.content.split()[1:]:
        if role_name.lower() in role_names:
            index = role_names.index(role_name.lower())
            role = message.server.roles[index]
            if role in message.author.roles:
                rm.append(role)
            elif role.permissions.administrator:
                pd.append(role)
            else:
                add.append(role)
        else:
            nt.append(role_name)
    msg = ''
    if add:
        await client.add_roles(message.author, *add)
        msg = msg + '\n役職 {} を付与しました'.format(', '.join([r.name for r in add]))
    if rm:
        await client.remove_roles(message.author, *rm)
        msg = msg + '\n役職 {} を解除しました'.format(', '.join([r.name for r in rm]))
    if pd:
        msg = msg + '\n役職 {} は追加できません'.format(', '.join([r.name for r in pd]))
    if nt:
        msg = msg + '\n役職 {} は存在しません'.format(', '.join(nt))
    return msg


def generate_random_color():
    """カラーコードを10進数で返す"""
    rgb = [randint(0, 255) for _ in range(3)]
    return int('0x{:X}{:X}{:X}'.format(*rgb), 16)


async def requires_admin(client, message, func):
    """管理者のみ関数を実行する"""
    if message.author.server_permissions.administrator:
        return await func(client, message)
    return '実行する権限がありません'
