from ipykernel.kernelapp import IPKernelApp
from .kernel import ZshKernel

IPKernelApp.launch_instance(kernel_class = ZshKernel)
