import pandas as pd
import os


class ExcelToCSVConverter:
    def __init__(self, excel_file_path, output_dir):
        self.excel_file_path = excel_file_path
        self.output_dir = output_dir

    def convert(self):
        xls = pd.ExcelFile(self.excel_file_path)

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for sheet_name in xls.sheet_names:
            df = pd.read_excel(self.excel_file_path, sheet_name=sheet_name)
            csv_file_path = os.path.join(self.output_dir, f"{sheet_name}.csv")
            # write to csv
            df.to_csv(csv_file_path, index=False)
            print(f"工作表 '{sheet_name}' 已保存到: {csv_file_path}")


class CSVProcessor:
    def __init__(self, input_dir, columns_to_process=None):
        self.input_dir = input_dir
        self.columns_to_process = columns_to_process if columns_to_process else []

    def process_csv_files(self):
        for file_name in os.listdir(self.input_dir):
            if file_name.endswith('.csv'):
                file_path = os.path.join(self.input_dir, file_name)
                self.process_csv(file_path)

    def process_csv(self, file_path):
        df = pd.read_csv(file_path, header=None)
        days_of_week = ['星期一', '星期二', '星期三', '星期四', '星期五']

        for index, row in df.iterrows():
            if row[0] in days_of_week:
                self._process_row(df, index, row)
                # 处理下面对应位置的数字
                next_index = index + 1
                while next_index < len(df) and pd.isna(df.at[next_index, 0]):
                    self._process_row(df, next_index, df.iloc[next_index])
                    next_index += 1

        df.to_csv(file_path, index=False, header=False)
        print(f"文件 '{file_path}' 已处理并保存")

    def _process_row(self, df, index, row):
        for col in range(1, len(row)):
            if self.columns_to_process and col not in self.columns_to_process:
                continue
            if pd.notna(row[col]) and isinstance(row[col], str) and row[col].isdigit():
                df.at[index, col] = f"第{row[col]}节"


class CSVToTextConverter:
    def __init__(self, input_dir, output_file, fill_value=" ", sep="|"):
        self.input_dir = input_dir
        self.output_file = output_file
        self.fill_value = fill_value
        self.sep = sep

    def convert(self):
        all_text = ""
        for file_name in os.listdir(self.input_dir):
            if file_name.endswith('.csv'):
                file_path = os.path.join(self.input_dir, file_name)
                df = pd.read_csv(file_path, header=None)
                # 将 NaN 值替换为指定的 fill_value
                df.fillna(self.fill_value, inplace=True)
                # 使用自定义分隔符 | 将 DataFrame 转换为字符串
                all_text += df.to_csv(sep=self.sep, header=False,
                                      index=False) + "\n"

        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(all_text)
        print(f"所有 CSV 文件已连接并保存到: {self.output_file}")


if __name__ == "__main__":
    excel_file_path = "./data/table-csv/input-table/example.xlsx"
    output_dir = "./data/table-csv"
    result_file = "./data/table-csv/combined/combined.txt"
    columns_to_process = [1, 2]

    if os.path.exists(excel_file_path):
        excel_converter = ExcelToCSVConverter(excel_file_path, output_dir)
        excel_converter.convert()
        print(f"转换成功，所有工作表已保存到目录: {output_dir}")
    else:
        print(f"文件不存在: {excel_file_path}")

    csv_processor = CSVProcessor(output_dir, columns_to_process)
    csv_processor.process_csv_files()
    print(f"所有 CSV 文件已处理并保存")

    txt_converter = CSVToTextConverter(output_dir, result_file)
    txt_converter.convert()
