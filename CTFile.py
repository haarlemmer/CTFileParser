class CTFileShare:
    def __init__(self,ctFileShareLink,ctSharePasswd=None,userAgent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.59 Safari/537.36 Edg/92.0.902.22'):
        self.ctShareLink = ctFileShareLink
        self.ctServer = f"https://{ctFileShareLink.split('/')[2]}" # 获得城通网盘马甲链接，在获取直链时需要作为首部 Origin 字段发送。
        self.shareType = ctFileShareLink.split('/')[3] # 城通下载链接中, "/d/" 为文件夹, "/f/"为单文件
        self.shareCode = ctFileShareLink.split('/')[4] # 分享URL中最后一项为shareCode
        self.sharePasswd = ctSharePasswd
        self.ctFileList = [] # 文件信息存储
        self.downloadLinkList = []
        if ctSharePasswd == None:
            self.httpHeaders = {"user-agent": userAgent,"Origin": self.ctServer}
        else:
            shareId = self.shareCode.split('-')[1]
            self.httpHeaders = {"user-agent": userAgent,"Origin": self.ctServer,'cookie':f"pass_{self.shareType}{shareId}={str(ctSharePasswd)}"}
    def getDirectoryShare(self):
        self.ctFileList = self.getDirectoryInfo(self.shareCode)
        return self.ctFileList
    def getDirectoryInfo(self,dirCode,path="d"):
        import requests,json
        fileList = []
        getDirRequest = requests.get(f'https://webapi.ctfile.com/getdir.php?path={path}&d={dirCode}',headers=self.httpHeaders) # 调用文件夹详情API
        getDirJson = json.loads(getDirRequest.text)
        apiUrl = f"https://webapi.ctfile.com{getDirJson['url']}" # 获取文件夹内容 API 接口 URL
        apiRequest = requests.get(apiUrl,headers=self.httpHeaders)
        apiJson = json.loads(apiRequest.text)
        for f in apiJson['aaData']:
            fileCode = self.getFileCode(f) # fileCode 读取挪至 getFileCode 函数
            fileList.append(self.getFileInfo(fileCode)) # 文件详情读取挪至 getFileInfo
        return fileList
    def getFileInfo(self,fileCode):
        import json,requests
        getFileRequest = requests.get(f'https://webapi.ctfile.com/getfile.php?f={fileCode}',headers=self.httpHeaders)
        getFileJson = json.loads(getFileRequest.text)
        uid = getFileJson['userid']
        fid = getFileJson['file_id']
        fname = getFileJson['file_name']
        fchk = getFileJson["file_chk"]
        downloadApiLink = f'https://webapi.ctfile.com/get_file_url.php?uid={uid}&fid={fid}&file_chk={fchk}'
        fileList = [fname,uid,fid,fchk,downloadApiLink]
        self.ctFileList.append(fileList) # ctFileList 的每一个项目都是一个列表，格式为 [fileName, userId, file_id, file_chk, DownloadApi]
    def getFileCode(self,f):
        import re
        try:
            return re.search(r'(?<=<a target="_blank" href=").*(?=">)',f[1]).group().split('/')[-1] # 在城通文件夹分享中, 每一个子文件页面的URL中最后的一项即为fileCode. 此处调用了城通API，直接从返回值中提取fileCode. fileCode会过期
        except:
            return None
    def getFileShare(self):
        fileCode = self.shareCode # 在单文件分享中, fileCode 和 shareCode 相同
        self.ctFileList.append(self.getFileInfo(fileCode))
    def getShare(self):
        if self.shareType == 'd':
            self.getDirectoryShare()
        elif self.shareType == 'f':
            self.getFileShare()
    def genDownloadLink(self,verifyCodeAutoRetry=True):
        import requests,json 
        for ctFile in self.ctFileList:
            downApiRequest = requests.get(f'https://webapi.ctfile.com/get_file_url.php?uid={ctFile[1]}&fid={ctFile[2]}&file_chk={ctFile[3]}')
            downApiJson = json.loads(downApiRequest.text)
            if downApiJson['code'] == 503: # 若需要验证码, 则重新调用 API
                if downApiJson['message'] == 'require for verifycode':
                    if verifyCodeAutoRetry:
                        return self.genDownloadLink()
                    else:
                        raise KeyError("CTFile Need A Verify Code And Auto Retry Is Desabled")
            self.downloadLinkList.append([ctFile[0],downApiJson['downurl']]) # downloadLinkList 的每一个项目都是一个列表, 格式为 [fileName, downloadLink]
        return self.downloadLinkList


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
