

## 仓位管理基本原则

### 1. 风险第一原则

**单笔投资风险限制**：
- 保守型：单笔风险不超过总资金的1%
- 平衡型：单笔风险不超过总资金的2%
- 进取型：单笔风险不超过总资金的3%

**风险定义**：
$
Risk = Position\ Size \times Stop\ Loss\ Percentage
$

**示例**：
- 总资金：100万
- 风险容忍：2%（2万）
- 止损：10%
- 最大仓位：2万 / 10% = 20万（20%仓位）

### 2. 分散化原则

**不要把所有鸡蛋放在一个篮子里**：
- 单一股票：不超过10-15%
- 单一行业：不超过25-30%
- 单一资产类别：不超过60-70%

### 3. 金字塔原则

**高确定性 = 大仓位，低确定性 = 小仓位**：
- 核心持仓（高确定性）：30-40%
- 卫星持仓（中等确定性）：40-50%
- 机会持仓（低确定性）：10-20%

### 4. 动态调整原则

**根据市场环境和组合表现调整**：
- 牛市：可以适当增加仓位
- 熊市：降低仓位，保留现金
- 连续盈利：可以适当增加仓位
- 连续亏损：降低仓位，重新评估


## 主要仓位管理方法

### 固定金额法

**方法**：每笔投资固定金额。

**示例**：
- 总资金：100万
- 每笔投资：10万
- 最多持有：10只股票

**优点**：
- 简单易行
- 自动分散风险

**缺点**：
- 不考虑个股风险差异
- 不考虑机会质量

**适用场景**：
- 初学者
- 被动投资
- 指数化投资

### 固定比例法

**方法**：每笔投资占总资金的固定比例。

**示例**：
- 总资金：100万
- 每笔投资：10%
- 第一笔：10万
- 盈利后总资金：110万
- 第二笔：11万

**优点**：
- 自动适应资金变化
- 盈利时增加仓位
- 亏损时减少仓位

**缺点**：
- 可能过度集中
- 不考虑个股风险

**Python实现**：

```python
class FixedPercentage:
    def __init__(self, initial_capital, percentage=0.1):
        """
        initial_capital: 初始资金
        percentage: 固定比例
        """
        self.capital = initial_capital
        self.percentage = percentage
        self.positions = []
    
    def calculate_position_size(self):
        """计算仓位大小"""
        return self.capital * self.percentage
    
    def open_position(self, price):
        """开仓"""
        position_value = self.calculate_position_size()
        shares = int(position_value / price)
        
        self.positions.append({
            'shares': shares,
            'entry_price': price,
            'value': shares * price
        })
        
        return shares
    
    def update_capital(self, new_capital):
        """更新资金"""
        self.capital = new_capital

# 示例
strategy = FixedPercentage(initial_capital=100000, percentage=0.1)
shares = strategy.open_position(price=50)
print(f"购买股数: {shares}")
print(f"投资金额: ${shares * 50:,.0f}")
```

### 波动率调整法

**方法**：根据资产波动率调整仓位，高波动率 = 小仓位。

**公式**：
$
Position\ Size = \frac{Target\ Risk}{Volatility}
$

**示例**：
- 目标风险：2%
- 股票A波动率：20% → 仓位 = 2% / 20% = 10%
- 股票B波动率：40% → 仓位 = 2% / 40% = 5%

**Python实现**：

```python
class VolatilityAdjusted:
    def __init__(self, capital, target_risk=0.02):
        """
        capital: 总资金
        target_risk: 目标风险（如2%）
        """
        self.capital = capital
        self.target_risk = target_risk
    
    def calculate_position_size(self, volatility):
        """
        根据波动率计算仓位
        volatility: 年化波动率
        """
        position_percentage = self.target_risk / volatility
        position_value = self.capital * position_percentage
        return position_value, position_percentage
    
    def calculate_shares(self, price, volatility):
        """计算购买股数"""
        position_value, _ = self.calculate_position_size(volatility)
        shares = int(position_value / price)
        return shares

# 示例
vol_strategy = VolatilityAdjusted(capital=100000, target_risk=0.02)

# 低波动率股票
shares_low = vol_strategy.calculate_shares(price=100, volatility=0.15)
print(f"低波动率股票(15%): {shares_low}股")

# 高波动率股票
shares_high = vol_strategy.calculate_shares(price=100, volatility=0.40)
print(f"高波动率股票(40%): {shares_high}股")
```

**优点**：
- 风险标准化
- 自动适应波动率
- 更科学的风险管理

**缺点**：
- 需要估计波动率
- 历史波动率可能不代表未来


### 凯利公式法

**凯利公式**：数学上最优的仓位管理方法，最大化长期对数收益。

**公式**：
$
f^* = \frac{p \times b - q}{b} = \frac{p - q}{b}
$

其中：
- $f^*$ 是最优仓位比例
- $p$ 是胜率
- $q = 1 - p$ 是败率
- $b$ 是盈亏比（盈利/亏损）

**简化公式**（盈亏比为1:1时）：
$
f^* = 2p - 1
$

**示例计算**：

**案例1：高胜率策略**
- 胜率：60%
- 盈亏比：1:1
- 凯利仓位：(0.6 - 0.4) / 1 = 20%

**案例2：低胜率高盈亏比**
- 胜率：40%
- 盈亏比：3:1
- 凯利仓位：(0.4 × 3 - 0.6) / 3 = 20%

**Python实现**：

```python
import numpy as np
import matplotlib.pyplot as plt

class KellyCalculator:
    def __init__(self):
        pass
    
    def calculate_kelly(self, win_prob, win_loss_ratio):
        """
        计算凯利仓位
        win_prob: 胜率
        win_loss_ratio: 盈亏比
        """
        kelly_fraction = (win_prob * win_loss_ratio - (1 - win_prob)) / win_loss_ratio
        return max(0, kelly_fraction)  # 不能为负
    
    def calculate_expected_growth(self, win_prob, win_loss_ratio, fraction):
        """
        计算期望增长率
        """
        # 对数期望增长率
        win_return = np.log(1 + fraction * win_loss_ratio)
        loss_return = np.log(1 - fraction)
        
        expected_growth = win_prob * win_return + (1 - win_prob) * loss_return
        return expected_growth
    
    def plot_growth_curve(self, win_prob, win_loss_ratio):
        """
        绘制增长率曲线
        """
        fractions = np.linspace(0, 1, 100)
        growth_rates = [self.calculate_expected_growth(win_prob, win_loss_ratio, f) 
                       for f in fractions]
        
        kelly_fraction = self.calculate_kelly(win_prob, win_loss_ratio)
        kelly_growth = self.calculate_expected_growth(win_prob, win_loss_ratio, kelly_fraction)
        
        plt.figure(figsize=(12, 7))
        plt.plot(fractions, growth_rates, linewidth=2)
        plt.axvline(kelly_fraction, color='red', linestyle='--', 
                   label=f'Kelly Fraction: {kelly_fraction:.2%}')
        plt.axhline(0, color='black', linestyle='-', alpha=0.3)
        plt.scatter([kelly_fraction], [kelly_growth], color='red', s=100, zorder=5)
        
        plt.xlabel('Bet Fraction')
        plt.ylabel('Expected Log Growth Rate')
        plt.title(f'Kelly Criterion (Win Rate: {win_prob:.0%}, Win/Loss: {win_loss_ratio:.1f})')
        plt.legend()
        plt.grid(True, alpha=0.3)
        return plt

# 示例
kelly = KellyCalculator()

# 计算不同策略的凯利仓位
strategies = [
    {'name': '高胜率低盈亏比', 'win_prob': 0.65, 'ratio': 1.0},
    {'name': '中等胜率中等盈亏比', 'win_prob': 0.50, 'ratio': 2.0},
    {'name': '低胜率高盈亏比', 'win_prob': 0.35, 'ratio': 3.0},
]

print("凯利仓位计算:")
for s in strategies:
    kelly_f = kelly.calculate_kelly(s['win_prob'], s['ratio'])
    print(f"{s['name']}: {kelly_f:.1%}")
```

**半凯利（Half Kelly）**：

实践中，完全凯利仓位风险较大，通常使用半凯利或1/4凯利：

$
f_{half} = \frac{f^*}{2}
$

**原因**：
- 降低波动率
- 对参数估计误差更宽容
- 更适合实际投资

**凯利公式的优缺点**：

**优点**：
- 数学上最优
- 最大化长期增长
- 考虑胜率和盈亏比

**缺点**：
- 需要准确估计胜率和盈亏比
- 完全凯利波动率很大
- 对参数估计误差敏感
- 可能导致过度集中

**实践建议**：
- 使用半凯利或1/4凯利
- 设置最大仓位上限（如25%）
- 保守估计胜率和盈亏比
- 定期重新评估参数


### 风险平价法

**方法**：使每个资产对组合风险的贡献相等。

**原理**：
传统配置按资金分配（如60/40股债），但股票风险远大于债券，导致风险集中在股票。

风险平价按风险分配，使每个资产的风险贡献相等。

**风险贡献**：
$
Risk\ Contribution_i = w_i \times \frac{\partial \sigma_p}{\partial w_i}
$

**目标**：
$
Risk\ Contribution_1 = Risk\ Contribution_2 = ... = Risk\ Contribution_n
$

**简化计算**（两资产）：
$
w_1 = \frac{\sigma_2}{\sigma_1 + \sigma_2}, \quad w_2 = \frac{\sigma_1}{\sigma_1 + \sigma_2}
$

**Python实现**：

```python
class RiskParity:
    def __init__(self, returns):
        """
        returns: DataFrame, 各资产收益率
        """
        self.returns = returns
        self.cov_matrix = returns.cov()
        self.volatilities = returns.std()
    
    def calculate_weights_simple(self):
        """
        简化风险平价（假设资产不相关）
        """
        inv_vol = 1 / self.volatilities
        weights = inv_vol / inv_vol.sum()
        return weights
    
    def calculate_portfolio_risk(self, weights):
        """计算组合风险"""
        portfolio_var = np.dot(weights, np.dot(self.cov_matrix, weights))
        return np.sqrt(portfolio_var)
    
    def calculate_risk_contribution(self, weights):
        """计算风险贡献"""
        portfolio_vol = self.calculate_portfolio_risk(weights)
        marginal_contrib = np.dot(self.cov_matrix, weights) / portfolio_vol
        risk_contrib = weights * marginal_contrib
        return risk_contrib / risk_contrib.sum()

# 示例
np.random.seed(42)
returns_data = pd.DataFrame({
    'Stock': np.random.normal(0.0008, 0.02, 250),
    'Bond': np.random.normal(0.0003, 0.005, 250),
    'Commodity': np.random.normal(0.0005, 0.015, 250)
})

rp = RiskParity(returns_data)
weights = rp.calculate_weights_simple()
risk_contrib = rp.calculate_risk_contribution(weights.values)

print("风险平价权重:")
for asset, weight in weights.items():
    print(f"  {asset}: {weight:.1%}")

print("\n风险贡献:")
for asset, contrib in zip(weights.index, risk_contrib):
    print(f"  {asset}: {contrib:.1%}")
```

**优点**：
- 真正的风险分散
- 适合多资产配置
- 降低组合波动率

**缺点**：
- 可能需要杠杆（低风险资产权重高）
- 不考虑预期收益
- 实施复杂

### 最大回撤控制法

**方法**：根据最大可接受回撤确定仓位。

**公式**：
$
Position\ Size = \frac{Max\ Acceptable\ Drawdown}{Expected\ Drawdown}
$

**示例**：
- 最大可接受回撤：20%
- 策略历史最大回撤：40%
- 建议仓位：20% / 40% = 50%

**Python实现**：

```python
class DrawdownControl:
    def __init__(self, returns, max_acceptable_dd=0.20):
        """
        returns: 策略历史收益率
        max_acceptable_dd: 最大可接受回撤
        """
        self.returns = returns
        self.max_acceptable_dd = max_acceptable_dd
    
    def calculate_max_drawdown(self):
        """计算历史最大回撤"""
        cumulative = (1 + self.returns).cumprod()
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min()
    
    def calculate_position_size(self):
        """计算建议仓位"""
        historical_dd = abs(self.calculate_max_drawdown())
        
        if historical_dd == 0:
            return 1.0  # 无历史回撤，满仓
        
        position_size = self.max_acceptable_dd / historical_dd
        return min(position_size, 1.0)  # 不超过100%

# 示例
strategy_returns = np.random.normal(0.001, 0.03, 250)
dd_control = DrawdownControl(strategy_returns, max_acceptable_dd=0.15)

historical_dd = dd_control.calculate_max_drawdown()
position_size = dd_control.calculate_position_size()

print(f"历史最大回撤: {historical_dd:.1%}")
print(f"建议仓位: {position_size:.1%}")
```

## 动态仓位调整

### 金字塔加仓

**方法**：盈利后逐步加仓，亏损不加仓。

**正金字塔**（推荐）：
- 首次：30%
- 盈利5%后：20%
- 再盈利5%后：10%

**倒金字塔**（不推荐）：
- 首次：10%
- 盈利后：20%
- 再盈利后：30%

**为什么正金字塔更好**：
- 初始仓位大，成本低
- 后续加仓谨慎
- 控制平均成本

**Python实现**：

```python
class PyramidStrategy:
    def __init__(self, initial_capital, initial_position_pct=0.3):
        """
        initial_capital: 初始资金
        initial_position_pct: 初始仓位比例
        """
        self.capital = initial_capital
        self.initial_position_pct = initial_position_pct
        self.positions = []
        self.total_shares = 0
    
    def initial_entry(self, price):
        """初始建仓"""
        position_value = self.capital * self.initial_position_pct
        shares = int(position_value / price)
        
        self.positions.append({
            'shares': shares,
            'price': price,
            'value': shares * price
        })
        self.total_shares += shares
        
        return shares
    
    def add_position(self, current_price, add_pct, profit_threshold=0.05):
        """加仓"""
        if not self.positions:
            return 0
        
        # 检查是否达到盈利阈值
        avg_cost = sum(p['value'] for p in self.positions) / self.total_shares
        profit_pct = (current_price - avg_cost) / avg_cost
        
        if profit_pct < profit_threshold:
            return 0
        
        # 加仓
        add_value = self.capital * add_pct
        shares = int(add_value / current_price)
        
        self.positions.append({
            'shares': shares,
            'price': current_price,
            'value': shares * current_price
        })
        self.total_shares += shares
        
        return shares
    
    def get_average_cost(self):
        """计算平均成本"""
        if self.total_shares == 0:
            return 0
        total_value = sum(p['value'] for p in self.positions)
        return total_value / self.total_shares

# 示例
pyramid = PyramidStrategy(initial_capital=100000, initial_position_pct=0.3)

# 初始建仓
shares1 = pyramid.initial_entry(price=100)
print(f"初始建仓: {shares1}股 @ $100")

# 第一次加仓（价格上涨5%）
shares2 = pyramid.add_position(current_price=105, add_pct=0.2, profit_threshold=0.05)
print(f"第一次加仓: {shares2}股 @ $105")

# 第二次加仓（价格再上涨5%）
shares3 = pyramid.add_position(current_price=110, add_pct=0.1, profit_threshold=0.05)
print(f"第二次加仓: {shares3}股 @ $110")

print(f"\n总持仓: {pyramid.total_shares}股")
print(f"平均成本: ${pyramid.get_average_cost():.2f}")
```

### 马丁格尔策略（不推荐）

**方法**：亏损后加倍下注。

**示例**：
- 首次：10%
- 亏损后：20%
- 再亏损：40%

**为什么不推荐**：
- 可能导致破产
- 需要无限资金
- 违背风险管理原则

**历史教训**：
许多交易员因使用马丁格尔策略而破产。

### 反马丁格尔策略（推荐）

**方法**：盈利后增加仓位，亏损后减少仓位。

**示例**：
- 盈利：增加10%仓位
- 亏损：减少10%仓位

**优点**：
- 顺势而为
- 控制风险
- 符合趋势跟踪


## 实战案例

### 案例1：巴菲特的集中投资

**策略**：
- 重仓持有少数优质公司
- 前5大持仓占比超过70%
- 长期持有，很少交易

**仓位管理特点**：
- 高确定性 = 大仓位
- 深入研究后重仓
- 不分散到不了解的领域

**适用条件**：
- 深度研究能力
- 长期投资视角
- 高风险承受能力

**启示**：
对于真正理解的机会，可以重仓；但需要极高的研究深度。

### 案例2：索罗斯的量子基金

**策略**：
- 高杠杆，高集中度
- 重大机会时重仓出击
- 1992年做空英镑，单笔盈利10亿美元

**仓位管理特点**：
- 平时分散，机会来临时集中
- 使用杠杆放大收益
- 严格止损

**风险**：
- 极高风险
- 需要精准判断
- 不适合普通投资者

### 案例3：长期资本管理公司（LTCM）的失败

**策略**：
- 高杠杆（25-30倍）
- 看似低风险的套利策略
- 分散化投资

**失败原因**：
- 过度杠杆
- 极端情况下相关性崩溃
- 流动性危机
- 被迫平仓

**教训**：
- 杠杆是双刃剑
- 即使分散化也要控制总仓位
- 保留流动性缓冲
- 极端情况下模型可能失效

## 不同市场环境的仓位策略

### 牛市策略

**特征**：
- 市场整体上涨
- 风险偏好高
- 波动率低

**仓位策略**：
- 可以适当提高仓位（70-90%）
- 增加进攻性资产
- 使用杠杆（谨慎）
- 保留部分现金应对回调

### 熊市策略

**特征**：
- 市场整体下跌
- 风险偏好低
- 波动率高

**仓位策略**：
- 大幅降低仓位（30-50%）
- 增加防御性资产
- 保留大量现金
- 等待机会

### 震荡市策略

**特征**：
- 无明确趋势
- 区间波动
- 不确定性高

**仓位策略**：
- 中等仓位（50-70%）
- 分散投资
- 高抛低吸
- 灵活调整

### 危机时期策略

**特征**：
- 极端波动
- 流动性危机
- 恐慌性抛售

**仓位策略**：
- 保留大量现金（50%+）
- 分批建仓
- 关注优质资产
- 耐心等待

## 常见误区

### 误区1：满仓才能赚大钱

**真相**：满仓风险极大，一次重大亏损可能抹去多年收益。

**正确做法**：
- 保留安全边际
- 根据机会质量调整仓位
- 不要害怕持有现金

### 误区2：分散越多越好

**真相**：过度分散会稀释收益，增加管理难度。

**正确做法**：
- 适度分散（10-20只股票）
- 集中在理解的领域
- 平衡分散和集中

### 误区3：亏损后加仓摊平成本

**真相**：这是马丁格尔策略，可能导致更大亏损。

**正确做法**：
- 亏损后重新评估
- 如果逻辑改变，止损离场
- 如果逻辑未变，可以适当加仓
- 但要设置总亏损上限

### 误区4：凭感觉决定仓位

**真相**：情绪化决策往往导致错误。

**正确做法**：
- 建立系统化的仓位管理规则
- 提前制定计划
- 严格执行纪律

### 误区5：忽视相关性

**真相**：持有多只高度相关的股票并非真正分散。

**正确做法**：
- 关注资产相关性
- 跨资产类别分散
- 跨地域分散

## 实战建议

### 1. 建立仓位管理系统

**系统化流程**：
```
1. 风险评估 → 确定总风险预算
2. 机会评估 → 评估投资机会质量
3. 仓位计算 → 使用合适的方法计算仓位
4. 执行建仓 → 分批建仓
5. 动态调整 → 根据市场变化调整
6. 定期审查 → 评估仓位管理效果
```

### 2. 制定仓位管理规则

**示例规则**：
- 单只股票：不超过10%
- 单一行业：不超过25%
- 总仓位：根据市场环境在30-90%之间
- 单笔风险：不超过2%
- 止损：每只股票设置止损点

### 3. 使用仓位管理工具

**Excel/Python工具**：
- 自动计算建议仓位
- 跟踪实际仓位
- 监控风险敞口
- 生成报告

```python
class PositionManager:
    def __init__(self, total_capital, max_single_position=0.10, 
                 max_sector=0.25, max_total=0.90):
        """
        total_capital: 总资金
        max_single_position: 单只股票最大仓位
        max_sector: 单一行业最大仓位
        max_total: 总仓位上限
        """
        self.total_capital = total_capital
        self.max_single_position = max_single_position
        self.max_sector = max_sector
        self.max_total = max_total
        self.positions = {}
        self.sectors = {}
    
    def can_add_position(self, symbol, sector, proposed_value):
        """检查是否可以增加仓位"""
        # 检查单只股票限制
        current_value = self.positions.get(symbol, 0)
        if (current_value + proposed_value) / self.total_capital > self.max_single_position:
            return False, "超过单只股票限制"
        
        # 检查行业限制
        current_sector = self.sectors.get(sector, 0)
        if (current_sector + proposed_value) / self.total_capital > self.max_sector:
            return False, "超过行业限制"
        
        # 检查总仓位限制
        total_position = sum(self.positions.values())
        if (total_position + proposed_value) / self.total_capital > self.max_total:
            return False, "超过总仓位限制"
        
        return True, "可以建仓"
    
    def add_position(self, symbol, sector, value):
        """增加仓位"""
        can_add, message = self.can_add_position(symbol, sector, value)
        
        if not can_add:
            print(f"无法建仓 {symbol}: {message}")
            return False
        
        self.positions[symbol] = self.positions.get(symbol, 0) + value
        self.sectors[sector] = self.sectors.get(sector, 0) + value
        
        print(f"成功建仓 {symbol}: ${value:,.0f}")
        return True
    
    def get_position_summary(self):
        """获取仓位摘要"""
        total_position = sum(self.positions.values())
        
        return {
            'total_capital': self.total_capital,
            'total_position': total_position,
            'position_percentage': total_position / self.total_capital,
            'cash': self.total_capital - total_position,
            'positions': self.positions,
            'sectors': self.sectors
        }

# 示例
pm = PositionManager(total_capital=1000000)

# 尝试建仓
pm.add_position('AAPL', 'Technology', 80000)
pm.add_position('MSFT', 'Technology', 70000)
pm.add_position('GOOGL', 'Technology', 90000)  # 可能超过行业限制

summary = pm.get_position_summary()
print(f"\n总仓位: {summary['position_percentage']:.1%}")
print(f"剩余现金: ${summary['cash']:,.0f}")
```

### 4. 定期审查和调整

**审查频率**：
- 日度：监控风险敞口
- 周度：评估仓位分布
- 月度：全面审查和调整
- 季度：评估仓位管理策略

**审查内容**：
- 实际仓位 vs 目标仓位
- 风险集中度
- 行业分布
- 盈亏情况
- 市场环境变化

### 5. 记录和学习

**建立交易日志**：
- 记录每次仓位决策
- 记录决策理由
- 跟踪结果
- 分析成功和失败

**持续改进**：
- 定期回顾
- 总结经验教训
- 优化仓位管理规则
- 适应市场变化

## 延伸阅读

### 经典著作

1. **Thorp, E. O. (2006)**. *Beat the Dealer*. Vintage.
   - 凯利公式的实践应用

2. **Poundstone, W. (2005)**. *Fortune's Formula: The Untold Story of the Scientific Betting System That Beat the Casinos and Wall Street*. Hill and Wang.
   - 凯利公式的历史和应用

3. **Vince, R. (1992)**. *The Mathematics of Money Management*. Wiley.
   - 资金管理的数学基础

4. **Jones, R. (1999)**. *The Trading Game: Playing by the Numbers to Make Millions*. Wiley.
   - 仓位管理实践指南

### 学术论文

5. **Kelly, J. L. (1956)**. "A New Interpretation of Information Rate". *Bell System Technical Journal*, 35(4), 917-926.
   - 凯利公式原始论文

6. **MacLean, L. C., Thorp, E. O., & Ziemba, W. T. (2011)**. *The Kelly Capital Growth Investment Criterion*. World Scientific.
   - 凯利公式的全面研究

7. **Browne, S. (1999)**. "The Risk and Rewards of Minimizing Shortfall Probability". *Journal of Portfolio Management*, 25(4), 76-85.
   - 风险管理和仓位优化

### 实践指南

8. **Elder, A. (1993)**. *Trading for a Living*. Wiley.
   - 包含实用的资金管理章节

9. **Schwager, J. D. (2012)**. *Market Wizards*. Wiley.
   - 顶级交易员的仓位管理经验

10. **Covel, M. W. (2009)**. *Trend Following*. FT Press.
    - 趋势跟踪中的仓位管理

## 总结

仓位管理是投资成功的关键，需要：

**关键要点**：
1. 风险第一，永远不要冒破产风险
2. 根据机会质量和风险调整仓位
3. 凯利公式提供理论最优，但实践中要保守
4. 动态调整仓位，适应市场环境
5. 建立系统化的仓位管理规则
6. 定期审查和持续改进
7. 避免情绪化决策

**实践框架**：
- 日常：使用波动率调整法或固定比例法
- 重大机会：参考凯利公式（使用半凯利）
- 多资产：使用风险平价法
- 危机时期：大幅降低仓位，保留现金
- 持续：记录、审查、学习、改进

仓位管理没有完美的方法，关键是找到适合自己的系统，并严格执行。记住：保护资本是第一位的，只有活下来，才能等到下一个机会。

---

**下一步学习**：
- [行为金融学](behavioral-finance.html) - 理解心理因素对仓位决策的影响
- [组合对冲](portfolio-hedging.html) - 学习如何对冲风险
- [风险测量](risk-measurement.html) - 深入理解风险度量

**相关主题**：
- [VaR和CVaR](var-cvar.html)
- [压力测试](stress-testing.html)
- [风险类型](risk-types.html)
