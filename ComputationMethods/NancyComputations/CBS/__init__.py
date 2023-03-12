from ComputationMethods.NancyComputations.load_dll import load_dll
# interface description
from .CsharpInterface import Rational, BigInteger, Curve, AvbClass, NancyCBS, Link, Flow, Plot

dll_dir = "ComputationMethods/NancyComputations/DLLs/CBS/"
dll_name = "CBS"
load_dll(dll_dir, dll_name)

# replace interface description with actual C# implementation
from CBS import CreditBasedShaper as NancyCBS, Link, Flow, AvbClass, Plot  # C# syntax: from NAMESPACE import CLASS
from Unipi.Nancy.Numerics import Rational
from System.Numerics import BigInteger

# avoid unused import warning
_ = NancyCBS, Rational, BigInteger, Link, Flow, AvbClass, Plot
