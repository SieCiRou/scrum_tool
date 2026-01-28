# -*- coding: utf-8 -*-
import datetime
import json
from pathlib import Path
import customtkinter as ctk  # 建議使用這個庫來達成圖片中的現代感
from tkinter import messagebox
import pandas as pd

# 設定主題顏色 (接近圖片中的淡紫色與白色)
ctk.set_appearance_mode("light") 
ctk.set_default_color_theme("blue") 

CHECKLIST_ITEMS = [
    "Daily Scrum 參加 (15m)",
    "更新 Sprint Goal 進度",
    "列出今日 1-3 項重點",
    "排除或提出 Blocker",
    "保持 Git Main 最新",
    "完成小功能開 PR",
    "更新 Jira / 看板"
]

class ScrumModernGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Helper - 每日 Scrum 管理")
        self.geometry("900x650")
        
        # 設定網格權重
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- 側邊欄 (Sidebar) 參考圖片左側深色條 ---
        self.sidebar_frame = ctk.CTkFrame(self, width=80, corner_radius=0, fg_color="#3B328B")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="H", font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        self.logo_label.pack(pady=30)
        
        # 模仿圖片中的圖示按鈕
        for icon in ["🏠", "📊", "💬", "🕒", "⚙️"]:
            btn = ctk.CTkButton(self.sidebar_frame, text=icon, width=40, fg_color="transparent", hover_color="#5145B5")
            btn.pack(pady=15)

        # --- 主內容區 (Main Content) ---
        self.main_container = ctk.CTkScrollableFrame(self, fg_color="#F5F6FA", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        # 頂部歡迎區 (參考圖片黃色橫幅)
        self.welcome_card = ctk.CTkFrame(self.main_container, fg_color="#FFD18B", height=120, corner_radius=15)
        self.welcome_card.pack(fill="x", padx=30, pady=20)
        
        self.welcome_label = ctk.CTkLabel(self.welcome_card, 
                                          text=f"Good morning, Ci Rou!\n今天是 {datetime.date.today()}，準備好開始 Scrum 了嗎？",
                                          font=ctk.CTkFont(family="Microsoft JhengHei", size=18, weight="bold"),
                                          text_color="#5A4A32", justify="left")
        self.welcome_label.pack(side="left", padx=30)

        # 標題：Popular Services -> 改為 Checklist
        self.section_label = ctk.CTkLabel(self.main_container, text="Scrum Checklist", 
                                          font=ctk.CTkFont(family="Microsoft JhengHei", size=20, weight="bold"), text_color="#333")
        self.section_label.pack(anchor="w", padx=35, pady=(10, 5))

        # Checklist 卡片區域 (模仿圖片的中間卡片)
        self.check_frame = ctk.CTkFrame(self.main_container, fg_color="white", corner_radius=15)
        self.check_frame.pack(fill="x", padx=30, pady=10)

        self.check_vars = {}
        # 使用兩欄佈局
        inner_frame = ctk.CTkFrame(self.check_frame, fg_color="transparent")
        inner_frame.pack(padx=20, pady=20)
        
        for i, item in enumerate(CHECKLIST_ITEMS):
            var = ctk.BooleanVar(value=False)
            self.check_vars[item] = var
            cb = ctk.CTkCheckBox(inner_frame, text=item, variable=var, 
                                 font=("Microsoft JhengHei", 13),
                                 fg_color="#3B328B", border_color="#3B328B")
            cb.grid(row=i//2, column=i%2, padx=20, pady=10, sticky="w")

        # 筆記區 (參考圖片底部 Order Statistics 的深色質感)
        self.note_label = ctk.CTkLabel(self.main_container, text="Notes & Blockers", 
                                       font=ctk.CTkFont(family="Microsoft JhengHei", size=20, weight="bold"), text_color="#333")
        self.note_label.pack(anchor="w", padx=35, pady=(20, 5))

        self.note_text = ctk.CTkTextbox(self.main_container, height=120, corner_radius=15, 
                                        border_width=1, border_color="#DDD", font=("Microsoft JhengHei", 14))
        self.note_text.pack(fill="x", padx=30, pady=10)

        # 按鈕區 (放在右下角)
        self.btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.btn_frame.pack(fill="x", padx=30, pady=20)

        self.save_btn = ctk.CTkButton(self.btn_frame, text="儲存並寄送 Excel", 
                                      fg_color="#3B328B", hover_color="#5145B5",
                                      font=("Microsoft JhengHei", 14, "bold"), height=45, corner_radius=10)
        self.save_btn.pack(side="right", padx=10)

        self.only_save_btn = ctk.CTkButton(self.btn_frame, text="僅儲存", 
                                           fg_color="white", text_color="#3B328B", border_width=1, border_color="#3B328B",
                                           hover_color="#EEE",
                                           font=("Microsoft JhengHei", 14), height=45, corner_radius=10)
        self.only_save_btn.pack(side="right", padx=10)

if __name__ == "__main__":
    app = ScrumModernGUI()
    app.mainloop()