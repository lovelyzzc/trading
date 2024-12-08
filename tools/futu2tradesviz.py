from dataclasses import dataclass
from typing import List, Tuple, Optional
import pandas as pd
import datetime

@dataclass
class Trade:
    """交易记录基础结构"""
    date: str
    time: str
    symbol: str
    asset_type: str
    price: float
    currency: str
    quantity: float
    commission: float
    tags: str = ''
    notes: str = ''

def parse_datetime(dt_str: str) -> Tuple[Optional[str], Optional[str]]:
    """解析日期时间字符串,返回UTC的date和time"""
    if pd.isna(dt_str):
        return None, None
    
    timezone_map = {
        '香港': 8,   # UTC+8
        '美东': -4,  # UTC-4
    }
    
    dt_str = str(dt_str)
    timezone = dt_str.split('(')[1].rstrip(')')
    dt = datetime.datetime.strptime(dt_str.split('(')[0], '%Y/%m/%d %H:%M:%S')
    
    if timezone in timezone_map:
        dt = dt - datetime.timedelta(hours=timezone_map[timezone])
    
    return dt.strftime('%Y%m%d'), dt.strftime('%H:%M:%S')

def get_asset_type(symbol: str) -> str:
    """判断资产类型"""
    if len(symbol) == 5:
        return 'stock'
    if 'P' in symbol or 'C' in symbol:
        return 'stock_option'
    return 'stock'

def create_single_trade(row: pd.Series, symbol: str, direction: str) -> Trade:
    """创建单个交易记录"""
    date, time = parse_datetime(row['成交时间'])
    quantity = float(row['成交数量'])
    if direction in ['卖出', '卖空']:
        quantity = -quantity
        
    return Trade(
        date=date,
        time=time,
        symbol=symbol,
        asset_type=get_asset_type(symbol),
        price=float(row['成交价格']),
        currency='HKD' if row['币种'] == '港元' else 'USD',
        quantity=quantity,
        commission=float(row['合计费用']) if pd.notna(row['合计费用']) else 0.0
    )

def is_follow_execution(current_row: pd.Series) -> bool:
    """判断是否为分批成交的后续记录
    
    分批成交的特征:
    1. 代码为空
    2. 有成交时间
    """
    return (pd.isna(current_row['代码']) and  # 代码为空
            pd.notna(current_row['成交时间']))  # 有成交时间

def merge_batch_trades(trades: List[Trade]) -> Trade:
    """合并分批成交"""
    base_trade = trades[0]
    total_quantity = sum(t.quantity for t in trades)
    
    return Trade(
        date=base_trade.date,
        time=base_trade.time,
        symbol=base_trade.symbol,
        asset_type=base_trade.asset_type,
        price=base_trade.price,
        currency=base_trade.currency,
        quantity=total_quantity,
        commission=base_trade.commission  # 手续费已经在第一笔交易中
    )

def process_strategy_trades(trades: List[Trade], total_commission: float) -> List[Trade]:
    """处理策略交易组，按成交量比例分配手续费"""
    if not trades:
        return trades
        
    total_quantity = sum(abs(trade.quantity) for trade in trades)
    for trade in trades:
        trade.commission = round(total_commission * (abs(trade.quantity) / total_quantity), 2)
    return trades

def process_trades(filename: str) -> pd.DataFrame:
    """主处理函数"""
    df = pd.read_csv(filename)
    results = []
    
    # 状态变量
    strategy_trades: List[Trade] = []
    batch_trades: List[Trade] = []
    last_commission = 0
    last_symbol = None
    last_direction = None
    is_strategy = False
    
    for _, row in df.iterrows():
        # 策略行处理
        if pd.notna(row['合计费用']) and pd.isna(row['成交时间']):
            last_commission = float(row['合计费用'])
            is_strategy = True
            continue
        
        if pd.isna(row['成交时间']):
            continue
            
        if is_follow_execution(row):
            # 使用上一个交易的代码和方向
            trade = create_single_trade(row, last_symbol, last_direction)
            if is_strategy:
                strategy_trades.append(trade)
            else:
                batch_trades.append(trade)
            continue
        
        if is_strategy and pd.notna(row['合计费用']) and pd.notna(row['成交时间']):
            if strategy_trades:
                results.extend(process_strategy_trades(strategy_trades, last_commission))
                strategy_trades = []
            is_strategy = False
        
        # 处理新交易
        current_symbol = str(row['代码'])
        current_direction = row['方向']
        
        # 创建交易记录
        trade = create_single_trade(row, current_symbol, current_direction)
        
        # 处理之前累积的分批成交
        if batch_trades:
            results.append(merge_batch_trades(batch_trades))
            batch_trades = []
        
        # 更新状态
        last_symbol = current_symbol
        last_direction = current_direction
        
        # 分配到对应的处理组
        if is_strategy:
            strategy_trades.append(trade)
        else:
            batch_trades = [trade]  # 开始新的分批成交组
    
    # 处理最后一组记录
    if strategy_trades:
        results.extend(process_strategy_trades(strategy_trades, last_commission))
    elif batch_trades:
        results.append(merge_batch_trades(batch_trades))
    
    return pd.DataFrame([vars(trade) for trade in results])

if __name__ == '__main__':
    # 设置pandas显示选项
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_rows', None)
    
    # 处理交易数据
    result_df = process_trades('src.csv')
    result_df.to_csv('res.csv', index=False)
