from simtk.openmm import app
import simtk.openmm as mm
from simtk import unit as u

#padding = 1.0 * u.nanometers  # For initial crystal structure
padding = 0.9045 * u.nanometers
cutoff = 0.95 * u.nanometers

ff = app.ForceField('amber99sbnmr.xml', 'tip3p-fb.xml')

temperature = 293. 
pressure = 1.0 * u.atmospheres

#pdb = app.PDBFile("./1am7_fixed.pdb")
#pdb = app.PDBFile("./1am7_final.pdb")

#modeller = app.Modeller(pdb.topology, pdb.positions)
#modeller.addSolvent(ff, padding=padding)

pdb = app.PDBFile("./out.pdb")

#topology = modeller.topology
#positions = modeller.positions
topology = pdb.topology
positions = pdb.positions


system = ff.createSystem(topology, nonbondedMethod=app.PME, nonbondedCutoff=cutoff, constraints=app.HBonds)

integrator = mm.LangevinIntegrator(temperature, 1.0 / u.picoseconds, 1.0 * u.femtoseconds)
system.addForce(mm.MonteCarloBarostat(pressure, temperature, 25))
simulation = app.Simulation(topology, system, integrator)
simulation.context.setPositions(positions)
print('Minimizing...')
simulation.minimizeEnergy()

simulation.context.setVelocitiesToTemperature(temperature)
print('Equilibrating...')
simulation.step(45000)
state = simulation.context.getState(getPositions=True, getParameters=True)

positions = state.getPositions()
vectors = state.getPeriodicBoxVectors()
vectors = tuple([v[i] / u.nanometers for (i,v) in enumerate(vectors)])
vectors = u.Quantity(vectors, u.nanometer)
topology.setUnitCellDimensions(vectors)
app.PDBFile.writeFile(topology, positions, open("./1am7_equil2.pdb", 'w'))
