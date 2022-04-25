import socket

host = '172.30.1.5'
port = 8088

def get_bytes_stream(sock, length):
    buf = b''
    try:
        step = length
        while True:
            data = sock.recv(step)
            buf += data
            if len(buf) == length:
                break
            elif len(buf) < length:
                step = length - len(buf)
    except Exception as e:
        print(e)
    return buf[:length]

def write_utf8(s, sock):
    encoded = s.encode(encoding='utf-8')
    sock.sendall(len(encoded).to_bytes(4, byteorder="big"))
    sock.sendall(encoded)


server_sock = socket.socket(socket.AF_INET)
server_sock.bind((host, port))
server_sock.listen(1)
result = ''
idx = 0

while True:
    idx += 1
    print("기다리는 중")
    client_sock, addr = server_sock.accept()
    print("소켓 연결")

    len_bytes_string = bytearray(client_sock.recv(1024))[2:]
    len_bytes = len_bytes_string.decode("cp949")
    length = int(len_bytes)

    img_bytes = get_bytes_stream(client_sock, length)
    img_path = "C:/Users/Ryoo/Desktop/yolov4_test/image/"+str(idx)+str(addr[1])+".jpg"
    
    with open(img_path, "wb") as writer:
        writer.write(img_bytes)
    print(img_path+" is saved")
    
    img_name = 'img'+str(idx)+str(addr[1])+".jpg"
    ##이미지를 모델에 입력해서 result에 detection 결과 저장하는 코드##
    
    # write_utf8(img_path, client_sock)
    # write_utf8(result, client_sock)
    
    client_sock.close()

server_sock.close()

