# 微控制器（MCU）芯片管脚速查与官网示例

基于官方数据手册 / 用户手册与官网库函数例程制作的交互式管脚可视化网页（单文件 HTML，可离线打开，也可经 GitHub Pages 在线访问）。

## 芯片速查页

| 芯片 | 封装 | 内核 / 主频 | 说明 | 在线访问 |
| --- | --- | --- | --- | --- |
| [HC32L130](./HC32L130/) | LQFP-48 | Cortex-M0+ / 48MHz | 华大低功耗主控，48 引脚交互图 + 项目示例 | https://yuzhouzhiwang.github.io/mcu/HC32L130/ |
| [MM32L0020](./MM32L0020/) | TSSOP20 / QFN20 | Cortex-M0+ / 48MHz | 灵动低功耗 MCU，双封装切换 + 官网例程 | https://yuzhouzhiwang.github.io/mcu/MM32L0020/ |
| [HC32F005](./HC32F005/) | QFN20 / TSSOP20 / SOP20 / QFN24 | Cortex-M0+ / 32MHz | 华大通用 MCU，双封装切换 + 官网 DDL 例程 | https://yuzhouzhiwang.github.io/mcu/HC32F005/ |

## 各页内容

- **管脚总览**：自绘 SVG 交互式引脚图，悬停 / 点击查看引脚名、封装编号与全部复用功能
- **功能速查表**：全部引脚的复用功能（AF / 数字复用）、模拟功能（ADC / VC / LVD）与封装编号
- **外设资源**：片上外设及其可用引脚映射
- **官网示例**：官网库函数 / DDL 例程源码节选（点灯、串口、ADC、PWM 等）
- **例程清单**：官网 SDK 全部例程目录
- **存储映射**：Flash / SRAM / 外设寄存器地址分配

## 数据来源

- HC32L130：DS_HC32L13x 数据手册 / RM_HC32L13x 参考手册（华大）
- MM32L0020：DS_MM32L0020 数据手册 + LibSamples_MM32L0020 官网库函数与例程（灵动）
- HC32F005：RM_HC32F003_005 用户手册 + HC32F003/005 DDL 设备驱动库（华大）
