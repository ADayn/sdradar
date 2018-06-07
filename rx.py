import utils as u
import SoapySDR as sp
import zmq
import numpy as np
import time

def config_radio(sample_rate, center_frequency):
	sdr = sp.Device({
		'driver': 'bladerf',
		'serial': u.BLADE_2
	})
	print(sample_rate)
	print(center_frequency)
	sdr.setSampleRate(sp.SOAPY_SDR_RX, 0, sample_rate)
	sdr.setFrequency(sp.SOAPY_SDR_RX, 0, center_frequency)
	return sdr

def main():
	# parameters
	port = 7269
	sample_rate = u.mhz(2)
	center_frequency = u.ghz(2.41)

	# file setup
	tx_file_name = raw_input("TX file name: ")
	shape = raw_input("Shape: ")
	frequency = raw_input("Frequency: ")
	resolution = raw_input("Resolution: ")
	file_name = "_".join(["rx", tx_file_name, shape, frequency + "mhz", resolution]) + ".bin"
	file = open(file_name, "wb")

	# SDR setup
	sdr = config_radio(sample_rate, center_frequency)
	rx_stream = sdr.setupStream(sp.SOAPY_SDR_RX, sp.SOAPY_SDR_CF32, [0])
	#print("MTU: ", sdr.get_stream_MTU(rx_stream))
	rx_time_0 = sdr.getHardwareTime() + long(.1e9)
	rx_flags = sp.SOAPY_SDR_END_BURST
	sdr.activateStream(rx_stream, rx_flags, rx_time_0)

	# ZMQ setup
	context = zmq.Context()
	socket = context.socket(zmq.PUB)
	socket.bind("tcp://*:%s" %str(port))

	# Loop
	print("start")
	cnt = 0
	while(True):
		rx_buffer = np.array([0]*1024, np.complex64)
		sr = sdr.readStream(rx_stream, [rx_buffer], len(rx_buffer), timeoutUs=long(5e5))
		print
		print
		print
		print("----", cnt)
		print
		print("ret: ", sr.ret)
		print("flags: ", sr.flags)
		print("timeNs: ", sr.timeNs)
		print("type: ", type(rx_buffer[0]))
		print("data: ", rx_buffer[0],  " ... ", rx_buffer[-1])
		#for point in rx_buffer:
			#print point
			#socket.send(float(point))
		#time.sleep(1)
		#np.savetxt(file_name, rx_buffer.view(complex))
		#socket.send(rx_buffer)
		cnt += 1
		rx_buffer.tofile(file)

	# Cleanup
	file.close()
	sdr.deactivateStream(rx_stream)
	sdr.closeStream(rx_stream)

if __name__ == '__main__':
	main()
