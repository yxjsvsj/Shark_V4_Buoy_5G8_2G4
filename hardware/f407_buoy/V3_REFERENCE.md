# Shark_V3_SingleMCU_RevA

微型鲨鱼潜水艇专用 PCB —— 单颗 STM32F407VET6 控制三推进器、摄像头图传与无线遥控。

## 项目概况

- MCU：STM32F407VET6（LQFP-100）
- 时钟：24MHz HSE，SYSCLK 168MHz，USB 48MHz，MCO2 24MHz 供 OV2640
- 摄像头：OV2640，24-pin 0.5mm FPC
- 无线：2× 2.4GHz SPI 模块（原版 AS01-ML01S；当前工程放置 E01C-ML01S）
- 电源：1S 锂电池 → 3.3V 升降压；摄像头 2.8V / 1.3V LDO
- 电机：3× MX113H（电机电压/堵转电流尚未确定，驱动尚未设计）

## 当前设计状态

| 图页 | 状态 |
|---|---|
| 01_POWER | 1S 保护、TPS63802 3.3V、RF 滤波、电池测压已绘制 |
| 02_STM32 | STM32F407 最小系统、24MHz 晶振、去耦、VCAP、SWD 已绘制 |
| 03_CAMERA_RF | 器件已放置；**尚未布线** |
| 04_MOTOR_SERVO | 未设计 |
| 05_SENSORS_DEBUG | 未设计 |

## 关键设计决定

- 24MHz HSE，PLLM=24、PLLN=336、PLLP=2、PLLQ=7；PLLI2S 不使用。
- OV2640 XVCLK 由 PC9 / RCC_MCO2 提供 24MHz。
- 1S 电池保护：DW01A（YONGYUTAI，C2927799）+ FS8205A（FORTUNE，C16052）。
  - DW01A 第 4 脚按 YONGYUTAI 数据手册为 **NC**，保持悬空。
- 主 3.3V：TPS63802DLAR（TI，C2845237），0.47µH / 9.5A 电感，2×22µF 输出。
- 原版 U12 MIC5219-3.3 及其 5V 供电结构已取消；RF 由 3.3V 经磁珠滤波后，经 Q1/Q2 P-MOSFET 开关供电。
  - Q1/Q2 统一为 AO3401A（TECH PUBLIC，C5122001），SOT-23-3；1=G、2=S、3=D。
  - 设计意图：源极接 `+3V3_NRF`，栅极由 R9/R12 10k 上拉；PD14/PD4 低电平开通，高阻默认关断。
- 摄像头电源：U2 LN6206P282MR-G（2.8V）、U4 LN6206P132MR-G（1.3V）、U6 磁珠供 DOVDD。
- RF 模块：当前放置 E01C-ML01S（EBYTE，C970278），引脚顺序与 AS01-ML01S 相同，但封装/芯片/高速图传固件兼容性尚未验证。

## 本轮复核记录

- 已删除 02_STM32 中误放的未连接重复位号 `C53`、`FB2`、`FB3`、`FB4`；正式器件仅保留在 03_CAMERA_RF。全工程位号冲突为 0（U1 为同一 STM32 的多 Part，不计冲突）。
- 已清理 01_POWER / 02_STM32 中同一导线上的重复 `NET` 属性，共删除 121 条冗余记录；DRC `ONENETNAME` 由 111 降为 0。不同导线上的同名网络标签（如各去耦电容的 `+3V3`、`GND`）属于正常全局连接，未删除。
- U4 选用 LN6206P132MR-G（LCSC C236394）。按 Natlinear 订购型号规则 `①=1、②=3`，实际输出为 **1.3V**；LCSC/JLCPCB 页面元数据误标为 3.3V，BOM/采购时以厂家型号为准，禁止按页面标题改成 3.3V。
- Q1/Q2 已由空属性器件替换为 AO3401A（C5122001），封装、焊盘和引脚映射已核对。

## 文件结构

```text
Shark_V3_SingleMCU_RevA.eprj3        # 嘉立创EDA专业版工程
sch/Schematic2/                       # 五个正式原理图页
  01_POWER.esch2
  02_STM32.esch2
  03_CAMERA_RF.esch2
  04_MOTOR_SERVO.esch2
  05_SENSORS_DEBUG.esch2
pcb/                                  # PCB 文档（未布局）
panel/                                # 面板文档
docs/                                 # 导出的原理图 PNG
```

## 原理图预览

- [01_POWER](docs/01_POWER.png)
- [02_STM32](docs/02_STM32.png)
- [03_CAMERA_RF](docs/03_CAMERA_RF.png)

## 已知问题 / 待完成

- 03_CAMERA_RF 尚未完成摄像头、SCCB、DVP、RF SPI/CSN/CE/IRQ/EN 及电源布线。
- C32、Q1/Q2、FB2/FB3/FB4 的正式连接仍待完成；Q1/Q2 目前只有设计意图，尚未形成网络。
- DRC 当前为 0 error、7 warning，均为 `CHECKFLOATPIN` 悬空引脚；未发现不同网络短路。`ONENETNAME` 已清零。
- U4 的 LCSC/JLCPCB 页面把 LN6206P132MR-G 标为 3.3V，与厂家型号规则不符；已按 1.3V 设计，采购/贴片前需人工确认。
- `VBAT_SENSE` 尚未分配到具体 STM32 ADC 引脚。
- 三颗 MX113H 的电压/堵转电流未确定；`VBAT_MOTOR` 未设计，FS8205A 电机电流能力待验证。
- E01C-ML01S 的高速 JPEG 图传与遥控配对兼容性未经实测。
- 摄像头 U3/U5/U6 磁珠原图未给型号；当前选用 Murata BLM18PG600SN1D 作为工程等效件。
- 未开始 PCB 布局，未生成 Gerber 或生产文件。

## 打开方式

使用嘉立创EDA专业版 V4.1.78 打开 `Shark_V3_SingleMCU_RevA.eprj3`。

## 说明

本仓库是设计过程快照，不代表已完成或已验证的硬件。上电、打样前请完成电源、保护、时钟、射频和机械接口的完整评审。
