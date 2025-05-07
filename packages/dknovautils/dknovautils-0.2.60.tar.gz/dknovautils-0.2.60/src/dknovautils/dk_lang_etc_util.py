from __future__ import annotations

# 导入module避免某些循环import的问题
from dknovautils import commons, iprint_debug, iprint_warn, iprint, AT
from dknovautils.commons import *


class DkLangEtcUtils(object):
    _debug = True

    @classmethod
    def f_remove_comments_v1(
        cls,
        py: str,
        *,
        _removeAstSentence: bool = False,
        _removeATVast: bool = False,
        _removeSingleQuoteMuilti: bool = False,
    ) -> str:
        """
        行尾的注释需要保留

        缺省情况下 单引号多行文本会被删除

        _removeSingleQuoteMuilti 参数 可以切换是单引号还是双引号


        """

        # 可以在py文件中添加如下字符串阻止移除多行注释 分开写是让此文件本身不会被错误识别
        KEEP = "__keep_" + "quotes__"

        assert py is not None, "err5242"

        # 注意ln已经有末尾的回车符 最好替换成\n方便后续处理 rstrip 将去掉末尾的回车符

        lns = "\n".join(ln.rstrip() for ln in py.splitlines())

        keep_quotes = KEEP in lns

        if cls._debug:
            print(lns)
            print("=====")

        # 去掉单行注释
        re_single_a = r"\n\s*#.*"
        pattern = re.compile(re_single_a)
        lns = re.sub(pattern, "", lns)  # 查找匹配 然后替换

        """
        是匹配单引号还是匹配双引号？
        
        写注释习惯用得最多的是双引号。所以还是缺省删除双引号。


        """

        # 首行开始的文本不会被替换掉，因为前方没有回车符
        if _removeSingleQuoteMuilti:
            fr_multi = r"(?s)'''.*?'''"
        else:
            fr_multi = r'(?s)""".*?"""'
        pattern = re.compile(fr_multi)
        if not keep_quotes:
            lns = re.sub(pattern, "pass", lns)  # 查找匹配 然后替换

        # 暂时关闭
        # _removeAstSentence = False
        if _removeAstSentence:
            re_single_a = r"\n\s*assert\s.+"
            pattern = re.compile(re_single_a)
            lns = re.sub(pattern, "", lns)

        # 暂时关闭的

        if _removeATVast:
            re_single_a = r"\n\s*AT.vassert_\(.+"
            pattern = re.compile(re_single_a)
            lns = re.sub(pattern, "", lns)

        if cls._debug:
            print(lns)

        return lns

    langWordSet = r"[a-zA-Z0-9\_\u4e00-\u9fa5]"

    # langNotWordSet = r'[^a-zA-Z0-9_\u4e00-\u9fa5]'

    @classmethod
    def find_words(
        cls, texts: List[str], keyFun: Callable[[str], Any], *, minLen: int = 6
    ) -> Set[str]:
        assert keyFun is not None
        rs = set()
        langWord = f"{cls.langWordSet}+"
        pWord = re.compile(langWord)

        for text in texts:
            assert len(text) >= 0  # and len(keyStr) >= 1
            ws = pWord.findall(text)
            ws = [x for x in ws if len(x) >= minLen and keyFun(x)]
            rs.update(ws)

        iprint(f"rs:{rs}")

        return rs

    @classmethod
    def sub_word(cls, texts: List[str], *, fromWord: str, toWord: str) -> List[str]:
        langWord = f"{cls.langWordSet}+"
        pWord = re.compile(langWord)
        AT.assert_(re.fullmatch(pWord, fromWord) is not None)
        AT.assert_(re.fullmatch(pWord, toWord) is not None)

        iprint(f"fromw:{fromWord} tow:{toWord}")

        r33str = f"""
        (?<=[^a-zA-Z0-9\_\u4e00-\u9fa5])
        {fromWord}
        (?=[^a-zA-Z0-9\_\u4e00-\u9fa5])    
        
        """
        r33 = re.compile(r33str, re.X)

        def fa() -> Iterator[str]:
            for text in texts:
                assert isinstance(text, str)
                yield re.sub(r33, toWord, text)

        rs = list(fa())

        return rs

    @classmethod
    def f_replace_text_simplea(cls, filepath: str, fcb: Callable[[str], str]) -> None:
        # 最简单的方式 直接将文件内容读出文本 utf8编码的文本
        # assert filepath and fcb

        # 如果不设置编码 缺省为系统缺省编码gbk
        text = Path(filepath).read_text(encoding="utf8")
        # print(text)
        text = fcb(text)
        AT.assert_(text is not None)
        Path(filepath).write_text(text, encoding="utf8")

    @classmethod
    def handle_files_100(cls, fs: List[Path], keyFun: Callable[[str], Any]) -> None:
        """
        即使在字符串常量中 也会替换的
        """
        texts = [fp.read_text() for fp in fs]
        iprint(f"files: {len(fs)}")

        assert sorted(["ab", "ba", "caa"], key=lambda x: x[::-1]) == ["caa", "ba", "ab"]

        ws = list(DkLangEtcUtils.find_words(texts, keyFun))

        if len(ws) <= 1:
            iprint_warn(f"err9667")
            return

        ws = sorted(ws, key=lambda x: x[::-1])

        tmpf = f"K_STS_K_{AT.fepochMillis()}"

        texts = DkLangEtcUtils.sub_word(texts, fromWord=ws[0], toWord=tmpf)
        subs = list(zip(ws, [*ws[1:], ws[0]]))
        for i, w in enumerate(subs[:-1]):
            tow, fromw = w

            texts = DkLangEtcUtils.sub_word(texts, fromWord=fromw, toWord=tow)

        texts = DkLangEtcUtils.sub_word(texts, fromWord=tmpf, toWord=ws[-1])

        for i, file in enumerate(fs):
            file.write_text(texts[i])


def _f_main() -> None:
    rPyId = r"([a-zA-Z0-9_\u4e00-\u9fa5]+)"

    pattern = re.compile(rPyId)  # 查找数字
    ta = (
        "runoob 123 google 456  \n 大家比里好 和*比/来.(这+里)里}里{"
        """
    xyz
    def 里()
        里好=abc
        里2=ttt
        x.里=xyz

    
    """
    )
    print(ta.splitlines())
    result1 = pattern.findall(ta)
    result2 = pattern.findall("run88oob123google456")

    rs = DkLangEtcUtils.find_words([ta, ta], lambda x: 2, minLen=2)
    iprint(rs)

    print(result1)
    print(result2)

    r22 = r"[^a-zA-Z0-9_\u4e00-\u9fa5]+"

    r33str = """
    (?<=[^a-zA-Z0-9_\u4e00-\u9fa5])
    #(?:[^a-zA-Z0-9_\u4e00-\u9fa5]+)
    里
    (?=[^a-zA-Z0-9_\u4e00-\u9fa5])    
    #(?:[^a-zA-Z0-9_\u4e00-\u9fa5]+)
    
    """

    ra = f"{r22}abc{r22}"
    r33 = re.compile(r33str, re.X)
    ta2 = re.sub(r33, "东西", ta)
    # print(ta2)

    ta3 = DkLangEtcUtils.sub_word([ta], fromWord="里", toWord="东西2")
    print(*ta3)

    # replace

    pass


if __name__ == "__main__":
    _f_main()


"""
a-z0-9A-Z_

public static final String REGEX_CHINESE = "^[\u4e00-\u9fa5],{0,}$";




"""
