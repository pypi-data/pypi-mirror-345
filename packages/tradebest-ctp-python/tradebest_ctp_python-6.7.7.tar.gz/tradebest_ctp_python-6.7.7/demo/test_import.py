import sys
import os
import ctypes

sys.path.insert(0, '..')

if os.name == 'posix':
    lib_path = os.path.join('..', '6.7.7_20240607', 'linux64')
    abs_lib_path = os.path.abspath(lib_path)
    os.environ['LD_LIBRARY_PATH'] = f"{abs_lib_path}:{os.environ.get('LD_LIBRARY_PATH', '')}"
    
    try:
        md_lib_path = os.path.join(abs_lib_path, 'libthostmduserapi_se.so')
        td_lib_path = os.path.join(abs_lib_path, 'libthosttraderapi_se.so')
        
        if os.path.exists(md_lib_path):
            print(f"Loading MD library from: {md_lib_path}")
            ctypes.CDLL(md_lib_path)
        else:
            print(f"MD library not found at: {md_lib_path}")
            
        if os.path.exists(td_lib_path):
            print(f"Loading TD library from: {td_lib_path}")
            ctypes.CDLL(td_lib_path)
        else:
            print(f"TD library not found at: {td_lib_path}")
    except Exception as e:
        print(f"Error loading libraries: {e}")

try:
    print("Attempting to import tradebest_ctp modules...")
    from tradebest_ctp import mdapi, tdapi
    print("Successfully imported tradebest_ctp modules")
    print(f"Module paths: {mdapi.__file__}, {tdapi.__file__}")
except Exception as e:
    print(f"Error importing modules: {e}")
    print(f"Current sys.path: {sys.path}")
    print(f"Current LD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH', 'Not set')}")
