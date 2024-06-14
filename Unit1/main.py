import os

os.system("java -jar code1.jar < input.txt > output1.txt")
os.system("java -jar code2.jar < input.txt > output2.txt")


def add_line_to_start_of_file(file_path, line_to_add):
    # 读取原始文件内容
    with open(file_path, 'r') as file:
        original_content = file.readlines()

    # 在开头添加新的一行内容
    new_content = [line_to_add + '\n'] + original_content

    # 将修改后的内容写回文件
    with open(file_path, 'w') as file:
        file.writelines(new_content)


def compare_files(file_path1, file_path2):
    with open(file_path1, 'r') as file1, open(file_path2, 'r') as file2:
        for line1, line2 in zip(file1, file2):
            if line1 != line2:
                return False

        # Check if one file has extra lines
        if file1.read() or file2.read():
            return False

    return True


file_path1 = 'output1.txt'
file_path2 = 'output2.txt'
line_to_add = '0'
add_line_to_start_of_file(file_path1, line_to_add)
add_line_to_start_of_file(file_path2, line_to_add)

os.system("java -jar code1.jar < output1.txt > ans1.txt")
os.system("java -jar code1.jar < output2.txt > ans2.txt")

if compare_files('ans1.txt', 'ans2.txt'):
    print("The ans are identical.")
else:
    print("The ans are different.")

