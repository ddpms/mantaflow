#
# Simple example scene (hello world)
# Simulation of a buoyant smoke density plume

from manta import *
import os, shutil, math, sys

# solver params
res = 44
# gs = vec3(res,1.5*res,res)
gs = vec3(res,res,res)

sm = Solver(name='main', gridSize = gs)


# sm.timestep = 1.0
sm.timestep = 2.0

velInflow = vec3(1, 0, 0)
#velInflow = vec3(1, 1, 1)

# prepare grids
flags = sm.create(FlagGrid)
vel = sm.create(MACGrid)
density = sm.create(RealGrid)
pressure = sm.create(RealGrid)

# noise field
noise = sm.create(NoiseField, fixedSeed=765)
noise.posScale = vec3(20)
noise.clamp = True
noise.clampNeg = 0
noise.clampPos = 2
noise.valScale = 1
noise.valOffset = 0.075
# solid:
# noise.valOffset = 990.75
noise.timeAnim = 0.2

flags.initDomain()
flags.fillGrid()

source = sm.create(Cylinder, center=gs*vec3(0.2,0.2,0.5), radius=res*0.1, z=gs*vec3(0.1, 0, 0))

# larger solver
# recompute sizes...

upres = 2
xl_res = upres*res
xl_gs = vec3(xl_res,xl_res,xl_res)
xl = Solver(name='larger', gridSize = xl_gs)
xl.timestep = upres*sm.timestep

xl_flags   = xl.create(FlagGrid)
xl_vel     = xl.create(MACGrid)
xl_density = xl.create(RealGrid)

xl_flags.initDomain()
xl_flags.fillGrid()

xl_source = xl.create(Cylinder, center=xl_gs*vec3(0.2,0.2,0.5), radius=xl_res*0.1, z=xl_gs*vec3(0.1, 0, 0))

xl_noise = xl.create(NoiseField, fixedSeed=765)
xl_noise.posScale = vec3(20)
xl_noise.clamp = noise.clamp
xl_noise.clampNeg = noise.clampNeg
xl_noise.clampPos = noise.clampPos
xl_noise.valScale = noise.valScale
xl_noise.valOffset = noise.valOffset
xl_noise.timeAnim  = noise.timeAnim



if (GUI):
    gui = Gui()
    gui.show()

#main loop
for t in range(200):
    
    curt = t * sm.timestep
    #sys.stdout.write( "Curr t " + str(curt) +" \n" )
        
    #source.applyToGrid(grid=vel, value=velInflow)
    advectSemiLagrange(flags=flags, vel=vel, grid=density, order=2)    
    advectSemiLagrange(flags=flags, vel=vel, grid=vel, order=2)
    
    if (curt>=0 and curt<30) or (curt>60 and curt<90):
        densityInflow( flags=flags, density=density, noise=noise, shape=source, scale=1, sigma=0.5 )
        source.applyToGrid( grid=vel , value=velInflow )
    
    setWallBcs(flags=flags, vel=vel)    
    addBuoyancy(density=density, vel=vel, gravity=vec3(0,-1e-3,0), flags=flags)
    
    solvePressure(flags=flags, vel=vel, pressure=pressure)
    setWallBcs(flags=flags, vel=vel)

#    density.save('densitySm_%04d.vol' % t)
    
    sm.step()
    
     # xl ...
	 # same inflow
    
#    interpolateGrid(density,xl_density)
    interpolateMACGrid(vel,xl_vel)
    
    advectSemiLagrange(flags=xl_flags, vel=xl_vel, grid=xl_density, order=2)    
#    advectSemiLagrange(flags=xl_flags, vel=xl_vel, grid=xl_vel, order=2)
    
    if (curt>=0 and curt<30) or (curt>60 and curt<90):
         densityInflow( flags=xl_flags, density=xl_density, noise=xl_noise, shape=xl_source, scale=1, sigma=0.5 )
 #       source.applyToGrid( grid=xl_vel , value=velInflow )
    
#    xl_density.save('densityXl_%04d.vol' % t)
	
    xl.step()

