#include <vector>
#include <iostream>
#include <cstdlib>

#include "thinning.h"
#include "h5_io.h"


int main(int argc, char *argv[])
{

	if (argc < 4) {
		std::cout << "arguments: depth directory maxIter p (e.g. 256 oldH5 80 10)" << std::endl;
		return 1;
	}
	unsigned numSlices = std::atoi(argv[1]);
	unsigned width = numSlices, height = numSlices;
	unsigned maxIter = std::atoi(argv[3]);
	unsigned p = std::atoi(argv[4]);

	std::cout << "using dimension:" << std::endl;
	std::cout << "  numSlices:" << numSlices << std::endl;
	std::cout << "      width:" << width << std::endl;
	std::cout << "     height:" << height << std::endl;
	std::cout << "initial data from:" << std::endl;
	std::cout << "   " << argv[2] << std::endl;
	std::cout << "other configuration elements:" << std::endl;
	std::cout << "    maxIter:" << maxIter << std::endl;
	std::cout << "          p:" << p << std::endl;

	thin::IjkType size3D = thin::makeIjk(width, height, numSlices);
	unsigned maxNumVoxelsPerChunk = 100000U;

	h5_io::H5SliceIoManager sliceIoMngr("", argv[2], "newH5", width, height, numSlices, "chunkMap.txt", maxNumVoxelsPerChunk);

	thin::initDevice();
	thin::setNumThreadsPerBlock(196U);

	thin::chunkwiseThinning(sliceIoMngr, size3D, curIter, curDim, p, maxIter);
	thin::shutdownDevice();


	return 0;
}
