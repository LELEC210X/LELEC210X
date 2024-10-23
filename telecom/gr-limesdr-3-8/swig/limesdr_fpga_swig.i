/* -*- c++ -*- */

#define LIMESDR_FPGA_API

%include "gnuradio.i"           // the common stuff

//load generated python docstrings
%include "limesdr_fpga_swig_doc.i"

%{
#include "limesdr_fpga/sink.h"
#include "limesdr_fpga/source.h"
%}

%include "limesdr_fpga/sink.h"
GR_SWIG_BLOCK_MAGIC2(limesdr_fpga, sink);
%include "limesdr_fpga/source.h"
GR_SWIG_BLOCK_MAGIC2(limesdr_fpga, source);
