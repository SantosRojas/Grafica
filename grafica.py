from tkinter import *
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from control01 import *
import control.matlab as cn
from tkinter.messagebox import showerror,showinfo
from ttkthemes import ThemedTk


class Grafica:
    def __init__(self,ventana):
        self.frame1=ttk.Frame(ventana)
        self.frame1.pack(fill='both')
        
        self.frame11=ttk.Frame(self.frame1)
        self.frame11.pack(fill='both',expand=True,side=LEFT,padx=5)
        ttk.Label(self.frame11,text='Transfer Function: ').pack(fill='both',expand=True,padx=5,pady=5)
        self.tf=ttk.Entry(self.frame11)
        self.tf.pack(fill='both',expand=True,padx=5,pady=5)
        self.frame12=ttk.LabelFrame(self.frame1,text='Tipo de grafica')
        self.frame12.pack(fill='x',side=LEFT)
        self.frame121=ttk.Frame(self.frame12)
        self.frame121.pack(fill='x',side=LEFT)
        self.frame122=ttk.Frame(self.frame12,)
        self.frame122.pack(fill='x',side=RIGHT)
        self.opcion = IntVar() # Como StrinVar pero en entero
        ttk.Radiobutton(self.frame121, text="Step", variable=self.opcion, value=1).pack(padx=5,pady=5)
        ttk.Radiobutton(self.frame122, text="LGR", variable=self.opcion,value=2).pack(padx=5,pady=5)
        self.frame13=ttk.Frame(self.frame1)
        self.frame13.pack(fill='x',side=RIGHT)
        ttk.Button(self.frame13,text='GRAFICAR',command=self.animate).pack(padx=5,pady=5)

        self.frame3=ttk.Frame(ventana)
        self.frame3.pack(fill='both',expand=True)
        
        #style.use('fivethirtyeight')
        self.fig,self.ax=plt.subplots()
        #self.ax.set_facecolor('k')
        self.ax.tick_params(direction='out',length=6,width=2,color='k',grid_color='r',grid_alpha=0.5)
        
        self.cont=FigureCanvasTkAgg(self.fig,master=self.frame3)
        self.cont.draw()
        self.cont.get_tk_widget().pack(side=TOP,fill=BOTH,expand=TRUE)
        tbl=NavigationToolbar2Tk(self.cont,self.frame3)
        tbl.update()
        self.cont.get_tk_widget().pack(side=TOP,fill=BOTH,expand=TRUE)

        self.frame2=ttk.LabelFrame(ventana,text='Parametros')
        self.frame21=ttk.Frame(self.frame2)
        self.frame21.pack(expand=True,side=LEFT)
        self.frame22=ttk.Frame(self.frame2)
        self.frame22.pack(expand=True,side=LEFT)
        self.frame23=ttk.Frame(self.frame2)
        self.frame23.pack(expand=True,side=LEFT)
        self.frame24=ttk.Frame(self.frame2)
        self.frame24.pack(expand=True,side=LEFT)
        self.frame25=ttk.Frame(self.frame2)
        self.frame25.pack(expand=True,side=RIGHT)
        self.tp=BooleanVar()
        ttk.Checkbutton(self.frame21,text='Tiempo pico',variable=self.tp).pack(padx=5,pady=5)
        self.ts=BooleanVar()
        ttk.Checkbutton(self.frame22,text='Tiempo Establecimiento',variable=self.ts).pack(padx=5,pady=5)
        self.vs=BooleanVar()
        ttk.Checkbutton(self.frame23,text='Valor estable',variable=self.vs).pack(padx=5,pady=5)
        self.vp=BooleanVar()
        ttk.Checkbutton(self.frame24,text='Valor pico',variable=self.vp).pack(padx=5,pady=5)
        self.an=BooleanVar()
        ttk.Checkbutton(self.frame25,text='Anotaciones',variable=self.an).pack(padx=5,pady=5)
        
       

        self.sys=''
    
    def animate(self):
          
        try:
            self.frame3.after_cancel(self.id_tarea)
            self.th.close()
        except:
            pass

        try:
            trf=self.tf.get()
            trf=trf.split(';')
            num=trf[0].split(',')
            den=trf[1].split(',')
            num=[float(a) for a in num]
            den=[float(a) for a in den]
            self.sys=tf(num,den)
        except:
            showerror('ERROR','INGRESE EL NUMERADOR Y DENOMINADOR DE LA TF')
            return
        
        
        self.ax.clear()
        #self.ax.axhline(0,color='k')
        #self.ax.axvline(0,color='k')
        sts=''
        if self.opcion.get()==1:
            self.frame2.pack(fill=X)
            if self.tp.get():
                sts+='tp,'
            if self.ts.get():
                sts+='ts,'
            if self.vp.get():
                sts+='vp,'
            if self.vs.get():
                sts+='vs'
            sts=sts.strip(',')
            if len(sts)>1:
                params=parameters(self.sys,params=sts,print_params=False)
            else:
                params=None

            t,y=step(self.sys)
            print(sts)
            try:
                plot(t,y,ax=self.ax,params=params,anotation=self.an.get())
            except Exception as e:
                showerror('ERROR',e)

        elif self.opcion.get()==2:
            self.frame2.pack_forget()
            LGR(self.sys,ax=self.ax)
        

        else:
            showinfo('Warning','USTED DEBE ELEJIR UNA GRAFICA')
        

        self.cont.draw()
        
ventana=ThemedTk(theme="adapta")
ventana.title("GRAFICADOR")
Grafica(ventana)
ventana.mainloop()


