import os
import shutil

class FileMover:
    def move_file(self, src, dest):
        if not os.path.isfile(src):
            raise FileNotFoundError(f"源文件 {src} 不存在")
        
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        
        shutil.move(src, dest)
        print(f"文件已移动到 {dest}")

# example usage
if __name__ == "__main__":
    mover = FileMover()
    try:
        mover.move_file('./data/combined/combined.txt', './ragtest/input/combined.txt')
    except Exception as e:
        print(e)