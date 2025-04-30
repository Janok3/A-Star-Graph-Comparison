g++ main.cpp -o astar; if ($?) { .\astar }
The command above is the command that can be used to both compile and run the program.

main.cpp:
In the main funciton:
- The program starts by reading the graphs from the specified folder and checks to make sure the folder is not empty. 
- Then for each graph it runs the the A* algorithm while keeping track of the time. 
- It prints the necessary metrics such as the nodes expanded, average steps, average execution time, minimum execution time, path cost to goal
- Once each of the graphs have been analyzed, the program finishes. 

visualize_graphs.py
- The program stats off by reading the graphs from the specified folder.
- It vusailizes these graphs by using the libraries: matplotlib.pyplot and networkx