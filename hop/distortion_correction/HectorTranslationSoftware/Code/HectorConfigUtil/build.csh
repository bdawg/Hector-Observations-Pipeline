cc -c -O gen_qfmed.c
c++ -c -O TcsUtil.cpp
c++ -o HectorConfigUtil -DM_I86 -std=c++11 -Wall -pedantic -I ../../configure/2dFutil/ -I ../../configure/include/ -I ../../configure/sds -I ../../configure/sds/Standalone/ -I ../../SAMI/sami/ -I ../../SAMI/coneOfDarkness/ -I ../../SAMI/aatTelMdl/ -I ../../SAMI/cpp_util/ -I ../../configure/aaoConfigure/drama_src   HectorConfigUtil.cpp HectorRaDecXY.cpp gen_qfmed.o TcsUtil.o ../../SAMI/aatTelMdl/libaattelmdl.a ../../configure/2dFutil/tdffpilfull.o ../../configure/2dFutil/tdfxy.o ../../configure/2dFutil/tdffpilmin.o ../../configure/2dFutil/tdFcollision.o ../../configure/fpil/fpil.o ../../libraries/libsds.a ../../libraries/libers.a ../../libraries/libsla.a