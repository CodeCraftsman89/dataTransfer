import tkinter as tk
from queue import Queue
from tkinter import Tk
from tkinter.font import Font

from parameters import Base, Colors, FontMsgUser, FontBtnChat, FontMsgOther, ChatKeys, Connection, Message
from client import Conversation

class MessangerGui(Tk):
    def __init__(self):
        super().__init__()
        self.chats = {}
        self.archive_chat = Base.name_for_chat_all

        self.title(f"{Base.window_title} [{Connection.NICK}]")
        self.config(bg=Colors.bg_window_color)
        self.geometry(f"{Base.window_width}x{Base.window_height}+"
                      f"{(self.winfo_screenwidth() - Base.window_width) // 2}+"
                      f"{(self.winfo_screenheight() - Base.window_height) // 2}")
        self.resizable(False, False)
        self.btn_chat_font = Font(family=FontBtnChat.family, size=FontBtnChat.size, weight=FontBtnChat.weight, slant=FontBtnChat.slant)
        self.message_from_user_font = Font(family=FontMsgUser.family, size=FontMsgUser.size, slant=FontMsgUser.slant)
        self.message_from_other_font = Font(family=FontMsgOther.family, size=FontMsgOther.size, slant=FontMsgOther.slant)
        self.text_tag_user_msg = 'user_message'
        self.text_tag_other_msg = 'other_message'
        
        self.buttons_list = tk.Text(self, width=40, height=35, bd=0, padx=1, background=Colors.button_list_color, pady=1)
        self.buttons_list.place(x=10, y=20, anchor=tk.NW)

        self.sb = tk.Scrollbar(self.buttons_list, command=self.buttons_list.yview)
        self.sb.place(relx=1, y=0, anchor=tk.NE, relheight=1)
        self.buttons_list.configure(state=tk.DISABLED, yscrollcommand=self.sb.set)

        self.msg_send = tk.Text(self, width=60, height=2, bd=5, padx=1, bg=Colors.send_messages_bg_color)
        self.msg_send.place(relx=0.35, rely=0.95, anchor=tk.W)
        self.btn_send = tk.Button(self, text="Send", width=12, height=1, bg=Colors.btn_send_color)
        self.btn_send.bind("<Button-1>", self.send_message_user)
        self.btn_send.place(relx=0.99, rely=0.94, anchor=tk.E)

        chat = tk.Text(self, width=75, height=30, bd=5, padx=5, pady=5, state=tk.DISABLED,
                       bg=Colors.chat_messanger_bg_color)
        chat.place(relx=0.35, y=20, anchor=tk.NW)
        chat.tag_configure(self.text_tag_user_msg, foreground=Colors.message_from_user_text_color,
                           font=self.message_from_user_font, justify='right')
        chat.tag_configure(self.text_tag_other_msg, foreground=Colors.message_from_other_text_color,
                           font=self.message_from_other_font, justify='left')

        btn = tk.Button(self, text=Base.name_for_chat_all, width=35, height=1, bg=Colors.btn_chat_color, borderwidth=0)
        btn.bind("<Button-1>", self.open_chat)
        self.buttons_list.window_create(tk.END, window=btn)

        chat_dict = {ChatKeys.btn: btn, ChatKeys.msg_text: chat, ChatKeys.nick: Base.name_for_chat_all}
        self.chats[id(btn)] = chat_dict
        self.chats[Base.name_for_chat_all] = chat

        self.q_send = Queue()
        self.q_recv = Queue()
        self.bind(Base.receiver_event, self.process_message)

        self.messanger = Conversation(Connection.SERVER_IP, Connection.SERVER_PORT, Connection.NICK,
                                      self.q_send, self.q_recv, self, Base.receiver_event)

        self.connection_state = tk.StringVar()

        cs_lb = tk.Label(self, textvariable=self.connection_state, bg=Colors.bg_window_color)
        cs_lb.place(x=2, y=2)
        self.connection_state.set('connection to server...')
        self.after(Base.check_connection_pause, self.check_connection)

        self.mainloop()

    def open_chat(self, event):
        active_text_dict = self.chats.get(self.archive_chat)
        active_text = active_text_dict.get(ChatKeys.msg_text)
        active_text.place_forget()
        chat = self.chats.get(id(event.widget))
        new_text = chat.get(ChatKeys.msg_text)
        new_text.place(relx=0.35, y=20, anchor=tk.NW)
        self.active_chat = chat.get(ChatKeys.nick)

    def send_message_user(self, event):
        if not self.messanger.connected:
            return
        msg = self.msg_send.get("1.0", tk.END)
        types = Message.basic_types()
        if self.active_chat == Base.name_for_chat_all:
            msg_send = Message(types[1], Connection.NICK, None, msg)
        else:
            msg_send = Message(types[2], Connection.NICK, self.active_chat, msg)
        self.q_send.put(msg_send)
        self.msg_send.delete("1.0", tk.END)

        chat = self.chats[self.archive_chat]
        text = chat[ChatKeys.msg_text]
        text.configure(state=tk.NORMAL)

        text.insert(tk.INSERT, f"{msg}\n", self.text_tag_user_msg)
        text.configure(state=tk.DISABLED)

    def process_message(self, event):
        print('События')
        while not self.q_recv.empty():
            print('Сообщение')
            recv_msg = self.q_recv.get()
            self.q_recv.task_done()
            print(f'Получено сообщение: [{recv_msg.type_msg}], [{recv_msg.nick_from}], [{recv_msg.nick_to}], [{recv_msg.message}]')
            
            print('Конец')

            types = Message.basic_types()

            if recv_msg.type_msg == types[0]:
                print("Подключенные пользователи: " + recv_msg.message)
                self.check_clients(recv_msg.message.split())
            elif recv_msg.type_msg == types[1]:
                print(f"От [{recv_msg.nick_from}] сообщение для всех: {recv_msg.message}")
                self.show_message(recv_msg.nick_from, recv_msg.message, True)
            elif recv_msg.type_msg == types[2]:
                print(f"От [{recv_msg.nick_from}] сообщение: {recv_msg.message}")
            elif recv_msg.type_msg == types[3]:
                print("Соединение разорвано")
                break

    def add_client(self, nick: str):
        chat = tk.Text(self, width=75, height=30, bd=5, padx=5, pady=5, state=tk.DISABLED, bg=Colors.chat_messanger_bg_color)
        chat.tag_configure(self.text_tag_user_msg, foreground=Colors.message_from_user_text_color,
                           font=self.message_from_user_font, justify='right')
        chat.tag_configure(self.text_tag_other_msg, foreground=Colors.message_from_other_text_color,
                           font=self.message_from_other_font, justify='left')
        btn = tk.Button(self, text=nick, width=17, height=1, bg=Colors.btn_chat_color, borderwidth=0,
                        fg=Colors.btn_chat_text_color, font=self.btn_chat_font)
        btn.bind("<Button-1>", self.open_chat)
        self.buttons_list.window_create(tk.END, window=btn)

        chat_dict = {ChatKeys.btn: btn, ChatKeys.msg_text: chat, ChatKeys.nick: nick}
        self.chats[id(btn)] = chat_dict
        self.chats[nick] = chat_dict

    def remove_client(self, event):
        pass

    def show_message(self, nick: str, message: str, for_all: bool):
        if for_all:
            chat = self.chats[Base.name_for_chat_all]
            text = chat
            text.configure(state=tk.NORMAL)
            text.insert(tk.INSERT, f"{nick}: {message}\n", self.text_tag_other_msg)
            text.configure(state=tk.DISABLED)

    def check_connection(self):
        if self.messanger.connected:
            self.connection_state.set('Connected')
        else:
            self.connection_state.set('connection to server...')

    def check_clients(self):
        for nick in not self.messanger.clients:
            if nick == Connection.NICK:
                continue
            if nick not in self.chats.keys:
                self.add_client(nick)
if __name__ == "__main__":
    msng_gui = MessangerGui()