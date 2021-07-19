# pylint: disable=missing-module-docstring
import json
import re
import requests

def getDirCode(retFile):
    """
    dirCode 读取
    Usage: getDirCode(<file>)
    """
    try:
        regex = r'(?<=<a href="javascript: void\(0\)" onclick="load_subdir\().*(?=">\))'
        dirCode = re.search(regex, retFile[1]).group()
        return dirCode
    except AttributeError:
        return None
def getFileCode(retFile):
    """
    fileCode 读取
    Usage: getFileCode(<file>)
    """
    try:
        # 在城通文件夹分享中, 每一个子文件页面的URL中最后的一项即为fileCode. 此处调用了城通API，
        # 直接从返回值中提取fileCode. fileCode会过期
        fileCode = re.search(r'(?<=<a target="_blank" href=").*(?=">)',retFile[1]).group()
        return fileCode.split('/')[-1]
    except AttributeError:
        return None
class CTFileShare:
    """
    城通网盘分享类，用于读取城通分享和直链获取.
    Usage: CTFileShare(<分享链接>, <分享密码>, [userAgent])
    """
    def __init__(self,ctFileShareLink,ctSharePasswd=None,userAgent='Mozilla/5.0'):
        self.ctShareLink = ctFileShareLink
        # 获得城通网盘马甲链接，在获取直链时需要作为首部 Origin 字段发送
        self.ctServer = f"https://{ctFileShareLink.split('/')[2]}"
        self.shareType = ctFileShareLink.split('/')[3] # 城通下载链接中, "/d/" 为文件夹, "/f/"为单文件
        self.shareCode = ctFileShareLink.split('/')[4] # 分享URL中最后一项为shareCode
        self.sharePasswd = ctSharePasswd
        self.ctFileList = [] # 文件信息存储
        if ctSharePasswd is None:
            self.httpHeaders = {"user-agent": userAgent,"Origin": self.ctServer}
        else:
            shareId = self.shareCode.split('-')[1]
            self.httpHeaders = {"user-agent": userAgent,
                "Origin": self.ctServer,
                'cookie':f"pass_{self.shareType}{shareId}={str(ctSharePasswd)}"}
    def getDirectoryShare(self):
        """
        文件夹分享读取主函数
        """
        self.ctFileList = self.getDirectoryInfo(self.shareCode)
        return self.ctFileList
    def getDirectoryInfo(self,dirCode,path="d"):
        """
        文件夹信息读取
        Usage: getDirectoryInfo(<文件夹id>,[上级文件夹])
        """
        fileList = []
        # 调用文件夹详情API
        getDirReq = requests.get(f'https://webapi.ctfile.com/getdir.php?path={path}&d={dirCode}',\
                                    headers=self.httpHeaders)
        getDirJson = json.loads(getDirReq.text)
        apiUrl = f"https://webapi.ctfile.com{getDirJson['url']}" # 获取文件夹内容 API 接口 URL
        apiRequest = requests.get(apiUrl,headers=self.httpHeaders)
        apiJson = json.loads(apiRequest.text)
        for file in apiJson['aaData']:
            fileCode = getFileCode(file) # fileCode 读取挪至 getFileCode 函数
            if fileCode is None:
                nextDirCode = getDirCode(file)
                if dirCode is None:
                    raise TypeError("Unknown File Type")
                if dirCode == self.shareCode:
                    fileList.append({
                        "type": "Dir",
                        "name": getDirJson['folder_name'],
                        "files": self.getDirectoryInfo(nextDirCode),
                    })
                else:
                    fileList.append({
                        "type": "Dir",
                        "files": self.getDirectoryInfo(nextDirCode,path=dirCode),
                    })
            else:
                fileList.append(self.getFileInfo(fileCode)) # 文件详情读取挪至 getFileInfo
        return fileList
    def getFileInfo(self,fileCode):
        """
        文件信息获取
        Usage: geFileInfo(<fileCode>)
        """
        getFileRequest = requests.get(f'https://webapi.ctfile.com/getfile.php?f={fileCode}',\
                                        headers=self.httpHeaders)
        getFileJson = json.loads(getFileRequest.text)
        uid = getFileJson['userid']
        fid = getFileJson['file_id']
        fname = getFileJson['file_name']
        fchk = getFileJson["file_chk"]
        downloadApi = (f'https://webapi.ctfile.com/get_file_url.php?uid={uid}&fid={fid}',\
            f'&file_chk={fchk}')
        self.ctFileList.append({
            "type": "File",
            "name": fname,
            "userId": uid,
            "fileId": fid,
            "fileChk": fchk,
            "downloadAPI": downloadApi,
        })
    def getFileShare(self):
        """
        文件夹信息读取
        """
        fileCode = self.shareCode # 在单文件分享中, fileCode 和 shareCode 相同
        self.ctFileList.append(self.getFileInfo(fileCode))
    def getShare(self):
        """
        分享读取主函数
        """
        if self.shareType == 'd':
            self.getDirectoryShare()
        elif self.shareType == 'f':
            self.getFileShare()
    def genDownloadLink(self,verifyCodeAutoRetry=True):
        """
        下载链接生成
        """
        downloadLinkList = []
        for ctFile in self.ctFileList:
            downApiRequest = requests.get(('https://webapi.ctfile.com/get_file_url.php?',\
                f'uid={ctFile[1]}&fid={ctFile[2]}&file_chk={ctFile[3]}'))
            downApiJson = json.loads(downApiRequest.text)
            if downApiJson['code'] == 503: # 若需要验证码, 则重新调用 API
                if downApiJson['message'] == 'require for verifycode':
                    if verifyCodeAutoRetry:
                        return self.genDownloadLink()
                    raise KeyError("CTFile Need A Verify Code And Auto Retry Is Desabled")
            # downloadLinkList 的每一个项目都是一个列表, 格式为 [fileName, downloadLink]
            downloadLinkList.append([ctFile[0],downApiJson['downurl']])
        return downloadLinkList


if __name__ == '__main__':
    import getpass
    link = input("CTFile Share Link: ")
    passwd = getpass.getpass("Password: ")
    print("\b\b\b\b\b\b\b\b\b\bIniting...",end='')
    ct = CTFileShare(link,passwd)
    print("\b\b\b\b\b\b\b\b\b\b读取分享...",end='')
    ct.getShare()
    downloadLinks = ct.genDownloadLink()
    print("\b\b\b\b\b\b\b\b\b\b生成链接...")
    print("\nWarning: 城通网盘在下载直链层进行了多文件下载限制而不是在web界面限制, 无法从浏览器直接全部下载\n\n")
    for downloadLink in downloadLinks:
        print(f"{downloadLink[0]}\t{downloadLink[1]}\n")
