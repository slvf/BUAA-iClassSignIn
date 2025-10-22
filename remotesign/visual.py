from tkinter import *
from tkinter import messagebox
import sign
import check

import os
import sys

def resource_path(relative_path):
    #获取打包后资源文件的绝对路径
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class Application(Frame):
    def __init__(self, master = None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.createWidgets()

    def createWidgets(self):
        self.labelUser = Label(self, text = '请输入学号：', width = 40, anchor= 'w', font = 12, fg = 'blue')
        self.labelUser.pack()
        
        v1 = StringVar()
        self.entryUser = Entry(self, textvariable = v1, font = 12, width = 40)
        self.entryUser.pack()

        # 创建水平框架,用于放置按钮
        self.frame_buttons = Frame(self)
        self.frame_buttons.pack(side='top')  

        # 第一个按钮（签到）
        self.btnSign = Button(self.frame_buttons, text='签到', command=self.sign, font=12, width=10)
        self.btnSign.pack(side='left', padx=(0, 5))  
        self.btnSign.bind("<Enter>", self.on_enter)
        self.btnSign.bind("<Leave>", self.on_leave)

        # 第二个按钮（查询）
        self.btnCheck = Button(self.frame_buttons, text='查询本学期未签到课程', command=self.check, font=12, width=20)
        self.btnCheck.pack(side='left')  
        self.btnCheck.bind("<Enter>", self.on_enter)
        self.btnCheck.bind("<Leave>", self.on_leave)


        photo = PhotoImage(file = resource_path("assets/photo.png"))
        self.labelPhoto = Label(self, image = photo)
        self.labelPhoto.image = photo
        self.labelPhoto.pack(side= 'bottom', pady=10, fill = 'x')

    #签到
    def sign(self):
        student_id = self.entryUser.get()
        sign.sign(student_id)
        messagebox.showinfo('提示', sign.sign(student_id))
    
    #查询
    def check(self):

        student_id = self.entryUser.get()
        self.content_list = check.check_sign_status(student_id)['course']
        self.id_list = check.check_sign_status(student_id)['id']
        
        #判断输入是否有效
        if self.content_list == 'error':
            messagebox.showinfo('提示', "查无此人，请检查网络或学号是否正确")

        else:
            self.labelPhoto.pack_forget()  # 移除图片标签

            self.w = Text(self, width = 55, height = 15)
            self.w.pack()

            self.btnreturn = Button(self, text = '返回', font = 12, command = self.return_to_main)
            self.btnreturn.pack(side = 'bottom', anchor= 'e', pady = 10, padx = 15)
            self.btnreturn.bind("<Enter>", self.on_enter)
            self.btnreturn.bind("<Leave>", self.on_leave)    
            
                    
            
            def refresh_list():
                cnt = 1
                self.w.delete(1.0, END)
                self.w.insert(END, "截至今天未签到的课程：\n")
                self.w.tag_add("tag", 1.0, 1.11)
                self.w.tag_config("tag", foreground= 'red')

                #为每个未打卡课程设置单独链接
                for idx, obj in enumerate(self.content_list):
                    cnt += 1
                    self.w.insert(END, obj)

                    self.w.tag_add(f"link{cnt}", f"{cnt}.0", f"{cnt}.2")
                    self.w.tag_config(f"link{cnt}", foreground = "blue", underline = True)

                    #绑定“补签”与对应的课程id
                    def late_sign(event, current_idx = idx):
                        late_sign_message = check.late_sign(self.id_list[current_idx])
                        messagebox.showinfo('提示', late_sign_message)

                        if late_sign_message == '签到成功':
                            #签到成功则删除该行数据
                            del self.content_list[current_idx]
                            del self.id_list[current_idx]
                            
                            #函数调用自身，使列表更新时重新打印列表
                            refresh_list()

                    self.w.tag_bind(f"link{cnt}", "<Button-1>", late_sign)
            
            refresh_list()
            

    #设置返回键返回主页面
    def return_to_main(self):
        self.w.pack_forget()
        self.btnreturn.pack_forget()
        self.labelPhoto.pack(side= 'bottom', pady=10, fill = 'x')

    #鼠标停留效果
    def on_enter(self, event):
        event.widget.config(fg='blue')  

    def on_leave(self, event):
        event.widget.config(fg='black')

        
    


        
        