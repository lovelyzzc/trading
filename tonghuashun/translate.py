import pandas as pd
import os
from pathlib import Path
import glob

def batch_xls_to_ths(source_dir='tonghuashun/source_file', 
                    output_dir='tonghuashun/outputs',
                    tv_output_dir='tonghuashun/tv_outputs'):
    """
    批量转换目录中的XLS文件为同花顺格式
    参数：
    source_dir: 源文件目录（默认'source_file'）
    output_dir: 输出目录（默认'outputs'）
    tv_output_dir: TradingView输出目录（默认'tonghuashun/tv_outputs'）
    """
    # 创建两个输出目录
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(tv_output_dir).mkdir(parents=True, exist_ok=True)  # 新增TV输出目录
    
    # 获取所有Excel文件（支持.xls和.xlsx）
    excel_files = glob.glob(os.path.join(source_dir, '*.xls*'))
    
    for file_path in excel_files:
        try:
            # 读取文件时跳过首行（添加行数统计）
            df = pd.read_excel(file_path)
            total_rows = len(df)
            
            # 生成两个输出路径
            base_name = os.path.basename(file_path).split('.')[0]
            ini_path = os.path.join(output_dir, f"{base_name}_ths.ini")
            txt_path = os.path.join(tv_output_dir, f"{base_name}_ths.txt")  # 新增txt路径
            
            # 提取所有股票代码（去重+去空值）并补零到6位
            stock_codes = df['股票代码'].dropna().astype(str).str.zfill(6).unique()
            
            # 提取并限制TV格式的股票代码数量（保持补零后的格式）
            tv_codes = stock_codes[:999]  # 截取前999个代码
            
            # 转换为INI格式
            with open(ini_path, 'w', encoding='gbk') as f:
                f.write("[自选股设置]\n")
                f.write(f"股票代码={','.join(stock_codes)}\n")
                f.write("板块名称=我的自选股\n")  # 固定名称或可替换为变量
                
            # 处理TV格式输出
            with open(txt_path, 'w', encoding='gbk') as f:
                f.write(','.join(tv_codes))  # 只写入前999个
                
            # 更新统计信息
            tv_count = len(tv_codes)
            print(f"成功转换：{base_name}（共处理{total_rows}行，有效代码{len(stock_codes)}个，TV截取前{tv_count}个）")
            
        except KeyError:
            print(f"错误：文件 {os.path.basename(file_path)} 缺少'股票代码'列")
        except Exception as e:
            print(f"处理 {os.path.basename(file_path)} 失败：{str(e)}")

# 使用示例
batch_xls_to_ths()