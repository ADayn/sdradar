import SoapySDR as sp
import numpy as np
import time

C = 299792458
d_range = 60
min_rf = 100000

def radar_range(gain, cross_section, freq):
    g = 10**(gain/10.0)
    d = 10**(d_range/10.0)
    tmp = d*g**2*C**2*cross_section
    tmp /= freq**2 * (4*np.pi)**3
    return tmp**.25

def get_sweep_rate(delay, deg_safety):
    return min_rf*deg_safety*1.0/delay

def gen_chirp(count, sweep_rate):
    t = np.linspace(0,(count-1),count)
    return np.sin(2*np.pi*sweep_rate/4*t**2)

def gen_pulse(sample_rate):
    n = 100000
    a = np.zeros(n)
    l = .1
    a[:int(l*n)] = 1
    a[-int(l*n):] = 1
    pulse = np.fft.ifft(a)
    return pulse

def main():
    sample_rate = 50e6
    center_freq = 2.41e9
    rrange = radar_range(10,2,center_freq)
    sample_round_trip = 2*rrange*sample_rate*1./C
    sample_delay = np.ceil(sample_round_trip)
    sweep_rate = get_sweep_rate(sample_delay,2)
    length = int(np.round(sample_rate/sweep_rate))

    ##signal
    #pulse = gen_chirp(length, sweep_rate/sample_rate)
    pulse = gen_pulse(sample_rate)

    packet = pulse.astype(np.complex64)
    
    ##SDR
    sdr = sp.Device(dict(driver='bladerf'))
    ##LIME has more than 1 channel
    sdr.setSampleRate(1,0,sample_rate)
    sdr.setFrequency(1,0,center_freq)

    tx = sdr.setupStream(sp.SOAPY_SDR_TX, "CF32", [0])

    sdr.activateStream(tx)

    while True:
        words = raw_input("hit enter to send")
        if words == 'q':
            break
        txTime0 = sdr.getHardwareTime() + long(.1e9)
        txflags = sp.SOAPY_SDR_HAS_TIME|sp.SOAPY_SDR_END_BURST
        print txflags
        st = sdr.writeStream(tx, [packet], len(pulse), txflags, txTime0)

        print st.flags, " is flags"
    
    
    sdr.deactivateStream(tx)
    sdr.closeStream(tx)

    
if __name__ == '__main__':
    main()
    
