from __future__ import annotations

from dknovautils.commons import *

import pathlib


_debug = False


@dataclass
class DkPathInfo:
    ext: str
    extnd: str
    bn: str
    bnne: str
    fp: str
    fpp: str


"""

        dkf = DkFile(ln)



        namespace = {
            "ext": ext,
            "extnd": extnd,
            "bn": bn,
            "bnne": bnne,
            "fp": fp,
            "fpp": fpp,
        }


"""


class DkFile(object):

    def __init__(self, pathstr: str) -> None:
        """
        增加一个参数 将路径中的分隔符转化为 slash or back-slash or keep-original.

        """
        self.pathstr: str = str(pathstr)

        self.path: Path = Path(pathstr)

    def __key(self) -> Any:
        return self.path

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other: Any) -> Any:
        if isinstance(other, DkFile):
            return self.__key() == other.__key()
        return NotImplemented

    @property
    def basename(self) -> str:
        return os.path.basename(self.path)


    def basename_without_extension(self) -> str:
        bn: str = self.basename
        return bn[: (len(bn) - len(self.extension))]

    # @property
    # def name_meta(self) -> str:

    #     return os.path.basename(self.path)

    @property
    def path_info(self) -> DkPathInfo:
        dkf = self
        ln = self.pathstr

        ext = dkf.extension[0:]
        extnd = ext[1:]

        bn = dkf.basename
        bnne = bn[: len(bn) - len(ext)]

        fp = ln
        fpp = ln[: len(fp) - len(bn) - 1]

        return DkPathInfo(
            ext=ext,
            extnd=extnd,
            bn=bn,
            bnne=bnne,
            fp=fp,
            fpp=fpp,
        )

    @DeprecationWarning
    @property
    def filesize(self) -> int:
        return self.file_size()  # getsize(self.path)

    def file_size(self) -> int:
        return getsize(self.path)

    @property
    def dirname(self) -> str:
        return os.path.dirname(self.path)

    @property
    def extension(self) -> str:
        """包括点号 比如 .txt 如果没有扩展名 则返回空串"""
        # function to return the file extension
        file_extension = self.path.suffix
        return file_extension

    @property
    def extensionlower(self) -> str:
        """包括点号 比如 .txt 如果没有扩展名 则返回空串"""
        return self.extension.lower()

    def get_mtime_millis(self) -> int:
        r = int(self.get_mtime() * 1000)
        return r

    def get_mtime(self) -> float:
        """
        epoch seconds

        https://docs.python.org/3/library/os.path.html#os.path.getmtime

        Return the time of last modification of path. The return value is a floating-point number giving the number of seconds since the epoch (see the time module). Raise OSError if the file does not exist or is inaccessible.

        https://stackoverflow.com/questions/237079/how-do-i-get-file-creation-and-modification-date-times


        import os
        import datetime
        def modification_date(filename):
            t = os.path.getmtime(filename)
            return datetime.datetime.fromtimestamp(t)

        import os, time
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(file)
        print("last modified: %s" % time.ctime(mtime))


        """
        mt = os.path.getmtime(self.path)
        return mt

    def remove_curr_file(self):
        """
        Remove (delete) the file path. If path is a directory, an OSError is raised. Use rmdir() to remove directories. If the file does not exist, a FileNotFoundError is raised.

        """
        assert not self.is_dir()
        os.remove(self.path)

    def remove_curr_dir(self):
        assert self.is_dir()
        os.rmdir(self.path)

    def parent_dkfile(self) -> DkFile:
        r = DkFile(str(self.path.parent))
        return r

    @DeprecationWarning
    def exists(self) -> bool:
        return self.is_exists()

    def is_exists(self) -> bool:
        return self.path.exists()

    def is_file(self) -> bool:
        return self.path.is_file()

    def is_dir(self) -> bool:
        return self.path.is_dir()

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return str(self.path)

    @staticmethod
    def clear_dir(folder: str) -> None:
        """

        https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder

        """
        import os, shutil

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                iprint("Failed to delete %s. Reason: %s" % (file_path, e))

    @staticmethod
    def file_md5(
        f: str,
        *,
        md5Cache: Dict[str, str] | None = None,
        cb: Callable[[bytes], None] = None,
    ) -> str:
        """ """

        if md5Cache is None:
            md5Cache = {}

        if f in md5Cache:
            r = md5Cache[f]
            assert len(r) == 32
            return r
        else:
            dkf = DkFile(f)
            iprint_debug(f"gen md5 begin. size:{dkf.file_size():,} {f}")
            r = DkFile._fhash(dkf, hashlib.md5(), cb=cb)
            md5Cache[f] = r
            return r

    @staticmethod
    def _fhash(
        dkf: DkFile,
        _fsh,
        *,
        cb: Callable[[bytes], None] = None,
    ):
        size_1g = 1024 * 1024 * 1024
        size_8k = 8192
        LN = size_1g // size_8k
        readn = 1
        bs = 0
        allsize = dkf.file_size()
        """
        file_hash = _fsh  # hashlib.sha1()
            while chunk := f.read(size_8k):
                file_hash.update(chunk)
                r = file_hash.hexdigest().lower()
        
        """

        file_hash = _fsh  # hashlib.sha1()
        with open(dkf.path, "rb", buffering=1024 * 1024) as f:
            while chunk := f.read(size_8k):
                file_hash.update(chunk)
                if cb:
                    cb(chunk)
                readn += 1
                bs += len(chunk)
                if readn % LN == 0:
                    iprint_debug(f"gen hash. read:{bs:,} total:{allsize:,}")

        r = file_hash.hexdigest().lower()
        assert len(r) == 32
        return r

    @staticmethod
    def file_sha1(f: str) -> str:
        import hashlib

        dkf = DkFile(f)
        iprint_debug(f"gen sha1 begin. size:{dkf.file_size():,} {f}")
        r = DkFile._fhash(dkf, hashlib.sha1())
        return r

    @classmethod
    def list_dir(cls, d: str) -> List[DkFile]:
        """仅仅列举目录d的下一级子元素（不包括更深的子元素）"""
        fs = [DkFile(join(d, f)) for f in os.listdir(d)]
        # fs=[DkFile(f) for f in fs]
        return fs

    @staticmethod
    def fill_disk_simple(
        *,
        dir: str = ".",
        verify: bool = True,
        size: int = 1024 * 1024 * 100,
        pre: str = "tmp",
        verbose: bool = False,
    ) -> None:
        import numpy as np

        """
        在目录下创建文件. 文件大小约为10M. 创建之后马上读出检查内容是否正确. 用来对硬盘进行简单的检查.
        直到写满磁盘为止, [Errno 28] No space left on device 最后退出.
        
        mkdir tmp
        python3.10 -c "from dknovautils import *; DkFile.fill_disk_simple(dir='./tmp',verify=True,verbose=True)" |& tee -a ~/fill.log

        """
        bse = b"a"
        bs = np.frombuffer(bse * (1024 * 1024), dtype=np.uint8)

        if isinstance(size, int):
            assert size >= 1024 * 1024
            N = size // len(bs)
        else:
            raise Exception("unimplemented")

        def fpath(fid: int) -> Path:
            return Path(f"{dir}/{pre}{fid:08d}")

        iprint("begin write file")
        fid = 1
        while True:
            file = fpath(fid)
            if verbose:
                iprint(f"write file {file}")
            try:
                with file.open(mode="wb") as f:
                    for i in range(N):
                        f.write(bs)
                    f.flush()
                fid += 1
            except Exception as e:
                iprint(f"error {file} {e}")
                break

        iprint("fill disk end")

        if verify:
            DkFile.verify_disk_simple(dir=dir, pre=pre, verbose=verbose)

    @staticmethod
    def verify_disk_simple(
        *,
        dir: str = ".",
        pre: str = "tmp",
        verbose: bool = False,
    ) -> None:
        import numpy as np

        """
        在目录下创建文件. 文件大小约为10M. 
        直到写满磁盘为止, [Errno 28] No space left on device 最后退出.
        
        注意,下面命令的日志文件不要记录在当前磁盘中.因为当前磁盘会充满,会无法写入日志.
        mkdir tmp
        python3.10 -c "from dknovautils import *; DkFile.verify_disk_simple(dir='./tmp',verbose=True)" |& tee -a ~/verify.log

        """
        bse = b"a"
        bs = np.frombuffer(bse * (1024 * 1024), dtype=np.uint8)

        iprint("begin verify")

        files = (f for f in DkFile.listdir(dir) if f.basename.startswith(pre))
        for idx, file in enumerate(files):
            file = file.path
            if verbose:
                iprint(f"verify file {idx} {file}")
            try:
                with file.open(mode="rb") as f:
                    r = f.read(len(bs))
                    bs2 = np.frombuffer(r, dtype=np.uint8)
                    if len(bs2) == len(bs):
                        assert np.all(bs2 == bs), f"err56373 verify error {file}"
                    else:
                        condition = bs2 == bs[0]
                        assert np.all(condition), f"err56374 verify error {file}"
                # fid += 1
            except Exception as e:
                iprint(f"error idx{idx} {file} {e}")
                break

        iprint("verify disk end")


"""




"""


class DkPyFiles(object):
    pass


if __name__ == "__main__":
    print("OK")
