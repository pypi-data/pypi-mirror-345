from .file import *
from .info import *
import logging, requests, re, os, requests
from concurrent.futures import ThreadPoolExecutor, wait


def isUrl(url: str):
    """
    判断是否是网址
    @param url: 网址字符串
    @return: 布尔值
    """

    return bool(re.compile(r"(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]").match(url))


def joinUrl(*urls):
    """
    拼接网址
    @param urls: 网址
    @return: 拼接结果
    """
    from urllib.parse import urljoin
    data: str = ""
    for i in urls:
        data = urljoin(data, i)
    return data


def splitUrl(url: str):
    """
    分割网址
    @param url: 网址
    @return: urlparse对象，使用scheme、netloc、path、params、query、fragment获取片段
    """
    from urllib.parse import urlparse
    return urlparse(url)


def getUrl(url: str, header: dict = REQUEST_HEADER, timeout: int | tuple = (5, 10), times: int = 5):
    """
    可重试的get请求
    @param url: 链接
    @param header: 请求头
    @param timeout: 超时
    @param times: 重试次数
    @return:
    """
    logging.info(f"正在Get请求{url}的信息！")
    for i in range(times):
        try:
            response = requests.get(url, headers=header, stream=True, timeout=timeout, verify=False)
            logging.info(f"Get请求{url}成功！")
            return response
        except Exception as ex:
            logging.warning(f"第{i + 1}次Get请求{url}失败，错误信息为{ex}，正在重试中！")
            continue
    logging.error(f"Get请求{url}失败！")


def postUrl(url: str, data: dict = None, json: dict = None, header: dict = REQUEST_HEADER, timeout: int | tuple = (5, 10), times: int = 5):
    """
    可重试的post请求
    @param url: 链接
    @param data: 发送表单数据
    @param json：发送json数据
    @param header: 请求头
    @param timeout: 超时
    @param times: 重试次数
    @return:
    """
    logging.info(f"正在Post请求{url}的信息！")
    for i in range(times):
        try:
            if json:
                response = requests.post(url, headers=header, json=json, timeout=timeout, verify=False)
            elif data:
                response = requests.post(url, headers=header, data=data, timeout=timeout, verify=False)
            else:
                raise ValueError("data和json不能同时为空！")
            logging.info(f"Post请求{url}成功！")
            return response
        except Exception as ex:
            logging.warning(f"第{i + 1}次Post请求{url}失败，错误信息为{ex}，正在重试中！")
            continue
    logging.error(f"Post请求{url}失败！")


def getFileNameFromUrl(url: str):
    """
    从链接获取文件名
    @param url: 链接
    @return:
    """
    return os.path.basename(splitUrl(url).path)


def singleDownload(url: str, path: str, exist: bool = True, force: bool = False, header: dict = REQUEST_HEADER):
    """
    下载文件
    @param url: 下载链接
    @param path: 下载后完整目录/文件名
    @param exist: 是否在已有文件的情况下下载（False时force无效）
    @param force: 是否强制下载（替换已有文件）
    @param header: 请求头
    @return:
    """
    import requests
    if not existPath(path):
        createDir(splitPath(path, 3))
    try:
        if isDir(path):
            path = joinPath(path, getFileNameFromUrl(url))
        if isFile(path) and not exist:
            logging.warning(f"由于文件{path}已存在，自动跳过单线程下载！")
            return False
        if exist and not force:
            path = addRepeatSuffix(path)
        logging.info(f"正在单线程下载文件{url}到{path}！")
        response = requests.get(url, headers=header, stream=True)
        with open(path, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        logging.info(f"已将文件{url}单线程下载到{path}！")
        return path
    except Exception as ex:
        logging.error(f"单线程下载文件{url}到{path}失败，报错信息：{ex}！")
        return False


class DownloadManager:
    downloadThreadPool = ThreadPoolExecutor(max_workers=32)
    futures=[]
    def setMaxThread(self, num: int):
        if num <= 0:
            logging.error(f"设置多线程下载线程数{num}无效！")
            return False
        self.downloadThreadPool._max_workers = num
        return True

    def download(self, url: str, path: str, exist: bool = True, force: bool = False, header: dict = REQUEST_HEADER):
        """
        下载文件
        @param url: 下载链接
        @param path: 下载后完整目录/文件名
        @param exist: 是否在已有文件的情况下下载（False时force无效）
        @param force: 是否强制下载（替换已有文件）
        @param header: 请求头
        @return: 下载对象
        """
        d = DownloadSession()
        d.download(url, path, self, exist, force, header)
        self.futures.append(d.session)
        return d
    def wait(self):
        """
        等待所有下载完成
        :return:
        """
        wait(self.futures)

class DownloadSession:
    _cancel = False
    _progress = 0
    _result = None
    session = None

    def _download(self, url: str, path: str, exist: bool = True, force: bool = False, header: dict = REQUEST_HEADER):
        if not existPath(path):
            createDir(splitPath(path, 3))
        try:
            if isDir(path):
                path = joinPath(path, getFileNameFromUrl(url))
            if isFile(path) and not exist:
                logging.warning(f"由于文件{path}已存在，自动跳过单线程下载！")
                self._result = "skip"
                return "skip"
            if exist and not force:
                path = addRepeatSuffix(path)
            logging.info(f"正在多线程下载文件{url}到{path}！")
            response = requests.get(url, headers=header, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            progress = 0
            with open(path, "wb") as file:
                for chunk in response.iter_content(chunk_size=block_size):
                    if self._cancel:
                        logging.info(f"下载文件{url}到{path}被取消！")
                        self._result = "cancel"
                        file.close()
                        deleteFile(path)
                        return "cancel"
                    if chunk:
                        file.write(chunk)
                        progress += len(chunk)
                        self._progress = progress / total_size * 100
            logging.info(f"已将文件{url}多线程下载到{path}！")
            self._result = "success"
            return path
        except Exception as ex:
            logging.error(f"多线程下载文件{url}到{path}失败，报错信息：{ex}！")
            self._result = "fail"
            return "fail"

    def download(self, url: str, path: str, manager: DownloadManager = None, exist: bool = True, force: bool = False, header: dict = REQUEST_HEADER):
        self.session = manager.downloadThreadPool.submit(self._download, url, path, exist, force, header)

    def cancel(self):
        """
        取消下载
        """
        self._cancel = True

    def progress(self):
        """
        下载进度
        :return: 0-100之间的小数进度
        """
        return self._progress

    def isFinished(self):
        """
        任务完成状态
        :return: 是否完成
        """
        if self._result is not None:
            return True
        else:
            return False

    def result(self):
        """
        任务结果
        :return: skip,cancel,success,fail
        """
        return self._result

    def outputPath(self):
        try:
            if self._result == "success":
                return self.session.result(0.1)
        except TimeoutError:
            return None


downloadManager = DownloadManager()
