import socket
import cv2
import numpy as np
import time

host = '172.30.1.7'
port = 8080


# 이미지 받는 함수
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

# 결과 보내는 함수
def send_result(s, sock):
    encoded = s.encode(encoding='utf-8')
    sock.sendall(len(encoded).to_bytes(4, byteorder="big"))
    sock.sendall(encoded)

# yolo4 인식 함수 

def yolo_detect():

    try:

            net = cv2.dnn.readNet("yolov4-custom_last.weights", "yolov4-custom.cfg")
            classes = []
            with open("obj.names", "r") as f:
                classes = [line.strip() for line in f.readlines()]
            layer_names = net.getLayerNames()
            output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
            colors = np.random.uniform(0, 255, size=(len(classes), 3))


            img = cv2.imread("image/img1.jpg")
            img = cv2.resize(img, None, fx=0.4, fy=0.4)
            height, width, channels = img.shape

            
            blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)
            
            class_ids = []
            confidences = []
            boxes = []
            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        # Object detected
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        # 좌표
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)


            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
            result = []

            font = cv2.FONT_HERSHEY_PLAIN
            for i in range(len(boxes)):
                if i in indexes:
                    x, y, w, h = boxes[i]
                    label = str(classes[class_ids[i]])
                    result.append(label)
                    # print(label)
                    color = colors[0]
                    cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                    cv2.putText(img, label, (x, y + 30), font, 1, color, 2)

            
            # cv2.imshow("Image", img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            
            result = list(set(result)) # 값이 여러개일 수도 있어서 
            yolo_result = ''

            for i in range(len(result)):
                yolo_result += result[i] 
                if i+1 != len(result):
                   yolo_result += '_'
           
            return yolo_result

           

    except Exception as e:
        print(str(e))

    


# 소켓 통신 

server_sock = socket.socket(socket.AF_INET)
server_sock.bind((host, port))
server_sock.listen(10)
result = ''
idx = 0

while True:
    # idx += 1
    print("기다리는 중")
    client_sock, addr = server_sock.accept()
    print("소켓 연결")

    len_bytes_string = bytearray(client_sock.recv(1024))[2:]
    print(len_bytes_string)

    # len_bytes = len_bytes_string.decode("cp949")
    len_bytes = len_bytes_string.decode("utf-8")

    length = int(len_bytes)

    img_bytes = get_bytes_stream(client_sock, length)
    # img_path = "C:/Users/Ryoo/Desktop/yolov4_test/image/"+"img1"+".jpg"
    img_path = "./image/"+"img1"+".jpg"
    
    with open(img_path, "wb") as writer:
        writer.write(img_bytes)
    print(img_path+" is saved")
    
    yolo_result = ''
    yolo_result = yolo_detect()
    # yolo_temp = 'plastic wrapping_plastic bottle'
    
    print(yolo_result)
    time.sleep(1.5)
    send_result(yolo_result, client_sock)
    # send_result(result, client_sock)
    
    client_sock.close()

# server_sock.close()

