# Visio Stencil Reference

This document lists commonly available Visio stencil files and their master shapes.

## How to Find Stencil Files

Visio stencil files (`.vssx` or `.vss`) are typically located at:
- **Chinese (Simplified)**: `C:\Program Files\Microsoft Office\root\Office16\Visio Content\2052\`
- **English (US)**: `C:\Program Files\Microsoft Office\root\Office16\Visio Content\1033\`

## Common Stencil Categories

### Network & Infrastructure

#### NETSYM_M.VSSX - Network Symbols [BANNED]
> [!WARNING]
> DO NOT USE. Causes headless COM automation to hang due to `EventDrop` modal popups. Use styled basic shapes instead.
Basic network devices and components (DO NOT USE):
- `路由器` / `Router`
- `ATM 路由器` / `ATM Router`
- `ISDN 交换机` / `ISDN Switch`
- `ATM 交换机` / `ATM Switch`
- `工作组交换机` / `Workgroup Switch`
- `小型集线器` / `Mini Hub`
- `100BaseT 集线器` / `100BaseT Hub`
- `网桥` / `Bridge`
- `网关` / `Gateway`
- `主机` / `Host`
- `WAN`
- `DSU/CSU`
- `防火墙` / `Firewall`
- `调制解调器` / `Modem`

#### CISCONETWORKSHAPES_M.VSSX - Cisco Network Devices [BANNED]
> [!WARNING]
> DO NOT USE. Causes headless COM automation to hang due to `EventDrop` modal popups. Use styled basic shapes instead.
Professional Cisco-branded network equipment icons (DO NOT USE)

#### SERVER_M.VSSX - Servers and Racks [BANNED]
> [!WARNING]
> DO NOT USE. Causes headless COM automation to hang due to `EventDrop` modal popups. Use styled basic shapes instead.
- `服务器` / `Server`
- `Web 服务器` / `Web Server`
- `数据库服务器` / `Database Server`
- `文件服务器` / `File Server`
- `机架` / `Rack`

#### COMPS_M.VSSX - Computers and Monitors [BANNED]
> [!WARNING]
> DO NOT USE. Causes headless COM automation to hang due to `EventDrop` modal popups. Use styled basic shapes instead.
- `PC`
- `工作站` / `Workstation`
- `笔记本电脑` / `Laptop`
- `显示器` / `Monitor`
- `打印机` / `Printer`

### Cloud Services

#### AZURECLOUD_M.VSSX - Azure Cloud Services
Azure cloud service icons

#### AZURECOMPUTE_M.VSSX - Azure Compute
Azure virtual machines and compute resources

#### AZURENETWORKING_M.VSSX - Azure Networking
Azure networking components

#### AZUREDATABASES_M.VSSX - Azure Databases
Azure database services

#### AZURESTORAGE_M.VSSX - Azure Storage
Azure storage services

#### AWSCOMPUTE_M.VSSX - AWS Compute
AWS EC2 and compute services

#### AWSSTORAGE_M.VSSX - AWS Storage
AWS S3 and storage services

#### AWSNETCONTENTDELIVERY_M.VSSX - AWS Networking
AWS networking and content delivery

### Container & Orchestration

#### KUBERNETESVISIOSTENCIL_M.VSSX - Kubernetes
Kubernetes components and icons

### Other Useful Stencils

#### ARROWS_M.VSSX - Arrows and Connectors
Various arrow shapes and directional indicators

#### ANNOT_M.VSSX - Annotations
Callouts, notes, and annotation shapes

#### ANALYTICS_M.VSSX - Analytics
Data analytics and visualization shapes

## How to Discover Master Names

To list all masters in a stencil file, use PowerShell:

```powershell
$visio = New-Object -ComObject Visio.Application
$visio.Visible = $false
$stencil = $visio.Documents.OpenEx("C:\Path\To\Stencil.vssx", 64)
$stencil.Masters | ForEach-Object { $_.Name }
$stencil.Close()
$visio.Quit()
```

## Language Considerations

- Stencil files in the `2052` folder contain Chinese master names
- Stencil files in the `1033` folder contain English master names
- Use the exact master name as it appears in the stencil
- Master names are case-sensitive

## Tips for Using Stencils

1. **Exact Names**: Master names must match exactly as they appear in the stencil
2. **Language Consistency**: Use Chinese names for Chinese stencils, English for English stencils
3. **Fallback to Basic Shapes**: If a stencil or master isn't found, the script will fail - always verify names first
4. **Mixed Usage**: You can mix stencil masters and basic shapes in the same diagram
5. **Custom Stencils**: You can use your own custom `.vssx` files by providing the full path

## Example Usage

```json
{
  "stencils": [
    { "id": "network", "file": "NETSYM_M.VSSX" },
    { "id": "server", "file": "SERVER_M.VSSX" },
    { "id": "aws", "file": "AWSCOMPUTE_M.VSSX" }
  ],
  "nodes": [
    {
      "id": "router1",
      "stencil": "network",
      "master": "路由器",
      "text": "Core Router",
      "x": 2,
      "y": 5
    }
  ]
}
```
