# ssd-dag

## setup

you need a virtual environment (conda on SageMaker, I use virtualenvwrapper on my laptop)

- tensorflow
- opencv-python
- pillow

There is a requirements.txt file

TF 1.14  CUDA 10.0  
TF 1.15  CUDA 10.1 - verified on SageMaker  (20200124)  
TF 1.14  CUDA 10.2 - won't work!   TF 1.14 specifically looks for libcuda*10.0* object files  

Docker



## git clone

### tensorflow/models

you need tensorflow/models.  this is a collection of models and helper functions (supplements tensorflow) 
`git clone https://github.com/tensorflow/models.git`

#### TO USE THIS - you need to add these environment variables:

(they are already in existing scripts)   
`MODEL_RESEARCH="${OBJ_DET_DIR}/../models/research"`
`export PYTHONPATH=$PYTHONPATH:${MODEL_RESEARCH}`
