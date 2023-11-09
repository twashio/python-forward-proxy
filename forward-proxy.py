import socket
import sys
import threading


class Server:
    def __init__(self, buffer_size: int = 1024, listening_port: int = 8000, max_connection: int = 5) -> None:
        self.__socket = None
        self.__buffer_size = buffer_size
        self.__listening_port = listening_port
        self.__max_connection = max_connection

    # サーバのスタート
    def start(self) -> None:
        # ソケットの作成
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind(('', self.__listening_port))
            self.__socket.listen(self.__max_connection)
            print("[*] Server started: %d" % (self.__listening_port))
        except Exception as error:
            print("[*] Unable to Initialize ")
            print(error)
            sys.exit(1)

    # コネクションを確立し，通信を中継する
    def accept(self) -> None:
        while True:
            try:
                conn, addr = self.__socket.accept()
                print("[*] Accept: %s:%d" % (addr[0], addr[1]))
                data = conn.recv(self.__buffer_size)

                t = threading.Thread(
                    target=self.proxy, args=(conn, data))  # スレッドを作成
                t.start()  # スレッドを開始

            except KeyboardInterrupt:
                self.__socket.close()
                print("\n[*] Shutdown")
                sys.exit(0)

    # リクエストを代理でクエリし，結果をフォワードする
    def proxy(self, conn, data) -> None:
        print(data)

       # サーバのアドレスとポートを取得
        webserver, port = self.parse_request(data)

        try:
            # Webサーバとの通信するためのソケットを作成
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((webserver, port))  # Webサーバとのコネクションを確立
            sock.send(data)  # クライアントに代わりデータを送信

            while True:
                reply = sock.recv(self.__buffer_size)  # Webサーバから応答を受け取る
                if (len(reply) > 0):
                    conn.send(reply)
                else:
                    break

            sock.close()  # Webサーバとのコネクションを閉じる
            conn.close()  # クライアントとのコネクションを閉じる

        except Exception as error:
            sock.close()
            conn.close()
            print(error)
            sys.exit(1)

    # HTTPリクエストの解析
    def parse_request(self, data) -> (str, int):
        try:
            first_line = data.split(b'\n')[0]  # リクエストの1行目を抽出
            url = first_line.split()[1]  # URLを抽出

            http_pos = url.find(b'://')  # 「://」の位置を見つける
            if (http_pos == -1):
                tmp = url
            else:
                tmp = url[(http_pos+3):]  # 「://」以降を抽出

            port_pos = tmp.find(b':')  # 「:」の位置を見つける
            webserver_pos = tmp.find(b'/')  # 「/」の位置を見つける

            if webserver_pos == -1:
                webserver_pos = len(tmp)
            webserver = ""
            port = -1
            if (port_pos == -1):  # 80番ポートを使用している場合
                port = 80
                webserver = tmp[:webserver_pos]
            else:  # 80番ポートを使用していない場合
                port = int(tmp[port_pos+1:][:webserver_pos-port_pos-1])
                webserver = tmp[:port_pos]

            return webserver, port

        except Exception as error:
            print(error)
            sys.exit(1)


if __name__ == '__main__':
    server = Server()
    server.start()
    server.accept()
