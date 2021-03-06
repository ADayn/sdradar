from array import array
import numpy as np
import matplotlib.pyplot as plt


## example write complex buffer to file
buff = np.array([0]*1024, np.complex64)
for i in range(1024):
    if i == 1020:
        buff[i] = 20+3j
out_file = open("test.data", 'wb')
buff.tofile(out_file)
out_file.close()

## example read complex from file
buff2 = np.fromfile("test.data", np.complex64)




## break out real and imaginary parts
real2 = np.array([0]*1024, np.float32)
imag2 = np.array([0]*1024, np.float32)
for i in range(1024):
     real2[i] = buff2[i].real
     imag2[i] = buff2[i].imag

t = np.linspace(0,1023,1024)

#plt.plot(t,np.abs(real2), t, np.abs(imag2))
plt.plot(t,np.abs(real2))
plt.show()
