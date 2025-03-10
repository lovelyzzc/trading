import csv
from datetime import datetime

def convert_txt_to_csv(input_file, output_file):
    with open(input_file, 'r', encoding='gbk') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = infile.readlines()
        fieldnames = [
            'date', 'symbol', 'side', 'currency', 'underlying',
            'asset_type', 'price', 'quantity', 'commission', 'fees',
            'tags', 'notes', 'spread_id'
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for idx, line in enumerate(reader):
            if idx == 0:  # 跳过标题行
                continue

            # 解析原始数据
            parts = [x.strip() for x in line.strip().split('\t') if x.strip()]
            if len(parts) < 10:
                continue

            # 处理时间格式
            trade_time = parts[0]
            trade_date = parts[8]
            iso_date = datetime.strptime(
                f"{trade_date} {trade_time}", "%Y%m%d %H:%M:%S"
            ).strftime("%Y-%m-%dT%H:%M:%S+0800")

            # 映射买卖方向
            side_mapping = {
                '证券买入': 'buy',
                '证券卖出': 'sell',
                '红股派息': 'dividend',
                '指定交易': 'assignment'
            }
            operation = parts[2]
            side = side_mapping.get(operation, operation.lower())

            # 判断资产类型
            asset_name = parts[3]
            asset_type = 'ETF' if 'ETF' in asset_name else 'stock'

            # 处理特殊记录
            quantity = parts[4] if parts[4] != '0' else '0'
            price = parts[5] if parts[5] != '0.000' else '0'

            # 构建输出记录
            record = {
                'date': iso_date,
                'symbol': parts[1].zfill(6),  # 补全6位代码
                'side': side,
                'currency': 'CNY',
                'underlying': asset_name,
                'asset_type': asset_type,
                'price': price,
                'quantity': quantity,
                'commission': '0',  # 原始数据未提供
                'fees': '0',        # 原始数据未提供
                'tags': '',
                'notes': '',
                'spread_id': parts[1].zfill(6)  # 修改为symbol值
            }

            # 处理特殊操作类型
            if operation == '红股派息':
                record['quantity'] = '0'
                record['price'] = '0'
                record['asset_type'] = 'dividend'
            elif operation == '指定交易':
                record['asset_type'] = 'special'

            writer.writerow(record)

# 使用示例
convert_txt_to_csv('tradesviz/table.txt', 'tradesviz/output.csv')
