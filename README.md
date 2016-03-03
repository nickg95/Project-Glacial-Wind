# Project-Glacial-Wind
A 3D vehicular combat game I'm working on and my project for my sophomore level Graphics 2 class.

To run on Windows or Linux: 

Running it currently takes a bit of work since it's a work in progress -- I'll look into ways to make it more portable, but for now follow these steps if you want to run it:

Download everything and put it together in one folder/directory, then open up the python script called build.py. You will need to have Python, JDK(Java) and Visual Studio(with Visual C) installed. Once those are all installed, run the build.py script and it should generate a JAR called JGLSDL. This is a binding for Java OpenGL, which is what the game uses. Once you have that, download and install Netbeans if you don't already have it (easiest way to run it since it has so many dependencies) and open up the Graphics2Project Netbeans project. Right-slick the project under the project tab and click 'properties', then click the 'libraries' tab and click 'add JAR/Folder' and select the JGLSDL JAR file you built. After that, just open up the main.java source code file and run it and it should work.
