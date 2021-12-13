import socket,time,os

class Client():
    def __init__(self) -> None:
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        print('hostname:', self.hostname)
        print('ip:', self.ip)

    def connect(self,target_ip,target_port,host_PORT=None):
        self.target_ip = target_ip
        self.target_port = target_port
        self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_addr = (target_ip , target_port)  # ip port
        if host_PORT: #默认随机端口号
            self.client.bind((self.ip, host_PORT))
        try:
            self.client.connect(server_addr)
            print('successful, connected the target IP, wait for next order...')

        except:
            print('error, fail to connect the target IP,',socket.error)

    def file_read(self,file_path):  #读取文件的方法
        mes = b''
        try:
            file = open(file_path,'rb')
            mes = file.read()
        except:
            print('error{}'.format(file_path))
        else:
            file.close()
            return mes

    def send_file(self,filepath):
        st = time.time()
        dirname, filename = os.path.split(filepath)
        data = self.file_read(filepath)
        self.client.send('{}|{}'.format(len(data), filename).encode())  #默认编码 utf-8,发送文件长度和文件名
        reply = self.client.recv(1024)    
        if 'ok' == reply.decode():       #确认一下服务器get到文件长度和文件名数据
            go = 0
            total = len(data)
            while go < total:            #发送文件
                data_to_send = data[go:go + 102400000]  # 10M/s
                self.client.send(data_to_send)
                go += len(data_to_send)
            reply = self.client.recv(1024)
            if 'done' == reply.decode():
                print('{} send successfully'.format(filepath))
            self.client.close()     
            et = time.time()
            print('time cost:',et-st)


target_IP  = '219.223.175.200'
target_PORT = 8888
filepath = 'F:\\Swim_Proj\\Photo_0611_1a.MOV'

client = Client()
client.connect(target_IP,target_PORT,host_PORT=6666)  # host_PORT 可以为空，随机端口
client.send_file(filepath)


