import pandas as pd
import os
# only for csv and xlsx test

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
            print(f"sheet '{sheet_name}' stored into: {csv_file_path}")


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
                # process the number below
                next_index = index + 1
                while next_index < len(df) and pd.isna(df.at[next_index, 0]):
                    self._process_row(df, next_index, df.iloc[next_index])
                    next_index += 1

        df.to_csv(file_path, index=False, header=False)
        print(f"file '{file_path}' stored")

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
                # change NaN to fill_value
                df.fillna(self.fill_value, inplace=True)
                # use | to separate columns
                all_text += df.to_csv(sep=self.sep, header=False,
                                      index=False) + "\n"

        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(all_text)
        print(f"all CSV file connected and stored into: {self.output_file}")


if __name__ == "__main__":
    excel_file_path = "./data/input_file/example.xlsx"
    output_dir = "./data/table_csv"
    result_file = "./data/combined/combined.txt"
    columns_to_process = [1, 2]

    if os.path.exists(excel_file_path):
        excel_converter = ExcelToCSVConverter(excel_file_path, output_dir)
        excel_converter.convert()
        print(f"all table stored into: {output_dir}")
    else:
        print(f"file not exist: {excel_file_path}")

    csv_processor = CSVProcessor(output_dir, columns_to_process)
    csv_processor.process_csv_files()
    print(f"all CSV files processed")

    txt_converter = CSVToTextConverter(output_dir, result_file)
    txt_converter.convert()
