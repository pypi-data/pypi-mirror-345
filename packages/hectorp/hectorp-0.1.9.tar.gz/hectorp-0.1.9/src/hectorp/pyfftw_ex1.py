import pyfftw
import multiprocessing
import scipy.signal
import scipy.fft
import numpy
from timeit import Timer

a = pyfftw.empty_aligned((128, 64), dtype='complex128')
b = pyfftw.empty_aligned((128, 64), dtype='complex128')

a[:] = numpy.random.randn(128, 64) + 1j*numpy.random.randn(128, 64)
b[:] = numpy.random.randn(128, 64) + 1j*numpy.random.randn(128, 64)

t = Timer(lambda: scipy.signal.fftconvolve(a, b))

print('Time with scipy.fft default backend: %1.3f seconds' %
      t.timeit(number=100))

# Configure PyFFTW to use all cores (the default is single-threaded)
pyfftw.config.NUM_THREADS = multiprocessing.cpu_count()
print('NUM_THREADS=',pyfftw.config.NUM_THREADS)
pyfftw.config.PLANNER_EFFORT = 'FFTW_MEASURE'

# Use the backend pyfftw.interfaces.scipy_fft
with scipy.fft.set_backend(pyfftw.interfaces.scipy_fft):
     # Turn on the cache for optimum performance
     pyfftw.interfaces.cache.enable()

      # We cheat a bit by doing the planning first
     scipy.signal.fftconvolve(a, b)

     print('Time with pyfftw backend installed: %1.3f seconds' %
            t.timeit(number=100))
