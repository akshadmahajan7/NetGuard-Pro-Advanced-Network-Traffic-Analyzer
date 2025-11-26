# 🛡️ NetGuard Pro: Advanced Network Traffic Analyzer

---

## 🌟 Project Overview
NetGuard Pro is a sophisticated, real-time cybersecurity dashboard designed to monitor network traffic, detect anomalies, and generate professional audit reports. Unlike basic packet sniffers, NetGuard Pro utilizes a multi-threaded architecture where packet capture (Scapy) runs asynchronously from the visualization layer (Tkinter). This ensures a lag-free experience with live moving graphs, persistent logging to MySQL, and instant PDF report generation.

---

## 🚀 Key Features

### 📊 Live Dashboard
* Real-Time KPIs: Monitors Total Packets, TCP vs UDP traffic counts instantly.
* Moving Traffic Graph: Visualizes network volume over a rolling 10-second window.
* Protocol Distribution: Live Donut chart showing protocol shares.
* Live Stream: Scrolling terminal view of the latest 5 packets.

### 📉 Deep Analysis
* Top Threat Actors: Bar charts identifying the Source IPs generating the most traffic.
* Statistical Breakdown: Historical data analysis via Matplotlib integration.

### 🛡️ Security Logs
* Persistent Storage: All packet headers are saved to a local MySQL database.
* Audit Table: A searchable, scrollable Treeview of historical logs.

### 📑 Reporting & Export
* PDF Generation: One-click generation of "**Executive Security Reports**" containing:
  * Traffic analysis charts.
  * Executive summary of protocol usage.
  * Recent suspicious activity logs.
* CSV Export: Raw data export for external analysis.

---

## 🛠️ Technology Stack
| Component | Technology | Description | 
| --- | --- | --- |
| Core Logic | Python 3| Main application controller.
| Sniffer| Scapy | Raw socket packet capture & parsing. | 
| Database| MySQL | High-performance storage for logs.
| GUI | Tkinter & ttkbootstrap | Modern "Superhero" Dark Theme UI. | 
| Visualization | Matplotlib | Real-time graphs and report charting.
| Reporting | FPDF2 | Programmatic PDF report generation. | 

---

## 📁 Project Structure
```
NetGuard-Pro/
├── src/
│   ├── __init__.py
│   ├── database.py         # MySQL Connection Manager (Thread-Safe)
│   └── backend_sniffer.py  # Background Thread for Packet Capture
├── .env                    # Database Credentials (HIDDEN)
├── main_gui.py             # Main Dashboard Application
├── requirements.txt        # Dependencies
└── README.md               # Documentation
```

---

## ⚙️ Installation & Setup
1. Prerequisites
  * Python 3.8+
  * MySQL Server (must be running locally).
  * Npcap (Windows only): Download from [npcap.com](npcap.com). Ensure you check "_Install in WinPcap API-compatible Mode_".

2. Install Dependencies
```bash
pip install scapy mysql-connector-python python-dotenv matplotlib pandas ttkbootstrap fpdf2
```

3. Database Configuration
  * Open your MySQL Workbench or CLI.
  * Run the following commands to set up the user and database:
  ```SQL
  CREATE DATABASE netguard_db;
  USE netguard_db;

  -- Create a dedicated user for security
  CREATE USER 'sniffer_bot'@'localhost' IDENTIFIED BY 'secure_password123';
  GRANT ALL PRIVILEGES ON netguard_db.* TO 'sniffer_bot'@'localhost';
  FLUSH PRIVILEGES;
```
  * Create a .env file in the project root:
  ```Code snippet
  DB_HOST=localhost
  DB_USER=sniffer_bot
  DB_PASS=secure_password123
  DB_NAME=netguard_db
  ```

---

## 🖥️ Usage
⚠️ Important: Network sniffing requires Administrator/Root privileges to access the Network Interface Card (NIC).

**Windows**
Run Command Prompt or PowerShell as Administrator:
```DOS
python main_gui.py
```
Linux / Mac
```bash
sudo python3 main_gui.py
```

---

## 📸 Screenshots

### **The Dashboard (Live Monitoring)**

**1. MySQL Database.**
<img width="1918" height="1020" alt="MySQL" src="https://github.com/user-attachments/assets/3e9a96cf-92a7-4160-9b8f-d468ec48b5e8" />


**2. Packet Sender(Used to test the network analyzer tool ).**
  <img width="1918" height="1025" alt="Packet Sender" src="https://github.com/user-attachments/assets/a3a9da5c-dd3c-4bc0-9a97-77de7de0d8ea" />

**3. GUI**
 
 _a. Before Starting Monitoring._
    <img width="1917" height="1012" alt="gui_1" src="https://github.com/user-attachments/assets/14554f6d-b224-4cb1-a70c-b8f248ae3bc8" />
    
 
 _b. After Starting Monitoring._
    <img width="1918" height="1005" alt="gui_2" src="https://github.com/user-attachments/assets/77f64e3a-ed9e-423e-8259-52253e51ba79" />
    
 
 _c. Statistics Of Network Traffic._
    <img width="1918" height="1017" alt="gui_3" src="https://github.com/user-attachments/assets/0c28f2ef-0d55-4d8e-b960-35cd6e8c528f" />
    
 
 _d. Data MAnagememnt Option._
    <img width="1918" height="1015" alt="gui_4" src="https://github.com/user-attachments/assets/a8b7c81c-63c0-4581-bfe8-6742c2afdbfd" />
    
 
 _e. Showing Dialog box for confirmation of logs deletion._
    <img width="1918" height="1020" alt="gui_5" src="https://github.com/user-attachments/assets/0a0bcadd-6816-46d8-9163-8dff8b531a9b" />
    
 
 _f. Saving the Report Location Dialog box._
    <img width="1918" height="1017" alt="gui_6" src="https://github.com/user-attachments/assets/6df9118c-6553-4a85-88d8-7e9f3fa3306e" />

 
 _g. Report Generated Successfully._
    <img width="1918" height="1017" alt="gui_7" src="https://github.com/user-attachments/assets/5d642372-2ce0-4c38-a5f6-2b5e02aeb7fe" />

**4. Testing**

  _a. Graph, TCP, UDP and Total Packets count is seen on dashboard after using packet sender to send TCP, UDP packets._
    <img width="1918" height="1022" alt="test-2" src="https://github.com/user-attachments/assets/052a1a20-fa3e-49c7-a52d-9c585d217536" />

    
 _b. Logs can be seen under Security Logs with complete detais._
    <img width="1918" height="1022" alt="test-1" src="https://github.com/user-attachments/assets/f5932fec-9a3d-4b70-b35a-f392e85676b9" />



### **PDF Report Output**

Example of the auto-generated Executive Security Report.
<img width="750" height="1067" alt="report_1" src="https://github.com/user-attachments/assets/349df471-ebfa-4094-9bc0-8b23fb58f53b" />

<img width="606" height="860" alt="report_2" src="https://github.com/user-attachments/assets/a664abbb-ad9a-4914-aa43-1387ee81955e" />

<img width="607" height="857" alt="report_3" src="https://github.com/user-attachments/assets/5befe146-e194-49cf-8892-d141cdf36aa9" />

---

## 🤝 Contributing
Contributions are welcome!
* Bug Reports: Please attach the error log from the console.
* Feature Requests: Open an issue to discuss new metrics or graphs.

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


### **🚨 Disclaimer**: 
This tool is intended for _**educational purposes**_ and _**network analysis**_ on authorized networks only. The _**developer**_ is _**not responsible**_ for _**any misuse or illegal activities**_ performed _**using**_ this _**software**_.
