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
1. The Dashboard (Live Monitoring)
Visualizes live traffic volume and protocol distribution.

2. PDF Report Output
Example of the auto-generated Executive Security Report.

---

## 🤝 Contributing
Contributions are welcome!
Bug Reports: Please attach the error log from the console.
Feature Requests: Open an issue to discuss new metrics or graphs.

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


### **🚨 Disclaimer**: This tool is intended for _**educational purposes**_ and _**network analysis**_ on authorized networks only. The _**developer**_ is _**not responsible**_ for _**any misuse or illegal activities**_ performed _**using**_ this _**software**_.
