import matplotlib.pyplot as plt
import io, matplotlib

matplotlib.use('Agg') 

def generate_weekly_graph(weekly_data):
    days = []
    temps_max = []
    temps_min = []

    weekdays_map = {
        0: "Понедельник", 1: "Вторник", 2: "Среда", 3: "Четверг", 
        4: "Пятница", 5: "Суббота", 6: "Воскресенье"
    }

    for day in weekly_data['days']:
        wd = weekdays_map[day['date'].weekday()]
        d_str = day['date'].strftime('%d.%m')
        days.append(f"{wd}\n{d_str}")
        
        temps_max.append(day['temp_max'])
        temps_min.append(day['temp_min'])

    fig, ax = plt.subplots(figsize=(10, 5), facecolor='#2b2b2b')
    ax.set_facecolor('#2b2b2b')

    ax.plot(days, temps_max, marker='o', color='#993463', linewidth=3, label='Max')
    ax.plot(days, temps_min, marker='o', color='#7376ba', linewidth=3, label='Min')

    ax.grid(visible=True, axis='y', linestyle='--', alpha=0.5, color='#59396e')
    ax.grid(visible=True, axis='x', linestyle='--', alpha=0.5, color='#59396e')
    ax.set_axisbelow(True)

    ax.spines['top'].set_visible(True)
    ax.spines['top'].set_color('#59396e')
    ax.spines['top'].set_linewidth(1)

    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color('#59396e')
    ax.spines['bottom'].set_linewidth(1)

    ax.spines['right'].set_visible(False)

    ax.spines['left'].set_visible(True)
    ax.spines['bottom'].set_color('#59396e')
    ax.spines['bottom'].set_linewidth(1)

    ax.tick_params(axis='x', colors='#aaaaaa', labelsize=10, top=False, bottom=True)
    ax.tick_params(axis='y', colors='#aaaaaa', labelsize=10, left=False)

    for i, temp in enumerate(temps_max):
        ax.text(i, temp + 0.8, f"{temp}°", ha='center', fontsize=11, fontweight='bold', color='#993463')

    for i, temp in enumerate(temps_min):
        ax.text(i, temp - 1.8, f"{temp}°", ha='center', fontsize=11, fontweight='bold', color='#7376ba')

    all_temps = temps_max + temps_min
    if all_temps:
        ax.set_ylim(min(all_temps) - 4, max(all_temps) + 6)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight', dpi=300)
    buf.seek(0)
    plt.close()

    return buf