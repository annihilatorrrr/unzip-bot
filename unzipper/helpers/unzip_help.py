# Copyright (c) 2022 EDM115
import math
import time
from typing import List, Union


# Credits: SpEcHiDe's AnyDL-Bot for Progress bar + Time formatter
async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 10.00) == 0 or current == total:
        timenow = round(time.time() - start) * 1000
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion
        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        """
        if ((int(estimated_total_time) > int(elapsed_time)) and (int(timenow) > int(elapsed_time))) or ((int(estimated_total_time) > int(elapsed_time)) and (int(percentage) > 50)):
            estimated_total_time -= elapsed_time / 10
        """
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)
        progress = "[{0}{1}] \n**Processing…** : `{2}%`\n".format(
            "".join(["⬢" for _ in range(math.floor(percentage / 5))]),
            "".join(["⬡" for _ in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2),
        )

        tmp = progress + "`{0} of {1}`\n**Speed :** `{2}/s`\n**ETA :** `{3}`\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time
            if estimated_total_time != "" or percentage != "100" else "0 s",
        )
        try:
            await message.edit(text=f"{ud_type}\n {tmp} \n\n**Powered by @EDM115bots**")
        except:
            pass


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        n += 1
    return f"{str(round(size, 2))} {Dic_powerN[n]}B"


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        (f"{str(days)}d, " if days else "")
        + (f"{str(hours)}h, " if hours else "")
        + (f"{str(minutes)}m, " if minutes else "")
        + (f"{str(seconds)}s, " if seconds else "")
        + (f"{str(milliseconds)}ms, " if milliseconds else "")
    )
    return tmp[:-2]


def timeformat_sec(seconds: int) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        (f"{str(days)}d, " if days else "")
        + (f"{str(hours)}h, " if hours else "")
        + (f"{str(minutes)}m, " if minutes else "")
        + (f"{str(seconds)}s, " if seconds else "")
    )
    return tmp[:-2]


# List of common extentions
extentions_list = {
    "archive": [
        "7z",
        "apk",
        "apkm",
        "apks",
        "appx",
        "arc",
        "bcm",
        "bin",
        "br",
        "bz2",
        "dmg",
        "exe",
        "gz",
        "img",
        "ipsw",
        "iso",
        "jar",
        "lz4",
        "msi",
        "paf",
        "pak",
        "pea",
        "rar",
        "tar",
        "wim",
        "xapk",
        "xz",
        "z",
        "zip",
        "zpaq",
        "zstd",
    ],
    "audio": ["aif", "aiff", "aac", "flac", "mp3", "ogg", "wav", "wma"],
    "photo": ["gif", "ico", "jpg", "jpeg", "png", "tiff", "webp"],
    "split": ["0*", "001", "002", "003", "004", "005"],
    "video": ["3gp", "avi", "flv", "mp4", "mkv", "mov", "mpeg", "mpg", "webm"],
}
