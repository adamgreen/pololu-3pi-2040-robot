from machine import Pin
import array

_DONE = const(0)
_READ_LINE = const(1)
_READ_BUMP = const(2)
_state = _DONE
_qtr = None

class _IRSensors():
    def __init__(self):
        from ._lib.qtr_sensors import QTRSensors

        self.ir_down = Pin(26, Pin.IN)
        self.ir_bump = Pin(23, Pin.IN)
        
        global _qtr
        if not _qtr:
            _qtr = QTRSensors(4, 16)
        self.qtr = _qtr
        
        self.reset_calibration()
        self.reset_calibration()
        
class LineSensors(_IRSensors):
    def _state(self):
        # for testing
        global _state
        return _state
    
    def reset_calibration(self):
        self.cal_min = array.array('H', [1024,1024,1024,1024,1024])
        self.cal_max = array.array('H', [0,0,0,0,0])
        
    def calibrate(self):
        data = self.read()
        for i in range(5):
            self.cal_min[i] = min(data[i], self.cal_min[i])
        for i in range(5):
            self.cal_max[i] = max(data[i], self.cal_max[i])
    
    def start_read(self):
        global _state
        self.ir_bump.init(Pin.IN)
        self.ir_down.init(Pin.OUT, value=1)
        _state = _READ_LINE
        self.qtr.run()
    
    def read(self):
        global _state
        if _state != _READ_LINE:
            self.start_read()
        data = self.qtr.read()
        
        self.ir_down.init(Pin.IN)
        self.ir_bump.init(Pin.IN)
        _state = _DONE
        return data[2:]
    
    @micropython.viper
    def read_calibrated(self):
        data = self.read()
        d = ptr16(data)
        cal_min = ptr16(self.cal_min)
        cal_max = ptr16(self.cal_max)
        for i in range(5):
            if cal_min[i] >= cal_max[i] or d[i] < cal_min[i]:
                d[i] = 0
            elif d[i] > cal_max[i]:
                d[i]= 1000
            else:
               d[i] = (d[i] - cal_min[i])*1000 // (cal_max[i] - cal_min[i])
        return data
        
class BumpSensors(_IRSensors):
    def _state(self):
        # for testing
        global _state
        return _state
        
    def reset_calibration(self):
        self.cal_min = array.array('H', [1024,1024])
        self.cal_max = array.array('H', [0,0])
            
    def calibrate(self):
        data = self.read()
        for i in range(2):
            self.cal_min[i] = min(data[i], self.cal_min[i])
        for i in range(2):
            self.cal_max[i] = max(data[i], self.cal_max[i])
        
    def start_read(self):
        global _state
        self.ir_down.init(Pin.IN)
        self.ir_bump.init(Pin.OUT, value=1)
        _state = _READ_BUMP
        self.qtr.run()
    
    def read(self):
        global _state
        if _state != _READ_BUMP:
            self.start_read()
        data = self.qtr.read()
        
        self.ir_down.init(Pin.IN)
        self.ir_bump.init(Pin.IN)
        _state = _DONE
        return data[0:2]
    
    @micropython.viper
    def read_calibrated(self):
        data = self.read()
        d = ptr16(data)
        cal_min = ptr16(self.cal_min)
        cal_max = ptr16(self.cal_max)
        for i in range(2):
            if 2 * d[i] > cal_min[i] + cal_max[i]:
                d[i] = 1000
            else:
                d[i] = 0
        return data
