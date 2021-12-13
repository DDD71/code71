import socket,time,os,sys


class Server():
    def __init__(self) -> None:
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)
        print('hostname:', self.hostname)
        print('ip:', self.ip)

    def build_server(self,port=8888):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind(('', port))  # 绑定端口
            self.server.listen(16) # 设置监听数
            print('successful building a server,PORT:',port)
            print('Waiting connection...')
        except socket.error as msg:
            print (msg)
            sys.exit(1)
            print('failt to build a server, try again...')

    def get_file(self):

        while True:
            new_client,client_addr = self.server.accept()
            print('a new client coming!!! new client :',client_addr)
            st = time.time()
            info = new_client.recv(1024)    #首先接收一段数据，这段数据包含文件的长度和文件的名字，使用|分隔，具体规则可以在客户端自己指定
            length,file_name = info.decode().split('|')
            print('length {},filename {}'.format(length,file_name))
            if length and file_name:
                newfile = open(file_name,'wb') #这里可以使用从客户端解析出来的文件名
                new_client.send(b'ok')  #表示收到文件长度和文件名
                file = b''
                total = int(length)
                get = 0
                while get < total:     #接收文件
                    data = new_client.recv(102400000)
                    file += data
                    get = get + len(data)
                et = time.time()
                print('time cost:',et-st)
                print('应该接收{},实际接收{}'.format(length,len(file)))
                if file:
                    print('acturally length:{}'.format(len(file)))
                    newfile.write(file[:])
                    newfile.close()
                    new_client.send(b'done')  #告诉完整的收到文件了
                new_client.close()
         

PORT = 8888
    
server = Server()
server.build_server(PORT)
server.get_file()

