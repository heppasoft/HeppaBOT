import re
import json
import time
import pickle
import codecs
import random
import modules
import smtplib
import discord
import functools
import subprocess
import typing as t
from modules import constants
from os import path as os_path
from operator import attrgetter
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image, ImageChops, ImageDraw

__all__ = [
    "log",
    "get",
    "find",
    "is_exists",
    "bot_count",
    "send_email",
    "member_count",
    "has_ayn_role",
    "create_embed",
    "load_json_file",
    "dump_json_file",
    "load_data_files",
    "dump_data_files",
    "split_arg_string",
    "create_data_files",
    "get_circled_image",
    "strftime_translate",
    "generate_random_code",
    "execute_shell_command",
    "send_verifaction_email",
    "validate_university_email",
    "html_formatter"
]

T = t.TypeVar("T")


def load_data_files(filePath: str) -> t.Any:
    """
        Load decoded data files with pickle.

        :param filePath: File path.
        :type filePath: str
        :returns: File datas.
        :rtype: Any
    """
    return pickle.loads(codecs.decode(open(filePath, "rb").read(), "zlib"))


def dump_data_files(filePath: str, data: t.Any) -> None:
    """
        Dump encoded data files with pickle.

        :param filePath: File path.
        :param data: File data.
        :type filePath: str
        :type : Any
    """
    open(filePath, "wb").write(codecs.encode(pickle.dumps(data), "zlib"))


def create_data_files(filePath: str) -> None:
    """
        Create data files with pickle.

        :param filePath: File path.
        :type filePath: str
    """
    open(filePath, "wb").write(codecs.encode(pickle.dumps({}), "zlib"))


def load_json_file(filePath: str) -> dict:
    """
        Load json file.

        :param filePath: File path.
        :type filePath: str
        :returns: Json data.
        :rtype: dict
    """
    with open(filePath) as fp:
        data = json.load(fp)
    return data


def dump_json_file(filePath: str, data: dict) -> None:
    """
        Dump json data to file.

        :param filePath: File path.
        :param: Json data.
        :type filePath: str
        :type: dict
    """
    with open(filePath, "w") as fp:
        json.dump(data, fp)


def is_exists(path: str) -> bool:
    """
        Check if path exists.

        :param path: The path to check.
        :type path: str
        :rtype: bool
    """
    return os_path.exists(path)


def log(msg: str, level: str = "info"):
    """
        Print log.

        :param level: Log level.
        :param msg: Log message.
        :type level: str
        :type msg: str
    """
    levels = {"info": "[INFO]", "warning": "[WARNING]", "error": "[ERROR]", "dev": "[DEVELOP]"}
    
    print(f"{time.strftime('%d.%m.%YT%H:%M:%S')} :: {levels[level]} {msg}")


def find(predicate: t.Callable[[T], t.Any], seq: t.Iterable[T], only_first = False) -> t.Union[T, list[T]] | None:
    """
        Return the elements found in the sequence that meets the predicate.
        If an entry is not found, then ``None`` is returned.

         Examples
        ---------

        Basic usage:

        .. code-block:: python3

            member = find(lambda m: m.name == 'Mighty', [m])

        :param predicate: A function that returns a boolean-like result.
        :param seq: The iterable to search through.
        :param only_first: Retuens only fisrt element.
        :type predicate: Callable
        :type seq: Iterable
        :type only_first: bool
    """
    elements = []

    for element in seq:
        if predicate(element):
            elements.append(element)
    
    if only_first and len(elements) > 0:
        return elements[0]
    
    if len(elements) == 1:
        return elements[0]
    elif len(elements) > 1:
        return elements
    return None


def get(iterable: t.Iterable[T], **attrs: t.Any) -> T | None:
    r"""
        A helper that returns the elements in the iterable that meets
        all the traits passed in ``attrs``. 

        When multiple attributes are specified, they are checked using
        logical AND, not logical OR. Meaning they have to meet every
        attribute passed in and not one of them.

        To have a nested attribute search (i.e. search by ``x.y``) then
        pass in ``x__y`` as the keyword argument.

        If nothing is found that matches the attributes passed, then
        ``None`` is returned.

        Examples
        ---------

        Basic usage:

        .. code-block:: python3

            member = modules.get(message.guild.members, name='Foo')

        Multiple attribute matching:

        .. code-block:: python3

            channel = modules.get(guild.voice_channels, name='Foo', bitrate=64000)

        Nested attribute matching:

        .. code-block:: python3

            channel = modules.get(client.get_all_channels(), guild__name='Cool', name='general')

        Parameters
        -----------
        iterable
            An iterable to search through.
        \*\*attrs
            Keyword arguments that denote attributes to search with.
    """

    _all = all
    attrget = attrgetter

    if len(attrs) == 1:
        k, v = attrs.popitem()
        pred = attrget(k.replace("__", "."))
        elems = []
        for elem in iterable:
            if pred(elem) == v:
                elems.append(elem)
        if len(elems) == 1:
            return elems[0]
        elif len(elems) > 1:
            return elems
        return None

    converted = [
        (attrget(attr.replace("__", ".")), value) for attr, value in attrs.items()
    ]
    
    elems = []
    print(pred(elem) == value for pred, value in converted)

    for elem in iterable:
        if _all(pred(elem) == value for pred, value in converted):
            elems.append(elem)
    
    if len(elems) == 1:
        return elems[0]
    elif len(elems) > 1:
        return elems
    return None


def create_embed(title: str, description: t.Optional[str], colour: int = constants.EMBED_COLOUR) -> modules.MyEmbed:
    """
        Create new embed.

        :param title: Embed title.
        :param description: Embed description.
        :param colour: Embed colour.
        :type title: str
        :type description: str
        :type colour: int
        :returns: New embed.
        :rtype: modules.MyEmbed
    """
    embed = modules.MyEmbed(title=title, description=description, colour=colour)
    embed.set_author(name=constants.EMBED_AUTHOR_NAME, url=constants.EMBED_AUTHOR_URL, icon_url=constants.EMBED_AUTHOR_ICON_URL)
    embed.set_footer(text=constants.EMBED_FOOTER, icon_url=constants.EMBED_AUTHOR_ICON_URL)
    embed.set_thumbnail(url=constants.EMBED_AUTHOR_ICON_URL)
    return embed


def has_ayn_role(member: discord.Member, roles: t.Union[list,str,int]) -> bool:
    """
        Check if member has any role.

        :param member: Member to check..
        :param roles: Roles to check.
        :type member: discord.Member
        :type roles: list, str, int
        :rtype: bool
    """
    if isinstance(roles, str) or isinstance(roles, int):
        roles = [roles]
        

    getter = functools.partial(discord.utils.get, member.roles)
    return any(getter(id=role) is not None if isinstance(role, int) else getter(name=role) is not None for role in roles)


def bot_count(guild: discord.Guild) -> int:
    """
        Returns the number of bots on the guild.

        :param guild: The guild whose number of bot will be returned.
        :type guild: discord.Guild
        :returns: Bot count.
        :rtype: int
    """
    bot_count = 0

    for member in guild.members:
        if member.bot:
            bot_count += 1

    return bot_count


def member_count(guild: discord.Guild) -> int:
    """
        Returns the number of members on the guild.

        :param guild: The guild whose number of member will be returned.
        :type guild: discord.Guild
        :returns: Member count.
        :rtype: int
    """
    member_count = 0

    for member in guild.members:
        if not member.bot:
            member_count += 1

    return member_count


def strftime_translate(txt: str) -> str:
    """
        Translate strftime output to Turkish.

        :param txt: strftime output.
        :type txt: str
        :rtype: str
    """
    b = {"Jan": "Ocak", "Feb": "Şubat", "Mar": "Mart", "Apr": "Nisa", "May": "Mayıs", "Jun": "Haziran", "Jul": "Temmuz", "Aug": "Ağustos", "Sep": "Eylül", "Oct": "Ekim", "Nov": "Kasım", "Dec": "Aralık"}

    for i in b:
        if i in txt:
            txt = txt.replace(i, b[i])

    return txt


def validate_university_email(email: str) -> bool:
    """
        Validates whether the email is a university email or not.

        :param email: Email address.
        :type email: str
        :rtype: bool
    """
    r1 = re.match("\\S+@\\S+\\.edu", email)
    r2 = re.match("\\S+@\\S+\\.edu\\S+", email)

    return (r1 is not None or r2 is not None)


def generate_random_code(length: int = constants.RANDOM_CODE_LEN, char_set: str = constants.RANDOM_CODE_CHAR_SET) -> str:
    """
        Generate random code.

        :param length: Length of code.
        :param char_set: Char set of code.
        :type length: int
        :type char_set: str
        :returns: Generated code.
        :rtype: str
    """
    return "".join(random.choices(char_set, k=length))


def get_circled_image(im: Image.Image, size=(215, 215)) -> Image.Image:
    """
        Rearranges the image in a circle.

        :param im: The image to be edited.
        :param size: New image size.
        :type im: Image.Image
        :type size: tuple
        :returns: New image.
        :rtype: Image.Image
    """
    im = im.resize(size, Image.ANTIALIAS)
    big_size = (im.size[0]*3, im.size[1]*3)
    mask = Image.new("L", big_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0)+big_size, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)
    return im


def split_arg_string(arg_s: str) -> list:
    """
        Splits string of arguments.

        :param arg_s: String of arguments.
        :type arg_s: str
        :returns: List of arguments.
        :rtype: list
    """
    rv = []
    for match in re.finditer(r"('([^'\\]*(?:\\.[^'\\]*)*)'"
                             r'|"([^"\\]*(?:\\.[^"\\]*)*)"'
                             r'|\S+)\s*', arg_s, re.S):
        arg = match.group().strip()
        if arg[:1] == arg[-1:] and arg[:1] in '"\'':
            arg = arg[1:-1].encode("ascii", "backslashreplace") \
                .decode("unicode-escape")
        try:
            arg = type(arg_s)(arg)
        except UnicodeError:
            pass
        rv.append(arg)
    return rv


def execute_shell_command(command: t.Union[str, list], decode: bool = True, decoding: str = "utf-8") -> t.Tuple[str, t.Union[str, None]]:
    """
        Execute shell command.

        :param command: Command.
        :param decode: Decode the output.
        :param decoding: Decoding format.
        :type command: t.Union[str, list]
        :type decode: bool
        :type decoding: str
        :returns: Output and error.
        :rtype: t.Tuple[str, t.Union[str, None]]
    """
    if isinstance(command, str):
        command_args = split_arg_string(command)
    else:
        command_args = command

    p = subprocess.Popen(command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    output = p[0]
    error = None

    if len(p[1]) > 0:
        error = p[1]

    if decode:
        output = output.decode(decoding)
        if error is not None:
            error = error.decode(decoding)

    return output, error


def html_formatter(html: str, **kwargs) -> str:
    """HTML formaatter

    :param html: HTML text.
    :type html: str
    :return: Formatted HTML text.
    :rtype: str
    """
    for k,v in kwargs.items():
        html = html.replace(f"{{{{{k}}}}}", v)
    
    return html


def send_email(receiver: str, subject: str, content: str):
    """
        Send email.

        :param receiver: Receiver.
        :param subject: E-mail subject.
        :param filePath: E-mail content.
        :type receiver: str
        :type subject: str
        :type content: str
    """
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = constants.SENDEMAIL_FROM
    msg["To"] = receiver

    part1 = MIMEText(content, "html", "utf-8")
    msg.attach(part1)
    text = msg.as_string().encode("ascii")

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(constants.SENDEMAIL_EMAIL_ADDRESS, constants.SENDEMAIL_EMAIL_PASSWORD)
        server.sendmail(constants.SENDEMAIL_FROM, receiver, text)
        server.close()
    except smtplib.SMTPAuthenticationError as e:
        print(e)
        raise modules.errors.SendEmailAuthError(str(e))


def send_verifaction_email(name: str, email: str, verifaction_code: str, channel_name: str):
    """
        Send verification email.

        :param name: Member name.
        :param email: Member e-mail.
        :param verifactionCode: Verifaction code.
        :type name: str
        :type email: str
        :type verifactionCode: str
    """
    content = modules.html_formatter(constants.SENDEMAIL_CONTENT, name=name, server_name=constants.SERVER_NAME, bot_name=constants.BOT_NAME, channel=channel_name, prefix=constants.COMMAND_PREFIX, verifaction_code=verifaction_code)

    send_email(email, f"{constants.SERVER_NAME} Discord | Üniversite Rolü Başvuru Onaylama", content)
