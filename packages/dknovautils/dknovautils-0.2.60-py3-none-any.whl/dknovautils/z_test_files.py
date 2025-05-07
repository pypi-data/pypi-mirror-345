from dk_imports import *
from dknovautils import *
from dkfiles import *


def oper_():
    pass


def path_eval_1238(
    si: Iterator[str],
    exp: str = None,
    verbose: bool = True,
) -> Iterator[str]:
    """

    abc='mv "{a}" to "{x}"'

    ext = extension (including the dot)
    extnd = extension without the dot

    bn = basename
    bnne = basename without extension

    fp = fullpath
    fpp = fullpath of parent




    """

    def fstr(exp: str):
        assert "'" not in exp, f"err56715 bad quote {exp}"
        return f""" f'{exp}' """.strip()

    for ln in si:
        lnstrip = ln.strip()
        assert lnstrip == ln, f"err72687 {ln}"
        bad1 = ln.endswith("/") or ln.endswith("\\")
        assert not bad1, f"err85854 {ln}"

        dkf = DkFile(ln)

        pif = dkf.path_info

        res = eval(fstr(exp), dataclasses.asdict(pif))

        if verbose:
            iprint(f"yield {res}")
        yield res

    pass


def path_1234(si: Iterator[str], SEP=" && ") -> Iterator[str]:
    """
    假定：
        输入都是普通文件
        全部路径中不包含&&字符

    stdin 输入是每行一个全路径（例如用find生成的）
    stdout 输出是 SEP分割的内容 分隔符两端无空格
    分别是 100&&ext&&filename&&fullpath
    d 取值为d or f 表示是目录或者普通文件
    ext是原始扩展名 包括点符号 比如 .jpg .txt 如果是d 或者 无扩展名 那么是空字符串
    filename是文件名称
    fullpath就是输入的内容

    """
    N = 1234
    S2 = SEP.strip()
    printi = partial(print, flush=True)

    for ln in si:
        assert SEP not in ln, f"err77509 {ln}"
        dkf = DkFile(ln)
        bn = dkf.basename
        ext = dkf.extension[0:]

        out = SEP.join([str(N), ext, bn, ln])
        yield out
        # printi(out)


_demo100 = """


./tb/ta
./Calibre Library
./Calibre Library/(Mei )Bu Lu Si _Bu Lu Nuo _De _Mei Si Kui Ta  (Mei )A La Si Tai Er _Shi Mi Si
./Calibre Library/(Mei )Bu Lu Si _Bu Lu Nuo _De _Mei Si Kui Ta  (Mei )A La Si Tai Er _Shi Mi Si/Du Cai Zhe Shou Ce 1 (2)
./Calibre Library/(Mei )Bu Lu Si _Bu Lu Nuo _De _Mei Si Kui Ta  (Mei )A La Si Tai Er _Shi Mi Si/Du Cai Zhe Shou Ce 1 (2)/Du Cai Zhe Shou Ce 1 - (Mei )Bu Lu Si _Bu Lu Nuo _De _Mei Si Kui .pdf
./Calibre Library/(Mei )Bu Lu Si _Bu Lu Nuo _De _Mei Si Kui Ta  (Mei )A La Si Tai Er _Shi Mi Si/Du Cai Zhe Shou Ce 1 (2)/cover.jpg
./Calibre Library/(Mei )Bu Lu Si _Bu Lu Nuo _De _Mei Si Kui Ta  (Mei )A La Si Tai Er _Shi Mi Si/Du Cai Zhe Shou Ce 1 (2)/Du Cai Zhe Shou Ce 1 - (Mei )Bu Lu Si _Bu Lu Nuo _De _Mei Si Kui .epub
./Calibre Library/(Mei )Bu Lu Si _Bu Lu Nuo _De _Mei Si Kui Ta  (Mei )A La Si Tai Er _Shi Mi Si/Du Cai Zhe Shou Ce 1 (2)/metadata.opf
./Calibre Library/metadata.db
./Calibre Library/John Schember
./Calibre Library/John Schember/Quick Start Guide (1)
./Calibre Library/John Schember/Quick Start Guide (1)/cover.jpg
./Calibre Library/John Schember/Quick Start Guide (1)/Quick Start Guide - John Schember.epub
./Calibre Library/John Schember/Quick Start Guide (1)/metadata.opf
./Calibre Library/metadata_db_prefs_backup.json
./.android
./.android/debug.keystore.lock
./.android/analytics.settings
./.android/adbkey
./.android/modem-nv-ram-5554
./.android/avd
./.android/avd/Pixel_Fold_API_35.avd
./.android/avd/Pixel_Fold_API_35.avd/config.ini
./.android/avd/Pixel_Fold_API_35.avd/cache.img
./.android/avd/Pixel_Fold_API_35.avd/sdcard.img.qcow2
./.android/avd/Pixel_Fold_API_35.avd/read-snapshot.txt
./.android/avd/Pixel_Fold_API_35.avd/encryptionkey.img
./.android/avd/Pixel_Fold_API_35.avd/multiinstance.lock
./.android/avd/Pixel_Fold_API_35.avd/sdcard.img
./.android/avd/Pixel_Fold_API_35.avd/modem_simulator
./.android/avd/Pixel_Fold_API_35.avd/modem_simulator/iccprofile_for_sim0.xml
./.android/avd/Pixel_Fold_API_35.avd/modem_simulator/modem_nvram.json
./.android/avd/Pixel_Fold_API_35.avd/modem_simulator/iccprofile_for_carrierapitests.xml
./.android/avd/Pixel_Fold_API_35.avd/modem_simulator/etc
./.android/avd/Pixel_Fold_API_35.avd/modem_simulator/etc/modem_simulator
./.android/avd/Pixel_Fold_API_35.avd/modem_simulator/etc/modem_simulator/files
./.android/avd/Pixel_Fold_API_35.avd/modem_simulator/etc/modem_simulator/files/numeric_operator.xml
./.android/avd/Pixel_Fold_API_35.avd/hardware-qemu.ini
./.android/avd/Pixel_Fold_API_35.avd/version_num.cache



"""


demo_110 = """


./NCE.01.Parts.III.01.mp3
./NCE.02.Parts.III.02.mp3
./NCE.03.Parts.III.03.mp3
./NCE.04.Parts.III.04.mp3
./NCE.05.Parts.III.05.mp3
./NCE.06.Parts.III.06.mp3
./NCE.07.Parts.IV.01.mp3
./NCE.08.Parts.IV.02.mp3
./NCE.09.Parts.IV.03.mp3
./NCE.10.Parts.IV.04.mp3
./NCE.11.Parts.IV.05.mp3



"""


"""

cd /mnt/w_hot/_DISC_B_BAK/HomeShareEngllish/EnglishTextBooks
find ~+ -type f -name "*.mp3" | grep -i -v track > ~/files.txt


"""
exp_ffmpeg_mp3_to_mp4 = """ ffmpeg -i "{fpp}/{bn}" "{fpp}/{bn}.mp4" """


if __name__ == "__main__":

    # path_1234(_demo100.strip().splitlines())

    # exp = 'mv "{fpp}/{bn}" to "{fpp}/{bnne}.mp4"'

    input_str = pyperclip.paste()
    print("input:")
    print(input_str)

    input_str = input_str.strip().splitlines()
    exp = exp_ffmpeg_mp3_to_mp4.strip()
    rss = [ln for ln in path_eval_1238(input_str, exp)]

    rss = "\n".join(rss)
    print("output:")
    print(rss)
    
    

    pyperclip.copy(rss)

    pass
