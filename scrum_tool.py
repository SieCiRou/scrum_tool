# -*- coding: utf-8 -*-
import datetime
import json
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

import customtkinter as ctk
from tkinter import messagebox
import pandas as pd

# --- 配置區 ---
target_font = ("Microsoft JhengHei", 14)
title_font = ("Microsoft JhengHei", 16, "bold")

RECORDS_DIR = Path("scrum_daily_logs")
RECORDS_DIR.mkdir(exist_ok=True)

# 定義流程階段與項目
SCRUM_WORKFLOW = {
    "站會前暖身 (08:50-09:00)": [
        "更新 Jira/Linear 任務狀態",
        "思考 3 個站會必答問題 (昨/今/阻礙)",
        "git pull --rebase main (保持最新)",
        "確認今日 1-3 個小而明確的目標"
    ],
    "深度開發 & 品質 (09:15-17:30)": [
        "Focus Mode (狀態紀錄)",
        "小步 Commit & 每 2 小時 Push",
        "Review 至少 1 個別人的 PR",
        "完成小功能即開 PR (附帶 Test Case)",
        "更新 Sprint Burndown / 看板"
    ],
    "收尾 & 明日預備 (17:30-18:00)": [
        "Merge 已通過的 PR 並刪除 Branch",
        "寫下明天第一件事",
        "確認當天進度是否符合 DoD",
        "檢查是否有 Blocker 需要 @SM/PO"
    ]
}

class ScrumHelperApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Scrum Developer Daily Pro")
        self.geometry("1100x850") # 稍微加寬以容納輸入框
        ctk.set_appearance_mode("light")
        
        # 資料初始化：儲存勾選狀態與對應的文字內容
        self.check_vars = {}
        self.entry_vars = {} 
        self.today = datetime.date.today()
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_main_content()

    def setup_sidebar(self):
        """左側深色導航欄"""
        self.sidebar = ctk.CTkFrame(self, width=100, corner_radius=0, fg_color="#3B328B")
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        lbl = ctk.CTkLabel(self.sidebar, text="S", font=("Arial", 32, "bold"), text_color="white")
        lbl.pack(pady=30)

        # 模擬圖示按鈕
        for icon in ["📅", "✅", "📝", "📧"]:
            btn = ctk.CTkButton(self.sidebar, text=icon, width=40, fg_color="transparent", font=("Arial", 20))
            btn.pack(pady=15)

    def setup_main_content(self):
        """主內容區"""
        self.main_view = ctk.CTkScrollableFrame(self, fg_color="#F8F9FD")
        self.main_view.grid(row=0, column=1, sticky="nsew")

        # --- 頂部標題卡片 ---
        self.banner = ctk.CTkFrame(self.main_view, fg_color="#FFD18B", corner_radius=15)
        self.banner.pack(fill="x", padx=30, pady=20)
        title_text = f"Good morning! \n今天是 Sprint 的一天: {self.today.strftime('%Y-%m-%d (%A)')}"
        ctk.CTkLabel(self.banner, text=title_text, font=("Microsoft JhengHei", 18, "bold"), 
                     text_color="#5A4A32", justify="left").pack(side="left", padx=30, pady=20)

        # --- Sprint Goal ---
        self.goal_frame = ctk.CTkFrame(self.main_view, fg_color="white", corner_radius=15)
        self.goal_frame.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(self.goal_frame, text="Current Sprint Goal:", font=("Microsoft JhengHei", 14, "bold")).pack(side="left", padx=20, pady=15)
        self.goal_entry = ctk.CTkEntry(self.goal_frame, placeholder_text="輸入本週目標...", width=500, border_width=0, fg_color="#F0F0F0")
        self.goal_entry.pack(side="left", padx=10, pady=10)

        # --- 生成 Checklist 與輸入框 ---
        for section, items in SCRUM_WORKFLOW.items():
            self.create_section(section, items)

        # --- 筆記區 ---
        ctk.CTkLabel(self.main_view, text="Daily Retrospective / Notes", font=title_font ).pack(anchor="w", padx=35, pady=(20, 5))
        self.note_box = ctk.CTkTextbox(self.main_view, height=150, corner_radius=15, font=target_font, border_width=1, border_color="#EEE")
        self.note_box.pack(fill="x", padx=30, pady=10)
        self.note_box.insert("0.0", "1. 昨天做了：\n2. 今天計劃：\n3. 遇到阻礙：\n4. 明天改進：")

        # --- SMTP 設定 ---
        self.config_frame = ctk.CTkFrame(self.main_view, fg_color="white", corner_radius=15)
        self.config_frame.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(self.config_frame, text="SMTP 設定:", font=("Microsoft JhengHei", 14, "bold")).pack(side="left", padx=20, pady=15)
        self.email_entry = ctk.CTkEntry(self.config_frame, placeholder_text="你的 Gmail 帳號", width=200)
        self.email_entry.pack(side="left", padx=5, pady=10)
        self.pw_entry = ctk.CTkEntry(self.config_frame, placeholder_text="你的 Gmail 密碼", width=200, show="*")
        self.pw_entry.pack(side="left", padx=5, pady=10)

        # --- 操作按鈕 ---
        self.btn_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=30, pady=30)
        self.send_btn = ctk.CTkButton(self.btn_frame, text="儲存並寄送報告", command=self.action_save_and_send,
                                      fg_color="#3B328B", hover_color="#5145B5", height=45, corner_radius=10)
        self.send_btn.pack(side="right", padx=10)

    def create_section(self, section_title, items):
        """建立帶有輸入框的分段卡片"""
        frame = ctk.CTkFrame(self.main_view, fg_color="white", corner_radius=15)
        frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(frame, text=section_title, font=("Microsoft JhengHei", 14, "bold"), text_color="#3B328B").pack(anchor="w", padx=20, pady=(10, 5))
        
        for item in items:
            item_row = ctk.CTkFrame(frame, fg_color="transparent")
            item_row.pack(fill="x", padx=20, pady=2)

            # 勾選框
            var = ctk.BooleanVar()
            self.check_vars[item] = var
            cb = ctk.CTkCheckBox(item_row, text=item, variable=var, font=("Microsoft JhengHei", 12),
                                 fg_color="#3B328B", width=250)
            cb.pack(side="left", padx=10, pady=5)

            # 對應的細節輸入框
            entry_var = ctk.StringVar()
            self.entry_vars[item] = entry_var
            detail_entry = ctk.CTkEntry(item_row, textvariable=entry_var, placeholder_text="補充細節 (如 Jira ID, 連結...)", 
                                        width=400, height=25, font=("Microsoft JhengHei", 11))
            detail_entry.pack(side="left", padx=10, fill="x", expand=True)

    def action_save_and_send(self):
        user_email = self.email_entry.get().strip()
        user_pw = self.pw_entry.get().strip()

        if not user_email or not user_pw:
            messagebox.showerror("錯誤", "請輸入 Email 與應用程式密碼！")
            return

        # 整理資料
        data = {
            "Date": str(self.today),
            "Goal": self.goal_entry.get(),
            "Checklist": {},
            "Notes": self.note_box.get("0.0", "end").strip()
        }
        
        for item in self.check_vars:
            status = "DONE" if self.check_vars[item].get() else "TODO"
            detail = self.entry_vars[item].get().strip()
            data["Checklist"][item] = {"status": status, "detail": detail}

        # 儲存 JSON
        file_path = RECORDS_DIR / f"scrum_{self.today}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 寄送郵件
        if self.send_mail(data, user_email, user_pw):
            messagebox.showinfo("Success", "今日 Scrum 記錄已儲存並寄送！")
        else:
            messagebox.showwarning("Notice", "記錄已儲存，但郵件寄送失敗。")

    def send_mail(self, data, sender_email, app_password):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = sender_email 
            msg['Subject'] = f"🚀 Scrum Daily Report - {self.today}"
            
            # 組合更精緻的郵件內容
            body = f"Sprint Goal: {data['Goal']}\n\n"
            body += "="*30 + "\n DAILY CHECKLIST \n" + "="*30 + "\n"
            
            for item, info in data["Checklist"].items():
                detail_str = f" -> ({info['detail']})" if info['detail'] else ""
                body += f"[{info['status']}] {item}{detail_str}\n"
            
            body += "\n" + "="*30 + "\n RETROSPECTIVE \n" + "="*30 + "\n"
            body += data['Notes']
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Mail Error: {e}")
            return False

if __name__ == "__main__":
    app = ScrumHelperApp()
    app.mainloop()