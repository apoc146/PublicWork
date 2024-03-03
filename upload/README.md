# Robotics

<!-- ![banner]() -->

<!-- ![badge]()
![badge]()
[![license](https://img.shields.io/github/license/:user/:repo.svg)](LICENSE)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/RichardLitt/standard-readme) -->

<!-- This is an example file with maximal choices selected.

This is a long description. -->
## Description
<section id="readme-top"></section>
This directory contains work on network communication, featuring socket programming, HTTP protocols, web server development, routing, network layer simulation, and packet analysis.

## Content

- [Imitation Learning](https://github.com/apoc146/roboticsProject/tree/main) - RRT* guided Imitation Learning for a TurtleBot robot
- [Controller](./controller/) - Classical Control
- [Motion Planning](./motionPlanning/) - Sample-based motion planning
- [Policy Gradient](./policyGradient) -  Policy gradient methods to solve gym environments(<b>CartPole-v1 and 2 Link Arm</b>) with discrete and continuous action spaces
- [mpnet](./mpnet) - Motion Plannig Neural Networks

<details>
<summary><b>1. RRT (Rapidly-exploring Random Tree) in 3D Environment</b><a href="./src/socket/" style="color: #40A2E3; font-weight: bold;"> [code]</a></summary>

- Applied to a 3-DOF UR5 robot arm for collision-free navigation to a target position.
<div align="center">

<img src="img/A1/A1-3d.gif" alt="RRT in 3D Environment" width="350px">
<br>
<em>Figure 1.1: Visualization of RRT in a 3D Environment</em>
</div>

</details>

<details>
<summary><b>2. BiRRT (Bidirectional Rapidly-exploring Random Tree) in 3D Environment</b><a href="./src/socket/" style="color: #40A2E3; font-weight: bold;"> [code]</a></summary>

- Implements BiRRT. Enhances efficiency by initiating search from both the start and goal positions.

</details>

<details>
<summary><b>3. Path Smoothing for BiRRT</b><a href="./src/socket/" style="color: #40A2E3; font-weight: bold;"> [code]</a></summary>

- Refines the path found by BiRRT to minimize the number of nodes and create a more direct route.

</details>

<details>
<summary><b>4. RRT* (Rapidly-exploring Random Trees Star) in 2D Environment</b><a href="./src/socket/" style="color: #40A2E3; font-weight: bold;"> [code]</a></summary>

<p align="center">
  Used for optimizing the path for different robot systems, including 2D point-mass, circular rigid body, and rectangular rigid body.
</p>

<p align="center">
  <img src="img/A1/rrt.png" alt="RRT" width="210px" height="160px"/>
  <img src="img/A1/rrtstarcircle.png" alt="RRT*" width="210px" height="160px"/>
  <img src="img/A1/rrtstarbox.png" alt="RRT*" width="210px" height="160px"/>
</p>

<p align="center">
  <em>Visualization of RRT* algorithms in 2D environment for circular and rectangular rigid bodies</em>
</p>
</details>



<details>
<summary><b>5. PD Controller Trajectory Tracking for 2-DOF Robotic Arm</b><a href="./src/controllers/" style="color: #40A2E3; font-weight: bold;"> [code]</a></summary>

The results of a 2-DOF robotic arm using two different PD control strategies are presented below. The first strategy corrects movement <strong>based on the end-effector's positional error</strong>, while the second strategy adjusts <strong>using joint angle errors computed via Inverse Kinematics (IK)</strong>.



<summary><b>X-Y PD Controller</b><a href="./src/x-y-controller/" style="color: #40A2E3; font-weight: bold;"> [code]</a></summary>
<p align="center">
This controller uses the Jacobian to convert the end-effector's positional error into corrective joint torques. The target trajectory is shown in blue, and the actual ones in red.
</p>

<p align="center">
  <img src="img/A2/armOri.png" alt="Target Trajectory" width="200"/>
  <img src="img/A2/arm2.png" alt="Intermediate Control" width="200"/>
  <img src="img/A2/arm1.png" alt="Best Controlled Path" width="200"/>
  <br>
  <em>Figures 5.1 to 5.3: Trajectory tracking with X-Y PD Controller; Target (blue) and Actual (red)</em>
</p>



<summary><b>IK-Based PD Controller</b><a href="./src/ik-controller/" style="color: #40A2E3; font-weight: bold;"> [code]</a></summary>
<p align="center">
Differing from the X-Y approach, this method uses joint angles derived through IK for error calculation and control.
</p>

<p align="center">
  <img src="img/A2/ik.png" alt="IK Trajectory Result" width="200"/>
  <img src="img/A2/ik_error.png" alt="IK Error Plot" width="200" height="150"/>
  <br>
  <em>Figures 5.4 and 5.5: Trajectory and error plotting with IK-Based PD Controller</em>
</p>

</details>




<details>
<summary><b>6. Autonomous Track Navigation with PID Controllers</b> <a href="./src/adaptive_controller/" style="color: #40A2E3; font-weight: bold;">[code]</a></summary>

Implements a adaptive controller to navigate a race car across varied tracks, optimizing wheel angle and thrust for maximum speed and accuracy, with performance gauged by cumulative rewards.

<p align="center">
  <img src="img/A3/8_pd.gif" alt="Adaptive Controller on FigureEight Track" width="300" height="200"/>
  <img src="img/A3/circle_pd.gif" alt="Adaptive Controller on Circle Track" width="300" height="200"/>
  <img src="img/A3/line_pd.gif" alt="Adaptive Controller on Linear Track" width="300" height="200"/>
</p>
<p align="center">
  <em>PID Controller strategy on FigureEight, Circle, and Linear tracks
</p>

</details>

<details>
<summary><b>7. MPNets - Neural Network based Motion Planning*</b> <a href="./src/mpnet_rrt_star/" style="color: #40A2E3; font-weight: bold;">[code]</a> [<a href="https://arxiv.org/abs/1806.05767" style="color: #40A2E3; font-weight: bold;">paper</a>]</summary>

MPNet implementation for efficient robotics motion planning in 2D/3D, integrating Dropout and Lazy Vertex Contraction for enhanced pathfinding. Combines MPNet's learning efficiency with RRT*'s optimization, showcasing pathfinding improvements in complex environments.

<p align="center">
  <img src="img/A3/mpnet-2d.png" alt="MPNet in 2D" width="200" height="150"/>
  <img src="img/A3/mpnet-3d.png" alt="MPNet in 3D" width="200" height="150"/>
  <img src="img/A3/mpnet-pointcloud.png" alt="MPNet with Point Cloud" width="200" height="150"/>
  <img src="img/A3/mpnet-org.png" alt="MPNet in 3D" width="200" height="150"/>
</p>
<p align="center">
  <em>MPNet applications: 2D environment, 3D environment, and point cloud navigation.</em>
</p>
</details>




<details>
<summary><b>8. Reinforcement Learning with Policy Gradients for CartPole and 2 Link Arm</b></summary>

We implement and compare different policy gradient methods, including:

- **Vanilla Policy Gradient (VPG)**: For the `CartPole-v1` environment, we use the objective function illustrated below. This represents the policy gradient, averaged over n episodes.
  <p align="center">
    <img src="img/A4/v1.png" alt="VPG Equation"/>
  </p>

- **Reward-to-Go Policy Gradient**: This method focuses on the future rewards for each action at time t, suitable for both environments. The equation is as follows:
  <p align="center">
    <img src="img/A4/v2.png" alt="Reward-to-Go Equation"/>
  </p>

- **Baseline-Subtracted Policy Gradient**: Incorporating a baseline b and normalizing rewards by standard deviation σ to reduce variance. The equation is detailed below:
  <p align="center">
    <img src="img/A4/v3.png" alt="Baseline-Subtracted Equation"/>
  </p>

### Results for Each Policy

<p align="center">
  <img src="img/A4/r1.png" alt="Results for VPG" width="200" height="150"/>
  <img src="img/A4/r2.png" alt="Results for Reward-to-Go" width="200" height="150"/>
  <img src="img/A4/r3.png" alt="Results for Baseline-Subtracted" width="200" height="150"/>
</p>
<p align="center">
  <em>Top row: Equations for each policy gradient method. Bottom row: Corresponding results.</em>
</p>

### Simulation Results

<p align="center">
  <img src="img/A4/cartpole.gif" alt="CartPole-v1 Result" width="300" height="200"/>
  <img src="img/A4/arm.gif" alt="2 Link Arm Result" width="300" height="200"/>
</p>
<p align="center">
  <em>The CartPole agent learns to maintain balance (left), while the 2 Link Arm successfully reaches its target positions (right).</em>
</p>

</details>









## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- LICENSE -->
## License
Not Distributed

<!-- Not Distributed under the MIT License. See `LICENSE.txt` for more information. -->

<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- CONTACT -->
## Contact

[Shivam](https://twitter.com/) - bhat41@purdue.edu



<!-- Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name) -->

<!-- <p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
* [Purdue CS593-Robotics](https://qureshiahmed.github.io/sp23.html)

