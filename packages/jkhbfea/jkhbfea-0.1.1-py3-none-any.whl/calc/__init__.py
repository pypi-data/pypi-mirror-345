from .operations import addition, soustraction, multiplication, division, idk, HelloWorld

__all__ = ["addition", "soustraction", "multiplication", "division", "idk", "HelloWorld"]

# Attache les fonctions et la classe directement au nom du module
import sys
this_module = sys.modules[__name__]
this_module.addition = addition
this_module.soustraction = soustraction
this_module.multiplication = multiplication
this_module.division = division
this_module.idk = idk
this_module.HelloWorld = HelloWorld
