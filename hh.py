import pandas as pd
from datetime import date, timedelta
import streamlit as st
import plotly.graph_objs as go
import lxml
import averagetemplist as atl

amedas_l = ['気仙沼', '川渡', '築館', '志津川', '古川', '大衡', '鹿島台',
            '石巻', '新川', '仙台', '白石', '亘理', '米山', '塩釜', '駒ノ湯',
            '丸森', '名取', '蔵王', '女川']
city_l = ['仙台市', '青葉区', '宮城野区', '若林区', '太白区', '泉区', '白石市',
          '角田市', '蔵王町', '七ヶ宿町', '大河原町', '村田町', '柴田町', '川崎町',
          '丸森町', '名取市', '岩沼市', '亘理町', '山元町', '塩釜市', '多賀城市',
          '富谷市', '松島町', '七ヶ浜町', '利府町', '大和町', '大郷町', '大衡村',
          '大崎市', '色麻町', '加美町', '涌谷町', '美里町', '栗原市', '登米市',
          '石巻市', '東松島市', '女川町', '気仙沼市', '南三陸町']

st.set_page_config(page_title='稲刈り行こうぜ！', page_icon='icon.ico')
st.title('稲刈り行こうぜ！')
st.caption('水稲の収穫適期を予測するアプリですφ(..)メモメモ')
st.text('積算気温から、ひとめぼれの収穫適期を予測します。')
st.text('実際の収穫のタイミングは、籾の黄化の程度を見て、判断してください。')
if st.button('アプリの説明～まずはここを読んでから！'):
    st.switch_page('pages/readme.py')
st.subheader('エラー情報')
st.text('R7.7.29 出穂日に一昨日の日付を入れるとエラーが出ます。現在、原因解明中です。')
with st.form(key='input_form'):
    st.header('入力フォーム')
    a_area = st.selectbox('アメダス地点の選択', amedas_l, index=9)
    city = st.selectbox('市町村の選択', city_l)
    begin_date = st.date_input('出穂日（ほ場全体の50％が出穂した日）') + timedelta(
        days=1)
    years = st.text_input('平年値とするデータの年数（直近〇か年）※数字のみ')
    submit_button = st.form_submit_button(label='予測開始')

if submit_button:
    ave_temp_series = atl.ave_temp_list(a_area, city, begin_date, 60,
                                        int(years))
    cum_temp_series = ave_temp_series.cumsum()
    df_chart = pd.DataFrame({
        '平均気温': ave_temp_series,
        '積算平均気温': cum_temp_series
    })

    # 940〜1100℃に該当する行を抽出
    mask = (df_chart['積算平均気温'] >= 940) & (
                df_chart['積算平均気温'] <= 1100)
    # 該当期間の開始・終了日を取得
    highlight_dates = df_chart[mask].index
    if not highlight_dates.empty:
        start_date = highlight_dates[0]
        end_date = highlight_dates[-1]

    st.header('予測結果')

    fig = go.Figure()
    # 平均気温グラフ（左軸）
    fig.add_trace(go.Scatter(
        x=df_chart.index,
        y=df_chart['平均気温'],
        name='平均気温',
        line=dict(color='green'),
        yaxis='y1'
    ))
    # 積算平均気温グラフ（右軸）
    fig.add_trace(go.Scatter(
        x=df_chart.index,
        y=df_chart['積算平均気温'],
        name='積算平均気温',
        line=dict(color='orange'),
        yaxis='y2'
    ))
    fig.add_shape(
        type="line",
        x0=0, x1=1,
        xref="paper",
        y0=27, y1=27,
        yref="y",  # y1 に対応している
        line=dict(color="lime", dash="dot")
    )
    fig.add_shape(
        type="rect",
        x0=0, x1=1,
        xref="paper",
        y0=940, y1=1100,
        yref="y2",  # y2 が積算平均気温の軸
        fillcolor="yellow",
        opacity=0.2,
        layer="below",
        line_width=0
    )
    fig.add_shape(
        type="rect",
        x0=start_date,
        x1=end_date,
        xref="x",  # x軸は日付
        y0=0,
        y1=1,
        yref="paper",  # yはグラフ全体を覆うように
        fillcolor="rgba(255, 102, 146, 0.3)",
        layer="below",
        line_width=0
    )
    fig.update_layout(
        xaxis=dict(title='日付'),
        yaxis=dict(
            title='平均気温（℃）',
            range=[15, 35],
            dtick=5,
            showgrid=False
        ),
        yaxis2=dict(
            title='積算平均気温（℃）',
            overlaying='y',
            side='right',
            range=[0, 1500],
            dtick=100,
            showgrid=False
        ),
        legend=dict(x=0.05, y=0.95),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)
    st.text('出穂後の平均気温')
    st.dataframe(df_chart, width=270)
