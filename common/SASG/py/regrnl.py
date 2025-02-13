import abc
import os
import sys, getopt
import argparse
import time
import pandas as pd
import numpy as np
from sklearn.svm import SVR
import random


InitTicks = time.time()

def TIME_COST (Name):
    print ("@@@@ ", Name, " time cost: ", str (time.time() - InitTicks))

class BrValue ():
    def __init__ (self, Key, Type, Predict, Value):
        self.Key     = Key
        self.Type    = Type
        self.Pred    = Predict
        self.Values  = []
        self.Values  += Value

    def AddValue (self, Value):
        self.Values  += Value
        

class BrVSet ():
    Pred2Mean = {}
    Pred2Mean [0]  = "FCMP: Always false"
    Pred2Mean [1]  = "FCMP: True if ordered and equal"
    Pred2Mean [2]  = "FCMP: True if ordered and greater than"
    Pred2Mean [3]  = "FCMP: True if ordered and greater than or equal"
    Pred2Mean [4]  = "FCMP: True if ordered and less than"
    Pred2Mean [5]  = "FCMP: True if ordered and less than or equal"
    Pred2Mean [6]  = "FCMP: True if ordered and operands are unequal"
    Pred2Mean [7]  = "FCMP: True if ordered (no nans)"
    Pred2Mean [8]  = "FCMP: True if unordered: isnan(X) | isnan(Y)"
    Pred2Mean [9]  = "FCMP: True if unordered or equal"
    Pred2Mean [10] = "FCMP: True if unordered or greater than"
    Pred2Mean [11] = "FCMP: True if unordered, greater than, or equal"
    Pred2Mean [12] = "FCMP: True if unordered or less than"
    Pred2Mean [13] = "FCMP: True if unordered, less than, or equal"
    Pred2Mean [14] = "FCMP: True if unordered or not equal"
    Pred2Mean [15] = "FCMP: Always true (always folded)"

    Pred2Mean[32]  = "ICMP: equal"
    Pred2Mean[33]  = "ICMP: not equal"
    Pred2Mean[34]  = "ICMP: unsigned greater than"
    Pred2Mean[35]  = "ICMP: unsigned greater or equal"
    Pred2Mean[36]  = "ICMP: unsigned less than"
    Pred2Mean[37]  = "ICMP: unsigned less or equal"
    Pred2Mean[38]  = "ICMP: signed greater than"
    Pred2Mean[39]  = "ICMP: signed greater or equal"
    Pred2Mean[40]  = "ICMP: signed less than"
    Pred2Mean[41]  = "ICMP: signed less or equal"

    Pred2Mean[255]  = "SWITCH: enum"
    
    def __init__ (self, Path=["branch_vars.bv"]):
        self.Path = Path
        self.BrVals = {}
        
        self.LoadBrVars ()
        #self.Show ()

    def Show (self):
        for VKey, BV in self.BrVals.items ():
            PredMean = BrVSet.Pred2Mean.get (BV.Pred)
            if PredMean == None:
                PredMean = "None"
            print ("VrKey:%d, Type:%s, Pred:%d[%s], Value: " %(VKey, BV.Type, BV.Pred, PredMean), end="")
            print (BV.Values)

    def GetValueList (self, Pred, Value):
        ValueList = []
        if Pred >= 0 and Pred <= 15:
            pass
        else:
            if Pred == 32:
               ValueList.append (Value)
               ValueList.append (Value - 1)
            elif Pred == 33:
               ValueList.append (Value + 1)
               ValueList.append (Value - 1)
            elif Pred in [34, 38]:
                ValueList.append (Value + 1)
                ValueList.append (Value - 1)
            elif Pred in [35, 39]:
                ValueList.append (Value)
                ValueList.append (Value + 1)
                ValueList.append (Value - 1)
            elif Pred in [36, 40]:
                ValueList.append (Value - 1)
                ValueList.append (Value + 1)
            elif Pred in [37, 41]:
                ValueList.append (Value)
                ValueList.append (Value - 1)
                ValueList.append (Value + 1)
            elif Pred == 255:
                ValueList.append (Value)
                ValueList.append (Value + 1)

        return ValueList
                
    
    def LoadBrVars (self):
        for path in self.Path:
            if len (path) == 0:
                continue
            with open(path, 'r', encoding='latin1') as BrVF:
                for line in BrVF:
                    Item = list (line.split (":"))
                    Key  = int (Item[0])
                    Type = Item[1]
                    Pred = int (Item[2])
                    Value= int (Item[3])

                    ValueList = self.GetValueList (Pred, Value)
                    VrKey = int (str (Key) + str(Pred))
                    Bv = self.BrVals.get (VrKey)
                    if Bv == None:      
                        self.BrVals[VrKey] = BrValue (Key, Type, Pred, ValueList)
                    else:
                        Bv.AddValue (ValueList)
                

def Load (InputFile):
    DF = pd.read_csv(InputFile, header=0)
    DF = DF.sort_values(by=[DF.columns[0]])

    Headers = DF.columns.values
    y_Name = DF.columns[0]
    X_Name = DF.columns[1]
        
    y  = np.array (DF.loc[ :, Headers[0]])
    X  = np.array (DF.loc[ :, Headers[1]]).reshape(-1, 1)

    Len = int (len (X) * 0.8)
    X_Train = X [0:Len]
    y_Train = y [0:Len]
    X_Test  = X [Len:-1]
    y_Test  = y [Len:-1]

    return X_Name, y_Name, X_Train, y_Train, X_Test, y_Test

class RegrBase (metaclass=abc.ABCMeta):

    CList     = [1, 0.01, 0.1, 0.3, 0.5, 0.7, 0.9, 5, 10, 20, 50, 100, 500, 1000, 2000, 5000]
    EpsnList  = [0.1, 0.01, 0.05, 0.3, 0.5, 0.7, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0, 3.0, 5.0]
    Coef0List = [0, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    def __init__ (self, Kernal):
        self.Kernal    = Kernal
        self.Model     = None
        self.FitModel  = None
        self.FitC     = -1
        self.FitEpsn  = -1
        self.FitGamma = -1
        self.FitCoef0 = -1

    def SVs (self):
        return self.Model.support_

    @abc.abstractmethod
    def Fit (self):
        print ("[RegrBase] start to fit...")
        return 0
    
    def Predict (self, X):
        return self.FitModel.predict (X)
        

class RbfReg (RegrBase):
    def __init__ (self, Kernal):
        super(RbfReg, self).__init__(Kernal)

    def Fit (self, X_Train, y_Train, X_Test, y_Test):
        FitFailNum = 0
        Distance = 4294967200
        for C in RegrBase.CList:
            for epsilon in RegrBase.EpsnList:
                #for gamma in RegrBase.GammaList:
                if FitFailNum >= 1:
                    break
                    
                Model    = SVR(kernel="rbf", C=C, epsilon=epsilon, max_iter=50000000)
                FitModel = Model.fit (X_Train, y_Train)
                Predicts = FitModel.predict (X_Test)

                if Model.fit_status_ == 1:
                    FitFailNum += 1
                    
                CurDis   = 0
                for ix in range(len (y_Test)):
                    CurDis += abs (y_Test[ix] - Predicts[ix]) / y_Test[ix]
                CurDis = CurDis / len (y_Test)
                
                if CurDis < Distance:
                    self.Model    = Model
                    self.FitModel = FitModel
                        
                    self.FitC     = C
                    self.FitEpsn  = epsilon
                    #self.FitGamma = gamma
                        
                    Distance = CurDis
        
        print ("[RbfReg]Min-Dis: %.2f, FitC:%f, FitEpsn:%f, FitGamma:%f" %(Distance, self.FitC, self.FitEpsn, 0))
        return Distance

class PolyReg (RegrBase):
    def __init__ (self, Kernal):
        super(PolyReg, self).__init__(Kernal)
        self.FitCoef0 = -1

    def Fit (self, X_Train, y_Train, X_Test, y_Test):
        FitFailNum = 0
        Distance = 1
        for Coef0 in RegrBase.Coef0List:
            for epsilon in RegrBase.EpsnList:
                if FitFailNum >= 1:
                    break
                #print ("PolyReg -> Coef0 = %f, epsilon = %f\r\n " %(Coef0, epsilon))
                Model    = SVR(kernel="poly", epsilon=epsilon, coef0=Coef0, max_iter=50000000)
                FitModel = Model.fit (X_Train, y_Train)
                Predicts = FitModel.predict (X_Test)

                if Model.fit_status_ == 1:
                    FitFailNum += 1
                  
                CurDis   = 0
                for ix in range(len (y_Test)):
                    CurDis += abs (y_Test[ix] - Predicts[ix]) / y_Test[ix]
                CurDis = CurDis / len (y_Test)
                        
                if CurDis < Distance:
                    self.Model    = Model
                    self.FitModel = FitModel
                            
                    self.FitCoef0 = Coef0
                    self.FitEpsn  = epsilon

                    Distance = CurDis
        
        print ("[PolyReg]Min-Dis: %.2f, FitCoef0:%f, FitEpsn:%f" %(Distance, self.FitCoef0, self.FitEpsn))
        return Distance

class LinearReg (RegrBase):
    def __init__ (self,     Kernal):
        super(LinearReg, self).__init__(Kernal)

    def Fit (self, X_Train, y_Train, X_Test, y_Test):
        FitFailNum = 0
        Distance = 1
        for C in RegrBase.CList:
            for epsilon in RegrBase.EpsnList:
                if FitFailNum >= 1:
                    break
                
                Model    = SVR(kernel="linear", C=C, epsilon=epsilon, max_iter=50000000)
                FitModel = Model.fit (X_Train, y_Train)
                Predicts = FitModel.predict (X_Test)

                if Model.fit_status_ == 1:
                    FitFailNum += 1

                CurDis   = 0
                for ix in range(len (y_Test)):
                    CurDis += abs (y_Test[ix] - Predicts[ix])/y_Test[ix]
                CurDis = CurDis / len (y_Test)
                        
                if CurDis < Distance:
                    self.Model    = Model
                    self.FitModel = FitModel
                        
                    self.FitC     = C
                    self.FitEpsn  = epsilon
                        
                    Distance = CurDis

        print ("[LinearReg]Min-Dis: %.2f, FitC:%f, FitEpsn:%f" %(Distance, self.FitC, self.FitEpsn))
        return Distance


def Plot (InputFile, SVRs, X_Name, y_Name, X_Train, y_Train, X_Test, y_Test):
    import matplotlib.pyplot as plt
    
    lw = 2
    MdColors = ["m", "c", "g"]
    fig, axes = plt.subplots(nrows=1, ncols=len(SVRs), figsize=(14, 6), sharey=True)
    for ix, svr in enumerate(SVRs):
        PredTrain = svr.Predict(X_Train)
        PredTest  = svr.Predict(X_Test)
        axes[ix].plot(
            X_Train,
            PredTrain,
            color=MdColors[ix],
            lw=lw,
            label="{} model".format(svr.Kernal),
        )
        axes[ix].scatter(
            X_Train[svr.SVs()],
            y_Train[svr.SVs()],
            facecolor="none",
            edgecolor=MdColors[ix],
            s=50,
            label="{} SVs".format(svr.Kernal),
        )
        axes[ix].scatter(
            X_Train[np.setdiff1d(np.arange(len(X_Train)), svr.SVs())],
            y_Train[np.setdiff1d(np.arange(len(X_Train)), svr.SVs())],
            facecolor="none",
            edgecolor="k",
            s=50,
            label="other training data",
        )
        axes[ix].plot(
            X_Test,
            PredTest,
            color='b',
            lw=lw,
            label="{} test predict".format(svr.Kernal),
        )
        axes[ix].scatter(
            X_Test,
            y_Test,
            facecolor="none",
            edgecolor='b',
            s=50,
            label="{} test data".format(svr.Kernal),
        )
        axes[ix].legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.1),
            ncol=1,
            fancybox=True,
            shadow=True,
        )

    fig.text(0.5, 0.04, X_Name, ha="center", va="center")
    fig.text(0.06, 0.5, y_Name, ha="center", va="center", rotation="vertical")
    fig.suptitle("SVRs of " + InputFile, fontsize=14)
    plt.savefig(os.path.splitext(InputFile)[0] + ".png")
    plt.close()        


def RegMain (InputFile, DisThreshold=0.1, Directory=None, IsPlot=False):
    X_Name, y_Name, X_Train, y_Train, X_Test, y_Test = Load (InputFile)
    if len (X_Train) == 0 or len (X_Test) == 0:
        return
    
    SvrRbf    = RbfReg ("Rbf")
    SvrPoly   = PolyReg ("Polynomial")
    SvrLinear = LinearReg ("Linear")
    
    SVRs = [SvrLinear, SvrPoly, SvrRbf]
    MainSvr = None
    Distance = 1
    for svr in SVRs:
        CurDis = svr.Fit (X_Train, y_Train, X_Test, y_Test)
        if CurDis < Distance:
            Distance = CurDis
            MainSvr  = svr
            if Distance <= DisThreshold:
                break
    print ("@@@ [%s]MinDistance is: %.2f" %(str (MainSvr), Distance))

    if Plot == True:
        Plot (InputFile, SVRs, X_Name, y_Name, X_Train, y_Train, X_Test, y_Test)

    # set the threshold, default: 0.1
    if Distance > DisThreshold:
        return

    # load all files of branch_vars.cv
    if Directory == None:
        Directory = "./"
    Command  = "find " + Directory + " -name branch_vars.bv"
    ALLFiles = os.popen(Command).read()
    PathList = list (ALLFiles.split ('\n'))
    if PathList[0] == '':
        print ("Warning: get no branch_vars.bv, Directory = ....." + Directory)
        return
    BVS = BrVSet (PathList)
    
    #print ("@@@ MainSVR is" + str (MainSvr))
    BlkSeedValues = []   
    for BrKey, BrV in BVS.BrVals.items ():
        Values = np.array(BrV.Values).reshape(-1, 1)
        CurPreds = list (MainSvr.Predict (Values))
        #print (CurPreds)
        BlkSeedValues += CurPreds
        #print ("BrKey: %s, Predicts: %s" % (str(BrKey), str(CurPreds)))

    BsValue = {}
    with open(InputFile+".bs", 'w', encoding='latin1') as BSF:
        for val in BlkSeedValues:
            Value = int (val)
            if (Value & 0xFFFFFFFF00000000) != 0:
                continue
            if BsValue.get (Value) != None:
                continue
            BsValue [Value] = 1
            BSF.write (str(Value) + "\n")
            
    
def InitArgument (parser):
    parser.add_argument('--version', action='version', version='regrnl 1.0')
    
    grp = parser.add_argument_group('Main options', 'One of these (or --report) must be given')
    grp.add_argument('-B', '--bvdir', help='the directory where store files of branch_vars.cv')
    grp.add_argument('-d', '--distance', help='the distance threshold [0, 1]')
    grp.add_argument('-p', '--plot', action='store_true', help='plot the regression results')
                  
    parser.add_argument('filename', nargs='?', help='input file')
    parser.add_argument('arguments', nargs=argparse.REMAINDER, help='arguments to the program')


def main():
    parser = argparse.ArgumentParser()
    InitArgument (parser)

    opts = parser.parse_args()
    if opts.filename is None:
        parser.error('filename is missing: required with the main options')

    if opts.distance is None:
        opts.distance = 0.5

    RegMain (opts.filename, DisThreshold=opts.distance, Directory=opts.bvdir, IsPlot=opts.plot)

if __name__ == "__main__":
   main()
