import numpy as np
import pickle
import tkinter as tk
from tkinter import messagebox

def feature_num():
    """定义特征数量"""
    return 10

def calculate(*args):
    """执行计算并处理输入验证"""
    input_str = input_var.get()

    # 分割输入字符串
    numbers = input_str.split()

    # 输入验证
    if len(numbers) != feature_num():
        messagebox.showerror(" 格式错误", f"需要输入{feature_num()}个数字，用空格分隔！")
        return

    try:
        # 转换为浮点数列表
        nums = list(map(float, numbers))
    except ValueError:
        messagebox.showerror(" 格式错误", "包含非数字字符！")
        return

    # 筛选有效特征
    x_valid = numbers[0:2] + numbers[4:7]
    feature_num_valid = len(x_valid)

    # 执行计算
    x = np.array(x_valid).reshape(-1, feature_num_valid)
    x_std = sc_X['std_param'].transform(x)
    y_std = neu_model['model'].predict(x_std)
    y = sc_y['std_param'].inverse_transform(y_std.reshape(1, -1))[0][0]
    if y <= 330:
        predict_vol.set(f"预测电压：{round(y)} 伏")
        print(f'{neu_model['name']}模型预测值: {y}伏')
    else:
        predict_vol.set(f"{neu_model['name']}模型预测失败！！！")

def clear_output(*args):
    """清空输出"""
    predict_vol.set('')

def clear_input(*args):
    """清空输出"""
    input_var.set('')

# 加载缩放器
with open('../res/sc_X.pkl', 'rb') as f:
    sc_X = pickle.load(f)

with open('../res/sc_y.pkl', 'rb') as f:
    sc_y = pickle.load(f)

# 加载神经网络模型
with open('../res/opto_predict_neu.pkl', 'rb') as f:
    neu_model = pickle.load(f)

# 创建主窗口
root = tk.Tk()
root.title('北扶-电压预测工具')
root.geometry('900x250+500+300')
root.iconphoto(False, tk.PhotoImage(file='../res/北扶logo图标.png'))

# 输入区域
tk.Label(root, text=f"请输入{feature_num()}个表示皮肤特征的数值（空格分隔）：", font=('微软雅黑', 12)).pack(pady=10)
input_var = tk.StringVar()
entry_input = tk.Entry(root, textvariable=input_var, width=90, justify='center', font=('Arial', 12))
input_var.trace('w', clear_output)
entry_input.bind('<Return>', calculate)
entry_input.pack()

# 操作按钮
fr_opr_btn = tk.Frame(root, relief='flat', borderwidth=1)
fr_opr_btn.pack(anchor='center')
btn_clr = tk.Button(fr_opr_btn, text="清空", command=clear_input, width=10, font=('微软雅黑', 13))
btn_clr.grid(row=0, column=0, padx=15, pady=15)
btn_calculate = tk.Button(fr_opr_btn, text="计算", command=calculate, width=10, font=('微软雅黑', 13))
btn_calculate.grid(row=0, column=1, padx=15, pady=15)

# 输出区域
predict_vol = tk.StringVar()
tk.Entry(root, textvariable=predict_vol, state='readonly', relief='flat', justify='center',font=('微软雅黑', 13)).pack(pady=10)

# 分割线
tk.Frame(root, height=2, borderwidth=1, relief='groove').pack(fill='x', padx=10, pady=10)

# 模型信息
fr_model_info = tk.Frame(root, relief='flat', borderwidth=1)
fr_model_info.pack(anchor='center')
tk.Label(fr_model_info, text='Author: '+neu_model['author']).grid(row=0, column=0)
tk.Label(fr_model_info, text='Algorithm: '+neu_model['name']).grid(row=0, column=1, padx=30)
tk.Label(fr_model_info, text='Update: '+str(neu_model['timestamp'].replace(microsecond=0))).grid(row=0, column=2)

root.resizable(width=False, height=False)
root.mainloop()