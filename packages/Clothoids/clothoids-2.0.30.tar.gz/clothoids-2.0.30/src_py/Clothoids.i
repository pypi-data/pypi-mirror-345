%module Clothoids

%include "std_vector.i"
%template() std::vector<double>;

%include "std_array.i"
%template() std::array<double, 4>;
%template() std::array<double, 5>;
%template() std::array<double, 6>;

%include "std_pair.i"
%template() std::pair<double, double>;
%template() std::pair<std::vector<double>, std::vector<double>>;

%{
#include "clothoids_interface.hh"
%}

%include "GenericContainer.i"

%include "clothoids_interface.hh"
