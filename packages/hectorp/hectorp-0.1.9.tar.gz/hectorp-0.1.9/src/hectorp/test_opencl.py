
import numpy
from pyfft.cuda import Plan
import pycuda.autoinit
import pycuda.gpuarray as gpuarray

# w,h,k are the array dimensions in a power of 2
# im1, im2 are the input 3d arrays of dtype complex64

w = h = k = 512
im1 = numpy.random.rand(w,h,k).astype(numpy.complex64)
im2 = numpy.random.rand(w,h,k).astype(numpy.complex64)

plan = Plan((w,h,k), normalize=True)

# forward transform on device
im1_gpu = gpuarray.to_gpu(im1)
plan.execute(im1_gpu)
im1_ft = im1_gpu.get()
del im1_gpu

im2_gpu = gpuarray.to_gpu(im2)
plan.execute(im2_gpu)
im2_ft = im2_gpu.get()
del im2_gpu

# do multiplication on host - can be done on device.
conv = im1_ft * im2_ft

#inverse transform on device
conv_gpu = gpuarray.to_gpu(conv)
del conv
plan.execute(conv_gpu, inverse=True)
corr_gpu = conv_gpu.get()

# Reference calculation on CPU:
im1_ft = numpy.fft.fftn(im1)
im2_ft = numpy.fft.fftn(im2)
conv = im1_ft * im2_ft
del im1
del im2
del im1_ft
del im2_ft
corr_cpu = numpy.fft.ifftn(conv)

print numpy.linalg.norm(corr_cpu - corr_gpu) / numpy.linalg.norm(corr_gpu)
