# Visio Stencil Reference

This document lists commonly available Visio stencil files and their master shapes.
**Master names are from live COM enumeration and verified accurate.**

## Stencil File Locations

Visio stencil files (`.vssx`) are typically at:
- **Chinese (Simplified)**: `C:\Program Files\Microsoft Office\root\Office16\Visio Content\2052\`
- **English (US)**: `C:\Program Files\Microsoft Office\root\Office16\Visio Content\1033\`

## Network & Infrastructure

### NETSYM_M.VSSX — Network Symbols (24 masters)

| # | Master Name | Description |
|---|-------------|-------------|
| 1 | 路由器 | Router |
| 2 | ATM 路由器 | ATM Router |
| 3 | ISDN 交换机 | ISDN Switch |
| 4 | ATM 交换机 | ATM Switch |
| 5 | ATM/FastGB 以太网交换机 | ATM/FastGB Ethernet Switch |
| 6 | 工作组交换机 | Workgroup Switch |
| 7 | 小型集线器 | Mini Hub |
| 8 | 100BaseT 集线器 | 100BaseT Hub |
| 9 | CDDI/FDDI 集中器 | CDDI/FDDI Concentrator |
| 10 | 终端服务器 | Terminal Server |
| 11 | 通信服务器 | Communication Server |
| 12 | 探测器 | Probe |
| 13 | 网桥 | Bridge |
| 14 | 网关 | Gateway |
| 15 | WAN | WAN |
| 16 | DSU/CSU | DSU/CSU |
| 17 | 主机 | Host |
| 18 | 关系数据库 | Relational Database |
| 19 | 锁 | Lock |
| 20 | 锁和密钥 | Lock and Key |
| 21 | 密钥 | Key |
| 22 | 公钥/私钥服务器 | Public/Private Key Server |
| 23 | 证书服务器 | Certificate Server |
| 24 | 动态连接线 | Dynamic Connector |

### SERVER_M.VSSX — Servers (17 masters)

| # | Master Name | Description |
|---|-------------|-------------|
| 1 | 服务器 | Server |
| 2 | 文件服务器 | File Server |
| 3 | 电子邮件服务器 | Email Server |
| 4 | Web 服务器 | Web Server |
| 5 | 代理服务器 | Proxy Server |
| 6 | 实时通信服务器 | Real-time Communication Server |
| 7 | 电子商务服务器 | E-commerce Server |
| 8 | 数据库服务器 | Database Server |
| 9 | 内容管理服务器 | Content Management Server |
| 10 | FTP 服务器 | FTP Server |
| 11 | 流化媒体服务器 | Streaming Media Server |
| 12 | 管理服务器 | Management Server |
| 13 | 目录服务器 | Directory Server |
| 14 | 打印服务器 | Print Server |
| 15 | 移动信息服务器 | Mobile Info Server |
| 16 | 应用程序服务器 | Application Server |
| 17 | 动态连接线 | Dynamic Connector |

### COMPS_M.VSSX — Computers and Monitors (10 masters)

| # | Master Name | Description |
|---|-------------|-------------|
| 1 | PC | PC |
| 2 | 笔记本电脑 | Laptop |
| 3 | LCD 显示器 | LCD Monitor |
| 4 | 终端 | Terminal |
| 5 | 平板电脑 | Tablet |
| 6 | PDA | PDA |
| 7 | iMac | iMac |
| 8 | 新式 iMac | Modern iMac |
| 9 | CRT 监视器 | CRT Monitor |
| 10 | 动态连接线 | Dynamic Connector |

## Cloud Services (未逐一验证，使用前建议用发现脚本确认)

- `AZURECLOUD_M.VSSX` — Azure Cloud Services
- `AZURECOMPUTE_M.VSSX` — Azure Compute
- `AZURENETWORKING_M.VSSX` — Azure Networking
- `AZUREDATABASES_M.VSSX` — Azure Databases
- `AZURESTORAGE_M.VSSX` — Azure Storage
- `AWSCOMPUTE_M.VSSX` — AWS Compute
- `AWSSTORAGE_M.VSSX` — AWS Storage
- `AWSNETCONTENTDELIVERY_M.VSSX` — AWS Networking
- `KUBERNETESVISIOSTENCIL_M.VSSX` — Kubernetes

## How to Discover Master Names

Use Python to list all masters in any stencil file:

```python
import win32com.client

visio = win32com.client.Dispatch("Visio.Application")
visio.Visible = False
s = visio.Documents.OpenEx(r"C:\Path\To\Stencil.vssx", 64)
for i in range(1, s.Masters.Count + 1):
    print(f"{i}: {s.Masters.Item(i).Name}")
visio.Quit()
```

## Important Notes

1. **Master names must be exact** — case-sensitive, including spaces (e.g., `Web 服务器` not `Web服务器`)
2. **Use Chinese names for `2052` stencils**, English names for `1033` stencils
3. **`动态连接线` exists in every stencil** — ignore it, use `ConnectorToolDataObject` for connections instead
4. **No "防火墙" master** — NETSYM_M does not contain a firewall shape; use `网关` as the closest alternative
5. **No "打印机" in COMPS_M** — use `打印服务器` from SERVER_M instead
6. **Mixed usage works** — stencil masters and basic shapes (`rectangle`, `roundrect`, `ellipse`, `diamond`) can coexist in one diagram
