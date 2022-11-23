import socket
import pathlib
from functions import CheckWebsite
from functions import getHost
from functions import getPath
from functions import getHeader
from functions import ContentLength
from functions import getFileName
from functions import isContentLength
from functions import ContentLengthBody
from functions import isChunked
from functions import ChunkedBody
from functions import isSubFolder
from functions import SubFolderBody

def ClientConnection(website):
    # Tạo TPC socket IPv4
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Nếu website có "https://" thì xóa, thiếu "/" thì thêm
    website = CheckWebsite(website)

    # host là phần trước dấu "/" đầu tiên
    host = getHost(website)

    # path là phần sau dấu "/" đầu tiên, nếu sau đó không có gì nữa thì mặc định là index.html
    path = getPath(website)

    # tạo kết nối đến server ở cổng 80
    s.connect((host, 80))

    # request GET
    request = "GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"

    # gửi request đến server
    s.send(request.encode())

    try:
        #lấy header
        header = ""
        header = getHeader(s, header)

        # tìm Content-Length, nếu không có gán nó bằng 0
        content_length = ContentLength(header)
        
        # tìm Transfer-Encoding: chunked
        pos_c = header.find("Transfer-Encoding: chunked")

        # tìm kiểu dữ liệu filename ở Content-Type
        pos_ct = header.find("Content-Type: ")
    
        # Lấy tên của file
        filename = getFileName(header, path, pos_ct, pos_c)
        
        # Lấy body
        # Nếu cho biết trước Content-Length
        if (isContentLength(content_length)):
            body = ContentLengthBody(s, content_length)
            
        # Nếu là chunked
        elif (isChunked(pos_c)):
            body = ChunkedBody(s, body)

        # Nếu đường link là subfolder
        if (isSubFolder(website)):
            SubFolderBody(s, host, website, body)
        else:
            # ghi vào file
            file = open(filename, 'wb')
            file.write(body)
            file.close()
    except:
        print("Disconnect")
    finally:
        s.close()