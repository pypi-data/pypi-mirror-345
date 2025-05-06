#include <stdio.h>

//definitions to set up dual-use headers for CPU compilation only:
#define __h__
#define __d__

#include "NumCuda.h"
#include "Annealables.h" 

//these need to be included, as this file functions as the compiler entry point for them
#include "TspAnnealable.h"
#include "IsingAnnealable.h"
#include "IsingPrecomputeAnnealable.h"
#include "PottsJitAnnealable.h"
#include "PottsPrecomputeAnnealable.h"

#include "Cores.h"
bool GetGpuAvailability(){
	printf("This copy of PottsPlayground is not compiled with GPU support.\n");
    return false;
}

//because NumCuda is compiled here only, the usual import_array is ineffectual for code inside NumCuda.
//Therefore we force it to execute once in this context too. See:
//https://stackoverflow.com/questions/47026900/pyarray-check-gives-segmentation-fault-with-cython-c
int init_numpy(){
     import_array(); // PyError if not successful
     return 0;
}
const static int numpy_initialized =  init_numpy();

template class NumCuda<int>;
template class NumCuda<float>;

DispatchFunc* GpuTspDispatch = NULL;
DispatchFunc* GpuIsingDispatch = NULL;
DispatchFunc* GpuIsingPrecomputeDispatch = NULL;
DispatchFunc* GpuPottsJitDispatch = NULL;
DispatchFunc* GpuPottsPrecomputeDispatch = NULL;
DispatchFunc* GpuPottsPrecomputePEDispatch = NULL;
