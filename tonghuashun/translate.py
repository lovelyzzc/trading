import pandas as pd
import os
from pathlib import Path
import glob

def batch_xls_to_ths(source_dir='tonghuashun/source_file', output_dir='tonghuashun/outputs'):
    """
    批量转换目录中的XLS文件为同花顺格式
    参数：
    source_dir: 源文件目录（默认'source_file'）
    output_dir: 输出目录（默认'outputs'）
    """
    # 创建输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 获取所有Excel文件（支持.xls和.xlsx）
    excel_files = glob.glob(os.path.join(source_dir, '*.xls*'))
    
    for file_path in excel_files:
        try:
            # 读取文件时跳过首行
            df = pd.read_excel(file_path)
            print(df.columns)
            
            # 生成输出路径（改为ini扩展名）
            filename = os.path.basename(file_path).split('.')[0] + '_ths.ini'
            output_path = os.path.join(output_dir, filename)
            
            # 提取所有股票代码（去重+去空值）
            stock_codes = df['股票代码'].dropna().astype(str).unique()
            
            # 转换为INI格式
            with open(output_path, 'w', encoding='gbk') as f:
                f.write("[自选股设置]\n")
                f.write(f"股票代码={','.join(stock_codes)}\n")
                f.write("板块名称=我的自选股\n")  # 固定名称或可替换为变量
                
            print(f"成功转换：{filename}")
            
        except KeyError:
            print(f"错误：文件 {os.path.basename(file_path)} 缺少'股票代码'列")
        except Exception as e:
            print(f"处理 {os.path.basename(file_path)} 失败：{str(e)}")

# 使用示例
batch_xls_to_ths()