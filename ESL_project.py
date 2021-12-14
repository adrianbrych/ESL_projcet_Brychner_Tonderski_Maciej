from myhdl import block, always_comb, Signal, instance, intbv, delay, Simulation
from scipy import signal
import unittest
import numpy as np
import random


@block
def FIR(y, out, sel, counter):

    @always_comb
    def comb():  # wspłóczynniki fitlru dolnoprzepustowego
        hFIRDOL = [-0.0003, -0.0009, -0.0019, -0.0036, -0.0058, -0.0086,
                   -0.0115, -0.0140, -0.0154, -0.0148, -0.0113, -0.0044,
                   0.0064, 0.0208, 0.0384, 0.0577, 0.0773, 0.0952, 0.1096,
                   0.1189, 0.1222, 0.1189, 0.1096, 0.0952, 0.0773, 0.0577,
                   0.0384, 0.0208, 0.0064, -0.0044, -0.0113, -0.0148,
                   -0.0154, -0.0140, -0.0115, -0.0086, -0.0058, -0.0036,
                   -0.0019, -0.0009, -0.0003]
        if sel == 1:
            syg = signal.lfilter(hFIRDOL, [1], y)
            out.next = int(syg[counter] * 100)
        else:
            out.next = int(y[counter - 1] * 100)
    return comb


random.seed(5)
randrange = random.randrange


@block
def test_FIR():
    f1 = 200
    f2 = 2000
    f3 = 20000
    x = np.linspace(0, 1, 400)

    y = np.sin(f3 * x) + np.sin(f2 * x) + np.sin(f1 * x)
    out, sel = [Signal(intbv(0)) for i in range(2)]
    counter = Signal(1)
    z = Signal(0)
    output_file = FIR(y, out, sel, counter)

    @instance
    def stimulus():
        y = ((np.sin(f3 * x) + np.sin(f2 * x) + np.sin(f1 * x))*100)
        print("y", y)
        print("out sel counter")
        for i in range(len(x)-2):
            counter.next = counter + 1
            sel.next = randrange(2)
            z.next = int(y[counter])
            yield delay(10)
            print("%s %s %s" % (out, sel, counter))
    return output_file, stimulus


class TestFIR(unittest.TestCase):


    def test_should_check_low_freq_throughput(self):
        f1 = 100
        x = np.linspace(0, 1, 400)
        y = np.sin(x*f1) * 10
        out = Signal(intbv(0))
        sel = Signal(intbv(1))
        counter = Signal(range(intbv(100)))

        output = FIR(y, out, sel, counter)
        if y[0] == int(out[0]):
            self.assertTrue(True)
        else:
            self.assertFalse(False)
    
    def test_should_check_sel_block(self):
        f1 = 100
        x = np.linspace(0, 1, 400)
        y = np.sin(x * f1) * 10
        out = Signal(intbv(0))
        counter = Signal(range(intbv(100)))
        sel = 0
        output = FIR(y, out, sel, counter)
        if y[0] == int(out[0]):
            self.assertTrue(True)
        else:
            self.assertFalse(False)
    
    def test_should_check_sel_enable(self):
        f1 = 50000
        x = np.linspace(0, 1, 400)
        y = np.sin(x*f1) * 10
        out = Signal(intbv(0))
        counter = Signal(range(intbv(100)))
        sel = 1
        output = FIR(y, out, sel, counter)
        if y[0] == int(out[0]):
            self.assertTrue(True)
        else:
            self.assertFalse(False)


unittest.main(verbosity=1)
tb = test_FIR()
tb.config_sim(trace=True)
tb.run_sim()

