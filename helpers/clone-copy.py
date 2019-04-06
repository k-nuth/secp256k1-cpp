import os
import os.path
from shutil import copyfile


PATH = '/Users/fernando/dev/bitprim/bitprim-consensus/src/clone-abc/'
SOURCE_PATH = '/Users/fernando/dev/bitcoin-abc/src/'

# result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames if os.path.splitext(f)[1] == '.txt']
# result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames]
result = [(dp, f) for dp, dn, filenames in os.walk(PATH) for f in filenames]

for dp, f in result:
    x = os.path.join(dp, f)

    # print(dp)
    # print(x)
    # print(x[len(PATH):])

    source_file = os.path.join(SOURCE_PATH, x[len(PATH):])   
    print(source_file)
    # print(os.path.isfile(source_file))

    # print(x)



    copyfile(source_file, x)
