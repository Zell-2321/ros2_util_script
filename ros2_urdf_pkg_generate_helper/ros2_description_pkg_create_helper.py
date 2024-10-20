import os
import re
import subprocess
from typing import AnyStr, List

count = 0

def get_ws_path() -> AnyStr:
    user_input = input("请输入你的工作空间绝对路径，如果为 ~/ros2_ws 可直接回车。Please enter the absolute path of your workspace. If it is ~/ros2_ws, you can press Enter directly: ")
    if user_input == '':
        ros2_ws_path = '~/ros2_ws'
        ros2_ws_path = os.path.expanduser(ros2_ws_path)
    elif user_input[0] == '~':
        ros2_ws_path = os.path.expanduser(user_input)
    else:
        ros2_ws_path = user_input

    if not os.path.exists(ros2_ws_path):
        print("路径不存在，请检查。The path does not exist, please check.")
        return get_ws_path()

    return ros2_ws_path

def get_pkg_name() -> AnyStr:
    name = input("请输入你要创建的包的名称，例如：my_robot_description。Please enter the name of the package you want to create, such as: my_robot_description: ")
    global count
    valid_name_pattern = re.compile(r'^[a-z][a-z0-9_]*$')

    while not valid_name_pattern.match(name):
        print("包名不符合规范")
        name = re.sub(r'[^a-z0-9_]', '', name)
        if not name or name[0].isdigit():
            if count > 3:
                exit()
            count += 1
            name = get_pkg_name()
        else:
            print(f"去除不满足的符号后的包名: {name}")
            break

    return name

def get_pkg_type() -> AnyStr:
    typ = input("你想创建哪一种包 \n [0]: python \n [1]: c++ \n [2]: c++ 跨平台(非ROS包): ")
    global count
    if typ == '0':
        return 'ament_python'
    elif typ == '1':
        return 'ament_cmake'
    elif typ == '2':
        return 'cmake'
    else:
        if count > 3:
            exit()
        print("请从0-2中选择。Please enter from 0-2.")
        count += 1
        return get_pkg_type()

def get_pkg_parameters() -> dict:
    print("可选参数: parameters:")
    print("[0]: --library-name")
    print("[1]: --node-name")
    print("[2]: --dependencies")
    print("[3]: --license")
    print("[4]: --description")
    print("[5]: --maintainer-email")
    print("[6]: --maintainer-name")
    print("[7]: --destination-directory")
    global count

    user_input = input("请输入需要设置的参数编号（使用空格分隔） (手动设置 使用默认值)。输入不需要的参数时可使用 'x' 来替代（例如: x 234)。: " +
                       "Please enter the parameter numbers you want to set(manually set/ using default value), separated by spaces. You can use 'x' to indicate parameters you do not need (e.g., x 234):")
    selected_params = user_input.split()

    if len(selected_params) != 2 or len(selected_params[0]) == 0 or len(selected_params[1]) == 0:
        if count > 3:
            exit()
        print("参数输入错误，请重新输入。Parameter input error, please re-enter.")
        count += 1
        return get_pkg_parameters()
    valid_num = [[],[]]
    i = 0
    for element in selected_params:
        for ele in element:
            if ele != "x" and ele != "0" and ele != "1" and ele != "2" and ele != "3" and ele != "4" and ele != "5" and ele != "6" and ele != "7":
                if count > 3:
                    exit()
                else:
                    print("[Error_type2]:参数输入错误，请重新输入。Parameter input error, please re-enter.")
                    count += 1
                    return get_pkg_parameters()
            else:
                if ele == "x":
                    continue
                else:
                    valid_num[i].append(ele)
        i += 1

    params = {}
    defaults = {
        '--library-name': '',
        '--node-name': 'default_node_name',
        '--dependencies': '',
        '--license': 'MIT',
        '--description': 'This is a package.',
        '--maintainer-email': 'you@example.com',
        '--maintainer-name': 'Your Name',
        '--destination-directory': ''
    }
    print(len(valid_num[0]), len(valid_num[1]))
    # 默认参数
    if len(valid_num[0]) > 0: 
        for i in valid_num[0]:
            param_key = list(defaults.keys())[int(i)]
            params[param_key] = defaults[param_key]

    # 手动设置
    if len(valid_num[1]) > 0: 
        for i in valid_num[1]:
            param_key = list(defaults.keys())[int(i)]
            params[param_key] = input(f"请输入 {param_key} (默认: {defaults[param_key]}): ") or defaults[param_key]

    return params

# 执行命令时处理带空格的参数
def execute_command(command, ros2_ws_path):
    print(f"创建包的命令: {' '.join(command)}")
    result = subprocess.run(command, cwd=ros2_ws_path, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("包创建成功:")
        print(result.stdout)
    else:
        print("包创建失败:")
        print(result.stderr)

def test_function() -> None:
    pass
    # a = get_pkg_parameters()
    print(get_pkg_parameters())

def package_create_agent():
    print("这是一个帮助你创建标准机器人模型ROS2包的脚本。This is a script that helps you to create a standard ROS2 robot description pkg.")
    print("请确认你是ROS2 humble, 其他版本暂未测试。Please make sure you are using ROS2 humble, other versions have not been tested.")

    # 获取工作空间路径
    ros2_ws_path = get_ws_path()

    # 检查是否在这一路径下存在src文件夹，如果不存在则创建
    src_path = os.path.join(ros2_ws_path, 'src')
    if not os.path.exists(src_path):
        print(f"'{src_path}' 文件夹不存在，正在创建... folder does not exist and is being created.")
        os.makedirs(src_path)
        print("src 文件夹创建成功。successfully created src folder.")

    command = ['ros2', 'pkg', 'create']
    
    global count
    count = 0
    name = get_pkg_name()
    
    count = 0
    typ = get_pkg_type()

    # 获取用户参数
    count = 0
    params = get_pkg_parameters()

    # 构建命令
    command.extend([name, '--build-type', typ])

    for param, value in params.items():
        if param != '--dependencies':
            if value:  # 如果有值，添加到命令中
                command.extend([param, value])
    if '--dependencies' in params.keys():
        print("ccc")
        dep_list = params['--dependencies'].split()
        command.extend(['--dependencies'])
        for dep in dep_list:
            command.extend([dep])


    execute_command(command, src_path)


if __name__ == "__main__":
    package_create_agent()
    # test_function()
