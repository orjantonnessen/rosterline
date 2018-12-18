# rosterline
Vegard Pedersen and Sander Coates project report. NTNU, December 2018.

File                            Description
===============================================================================================================================================================================
rosterlineMaster.mos            Mosel Xpress RMP. Constraints should be commented out depending on decomposed model configuration. Binary requirement can be enforced. Self-executable files need to be made in Xpress-IVE to run program from columnGeneration.py.
columnGeneration.py             Function for column generation algorithm implementation. Called by decomposed.py.
decomposed.py                   Script to run decomposed model on input instance(s) and save results to file.
functionsCG.py                  Functions used in columnGeneration.py.
classes.py                      Classes used in SPPRC network.
solveSPPRC.py                   Function to solve SPPRC. Called by columnGeneration.py.
functionsSPPRC.py               Functions used in spprc.py.
resourceExtensionFunctions.py   REFs used in functionsSPPRC.py.
mip.py                          Script to run MIP model on input instance(s) and save results to file.
functionsMIP.py                 Functions used by mip.py.
rosterlineMIP.py                Mosel Xpress MIP. Self-executable files need to be made in Xpress-IVE to run program from mip.py.
===============================================================================================================================================================================
