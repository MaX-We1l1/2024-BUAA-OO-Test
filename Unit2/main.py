import os
import sys
from checker import check
from checker import input_check
from checker import output_check

# 创建一个线程列表
threads = []
# print("生成数据中")
os.system("python data_gen.py")
# print("生成完成，准备测评")
# 创建并启动评测线程
input_file = "datainput_student_win64.exe"
jar_file = f"code.jar"
output_file = f"output.txt"

cmd = f"{input_file} | java -jar {jar_file} > {output_file}"
os.system(cmd)
input = input_check('stdin.txt')
output = output_check('output.txt')
print(check(input, output))
sys.exit()


