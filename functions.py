import pathlib

# Kiểm tra website nhập vào có hợp lệ không
def CheckWebsite(website):
    if website.find("http://") != -1:
        website = website[7 : ]
    if website.find("/") == -1:
        website = website + "/"
    return website

def getHost(website):
    return website[ : website.find("/")]

def getPath(website):
    path = website[website.find("/") : ]
    if path == "/":
        path = path + "index.html"
    return path

# Hàm find() trả về -1 nếu không tìm thấy giá trị
def getHeader(s, header):
    #lấy header
    while True:
        header = header + s.recv(1).decode()
        # nếu header rỗng thì thoát vòng lặp
        if not header:
            break
        # đọc đến hết header (ở chuỗi kí tự \r\n\r\n)
        if header.find("\r\n\r\n") != -1:
            break
    print(header)
    return header

def getFileName(header, path, pos_ct, pos_c):
    filename = ""
    # nếu kiểu dữ liệu là application, mặc định kiểu dữ liệu của file là kiểu dữ liệu trong phần path
    # hoặc nếu file có định dạng html thì lấy tên file ở đuôi của path
    if header.find("application") != -1 or (header.find("html", pos_ct) != -1 and path[path.rfind("/") + 1 : ] != "" and pos_c == -1):
        filename = path[path.rfind("/") + 1 : ]
    # nếu Content-Type có dạng "kiểu dữ liệu" / "tên đuôi" \r\n thì tên đuôi nằm giữa "/" và "\r\n"
    elif (header.find("\r\n", pos_ct) < header.find(";", pos_ct) or header.find(";" , pos_ct) == -1):
        filename = "index." + header[header.find("/", pos_ct) + 1 : header.find("\r\n", pos_ct)]
    # nếu Content-Type có dạng "kiểu dữ liệu" / "tên đuôi" ; "kiểu mã hóa" \r\n thì tên đuôi nằm giữa "/" và ";"
    else:
        filename = "index." + header[header.find("/", pos_ct) + 1 : header.find(";", pos_ct)]
    return filename

def ContentLength(header):
    # Tìm Content-Length, nếu không có gán nó bằng 0
    # Vì Content-Length được biểu diễn theo hệ 16 
    if header.find("Content-Length: ") != -1:
        start_cl = header.find("Content-Length: ") + 16
        end_cl = header.find("\r\n", start_cl)
        content_length = int(header[start_cl : end_cl])
    else:
        content_length = 0
    return content_length

def isContentLength(content_length):
    return content_length != 0

def ContentLengthBody(s, content_length):
    body = b""
    #nhận đến khi chiều dài body = content length
    while len(body) < content_length:
        # vì kích thước file lớn nên ta lấy 10000 bytes cho mỗi lần đọc
        body = body + s.recv(10000)
        # nếu body rỗng thì thoát vòng lặp
        if not body:
            break
    return body

# Chunked có dạng:
# 4\r\n        (bytes to send)
# Wiki\r\n     (data)
def isChunked(pos_c):
    return pos_c != -1

def ChunkedBody(s, body):
    while True:
        # lấy size của chunked
        chunked_size_str = ""
        while True:
            # lấy về dạng nhị phân và đổi về kiểu string
            chunked_size_str = chunked_size_str + s.recv(1).decode()
            # dừng nhận khi tìm thấy \r\n, khi đó đã lấy đủ các đoạn chunked
            if chunked_size_str.find("\r\n") != -1:
                # đổi kiểu string -> thập lục phân -> thập phân
                chunked_size = int(chunked_size_str[ : chunked_size_str.find("\r\n")], 16)
                break
        # nếu chunked_size = 0 tức là hết phần body
        if chunked_size == 0:
            break
        # lấy chunked
        chunked = b""
        res_len = 0     # size của chunked đang lấy
        # nhận đến khi chiều dài chunked = chunked_size
        while res_len < chunked_size:
            # nếu nhận chưa hết thì nhận tiếp phần còn lại 
            res = s.recv(chunked_size - res_len)
            res_len = res_len + len(res)
            chunked = chunked + res
        # chép chunked vào body
        body = body + chunked
        # bỏ đi chuỗi "\r\n" thừa
        delete = s.recv(2)
        # nếu body rỗng thì thoát vòng lặp
        if not body:
            break
    return body

def isSubFolder(website):
    return (website[website.rfind("/") + 1 : ]  == "" and website.rfind("/", 0, website.rfind("/") - 1) != -1)

def SubFolderBody(s, host, website, body):
    # nếu đường link là subfolder
    if (isSubFolder(website)):
        # tạo folder có tên nằm giữa 2 kí tự "/" phải cùng
        foldername = website[website.rfind("/", 0, website.rfind("/") - 1) + 1 : website.rfind("/")]
        # "./" có nghĩa là bằng cấp với file python đang chạy
        folderpath = "./" + foldername
        # tạo folder có tên là foldername
        path = pathlib.Path(folderpath)
        # nếu đã có sẵn thì không cần tạo tiếp
        path.mkdir(exist_ok = True)
        # tìm vị trí của kí tự "href=" đầu tiên
        pos_cur_file = body.find(b"href=")
        # đọc đến khi hết "href=" trong body
        while pos_cur_file != -1:
            # nếu "href=" có file cần tải thì gửi request để tải file với file cần tải phải có đuôi là một kiểu nhất định
            if body.find(b".", pos_cur_file, body.find(b">", pos_cur_file)) != -1:
                # tên file nằm giữa " "
                filename = body[body.find(b"\"", pos_cur_file) + 1 : body.find(b"\"", body.find(b"\"", pos_cur_file) + 1)].decode()
                # đường dẫn = website gốc + tên file
                path = website[website.find("/") : ] + filename
                request = "GET " + path + " HTTP/1.1\r\nHost:" + host + "\r\n\r\n"
                s.send(request.encode())
                
                # lấy header của từng file
                header = ""
                header = getHeader(s, header)
                # Tìm content-length, nếu không có gán bằng 0
                content_length = ContentLength(header)

                # tìm Transfer-Encoding: chunked
                pos_c = header.find("Transfer-Encoding: chunked")

                # lấy body của từng file
                body_subfile = b""
                # nếu cho biết trước content_length
                if isContentLength(content_length):
                    body_subfile = ContentLengthBody(s, body_subfile)
                
                # nếu kiểu được cho là chunked
                elif isChunked(pos_c):
                    body_subfile = ChunkedBody(s, body_subfile)

                # ghi vào file
                file = open("./" + foldername + "/" + filename, 'wb')
                file.write(body_subfile)
                file.close()
            # Tìm vị trí "href=" kế tiếp
            pos_cur_file = body.find(b"href=", pos_cur_file + 6)
                