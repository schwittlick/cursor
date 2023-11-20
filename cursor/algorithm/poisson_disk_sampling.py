import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

"""
Implementation of the fast Poisson Disk Sampling algorithm of 
Bridson (2007) adapted to support spatially varying sampling radii. 

Adrian Bittner, 2021
Published under MIT license. 
"""


def getGridCoordinates(coords):
    return np.floor(coords).astype('int')


def poissonDiskSampling(radius, k=30, radiusType='default'):
    """
    Implementation of the Poisson Disk Sampling algorithm.

    :param radius: 2d array specifying the minimum sampling radius for each spatial position in the sampling box. The
                   size of the sampling box is given by the size of the radius array.
    :param k: Number of iterations to find a new particle in an annulus between radius r and 2r from a sample particle.
    :param radiusType: Method to determine the distance to newly spawned particles. 'default' follows the algorithm of
                       Bridson (2007) and generates particles uniformly in the annulus between radius r and 2r.
                       'normDist' instead creates new particles at distances drawn from a normal distribution centered
                       around 1.5r with a dispersion of 0.2r.
    :return: nParticle: Number of particles in the sampling.
             particleCoordinates: 2d array containing the coordinates of the created particles.
    """
    # Set-up background grid
    gridHeight, gridWidth = radius.shape
    grid = np.zeros((gridHeight, gridWidth))

    # Pick initial (active) point
    coords = (np.random.random() * gridHeight, np.random.random() * gridWidth)
    idx = getGridCoordinates(coords)
    nParticle = 1
    grid[idx[0], idx[1]] = nParticle

    # Initialise active queue
    queue = [coords]  # Appending to list is much quicker than to numpy array, if you do it very often
    particleCoordinates = [coords]  # List containing the exact positions of the final particles

    # Continue iteration while there is still points in active list
    while queue:

        # Pick random element in active queue
        idx = np.random.randint(len(queue))
        activeCoords = queue[idx]
        activeGridCoords = getGridCoordinates(activeCoords)

        success = False
        for _ in range(k):

            if radiusType == 'default':
                # Pick radius for new sample particle ranging between 1 and 2 times the local radius
                newRadius = radius[activeGridCoords[1], activeGridCoords[0]] * (np.random.random() + 1)
            elif radiusType == 'normDist':
                # Pick radius for new sample particle from a normal distribution around 1.5 times the local radius
                newRadius = radius[activeGridCoords[1], activeGridCoords[0]] * np.random.normal(1.5, 0.2)

            # Pick the angle to the sample particle and determine its coordinates
            angle = 2 * np.pi * np.random.random()
            newCoords = np.zeros(2)
            newCoords[0] = activeCoords[0] + newRadius * np.sin(angle)
            newCoords[1] = activeCoords[1] + newRadius * np.cos(angle)

            # Prevent that the new particle is outside of the grid
            if not (0 <= newCoords[1] <= gridWidth and 0 <= newCoords[0] <= gridHeight):
                continue

            # Check that particle is not too close to other particle
            newGridCoords = getGridCoordinates((newCoords[1], newCoords[0]))

            radiusThere = np.ceil(radius[newGridCoords[1], newGridCoords[0]])
            gridRangeX = (np.max([newGridCoords[0] - radiusThere, 0]).astype('int'),
                          np.min([newGridCoords[0] + radiusThere + 1, gridWidth]).astype('int'))
            gridRangeY = (np.max([newGridCoords[1] - radiusThere, 0]).astype('int'),
                          np.min([newGridCoords[1] + radiusThere + 1, gridHeight]).astype('int'))

            searchGrid = grid[slice(gridRangeY[0], gridRangeY[1]), slice(gridRangeX[0], gridRangeX[1])]
            conflicts = np.where(searchGrid > 0)

            if len(conflicts[0]) == 0 and len(conflicts[1]) == 0:
                # No conflicts detected. Create a new particle at this position!
                queue.append(newCoords)
                particleCoordinates.append(newCoords)
                nParticle += 1
                grid[newGridCoords[1], newGridCoords[0]] = nParticle
                success = True

            else:
                # There is a conflict. Do NOT create a new particle at this position!
                continue

        if success == False:
            # No new particle could be associated to the currently active particle.
            # Remove current particle from the active queue!
            del queue[idx]

    return (nParticle, np.array(particleCoordinates))


def uniformDensity(shape, d=3):
    """ Create a radius array with uniform density """
    rad = np.zeros(shape) + d
    return rad


def sphericalDensity(shape):
    """ Create a radius array with the density radially increasing towards the centre """
    rad = np.zeros(shape)
    for x in range(shape[1]):
        for y in range(shape[0]):
            rad[y, x] = np.sqrt((x - shape[0] / 2) ** 2 + (y - shape[1] / 2) ** 2)

    # Prettier scaling
    rad = np.sqrt(2 * rad)

    # Add some noise
    rand = np.random.normal(1, 0.1, shape[0] * shape[1]).reshape(shape)
    rad = rad * rand / 3

    # Limit the maximum density
    idx = np.where(rad < 3)
    rad[idx] = 3

    return rad


def quartersOfConstantDensity(shape):
    """ Create a radius array consisting of four quarters with different densities """
    rad = np.zeros(shape)

    halfY = int(shape[0] / 2)
    halfX = int(shape[1] / 2)

    rad[0:halfY, 0:halfX] = 2
    rad[0:halfY, halfX:] = 4
    rad[halfY:, 0:halfX] = 6
    rad[halfY:, halfX:] = 8

    # Add some noise
    rand = np.random.normal(1, 0.1, shape[0] * shape[1]).reshape(shape)
    rad = rad * rand

    return rad


def chessDensity(shape):
    """ Create a radius array resembling a chessboard pattern """
    rad = np.zeros(shape)
    for i in range(5):
        for o in range(5):
            if (o + i * 5) % 2 == 0:
                rad[60 * i:60 * (i + 1), 60 * o:60 * (o + 1)] = 3
            else:
                rad[60 * i:60 * (i + 1), 60 * o:60 * (o + 1)] = 5

    # Add some noise
    rand = np.random.normal(1, 0.1, shape[0] * shape[1]).reshape(shape)
    rad = rad * rand

    return rad


def plotSampling(particleCoordinates, rad, name="uniformDensity5000"):
    """ Plot the density map and resulting Poisson Disk Sampling. """
    fig, (ax1, ax2) = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(50, 25))
    ax1.set_title("Density Field")
    ax1.imshow(rad, cmap='RdBu', interpolation='none')
    ax2.set_title("Poisson Disk Sampling")
    ax2.scatter(particleCoordinates[:, 0], particleCoordinates[:, 1], marker='.', s=4, c='k')

    ax1.xaxis.set_major_locator(MultipleLocator(50))
    ax1.yaxis.set_major_locator(MultipleLocator(50))
    ax1.xaxis.set_minor_locator(MultipleLocator(25))
    ax1.yaxis.set_minor_locator(MultipleLocator(25))
    ax1.tick_params(direction="in", which='both', bottom=True, top=True, left=True, right=True)
    ax2.tick_params(direction="in", which='both', bottom=True, top=True, left=True, right=True)
    # ax1.set_xlim([0, 1090])
    # ax1.set_ylim([0, 1090])

    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    plt.savefig(f"{name}.png")


if __name__ == "__main__":
    """
    This file presents various examples on the usage of this software package and the generated Poisson Disk Samplings. 
    """

    # Create the Radius Array
    rad = uniformDensity((300, 300))  # Uniform sampling radius throughout the field
    # rad = sphericalDensity((5000, 5000))  # Radially decreasing sampling radius
    # rad = quartersOfConstantDensity((300,300)) # Four quarters with different densities (run with k=100)
    # rad = chessDensity((300,300))              # A chessboard pattern of different densities (run with k=100)

    # Run the Poisson Disk Sampling
    nParticle, particleCoordinates = poissonDiskSampling(rad, k=30, radiusType='default')
    # Visualise the resulting sampling
    plotSampling(particleCoordinates, rad)
