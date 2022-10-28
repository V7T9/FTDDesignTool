import tkinter as tk 
from tkinter import messagebox
import math
from turtle import width
import setting
import os
import ctypes

class FTMapDetails:
    def __init__(self, wnum, hnum):
        self.wnum = wnum
        self.hnum = hnum
        # wnum * i + hnum
        self.roadlist = []
        self.buildinglist = []
        self.farmerlist = []
        self.marklist = []
        # crop, tree and flower
        self.soillist = []
        self.fishlist = []

    def LoadMap(self, filename):
        if (not os.path.exists(filename)):
            messagebox.showinfo('genius tip', f'file {filename} doesn\'t exists!')
            return
        with open(filename, 'r') as f:
            sizelist = []
            linelist = []
            for line in f:
                if (line):
                    linelist.append(line)
            sizelist= [int(x) for x in linelist[0].rstrip().split(' ')]
            self.wnum = sizelist[0]
            self.hnum = sizelist[1]
            self.roadlist.clear()
            self.buildinglist.clear()
            self.farmerlist.clear()
            self.marklist.clear()
            self.soillist.clear()
            self.fishlist.clear()
            square_lists = [self.roadlist, self.buildinglist, self.farmerlist, self.marklist, self.soillist, self.fishlist]
            i = 1
            while (i < len(linelist)):
                if (i == 1):
                    self.roadlist = self.LoadList(linelist[i])
                elif(i == 2):
                    self.buildinglist = self.LoadList(linelist[i])
                elif(i == 3):
                    self.farmerlist = self.LoadList(linelist[i])
                elif(i == 4):
                    self.marklist = self.LoadList(linelist[i])
                elif(i == 5):
                    self.soillist = self.LoadList(linelist[i])
                elif(i == 6):
                    self.fishlist = self.LoadList(linelist[i])
                i += 1

    def LoadList(self, datalist):
        datalist = datalist.rstrip().split(' ')
        intlist = []
        for x in datalist:
            if (x.isdigit()):
                intlist.append(int(x))
        return intlist

    def SaveMap(self, filename):
        with open(filename, "w") as f:
            f.truncate(0)
            f.write(f"{self.wnum} {self.hnum}\n")
            for road in self.roadlist:
                f.write(f"{road} ")
            f.write("\n")
            for building in self.buildinglist:
                f.write(f"{building} ")
            f.write("\n")
            for farmer in self.farmerlist:
                f.write(f"{farmer} ")
            f.write("\n")
            for mark in self.marklist:
                f.write(f"{mark} ")
            f.write("\n")
            for soil in self.soillist:
                f.write(f"{soil} ")
            f.write("\n")
            for fish in self.fishlist:
                f.write(f"{fish} ")
            f.write("\n")


class FTGrid:
    def __init__(self, parent, width, height, wnum, hnum, gridlen, xmin, xmax, ymin, ymax):
        self.parent = parent
        self.width = width
        self.height = height
        self.wnum = wnum
        self.hnum = hnum
        self.gridlen = gridlen
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.color = setting.gridcolor
        self.wcenter = self.wnum / 2
        self.hcenter = self.hnum / 2


        self.Draw()

    def Draw(self):
        wchunk = 40
        hcrunk = 20
        for i in range(self.wnum + 1):
            curx = i * self.gridlen + self.xmin
            self.parent.create_line(curx, self.ymin, curx, self.ymax, fill=setting.gridcolor)
        for i in range(self.hnum + 1):
            cury = i * self.gridlen + self.ymin
            self.parent.create_line(self.xmin, cury, self.xmax, cury, fill=setting.gridcolor)
        # draw border of each block if 280x140
        if (self.wnum != setting.DEFAULT_WIDTH_GRID or self.hnum != setting.DEFAULT_HEIGHT_GRID):
            return
        for i in range(self.wnum // wchunk):
            curx = i * wchunk * self.gridlen + self.xmin
            self.parent.create_line(curx, self.ymin, curx, self.ymax, fill=setting.darkgridcolor)
        for i in range(self.hnum // hcrunk):
            cury = i * hcrunk * self.gridlen + self.ymin
            self.parent.create_line(self.xmin, cury, self.xmax, cury, fill=setting.darkgridcolor)





class FTTool(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        if(os.path.exists(setting.FTDT_LOGO)):
            self.iconbitmap(setting.FTDT_LOGO)
        self.curfilename = tk.StringVar(self, value = setting.DEFAULT_NAME)
        self.UpdateTitle()
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("%dx%d+0+0" % (w, h))
        self.canwidth = w - 150.0
        self.canheight = h - 150.0
        self.can = tk.Canvas(self, width=self.canwidth, height=self.canheight, bg=setting.bgcolor)
        # 0vtool, 1scale, 2drawroad, 3erase, 4building, 5farmer
        self.funcnum = 0

        # farmer map
        self.farmerrec = {}

        # undo list
        self.undolist = []
        
        # scrollbar
        self.xscrbar = tk.Scrollbar(self, orient="horizontal", command=self.can.xview)
        self.yscrbar = tk.Scrollbar(self, orient="vertical", command=self.can.yview)
        self.can.config(yscrollcommand=self.yscrbar.set, xscrollcommand=self.xscrbar.set)
        self.can.config(scrollregion=(0, 0, self.canwidth, self.canheight))

        # text
        self.xpos = tk.StringVar()
        self.ypos = tk.StringVar()
        self.xlabel = tk.Label(self, textvariable=self.xpos)
        self.ylabel = tk.Label(self, textvariable=self.ypos)

        self.FuncBtn()

        # data in memory
        self.mapdetails = FTMapDetails(setting.DEFAULT_WIDTH_GRID, setting.DEFAULT_HEIGHT_GRID)
        
        self.UpdateGrid()

        self.SetLayout()

        self.can.bind("<MouseWheel>",self.zoomer)
        self.can.bind("<Button-1>", self.drawer)
        self.can.bind("<B1-Motion>", self.drawer)
        self.can.bind("<Button-3>", self.ShowPos)
        self.can.bind_all("<Control-z>", self.Undo)

    def UpdateTitle(self):
        self.title("Farm Together Design Tool - " + self.curfilename.get())

    # update canvas when grid number changed
    def UpdateGrid(self):
        self.can.delete('all')
        self.undolist.clear()
        self.farmerrec.clear()

        self.wnum = self.mapdetails.wnum
        self.hnum = self.mapdetails.hnum
        # grid filled history (x, y) -> x * w + y
        # 0, empty; 1, road; 2, building; 3, farmer
        self.filled = []

        self.gridlen = min(self.canwidth / self.wnum, self.canheight / self.hnum)
        self.gridwidth = self.gridlen * self.wnum
        self.gridheight = self.gridlen * self.hnum
        self.xmin = self.canwidth / 2 - self.gridwidth / 2
        self.xmax = self.xmin + self.gridwidth
        self.ymin = (self.canheight - self.gridheight) / 2
        self.ymax = self.ymin + self.gridheight
        drawgrid = FTGrid(self.can, self.canwidth, self.canheight, self.wnum, self.hnum, self.gridlen, self.xmin, self.xmax, self.ymin, self.ymax)
        self.ScaleCanvas(self.canwidth / 2, self.canheight / 2, max(self.wnum, self.hnum) / 80)
        self.undobtn["state"] = "disable"

        self.DrawYourItem()

        for i in range(self.wnum * self.hnum):
            self.filled.append(setting.EMPTY_GRID)
        for r in self.mapdetails.roadlist:
            self.filled[r]=setting.ROAD_GRID
            x = r % self.wnum
            y = r // self.wnum
            self.DrawRec(x, y, 1, setting.roadcolor, setting.gridcolor)
        for b in self.mapdetails.buildinglist:
            self.filled[b]=setting.BUILD_GRID
            x = b % self.wnum
            y = b // self.wnum
            self.DrawRec(x, y, 1, setting.buildcolor, setting.gridcolor)
        for f in self.mapdetails.farmerlist:
            self.filled[f]=setting.FARMER_GRID
            x = f % self.wnum
            y = f // self.wnum
            self.DrawRec(x, y, 1, setting.farmerborder, setting.gridcolor)
            self.farmerrec[f] = self.DrawFarmerborder(x, y, 13, "", setting.farmerborder)
        for m in self.mapdetails.marklist:
            self.filled[m]=setting.MARK_GRID
            x = m % self.wnum
            y = m // self.wnum
            self.DrawMark(x, y)
        for s in self.mapdetails.soillist:
            self.filled[s]=setting.SOIL_GRID
            x = s % self.wnum
            y = s // self.wnum
            self.DrawRec(x, y, 1, setting.soilcolor, setting.gridcolor)
        for fi in self.mapdetails.fishlist:
            self.filled[fi]=setting.FISH_GRID
            x = fi % self.wnum
            y = fi // self.wnum
            self.DrawRec(x, y, 1, setting.fishcolor, setting.gridcolor)

        
    def DrawYourItem(self):
        ## draw your image
        # self.img = img = tk.PhotoImage(file=os.getcwd()+"yourmig")
        # self.can.create_image(2400, 300, image=img)
        ## draw arbitrary shape you want here
        # self.DrawCircle(140, 70, 9)
        # self.DrawOctagon(140, 70, 27)
        # self.DrawOctagon(140, 70, 41)
        # self.DrawOctagon(140, 70, 55)
        # self.DrawOctagon(140, 70, 65)
        return

        
    def Vtoolcmd(self):
        self.funcnum = setting.VTOOL_CMD
        self.can.config(cursor="arrow")

    def Scalecmd(self):
        self.funcnum = setting.SCALE_CMD
        self.can.config(cursor="double_arrow")

    def DrawRoad(self):
        self.funcnum = setting.DRAWROAD_CMD
        self.can.config(cursor="circle")

    def Erase(self):
        self.funcnum = setting.ERASE_CMD
        self.can.config(cursor="X_cursor")

    def DrawBuild(self):
        self.funcnum = setting.DRAWBUILD_CMD
        self.can.config(cursor="star")
    
    def DrawFarmer(self):
        self.funcnum = setting.DRAWFARMER_CMD
        self.can.config(cursor="man")
        self.can.bind("<Enter>", self.ShowFarmerBorder)
        self.can.bind("<Leave>", self.HideFarmerBorder)

    
    def DrawMarkCMD(self):
        self.funcnum = setting.DRAWMARK_CMD
        self.can.config(cursor="target")

    def DrawSoilCMD(self):
        self.funcnum = setting.DRAWSOIL_CMD
        self.can.config(cursor="dotbox")

    def DrawFishCMD(self):
        self.funcnum = setting.DRAWFISH_CMD
        self.can.config(cursor="sailboat")

    def Undo(self, event = None):
        if (len(self.undolist) > 0):
            self.undolist.pop().Undoopr(self)
            if (len(self.undolist) == 0):
                self.undobtn["state"] = "disable"

    def ShowPos(self, event):
        x, y = self.togridnum(event)
        if (x < 0 or x > self.wnum or y < 0 or y > self.hnum): 
            x = '&$%'
            y = '&$%'
        self.xpos.set('X:  ' + str(x))
        self.ypos.set('Y:  ' + str(y))

    # when mouse enter show farmer border
    def ShowFarmerBorder(self, event):
        if (self.funcnum != setting.DRAWFARMER_CMD): return
        x, y = self.togridnum(event)
        self.farmerborder = self.DrawFarmerborder(x, y, 13, "", setting.farmerborder)
        self.can.bind("<Motion>", self.MoveFarmerBorder)

    def HideFarmerBorder(self, event):
        if (self.funcnum != setting.DRAWFARMER_CMD): return
        self.can.unbind("<Motion>")
        self.can.delete(self.farmerborder)

    def MoveFarmerBorder(self, event):
        x, y = self.togridnum(event)
        if (x >=0 and y >=0 and x < self.wnum and y < self.hnum):
            x = self.xmin + x * self.gridlen
            y = self.ymin + y * self.gridlen
            halflen = 13 // 2
            x1 = x -  halflen * self.gridlen
            y1 = y - halflen * self.gridlen
            self.can.moveto(self.farmerborder, x1, y1)


    # right side operation area
    def FuncBtn(self):
        # default btn
        btn_width = 10
        self.vtool = tk.Button(self, text = "Mouse 🖱", command = self.Vtoolcmd, width=btn_width)
        self.scalebtn = tk.Button(self, text = "Scale 🔍", command = self.Scalecmd, width=btn_width)
        self.roadbtn = tk.Button(self, text = "Road 🌫", command = self.DrawRoad, width=btn_width)
        self.eraserbtn = tk.Button(self, text = "Eraser 🗑",command = self.Erase, width=btn_width)
        self.buildbtn = tk.Button(self, text = "Building 🏚", command = self.DrawBuild, width=btn_width)
        self.farmbtn = tk.Button(self, text = "Farmer 🤠", command = self.DrawFarmer, width=btn_width)
        self.markbtn = tk.Button(self, text = "Mark ⭐", command = self.DrawMarkCMD, width=btn_width)
        self.soilbtn = tk.Button(self, text = "Soil ⛏", command = self.DrawSoilCMD, width=btn_width)
        self.fishbtn = tk.Button(self, text = "Fish 🐟", command = self.DrawFishCMD, width=btn_width)
        self.undobtn = tk.Button(self, text = "Undo 👈", command=self.Undo, width=btn_width)
        self.farmlistbtn = tk.Button(self, text = "Farm List📃", command = self.ShowFarmList, width=btn_width)
        self.savebtn = tk.Button(self, text = "Save 💾", command = self.SaveCur, width=btn_width)

    def SetLayout(self):
        totalrow = 14
        self.can.grid(row=0, column=0, rowspan=totalrow, sticky=tk.N+tk.E+tk.W)
        self.xscrbar.grid(row=totalrow, column=0, sticky=tk.E+tk.W)
        self.yscrbar.grid(row=0, column=1, rowspan=totalrow, sticky=tk.N+tk.S)
        btnlist = [self.xlabel, self.ylabel, self.vtool, self.scalebtn, self.roadbtn, self.buildbtn, self.farmbtn, self.markbtn, self.soilbtn, self.fishbtn, self.eraserbtn, self.undobtn, self.farmlistbtn, self.savebtn]
        for i in range(totalrow):
            btnlist[i].grid(row = i, column=2)

    # screen pos to canvas pos
    def tocanvasxy(self, event):
        return self.can.canvasx(event.x), self.can.canvasy(event.y)

    # get the grid pos(int)
    def togridnum(self, event):
        canx = int(self.can.canvasx(event.x))
        cany = int(self.can.canvasy(event.y))
        numx = math.floor((canx - self.xmin) / self.gridlen)
        numy = math.floor((cany - self.ymin) / self.gridlen)
        return numx, numy

    # scale the canvas
    def zoomer(self, event):
        if (self.funcnum == setting.SCALE_CMD):
            x, y = self.tocanvasxy(event)
            scale = 1.0
            if (event.delta > 0):
                scale = 1.1
            elif (event.delta < 0):
                scale = 0.9
            self.ScaleCanvas(x, y, scale)

    def ScaleCanvas(self, x, y, scale):
        self.can.scale("all", x, y, scale, scale)
        self.gridlen = self.gridlen * scale
        self.xmin = (self.xmin - x) * scale + x
        self.ymin = (self.ymin - y) * scale + y
        self.can.config(scrollregion = self.can.bbox("all"))

    # draw grid
    def drawer(self, event):
        x, y = self.togridnum(event)
        if (x >=0 and y >=0 and x < self.wnum and y < self.hnum):
            curindex = y * self.wnum + x
            # draw road
            if (self.funcnum == setting.DRAWROAD_CMD ):
                if (self.filled[curindex] != setting.ROAD_GRID):
                    self.AddToMap(x, y, setting.ROAD_GRID, setting.roadcolor)
            # eraser
            elif(self.funcnum == setting.ERASE_CMD):
                if (self.filled[curindex] != setting.EMPTY_GRID):
                    self.AddToMap(x, y, setting.EMPTY_GRID, setting.bgcolor)
            # building
            elif(self.funcnum == setting.DRAWBUILD_CMD):
                if (self.filled[curindex] != setting.BUILD_GRID):
                    self.AddToMap(x, y, setting.BUILD_GRID, setting.buildcolor)
            # farmer
            elif(self.funcnum == setting.DRAWFARMER_CMD):
                if (self.filled[curindex] != setting.FARMER_GRID):
                    self.farmerrec[curindex] = self.DrawFarmerborder(x, y, 13, "", setting.farmerborder)
                    self.AddToMap(x, y, setting.FARMER_GRID, setting.farmerborder)
            # mark
            elif(self.funcnum == setting.DRAWMARK_CMD):
                if (self.filled[curindex] != setting.MARK_GRID):
                    self.AddToMap(x, y, setting.MARK_GRID, setting.markcolor)  
            # soil 
            elif(self.funcnum == setting.DRAWSOIL_CMD):
                if (self.filled[curindex] != setting.SOIL_GRID):
                    self.AddToMap(x, y, setting.SOIL_GRID, setting.soilcolor)
            # fish
            elif(self.funcnum == setting.DRAWFISH_CMD):
                if (self.filled[curindex] != setting.FISH_GRID):
                    self.AddToMap(x, y, setting.FISH_GRID, setting.fishcolor)        

    # draw one rec,x, y: grid number 
    def DrawRec(self, x, y, alen:int, fillcolor, outlinecolor):
        x = self.xmin + x * self.gridlen
        y = self.ymin + y * self.gridlen
        halflen = alen // 2
        x1 = x -  halflen * self.gridlen
        y1 = y - halflen * self.gridlen
        x2 = x + (halflen + 1) * self.gridlen
        y2 = y + (halflen + 1) * self.gridlen
        return self.can.create_rectangle(x1, y1, x2, y2, fill=fillcolor, outline=outlinecolor)
    
    def DrawFarmerborder(self, x, y, alen:int, fillcolor, outlinecolor):
        x = self.xmin + x * self.gridlen
        y = self.ymin + y * self.gridlen
        halflen = alen // 2
        x1 = x -  halflen * self.gridlen
        y1 = y - halflen * self.gridlen
        x2 = x + (halflen + 1) * self.gridlen
        y2 = y + (halflen + 1) * self.gridlen
        return self.can.create_rectangle(x1, y1, x2, y2, fill=fillcolor, outline=outlinecolor, width=3, dash=(5, 1))

    # position marker
    def DrawMark(self, x, y):
        # copy from somewhere else
        center_x=self.xmin + x * self.gridlen + self.gridlen / 2
        center_y=self.ymin + y * self.gridlen + self.gridlen / 2
        r=self.gridlen / 2 
        points=[
            center_x-int(r*math.sin(2*math.pi/5)),
            center_y-int(r*math.cos(2*math.pi/5)),

            center_x+int(r*math.sin(2*math.pi/5)),
            center_y-int(r*math.cos(2*math.pi/5)),

            center_x-int(r*math.sin(math.pi/5)),
            center_y+int(r*math.cos(math.pi/5)),

            center_x,
            center_y-r,

            center_x+int(r*math.sin(math.pi/5)),
            center_y+int(r*math.cos(math.pi/5)),
        ]
        return self.can.create_polygon(points, outline="", fill=setting.markcolor)

    def DrawCircle(self, x, y, r):
        x0 = (x + 0.5 - r) * self.gridlen + self.xmin
        y0 = (y + 0.5 - r) * self.gridlen + self.ymin
        x1 = x0 + 2 * r * self.gridlen
        y1 = y0 + 2 * r * self.gridlen
        return self.can.create_oval(x0, y0, x1, y1)

    def DrawOctagon(self, x, y, r):
        alpha = 2 * math.pi / 16
        tt = self.gridlen * r * math.tan(alpha)
        rr = r * self.gridlen
        xc = (x + 0.5) * self.gridlen + self.xmin
        yc = (y + 0.5) * self.gridlen + self.ymin
        points = [
            xc - tt, yc - rr,
            xc - rr, yc - tt,
            xc - rr, yc + tt,
            xc - tt, yc + rr,
            xc + tt, yc + rr,
            xc + rr, yc + tt,
            xc + rr, yc - tt,
            xc + tt, yc - rr
        ]
        for i in range (0, 16, 2):
            self.can.create_line(points[i], points[i + 1], xc, yc)
        return self.can.create_polygon(points, fill="", outline=setting.darkgridcolor)


    def AddToMap(self, x, y, gridtype, fillcolor):
        curindex = y * self.wnum + x
        # if farmer
        if (self.filled[curindex] == setting.FARMER_GRID):
            self.can.delete(self.farmerrec[curindex])
            del self.farmerrec[curindex]
        
        curopr = FTOperation(curindex, self.filled[curindex], gridtype)
        if (gridtype == setting.MARK_GRID):
            curopr.AddElement(self.DrawMark(x, y))
        else:
            curopr.AddElement(self.DrawRec(x, y, 1, fillcolor, setting.gridcolor))
        self.filled[curindex] = gridtype
        self.undolist.append(curopr)
        self.undobtn["state"] = "normal"  
        # move farmer borders to the top
        for item in self.farmerrec.values():
            self.can.tag_raise(item)

    # save current map
    def SaveCur(self):
        # here may have some bug, please don't name the file DEFAULT_NAME
        if (self.curfilename.get() == setting.DEFAULT_NAME):
            savewin = tk.Toplevel(self)
            savewin.title("Save to...")
            savename = tk.StringVar(savewin)
            saveentry = tk.Entry(savewin, textvariable=savename, width=20)
            savebtn = tk.Button(savewin, text="Save", command=lambda:self.UpdateFarmName(savename, savewin))
            saveentry.pack()
            savebtn.pack()
            saveentry.focus_set()
        else :
            self.SaveCurrentMap()

    def UpdateFarmName(self, farmname, parent):
        # ----------here need to consider overwriting existing file but I'm lazy
        self.curfilename.set(farmname.get())
        if (self.curfilename.get() != ""):
            self.SaveCurrentMap()
            self.UpdateTitle()
        parent.destroy()
    
    # load data from tool filled to details list
    def SaveCurrentMap(self):
        self.mapdetails.roadlist.clear()
        self.mapdetails.buildinglist.clear()
        self.mapdetails.farmerlist.clear()
        self.mapdetails.marklist.clear()
        self.mapdetails.soillist.clear()
        self.mapdetails.fishlist.clear()
        for index in range(self.wnum * self.hnum):
            if (self.filled[index] == setting.ROAD_GRID):
                self.mapdetails.roadlist.append(index)
            elif (self.filled[index] == setting.BUILD_GRID):
                self.mapdetails.buildinglist.append(index)
            elif (self.filled[index] == setting.FARMER_GRID):
                self.mapdetails.farmerlist.append(index)
            elif (self.filled[index] == setting.MARK_GRID):
                self.mapdetails.marklist.append(index)
            elif (self.filled[index] == setting.SOIL_GRID):
                self.mapdetails.soillist.append(index)
            elif (self.filled[index] == setting.FISH_GRID):
                self.mapdetails.fishlist.append(index)
        self.mapdetails.SaveMap(setting.FARM_FILE + '/' + self.curfilename.get() + '.' + setting.FARM_SUFFIX)
        messagebox.showinfo(title="FT Tool", message="Save Successfully!")

    def ShowFarmList(self):
        farmlist = FarmListPopWin(self)


# show farm list
class FarmListPopWin(tk.Toplevel):
    def __init__(self, parent:FTTool):
        super().__init__(parent)
        self.curfarm = parent.curfilename
        self.parent = parent
        self.title("farm list")
        self.geometry("250x300")
        self.farmlist = tk.Listbox(self, selectmode=tk.SINGLE)
        self.RefreshFarm()
        self.addbtn = tk.Button(self, text="Add farm", command=self.AddFarm)
        self.selectbtn = tk.Button(self, text="Load this", command=self.SelectFarm)
        self.delbtn = tk.Button(self, text="Delete this", command=self.DelFarm)

        self.farmlist.pack(side='left', fill='both', expand=True)
        self.addbtn.pack()
        self.selectbtn.pack()
        self.delbtn.pack()

    def RefreshFarm(self):
        # create folder if not exists
        if not os.path.exists(setting.FARM_FILE):
            os.makedirs(setting.FARM_FILE)
        self.farmlist.delete(0, tk.END)
        for root, dirs, files in os.walk(setting.FARM_FILE, topdown=True):
            for name in files:
                if (name.split('.')[-1] == setting.FARM_SUFFIX):
                    self.farmlist.insert(tk.END, name.split('.')[0])
        
    def AddFarm(self):
        addfarmwin = tk.Toplevel()
        addfarmwin.title('Add Farm')
        farmname = tk.StringVar(value="my farm")
        farmwidth = tk.StringVar(value= str(setting.DEFAULT_WIDTH_GRID))
        farmheight = tk.StringVar(value= str(setting.DEFAULT_HEIGHT_GRID))
        entryname = tk.Entry(addfarmwin, textvariable=farmname, width=20)
        entrywidth = tk.Entry(addfarmwin, textvariable=farmwidth, width=20)
        entryheight = tk.Entry(addfarmwin, textvariable=farmheight, width=20)
        addfarmbtn = tk.Button(addfarmwin, text="Add it!", command=lambda:self.AddFile(farmname.get(), farmwidth.get(), farmheight.get(), addfarmwin))

        entryname.pack()
        entrywidth.pack()
        entryheight.pack()
        addfarmbtn.pack()
        
    def AddFile(self, farmname, width, height, parent):
        if (not (width.isdigit() and height.isdigit()) or len(farmname) <= 0):
            messagebox.showwarning(parent=self, title="something wrong", message="I'm lazy but something wrong with your input")
            return
        
        if (int(width) > setting.MAX_LENGTH or int(height) > setting.MAX_LENGTH):
            messagebox.showwarning(parent = self, title="something wrong", message="width  or height should be in " + str(setting.MIN_LENGTH) + ' ~ ' + str(setting.MAX_LENGTH))
            return
        

        filename = setting.FARM_FILE + '/' + farmname + '.' + setting.FARM_SUFFIX
        if (os.path.exists(filename)):
            if (not messagebox.askokcancel(parent = self, title = 'genius tip',  message = farmname + ' exists, overwrite it?')):
                return
        with open(filename, "w") as f:
            f.write(f"{width} {height}\n")
        
        self.RefreshFarm()
        parent.destroy()
        
    def DelFarm(self):
        index = self.farmlist.curselection()
        # if no file selected
        if (len(index) == 0):
            messagebox.showwarning(parent = self, title="warning", message="No file selected!")
            return
        
        farmname = self.farmlist.get(index[0])
        # if farm is currently used now
        if (farmname == self.curfarm.get()):
            messagebox.showwarning(parent = self, title="warning", message= "You are using ' " + farmname + " ' now!")
            return

        if (not messagebox.askokcancel(parent = self, title = "warning",  message = "Are you sure to delete ' " + farmname + " ' ?")):
            return

        path = setting.FARM_FILE + '/' + farmname + '.' + setting.FARM_SUFFIX
        if (os.path.exists(path)):
            os.remove(path)
        self.RefreshFarm()

    def SelectFarm(self):
        index = self.farmlist.curselection()
        # if no file selected
        if (len(index) == 0):
            messagebox.showwarning(parent = self, title="warning", message="No file selected!")
            return
        farmname = self.farmlist.get(index[0])
        farmpath = setting.FARM_FILE + '/' + farmname + '.' + setting.FARM_SUFFIX
        self.parent.mapdetails.LoadMap(farmpath)
        self.parent.UpdateGrid()
        self.parent.curfilename.set(farmname)
        self.parent.UpdateTitle()
        self.destroy()
    
        
# store operations
class FTOperation:
    def __init__(self, pos, lastfilled, oprname):
        self.pos = pos
        self.elements = []
        self.lastfilled = lastfilled
        # 'x' 0, empty; 1, road; 2, building; 3, farmer
        self.oprname = oprname

    def AddElement(self, element):
        self.elements.append(element)

    def Undoopr(self, fttool:FTTool):
        while (len(self.elements) > 0):
            fttool.can.delete(self.elements.pop())
        fttool.filled[self.pos] = self.lastfilled
        # if undo del farmer
        if (self.lastfilled == setting.FARMER_GRID):
            fttool.farmerrec[self.pos] = fttool.DrawFarmerborder(self.pos % fttool.wnum, self.pos // fttool.wnum, 13, "", setting.farmerborder)
        # id undo add farmer
        elif (self.oprname == setting.FARMER_GRID):
            fttool.can.delete(fttool.farmerrec[self.pos])
            del fttool.farmerrec[self.pos]



if __name__ == "__main__":
    myappid = 'genius.hcc' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    geniushere = FTTool()
    geniushere.mainloop()