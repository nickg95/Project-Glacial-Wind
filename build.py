#!/usr/bin/env python3


import os
import shutil
import os.path
import subprocess
import sys
import shutil
import platform
import glob

def error(msg):
    print(msg)
    input("Press 'enter' to continue...")
    sys.exit(1)
    
if os.getcwd().find(" ") != -1:
    error("Please run the build from a path that does not have spaces")

PLATFORM = platform.system().lower()

SDL_HOME=os.path.join( os.getcwd(),"SDL2-2.0.3" )
SDL_INC=os.path.join(SDL_HOME,"include")

JDK_HOME=None
if PLATFORM == "windows":
    for folder,dirs,files in os.walk(r"c:\program files\java"):
        if JDK_HOME:
            break
        for d in reversed(sorted(dirs)):
            javac_ = os.path.join(folder,d,"bin","javac.exe")
            if os.path.exists(javac_):
                JDK_HOME = os.path.join(folder,d)
                javac_ = os.path.join(JDK_HOME,"bin","javac.exe")
                break
else:
    JDK_HOME="/usr/lib/jvm/java/"
    javac_ = "javac"

     
if not JDK_HOME:
    error("You don't seem to have the Java Development Kit installed")
       
       


def javac(fname):
    cmd =  [
        javac_,
        "-classpath",sys.path[0],
        fname
    ]
    print(cmd)
    subprocess.check_call(cmd)
    
    
 #run command (cl.exe or link.exe) in an msvc subshell.
def vscommand(commands1,bits):
    assert PLATFORM == "windows"
    
    assert type(commands1) == list
    
    print(commands1)
    
    vcbatchfile = None
    
    for P in [
        r"c:\program files (x86)\Microsoft Visual Studio 12.0\VC\vcvarsall.bat",
        r"c:\program files (x86)\Microsoft Visual Studio 14.0\VC\vcvarsall.bat"
        ]:
        if os.path.exists(P):
            vcbatchfile = P
            break
            
    if vcbatchfile == None:
        error("You do not appear to have Visual Studio installed.")
        
    if bits == 64:
        vcbatcharg = "x86_amd64"
    elif bits == 32:
        vcbatcharg = "x86"
    else:
        assert 0
        
    
    commands = []
    commands.append('"'+vcbatchfile+'"'+" "+vcbatcharg)
    for c in commands1:
        commands.append(c)
        commands.append("if ERRORLEVEL 1 exit")
    commands.append("echo ...SUCCESS...")
    commands.append("exit")
    
    commands = "\n".join(commands)
    commands = commands.encode()
    
    p = subprocess.Popen(
            args=["cmd.exe"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
    outs,errs = p.communicate( commands )
    if outs:
        outs=outs.decode()
    else:
        outs=""
        
    if errs:
        errs = errs.decode()
    else:
        errs=""
    
    #print(outs)
    
    if outs.find("...SUCCESS...") != -1:
        return 
    else:
        error("Problem:"+outs+"\n"+errs)

    
    
def compilelibrary(files_to_compile, output_dir, output_library_stem, additional_libs, bits):
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if platform.system().lower() == "windows":
        if bits == 64:
            linkarch="x64"
        elif bits == 32:
            linkarch="x86"
        else:
            assert 0
        
        cmdlist=[]
        
        for fn in files_to_compile:
            print("Compiling",fn,"as",bits,"bits")
            tmp = [
                "cl.exe",
                
                #compile options
                    "/c",       #only compile, don't link
                    "/GS-",     #no security checks
                    "/W3",      #warning level 3
                    "/Zc:wchar_t",
                    #"/Zc:forScope", #C++ for-loop scope
                    "/Gm-",     #disable minimal rebuild
                    "/O2",      #optimization level
                    "/fp:precise",  #precise floating point
    
                    #include dirs
                    '/I"'+JDK_HOME+'\\include"',
                    '/I"'+JDK_HOME+'\\include\\win32"',
                    '/I'+SDL_INC,
                    
                    #defines
                    "/D","WIN32",
                    #"/D","_DEBUG",
                    "/D","_WINDOWS",
                    "/D","_USRDLL",
                    "/D","JGL_EXPORTS",
                    "/D","_WINDLL",
                    "/D","_UNICODE",
                    "/D","UNICODE",
                    
                    "/errorReport:none",    #what to do on internal compiler errors
                    "/WX-",         #warnings are not errors
                    "/Gd",          #cdecl convention
                    "/MD",          #multithreaded runtime DLL
                    "/EHsc",        #no structured exception handling; C code does not throw
                    "/nologo",
                    '/Fo'+output_dir+"\\"+fn+".obj",             #x64\\Debug\\"',            #object files
                    #'/Fd"vc120.pdb"',               #pdb file
                    #'/Fa'+fn+".aobj",    #"x64\\Debug\\"',            #assembly files
                    #'/Fp"x64\\Debug\\JGL.pch"',      #precompiled headers
                    fn
            ]
            cmdlist.append(" ".join(tmp))
         
        print("Linking")
        
        if bits == 32:
            sdldir = os.path.join(SDL_HOME,"VisualC","SDL","Win32","Release")
        else:
            sdldir = os.path.join(SDL_HOME,"VisualC","SDL","x64","Release")
            
        tmp = [    
                    "link.exe",
                    "/OUT:"+output_dir+"\\"+output_library_stem+".dll",
                    #"/MANIFEST",        #generate a manifest
                    "/NXCOMPAT",
                    #"/PDB:foo.pdb",
                    "/DYNAMICBASE",
                    #"/IMPLIB:"+dllname+".lib",
                    #"/DEBUG",
                    "/DLL",
                    "/MACHINE:"+linkarch,
                    "/INCREMENTAL:NO",
                    #"/PGD:..."
                    "/SUBSYSTEM:WINDOWS",
                    "/ERRORREPORT:none",
                    "/NOLOGO",
                    "/TLBID:1",
                    '/LIBPATH:"'+sdldir+'"'
        ]
        
        tmp += [
            "kernel32.lib","user32.lib","gdi32.lib",
            "winspool.lib","comdlg32.lib","advapi32.lib","shell32.lib",
            "ole32.lib","oleaut32.lib","uuid.lib","odbc32.lib",
            "odbccp32.lib"
        ]
        
        tmp += [q for q in additional_libs]
        
        tmp += [ os.path.join(output_dir+"\\"+q+".obj") for q in files_to_compile]
        cmdlist.append(" ".join(tmp))
        
        vscommand( cmdlist,bits)
 
    else:
        for fn in files_to_compile:
            subprocess.check_call(["gcc","-fPIC","-I"+SDL_HOME+"/include","-I/usr/lib/jvm/java/include","-I/usr/lib/jvm/java/include/linux",
                "-O2","-g","-Wall","-c",fn,"-o",os.path.join(output_dir,fn+".o")])
        
        tmp = ["gcc","-L"+SDL_HOME+"/build/.libs","-fPIC","-shared","-o",os.path.join(output_dir,output_library_stem+".so")]
        tmp += [os.path.join(output_dir,fn+".o") for fn in files_to_compile]
        for x in additional_libs:
            tmp.append("-l"+x)
            
        subprocess.check_call(tmp)
        
        

    
#build SDL
def buildsdl():
    if platform.system().lower() == "windows":
        try:
            os.unlink(os.path.join("SDL2-2.0.3","include","SDL_config.h"))
        except:
            pass
        shutil.copyfile(os.path.join("SDL2-2.0.3","include","SDL_config_windows.h"),
                os.path.join("SDL2-2.0.3","include","SDL_config.h"))
        if not os.path.exists(os.path.join(SDL_HOME,"VisualC","SDL","x64","Release","SDL2.dll")):
            print("Building SDL x64")
            vscommand([r"msbuild /target:SDL2 SDL2-2.0.3\VisualC\SDL_VS2013.sln /p:Configuration=Release;Platform=x64"],64)
        if not os.path.exists(os.path.join(SDL_HOME,"VisualC","SDL","Win32","Release","SDL2.dll")):
            print("Building SDL Win32")
            vscommand([r"msbuild /target:SDL2 SDL2-2.0.3\VisualC\SDL_VS2013.sln /p:Configuration=Release;Platform=Win32"],32)
    else:
        os.chdir(SDL_HOME)
        subprocess.check_call(["./configure"])
        subprocess.check_call(["make"])
        os.chdir("..")

 
#build jgl 
sys.path.append(os.path.join(os.getcwd(),"JGL"))
import parsegl
def buildgl(): 
    os.chdir("JGL")
    parsegl.quiet=True
    print("Generating GL files")
    parsegl.main()
    print("Compiling JGL.java")
    javac("JGL.java")
    os.chdir("..")
    print("Generating JGL.h")
    subprocess.check_call([os.path.join(JDK_HOME,"bin","javah"),"-d","JGL","JGL.JGL"])
    os.chdir("JGL")
    print("Compiling JGL library")
    
    inputs=["JGL.c"]
    
    if PLATFORM == "windows":
        addllibs = ["opengl32.lib"]
        inputs+=["dllmain.c"]
    else:
        addllibs = ["GL"]
        
    
    for bits in [32,64]:
        compilelibrary(inputs,PLATFORM+str(bits),"JGL",addllibs,bits)
    
    os.chdir("..")

sys.path.append(os.path.join(os.getcwd(),"JSDL"))
import parsesdl
def buildjsdl():
    os.chdir("JSDL")
    parsesdl.quiet=True
    print("Generating SDL files")
    parsesdl.main()
    print("Compiling JSDL.java")
    javac("JSDL.java")
    os.chdir("..")
    print("Generating JSDL.h")
    subprocess.check_call([os.path.join(JDK_HOME,"bin","javah"),"-d","JSDL","JSDL.JSDL"])
    os.chdir("JSDL")
    print("Compiling JSDL library")
    
    inputs=["JSDL.c"]
         
    if PLATFORM == "windows":
        addllibs = ["sdl2.lib"]
        inputs+=["dllmain.c"]
    else:
        addllibs = ["SDL2"]
 
 
    for bits in [32,64]:
        compilelibrary( inputs, PLATFORM+str(bits),"JSDL",addllibs,bits)
    
    os.chdir("..")

def buildjglsdlutils():
    os.chdir("JGLSDLUtils")
    javac("JGLSDLUtils.java")
    os.chdir("..")


def createjar():
    print("Creating jar file...")
    
    jarfile = os.path.join(os.getcwd(),"JGLSDL.jar")
    jar=os.path.join(JDK_HOME,"bin","jar")

    try: os.unlink(jarfile)
    except: pass

    tmp=[
        jar,
        "-cf",
        jarfile,
        "SDL2-2.0.3/COPYING.txt"
    ]
    
    for q in [
       "JGL/*.class",
        "JGL/*.txt",
        "JGL/*.java",
        #"JGL/*.h",
        "JGL/*.c",
        "JSDL/*.class",
        "JSDL/*.txt",
        "JSDL/*.java",
        #"JSDL/*.h",
        "JSDL/*.c",
        "JGLSDLUtils/*.class",
        "JGLSDLUtils/*.java",
    ]:
        tmp += glob.glob(q)
     
    subprocess.check_call( tmp )

    for bits in [32,64]:
        p = os.path.join("libs",PLATFORM+str(bits))
        if not os.path.exists(p):
            os.makedirs(p)
    
    if PLATFORM == "windows":
        suf=".dll"
    else:
        suf=".so"
        
    for ll in ["JGL","JSDL"]:
        for b in [32,64]:
            shutil.copyfile( os.path.join(ll,PLATFORM+str(b),ll+suf), os.path.join("libs",PLATFORM+str(b),ll+suf))


    if PLATFORM == "windows":
        shutil.copyfile(os.path.join(SDL_HOME,"VisualC","SDL","x64","Release","SDL2.dll"),os.path.join("libs",PLATFORM+"64","SDL2.dll"))
        shutil.copyfile(os.path.join(SDL_HOME,"VisualC","SDL","Win32","Release","SDL2.dll"),os.path.join("libs",PLATFORM+"32","SDL2.dll"))
    else:
        #FIXME: both architectures?
        shutil.copyfile(os.path.join(SDL_HOME,"build",".libs","libSDL2.so"), os.path.join("libs",PLATFORM+"32","SDL2.so") )
        shutil.copyfile(os.path.join(SDL_HOME,"build",".libs","libSDL2.so"), os.path.join("libs",PLATFORM+"64","SDL2.so") )
        
    subprocess.check_call([jar,"-uf",jarfile,"libs"])

todo=[]
if len(sys.argv) == 1:
    todo.append("jglsdlutils")
    todo.append("jgl")
    todo.append("sdl")
    todo.append("jsdl")
    todo.append("jar")
else:
    todo = sys.argv[1:]
    
if "jglsdlutils" in todo:
    buildjglsdlutils()
if "jgl" in todo:
    buildgl()
if "sdl" in todo:
    buildsdl()
if "jsdl" in todo:
    buildjsdl()
if "jar" in todo:
    createjar()
