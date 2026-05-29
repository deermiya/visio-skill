# Visio 模具速查表 (Stencil Catalog)

供 AI 生成 JSON spec 时参考。`master` 字段优先写 **NameU**（英文,跨语言稳定）,也支持 **Name**（中文显示名）。

## 快速示例

```json
{
  "stencils": [{ "id": "net", "file": "NETSYM_M.VSSX" }],
  "nodes": [{ "id": "r1", "stencil": "net", "master": "Router", "text": "核心路由", "x": 3, "y": 5 }]
}
```

## NETSYM_M.VSSX — 网络符号 (路由器/交换机/网桥等)

| Name (中文) | NameU (代码用) |
|---|---|
| 路由器 | Router |
| ATM 路由器 | ATM router |
| ISDN 交换机 | ISDN switch |
| ATM 交换机 | ATM switch |
| ATM/FastGB 以太网交换机 | ATM/FastGB etherswitch |
| 工作组交换机 | Workgroup switch |
| 小型集线器 | Small hub |
| 100BaseT 集线器 | 100BaseT hub |
| CDDI/FDDI 集中器 | CDDI/FDDI concentrator |
| 终端服务器 | Terminal server |
| 通信服务器 | Comm server |
| 探测器 | Probe |
| 网桥 | Bridge |
| 网关 | Gateway |
| WAN | WAN |
| DSU/CSU | DSU/CSU |
| 主机 | Host |
| 关系数据库 | Relational database |
| 锁 | Lock |
| 锁和密钥 | Lock and key |
| 密钥 | Key |
| 公钥/私钥服务器 | Public/private key server |
| 证书服务器 | Certificate server |

## SERVER_M.VSSX — 服务器 (Web/文件/邮件/数据库服务器等)

| Name (中文) | NameU (代码用) |
|---|---|
| 服务器 | Server |
| 文件服务器 | File server |
| 电子邮件服务器 | Email server |
| Web 服务器 | Web server |
| 代理服务器 | Proxy server |
| 实时通信服务器 | Real-time communications server |
| 电子商务服务器 | E-Commerce server |
| 数据库服务器 | Database server |
| 内容管理服务器 | Content management server |
| FTP 服务器 | FTP server |
| 流化媒体服务器 | Streaming media server |
| 管理服务器 | Management server |
| 目录服务器 | Directory server |
| 打印服务器 | Print server |
| 移动信息服务器 | Mobile information server |
| 应用程序服务器 | Application server |

## PERIPH_M.VSSX — 网络和外设 (PC/打印机/防火墙/手机等)

| Name (中文) | NameU (代码用) |
|---|---|
| 环形网络 | Ring network |
| 以太网 | Ethernet |
| 服务器 | Server |
| 大型机 | Mainframe |
| 路由器 | Router |
| 交换机 | Switch |
| 防火墙 | Firewall |
| 通信链路 | Comm-link |
| 超级计算机 | Super computer |
| 打印机 | Printer |
| 绘图仪 | Plotter |
| 扫描仪 | Scanner |
| 复印机 | Copier |
| 传真机 | Fax |
| 多功能设备 | Multi-function device |
| CRT 投影仪 | CRT projector |
| 屏幕 | Screen |
| 网桥 | Bridge |
| 集线器 | Hub |
| 调制解调器 | Modem |
| 电话机 | Telephone |
| 手机 | Cell phone |
| 智能手机 | Smart phone |
| 无线访问点 | Wireless access point |
| 数码相机 | Digital camera |
| 摄像机 | Video camera |
| 用户 | User |
| 图例 | Legend |

## COMPS_M.VSSX — 计算机和显示器 (PC/笔记本/平板等)

| Name (中文) | NameU (代码用) |
|---|---|
| PC | PC |
| 笔记本电脑 | Laptop computer |
| LCD 显示器 | LCD monitor |
| 终端 | Terminal |
| 平板电脑 | Tablet computer |
| PDA | PDA |
| iMac | iMac |
| 新式 iMac | New iMac |
| CRT 监视器 | CRT monitor |

## BASIC_M.VSSX — 基本形状 (矩形/圆/三角/星形等)

| Name (中文) | NameU (代码用) |
|---|---|
| 矩形 | Rectangle |
| 正方形 | Square |
| 圆形 | Circle |
| 椭圆形 | Ellipse |
| 直角三角形 | Right Triangle |
| 三角形 | Triangle |
| 旋转三角形 | Rotated Triangle |
| 五边形 | Pentagon |
| 六边形 | Hexagon |
| 七边形 | Heptagon |
| 八边形 | Octagon |
| 十边形 | Decagon |
| 圆柱形 | Can |
| 平行四边形 | Parallelogram |
| 梯形 | Trapezoid |
| 菱形 | Diamond |
| 十字形 | Cross |
| V 形 | Chevron |
| 立方体 | Cube |
| 水滴 | Drop |
| 半圆 | Semi Circle |
| 半圆 | Semi Ellipse |
| 圆锥 | Cone |
| 倒圆锥 | Inverted Cone |
| 棱锥 | Pyramid |
| 尖的椭圆形 | Pointed Oval |
| 漏斗 | Funnel |
| 齿轮 | Gear |
| 四角星 | 4-Point Star |
| 五角星 | 5-Point Star |
| 六角星 | 6-Point Star |
| 七角星 | 7-Point Star |
| 十六角星 | 16-Point Star |
| 二十四角星 | 24-Point Star |
| 三十二角星 | 32-Point Star |
| 圆角矩形 | Rounded Rectangle |
| 剪去单角的矩形 | Single Snip Corner Rectangle |
| 剪去同侧角的矩形 | Snip Same Side Corner Rectangle |
| 剪去对角的矩形 | Snip Diagonal Corner Rectangle |
| 单圆角矩形 | Single Round Corner Rectangle |
| 同侧圆角矩形 | Round Same Side Corner Rectangle |
| 对角圆角矩形 | Round Diagonal Corner Rectangle |
| 剪去单圆角矩形 | Snip and Round Single Corner Rectangle |
| 剪去角的矩形 | Snip Corner Rectangle |
| 圆角的矩形 | Round Corner Rectangle |
| 剪去角的和圆角矩形 | Snip and Round Corner Rectangle |
| 框架 | Frame |
| 框架角 | Frame Corner |
| L 形状 | L Shape |
| 斜纹 | Diagonal Stripe |
| 徽章 | Plaque |
| 环形 | Donut |
| 无符号 | No Symbol |
| 中心拖动圆形 | Center Drag Circle |
| 左圆括号 | Left Parenthesis |
| 右圆括号 | Right Parenthesis |
| 左括号 | Left Brace |
| 右括号 | Right Brace |

## BASFLO_M.VSSX — 基本流程图 (流程/判定/子流程/文档等)

| Name (中文) | NameU (代码用) |
|---|---|
| 流程 | Process |
| 判定 | Decision |
| 子流程 | Subprocess |
| 开始/结束 | Start/End |
| 文档 | Document |
| 数据 | Data |
| 数据库 | Database |
| 外部数据 | External Data |
| 自定义 1 | Custom 1 |
| 自定义 2 | Custom 2 |
| 自定义 3 | Custom 3 |
| 自定义 4 | Custom 4 |
| 页面内引用 | On-page reference |
| 跨页引用 | Off-page reference |

## FLOSHP_M.VSSX — 流程图形状 (高级流程/逻辑门/存储等)

| Name (中文) | NameU (代码用) |
|---|---|
| 分段流程 2 | Divided process 2 |
| 标记的流程 | Tagged process |
| 流程(圆形) | Process (circle) |
| 数据存储 3 | Data store 3 |
| 外部实体 1 | External entity 1 |
| 外部实体 2 | External entity 2 |
| 传输磁带 | Transmittal tape |
| 圆角流程 | Rounded process |
| 创建请求 | Create request |
| 带边框的矩形 | Bordered rectangle |
| 带框架的矩形 | Framed rectangle |
| 开放式矩形 | Open rectangle |
| 延迟 | Delay |
| 求和连接器 | Summing junction |
| 存储鼓 | Drum storage |
| OR | Or |
| 整理 | Collate |
| 提取 | Extract |
| 脱机存储 | Off-line storage |
| 合并 | Merge |
| 分类 2 | Sort 2 |
| 卡片叠 | Deck of cards |
| 卡片文件 | File of cards |
| 缩微胶片 | Microform |
| 缩微录制 | Microform recording |
| 缩微处理 | Microform processing |
| 复制 | Duplicating |
| 线条型/阴影型流程 | Lined/Shaded process |
| 标记的文档 | Tagged document |
| 线条型文档 | Lined document |
| 可变起点 | Variable start |
| 可变过程 | Variable procedure |
| 分类 | Sort |
| 数据存储 | Data store |
| 数据库 | Database |
| 来自调用控制的原语 | Primitive from call control |
| 到调用控制的原语 | Primitive to call control |
| 来自用户的消息 | Message from user |
| 到用户的消息 | Message to user |
| 输出 | Output |
| 反馈 | Feedback |
| 检查 | Check |
| 检查 2 | Check 2 |
| AND 门 | And gate |
| OR 门 | Or gate |
| 优化 | Refinement |
| 分支: 返回 | Branch: return |
| XOR(异或) | XOR (Exclusive Or) |
| 分支: 无返回 | Branch: no return |
| 垂直 XOR | Vertical XOR |
| 中断 | Interrupt |
| 垂直 P AND  | Vertical P And  |
| 外部控制 | External control |
| 省略号 | Ellipsis |
| 直线-曲线连接线 | Line-curve connector |

## DTLNET_M.VSSX — 详细网络图 (配线板/卫星/发射塔等)

| Name (中文) | NameU (代码用) |
|---|---|
| A/B 交换盒 | A/B switchbox |
| 生物特征读取器 | Biometric reader |
| 数据 | Data |
| 诊断设备 | Diagnostic device |
| 外部媒体驱动器 | External media drive |
| 外部硬盘 | External hard drive |
| 光纤信号发送器 | Fiber optic transmitter |
| 配线板 | Patch panel |
| PBX | PBX |
| 无线电发射塔 | Radio tower |
| 中继器 | Repeater |
| 卫星 | Satellite |
| 碟形卫星天线 | Satellite dish |
| 智能卡读卡器 | Smartcard reader |
| XML Web 服务 | XML Web Service |

## 其他模具分类索引

Visio 还自带 300+ 模具,以下按类别列出文件名(需要时声明在 `stencils` 中即可使用):

**AWS 云架构**: `AWSANALYTICS_M.VSSX``, ``AWSAPPINT_M.VSSX``, ``AWSARVR_M.VSSX``, ``AWSBLK_M.VSSX``, ``AWSBUSINESSAPP_M.VSSX``, ``AWSCOMPUTE_M.VSSX``, ``AWSCONTAINERS_M.VSSX``, ``AWSCOSTMGMT_M.VSSX``, ``AWSCUSTENB_M.VSSX``, ``AWSCUSTENG_M.VSSX``, ``AWSDB_M.VSSX``, ``AWSDEVTOOLS_M.VSSX``, ``AWSENDUSERCOMPUTE_M.VSSX``, ``AWSGAMETECH_M.VSSX``, ``AWSGEN_M.VSSX``, ``AWSIOT_M.VSSX``, ``AWSMEDIASERV_M.VSSX``, ``AWSMGMTGOV_M.VSSX``, ``AWSMIGRATIONTRANSFER_M.VSSX``, ``AWSML_M.VSSX``, ``AWSMOBILE_M.VSSX``, ``AWSNETCONTENTDELIVERY_M.VSSX``, ``AWSQUANTTECH_M.VSSX``, ``AWSROBOTICS_M.VSSX``, ``AWSSAT_M.VSSX``, ``AWSSECURITYCOMPLIANCE_M.VSSX``, ``AWSSTORAGE_M.VSSX`

**Azure 云架构**: `AZUREAIMACHINELEARNING_M.VSSX``, ``AZUREANALYTICS_M.VSSX``, ``AZUREAPPSERVICES_M.VSSX``, ``AZUREBLOCKCHAIN_M.VSSX``, ``AZURECLOUD_M.VSSX``, ``AZURECOMMAND_M.VSSX``, ``AZURECOMPUTE_M.VSSX``, ``AZURECONTAINERS_M.VSSX``, ``AZUREDATABASES_M.VSSX``, ``AZUREDEPRECATED_M.VSSX``, ``AZUREDEVOPS_M.VSSX``, ``AZUREDRAWING_M.VSSX``, ``AZUREECOSYSTEM_M.VSSX``, ``AZUREENTERPRISE_M.VSSX``, ``AZUREGENERALSYMBOLS_M.VSSX``, ``AZUREGENERAL_M.VSSX``, ``AZUREIDENTITY_M.VSSX``, ``AZUREINTEGRATION_M.VSSX``, ``AZUREINTUNE_M.VSSX``, ``AZUREIOT_M.VSSX``, ``AZUREMANAGEMENTGOVERNANCE_M.VSSX``, ``AZUREMENU1_M.VSSX``, ``AZUREMENU2_M.VSSX``, ``AZUREMENU3_M.VSSX``, ``AZUREMIGRATE_M.VSSX``, ``AZUREMIXEDREALITY_M.VSSX``, ``AZUREMONITOR_M.VSSX``, ``AZURENETWORKING_M.VSSX``, ``AZURENEWICONS_M.VSSX``, ``AZUREOMS_M.VSSX``, ``AZUREOPERATIONSMANAGER_M.VSSX``, ``AZUREOTHERMICROSOFTPRODUCTS_M.VSSX``, ``AZUREOTHER_M.VSSX``, ``AZUREPREVIEW_M.VSSX``, ``AZURESECURITY_M.VSSX``, ``AZURESTACK_M.VSSX``, ``AZURESTATUS_M.VSSX``, ``AZURESTORAGE_M.VSSX``, ``AZURESYSTEMCENTER_M.VSSX``, ``AZUREVMSBYFUNCTION_M.VSSX``, ``AZUREVMWARESOLUTION_M.VSSX``, ``AZUREWEB_M.VSSX`

**电气/电子**: `EECHIP_M.VSSX``, ``EECOMP_M.VSSX``, ``EEFUND_M.VSSX``, ``EEFUND_VISIO2013_M.VSSX``, ``EEMAIN_M.VSSX``, ``EEMAPS_M.VSSX``, ``EEMECH_M.VSSX``, ``EEPATH_M.VSSX``, ``EEPATH_VISIO2013_M.VSSX``, ``EEQUAL_M.VSSX``, ``EEQUAL_VISIO2013_M.VSSX``, ``EESEMI_M.VSSX``, ``EESEMI_VISIO2013_M.VSSX``, ``EESWCH_M.VSSX``, ``EESWCH_VISIO2013_M.VSSX``, ``EETCOM_M.VSSX``, ``EETERM_M.VSSX``, ``EETRAN_M.VSSX``, ``EEVHF_M.VSSX``, ``FREEQP_M.VSSX``, ``PEEQP_M.VSSX`

**UML**: `DBUML_M.VSSX``, ``OBJREL_M.VSSX``, ``UACTME_M.VSSX``, ``UCMNME_M.VSSX``, ``UCOMME_M.VSSX``, ``UDEPME_M.VSSX``, ``USEQME_M.VSSX``, ``USTAME_M.VSSX``, ``USTRME_M.VSSX``, ``UUSEME_M.VSSX`

**组织结构图**: `ORGBLT_M.VSSX``, ``ORGBND_M.VSSX``, ``ORGCH_M.VSSX``, ``ORGCNS_M.VSSX``, ``orgico_m.vssx``, ``ORGNCH_M.VSSX``, ``ORGPAN_M.VSSX``, ``ORGPER_M.VSSX``, ``ORGPET_M.VSSX``, ``ORGPIP_M.VSSX``, ``ORGSTO_M.VSSX``, ``ORGTAC_M.VSSX`

**流程/工作流**: `BPMN_M.VSSX``, ``DATFLO_M.VSSX``, ``DBIDEF1X_M.VSSX``, ``EPC_M.VSSX``, ``IDEF0_M.VSSX``, ``MSFLOW_M.VSSX``, ``SSFLOW_M.VSSX``, ``TQM_M.VSSX``, ``VSM_M.VSSX``, ``WRKFLO_M.VSSX`

**数据库**: `DBCHEN_M.VSSX``, ``DBCROW_M.VSSX`

**UI 控件/线框**: `MWFCONCTRL_M.VSSX``, ``MWFCTRL_M.VSSX``, ``MWFECTRL_M.VSSX``, ``MWFNAVCTRL_M.VSSX``, ``MWFTEXTCTRL_M.VSSX``, ``WFCICN_M.VSSX``, ``WFCRS_M.VSSX``, ``WFCTRL_M.VSSX``, ``WFDEME_M.VSSX``, ``WFDEP_M.VSSX``, ``WFDLGS_M.VSSX``, ``WFOBJ_M.VSSX``, ``WFOBME_M.VSSX``, ``WFSTEP_M.VSSX``, ``WFSTME_M.VSSX``, ``WFTLBR_M.VSSX``, ``WFWICN_M.VSSX``, ``WWFCICN_M.VSSX``, ``WWFCONCTRL_M.VSSX``, ``WWFCRS_M.VSSX``, ``WWFCTRL_M.VSSX``, ``WWFMECTRL_M.VSSX``, ``WWFNAVCTRL_M.VSSX``, ``WWFTEXTCTRL_M.VSSX``, ``WWFWICN_M.VSSX`

**办公/建筑**: `BLDCOR_M.VSSX``, ``BLDCOR_VISIO2013_M.VSSX``, ``CUBICL_M.VSSX``, ``CUBICL_VISIO2013_M.VSSX``, ``FURN_M.VSSX``, ``FURN_VISIO2013_M.VSSX``, ``HVACCE_M.VSSX``, ``HVACC_M.VSSX``, ``HVACD_M.VSSX``, ``HVACEQ_M.VSSX``, ``OFFACC_M.VSSX``, ``OFFACC_VISIO2013_M.VSSX``, ``OFFEQP_M.VSSX``, ``OFFEQP_VISIO2013_M.VSSX``, ``OFFFRN_M.VSSX``, ``OFFFRN_VISIO2013_M.VSSX``, ``PLUMB_M.VSSX``, ``WALL_M.VSSX`

**机架/设备**: `RCKEQP_M.VSSX``, ``RCKSME_M.VSSX``, ``RCKSVR_M.VSSX``, ``SERVME_M.VSSX`

**Cisco 网络**: `CISCONETWORKSHAPES_M.VSSX`

**Kubernetes**: `KUBERNETESVISIOSTENCIL_M.VSSX`

**SharePoint**: `SPORTS_M.VSSX``, ``SPRBR_M.VSSX``, ``SPWA2_M.VSSX``, ``SPWA_M.VSSX``, ``SPWC2_M.VSSX``, ``SPWC_M.VSSX``, ``SPWT2_M.VSSX``, ``SPWT_M.VSSX`

**Dynamics 365**: `DYNAMICS365ICONS_M.VSSX`

**Power Platform**: `POWERPLATFORMICONS_M.VSSX`

**Microsoft 产品**: `MICROSOFTPRODUCTS_M.VSSX`

**其他**: `ACCESSBILITY_NEW_M.VSSX``, ``ADO_M.VSSX``, ``ADS_M.VSSX``, ``ALARM_M.VSSX``, ``ANALYTICS_M.VSSX``, ``ANIMALS_M.VSSX``, ``ANNOT_M.VSSX``, ``APPAREL_M.VSSX``, ``APPL_M.VSSX``, ``APPL_VISIO2013_M.VSSX``, ``ARROWS2_M.VSSX``, ``ARROWS_M.VSSX``, ``ARTS_M.VSSX``, ``AUDIT_M.VSSX``, ``BASICORGCHART_M.VSSX``, ``BA_DEC_BAN_M.VSSX``, ``BA_DEC_M.VSSX``, ``BA_GRP_M.VSSX``, ``BCKGRN_M.VSSX``, ``BLOCK3_M.VSSX``, ``BLOCKP_M.VSSX``, ``BLOCK_M.VSSX``, ``BODYPARTS_M.VSSX``, ``BORDRS_M.VSSX``, ``BPRES_M.VSSX``, ``BSTORM_M.VSSX``, ``BTHKT_M.VSSX``, ``BTHKT_VISIO2013_M.VSSX``, ``BUGS_M.VSSX``, ``BUILDINGS_M.VSSX``, ``BUSINESS_FRAMEWORKS_M.VSSX``, ``BUSINESS_M.VSSX``, ``CABNT_M.VSSX``, ``CABNT_VISIO2013_M.VSSX``, ``CALNDR_M.VSSX``, ``CALOUT_M.VSSX``, ``CAUSEF_M.VSSX``, ``CELEBRATION_M.VSSX``, ``CHART_M.VSSX``, ``COMMERCE_M.VSSX``, ``COMMUNICATION_M.VSSX``, ``COMOLE_M.VSSX``, ``COMPLN_M.VSSX``, ``COMPME_M.VSSX``, ``CONNEC_M.VSSX``, ``CYCLEDIAG_M.VSSX``, ``DATAVISUALIZERPREVIEW_M.VSSX``, ``DATAVISUALIZER_M.VSSX``, ``DGICON_M.VSSX``, ``DIMENG_M.VSSX``, ``DRAWTL_M.VSSX``, ``DRILLD_M.VSSX``, ``DTLNME_M.VSSX``, ``DVCALL_M.VSSX``, ``EDUCATION_M.VSSX``, ``ELETEL_M.VSSX``, ``EMBELL_M.VSSX``, ``ENTAPP_M.VSSX``, ``ENTITY_M.VSSX``, ``EVIDENCE_M.VSSX``, ``EXCOBJ_M.VSSX``, ``FACES_M.VSSX``, ``FASTN1_M.VSSX``, ``FASTN2_M.VSSX``, ``FAULT_M.VSSX``, ``FOODDRINKS_M.VSSX``, ``FPASSM_M.VSSX``, ``FPEQP_M.VSSX``, ``FPVALV_M.VSSX``, ``GANESA_M.VSSX``, ``GANTT_M.VSSX``, ``GARDEN_M.VSSX``, ``GARDEN_VISIO2013_M.VSSX``, ``GDT_M.VSSX``, ``GENERAL_M.VSSX``, ``HOLIDAYS_M.VSSX``, ``HOME_M.VSSX``, ``INDOOR_M.VSSX``, ``INTANN_M.VSSX``, ``INTERFACE_M.VSSX``, ``IRRIG_M.VSSX``, ``ITIL_M.VSSX``, ``LANDSCAPE_M.VSSX``, ``LANGLV_M.VSSX``, ``LDAPOB_M.VSSX``, ``LEGEND_M.VSSX``, ``LGND_M.VSSX``, ``LINPAT_M.VSSX``, ``LNDMRK_M.VSSX``, ``LOCATION_M.VSSX``, ``LOGIC_M.VSSX``, ``MAP3D_M.VSSX``, ``MATRIXDIAGRAMSHAPES_M.VSSX``, ``MATRIXDOT_M.VSSX``, ``MATRIXSTICKYNOTES_M.VSSX``, ``MEDICAL_M.VSSX``, ``MEMOBJ_M.VSSX``, ``METRO_M.VSSX``, ``MRKTDG_M.VSSX``, ``NATUREOUTDOORS_M.VSSX``, ``NETLME_M.VSSX``, ``NETLOC_M.VSSX``, ``NETRM_M.VSSX``, ``NETSME_M.VSSX``, ``OUTDOOR_M.VSSX``, ``PEANNT_M.VSSX``, ``PEHEAT_M.VSSX``, ``PEINST_M.VSSX``, ``PEOPLE_M.VSSX``, ``PEPIPE_M.VSSX``, ``PEPUMP_M.VSSX``, ``PERIME_M.VSSX``, ``PERT_M.VSSX``, ``PEVALV_M.VSSX``, ``PEVESS_M.VSSX``, ``pictogram_m.vssx``, ``PIPE1_M.VSSX``, ``PIPE2_M.VSSX``, ``PLANT_M.VSSX``, ``PLANT_VISIO2013_M.VSSX``, ``PRKRD_M.VSSX``, ``PRKRD_VISIO2013_M.VSSX``, ``PROCESS_M.VSSX``, ``PROCESS_NEW_M.VSSX``, ``PTSCLD_M.VSSX``, ``PTSINT_M.VSSX``, ``PTSINT_VISIO2013_M.VSSX``, ``PTUSCL_M.VSSX``, ``PUZZLESANDGAMES_M.VSSX``, ``PYRAMID_SHAPES_M.VSSX``, ``RECRT_M.VSSX``, ``RECRT_VISIO2013_M.VSSX``, ``RECSHP_M.VSSX``, ``REGSTR_M.VSSX``, ``ROAD_M.VSSX``, ``SDCALL_M.VSSX``, ``SDCONT_M.VSSX``, ``SDL_M.VSSX``, ``SECURITYJUSTICE_M.VSSX``, ``SHPMCH_M.VSSX``, ``SHPREC_M.VSSX``, ``SHPSTR_M.VSSX``, ``SIGNS_M.VSSX``, ``SITACC_M.VSSX``, ``SITACC_VISIO2013_M.VSSX``, ``SSHOQ_M.VSSX``, ``statistical_infographic_m.vssx``, ``step_infographic_shapes_m.vssx``, ``SYMBOL_M.VSSX``, ``TECHELEC_M.VSSX``, ``Theme_m.vssx``, ``timelinetodolist_m.vssx``, ``TIMELN_M.VSSX``, ``TITLE_M.VSSX``, ``TOOLSBUILDING_M.VSSX``, ``TRANSP_M.VSSX``, ``VALVE1_M.VSSX``, ``VALVE2_M.VSSX``, ``VEHICLES_M.VSSX``, ``VEHICL_M.VSSX``, ``VEHICL_VISIO2013_M.VSSX``, ``VENNDIAG_M.VSSX``, ``VIDSUR_M.VSSX``, ``WADOWI_M.VSSX``, ``WEATHERSEASONS_M.VSSX``, ``WEBMAP_M.VSSX``, ``WEBSIT_M.VSSX``, ``WELD_M.VSSX``, ``XFUNC_M.VSSX``, ``YOURDON_COAD_NOTATION_M.VSSX`

