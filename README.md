 ## GreenPickUp-MTP

Green parcel delivery is a python project aiming at optimizing the placement of pick-up stations and minimizing the routes in between their positions. 

<img src="https://gitlab.com/jzenkner/greenpickup-mtp/-/raw/Wiki/readMepcitureofpositions.png" alt="Image of recommended pick-up stations by the algorithm" width="400">

_Example of pick-up station placement recommendations by the reinforcement learning model._
 

## Installation
There are two options to use the green parcel delivery project. It can be used out of the box with the given executable or by loading and using the given python library. The requirements and installation possibilities are presented below 

# Using the executable
Using the executable is the easier way to use the project and requires no programming knowledge. It guides the user through text prompts and allows for setting up a reinforcement learning project from providing the data over setting the given feature weights up until receiving the results.
**Requirements**
-Having python 3.915 or higher installed on your device.
-Ensure that the requirements presented requirements.txt file are fulfilled. 
**Installation**
Download the executable.exe file from the top directory to your device and run it. You will find further instructions in the executable.

# Using the library
Using the library allows for full customization of the given python library. This allows the user to modify the full project to their own requirements.
**Requirements**
-Having python 3.915 or higher installed on your device
-Suitable development tools for python, javascript, jss and html libraries
-Ensure that the requirements presented requirements.txt file are fulfilled. 
**Installation**
Load in the relevant libraries into the development surroundings. E.g. for frontend development the frontend data or for reinforcement development the reinforcement data.
Make sure that the required libraries are successfully installed.
Modify the project to your liking and then run it by using the MainPPO.py file. 


<img src="https://gitlab.com/jzenkner/greenpickup-mtp/-/raw/Wiki/readMefeatureexample.png" alt="Image of considered features by the algorithm." width="400">

_Example of features considered by the reinforcement learning model._


## Usage
- Data generation: The project allows for the generation of static and dynamic synthetic data for the city of Stuttgart, Germany. 
- Reinforcement Learning: This data can then be used to generate a reinforcement learning algorithm that determines the optimal placement of pick-up stations.
- Routeplanning: Once the placement stations of the pick-up stations has been calculated shortest routes between them can be calculated.
- These routes can then be presented in the accompanying customer and deliverer frontends of the project. 

### Frontend Setup
The frontend was developed using the VSCode editor. To run the flask application and initialise the database, follow these steps:

1. Install SQLite extension in VSCode.
2. Create a venv.
3. Install all the modules listed in the requirements.txt.
4. Initialise the database by running the sql query in the initialise_database.sql file using the flaskr.sqlite instance.
5. The database can be opened and explored by using the secondary click, which opens another dropdown button at the bottom of the explorer.
6. Run the __init__.py file.
7. Finally run the command: flask --app flaskr run in the terminal

## Support
In case you require assistance with the software please feel free to contact the authors of the project under our email adresses:
Alicia Böhret - 
Daniel Hostadt - 
Janis Zenkner - 
Michael Klassen - 
Rares Rahaian - 
David Svistea - 
Thomas Frey - thfrey@uni-mannheim.de 
In case you find bugs or problems with the software we would be very thankful if you opened an issue for them in this GitLab project.

## Roadmap 
Potential further ideas for this project: 
- Generalizability to different cities
- Visualization and explanation of the reinforcement learning results  
- Usage with the empirical dataset

## Wiki
Please consider the Wiki to find explanatory information on how all software artefacts work and how to use them yourself.

## Contributing
Contributing merge requests are welcome for this project. Please feel free to contact us for potential contributions and merge requests.

## Authors and acknowledgment
Our team worked on the project in the following areas:
- Alicia Böhret - Frontend, Synthetic Data generation and Routeplanning
- Daniel Hostadt - Synthetic Data Generation and Route planning
- Janis Zenkner - Teamlead
- Michael Klassen - Reinforcement Learning Algorithm and Deployment
- Rares Rahaian - Reinforcement Learning Algorithm
- David Svistea - Frontend
- Thomas Frey - Reinforcement Learning Algorithm and Frontend


## License
MIT License

Copyright (c) 2023

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Project status
The Project has been completed as of the 13.08.2023 for our team.

