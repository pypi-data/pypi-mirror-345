<!-- SPDX-FileCopyrightText: 2025 Ali Onsi -->
<!-- SPDX-License-Identifier: GPL-3.0-or-later -->

## Evaluating N-Dimensional Integration with Monte Carlo Methods
### Mathematical Basis
Another problem which can be solved using Monte Carlo's method is numerical integration. From the definition of the average of a function we have:

$$\langle f(x) \rangle = \frac{1}{b-a} \int_a^b f(x) dx$$

which can be rearranged as:

$$\int_a^b f(x) dx = (b-a) \langle f(x) \rangle$$

From this, we can conclude that with a large number of random points, we can approximate the value of the integral. If we have a function $f(x)$ and want to evaluate the integral from $a$ to $b$, we:

- Generate a large number of random points in the interval $[a,b]$ 
- Calculate the average value of $f(x)$ at these random points
- = Multiply this average by the length of the interval $(b-a)$

### Extension to Higher Dimensions 

This concept extends to 2D, 3D, and higher dimensional integrals:

For a 2D integral:

$$\langle f(x,y) \rangle = \frac{1}{b_x-a_x} , \frac{1}{b_y-a_y} , \int_{a_y}^{b_y} \int_{a_x}^{b_x} f(x,y) , dx , dy$$

Rearranged as:

$$\int_{a_y}^{b_y} \int_{a_x}^{b_x} f(x,y) , dx , dy = (b_x-a_x)(b_y-a_y) \langle f(x,y) \rangle$$

For a 3D integral:

$$\int_{a_z}^{b_z} \int_{a_y}^{b_y} \int_{a_x}^{b_x} f(x,y,z) , dx , dy , dz = (b_x-a_x)(b_y-a_y)(b_z-a_z) \langle f(x,y,z) \rangle$$

A general pattern emerges for $N$-dimensional integrals:

$$\int_{a_N}^{b_N} \cdots \int_{a_2}^{b_2} \int_{a_1}^{b_1} f(x_1, x_2, \ldots, x_N) , dx_1 , dx_2 , \ldots , dx_N = \left[\prod_{i=1}^N (b_i-a_i) \right] \cdot \langle f(x_1,x_2, \ldots, x_N) \rangle$$

What's impressive is that the difficulty of integrating a higher-order integral doesn't increase significantly with Monte Carlo methods, making it suitable for complex integrals.

## License
This project is licensed under the **GNU GPLv3**.  
- **You must**:  
  - Disclose source code for derivative works.  
  - License derivatives under GPL-3.0.  
- **Commercial use**: Allowed, but derivatives must remain open-source.  