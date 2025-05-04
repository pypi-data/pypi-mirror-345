# SSQuant 松鼠量化交易系统

<div align="center">
  <img src="https://raw.githubusercontent.com/songshuquant/ssquant/main/ssquant/assets/squirrel_quant_logo.png" alt="SSQuant Logo" width="200">
  
  [![PyPI version](https://img.shields.io/pypi/v/ssquant.svg)](https://pypi.org/project/ssquant/)
  [![Python Versions](https://img.shields.io/pypi/pyversions/ssquant.svg)](https://pypi.org/project/ssquant/)
  [![License](https://img.shields.io/pypi/l/ssquant.svg)](https://github.com/songshuquant/ssquant/blob/main/LICENSE)
</div>

## 简介

SSQuant (松鼠Quant) 是一个功能强大的量化交易回测系统，支持多品种、多周期的策略回测。系统设计灵活，易于使用，适合量化交易研究人员、金融机构和个人投资者使用。

### 主要特点

- **多品种多周期回测**：同时回测多个交易品种和不同时间周期
- **多数据源支持**：支持API数据获取、本地数据加载和自定义数据源
- **参数优化**：支持网格搜索、随机搜索和贝叶斯优化
- **灵活的策略API**：简单易用的策略编写接口
- **完整的绩效分析**：计算各种交易指标和可视化分析
- **可扩展性**：模块化设计，易于扩展和自定义

## 安装

```bash
# 从PyPI安装
pip install ssquant

# 安装完整版（包含更多依赖）
pip install ssquant[full]

# 开发版本（包含开发工具）
pip install ssquant[dev]
```

## 快速开始

### 基本用法

```python
from ssquant import MultiSourceBacktester

# 创建回测实例
backtester = MultiSourceBacktester()

# 配置回测参数
backtester.set_base_config({
    'use_cache': True,
    'save_data': True,
    'align_data': True,
    'debug': False
})

# 添加品种配置
backtester.add_symbol_config('rb888', {
    'periods': [
        {'kline_period': '1h', 'adjust_type': '1'},
        {'kline_period': 'D', 'adjust_type': '1'}
    ],
    'start_date': '2023-01-01',
    'end_date': '2023-12-31',
    'initial_capital': 100000.0
})

# 定义策略函数
def my_strategy(api):
    data = api.data[0]
    
    # 简单的移动平均线交叉策略
    if len(data.data) > 20 and data.current_idx >= 20:
        # 计算移动平均线
        ma5 = data.data['close'].iloc[data.current_idx-5:data.current_idx].mean()
        ma20 = data.data['close'].iloc[data.current_idx-20:data.current_idx].mean()
        
        position = data.current_pos
        
        # 金叉买入
        if ma5 > ma20 and position <= 0:
            api.buy(data, 1, reason="金叉买入")
        
        # 死叉卖出
        elif ma5 < ma20 and position > 0:
            api.sell(data, 1, reason="死叉卖出")

# 定义初始化函数
def initialize(api):
    api.log("策略初始化")
    api.log(f"策略参数: {api.params}")

# 运行回测
results = backtester.run(my_strategy, initialize, {'param1': 100})

# 显示回测结果
backtester.show_results(results)
```

## 项目结构

```
ssquant/
├── ssquant/           # 主要包目录
│   ├── api/           # API接口模块
│   ├── backtest/      # 回测核心模块
│   ├── config/        # 配置相关模块
│   ├── data/          # 数据获取与处理模块
│   ├── indicators/    # 技术指标计算模块
│   ├── assets/        # 静态资源文件
│   └── __init__.py    # 初始化文件
├── setup.py           # 打包配置文件
├── MANIFEST.in        # 资源文件配置
├── README.md          # 项目说明文件
```

## 主要功能

### 数据获取

系统支持多种数据获取方式：

1. **API数据获取**：通过网络API获取实时或历史数据
2. **本地数据加载**：加载本地CSV、Excel、HDF5等格式的数据文件
3. **自定义数据源**：可以扩展实现自己的数据源

```python
# API数据获取
backtester.add_symbol_config('rb888', {
    'data_source': 'api',
    'api_name': 'akshare',
    'periods': [{'kline_period': '1h'}],
    'start_date': '2023-01-01',
    'end_date': '2023-12-31'
})

# 本地数据加载
backtester.add_symbol_config('AAPL', {
    'data_source': 'local',
    'file_path': 'data/AAPL_daily.csv',
    'date_column': 'date',
    'price_columns': {
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    }
})
```

### 参数优化

系统支持多种参数优化方法，帮助找到最佳策略参数：

```python
param_grid = {
    'fast_period': [5, 10, 15, 20],
    'slow_period': [20, 30, 40, 50],
    'signal_period': [7, 9, 11]
}

# 网格搜索
best_params, best_result = backtester.optimize_parameters(
    strategy=my_strategy,
    param_grid=param_grid,
    method='grid',
    optimization_metric='sharpe_ratio',
    higher_is_better=True
)

# 贝叶斯优化
param_space = {
    'fast_period': (5, 20),
    'slow_period': (20, 50),
    'signal_period': (5, 12)
}

best_params, best_result = backtester.optimize_parameters(
    strategy=my_strategy,
    param_space=param_space,
    method='bayesian',
    n_calls=50,
    optimization_metric='profit_factor',
    higher_is_better=True
)
```

### 结果分析

系统提供完整的交易结果分析和可视化：

```python
# 计算性能指标
metrics = backtester.calculate_metrics(results)
print(f"总收益率: {metrics['total_return']:.2%}")
print(f"年化收益率: {metrics['annual_return']:.2%}")
print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
print(f"最大回撤: {metrics['max_drawdown']:.2%}")

# 可视化
backtester.plot_equity_curve(results)
backtester.plot_drawdown(results)
backtester.plot_monthly_returns(results)
backtester.plot_trades(results)
```

## 高级功能

### 多品种联合回测

```python
# 添加多个品种
backtester.add_symbol_config('rb888', {...})
backtester.add_symbol_config('IF9999', {...})
backtester.add_symbol_config('T9999', {...})

# 定义多品种策略
def multi_symbol_strategy(api):
    rb_data = api.get_symbol_data('rb888')
    if_data = api.get_symbol_data('IF9999')
    t_data = api.get_symbol_data('T9999')
    
    # 跨品种策略逻辑
    ...
```

### 自定义指标计算

```python
from ssquant.indicators import ta

# 在策略中使用
def strategy_with_indicators(api):
    data = api.data[0]
    
    # 计算MACD
    macd, signal, hist = ta.macd(data.data['close'], 
                                 fastperiod=12, 
                                 slowperiod=26, 
                                 signalperiod=9)
    
    # 计算布林带
    upper, middle, lower = ta.bbands(data.data['close'], 
                                     timeperiod=20, 
                                     nbdevup=2, 
                                     nbdevdn=2)
    
    # 基于指标的交易信号
    ...
```

## 完整文档

查看 [完整文档](https://github.com/songshuquant/ssquant) 获取更多详细信息和示例。

## 依赖项

核心依赖:
- pandas >= 1.0.0: 数据处理
- numpy >= 1.18.0: 数值计算
- matplotlib >= 3.3.0: 图表绘制
- scipy >= 1.6.0: 科学计算
- requests >= 2.25.0: HTTP请求
- joblib >= 1.0.0: 并行计算

可选依赖:
- scikit-learn >= 1.0.0: 机器学习算法
- plotly >= 5.0.0: 交互式可视化
- statsmodels >= 0.12.0: 统计模型
- numpy-financial >= 1.0.0: 金融函数

## 贡献指南

我们欢迎各种形式的贡献，包括但不限于:

1. 提交问题和功能请求
2. 提交代码改进
3. 改进文档
4. 分享使用经验

## 许可证

MIT License

## 联系方式

- 邮箱: 339093103@qq.com
- GitHub: [https://github.com/songshuquant/ssquant](https://github.com/songshuquant/ssquant) 