# Project-Glacial-Wind
A demo of a 3D graphics engine I built using OpenGL for my sophomore-level Graphics 2 class. 

To run on Windows or Linux: 

Download everything (all the .zips and files above) and extract them to/put them all in one folder/directory, then open up the python script called build.py. You will need to have Python, JDK(Java) and Visual Studio(with Visual C) installed. Once those are all installed, run the build.py script and it should generate a JAR called JGLSDL. This is a binding for Java OpenGL, which is what the game uses. Once you have that, open up your preferred IDE and open the Graphics2Project project. You will need to add the JAR binding as a dependency (In Netbeans: right-slick the project under the project tab and click 'properties', then click the 'libraries' tab and click 'add JAR/Folder' and select the JGLSDL JAR file you built.) After that, just open up the main.java source code file and run it and it should work.
