# Search in 2D and 3d Space - RRT, BiRRT, RRTStar

This Implements Various Robotics Search Algorithms
- RRT
- BiRRT and Smoothing
- RRT Star
- For Point, Circular and Rigid Square Body

Results with their performance metrics have been compiled in the [report](Report.pdf)

## Description

In [rrt_birrt](/rrt_birrt) we implement Rapidly-exploring Random Tree(RRT) and Bidirectional Rapidly-exploring Random Tree(BiRRT) in 3D environments. The algorithms will be applied on a simplified 3-DOF UR5 robot arm to let it reach the target position.

In [rrtStar](/rrtStar) We implement Rapidly-exploring Random Trees star (RRT*) method for three different robot systems, i.e., 2D point-mass, circular rigid body, and a rectangular rigid-body in a 2D environment.This part uses some of the course provided scaffolding code for collision checks. The Algorithms have been implemented from scratch follwoing the below pseudo code

## Getting Started

### Dependencies

* Pybullet

### Installing

* How/where to download your program

### Executing program

* Run the *.py files
```
code blocks for commands
```

<!-- ## Help

Any advise for common problems or issues.
```
command to run if program contains helper info
``` -->

<!-- ## Authors

Contributors names and contact info
* Purdue CS 593  -->


<!-- ## Version History

* 0.2
    * Various bug fixes and optimizations
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release -->

<!-- ## License

This project is licensed under the [NAME HERE] License - see the LICENSE.md file for details -->

## Acknowledgments and Credits
Contributors names and contact info
* Purdue CS 593 

<!-- Inspiration, code snippets, etc.
* [awesome-readme](https://github.com/matiassingers/awesome-readme)
* [PurpleBooth](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
* [dbader](https://github.com/dbader/readme-template)
* [zenorocha](https://gist.github.com/zenorocha/4526327)
* [fvcproductions](https://gist.github.com/fvcproductions/1bfc2d4aecb01a834b46) -->