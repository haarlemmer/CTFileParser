class CTFile:
    def __init__(self,ctFileShareLink,ctSharePasswd=None,userAgent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.59 Safari/537.36 Edg/92.0.902.22'):
        self.ctShareLink = ctFileShareLink
        self.ctServer = f"https://{ctFileShareLink.split('/')[2]}" # 获得城通网盘马甲链接，在获取直链时需要作为首部发送。
        self.shareType = ctFileShareLink.split('/')[3] # 城通下载链接中, "/d/" 为文件夹, "/f/"为单文件
        self.shareCode = ctFileShareLink.split('/')[4] # 分享URL中最后一项为shareCode
        self.sharePasswd = ctSharePasswd
        self.ctFileList = [] # 一个列表用于存储城通的文件ID
        if ctSharePasswd == None:
            self.httpHeaders = {"user-agent": userAgent,"Origin": self.ctServer}
        else:
            passName = self.shareCode.split('-')[1]
            self.httpHeaders = {"user-agent": userAgent,"Origin": self.ctServer,'cookie':f"pass_{self.shareType}{passName}={str(ctSharePasswd)}"}
    def getDirectoryShare(self):
        import requests,json,re
        getDirRequest = requests.get(f'https://webapi.ctfile.com/getdir.php?path=d&d={self.shareCode}',headers=self.httpHeaders) # 调用文件夹详情API
        getDirJson = json.loads(getDirRequest.text)
        apiUrl = f"https://webapi.ctfile.com{getDirJson['url']}" # 获取文件夹内容 API 接口 URL
        apiRequest = requests.get(apiUrl,headers=self.httpHeaders)
        apiJson = json.loads(apiRequest.text)
        for f in apiJson['aaData']:
            fileCode = re.search(r'(?<=<a target="_blank" href=").*(?=">)',f[1]).group().split('/')[-1] # 在城通文件夹分享中, 每一个子文件页面的URL中最后的一项即为fileCode. 此处调用了城通API，直接从返回值中提取fileCode. fileCode会过期
            getFileRequest = requests.get(f'https://webapi.ctfile.com/getfile.php?f={fileCode}',headers=self.httpHeaders)
            getFileJson = json.loads(getFileRequest.text)
            fileList = [getFileJson['file_name'],fileCode,getFileJson['file_id'],getFileJson['file_chk']]
            self.ctFileList.append(fileList) # ctFileList 的每一个项目都是一个列表，格式为 [fileName,fileCode,file_id,file_chk]
    def getShare(self):
        if self.shareType == 'd':
            self.getDirectoryShare()
        elif self.shareType == 'f':
            self.getFileShare()

if __name__ == '__main__':
    ct = CTFile('https://545c.com/d/21011413-44246109-662f16',1145141919810)
    ct.getShare()
    print(ct.ctFileList)
