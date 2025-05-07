import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import math

# Daire şeklinde kesir çizme fonksiyonu
def draw_circle_fraction(ax, total_parts, filled_parts, color):
    sizes = [1] * filled_parts + [1] * (total_parts - filled_parts)
    colors = [color] * filled_parts + ['white'] * (total_parts - filled_parts)
    ax.pie(sizes, colors=colors, startangle=90,
           wedgeprops={'edgecolor': 'black', 'linewidth': 2})
    ax.set_aspect('equal')

# Dikdörtgen şeklinde kesir çizme fonksiyonu
def draw_rect_fraction(ax, total_parts, filled_parts, color):
    part_width = 1 / total_parts
    for i in range(total_parts):
        filled = i < filled_parts
        rect = Rectangle((i * part_width, 0), part_width, 1,
                         facecolor=color if filled else 'white',
                         edgecolor='black', linewidth=2)
        ax.add_patch(rect)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')

# Şekil türüne göre uygun fonksiyonu seçme ve başlık ekleme
def draw_fraction(ax, total_parts, filled_parts, color, shape='rect', title=''):
    if shape == 'circle':
        draw_circle_fraction(ax, total_parts, filled_parts, color)
    else:
        draw_rect_fraction(ax, total_parts, filled_parts, color)

    if title:
        ax.set_title(title, fontsize=18, fontweight='bold')

# Parametrik kesirler için diagram oluşturma fonksiyonu
def create_fraction_diagram(fractions):
    fig, axs = plt.subplots(1, len(fractions), figsize=(5 * len(fractions), 4))

    if len(fractions) == 1:
        axs = [axs]

    for i, (ax, frac) in enumerate(zip(axs, fractions)):
        title = frac.get('title', f"Şekil {i + 1}")
        draw_fraction(
            ax,
            total_parts=frac['total'],
            filled_parts=frac['filled'],
            color=frac.get('color', '#3498db'),
            shape=frac.get('shape', 'rect'),
            title=title
        )

    plt.tight_layout()
    plt.savefig('parametrik_kesirler.png', dpi=150, bbox_inches='tight')
    plt.close()

# Parametrik kesirler listesi
fractions = [
    {
        'filled': 1,
        'total': 6,
        'shape': 'circle',
        'color': '#3498db',
        'title': 'G Kesri'
    },
    {
        'filled': 3,
        'total': 4,
        'shape': 'rect',
        'color': '#e67e22',
        'title': 'h Kesri'  # 8/10 kesiri
    },
    {
        'filled': 3,
        'total': 6,
        'shape': 'rect',
        'color': '#2ecc71',
        'title': 'H Kesri'
    }
]

# Çalıştır
create_fraction_diagram(fractions)
