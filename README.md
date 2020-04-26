# ssd-dag

## setup

using conda - preliminary  
- pip install python-pip
- pip install cython

you need a virtual environment (conda on SageMaker, I use virtualenvwrapper on my laptop)

- tensorflow (v 1.14 hardcoded to use CUDA 10.0 object files)  
- opencv-python
- pillow
- (Don't at this time-future, maybe) TensorRT - requies CUDA 10.0 or 10.2 (not 10.1 oddly) and the TF graph must be build w/ 1.14  

There is a requirements.txt file

-- VERIFIED --
### XPS8100  
TF 1.14  CUDA 10.0 - failed  
   AttributeError: 'ParallelInterleaveDataset' object has no attribute '_flat_structure'  
   this is a TF Build issue

### XPS8930
TF 1.14 CUDA 10.0 - failed,    
   trains but errors after creating an index file - TypeError: object of type <class 'numpy.float64'> cannot be safely interpreted as an integer.  


### SageMaker  
TF 1.15  CUDA 10.1 - verified on SageMaker  (20200124)  
  

### Docker - 8930
grilledclub/cuda100-tf114:20200124  
Host CUDA 10.2 - Docker:  TF 1.14  CUDA 10.0 - Verified 




## git clone

### tensorflow/models

you need tensorflow/models.  this is a collection of models and helper functions (supplements tensorflow) 
`git clone https://github.com/tensorflow/models.git`

#### TO USE THIS - you need to add these environment variables:

(they are already in existing scripts)   
`MODEL_RESEARCH="${OBJ_DET_DIR}/../models/research"`
`export PYTHONPATH=$PYTHONPATH:${MODEL_RESEARCH}`
