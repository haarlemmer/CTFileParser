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
        fileCode = re.search(r'(?<=<a target="_blank" href=").*(?=">)', retFile[1]).group()
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
        self.file = []  # 文件信息存储
        if ctSharePasswd is None:
            self.httpHeaders = {"user-agent": userAgent, "Origin": self.ctServer}
        else:
            shareId = self.shareCode.split('-')[1]
            self.httpHeaders = {"user-agent": userAgent,
                                "Origin": self.ctServer,
                                'cookie': f"pass_{self.shareType}{shareId}={str(ctSharePasswd)}"}

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
            'name': folderInfoJson['folder_name'],
            'folderId': folderInfoJson['folder_id'],
            'files': []
        }
        folderFileListRequest = requests.get(f"https://webapi.ctfile.com{folderInfoJson['url']}",
                                             headers=self.httpHeaders)
        folderFileList = json.loads(folderFileListRequest.text)
        for file in folderFileList['aaData']:
            fileCode = getFileCode(file)
            if fileCode is None:
                nexFolderId = getFolderId(file)
                folderInfo['files'].append(self.getFolderInfo(nexFolderId))
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
            getFileJson['file_name'],
            getFileJson['userid'],
            getFileJson['file_id'],
            getFileJson["file_chk"],
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


class CTFile:
    """
    城通文件
    """
    def __init__(self, name: str, userId: int, fileId: int, fileChk: str):
        self.name = name
        self.userId = userId
        self.fileId = fileId
        self.fileChk = fileChk

    def genDownloadApi(self):
        return ("https://webapi.ctfile.com/get_file_url.php"
                f"?uid={self.userId}"
                f"&fid={self.fileId}"
                f"&file_chk={self.fileChk}"
                )

    def genDownloadLink(self, verifyCodeAutoRetry=False, httpHeaders=None):
        downLink = None
        if httpHeaders is None:
            httpHeaders = {'user-agent': "Mozilla/5.0"}
        downloadApiRequest = requests.get(self.genDownloadApi(), headers=httpHeaders)
        downloadApi = json.loads(downloadApiRequest.text)
        try:
            downLink = CTFileDownloadLink(self, downloadApi['downurl'])
        except KeyError:
            if verifyCodeAutoRetry is True:
                downLink = self.genDownloadLink(verifyCodeAutoRetry=verifyCodeAutoRetry)
        return downLink

    def __getitem__(self, item):
        if item == 'name':
            return self.name
        elif item == 'userId':
            return self.userId
        elif item == "fileId":
            return self.fileId
        elif item == 'fileChk':
            return self.fileChk
        elif item == 'downloadAPI':
            return self.genDownloadApi()
        elif item == 'downloadLink':
            return self.genDownloadLink()

    def __str__(self):
        return "CTFile Object: name: " + self.name


class CTFileDownloadLink:
    def __init__(self, CTFileObject: CTFile, fileDownloadLink: str):
        self.link = fileDownloadLink
        self.CTFileObject = CTFileObject

    def getDownloadLink(self):
        return self.link

    def renewDownloadLink(self):
        newDownloadLink = self.CTFileObject.genDownloadLink()
        self.link = newDownloadLink
        return newDownloadLink

    def __getitem__(self, item):
        if item == 'downloadLink':
            return self.getDownloadLink()
        elif item == 'renewDownloadLink':
            return self.renewDownloadLink()
        elif item == 'name':
            return self.CTFileObject['name']

    def __str__(self):
        return self.getDownloadLink()


# --- Demo ---
def printFolder(fileDir, folderDepth, subDir=False):
    """
    文件夹信息显示
    """
    if subDir:
        print((f"{'|' if (folderDepth - 1) > 0 else ''}"
               f"{'  |' * (folderDepth - 2)}  Dir: {fileDir[1]}"))
    else:
        print((f"{'|' if (folderDepth - 1) > 0 else ''}"
               f"{'  ' * (folderDepth - 1)}Dir: {fileDir[1]}"))
    for fileDownloadLink in fileDir[2]:
        if isinstance(fileDownloadLink, list):
            printFolder(fileDownloadLink, folderDepth + 1, subDir=True)
        else:
            print(f"|{'  |' * folderDepth} {fileDownloadLink['name']}\t{fileDownloadLink['downloadLink']}")


if __name__ == '__main__':
    link = input("CTFile Share Link: ")
    passwd = input("Password: ")
    ct = CTFileShare(link, passwd)
    getShare = ct.getShare()
    downloadLink = ct.getFileList()
    print("---- Raw ----\n")
    print("-- getShare() Raw Return --")
    print(getShare)
    print("-- getShare() Raw Return --\n")
    print("-- genDownloadLink() Raw Return --")
    print(downloadLink)
    print("-- genDownloadLink() Raw Return --\n")
    print("---- Raw ----\n")

    print("--Download Link--")
    if isinstance(downloadLink, list):
        printFolder(downloadLink, 1)
    else:
        print("File Name\tDownload Link")
        print(f"{downloadLink[1]}\t{downloadLink[2]}")
    print("--Download Link--")
