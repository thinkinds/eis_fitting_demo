import re

import numpy as np
import streamlit as st
from impedance import preprocessing
from impedance.models.circuits import CustomCircuit
import plotly.graph_objects as go
from schemdraw import Drawing

from circuits_draw import draw_circuit

guess_dict = {
    'R': [.01],
    'L': [1e-7],
    'C': [.1],
    'CPE':[1e-4, .8],
    'W':  [.1],
    'Wo': [0.05, 1],
    'Ws': [0.05, 1],
}

st.title('EIS等效电路模型拟合')
st.markdown('''
EIS文件格式要求：
* 现仅支持csv格式
* csv文件中三列数据分别对应频率、阻抗的实部、虚部，不能有标题行
''')

# 文件上传器
uploaded_file = st.file_uploader("Choose an EIS file...", type=["csv"])

frequencies = None
Z = None

# Model : R0-(L3//R3)-(CPE1//R1)-(CPE2//R2)-W1
# circuit = 'R_0-p(L_3,R_3)-p(CPE_1,R_1)-p(CPE_2,R_2)-Wo_1'
circuit = st.text_input('请输入电路描述字符串，"-"表示串联，P(x, y)表示两条并联支路', 'R_0-p(L_3,R_3)-p(CPE_1,R_1)-p(CPE_2,R_2)-Wo_1')
# st.image('circuit_diagram.png', caption='等效电路模型')
with Drawing(file='temp_circuit_diagram.svg', show=False) as dwg:
    draw_circuit(circuit, dwg)
    image_bytes = dwg.get_imagedata('svg')
st.image('temp_circuit_diagram.svg', use_column_width=True, caption='等效电路模型示意图')

# make init guess for fitting
# Find all matches
comp_type_list = re.findall(r'\b(R|C|W|Wo|Ws|L|CPE)_?\d*\b', circuit)
initial_guess = []
for c_type in comp_type_list:
    initial_guess.extend(guess_dict[c_type])
# initial_guess = [.01, 1e-7, .1, .1, .1, .01, 1, 1, 1, .01, 1]
# initial_guess

if uploaded_file is not None:
    frequencies, Z = preprocessing.readCSV(uploaded_file)
# else:
#     # Load data from the example EIS data
#     frequencies, Z = preprocessing.readCSV('./exampleData.csv')

# keep only the impedance data in the first quandrant
# frequencies, Z = preprocessing.ignoreBelowX(frequencies, Z)


if frequencies is not None:
    circuit = CustomCircuit(circuit, initial_guess=initial_guess)

    circuit.fit(frequencies, Z)

    Z_fit = circuit.predict(frequencies)

    # plot result using plotly
    # 拆分实部和虚部
    real_Z = Z.real
    imag_Z = -Z.imag

    real_Z_fit = Z_fit.real
    imag_Z_fit = -Z_fit.imag

    # 创建点线图
    fig = go.Figure()

    # 添加第一个复数数组的点线
    fig.add_trace(go.Scatter(x=real_Z, y=imag_Z, mode='markers', name='测量值'))

    # 添加第二个复数数组的点线
    fig.add_trace(go.Scatter(x=real_Z_fit, y=imag_Z_fit, mode='markers', name='拟合值'))

    # 设置图表布局
    fig.update_layout(title='Nyquist(Cole-Cole) Plot',
                      xaxis_title='Impedance Real Part [Ω]',
                      yaxis_title='-Impedance Imaginary Part [Ω]')

    # 调整布局使 x 和 y 轴比例一致
    fig.update_layout(xaxis=dict(scaleanchor="y", scaleratio=1),
                      yaxis=dict(scaleanchor="x", scaleratio=1))

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.header("奈奎斯特图")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.header("拟合参数")
        st.text(f'等效电路模型（-串联，p并联）： {circuit.circuit}')

        param_names, param_units = circuit.get_param_names()
        zipped = zip(param_names, param_units, circuit.parameters_)
        for param in zipped:
            st.text(f'{param[0]}: {param[2]}[{param[1]}]')

        errors_abs = np.abs(Z_fit - Z)
        rmse = np.sqrt(np.mean(np.square(errors_abs)))
        st.text(f'RMSE: {rmse}[Ohm]')

