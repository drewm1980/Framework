from pprint import pprint as p
import h5py
import numpy
import pickle
import sys
import os

# if you need to convert from python3 version of pickle to something
# compatible with python2:
# cd python2 && python3 -c "import pickle;pickle.dump(pickle.load(open('../0.pkl','rb')),open('0.pkl','wb'), protocol=2)"

SHIFT_Z = True # if true cut off empty Z slices and start indexing from z 0

# outputdir=sys.argv[1]
# if not os.path.isdir(outputdir):
#     print("\"%s\" is not directory. first argument must be directory to putput new data and chunkMap.txt"%outputdir)
#     sys.exit(1)
#files=sys.argv[2:]

files=sys.argv[1:]
for f in files:
    if not os.path.exists(f):
        print("\"%s\" does not exist"%f)
        sys.exit(1)


for file in files:
    pkl = pickle.load(open(file,'rb'))
    print(pkl.keys(),dir(pkl))
    #for row in pkl['point_cloud']:
    """
        >>> d['point_cloud']
            array([[-0.01492455,  0.02961376, -0.03069022],
               [-0.01526683,  0.02911375, -0.03032573],
               [-0.01492455,  0.02911375, -0.03069022],
               ...,
               [ 0.00221934, -0.12538657, -0.00293069],
               [ 0.00151258, -0.12538657, -0.00290848],
               [ 0.00185486, -0.12538657, -0.00327297]], dtype=float32)
    """
    voxels = pkl['occupancy_grid']
    # depth used later when computing voxel x,y represenation
    maxdimension = sorted(voxels.shape)[-1]
    width = maxdimension
    height = maxdimension
    depth = maxdimension
    """
    array([[[False, False, False, ..., False, False, False],
        [False, False, False, ..., False, False, False],
        [False, False, False, ..., False, False, False],
        ...,
        [False, False, False, ..., False, False, False],
        [False, False, False, ..., False, False, False],
        [False, False, False, ..., False, False, False]],

       [[False, False, False, ..., False, False, False],
        [False, False, False, ..., False, False, False],
        [False, False, False, ..., False, False, False],
        ...,
        [False, False, False, ..., False, False, False],
        [False, False, False, ..., False, False, False],
        [False, False, False, ..., False, False, False]]], dtype=bool)
        voxels.shape
        (480, 373, 364)
        example: check if x=100,y101,z102 is on: voxel[100][101][102]==True
    """
    data = numpy.argwhere(voxels==True)
    """
    array([[160, 244, 197],
           [161, 244, 196],
           [161, 244, 197],
           ...,
           [470, 181, 180],
           [470, 182, 179],
           [470, 182, 180]])
    data.shape (444521, 3)
    """
    # rotate 90 deg
    #data=numpy.rot90(data) # BUGBUG: this doesnt work how we want
    """
    we assume order of xyz
    so lets sort it by z so we can determine max depth
    """
    # sort by z
    # each data chunk in h5 file should be a z increment
    data = sorted(data, key=lambda v: v[2])

    # Store data in h5 file as z slices
    # so lets iterate starting from smallest z to largest:
    if not os.path.exists(file+'_h5'):
        os.mkdir(file+'_h5')
    with h5py.File(file+'_h5/0.h5','w') as h5:
        minz = data[0][2]
        maxz = data[-1][2]
        for z in range(minz, maxz+1):
            rows = [r for r in data if r[2] == z]
            zdata=[]
            for row in rows:
                x=row[0]
                y=row[1]
                # eg, if zMax = 256, x = 61, y = 190...
                # complex hash = 48701
                #                (190*256)+61
                # to extract values:
                # x = 48701 % 256
                # y = 48701 / 256
                complex = (y*width)+x
                print("z%d:%d is (y%d * width%d) + x%d"%(z,complex,y,width,x))
                zdata.append((complex,1,1))
            # rotate it so colums become rows
            # [(3, 1), (4, 2)] = list(zip(*reversed([[1, 2], [3, 4]])))
            zdata=list(zip(*sorted(zdata)))
            # trying to find a solution to the error
            #zdata=list(reversed(zdata))
            if SHIFT_Z:
                z = z - minz
            h5.create_dataset(str(z),data=zdata, dtype='i')
        with open(file+'_h5/chunkMap.txt', 'w') as f:
            print("BUGBUG: not sure why but the max z but things broke if we did not reduce by 1 the maxz in chunkMap.txt")
            if SHIFT_Z:
                f.write("%d %d\n"%(0,maxz-minz-1))
            else:
                f.write("%d %d\n"%(minz,maxz-1))



    # data = [[[]]]
    #
    # for x in voxels
    #     data = numpy.empty(dtype=numpy.uint32)
