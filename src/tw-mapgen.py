import tkinter as tk
from create_layered import create_layered
from pathlib import Path


config = [
    ('filename', str(Path.cwd().joinpath('newmap.map')), str),
    ('base map size', '300', int),
    ('block length (max tunnel size)', '20', int),
    ('min wall thickness (per side)', '1', int),  # on each side
    ('max wall thickness (per side)', '5', int), # on each side
    ('wall thickness change probability', '0.15', float),
    ('obstacle grow length', '11', int),  # has be be less than sqrt(0.5) * blocklen - 2
    ('obstacle size', '5', int),
    ('obstacle side switch probability', '0.8', float),
    ('obstacle direction change probability', '0.4', float),
    ('obstacle freeze probability', '0.8', float),
    ('block wall (game layer)', '1', int),
    ('block corner (game layer)', '1', int),
    ('block obstacle (game layer)', '1', int),
    ('block freeze (game layer)', '9', int),
    ('directions (0:left, 1:up, 2:right, 3:down)', '2,2,2,3,3,3,2,1,1,1,2,2,3,3,3,2,1,1,1,2,2,2,2', lambda x: list(map(int,x.split(',')) if x.strip() else None))  # directions to build along
]


# window
window = tk.Tk()
window.title('Teeworlds Map Generator')
# window.geometry("1400x1200")

# header
tk.Label(text='enter settings below and hit generate').pack()

# inputs
frame = tk.Frame()
entries = []
for i, (text, default, t) in enumerate(config):
    label = tk.Label(text=text, master=frame)
    label.grid(row=i, column=0, padx=10, pady=10, sticky='e')
    entry = tk.Entry(master=frame)
    entry.insert(tk.END, default)
    entry.grid(row=i, column=1, padx=10, pady=10, sticky='ew')
    entries.append(entry)
frame.columnconfigure(0,weight=0)
frame.columnconfigure(1,weight=1)
frame.pack(fill=tk.BOTH, expand=True)

# generate
status_label = None
def generate(*args):
    try:
        create_layered(*[t(x.get()) for x, (text, default, t) in zip(entries, config)])
        result = 'success!'
    except Exception as e:
        result = f'error: {e}'
    print(result)
    status_label['text'] = result
button = tk.Button(text="generate", command=generate)
button.pack()
status_label = tk.Label()
status_label.pack()


# mainloop
window.mainloop()
