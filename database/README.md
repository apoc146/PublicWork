# Databases

<section id="readme-top"></section>

## Description

This repository showcases projects focused on advanced database indexing techniques and optimization methods to enhance database performance and functionality.

## Content Overview

- **GinAndGist**: An exploration into PostgreSQL's Gin indexing, highlighting its effectiveness for composite types and full-text search capabilities.
- **Vectorization**: Demonstrates the utilization of database optimization through vectorization, leveraging modern CPU architectures for enhanced parallel processing and query execution.


## 📊 Slides

### [🔗 GIN and GiST Indexing Techniques Slide Presentation](./src/GinAndGist/GinAndGist.pdf)


### [🔗 Vectorized Database Techniques Slide Presentation](./src/Vectorization/)

<br>
## Detailed Project Insights

### 1. GIN and GiST: Enhancing Database Efficiency

Investigates **Generalized Inverted Index (GIN)** and **Generalized Search Tree (GiST)** indexing strategies in database systems, particularly within PostgreSQL.

#### GIN Indexes
- **Overview:** Introduction to GIN's role in keyword and full-text searches.
- **Architecture:** Details on the structure, including index types and optimization strategies.
- **Optimization:** Discussion of the pending list and its impact on search performance.

#### GiST Indexes
- **Introduction:** Overview of GiST's flexibility for complex data types.
- **Mechanisms:** Insights into insertion algorithms, page splits, and PickSplit method.
- **Applications:** Examples showcasing the optimization of geometric and geospatial data queries.

<br>

### 2. Survey of Vectorized Database Techniques

Presents a thorough survey on SIMD (Single Instruction, Multiple Data) vectorization and its application in database systems.

#### Key Topics and Research Papers

- **Vectorization and SIMD:**
  - Introduction to the concept and its pivotal role in database systems.
  - **Research Paper:** Orestis Polychroniou, Arun Raghavan, and Kenneth A. Ross, 2015, "Rethinking SIMD Vectorization for In-Memory Databases," highlights SIMD's utility in in-memory databases.

- **Benefits of SIMD:**
  - Enhancements in memory usage, cache efficiency, and overall performance.
  - Adoption of SIMD across various ISAs (Instruction Set Architectures).

- **Vectorization Types and Fundamentals:**
  - Distinction between horizontal and vertical vectorization.
  - Fundamental operations that enable efficient database management systems.

- **Vectorized Operators:**
  - Analysis of performance improvements with vectorized selection scans and hashing.
  - **Research Paper:** Harald Lang et al., 2016, "Data Blocks: Hybrid OLTP and OLAP on Compressed Storage using both Vectorization and Compilation," explores datablocks and their significance.

- **Advanced Techniques and System Design:**
  - Adaptive Radix Trees (ART) for optimized indexing and retrieval.
    - **Research Paper:** Leis V., Kemper A., & Neumann T., 2013, "The Adaptive Radix Tree: ARTful Indexing for Main-Memory Databases," discusses ART's benefits.
  - Datablocks for handling hybrid OLTP and OLAP workloads and vectorizing Bloom filter probing.
    - **Research Paper:** Orestis Polychroniou and Kenneth A. Ross, 2014, "Vectorized Bloom filters for advanced SIMD processors," examines Bloom filters' vectorization.

- **Applications in Database Systems:**
  - Case study on the Quickstep database system, emphasizing vectorization for parallelism and efficiency.
    - **Research Paper:** "Quickstep: a data platform based on the scaling-up approach," by Jignesh M. Patel et al., 2018, showcases Quickstep's innovative approach.

#### Conclusion

Concludes with the observation that SIMD vectorization significantly enhances database system performance, supported by research and application examples.

For further information, visit the [course website](https://www.cs.purdue.edu/homes/chunyi/teaching/cs536-sp23/cs536-sp23.html).

## License

Not Distributed

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

Shivam - [bhat41@purdue.edu](mailto:bhat41@purdue.edu)

## Acknowledgments

* Course: CS 54100: Database Systems
