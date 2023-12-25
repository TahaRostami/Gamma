
QDomPrjCppHelperParallel.cpp and QDomPrjCppHelperSeq.cpp are written to be executed on Linux.

In the case of resource limitation, QDomPrjCppHelperSeq.cpp can be used to execute one trail at a time while QDomPrjCppHelperParallel.cpp can be used if multiple cores are available.

QDomPrjCppHelperParallel is a ready to use code, and only customizating configuration is required. However, for QDomPrjCppHelperSeq.cpp, fill_configurations function should be defined.

TODO: for the purpose of analyzing and visualizing the outputs produced by this search a seperate piece of code is needed.