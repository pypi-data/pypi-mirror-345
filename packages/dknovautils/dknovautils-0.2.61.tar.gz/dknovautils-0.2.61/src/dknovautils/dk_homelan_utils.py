import traceback
import paramiko
from getpass import getpass

import json
from typing import Protocol

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

from dknovautils import AT
from dknovautils import *

# pip install scp
from scp import SCPClient


def oswalk_simple_a(
    topdir: DkFile | str, topdown: bool = True
) -> Iterator[Tuple[DkFile, int]]:
    """
    遍历子目录树。

    # assert topdown
    """
    assert topdir, "bad topdir"
    if isinstance(topdir, str):
        topdir = DkFile(topdir)

    i = 0
    yield topdir, i
    i += 1
    for _i, (root, dirs, files) in enumerate(os.walk(topdir.path, topdown=topdown)):

        for d in dirs:
            dkf = DkFile(join(root, d))
            yield dkf, i
            i += 1

        for d in itertools.chain(files):
            dkf = DkFile(join(root, d))
            yield dkf, i
            i += 1


def oswalk_simple_b(topdir: DkFile | str, topdown: bool = True) -> Iterator[DkFile]:
    for dkf, _ in oswalk_simple_a(topdir=topdir, topdown=topdown):
        yield dkf


@dataclass_json
@dataclass(slots=True)
class SimpleFileItem:
    file: DkFile | None
    name: str
    length: int
    inode: int
    path: str

    # 此处一般不包括点号 eg: txt
    ext: str | None
    ext_lowercase: str | None

    isNormalFile: bool
    mtime: int
    isDir: bool
    permission: int
    userid: int

    file_ctt: bytes | None = None
    idev: int = -1  # file-system-id devid
    host: str | None = None
    idx: int = -1

    @property
    def fileN(self) -> DkFile:
        assert self.file
        return self.file

    @property
    def extN(self) -> str:
        assert self.ext
        return self.ext

    """
    
class SimpleFileItem(
    val file: File,
    val name: String,
    val idx: Int,
    val length: Long,
    val path: String,
    val ext: String? = null,
    val isNormalFile: Boolean,
    val mtime: Long,
    val isDir: Boolean,
) {

    val ext_lowercase: String? = ext?.lowercase()

    //    必要时 可以用来保存文件内容
    var file_ctt: ByteArray? = null
        
        
        
    """


def exec_ssh(
    ip: str,
    user: str,
    cmd: str,
    pwd: str,
    port: int = 22,
    sudopwd: str | None = None,
    verbose: bool = False,
) -> tuple[str, str]:

    cmd = cmd.strip()

    if verbose:
        iprint_debug(f"start cmd: {cmd}")

    startsudo = cmd.lower().startswith("sudo")

    if startsudo and not sudopwd:
        sudopwd = pwd

    sudocmd = startsudo

    get_pty = True if sudopwd else None

    # 建立连接
    trans = paramiko.Transport((ip, port))
    trans.connect(username=user, password=pwd)

    # 将sshclient的对象的transport指定为以上的trans
    ssh = paramiko.SSHClient()
    ssh._transport = trans

    # 剩下的就和上面一样了
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd, get_pty=get_pty)

    if sudocmd:

        if sudopwd:

            ssh_stdin.write(sudopwd + "\n")
            ssh_stdin.flush()
        else:

            AT.fail("err448")

    # if sudocmd and sudopwd:
    #     ssh_stdin.write(sudopwd + "\n")
    #     ssh_stdin.flush()

    # if sudopwd or cmd.startswith('sudo'):
    #     ssh_stdin.flush()

    outstr = str(ssh_stdout.read(), encoding="utf-8")
    errstr = str(ssh_stderr.read(), encoding="utf-8")

    # print(ssh_stdout.read())

    # 关闭连接
    trans.close()

    if verbose:
        iprint_debug(outstr)
        iprint_debug(f"end cmd: {cmd}")

    return outstr, errstr


@dataclass_json
@dataclass
class SSHConfig:
    ip: str
    user: str
    pwd: str
    port: int = 22

    def run_cmd(self, cmd: str, verbose: bool = False) -> tuple[str, str]:

        outstr, errstr = exec_ssh(
            ip=self.ip,
            user=self.user,
            cmd=cmd,
            pwd=self.pwd,
            port=self.port,
            sudopwd=self.pwd,
            verbose=verbose,
        )

        return outstr, errstr


class HomeLanUtils:

    @classmethod
    def parse_SimpleFileItem(cls, ln: str, idx: int = -1) -> SimpleFileItem:
        try:
            if False:
                # log.debug("parse line $ln")
                pass

            lnt = ln.strip()

            """
            

            y:d m:775 U:1000 T+:2024-10-20+13:12:57.8250581610 T@:1729401177.8250581610 
            secs s:4096 bytes i:2248960 path:./.android/cache

            
            """

            # H = len("-rwxr-xr-x 2023-12-31 22:37:08.0000000000")

            lnps = lnt.split(" ")

            isdir = lnps[0][2:] == "d"

            permission = int(lnps[1][2:])

            userid = int(lnps[2][2:])

            mtime = int(lnps[4][3:].split(".")[0]) * 1000

            _bytes = int(lnps[6][2:])  # s:xxx

            _inode = int(lnps[8][2:])  # i:xxxx

            bidx = lnt.find("path:")
            fpath = lnt[(bidx + len("path:")) :].strip()

            assert lnps[0][2:] in ["f", "d"], f"err93125 bad file type: {ln}"

            dkf = DkFile(fpath)
            name = dkf.basename
            length = _bytes
            isNormalFile = True if not isdir else False
            isDir = not isNormalFile
            ext = dkf.extension[1:]
            ext_lowercase = ext.lower()

            sfi = SimpleFileItem(
                file=dkf,
                name=name,
                length=length,
                inode=_inode,
                path=fpath,
                ext=ext,
                isNormalFile=isNormalFile,
                mtime=mtime,
                isDir=isDir,
                permission=permission,
                userid=userid,
                ext_lowercase=ext_lowercase,
            )

            return sfi
        except Exception as e:
            iprint_error(f"bad line: {ln}")
            traceback.print_exc()
            raise e

    BADSTR_kfnu = "Known file not used"

    @classmethod
    def ssh_traverse_dir2(
        cls,
        sshcfg: SSHConfig,
        dirpath: str | None = None,
        *,
        cmd_part: str | None = None,
        cmd_grep: str | None = None,
        follow: bool = True,
        verbose: bool = False,
    ) -> Iterator[SimpleFileItem]:  ##  #
        """

        -L     Follow symbolic links.

        val cmd4 =  find "$dir" -printf "%y %T+ %T@ secs %s bytes %p\n" | head -n $n  .trim()


        find . -printf "%y %T+ %T@ secs %s bytes %p\n"

        大概的结构是 后面的grep也可以是sort等等
        find . -printf "%y" | head -n 100 | grep xyz


        https://stackoverflow.com/questions/17478511/what-does-the-k-parameter-do-in-the-sort-function-linux-bash-scripting

        后面可以用 sort -k111 之类的方式进行排序。

        find -L . -printf "y:%y m:%m U:%U T+:%T+ T@:%T@ secs s:%s bytes path:%p\n" | head -n 100

        find -L . -printf "y:%y m:%m U:%U T+:%T+ T@:%T@ secs s:%s bytes i:%i path:%p\n" | head -n 100

        不定长的字段
            U userid
            i inode
            path


        """

        _N = 10**12
        cmd_printf = (
            r' -printf "y:%y m:%m U:%U T+:%T+ T@:%T@ secs s:%s bytes i:%i path:%p\n" | head -n '
            + str(_N)
        )
        follow = "-L " if follow else ""
        cmd_part = cmd_part if cmd_part else f'find {follow} "{dirpath}" '

        cmdall = cmd_part + cmd_printf + ("" if not cmd_grep else f" | {cmd_grep} ")
        outstr, errstr = sshcfg.run_cmd(cmd=cmdall, verbose=verbose)

        exp = (cls.parse_SimpleFileItem(ln) for ln in outstr.strip().splitlines())
        return exp

    @classmethod
    def is_hashdeep_file(cls, ctt: str) -> bool:
        return "HASHDEEP" in ctt.splitlines()[0]

    @classmethod
    def hashdeep_output_passed(cls, stdout: str) -> bool:
        """
                    hashdeep 返回

        hashdeep: Audit passed
           Input files examined: 0
          Known files expecting: 0
                  Files matched: 12
        Files partially matched: 0
                    Files moved: 0
                New files found: 0
          Known files not found: 0


        """
        kw = "Audit passed"
        r = kw in stdout.strip().splitlines()[0]

        return r

    @classmethod
    def md5sum_output_passed(cls, stdout: str) -> bool:
        """
        xxxx: OK

        """
        kw = "OK"
        r = [ln for ln in stdout.strip().splitlines() if not ln.endswith(kw)]
        return r == []

    @classmethod
    def net_check_shutdown(cls, url: str) -> None:
        """如果url不可正常访问 则马上向本机发出关机指令

        root crontab
            每1,2,3分钟执行一次

            python3.10 -c "from dknovautils import *; DkNetwork.net_check_shutdown('http://192.168.0.1')"

        不要指向外部网站,否则,公网断网则服务器关闭,另外,可能被外网屏蔽,从而无法正常工作.
        可以考虑指向路由器. 如果路由器重启 或者暂时维护,可能会造成服务器关闭. 当然,这个比指向外部网站会好一些.毕竟这个是可控的.

        20250404 这个功能基本上被 函数 hlan_checkurl_shutdown_bj 替代。




        """
        r = dknetwork.http_get_url_simple_str(url)
        if not r:
            iprint_warn("warn74542 shutdown the system")
            if AT.iswindows:
                os.system("shutdown /s /t 1")
            elif AT.islinux:
                os.system("shutdown -P now")
            else:
                iprint_warn("err65985 unsupported os")

        """

        https://geekdaxue.co/read/lwmacct@linux/shutdown
        https://www.geeksforgeeks.org/python-script-to-shutdown-computer/        

        windows 
        os.system("shutdown /s /t 1")

        linux
        os.system("shutdown -P now")

        """

    @classmethod
    def hlan_checkurl_shutdown_bj(
        cls,
        *,
        # xyc-mini-pc url
        cmd: str = "shutdown -P now",
        url: str = "http://192.168.0.60:8000/hello.txt",
        root_path: str | None = "/root",
        ST: float = 60 * (1.001 + 30 / 60),
        M: float = 10.0,
        dry_run: bool = False,
        verbose: bool = False,
    ):
        """
        如果2分钟都无法连接url 那么关闭当前系统

        20250404 已经验证是可用的。 在gtk-m6设备 pve中测试通过。

        安装软件依赖
            python3 -m pip install dknovautils


        在ubuntu root crontab中写入

            下面的任务是判断多个任务是否会相互干扰？不会干扰的。所以下面的echo命令其实不需要。当然记录启动日志是可以的。
            在调试功能稳定之后 将输入日志改变为写入到 /dev/null
            注意需要设置PATH 否则很多命令是无法找到的。缺省的cron运行的PATH环境是非常简化的。

            PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

        #某些pve中可能需要写 python3.10 -c xxx
            注意stdout输出到文件的日志 可能是有缓存的 并不一定会马上输出到文件中。
            调试的常用方法
                将 python3 -c xxx 这个指令直接在终端中运行 可以看到所有输出. 
                    这个命令文本在 _pve_stop_all.sh的脚本第一行也有的。
                将 _pve_stop_all.sh 直接运行 看是否能够关机

            @reboot python3 -c "from dknovautils import *; HomeLanUtils.hlan_checkurl_shutdown_bj(cmd='pve_stop_all',verbose=False,dry_run=False);" >>/root/pve_stop_all.log

            @reboot echo `date -Is` "after run checkurl-shutdown" >>/root/start.log

            @reboot echo `date -Is` `python3 --version` `shutdown --help` >>/root/test_cron.log

        现在系统都使用systemd 所有日志应该通过命令 journalctl 查看


        """
        debug_cmd = (
            "#"
            + r""" python3 -c "from dknovautils import *; HomeLanUtils.hlan_checkurl_shutdown_bj(cmd='pve_stop_all',verbose=True,dry_run=False);"  """.strip()
        )

        assert AT.isLinux
        KW_allok = "allok"
        import syslog

        def mypr(s: str) -> None:
            print(s)
            sname = "dknovautils"
            if AT.isLinux:
                # 现在系统都使用systemd 所有日志应该通过命令 journalctl 查看
                # LOG_KERN LOG_ERR LOG_INFO
                syslog.syslog(syslog.LOG_INFO, f"{sname} {s}")

        dtstr = AT.sdf_logger_format_datetime()
        mypr(f"{dtstr} hlan_checkurl_shutdown_bj start version:{AT.VERSION}")

        if cmd == "pve_stop_all":
            if True:
                """
                for vm in $(qm list | grep running | awk '{print $1}'); do qm shutdown $vm; done

                sort -r 让输入内容倒序排列。按照vmID降序排列。首先关闭id较大的vm。

                """

                CMD_pve_stop_all = """ for vm in $(qm list | grep running | awk '{print $1}' | sort -r ); do qm shutdown $vm; done; """

                CMD_pve_stop_all = """
                
                echo `date -Is` 'start qm shutdown all'; sleep 0s;
                
                # 关闭所有虚拟机
                for vm in $(qm list | grep running | awk '{print $1}' | sort -r ); do qm shutdown $vm; done;
                echo `date -Is` 'after qm shutdown all'; sleep 3s;

                # 关闭所有容器
                for ct in $(pct list | grep running | awk '{print $1}' | sort -r ); do pct shutdown $ct; done;          
                echo `date -Is`  'after pct shutdown all'; sleep 27s;
                
                #强制关机（如果没有响应）
                for vm in $(qm list | grep running | awk '{print $1}' | sort -r ); do qm stop $vm; done;
                echo `date -Is`  'after qm stop all'; sleep 10s;
                
                #关闭系统 此时vm和磁盘都已经停止 功耗应该已经很低了。
                echo 'run shutdown -P now'
                # 看命令是否可以执行
                shutdown --help;
                #shutdown -r now;
                shutdown -P now;
                
                """

            cmd = CMD_pve_stop_all
            # cmd += "shutdown -P now; "

            if root_path:
                # 运行这个文件会关闭所有vm然后关闭主机。如果有问题 可以直接运行这个文件进行调试。
                fname = f"{root_path}/_pve_stop_all.sh"
                Path(fname).write_text(f"{debug_cmd} \n{cmd}", encoding="utf-8")

        NL = int(ST / M)
        assert NL > 0

        def cb(rss: List[str | None]) -> bool:
            """ """
            ts = AT.sdf_logger_format_datetime()
            rss = rss[-NL:]
            rss = [(KW_allok if (rs and KW_allok in rs) else None) for rs in rss]
            shutdown = (len(rss) == NL) and all(rs is None for rs in rss)
            if shutdown:
                if True or verbose:
                    mypr(f"{ts} connect url:{url} shutdown cmd:{cmd}")

                # cmd = "shutdown -P now"
                if not dry_run:
                    run_simple_a(cmd, verbose=verbose)
                else:
                    # pass
                    mypr(f"dry_run is true. so not really shutdown.")

                if verbose:
                    mypr(f"shutdown end")

                return False
            else:
                if verbose:
                    mypr(f"{ts} connect url:{url} {rss[-1:]}")
                return True

        _f_check_hlan_url_wait_loop(url=url, M=M, cb=cb, NL=NL)


@dataclass_json
@dataclass
class CheckRes:

    res: List[tuple[DkFile, int, str, str]] = field(default_factory=list)
    has_known_file_not_used: bool = False
    pass


def f_md5_check(dhome: str, verbose: bool = True):
    """

    find . -type f -name "*.mp3" > hd_files.list

    hashdeep -rl -f hd_files.list > hd_files.md5

    hashdeep -rl -a -vv -k ./hd_files.md5 -f hd_files.list

    如果hash找不到文件 则会打印如下内容
    ./Media/StarterContent.png: Known file not used

    如果windows中使用TC创建md5文件 必须设置 unicode保存 和 使用unix分隔符。

    md5sum 返回


    """

    def is_doublecmd_file(ctt: str) -> bool:
        return True

    assert AT.is_linux

    filesmd5 = [
        dfk
        for dfk in oswalk_simple_a(topdir=DkFile(dhome))
        if dfk.basename == "hd_files.md5"
    ]

    cr = CheckRes()

    for md5file in filesmd5:
        iprint_debug(f"md5file: {md5file}")

        ctt = Path(md5file.path).read_text(encoding="utf-8")

        if HomeLanUtils.is_hashdeep_file(ctt):

            cmdhash = "hashdeep -rl -a -vv -k hd_files.md5 -f hd_files.list"

            cmd = f'cd "{md5file.path.parent}" && {cmdhash}  '

            rcode, stdout, stderr = run_simple_b(cmd=cmd, verbose=verbose)
            cr.res.append((md5file, rcode, stdout, stderr))

            if HomeLanUtils.BADSTR_kfnu in stdout:
                cr.has_known_file_not_used = True

        else:

            cmdhash = "md5sum --check hd_files.md5 "

            cmd = f'cd "{md5file.path.parent}" && {cmdhash}  '

            rcode, stdout, stderr = run_simple_b(cmd=cmd, verbose=verbose)
            cr.res.append((md5file, rcode, stdout, stderr))

            # if BADSTR in stdout:
            #     cr.has_known_file_not_used = True

    return cr


def _f_check_hlan_url_wait_loop(
    *,
    url: str,
    cb: Callable[[List[str | None]], bool],
    M: float = 20.0,
    NL: int = 100,
) -> None:
    """
    函数等待后台线程退出之后才会返回。

    每sleep M=30秒访问一次特定url（超时设置为3秒） 将最近NL=100次结果存储在L中
    每次访问url之后，马上调用一次回调函数cb，传入 L参数。
        该回调在后台线程中执行。
        如果cb返回False 则终止后台线程。

    """

    def fjob():
        rs_latest = []

        while True:
            time.sleep(M)
            r = dknetwork.http_get_url_simple_str(url=url, timeout=3.0)
            rs_latest.append(r)
            while True:
                if len(rs_latest) <= NL:
                    break
                else:
                    rs_latest.pop(0)

            r2 = cb(rs_latest)
            if r2 == False:
                break
            else:
                pass

    thread = threading.Thread(target=fjob, args=(), daemon=True)
    thread.start()
    thread.join()


"""




def faaa():
	assert is-linux
	参数	dhome为本地目录

	hd_files.md5

	遍历dhome目录，获取文件列表

	获取 hd_files.md5文件

		cd hddir
		md5hash ....
		
	class Res:
		...
		
		可以将运行结果打印输出到文件 方便持久化存储 作为数据日志来保存
			所以最好是pretty-json格式
			
	方便可以在sh中直接编写py脚本进行执行。
	初期用普通的文件遍历即可
	还要考虑与tc dc的结合问题
	后续会考虑支持hashdeep之类的工具等等
		
	返回 res



"""
