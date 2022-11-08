from scipy.signal import lti
import numpy as np
import matplotlib.pyplot as plt
from control.matlab import *
#==================Comentarios=========
#Autor: Santos Herminio Rojas Gutierrez
#Es libre para su uso y mejoras
#======================================

def tf(num,den,r=0,method='Pade'):
    '''
    num: Numerador de la funcion de transferencia del sistema
    den: Denominador de la funcion de transferencia del sistema
    r: Retardo del systema
    methodo: Metodo de aproximacion del retardo (default: Pade)
    '''
    if r>0:
        if method=='Pade':
            num_p=[(r)**2,-6*r,12]
            den_p=[(r)**2,+6*r,12]
            num=np.convolve(num,num_p)
            den=np.convolve(den,den_p)
        if method=='AR':
            num_p=[0.0783*(r)**2,-0.4986*r,1]
            den_p=[0.0783*(r)**2,+0.4986*r,1]
            num=np.convolve(num,num_p)
            den=np.convolve(den,den_p)
        
        if method=='ARop':
            num_p=[0.091*(r)**2,-0.496*r,1]
            den_p=[0.091*(r)**2,+0.496*r,1]
            num=np.convolve(num,num_p)
            den=np.convolve(den,den_p)
            
    return lti(num,den)
    
def serie(sys1,sys2):
    '''
    Para tf en serie
    sys1 y sys2 son control.tf()
    return Tx,Yx,Tp,Ts,Vp,Vs
    '''
    num=np.convolve(sys1.num,sys2.num)
    den=np.convolve(sys1.den,sys2.den)
    return lti(num,den)

def feedback(sys1,sys2):
    '''
    Para tf con retroalimentacion negativa
    sys1 y sys2 son control.tf o scipy.signal.lti
    sys1: Funcion de transferencia de camino directo
    sys2:Funcion de transferencia de realimentacion negativa
    '''
    num=np.convolve(sys1.num,sys2.den)
    den1=np.convolve(sys1.num,sys2.num)
    den2=np.convolve(sys1.den,sys2.den)
    n=len(den1)
    m=len(den2)
    
    if n>m:
        den2=np.append(den2[::-1],np.zeros(n-m))[::-1]
        
    if m>n:
        den1=np.append(den1[::-1],np.zeros(m-n))[::-1]
        
    den=den1+den2
    
    return lti(num,den)


def parameters(sys,X0=None,params=None,cs=3,print_params=True,label='Resp_stp'):

    #Inicializacion de variables
    prms=['tp','ts','vp','mp','tl','vs','g']

    #===============Verificacion de los parametros ingresados=====
    if not params is None:
        list_params=params.split(',')
        
        
        if len(list_params)==1:
            if list_params[0]=='all':
                list_params=prms
            elif list_params[0] in prms:
                pass
            else:
                raise ValueError(f'El parametro {list_params[0]} es desconocido, utilizar tp,ts,vp,mp,vs,tl')
        else:
            for i in list_params:
                if not i in prms:
                    raise ValueError(f'El parametro {list_params[i]} es desconocido, utilizar tp,ts,vp,mp,vs,tl')
                    
    else:
        list_params=[]
        raise ValueError(f'Usted no ha ingresado ningun parametro, utilizar tp,ts,vp,mp,vs,tl')


    #print(list_params)
    #====================Calculos de los parametros===================
    
    t,y=sys.step(X0=X0)
    y_r=list(y)
    t_r=list(t)
    t_r.reverse()
    y_r.reverse()
    if print_params:
        print(f"=========== PARAMETROS DE {label} ===============")
        
    if 'tp' in list_params:
        tp=round(t[list(y).index(y.max())],cs)#tiempo pico
        if print_params:
            print(f'Tiempo pico(S) = {tp}')
        
    if 'ts' in list_params:
        vs=sys.num[-1]/sys.den[-1]
        g=round(abs(vs-y[0]),cs)
        ts=0 #tiempo de establecimiento
        for k,l in zip(y_r,t_r):
            try:
                if abs(k-g)<=0.02*g:
                    ts=l
                else:
                    ts=round(ts,cs)
                    break
            except Exception as e:
                raise ValueError('El sistema es inestable')
        if print_params:
            print(f'Tiempo de establecimiento(S) = {ts}')
        
    if 'tl' in list_params:
        vs=sys.num[-1]/sys.den[-1]
        try:
            for k,l in zip(y,t):
                if k<=vs*0.1:
                    tli=l
                else:
                    tli=round(tli,cs)
                    break
            for k,l in zip(y,t):
                if k<=vs*0.9:
                    tlf=l
                else:
                    tlf=round(tlf,cs)
                    break
                    
            tl=tlf-tli 
            tl=round(tl,cs)#Tiempo de levantamiento
            if print_params:
                print(f'Tiempo de levantamiento = {tl}')
            
        except Exception as e:
            raise ValueError("El sistema no presenta un tiempo de levantamiento")
            
    if 'mp' in list_params:
        mp=abs(y.max()-vs)/vs
        mp=round(mp,cs)#Maximo sobreimpulso
        if print_params:
            print(f'Maximo sobreimpulso = {mp}')
    
    if 'vp' in list_params:
        vp=round(y.max(),cs)
        if print_params:
            print(f'Valor pico = {vp}')
    
    if 'g' in list_params:
        g=round(abs(vs-y[0]),cs)#ganancia
        if print_params:
            print('Ganancia = ',g)
        
    if 'vs' in list_params:
        vs=sys.num[-1]/sys.den[-1]
        vs=round(vs,cs)#valor estable
        if print_params:
            print('Valor estable = ',vs)

    lp={}
    for i in list_params:
        lp[i]=eval(i)

    return lp

def step(sys, X0=None,T=None):
    '''
    sys es control.tf() o sicpy.signal.lti
           
    X0: Estado inicial del sistema.

    T:[ti,tf,n] Vector de tiempo (lista,ti:tiempo inicial,tf:tiempo final,n:numero de puntos).

    
    cs:cifras significativas.
    
    params: str, define que parametros se analizaran (solo se pueden plotear 'tp,ts,vp,vs') {
        'all': todos los parametros('tp,ts,vp,mp,tl,vs')
        'tp,vs': tiempo pico mas valor estable
        'tp,ts':tiempo pico mas tiempo de establecimiento
        ...
        'tp,ts,vp,':tiempo pico mas tiempo de establecimiento mas valor pico
    }
    **kwargs:title,xlabel,ylabel,loc
    >>loc:
    'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 
    'center right', 'lower center', 'upper center', 'center'
    
    '''

    if not T is None:
        if T[1]<T[0]:
            raise ValueError('El valor de tf debe ser mayor a ti en T=[ti,tf,n]')
        else:
            T=np.linspace(T[0],T[1],T[2])
        
    t,y=sys.step(X0=X0,T=T)
    return t,y

def plot(t,y,params=None,c='b',label='Resp_step',lw=1.5,anotation=False,fc='cyan',fig=None,ax=None,**kwargs):
    
    #=====================Inicializacion de vaiables=======
    if params is None:
        params=[]

    args_plot={'title':'Respuesta al escalon unitario','xlabel':'Tiempo(S)','ylabel':'Magnitud','loc':'best'}
    for key,_ in kwargs.items():
        if key in args_plot.keys():
            args_plot[key]=kwargs[key]
        else:
            raise ValueError(f'''La llave {key} es desconocida. Utilizar 'title','xlabel','ylabel','loc' ''')
    if ax is None:
        if fig is None:
            fig = plt.figure(facecolor=fc)
        ax = fig.add_subplot(111)
    
    line, = ax.plot(t,y,c,label=label,linewidth=lw)


    
    if 'vs' in params:
        plt.plot([t[0],t[-1]],[params['vs']]*2,'grey',linestyle='dotted')
        if anotation:
            ax.annotate(f"{params['vs']}", xy=(0,params['vs']))

            
    if 'vp' in params:
        if 'tp' in params:
            plt.plot([t[0],params['tp']],[params['vp']]*2,'-.')
            if anotation:
                ax.annotate(f"{params['vp']}", xy=(params['tp'],params['vp']))
        else:
            plt.plot([t[0],t[-1]],[params['vp']]*2,'-.')
            if anotation:
                ax.annotate(f"{params['vp']}", xy=(0,params['vp']))

    if 'tp' in params:
        tp=params['tp']
        plt.plot([tp]*2,[y[0],y.max()],'-.')
        if anotation:
            ax.annotate(f'{tp}', xy=(tp,0))

    if 'ts' in params:
        ts=params['ts']
        plt.plot([ts]*2,[y[0],y[-1]],'-.')
        if anotation:
            ax.annotate(f'{ts}', xy=(ts,0))

    plt.title(args_plot['title'])
    plt.xlabel(args_plot['xlabel'])
    plt.ylabel(args_plot['ylabel'])
    plt.legend(loc=args_plot['loc'])
        
def PI(sys,m,ts):
    '''
    sys=tf
    m=sobre impulso en decimal.
    ts: tiempo de establecimiento.
    '''
    z=1/np.sqrt(1+(np.pi/np.log(m))**2)
    w=4/(z*ts)
    N=sys.num
    D=sys.den

    s1=complex(-w*z,w*np.sqrt(1-z**2))
    s2=complex(-w*z,-w*np.sqrt(1-z**2))

    D1=np.polyval(D,s1)
    D2=np.polyval(D,s2)
    N1=np.polyval(N,s1)
    N2=np.polyval(N,s2)

    kp=(s2*D2*N1-s1*D1*N2)/((s1-s2)*N1*N2)
    ki=-kp*s1-D1*s1/N1
    kp=kp.real
    ki=ki.real
    Gdir=serie(sys,tf([kp,ki],[1,0]))
    G=feedback(Gdir,tf(1,1))
    return G

def show():
    plt.show()

def LGR(sys,xlim=None,ylim=None,fc='cyan',grid=False,anotation=True,fig=None,ax=None):
    real=[]
    imag=[]
    p=sys.poles
    z=sys.zeros
    k=np.linspace(0.01,300,3000)
    if ax is None:
        if fig is None:
            fig = plt.figure(facecolor=fc)
        ax = fig.add_subplot(111)
    for i in k:
        ser=serie(sys,tf([i],[1]))
        fed=feedback(ser,tf([1],[1]))
        ps=fed.poles
        real.append(ps.real)
        imag.append(ps.imag)
    ax.plot(real,imag,linewidth=2)
    ax.plot(p.real,p.imag,c='red',marker='x',ms=10,ls='',linewidth=5)# graficamos los polos en lazo directo
    ax.plot(z.real,z.imag,c='blue',marker='o',ms=10,ls='',linewidth=5)#graficamos los ceros en lazo directo
    if anotation:
        for i in p:
            ax.annotate(f'{np.round(i,3)}', xy=(i.real+0.02,i.imag+0.02))

        for j in z:
            ax.annotate(f'{np.round(j,3)}', xy=(j.real+0.02,j.imag+0.02))
    
    plt.title('LGR')
    plt.xlabel('Real')
    plt.ylabel('Imag')
    plt.grid(grid)
    if not xlim is None:
        plt.xlim(xlim)
    if not ylim is None:
        plt.ylim(ylim)
    
def Bode(sys,graf=True):
    mag, phase, omega=bode(sys)
    if graf:
        fig,(ax1,ax2)=plt.subplots(2,1)
        ax1.semilogx(omega,20*np.log10(mag))
        ax1.grid(True)
        ax2.semilogx(omega,180*phase/np.pi)
        ax2.grid(True)
    else:
        return mag, phase, omega

def PIDG(sys,kp=1,ki=0,kd=0,ax=None,alpha=0.1):
    params=parameters(sys,params='tp,ts,vs,vp',print_params=False)
    t,y=step(sys)
    plot(t,y,params=params,ax=ax,label='SISTEMA ORIGINAL')
    pid=tf([alpha*kd*kp+kd,kp+alpha*ki*kd,ki],[alpha*kd,1,0])
    ser=serie(sys,pid)
    fed=feedback(ser,tf([1],[1]))
    paramsc=parameters(fed,params='tp,ts,vs,vp',print_params=False)
    tc,yc=step(fed)
    plot(tc,yc,params=paramsc,label='SISTEMA CONTROLADO',ax=ax,c='r',lw=2)

    
