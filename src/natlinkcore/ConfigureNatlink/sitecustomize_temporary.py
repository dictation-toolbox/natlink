'''add the directory where natlinkmain is located to sys.path.
'''
# QH, 14/7/2021
import sys
import os

natlinkcoreDir = os.path.normpath(os.path.join(sys.prefix, 'Lib', 'site-packages', 'natlinkcore'))
if os.path.isdir(natlinkcoreDir):
    if natlinkcoreDir not in sys.path:
        print(f'add to sys.path: {natlinkcoreDir}')
        sys.path.append(natlinkcoreDir)
        
if __name__ == '__main__':
    from pprint import pprint
    print('sys.path:')
    pprint(sys.path)
    