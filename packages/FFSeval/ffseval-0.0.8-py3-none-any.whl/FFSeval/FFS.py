import numpy as np
class Base:
    def __init__(self):
        self.title=None
        self.data=None
        self.res=None
        self.refer=None
    def SetTitle(self,title:str)->None:
        self.title=title
    def Title(self)->str:
        return self.title
    def SetData(self,data:dict):
        self.data=data
    def GetData(self):
        return self.data
    def SetRes(self,res:dict):
        self.res=res
    def GetRes(self):
        return self.res
    def SetRefer(self,refer:str):
        self.refer=refer
    def GetRefer(self):
        return self.refer
    def CalcKc(self):
        nu=self.data['Nu']
        E=self.data['E']
        j1c=self.data['J1c']
        Ed=E/(1-nu*nu)
        return np.sqrt(Ed*j1c)
    def Option1(self,Kr,Lr):
        kk=(1-0.15*Lr*Lr)*(0.3+0.7*np.exp(-0.65*Lr**6))
        flag=False
        if Kr<kk:
            flag=True
        return flag,kk
    def RolfeBarsom(self,Cv,Sy)->float:
        #Cv=self.data['Cv']
        #Sy=self.data['Sy']
        cc=np.array(Cv)
        c=0.6478*(cc/Sy-0.0098)
        K1c=np.sqrt(c)*Sy
        return K1c
class Fatigue:
    '''
    JSME維持規格における炭素鋼および低合金鋼の大気中における疲労亀裂進展特性
    '''
    def __init__(self,cls,data):
        self.cls=cls
        self.cls.SetData(data)
        self.data=data
    def dadN(self,a,c,Pmin,Pmax,R):
        self.data['a']=a
        self.data['c']=c
        self.data['P']=Pmin
        self.cls.SetData(self.data)
        self.cls.Calc()
        resMin=self.cls.GetRes()
        self.data['P']=Pmax
        self.cls.SetData(self.data)
        self.cls.Calc()
        resMax=self.cls.GetRes()
        dKA=resMax['KA']-resMin['KA']
        dKB=resMax['KB']-resMin['KB']
        da=self.FatigueSteel(dKA,R)
        dc=self.FatigueSteel(dKB,R)
        return da,dc,resMax
    def FatigueSteel(self,dK,R):
        S=25.72*(2.88-R)**(-3.07)
        C=3.88e-9*S
        n=3.07
        da=C*dK**n
        return da
    def EvalAC(self,a0,c0,Pmin,Pmax,R,n):
        self.data['a']=a0
        self.data['c']=c0
        self.data['P']=Pmax
        self.cls.SetData(self.data)
        self.cls.Calc()
        res0=self.cls.GetRes()
        a=a0
        c=c0
        for i in range(n):
            da,dc,resMax=self.dadN(a,c,Pmin,Pmax,R)
            a += da/1000
            c += dc/1000
        crack={'a':a,
               'c':c}
        res1=resMax
        return res0,res1,crack
        
        
class Treat:
    def Set(self,spec:str):
        '''
        対象とする解析記号名を文字列でセット
        '''
        spec2=spec.replace("-","_")
        df=self.Registered()
        dd=df[spec2[0]]
        if spec2 not in dd:
            print(spec+' is not registered yet!')
            return
        cls=globals()[spec2]
        instance=cls()
        return instance
    def Registered(self):
        df={'K':[
            'K_1_a_1',
            'K_2_a_3',
            'K_2_b_2',
            'K_2_e_2',
            'K_2_k_2'
        ],'L':[
            'L_1_a',
            'L_2_b'
        ]
        }
        return df
import Kriging as kr
import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from typing import Tuple
import importlib.resources as pkg_resources
from FFSeval import data
class dmanage:
    '''
    係数が表形式で与えられるときに，表データをcsvファイルから読み取り，
    Kriging法で内挿した上で，評価値を返す
    [使用法]二次元の場合*****************************
    dm=dmanage()
    data=dm.Finput('J-2-k-b.csv')
    X,W=dm.CSV2XW(data,1)
    r2_score=dm.KrigCalc(X,W)
    dm.DrawRes(X,W) #鳥観図による確認
    x_val=0.5; y_val=2.0 #評価したい点
    target_point=np.array([[x_val,y_val]])
    w_pred,sigma=dm.Eval(target_point)# w_predが予測値
    [使用法]三次元の場合*****************************
    dm=dmanage()
    data=dm.Finput('J-2-k-b.csv')
    z=[0.0625,0.125,0.25,0.37,0.50]#三次元目のデータリスト(表の数だけ存在)
    X,W=dm.Fconv3D(data,z)
    r2_score=dm.KrigCalc(X,W)
    target_point=np.array([[0.5,2,0.18]])
    w_pred,sigma=dm.Eval(target_point)# w_predが予測値
    '''
    def __init__(self):
        self.df=None
    def Fconv3D(self,data:list,z:list)->Tuple[np.ndarray, np.ndarray]:
        '''
        3次元の入力テーブルに対する対応
        dataの中から，全データの処理を行いX,Wを校正して戻す
        三次元目の情報はz:listで与える
        '''
        # STARTを含む要素の数をカウント
        count = 0
        for sublist in data:
            for item in sublist:
                if "START" in item:
                    count += 1
        nz=len(z)
        if count!=nz:
            print(f'STARTの数{count}とzのサイズ{nz}が一致していない')
            return
        W=np.array([])
        X=np.empty((0,3))
        for i in range(count):
            ith=i+1
            df=self.dRead(data,ith)
            xval=df['xval']
            yval=df['yval']
            xn=len(xval)
            yn=len(yval)
            for iy in range(yn):
                for ix in range(xn):
                    d=[yval[iy],xval[ix],z[i]]
                    X=np.append(X,[d], axis=0)
                    W=np.append(W,df['arr'][iy,ix])
        return X,W            
    def Finput(self,fname:str)->list:
        '''
        csvファイルを読み取りリストに格納する
        '''
        with pkg_resources.open(data,fname, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            data=[]
            for row in reader:
                data.append(row)
        return data        
    def dRead(self,data:list,ith:int)->dict:
        '''
        dataのith番目のテーブルを辞書として返す
        '''
        n=len(data)
        ii=0
        flag=False
        res=[]
        l=0
        for ll in data:
            if ll[0]=='START':
                ii+=1
                if ii==ith:
                    flag=True
                    l+=1
                    continue
            if flag and l!=0:
                if ll[0]=='END':
                    break
                if l==1:
                    nx=int(ll[0])
                    ny=int(ll[1])
                    l+=1
                    continue
                if l==2:
                    numlist=[float(x) for x in ll[:nx]]
                    xval=numlist
                    l+=1
                    continue
                if l==3:
                    numlist=[float(x) for x in ll[:ny]]
                    yval=numlist
                    l+=1
                    continue
                numlist=[float(x) for x in ll[:nx]]
                res.append(numlist)
                l+=1
        arr=np.array(res)
        df={}
        df['xval']=xval
        df['yval']=yval
        df['arr']=arr
        return df
    def MakeInp(self,df:dict)->Tuple[np.ndarray, np.ndarray]:
        '''
        辞書型データを，Kriging入力用のnp.arrayに変換する
        '''
        xval=df['xval']
        yval=df['yval']
        xn=len(xval)
        yn=len(yval)
        W=np.array([])
        X=np.empty((0,2))
        for iy in range(yn):
            for ix in range(xn):
                d=[yval[iy],xval[ix]]
                X=np.append(X,[d], axis=0)
                W=np.append(W,df['arr'][iy,ix])
        return X,W
    def CSV2XW(self,data:list,ith:int)->Tuple[np.ndarray, np.ndarray]:
        df=self.dRead(data,ith)
        X,W=self.MakeInp(df)
        self.df=df
        return X,W
    def GetDf(self):
        return self.df
    def KrigCalc(self,X,W,alpha=5e-4):
        self.krig=kr.Kriging()
        self.krig.setData(X,W)
        r2_score=self.krig.Fit(alpha=alpha)
        return r2_score
    def Eval(self,target_point:np.array)->float:
        #target_point = np.array([[x, y]])  
        w_pred,sigma=self.krig.Predict(target_point)
        return w_pred[0],sigma        
    def DrawRes(self,X,W)->None:
        # 1. 描画用のメッシュグリッドを作成
        x = np.linspace(np.min(X[:,0]), np.max(X[:,0]), 50)
        y = np.linspace(np.min(X[:,1]), np.max(X[:,1]), 50)
        X_grid, Y_grid = np.meshgrid(x, y)

        # 2. メッシュ座標を一次元にして予測
        XY = np.vstack([X_grid.ravel(), Y_grid.ravel()]).T

        # Kriging モデルで予測（タプルで返る）
        Z_pred, _ = self.krig.Predict(XY)

        # 予測値をグリッド形状に整形
        Z_grid = Z_pred.reshape(X_grid.shape)

        # 4. 描画
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        # 予測面
        ax.plot_surface(X_grid, Y_grid, Z_grid, cmap='viridis', alpha=0.7)

        # 元データ点も重ねる
        #ax.scatter(X[:,0], X[:,1], W, color='r', s=30, label='Data points')
        # 予測に使ったデータ点を赤い球で表示
        ax.scatter(X[:, 0], X[:, 1], W, color='black', s=30, marker='^', label='Training data')
        # 軸ラベル
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('W')

        # タイトル・凡例
        ax.set_title('Kriging Model Surface')
        ax.legend()
        plt.show()                

class J_2_k_b(Base):
    def __init__(self):
        super().SetTitle('周方向貫通亀裂　Zahoorの解')
        super().SetRefer('Zahoor, A.:Ductile Fracture Handbook Volume 1,EPRI NP-6301-D,1989')
    def Calc(self):
        df=super().GetData()
        th=df['Th']/180.0*np.pi
        plane=df['plane']
        if plane=='stress': beta=2
        if plane=='strain': beta=6
        M=df['M']
        R=df['R']
        t=df['t']
        P=df['P']
        St=P/(2.*np.pi*R*t)
        Sb=M/(np.pi*R*R*t)
        S0=df['S0']
        P0=2*S0*R*t*(np.pi-th-2*np.arcsin(0.5*np.sin(th)))
        M0=4*S0*R*R*t*(np.cos(th/2)-0.5*np.sin(th))
        lam=M/P/R
        P0d=0.5*(-lam*R*P0*P0/M0+np.sqrt((lam*R*P0*P0/M0)**2+4*P0*P0))
        n=df['n']
        dm=dmanage()
        x=lam/(1.+lam)
        data=dm.Finput('J-2-k-b.csv')
        z=[0.0625,0.125,0.25,0.37,0.50]#三次元目のデータリスト(表の数だけ存在)
        X,W=dm.Fconv3D(data,z)
        r2_score=dm.KrigCalc(X,W)
        target_point=np.array([[x,n,th/np.pi]])
        h1,sigma=dm.Eval(target_point)
        E=df['E']
        alpha=df['alpha']
        e0=df['e0']
        the=th*(1+(1/beta)*((n-1)/(n+1))*((St*Ft+Sb*Fb)**2/S0/S0)/(1+(P/P0d)**2))
        ft=(the/np.pi)*(1+A*(5.3303*(the/np.pi)**1.5+18.773*(the/np.pi)**4.24))**2
        fb=(the/np.pi)*(1+A*(4.5967*(the/np.pi)**1.5+2.6422*(the/np.pi)**4.24))**2
        J=ft*P*P/(4*R*t*t*E)+fb*M*M/(R*R*R*t*t*E)+alpha*S0*e0*R*(np.pi-th)*(th/np.pi)*h1*(P/P0d)**(n+1)
        res={'J':J}
        super().SetRes(res)


class K_1_a_1(Base):
    def __init__(self):
        super().SetTitle('平板の半楕円表面亀裂，Raju-Newmanの解')
        super().SetRefer('Newman,J.C>Jr., and Raju,I.S.:Stress-Intensity Factor Equations for Cracks in Three-Dimentional Finite Bodies Subjected to Tension and Bending Loads, NASA Technical Memorandum, 85793, NASA,1984')
    def Calc(self):
        df=super().GetData()
        a=df['a']
        c=df['c']
        b=df['b']
        t=df['t']
        P=df['P']
        M=df['M']
        Sm=P/(2*b*t)
        Sb=3*M/(b*t*t)
        if a/c <=1.0:
            Q=1+1.464*(a/c)**1.65
            g=1
            fphai=1
            fw=np.sqrt(1.0/np.cos(np.pi*c/(2*b)*np.sqrt(a/t)))
            H=1+(-1.22-0.12*a/c)*a/t+(0.55-1.05*(a/c)**0.75+0.47*(a/c)**1.5)*(a/t)**2
            FA=(1.13-0.09*a/c+(-0.54+0.89/(0.2+a/c))*(a/t)**2+(0.5-1/(0.65+a/c)+14*(1-a/c)**24)*(a/t)**4)*g*fphai*fw
        else:
            Q=1+1.464*(c/a)**1.65
            g=1
            fphai=np.sqrt(c/a)
            fw=np.sqrt(1.0/np.cos(np.pi*c/(2*b)*np.sqrt(a/t)))
            FA=(np.sqrt(c/a)*(1+0.04*c/a)+0.2*(c/a)**4*(a/t)**2-0.11*(c/a)**4*(a/t)**4)*g*fphai*fw
            H=1+(-2.11+0.77*c/a)*a/t+(0.55-0.72*(c/a)**0.75+0.14*(c/a)**1.5)*(a/t)**2
        KA=FA*(Sm+H*Sb)*np.sqrt(np.pi*a/Q)
        if a/c <=1.0:
            Q=1+1.464*(a/c)**1.65
            g=1.1+0.35*(a/t)**2
            fphai=np.sqrt(a/c)
            fw=np.sqrt(1.0/np.cos(np.pi*c/(2*b)*np.sqrt(a/t)))
            FB=(1.13-0.09*a/c+(-0.54+0.89/(0.2+a/c))*(a/t)**2+(0.5-1/(0.65+a/c)+14*(1-a/c)**24)*(a/t)**4)*g*fphai*fw
            H=1-0.34*a/t-0.11*a/c*a/t
        else:
            Q=1+1.464*(c/a)**1.65
            g=1.1+0.35*c/a*(a/t)**2
            fphai=1
            fw=np.sqrt(1.0/np.cos(np.pi*c/(2*b)*np.sqrt(a/t)))
            FB=(np.sqrt(c/a)*(1+0.04*c/a)+0.2*(c/a)**4*(a/t)**2-0.11*(c/a)**4*(a/t)**4)*g*fphai*fw
            H=1+(-0.04-0.41*c/a)*a/t+(0.55-1.93*(c/a)**0.75+1.38*(c/a)**1.5)*(a/t)**2
        KB=FB*(Sm+H*Sb)*np.sqrt(np.pi*a/Q)
        res={
            'KA':KA,
            'KB':KB
        }
        super().SetRes(res)
class K_2_a_3(Base):
    def __init__(self):
        super().SetTitle('軸方向無い表面半楕円表面亀裂，Zahoorの解')
        super().SetRefer('Zahoor,A.:Ductile Fracture Handbook Volume 3,EPRI NP-6301-D,1991')
    def Calc(self):
        df=super().GetData()
        Ro=df['Ro']
        Ri=df['Ri']
        p=df['p']
        Sm=(Ro*Ro+Ri*Ri)/(Ro*Ro-Ri*Ri)*p
        a=df['a']
        c=df['c']
        t=df['t']
        ar=(a/t)/(a/c)**0.58
        FA=0.25+(0.4759*ar+0.1262*ar*ar)/(0.102*(Ri/t)-0.02)**0.1
        KA=FA*Sm*np.sqrt(np.pi*t)
        FB=FA*(1.06+0.28*(a/t)**2)*(a/c)**0.41
        KB=FB*Sm*np.sqrt(np.pi*t)
        res={'KA':KA,
             'KB':KB}
        super().SetRes(res)
class K_2_b_2(Base):
    def __init__(self):
        super().SetTitle('軸方向内表面長い表面亀裂，Zahoorの解')
        super().SetRefer('Zahoor,A.:Closed Form Expressions for Fracture Mechanics Analysis of Cracked Pipes, Trans.ASME, J. of Pressure Vessel Technology,107,p.203,1987')
    def Calc(self):
        df=super().GetData()
        Ro=df['Ro']
        Ri=df['Ri']
        p=df['p']
        Sm=2*Ro*Ro/(Ro*Ro-Ri*Ri)*p
        a=df['a']
        t=Ro-Ri
        if Ri/t >=5.0 and Ri/t<10.0:
            A=(0.125*(Ri/t)-0.25)**0.25
        if Ri/t >=10.0 and Ri/t<=20.0:
            A=(0.2*(Ri/t)-1)**0.25
        F=1.1+A*(4.951*(a/t)**2+1.092*(a/t)**4)
        K=F*Sm*np.sqrt(np.pi*a)
        res={'K':K}
        super().SetRes(res)
class K_2_e_2(Base):
    def __init__(self):
        super().SetTitle('軸方向貫通亀裂，ASME Code Case N-513の解')
        super().SetRefer('ASME Boiler and Pressure Vessel Code, Code Case N-513, Evaluation Criteria for Temporary Acceptance of Flaws in Calss 3 Piping, 1997')
    def Calc(self):
        df=super().GetData()
        p=df['p']
        R=df['R']
        t=df['t']
        Sm=p*R/t
        c=df['c']
        l=c/np.sqrt(R*t)
        F=1+0.072449*l+0.64856*l*l-0.2327*l*l*l+0.038154*l**4-0.0023487*l**5
        K=F*Sm*np.sqrt(np.pi*c)
        res={'K':K}
        super().SetRes(res)
class K_2_k_2(Base):
    def __init__(self):
        super().SetTitle('周方向貫通亀裂，ASME Code Case N-513の解')
        super().SetRefer('ASME Boiler and Pressure Vessel Code, Code Cae N-513,Evaluation Criteria for Temporary Acceptance of Flaws in Class 3 Piping,1997')
    def Calc(self):
        df=super().GetData()
        R=df['R']
        c=df['c']
        P=df['P']
        M=df['M']
        t=df['t']
        Sm=P/(2*np.pi*R*t)
        Sbg=M/(np.pi*R*R*t)
        evaluate_cubic = lambda x, c: c[0] + c[1]*x + c[2]*x**2 + c[3]*x**3
        x=R/t
        coeffs=[-2.02917,1.67763,-0.07987,0.00176]
        Am=evaluate_cubic(x,coeffs)
        coeffs=[7.09987,-4.42394,0.21036,-0.00463]
        Bm=evaluate_cubic(x,coeffs)
        coeffs=[7.79661,5.16676,-0.24577,0.00541]
        Cm=evaluate_cubic(x,coeffs)
        coeffs=[-3.26543,1.52784,-0.072698,0.0016011]
        Abg=evaluate_cubic(x,coeffs)
        coeffs=[11.36322,-3.91412,0.18619,-0.004099]
        Bbg=evaluate_cubic(x,coeffs)
        coeffs=[-3.18609,3.84763,-0.18304,0.00403]
        Cbg=evaluate_cubic(x,coeffs)
        evaluate_F = lambda x, c: c[0] + c[1]*x**1.5 + c[2]*x**2.5 + c[3]*x**3.5
        x=c/(np.pi*R)
        coeffs=[1,Am,Bm,Cm]
        Fm=evaluate_F(x,coeffs)
        coeffs=[1,Abg,Bbg,Cbg]
        Fbg=evaluate_F(x,coeffs)
        K=(Fm*Sm+Fbg*Sbg)*np.sqrt(np.pi*c)
        res={'K':K
            }
        super().SetRes(res)


class L_1_a(Base):
    def __init__(self):
        super().SetTitle('平板の亀裂，半楕円表面亀裂')
        super().SetRefer('Dillstrom,P.andSattari-Far,I.:Limit Load Solutions for Surface Cracks in Plates and Cylinders, RSE R & D Report,No.2002/01,Det Norske Veritas AB 2002')
    def Calc(self):
        df=super().GetData()
        w=df['b']
        a=df['a']
        t=df['t']
        P=df['P']
        M=df['M']
        l=df['c']*2
        Sy=df['Sy']
        Sm=P/(2*w*t)
        Sb=3*M/(w*t*t)
        z=a*l/(t*(l+2*t))
        Lr=((1-z)**1.58*Sb/3+np.sqrt((1-z)**3.16*Sb*Sb/9+(1-z)**3.14*Sm*Sm))/((1-z)**2*Sy)
        res={'Lr':Lr}
        super().SetRes(res)

        
        
class L_2_b(Base):
    def __init__(self):
        super().SetTitle('軸方向内表面長い表面亀裂')
        super().SetRefer('Kumar V.,German M.D. and Shih C.F.:EPRI NP-1931,Electric Power Research Institute, Palo Alto,CA,July 1981')
    def Calc(self):
        df=super().GetData()
        a=df['a']
        t=df['t']
        Sy=df['Sy']
        Ri=df['Ri'] 
        p=df['p']
        z=a/t
        p0=(2/np.sqrt(3))*Sy*(t/Ri)
        pc=p0*((1-z)/(1+z/(Ri/t)))
        Lr=p/pc
        res={'Lr':Lr,
             'pc':pc}
        super().SetRes(res)
        