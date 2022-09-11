# pylint: disable=missing-module-docstring
import json
import re
import requests


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
        fileCode = re.search(r'(?<=href=").*(?=">)', retFile[1]).group()
        if "load_subdir" in fileCode:    # 对于文件夹的错误解析, 不应返回值
            return None
        return fileCode.split('/')[-1]
    except AttributeError:
        return None


class CTFileShare:
    """
    城通网盘分享类，用于读取城通分享和直链获取.
    Usage: CTFileShare(<分享链接>, <分享密码>, [API调用延迟], [userAgent])
    """

    def __init__(self, ctFileShareLink, ctSharePasswd=None, apiRequestDelay=0, userAgent='Mozilla/5.0'):
        self.ctShareLink = ctFileShareLink
        # 获得城通网盘马甲链接，在获取直链时需要作为首部 Origin 字段发送
        self.ctServer = f"https://{ctFileShareLink.split('/')[2]}"
        self.shareType = ctFileShareLink.split('/')[3]  # 城通下载链接中, "/d/" 为文件夹, "/f/"为单文件
        self.shareCode = ctFileShareLink.split('/')[4]  # 分享URL中最后一项为shareCode
        self.sharePasswd = ctSharePasswd
        self.apiRequestDelay = apiRequestDelay
        self.file = []  # 文件信息存储
        if ctSharePasswd is None:
            self.httpHeaders = {"user-agent": userAgent, "Origin": self.ctServer}
        else:
            shareId = self.shareCode.split('-')[1]
            self.httpHeaders = {"user-agent": userAgent,
                                "Origin": self.ctServer,
                                'cookie': (f"pass_{self.shareType}{shareId}="
                                           f"{str(ctSharePasswd)}")}  # 事先在Cookie中写入"解密文件页"写入的Cookie

    def getFolderShare(self):
        """
        文件夹分享读取主函数
        """
        self.file = self.getFolderInfo()
        return self.file

    def getFolderInfo(self, folderId=""):
        """
        文件夹信息读取
        Usage: getFolderInfo([上级文件夹])
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
        文件信息获取
        Usage: geFileInfo(<fileId>)
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

class CTFile:
    """
    城通文件
    """
    def __init__(self, name: str, userId: int, fileId: int, fileChk: str):
        self.name = name        # Filename
        self.userId = userId    # UID
        self.fileId = fileId    # FID
        self.fileChk = fileChk  # File's Checksum (unknown type)

    def genDownloadApi(self):
        """
        获取城通网盘下载链接生成API的URL
        """
        return ("https://webapi.ctfile.com/get_file_url.php?"
                f"uid={self.userId}&"
                f"fid={self.fileId}&"
                f"file_chk={self.fileChk}"
                )

    def genDownloadLink(self, verifyCodeAutoRetry=False, httpHeaders=None):
        """
        对于当前文件的下载链接生成
        """
        if httpHeaders is None:
            httpHeaders = {'user-agent': "Mozilla/5.0"}
        downloadApiRequest = requests.get(self.genDownloadApi(), headers=httpHeaders)
        downloadApi = json.loads(downloadApiRequest.text)
        try:
            return CTFileDownloadLink(self, downloadApi['downurl'])
        except KeyError:
            if verifyCodeAutoRetry is True:
                return self.genDownloadLink(verifyCodeAutoRetry=verifyCodeAutoRetry)
        return None

    def __getitem__(self, item):
        retItem = None
        if item == 'name':
            retItem = self.name
        elif item == 'userId':
            retItem = self.userId
        elif item == "fileId":
            retItem = self.fileId
        elif item == 'fileChk':
            retItem = self.fileChk
        elif item == 'downloadAPI':
            retItem = self.genDownloadApi()
        elif item == 'downloadLink':
            retItem = self.genDownloadLink()
        return retItem

    def __str__(self):
        return "CTFile Object: name: " + self.name


class CTFileDownloadLink:
    """
    城通网盘下载链接类
    """
    def __init__(self, ctFileObject: CTFile, fileDownloadLink: str):
        self.fileDownloadLink = fileDownloadLink
        self.ctFileObject = ctFileObject

    def getFileObject(self):
        return self.ctFileObject

    def getDownloadLink(self):
        """
        获取下载链接
        """
        return self.fileDownloadLink

    def renewDownloadLink(self):
        """
        刷新下载链接
        """
        newDownloadLink = self.ctFileObject.genDownloadLink()
        self.fileDownloadLink = newDownloadLink
        return newDownloadLink

    def __getitem__(self, item):
        returnItem = None
        if item == 'downloadLink':
            returnItem = self.getDownloadLink()
        elif item == 'renewDownloadLink':
            returnItem = self.renewDownloadLink()
        elif item == 'name':
            returnItem = self.ctFileObject['name']
        return returnItem

    def __str__(self):
        return self.getDownloadLink()


# --- Demo ---
def printFolder(fileDir, folderDepth, subDir=False):
    """
    文件夹信息显示
    """
    if subDir:
        print((f"{'|' if (folderDepth - 1) > 0 else ''}"
               f"{'  |' * (folderDepth - 2)}  Dir: {fileDir['name']}"))
    else:
        print((f"{'|' if (folderDepth - 1) > 0 else ''}"
               f"{'  ' * (folderDepth - 1)}Dir: {fileDir['name']}"))
    for fileDownloadLink in fileDir['files']:
        if isinstance(fileDownloadLink, dict):
            printFolder(fileDownloadLink, folderDepth + 1, subDir=True)
        elif isinstance(fileDownloadLink, CTFile):
            print((f"|{'  |' * (folderDepth - 1)} {fileDownloadLink['name']}"
                   f"\t{fileDownloadLink['downloadLink']['downloadLink']}"))


if __name__ == '__main__':
    link = input("CTFile Share Link: ")
    if "?" in link:
        passwd = link.split("?")[-1].split("=")[-1]
    else:
        passwd = input("Password: ")
    ct = CTFileShare(link, passwd)
    getShare = ct.getShare()
    print("-- getShare() Raw Return --")
    print(getShare)
    print("-- getShare() Raw Return --\n")

    print("--Download Link--")
    if isinstance(getShare, dict):
        printFolder(getShare, 1)
    else:
        print("File Name\tDownload Link")
        print(f"{getShare['name']}\t{getShare['downloadLink']}")
    print("--Download Link--")
