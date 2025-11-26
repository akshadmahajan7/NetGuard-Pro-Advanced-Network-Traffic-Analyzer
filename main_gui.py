import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import threading
import pandas as pd
from collections import deque
from datetime import datetime
import os

# PDF Library
from fpdf import FPDF
from fpdf.enums import XPos, YPos  # <--- NEW: Required for modern PDF generation

# Import our custom modules
from src.database import DBManager
from src.backend_sniffer import start_sniffing_thread, stop_sniffer_flag

# --- CONFIGURATION ---
COLOR_BG = "#1e1e2f"        
COLOR_CARD = "#27293d"      
COLOR_TEXT = "#ffffff"
COLOR_ACCENT = "#e14eca"    
COLOR_SUCCESS = "#00f2c3"   
COLOR_WARNING = "#ff8d72"   

# Styles
plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = COLOR_CARD
plt.rcParams['axes.facecolor'] = COLOR_CARD
plt.rcParams['axes.edgecolor'] = COLOR_CARD
plt.rcParams['text.color'] = 'white'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

class PDFReport(FPDF):
    def header(self):
        # Professional Dark Header
        self.set_fill_color(30, 30, 47) # Dark Navy
        self.rect(0, 0, 210, 40, 'F')
        
        # Logo / Title Text (Switched to Helvetica to fix warning)
        self.set_font('Helvetica', 'B', 20)
        self.set_text_color(255, 255, 255)
        # Updated positioning syntax
        self.cell(0, 15, 'NetGuard Security Report', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        
        # Timestamp
        self.set_font('Helvetica', 'I', 10)
        self.set_text_color(200, 200, 200)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')

class NetGuardApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("NetGuard Pro")
        self.geometry("1400x900")
        self.configure(bg=COLOR_BG)
        
        # Database & State
        self.gui_db = DBManager()
        self.sniffer_thread = None
        self.is_running = False
        self.current_page = "dashboard" 
        self.update_job = None
        self.traffic_data = deque([0]*20, maxlen=20) 
        self.pages = {} 

        # Init UI
        self.setup_sidebar()
        self.container = tk.Frame(self, bg=COLOR_BG)
        self.container.pack(side=RIGHT, fill=BOTH, expand=True, padx=20, pady=20)
        
        self.build_dashboard_page()
        self.build_statistics_page()
        self.build_logs_page()
        self.build_settings_page()
        self.show_page("dashboard")
        self.update_app_loop()

    # --- SIDEBAR & NAV ---
    def setup_sidebar(self):
        sidebar = tk.Frame(self, bg=COLOR_CARD, width=260)
        sidebar.pack(side=LEFT, fill=Y)
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="NetGuard", bg=COLOR_CARD, fg="white", 
                 font=("Segoe UI", 24, "bold")).pack(pady=40, padx=20, anchor="w")

        self.nav_btns = {}
        self.create_nav_item(sidebar, "dashboard", "📊  Dashboard")
        self.create_nav_item(sidebar, "statistics", "📉  Statistics")
        self.create_nav_item(sidebar, "logs", "🛡  Security Logs")
        self.create_nav_item(sidebar, "settings", "⚙️  Settings")

        ctrl_panel = tk.Frame(sidebar, bg=COLOR_CARD)
        ctrl_panel.pack(side=BOTTOM, fill=X, padx=20, pady=40)
        self.btn_start = ttk.Button(ctrl_panel, text="START MONITORING", bootstyle="success", command=self.start_sniffing)
        self.btn_start.pack(fill=X, pady=5)
        self.btn_stop = ttk.Button(ctrl_panel, text="STOP SYSTEM", bootstyle="danger", command=self.stop_sniffing, state=DISABLED)
        self.btn_stop.pack(fill=X, pady=5)

    def create_nav_item(self, parent, page_name, text):
        frame = tk.Frame(parent, bg=COLOR_CARD)
        frame.pack(fill=X, pady=5)
        indicator = tk.Frame(frame, bg=COLOR_CARD, width=4, height=30)
        indicator.pack(side=LEFT)
        btn = tk.Label(frame, text=text, bg=COLOR_CARD, fg="#a9a9a9", font=("Segoe UI", 11), cursor="hand2")
        btn.pack(side=LEFT, padx=15)
        btn.bind("<Button-1>", lambda e: self.show_page(page_name))
        self.nav_btns[page_name] = {'frame': frame, 'btn': btn, 'indicator': indicator}

    def show_page(self, page_name):
        self.current_page = page_name
        for name, widgets in self.nav_btns.items():
            if name == page_name:
                widgets['btn'].config(fg=COLOR_ACCENT, font=("Segoe UI", 11, "bold"))
                widgets['indicator'].config(bg=COLOR_ACCENT)
            else:
                widgets['btn'].config(fg="#a9a9a9", font=("Segoe UI", 11))
                widgets['indicator'].config(bg=COLOR_CARD)

        for name, frame in self.pages.items(): frame.pack_forget()
        self.pages[page_name].pack(fill=BOTH, expand=True)

        if page_name == "logs": self.refresh_logs_table()
        if page_name == "statistics": self.refresh_stats_graph()

    # --- PAGES ---
    def build_dashboard_page(self):
        page = tk.Frame(self.container, bg=COLOR_BG)
        self.pages['dashboard'] = page
        self.lbl_status = tk.Label(page, text="Status: SYSTEM STOPPED", bg=COLOR_BG, fg=COLOR_WARNING, font=("Segoe UI", 10, "bold"))
        self.lbl_status.pack(anchor="w", pady=(0, 20))
        
        row1 = tk.Frame(page, bg=COLOR_BG)
        row1.pack(fill=X, pady=(0, 20))
        self.card_total = self.create_stat_card(row1, "Total Packets", "0", "white")
        self.card_tcp = self.create_stat_card(row1, "TCP Traffic", "0", COLOR_SUCCESS)
        self.card_udp = self.create_stat_card(row1, "UDP Traffic", "0", COLOR_WARNING)

        row2 = tk.Frame(page, bg=COLOR_BG)
        row2.pack(fill=BOTH, expand=True, pady=(0, 20))
        frm_line = self.create_content_frame(row2, "Traffic Volume (Last 10s)")
        frm_line.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 10))
        self.fig_live, self.ax_live = plt.subplots(figsize=(5,3))
        self.cvs_live = FigureCanvasTkAgg(self.fig_live, master=frm_line)
        self.cvs_live.get_tk_widget().pack(fill=BOTH, expand=True)

        frm_donut = self.create_content_frame(row2, "Protocol Share")
        frm_donut.pack(side=RIGHT, fill=BOTH, expand=True, padx=(10, 0))
        self.fig_donut, self.ax_donut = plt.subplots(figsize=(4,3))
        self.cvs_donut = FigureCanvasTkAgg(self.fig_donut, master=frm_donut)
        self.cvs_donut.get_tk_widget().pack(fill=BOTH, expand=True)

        frm_log = self.create_content_frame(page, "Live Packet Stream")
        frm_log.pack(fill=BOTH, expand=True)
        self.txt_log = scrolledtext.ScrolledText(frm_log, height=6, bg=COLOR_BG, fg=COLOR_SUCCESS, font=("Consolas", 9), borderwidth=0)
        self.txt_log.pack(fill=BOTH, expand=True, padx=10, pady=10)

    def build_statistics_page(self):
        page = tk.Frame(self.container, bg=COLOR_BG)
        self.pages['statistics'] = page
        tk.Label(page, text="Deep Traffic Analysis", bg=COLOR_BG, fg="white", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=20)
        frm_graph = self.create_content_frame(page, "Top 5 Source IP Addresses")
        frm_graph.pack(fill=BOTH, expand=True)
        self.fig_stats, self.ax_stats = plt.subplots(figsize=(8, 4))
        self.cvs_stats = FigureCanvasTkAgg(self.fig_stats, master=frm_graph)
        self.cvs_stats.get_tk_widget().pack(fill=BOTH, expand=True, padx=10, pady=10)

    def build_logs_page(self):
        page = tk.Frame(self.container, bg=COLOR_BG)
        self.pages['logs'] = page
        header = tk.Frame(page, bg=COLOR_BG)
        header.pack(fill=X, pady=20)
        tk.Label(header, text="Security Audit Logs", bg=COLOR_BG, fg="white", font=("Segoe UI", 18, "bold")).pack(side=LEFT)
        ttk.Button(header, text="🔃 Refresh Data", bootstyle="info-outline", command=self.refresh_logs_table).pack(side=RIGHT)
        
        cols = ("Time", "Source", "Destination", "Protocol", "Length")
        self.tree = ttk.Treeview(page, columns=cols, show='headings', bootstyle="dark")
        for col in cols: self.tree.heading(col, text=col)
        self.tree.pack(fill=BOTH, expand=True)

    def build_settings_page(self):
        page = tk.Frame(self.container, bg=COLOR_BG)
        self.pages['settings'] = page
        tk.Label(page, text="System Configuration", bg=COLOR_BG, fg="white", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=20)
        card_exp = self.create_content_frame(page, "Data Management")
        card_exp.pack(fill=X, pady=10)
        
        ttk.Button(card_exp, text="📄 Generate PDF Report", bootstyle="warning", command=self.export_pdf).pack(anchor="w", padx=20, pady=10)
        ttk.Button(card_exp, text="🗑  Flush/Clear Database", bootstyle="danger", command=self.flush_db).pack(anchor="w", padx=20, pady=10)

    # --- HELPERS ---
    def create_stat_card(self, parent, title, value, color):
        card = tk.Frame(parent, bg=COLOR_CARD, padx=20, pady=20)
        card.pack(side=LEFT, fill=X, expand=True, padx=10)
        tk.Label(card, text=title, bg=COLOR_CARD, fg="#a9a9a9").pack(anchor="w")
        lbl = tk.Label(card, text=value, bg=COLOR_CARD, fg=color, font=("Segoe UI", 24, "bold"))
        lbl.pack(anchor="w")
        return lbl

    def create_content_frame(self, parent, title):
        frame = tk.Frame(parent, bg=COLOR_CARD, padx=10, pady=10)
        tk.Label(frame, text=title, bg=COLOR_CARD, fg="white", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))
        return frame

    # --- LOGIC ---
    def start_sniffing(self):
        if not self.is_running:
            self.is_running = True
            self.lbl_status.config(text="Status: MONITORING ACTIVE", fg=COLOR_SUCCESS)
            self.btn_start.config(state=DISABLED)
            self.btn_stop.config(state=NORMAL)
            self.sniffer_thread = threading.Thread(target=start_sniffing_thread, daemon=True)
            self.sniffer_thread.start()

    def stop_sniffing(self):
        if self.is_running:
            stop_sniffer_flag.set()
            self.is_running = False
            self.lbl_status.config(text="Status: SYSTEM STOPPED", fg=COLOR_WARNING)
            self.btn_start.config(state=NORMAL)
            self.btn_stop.config(state=DISABLED)

    def update_app_loop(self):
        if self.is_running and self.current_page == "dashboard":
            self.update_dashboard_data()
        if self.winfo_exists(): self.after(5000, self.update_app_loop)

    def update_dashboard_data(self):
        try:
            # 1. Update KPI Cards (Total)
            self.gui_db.cursor.execute("SELECT COUNT(*) FROM packet_logs")
            result = self.gui_db.cursor.fetchone()
            total = result[0] if result else 0
            self.card_total.config(text=str(total))
            
            # Count TCP/UDP with Robust TRIM/UPPER checks
            self.gui_db.cursor.execute("SELECT COUNT(*) FROM packet_logs WHERE UPPER(TRIM(protocol)) = 'TCP'")
            tcp_count = self.gui_db.cursor.fetchone()[0]
            self.card_tcp.config(text=str(tcp_count))

            self.gui_db.cursor.execute("SELECT COUNT(*) FROM packet_logs WHERE UPPER(TRIM(protocol)) = 'UDP'")
            udp_count = self.gui_db.cursor.fetchone()[0]
            self.card_udp.config(text=str(udp_count))
            
            # 2. Update Donut Chart
            self.gui_db.cursor.execute("SELECT UPPER(TRIM(protocol)), COUNT(*) FROM packet_logs GROUP BY UPPER(TRIM(protocol))")
            data = self.gui_db.cursor.fetchall()
            df = pd.DataFrame(data, columns=['protocol', 'count'])
            
            self.ax_donut.clear()
            if not df.empty:
                self.ax_donut.pie(df['count'], labels=df['protocol'], colors=[COLOR_ACCENT, COLOR_SUCCESS, COLOR_WARNING], autopct='%1.1f%%')
                self.ax_donut.add_artist(plt.Circle((0,0), 0.70, fc=COLOR_CARD))
            self.cvs_donut.draw()

            # 3. Update Moving Line Graph
            query = "SELECT COUNT(*) FROM packet_logs WHERE captured_at >= NOW() - INTERVAL 10 SECOND"
            self.gui_db.cursor.execute(query)
            count_last = self.gui_db.cursor.fetchone()[0]

            self.traffic_data.append(count_last)
            self.ax_live.clear()
            self.ax_live.plot(self.traffic_data, color=COLOR_ACCENT, linewidth=2, marker='o')
            self.ax_live.fill_between(range(len(self.traffic_data)), 0, self.traffic_data, color=COLOR_ACCENT, alpha=0.1)
            self.ax_live.set_title("Traffic Volume (Packets / 10s)", color="gray", fontsize=8)
            self.cvs_live.draw()
            
            # 4. Text Logs
            self.gui_db.cursor.execute("SELECT src_ip, dst_ip, protocol, length, captured_at FROM packet_logs ORDER BY id DESC LIMIT 5")
            rows = self.gui_db.cursor.fetchall()
            self.txt_log.config(state='normal')
            self.txt_log.delete('1.0', tk.END)
            for row in reversed(rows):
                 ts = row[4].strftime('%H:%M:%S') if row[4] else "00:00:00"
                 self.txt_log.insert(tk.END, f"[{ts}] {row[0]} -> {row[1]} [{row[2]}]\n")
            self.txt_log.config(state='disabled')

        except Exception as e:
            print(f"Dashboard Update Error: {e}")

    def refresh_stats_graph(self):
        try:
            query = "SELECT src_ip, COUNT(*) as count FROM packet_logs GROUP BY src_ip ORDER BY count DESC LIMIT 5"
            self.gui_db.cursor.execute(query)
            df = pd.DataFrame(self.gui_db.cursor.fetchall(), columns=['ip', 'count'])
            self.ax_stats.clear()
            if not df.empty:
                self.ax_stats.bar(df['ip'], df['count'], color=COLOR_ACCENT)
                self.ax_stats.set_title("Top 5 Source IPs (Volume)", color="white")
                self.ax_stats.tick_params(axis='x', rotation=15)
            self.cvs_stats.draw()
        except: pass

    def refresh_logs_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        try:
            self.gui_db.cursor.execute("SELECT captured_at, src_ip, dst_ip, protocol, length FROM packet_logs ORDER BY id DESC LIMIT 100")
            for row in self.gui_db.cursor.fetchall(): self.tree.insert("", "end", values=row)
        except: pass

    # ==========================================
    # --- PDF REPORT GENERATION (FIXED) ---
    # ==========================================
    def export_pdf(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
            if not file_path: return

            # 1. GENERATE CHART
            self.gui_db.cursor.execute("SELECT src_ip, COUNT(*) as count FROM packet_logs GROUP BY src_ip ORDER BY count DESC LIMIT 5")
            df = pd.DataFrame(self.gui_db.cursor.fetchall(), columns=['ip', 'count'])
            
            temp_chart_path = "temp_chart_report.png"
            if not df.empty:
                plt.figure(figsize=(10, 5), facecolor='white')
                plt.bar(df['ip'], df['count'], color='#4a90e2')
                plt.title("Top 5 Threat Actors (Source IPs)")
                plt.xlabel("IP Address")
                plt.ylabel("Packet Count")
                plt.tight_layout()
                plt.savefig(temp_chart_path)
                plt.close()

            # 2. CREATE PDF WITH NEW SYNTAX
            pdf = PDFReport()
            pdf.add_page()
            
            # --- SUMMARY SECTION ---
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, "Executive Summary", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            self.gui_db.cursor.execute("SELECT COUNT(*), (SELECT COUNT(*) FROM packet_logs WHERE UPPER(TRIM(protocol))='TCP'), (SELECT COUNT(*) FROM packet_logs WHERE UPPER(TRIM(protocol))='UDP') FROM packet_logs")
            stats = self.gui_db.cursor.fetchone()
            
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(50, 10, f"Total Packets: {stats[0]}", border=1)
            pdf.cell(50, 10, f"TCP Packets: {stats[1]}", border=1)
            pdf.cell(50, 10, f"UDP Packets: {stats[2]}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(10)

            # --- CHART SECTION ---
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Traffic Analysis Chart", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            if os.path.exists(temp_chart_path):
                pdf.image(temp_chart_path, x=10, w=190)
                pdf.ln(5)
                os.remove(temp_chart_path)
            else:
                pdf.cell(0, 10, "(No data available for chart)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # --- TABLE SECTION ---
            pdf.ln(10)
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Recent Suspicious Activity (Last 50 Logs)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            
            # Table Header
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_fill_color(200, 200, 200)
            col_widths = [45, 40, 40, 25, 20] 
            headers = ["Timestamp", "Source IP", "Dest IP", "Proto", "Len"]
            
            for i, h in enumerate(headers):
                pdf.cell(col_widths[i], 10, h, border=1, align='C', fill=True)
            pdf.ln()

            # Table Rows
            self.gui_db.cursor.execute("SELECT captured_at, src_ip, dst_ip, protocol, length FROM packet_logs ORDER BY id DESC LIMIT 50")
            logs = self.gui_db.cursor.fetchall()
            
            pdf.set_font("Helvetica", "", 9)
            fill = False
            for row in logs:
                pdf.set_fill_color(240, 240, 240) if fill else pdf.set_fill_color(255, 255, 255)
                
                # Cells 1-4: Move RIGHT
                pdf.cell(col_widths[0], 8, str(row[0]), border=1, align='C', fill=True)
                pdf.cell(col_widths[1], 8, str(row[1]), border=1, align='C', fill=True)
                pdf.cell(col_widths[2], 8, str(row[2]), border=1, align='C', fill=True)
                pdf.cell(col_widths[3], 8, str(row[3]), border=1, align='C', fill=True)
                # Last Cell: Move NEXT LINE
                pdf.cell(col_widths[4], 8, str(row[4]), border=1, align='C', fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                fill = not fill

            pdf.output(file_path)
            messagebox.showinfo("Success", "Security Report Generated Successfully!")

        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def flush_db(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to delete ALL logs?"):
            self.gui_db.cursor.execute("DELETE FROM packet_logs")
            self.gui_db.connection.commit()
            self.refresh_logs_table()
            messagebox.showinfo("Done", "Database cleared.")

    def on_closing(self):
        if self.is_running: stop_sniffer_flag.set()
        if hasattr(self, 'gui_db'): self.gui_db.close()
        self.destroy()

if __name__ == "__main__":
    app = NetGuardApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
