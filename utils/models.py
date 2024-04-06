import requests, json

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
