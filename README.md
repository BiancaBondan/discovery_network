# Network Automation Inventory

🚫 **Private script – not publicly available**

📧 Contact: bondansvbianca@gmail.com

This repository is related to the **Discovers project**, which automates network discovery by collecting:

- Active IP addresses
- Connection types
- Open ports
- Vendor identification

It generates a **.txt file** with the data collected from each IP address.

---

## 🧰 Libraries used

```python
# -*- coding: utf-8 -*-
import ipaddress
import socket
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
