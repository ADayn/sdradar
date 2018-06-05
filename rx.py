import utils as u
import SoapySDR as sp
import zmq
import numpy as np
import time

def config_radio(sample_rate, center_frequency):
	sdr = sp.Device({
		'driver': 'bladerf'
	})
	print(sample_rate)
	print(center_frequency)
	sdr.setSampleRate(sp.SOAPY_SDR_RX, 0, sample_rate)
	sdr.setFrequency(sp.SOAPY_SDR_RX, 0, center_frequency)
	return sdr

def main():
	port = 7269
	sample_rate = u.mhz(40)
	center_frequency = u.ghz(2.41)
	sdr = config_radio(sample_rate, center_frequency)
	rx_stream = sdr.setupStream(sp.SOAPY_SDR_RX, sp.SOAPY_SDR_CF32, [0])
	rx_time_0 = sdr.getHardwareTime() + long(.1e9)
	rx_flags = sp.SOAPY_SDR_END_BURST
	sdr.activateStream(rx_stream, rx_flags, rx_time_0)
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:%s" %str(port))
	print("start")
	while(True):
		rx_buffer = np.array([0]*20000, np.complex64)
		sr = sdr.readStream(rx_stream, [rx_buffer], len(rx_buffer), timeoutUs=long(5e5))
		print("ret: ", sr.ret)
		print("flags: ", sr.flags)
		print("timeNs: ", sr.timeNs)
		#for point in rx_buffer:
		#	print type(point), float(point)
			#socket.send(float(point))
		#time.sleep(1)
		socket.send(rx_buffer)
	sdr.deactivateStream(rx_stream)
	sdr.closeStream(rx_stream)

if __name__ == '__main__':
	main()
