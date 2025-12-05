import numpy as np
from scipy.optimize import fsolve

# PT100 - IEC 60751
R0 = 100.0
A = 3.9083e-3
B = -5.775e-7
C = -4.184e-12

class Conversor:
    @staticmethod
    def callendar_van_dusen(T):
        # C=0 para temperaturas positivas
        if (T>=0):
            return R0*(1 + A*T + B*T**2)
        else:
            return R0*(1 + A*T + B*T**2 + C*T**3*(T-100))
        
    @staticmethod
    def pt100_para_celsius(resistencia: float):
        f = lambda T: Conversor.callendar_van_dusen(T) - resistencia
        temperatura = fsolve(f, 0)[0]
        return float(temperatura)
            
    