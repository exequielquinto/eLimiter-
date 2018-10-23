import pandas as pd         
import visa, time    

#Connect to Instruments
rm = visa.ResourceManager()
daq = rm.open_resource('ASRL1::INSTR')
eload1 = rm.open_resource('USB0::0x0A69::0x083E::636002000532::0::INSTR')  #Ch2, Ch1
eload2 = rm.open_resource('USB0::0x0A69::0x083E::636002000381::0::INSTR')  #Ch4, Ch3

#Read Instrument IDs
#print daq.query('*IDN?')
#print eload1.query('*IDN?')
#print eload2.query('*IDN?')

#For load sequence
steps=(0,1,2,3,4,5,6,7,8,9,10)
load=(1.7,1.53,1.36,1.19,1.02,0.85,0.68,0.51,0.34,0.17,0)   #error seems to be coming from 0.2 or 0.1,make it 0.101 and 0.201

#steps=(0,1,2,3)
#load=(0.075,0.05,0.025,0)

#quick check channel
#steps=(0,1,2)    
#load=(0.025,0.125)

print steps
print load

#FUNCTIONS
def burn_in():
    eload1.write('CHAN 3')   #Ch1    
    eload1.write('CURR:STAT:L1 %.4f' % load[0])
    eload1.write('LOAD ON')
    eload1.write('CHAN 1')   #Ch2
    eload1.write('CURR:STAT:L1 %.4f' % load[0])
    eload1.write('LOAD ON')
    eload2.write('CHAN 3')   #Ch3    
    eload2.write('CURR:STAT:L1 %.4f' % load[0])
    eload2.write('LOAD ON')
    eload2.write('CHAN 1')   #Ch4
    eload2.write('CURR:STAT:L1 %.4f' % load[0])
    eload2.write('LOAD ON')
    print ('warming up...')
    print ('time now is')
    print (time.ctime())
def eload_set():
    eload1.write('CHAN 3')   #Ch1    
    eload1.write('CURR:STAT:L1 %.4f' % load[step])
    eload1.write('LOAD ON')
    eload1.write('CHAN 1')   #Ch2
    eload1.write('CURR:STAT:L1 %.4f' % load[step])
    eload1.write('LOAD ON')
    eload2.write('CHAN 3')   #Ch3   
    eload2.write('CURR:STAT:L1 %.4f' % load[step])
    eload2.write('LOAD ON')
    eload2.write('CHAN 1')   #Ch4
    eload2.write('CURR:STAT:L1 %.4f' % load[step])
    eload2.write('LOAD ON')
    print step
    #print ('capturing efficiency every min...')
    #print ('time now is')
    #print (time.ctime())
def measure():
    #Vin Measure
    daq.write('MEAS:VOLT:DC? AUTO,DEF,(@101)')
    time.sleep(0.5)                              
    Vin = float(daq.read())
    temp['A_Vin'] = Vin
    #Iin Measure
    daq.write('MEAS:VOLT:DC? AUTO,DEF,(@110)')
    time.sleep(0.5)                              
    Iin = (float(daq.read()))*1000
    temp['B_Iin'] = Iin          #Amp 1.002 for shunt calibration
    
    #Ch1 Measure  
    eload1.write('CHAN 3')   #Ch1    
    V1 = float(eload1.query('MEASure:VOLTage?'))
    time.sleep(0.5)
    I1 = float(eload1.query('MEASure:CURRent?'))
    #V1 = (eload1.query('MEASure:VOLTage?'))    also works with these
    #print (eload1.query('FETCh:ALLVoltage?'))
    #x=(eload1.query('MEASure:ALLVoltage?'))
    #print x
    #print x[0:10]
    time.sleep(0.5)
    temp['C_Ch1_Vout'] = (V1)
    temp['D_Ch1_Iout'] = (I1)

    #Ch2 Measure
    eload1.write('CHAN 1')   #Ch1    
    V2 = float(eload1.query('MEASure:VOLTage?'))
    time.sleep(0.5)
    I2 = float(eload1.query('MEASure:CURRent?'))
    time.sleep(0.5)
    temp['E_Ch2_Vout'] = (V2)
    temp['F_Ch2_Iout'] = (I2)
    
    #Ch3 Measure  
    eload2.write('CHAN 3')   #Ch1    
    V3 = float(eload2.query('MEASure:VOLTage?'))
    time.sleep(0.5)
    I3 = float(eload2.query('MEASure:CURRent?'))
    time.sleep(0.5)
    temp['G_Ch3_Vout'] = (V3)
    temp['H_Ch3_Iout'] = (I3)

    #Ch4 Measure
    eload2.write('CHAN 1')   #Ch1    
    V4 = float(eload2.query('MEASure:VOLTage?'))
    time.sleep(1)
    I4 = float(eload2.query('MEASure:CURRent?'))
    time.sleep(1)
    temp['I_Ch4_Vout'] = (V4)
    temp['J_Ch4_Iout'] = (I4)
    
    
    #Efficiency
    temp['K_Efficiency'] = ((V1*I1)+(V2*I2)+(V3*I3)+(V4*I4))*100/(Vin*Iin)
    #temp['K_Pout'] = (V4*I4)
    #temp['M_Efficiency'] = (Vin*Iin)
def min_load():
    #Set to less load after finishing test
    eload1.write('CHAN 3')   #Ch1    
    eload1.write('CURR:STAT:L1 %.4f' % load[7])
    eload1.write('LOAD ON')
    eload1.write('CHAN 1')   #Ch2
    eload1.write('CURR:STAT:L1 %.4f' % load[7])
    eload1.write('LOAD ON')
    eload2.write('CHAN 3')   #Ch3    
    eload2.write('CURR:STAT:L1 %.4f' % load[7])
    eload2.write('LOAD ON')
    eload2.write('CHAN 1')   #Ch4
    eload2.write('CURR:STAT:L1 %.4f' % load[7])
    eload2.write('LOAD ON')

burn_in()
time.sleep(6) # burn In time at full full before capturing efficiency
results = pd.DataFrame()

for step in steps:
    
    try:
        eload_set()
    except:
        try:
            print('loadset error1')
            eload_set()
        except:
            print('loadset error2')
            eload_set()
        
    time.sleep(40)   # Delay in seconds before capturing results
    temp = {}
    #measure()
    try:
        measure()
    except:
        try:
            print('measure error1')
            measure()
        except:
            print('measure error2')
            measure()
    
    results = results.append(temp, ignore_index=True)    # 17
    #print results
    print "%.2fV\t%.3fA" % (temp['C_Ch1_Vout'],temp['K_Efficiency'])    # ? on print formatting
    results.to_csv('Results.csv')
min_load()                
print('finished')
