import math
import tkinter as tk
from tkinter import *
from tkinter import filedialog, font, simpledialog, scrolledtext, colorchooser
from PIL import ImageTk, Image, ImageFilter, ImageOps
import cv2
import numpy as np
from datetime import datetime

imagefile = ''
layout_arr = []
numcolor = '#FF0000'
numcolor_inv = '#00FFFF'
linecolor = '#00FF00'
linecolor_inv = '#FF00FF'
root = tk.Tk()
root.title("Custom Sprite Maker")
windowSize = (910,610)
root.geometry('' + str(windowSize[0]) + 'x' + str(windowSize[1]))
root.resizable(False, False)
startnum = 0
log = []
refresh = 0

def focus(event):
    event.widget.focus_set()
def cropTarget():
    precrop = cv2.cvtColor(np.array(image_padded), cv2.COLOR_RGBA2BGRA)
    cropped = precrop[target[1]:target[1] + image.size[1], target[0]:target[0] + image.size[0]]
    cropped_converted = cv2.cvtColor(cropped, cv2.COLOR_BGRA2RGBA)
    image_cropped = Image.fromarray(cropped_converted)
    return image_cropped
def upload(event):
    global imagefile
    global image
    global target
    global image_padded
    global split
    global refresh
    global startnum
    global canvas
    imagefile = filedialog.askopenfilename(title='Choose an image', filetypes=[('PNG', '.png')])    #Prompts user to select image
    if imagefile == '':   #Check if image was selected
        return 'break'
    image = Image.open(imagefile).convert('RGBA')   #Open image in RGBA mode for consistent alpha handling
    width, height = image.size   #Save image width and height
    #paletteMaker(image)   #Generate full image color palette
    image_padded = Image.new('RGBA', (3*width, 3*height), (255,255,255,0))   #Create transparent image 3x size of original
    image_padded.paste(image, (width, height))   #Paste original image in center so it is padded
    target = [width, height]   #Set top-left corner of crop box as top left of original image
    cropped = cropTarget()   #Retrieve image cropped from target box
    root.focus_set()   #Deselect text entry box
    scaler.set(1)   #Set default scale = 1 (resetting scaler widget)
    v.set(0)   #Deselect radio buttons for split size
    split = v.get()   #Set default split = 0
    gridbox.deselect()   #Deselect grid visibility
    v2.set(0)   #Set default save option
    refresh = 1   #Set default refresh state = 1
    startnum = 0   #Set default initial sprite number = 0
    inputtxt.delete(0, END)   #clear savename entry widget
    display = ImageTk.PhotoImage(cropped)   #Create display image
    f3.grid_rowconfigure(0, weight=1)
    f3.grid_columnconfigure(0, weight=1)
    xbar = Scrollbar(f3, orient=HORIZONTAL)
    xbar.grid(row=1, column=0, sticky='ew')
    ybar = Scrollbar(f3, orient=VERTICAL)
    ybar.grid(row=0, column=1, sticky='ns')
    canvas = Canvas(f3, width=576, height=480, bg='gray')
    canvas.grid(row=0, column=0, sticky='nsew')
    root.display = display
    canvas.create_image(2, 2, image=display, anchor='nw')
    canvas.config(scrollregion=canvas.bbox(ALL))
    xbar.config(command=canvas.xview)
    ybar.config(command=canvas.yview)
    make_label(root, 5 + int(frameSize[0] / 3), 5 + int(frameSize[1] / 8), int(frameSize[1] / 15 / 2), 600, text='canvas size: 576x480          image size: ' + str(image.size[0]) + 'x' + str(image.size[1]) + '          scaled size: ' + str(image.size[0] * scaleint.get()) + 'x' + str(image.size[1] * scaleint.get()), bg='silver', justify=LEFT)
    SetLines()
    return "break"
def paletteMaker(image_array):
    round_step = -4
    it = 0
    while True:
        it += 1
        if it == 2:
            round_step = 0
        round_step += 5
        rounded = np.copy(image_array).astype(np.int32)
        mask = rounded != 255
        if round_step > 0:
            rounded[mask] = ((rounded[mask] + (round_step // 2)) // round_step) * round_step
            np.clip(rounded, 0, 255, out=rounded)
        rounded = rounded.astype(np.uint8)
        pixels = np.unique(rounded.reshape(-1, 4), axis=0)
        colors = [[0, 0, 0, 0]] + [p.tolist() for p in pixels if p[3] != 0]
        if 0 < len(colors) <= 70:
            break
    return [[format(c[3], '08b')] + [format(v, '08b') for v in c[:3]] for c in colors], round_step


def byteMaker():
    global s_list
    global palette_data
    global layout
    global layout_arr
    global bytecount
    if imagefile == '':
        return 'break'
    # -----------------------------------------------------------------------------------
    # generate sprite byte data (auto split sprites into 16x16 or 32x32------------------
    num = startnum-1
    bytecount = 0
    xidx = 0
    yidx = 0
    layout = '}'

    img_array = np.array(cropped)
    img_width, img_height = cropped.size

    arr = [[None] * math.ceil(img_width / split) for _ in range(math.ceil(img_height / split))]
    s_list = []
    palette_list = []
    for yidx in range(math.ceil(img_height / split)):  # y index of subimage
        for xidx in range(math.ceil(img_width / split)):  # xindex of subimage
            num += 1
            s = ''
            sub_img_array = img_array[yidx * split:(yidx + 1) * split, xidx * split:(xidx + 1) * split]
            if sub_img_array.shape[0] != split or sub_img_array.shape[1] != split:
                continue
            palette, round_step = paletteMaker(sub_img_array)
            colors = {tuple(int(b, 2) for b in color): idx for idx, color in enumerate(palette)}

            rounded = np.copy(sub_img_array).astype(np.int32)
            mask = rounded != 255
            if round_step != 0:
                rounded[mask] = ((rounded[mask] + (round_step // 2)) // round_step) * round_step
                np.clip(rounded, 0, 255, out=rounded)
            rounded = rounded.astype(np.uint8)
            rounded[rounded[:, :, 3] == 0] = [0, 0, 0, 0]

            for i in range(split):
                for j in range(split):
                    color = rounded[i, j].tolist()
                    idx = colors.get((color[3], color[0], color[1], color[2]), 0)
                    if j == 0:
                        s += "}"
                    s += f"${idx:02x},"
                    if j == split - 1:
                        if i == split - 1:
                            s = s[:-1]
                        s += "{\n"
            s += "}\n"

            flag = any(val in s for val in '123456789abcdef')
            if flag:
                if s in s_list:  # Prevent inclusion of repeat sub sprites
                    layout += str(s_list.index(s)+startnum) + ",\t"
                    arr[yidx][xidx] = s_list.index(s) + startnum
                    num -= 1
                else:
                    bytecount += 1
                    s_list.append(s)
                    palette_list.append(palette)
                    layout += str(s_list.index(s)+startnum) + ",\t"
                    arr[yidx][xidx] = s_list.index(s) + startnum
                if yidx == math.ceil(img_height / split) - 1 and xidx == math.ceil(img_width / split) - 1:
                    layout = layout[:-2]
            else:
                layout += "--\t"
        layout += "{\n}"
    palette_data = []
    for palette in palette_list:
        palette_str = ''
        for idx, color in enumerate(palette):
            if idx < len(palette) - 1:  # Only add a comma if it's not the last element
              binary_str = "}%" + "_".join(color) + ",{ 'index=0x" + format(idx, 'x') + f"  -  {idx}\n"
            else:
              binary_str = "}%" + "_".join(color) + "{ 'index=0x" + format(idx, 'x') + f"  -  {idx}\n"
            palette_str += binary_str
        palette_str += "}"  
        palette_data.append(palette_str)
    
    return arr
def SetLines():
    global cropped
    global startnum
    global split
    global refresh
    global layout_arr
    if imagefile == '':
        return 'break'
    cropped = cropTarget()
    img = ImageOps.scale(cropped, scaleint.get(), resample=4)
    display = ImageTk.PhotoImage(img)
    root.focus_set()
    canvas.delete("all")
    root.display = display
    xbar = Scrollbar(f3, orient=HORIZONTAL)
    xbar.grid(row=1, column=0, sticky='ew')
    ybar = Scrollbar(f3, orient=VERTICAL)
    ybar.grid(row=0, column=1, sticky='ns')
    canvas.create_image(2, 2, image=display, anchor='nw')
    canvas.config(scrollregion=canvas.bbox(ALL))
    xbar.config(command=canvas.xview)
    ybar.config(command=canvas.yview)
    make_label(root, 5 + int(frameSize[0] / 3), 5 + int(frameSize[1] / 8), int(frameSize[1] / 15 / 2), 600, text='canvas size: 576x480          image size: ' + str(image.size[0]) + 'x' + str(image.size[1]) + '          scaled size: ' + str(image.size[0] * scaleint.get()) + 'x' + str(image.size[1] * scaleint.get()), bg='silver', justify=LEFT)
    canvas.create_line(2, 2, 2, img.size[1]+2, fill='black', width=1)
    canvas.create_line(img.size[0]+2, 2, img.size[0]+2, img.size[1]+2, fill='black', width=1)
    canvas.create_line(2, 2, img.size[0]+2, 2, fill='black', width=1)
    canvas.create_line(2, img.size[1]+2, img.size[0]+2, img.size[1]+2, fill='black', width=1)
    if startnum is None:
        startnum = 0
    counter = startnum
    if gridVar.get() == 1:
        for j in range(0, image.size[1]):
            for i in range(0, image.size[0]):
                canvas.create_line(i*scaleint.get() + 2, 0, i*scaleint.get() + 2, img.size[1], fill='silver', width=0)
                canvas.create_line(0, j*scaleint.get() + 2, img.size[0], j*scaleint.get() + 2, fill='silver', width=0)
    if v.get() != 0:
        if v.get() != split:
            refresh = 1
        if refresh == 1:
            split = v.get()
            layout_arr = byteMaker()
        refresh = 0
        for j in range(0, math.ceil(image.size[1] / v.get())):
            for i in range(0, math.ceil(image.size[0] / v.get())):
                t = str(layout_arr[j][i])
                if layout_arr[j][i] is None:
                    t = '-'
                if not((v.get()*scaleint.get()*i)+2 > img.size[0]) and not((v.get()*scaleint.get()*j)+2 > img.size[1]):
                    canvas.create_text((v.get() * scaleint.get() * i) + 7, (v.get() * scaleint.get() * j) + 5, text=t, fill=numcolor, font=('Terminal 9 bold'), anchor='nw')
                    counter += 1
                canvas.create_line(v.get() * scaleint.get() * i + 3, 0, v.get() * scaleint.get() * i + 3, v.get() * scaleint.get() * (math.ceil(image.size[1]/v.get())) + 3, fill=linecolor, width=2)
                canvas.create_line(0, v.get() * scaleint.get() * j + 3, v.get() * scaleint.get() * (math.ceil(image.size[0]/v.get())) + 3, v.get() * scaleint.get() * j + 3, fill=linecolor, width=2)
        canvas.create_line(v.get() * scaleint.get() * (math.ceil(image.size[0]/v.get())) + 3, 0, v.get() * scaleint.get() * (math.ceil(image.size[0]/v.get())) + 3, v.get() * scaleint.get() * (math.ceil(image.size[1]/v.get())) + 3, fill=linecolor,width=2)
        canvas.create_line(0, v.get() * scaleint.get() * (math.ceil(image.size[1]/v.get())) + 3, v.get() * scaleint.get() * (math.ceil(image.size[0]/v.get())) + 3, v.get() * scaleint.get() * (math.ceil(image.size[1]/v.get())) + 3, fill=linecolor,width=2)
def placeImage(scaleint):
    if not(imagefile == ''):
        SetLines()
def make_label(master, x, y, h, w, *args, **kwargs):
    f = Frame(master, height=h, width=w)
    f.pack_propagate(0) # don't shrink
    f.place(x=x, y=y)
    label = Label(f, *args, **kwargs)
    label.pack(fill=BOTH, expand=1)
    return label
def make_button(master, x, y, h, w, *args, **kwargs):
    f = Frame(master, height=h, width=w)
    f.pack_propagate(0)  # don't shrink
    f.place(x=x, y=y)
    button = Button(f, *args, **kwargs)
    button.pack(fill=BOTH, expand=1)
    return button
def spriteNumber(event):
    global startnum
    global refresh
    startnum = simpledialog.askinteger("Input", "Choose your starting sprite number", parent=root)
    if startnum is None:
        root.focus_set()
        return 'break'
    refresh = 1
    root.focus_set()
    SetLines()
    return 'break'
def chooseNumColor(event):
    global numcolor
    global numcolor_inv
    clr = colorchooser.askcolor(title='Choose Numbering Color')
    if clr[0] != None and clr[1] != None:
        numcolor = clr[1]
        numcolor_inv = '#' + hex(255-clr[0][0])[2:].zfill(2) + hex(255-clr[0][1])[2:].zfill(2) + hex(255-clr[0][2])[2:].zfill(2)
    colorButton.configure(bg=numcolor, fg=numcolor_inv)
    root.focus_set()
    SetLines()
    return "break"
def chooseLineColor(event):
    global linecolor
    global linecolor_inv
    clr = colorchooser.askcolor(title='Choose Line Color')
    if clr[0] != None and clr[1] != None:
        linecolor = clr[1]
        linecolor_inv = '#' + hex(255 - clr[0][0])[2:].zfill(2) + hex(255 - clr[0][1])[2:].zfill(2) + hex(
            255 - clr[0][2])[2:].zfill(2)
    lineButton.configure(bg=linecolor, fg=linecolor_inv)
    root.focus_set()
    SetLines()
    return "break"
def submitConfirm(saveLoc):
    def killConfirmWindow(event):
        confirmWindow.destroy()
    confirmWindow = Toplevel(root)
    confirmWindow.config(bg='silver')
    Label(confirmWindow, width=50, text="CONVERSION SUCCESSFUL", bg='navy', fg='orange', font='Terminal 20').pack(fill='x', expand=True)
    Label(confirmWindow, text="Text file saved to:", bg='silver').pack()
    saveLocText = Text(confirmWindow, bg='silver', fg='black')
    saveLocText.pack(fill='x', expand=True)
    saveLocText.insert(END, "Sprite: " + log[-1][0] + '\t\tSplit: ' + log[-1][3] + '\t\tQuanitity: ' + log[-1][4] + '\t\tTime: ' + str(log[-1][2]) + '\n' + log[-1][1] + "\n\n")
    saveLocText.configure(state=DISABLED)

    closeButton = Button(confirmWindow, text="OK", padx=10, pady=3, bg='orange', font='Terminal 10 bold', justify=LEFT)
    closeButton.bind("<Button-1>", killConfirmWindow)
    closeButton.pack()
    Label(confirmWindow, bg='silver').pack()
    root.focus_set()
def showLog(event):
    logWindow = Toplevel(root)
    logWindow.geometry("800x300")
    logWindow.config(bg='silver')
    if not log:
        Label(logWindow, text='You have converted no sprites', padx=20, pady=30, bg='silver').pack(fill='x')
    else:
        T = scrolledtext.ScrolledText(logWindow, bg='silver')
        T.pack(fill=BOTH, expand=True)
        for item in log:
            T.insert(END, "Sprite: " + item[0] + '\t\tSplit: ' + item[3] + '\t\tQuanitity: ' + item[4] + '\t\tTime: ' + str(item[2]) + '\n' + item[1] + "\n\n")
        T.configure(state=DISABLED)
def convert(event):
    # generate file name for .txt output-----------------------------------------------------
    textname = inputtxt.get()
    if v2.get() == 0:
        if len(textname) == 0 or (".txt" in textname):
            return 'break'
    # ---------------------------------------------------------------------------------------
    # create file path to save .txt output---------------------------------------------------
    z = 0
    saveLoc = ''
    for character in imagefile[::-1]:
        z += 1
        if character == "/":
            saveLoc = imagefile[:-(z - 1)]
            break
    if saveLoc == '':
        saveLoc = imagefile
    split = v.get()
    if split == 0:
        return 'break'
    # ---------------------------------------------------------------------------------------
    if v2.get() == 1:
        out = filedialog.asksaveasfile(mode='w', defaultextension='.txt')
        if out is None:
            return 'break'
        saveLoc = out.name
        textname = saveLoc[::-1]
        textname = textname[textname.index('.') + 1:textname.index('/')]
        textname = textname[::-1]
    bytedata = "con '" + textname + " sprites\ndat "
    declaration = "pub load_" + textname + "_sprites()   'call this method from main to load sprites\n"
    for i in range(len(s_list)):
        bytedata += textname + "_" + str(i+startnum) + " byte {\n"
        bytedata += s_list[i]
        bytedata += textname + "_" + str(i+startnum) + "_colors long {\n"
        bytedata += palette_data[i] +"\n\n"
        declaration += "\tdebug(`screen spritedef " + str(i+startnum) + " " + str(split) + " " + str(split) + " `uhex_byte_array_(@" + textname + "_" + str(i+startnum) + ", " + str(split * split) + ") `uhex_long_array_(@" + textname + "_" + str(i+startnum) + "_colors, " + str(int(palette_data[i][len(palette_data[i])-4:len(palette_data[i])-2])+1) + "))\n"
    tileLayout = "dat " + textname + "_tiles byte {\n" + layout[:-3] + "\n"
    finaltext = declaration + "\n" + tileLayout + "\n" + bytedata# + longdata
    if v2.get() == 0:
        log.append((textname, saveLoc + textname + ".txt", datetime.now(), str(split)+'x'+str(split), str(bytecount)))
        with open(saveLoc + textname + ".txt", 'w') as out:
            out.write(finaltext)
    elif v2.get() == 1:
        log.append((textname, saveLoc, datetime.now(), str(split)+'x'+str(split), str(bytecount)))
        out.write(finaltext)
        out.close()
    canvas.delete("all")
    scaler.set(1)
    v.set(0)
    v2.set(0)
    inputtxt.delete(0,END)
    gridbox.deselect()
    submitConfirm(saveLoc)
    return 'break'
def up(event):
    global target
    if imagefile == '':
        return
    target[1] += 1
    SetLines()
def down(event):
    global target
    if imagefile == '':
        return
    target[1] -= 1
    SetLines()
def left(event):
    global target
    if imagefile == '':
        return
    target[0] += 1
    SetLines()
def right(event):
    if imagefile == '':
        return
    global target
    target[0] -= 1
    SetLines()
def refreshGrid(event):
    global refresh
    refresh = 1
    root.focus_set()
    SetLines()

frameSize = (windowSize[0]-10, windowSize[1]-10)
f = Frame(root, width=frameSize[0], height=frameSize[1], bg='silver', bd=0, highlightbackground='silver', highlightcolor='silver', highlightthickness=0, relief=FLAT)
f.pack_propagate(0)
f.place(x=5,y=5)

make_label(root, 5, 5, int(frameSize[1]/8), frameSize[0], text='Add photo you wish to sprite', background='black', foreground='white', font='Helvetica ' + str(int(frameSize[1]/16)) + ' bold')

make_label(root, 5, 5+int(frameSize[1]/8), int(frameSize[1]/15), int(frameSize[0]/3), text='Select an image file to convert...', justify=CENTER, font='Terminal ' + str(int(frameSize[1]/60)))
uploadButton = make_button(root, int(frameSize[0]/6 - int(frameSize[0]/11.25/2)), 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15, int(frameSize[1]/20), int(frameSize[0]/11.25), text='Upload', bg='navy', fg='white', font='Terminal ' + str(int(frameSize[1]/60)))
uploadButton.bind("<Button-1>", upload)

make_label(root, 5+int(frameSize[0]/6 - int(frameSize[0]/11.25/2))+int(frameSize[0]/11.25), 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/40), 10, 100, text='*png files only*', bg='silver', font='Terminal 6')

make_label(root, 5, 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15, int(frameSize[1]/15), int(frameSize[0]/3), text='Select your sprite size...', justify=CENTER, font='Terminal ' + str(int(frameSize[1]/60)))
v = IntVar()
options = [('8x8',8), ('16x16',16), ('32x32',32)]
f2 = Frame(root)
f2.place(x=25,y=5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+15)
for choice, val in options:
    Radiobutton(f2, width=10, height=1, text=choice, variable=v, command=SetLines, value=val).pack()

gridVar = IntVar()
gridbox = Checkbutton(root, width=10, height=1, text='Display grid', variable=gridVar, onvalue=1, offvalue=0, command=SetLines)
gridbox.place(x=140, y=5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+15)

make_label(root, 140, 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*3)+5, 40, 98, text="Use arrow keys\nto move image,\nrefresh grid", justify=CENTER, font='Terminal 6')

numberButton = make_button(root, int((frameSize[0]/3 + 245 - 25)/2), 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+14, 25, 25, text='#', font='Terminal 13', bg='orange')
numberButton.bind("<Button-1>", spriteNumber)

refreshButton = make_button(root, int((frameSize[0]/3 + 245 - 25)/2), 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*3)+10, 25, 25, text='R', font='Terminal 13', bg='orange')
refreshButton.bind("<Button-1>", refreshGrid)

make_label(root, 5, 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*7), int(frameSize[1]/15), int(frameSize[0]/3), text="Scale (won't affect sprite)", justify=CENTER, font='Terminal ' + str(int(frameSize[1]/60)))
scaleint = IntVar()
scaler = Scale(length=150, variable=scaleint, from_=1, to=25, orient=HORIZONTAL, command=placeImage)
scaler.place(x=25, y=5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*10)+5)

colorButton = make_button(root, 190, 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*10)+5, 20, 20, text='0', bg=numcolor, fg=numcolor_inv, font='Terminal 12')
colorButton.bind("<Button-1>", chooseNumColor)

lineButton = make_button(root, 190, 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*10)+5+22, 20, 20, text='/', bg=linecolor, fg=linecolor_inv, font='Terminal 12')
lineButton.bind("<Button-1>", chooseLineColor)

make_label(root, 5, 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*13)+10, int(frameSize[1]/15), int(frameSize[0]/3), text='Output filename (NO ".txt")...', justify=CENTER, font='Terminal ' + str(int(frameSize[1]/60)))
inputtxt = Entry(root, width=46)
inputtxt.place(x=12, y=5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*17))

convertButton = make_button(root, int((frameSize[0]/12))-int(frameSize[0]/11.25/2), 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*19)+5 , int(frameSize[1]/15), int(frameSize[0]/11.25), text='Convert', bg='orange', fg='navy', font='Terminal ' + str(int(frameSize[1]/60)))
convertButton.bind("<Button-1>", convert)

logButton = make_button(root, int((frameSize[0]/12))-int(frameSize[0]/11.25/2), 5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*19)+5+int(frameSize[1]/15)+15, int(frameSize[1]/30), int(frameSize[0]/11.25), text='show log', bg='silver', font='Terminal 8')
logButton.bind("<Button-1>", showLog)

saveFrame = Frame(root)
saveFrame.place(x=int(frameSize[0]/6)-25, y=5+int(frameSize[1]/8)+int(frameSize[1]/15)+15+int(frameSize[1]/20)+15+int(frameSize[1]/15)+(15*19))
v2 = IntVar()
saveOptions = [('Default save location', 0), ('Choose save location', 1)]
for choice, val in saveOptions:
    Radiobutton(saveFrame, width=20, height=1, text=choice, variable=v2, value=val, bg='silver').pack()

f3 = Frame(root, width=frameSize[0] - int(frameSize[0] / 3), height=frameSize[1] - int(frameSize[1] / 8) - int(frameSize[1] / 15 / 2), bg='gray')
f3.place(x=5 + int(frameSize[0] / 3), y=5 + int(frameSize[1] / 8) + int(frameSize[1] / 15 / 2))

root.bind("<Up>", up)
root.bind("<Down>", down)
root.bind("<Left>", left)
root.bind("<Right>", right)
root.bind("<r>", refreshGrid)
root.bind("<R>", refreshGrid)
root.bind("<#>", spriteNumber)
root.bind_all('<Button>', focus)

root.mainloop()