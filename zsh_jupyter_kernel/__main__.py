from ipykernel.kernelapp import launch_new_instance

from .kernel import ZshKernel

launch_new_instance(kernel_class = ZshKernel)
