# pylint: disable=missing-module-docstring

from utils.logging import logPrint
from utils.models import CTFile
import json
import re
import requests

# 下面的两个函数是为了在城通API返回的HTML片段中提取 folderId 和 fileCode, 为下面的读取作准备
# API 返回 HTML 片段, 直接动态加载到页面里, 让我们为城通的天才开发鼓掌!!!

def getFolderId(retFile):
    """
    folderId 读取
    Usage: getFolderId(<file>)
    """
    try:
        regex = r'(?<=load_subdir\().*(?=\))'
        folderId = re.search(regex, retFile[1]).group()
        return folderId
    except AttributeError:
        return None


def getFileCode(retFile):
    """
    fileCode 读取
    Usage: getFileCode(<file>)
    """
    try:
        # 在城通文件夹分享中, 每一个子文件页面的URL中最后的一项即为fileCode. 此处调用API，
        # 直接从返回值中提取fileId. fileId会过期
#        fileCode = re.search(r'(?<=<a target="_blank" href=").*(?=">)', retFile[1]).group()
        fileCode = re.search(r'(?<=href=").*(?=">)', retFile[1]).group()
        # 如果是文件夹的话会提取出这样的东西: 'javascript: void(0)" onclick="load_subdir(********)'， 如果是这样的话就返回 None, 作为文件夹处理
        try:
            re.search(r'javascript: ', retFile[1]).group() # 如果传入的是一个文件夹，这里就不会报错，从而继续执行下面的 return, 返回 None, 防止回传非 filecode数据
            return None
        except:  # 上面那句报错了就对了, 就是要报错的，报错证明传入的服务器返回值对应的是一个文件
            pass

        return fileCode.split('/')[-1]
    except AttributeError:
        return None


class CTFileShare:
    """
    城通网盘分享类，用于读取城通分享和直链获取.
    Usage: CTFileShare(<分享链接>, <分享密码>, [userAgent])
    """

    def __init__(self, ctFileShareLink, ctSharePasswd=None, userAgent='Mozilla/5.0'):
        self.ctShareLink = ctFileShareLink
        # 获得城通网盘马甲链接，在获取直链时需要作为首部 Origin 字段发送
        self.ctServer = f"https://{ctFileShareLink.split('/')[2]}"
        self.shareType = ctFileShareLink.split('/')[3]  # 城通下载链接中, "/d/" 为文件夹, "/f/"为单文件
        self.shareCode = ctFileShareLink.split('/')[4]  # 分享URL中最后一项为shareCode
        self.sharePasswd = ctSharePasswd
        logPrint('debug', f'城通马甲: {self.ctServer}')
        logPrint('debug', f'分享类型: {self.shareType}')
        logPrint('debug', f'调用时指定的密码: {ctSharePasswd}')
        self.file = []  # 文件信息存储
        if ctSharePasswd is None:
            logPrint('debug', '未指定密码， 视为无密码分享')
            logPrint('debug', '对于不使用自定义域名的城通网盘分享链接，这是不正常的，若报错有可能是缺少密码导致')
            self.httpHeaders = {"user-agent": userAgent, "Origin": self.ctServer}
        else:
            shareId = self.shareCode.split('-')[1]
            self.httpHeaders = {"user-agent": userAgent,
                                "Origin": self.ctServer,
                                'cookie': (f"pass_{self.shareType}{shareId}="
                                           f"{str(ctSharePasswd)}")}

    def getFolderShare(self):
        """
        文件夹分享读取主函数
        """
        self.file = self.getFolderInfo()
        return self.file

    def getFolderInfo(self, folderId=""):
        """
        文件夹信息读取
        Usage: getDirectoryInfo(<文件夹id>,[上级文件夹])
        """
        getFolderRequest = requests.get(('https://webapi.ctfile.com/getdir.php?path=d&'
                                         f'd={self.shareCode}&'
                                         f'folder_id={folderId}'),
                                        headers=self.httpHeaders)
        folderInfoJson = json.loads(getFolderRequest.text)
        folderInfo = {
            'type': 'Folder',
            'name': folderInfoJson['file']['folder_name'],
            'folderId': folderInfoJson['file']['folder_id'],
            'files': []
        }
        folderFileListRequest = requests.get(f"https://webapi.ctfile.com{folderInfoJson['file']['url']}",
                                             headers=self.httpHeaders)
        folderFileList = json.loads(folderFileListRequest.text)
        for file in folderFileList['aaData']:
            fileCode = getFileCode(file)
            if fileCode is None:
                nextFolderId = getFolderId(file)
                folderInfo['files'].append(self.getFolderInfo(nextFolderId))
            else:
                folderInfo['files'].append(self.getFileInfo(fileCode))
        return folderInfo

    def getFileInfo(self, fileCode):
        """
        请求 fileCode 对应的文件信息, 返回 CTFile 实例
        Usage: geFileInfo(fileCode)
        """
        getFileRequest = requests.get(f'https://webapi.ctfile.com/getfile.php?f={fileCode}',
                                      headers=self.httpHeaders)
        getFileJson = json.loads(getFileRequest.text)
        return CTFile(
            getFileJson['file']['file_name'],
            getFileJson['file']['userid'],
            getFileJson['file']['file_id'],
            getFileJson['file']["file_chk"],
        )

    def getFileShare(self):
        """
        文件夹信息读取
        """
        fileId = self.shareCode  # 在单文件分享中, fileId 和 shareCode 相同
        self.file.append(self.getFileInfo(fileId))

    def getShare(self):
        """
        分享读取主函数
        """
        if self.shareType == 'd':
            return self.getFolderShare()
        return self.getFileShare()

    def getFileList(self, verifyCodeAutoRetry=True):
        """
        下载链接生成主函数
        """
        return self.genFileList(self.file, verifyCodeAutoRetry=verifyCodeAutoRetry)

    def genFileList(self, file, verifyCodeAutoRetry=True):
        """
        下载链接生成
        """
        downloadLinkList = []
        if file['type'] == "Folder":
            folderDownloadLink = ["Folder", file['name'], []]
            for folderFiles in file['files']:
                downLink = self.genFileList(folderFiles, verifyCodeAutoRetry)
                folderDownloadLink[2].append(downLink)
            downloadLinkList.append(folderDownloadLink)
        elif isinstance(file, CTFile):
            downloadLinkList.append(file)
        if len(downloadLinkList) == 1:
            downloadLinkList = downloadLinkList[0]
        return downloadLinkList




