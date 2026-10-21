import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.ticker import FuncFormatter

base_dir = os.path.dirname(os.path.abspath(__file__))
file_path = next((os.path.join(base_dir, f) for f in ['abc.csv', 'abc-8.csv', 'abc-8.csv.csv'] if os.path.exists(os.path.join(base_dir, f))), None)
if not file_path: exit(print("Không tìm thấy file dữ liệu!"))

df = pd.read_csv(file_path, header=None)
df.columns = ['Open', 'P1', 'P2', 'P3', 'P4', 'P5', 'Close']

ref = np.concatenate([[10000.0], df['Close'].iloc[:-1].values])
flr, cel, means = 0.9 * ref, 1.1 * ref, df.mean(axis=1).values
months = np.repeat(np.arange(1, 13), [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
quarters = pd.Series(np.ceil(months / 3).astype(int))

def get_color(i):
    op = df.loc[i, 'Open']
    cl = df.loc[i, 'Close']
    return 'limegreen' if cl >= op else 'red'

m_rows = [{'Tháng': m, 'Giá TB': np.mean(sub := df[months == m].values), 'Độ lệch chuẩn': np.std(sub, ddof=1), 'Min': np.min(sub), 'Max': np.max(sub)} for m in range(1, 13)]
m_df = pd.DataFrame(m_rows)
print("=== THỐNG KÊ THÁNG ===\n", m_df.to_string(index=False))

q_rows = [{'Quý': f'Quý {q}', 'Giá TB': np.mean(sub := df[quarters == q].values), 'Độ lệch chuẩn': np.std(sub, ddof=1), 'Min': np.min(sub), 'Max': np.max(sub)} for q in range(1, 5)]
print("=== THỐNG KÊ QUÝ ===\n", pd.DataFrame(q_rows).to_string(index=False))

plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7.2), sharex=True)
formatter = FuncFormatter(lambda y, _: f'{int(y):,}')

for ax in (ax1, ax2):
    ax.set_facecolor('black')
    ax.set_xlim(-2, 395)
    ax.set_ylim(-500, 21000)
    ax.set_ylabel('VND', color='white', fontsize=11)
    ax.yaxis.set_major_formatter(formatter)
    ax.set_yticks([0, 5000, 10000, 15000, 20000])
    ax.set_xticks(np.arange(0, 361, 30))
    for s in ax.spines.values(): s.set_color('white')

ax2.set_xlabel('Date', color='white', fontsize=11)

l_mean, = ax2.plot([], [], color='limegreen', lw=1.5, zorder=3)
fill_artist = None

hline_max = ax2.axhline(means[0], color='limegreen', ls=':', lw=1.2, alpha=0)
hline_min = ax2.axhline(means[0], color='red', ls=':', lw=1.2, alpha=0)
hline_cur = ax2.axhline(means[0], color='gray', ls='-', lw=0.6, alpha=0.5)

txt_max = ax2.text(367, means[0], '', color='limegreen', fontsize=9, va='center')
txt_min = ax2.text(367, means[0], '', color='red', fontsize=9, va='center')
txt_cur = ax2.text(0, means[0], '', color='red', fontsize=9.5, va='center')

def update(day):
    global fill_artist
    
    ax1.clear()
    ax1.set_facecolor('black')
    ax1.set_xlim(-2, 395)
    ax1.set_ylim(-500, 21000)
    ax1.set_ylabel('VND', color='white', fontsize=11)
    ax1.yaxis.set_major_formatter(formatter)
    ax1.set_yticks([0, 5000, 10000, 15000, 20000])
    for s in ax1.spines.values(): s.set_color('white')
    
    for box_idx in range(0, day + 1, 4):
        if box_idx < len(df):
            blk = df.iloc[box_idx:min(box_idx+4, len(df))].values.flatten()
            q25, med, q75 = np.percentile(blk, [25, 50, 75])
            col = get_color(box_idx)
            ax1.plot([box_idx+1, box_idx+1], [np.min(blk), np.max(blk)], color=col, lw=1.8)
            ax1.add_patch(plt.Rectangle((box_idx - 0.2, q25), 2.4, q75 - q25, facecolor=col, edgecolor=col, alpha=0.85))
            ax1.plot([box_idx - 0.2, box_idx + 2.2], [med, med], color='white', lw=1.5)
        
    x = np.arange(day + 1)
    y_mean = means[:day + 1]
    y_min_daily = df.iloc[:day + 1].min(axis=1).values
    y_max_daily = df.iloc[:day + 1].max(axis=1).values
    
    col = get_color(day)
    
    if fill_artist is not None:
        fill_artist.remove()
            
    fill_artist = ax2.fill_between(x, y_min_daily, y_max_daily, color='olive', alpha=0.4, zorder=2)
    l_mean.set_data(x, y_mean)
    l_mean.set_color('red' if col == 'red' else 'limegreen')
    
    c_max, c_min, c_val = np.max(y_mean), np.min(y_mean), y_mean[-1]
    
    hline_max.set_ydata([c_max, c_max])
    hline_max.set_alpha(0.7)
    hline_min.set_ydata([c_min, c_min])
    hline_min.set_alpha(0.7)
    hline_cur.set_ydata([c_val, c_val])
    
    txt_max.set_position((367, c_max)); txt_max.set_text(f'{c_max:,.0f}')
    txt_min.set_position((367, c_min)); txt_min.set_text(f'{c_min:,.0f}')
    txt_cur.set_position((day + 4, c_val)); txt_cur.set_text(f'{c_val:,.0f}')
    txt_cur.set_color('red' if col == 'red' else 'limegreen')
    
    return l_mean, fill_artist, hline_max, hline_min, hline_cur, txt_max, txt_min, txt_cur

ani = animation.FuncAnimation(fig, update, frames=len(df), interval=200, blit=False, repeat=False)
plt.tight_layout()

print("Đang tiến hành xuất và lưu video mô phỏng ra file 'simulation_abc.mp4'...")
try:
    ani.save('simulation_abc.mp4', writer='ffmpeg', fps=2, dpi=150)
    print("Đã lưu thành công file video: simulation_abc.mp4!")
except Exception as e:
    print(f"Lỗi khi lưu video: {e}")

plt.show()