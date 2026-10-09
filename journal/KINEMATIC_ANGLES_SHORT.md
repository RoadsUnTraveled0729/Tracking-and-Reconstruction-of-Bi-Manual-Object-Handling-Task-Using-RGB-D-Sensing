# Joint angles from eight body landmarks in two frame conventions: summary

Lanqing Luo, 8 October 2026.

## 1. Data

The skeleton uses eight MediaPipe Pose landmarks: L11 and L12 the left and right shoulder, L13 and L14 the elbows, L15 and L16 the wrists, L23 and L24 the hips, left and right being the subject's own. Figure 1 places them on an ideal T-pose with the torso frame of each convention.

![Figure 1](figures/fig1_tpose_frames.png)

Figure 1. The torso frame of each convention on an ideal T-pose at the eight landmarks, seen in the image plane with page right as camera $+x$ and page down as camera $+y$. Panel (a) is the left-handed convention with the torso $x$ axis from L23 to L24, panel (b) the right-handed convention with the torso $x$ axis from L24 to L23. Axis colours are $x$ red, $y$ green and $z$ blue, a circled dot is an axis pointing out of the page toward the viewer and a circled cross an axis pointing into the page.

A depth camera measures them in its sensor frame {Camera}, $x$ to the right of the image, $y$ down, $z$ forward, in metres. Frames and rotations are written in Craig notation: ${}^{A}_{B}R$ is the rotation whose columns are the axes of frame $B$ expressed in frame $A$, ${}^{A}P_{k}$ is the position of landmark $k$ in frame $A$, and a hat marks a unit vector. The pipeline emits thirteen angles: the torso pitch $\theta_x$, yaw $\theta_y$ and roll $\theta_z$, then for each arm the shoulder azimuth $t_y$, elevation $t_z$ and twist $t_t$ and the elbow flexion $e_y$ and out-of-plane angle $e_z$. Figure 2 and Table 1 are the input, one frame of a person facing the camera, with values rounded to three decimals and angles in degrees.

![Figure 2](figures/perfect_frame_overlay.png)

Figure 2. The colour image of the worked-example frame with the eight landmarks and the segments between them. The subject faces the camera, so the subject's right side is on the image left.

| Axis | L11 | L12 | L13 | L14 | L15 | L16 | L23 | L24 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| $x$ (m) | 0.241 | -0.089 | 0.318 | -0.204 | 0.275 | -0.147 | 0.155 | -0.044 |
| $y$ (m) | -0.364 | -0.362 | -0.156 | -0.173 | 0.028 | -0.013 | 0.139 | 0.135 |
| $z$ (m) | 1.309 | 1.322 | 1.198 | 1.253 | 1.062 | 1.133 | 1.238 | 1.219 |

Table 1. The eight landmark positions ${}^{\mathrm{Camera}}P_{k}$ of the worked-example frame.

## 2. The left-handed convention, as implemented

The pipeline, as implemented in the thesis [1], reads every position in the frame {Camera'}, the sensor frame with $y$ reversed so that $y$ points up, which has the handedness of the Unity engine it drives:

$$
{}^{\mathrm{Camera}'}P_{k} = F\,{}^{\mathrm{Camera}}P_{k}, \qquad F = \mathrm{diag}(1,-1,1).
\tag{2.1}
$$

The torso frame {L24} has its origin at the right hip, its $x$ axis is the hip line from the left hip to the right hip, the subject's right, its $z$ axis is the normal of the plane through the hip line and the right shoulder, and its $y$ axis completes the triad, which for the worked-example frame gives:

$$
{}^{\mathrm{Camera}'}\hat{X}_{\mathrm{L24}} = \frac{{}^{\mathrm{Camera}'}P_{24} - {}^{\mathrm{Camera}'}P_{23}}{\lVert {}^{\mathrm{Camera}'}P_{24} - {}^{\mathrm{Camera}'}P_{23} \rVert}, \qquad
{}^{\mathrm{Camera}'}s = {}^{\mathrm{Camera}'}P_{12} - {}^{\mathrm{Camera}'}P_{24},
\tag{2.2}
$$

$$
{}^{\mathrm{Camera}'}\hat{Z}_{\mathrm{L24}} = \frac{{}^{\mathrm{Camera}'}\hat{X}_{\mathrm{L24}} \times {}^{\mathrm{Camera}'}s}{\lVert {}^{\mathrm{Camera}'}\hat{X}_{\mathrm{L24}} \times {}^{\mathrm{Camera}'}s \rVert}, \qquad
{}^{\mathrm{Camera}'}\hat{Y}_{\mathrm{L24}} = {}^{\mathrm{Camera}'}\hat{Z}_{\mathrm{L24}} \times {}^{\mathrm{Camera}'}\hat{X}_{\mathrm{L24}}, \qquad
{}^{\mathrm{Camera}'}_{\mathrm{L24}}R = \begin{pmatrix} {}^{\mathrm{Camera}'}\hat{X}_{\mathrm{L24}} & {}^{\mathrm{Camera}'}\hat{Y}_{\mathrm{L24}} & {}^{\mathrm{Camera}'}\hat{Z}_{\mathrm{L24}} \end{pmatrix}.
\tag{2.3}
$$

$$
{}^{\mathrm{Camera}'}_{\mathrm{L24}}R =
\begin{pmatrix} -0.995 & 0.000 & 0.097 \\ 0.021 & 0.977 & 0.211 \\ -0.095 & 0.212 & -0.973 \end{pmatrix}.
\tag{2.4}
$$

The torso angles are read from the entries $m_{ij}$ of this matrix as the decomposition $R = R_y(\theta_y)\,R_x(\theta_x)\,R_z(\theta_z)$ about the parent axes, in the order $z$, $x$, $y$, where $R_x$, $R_y$ and $R_z$ are the right-handed elementary rotations about the coordinate axes, $m_{ij}$ is the entry in row $i$ and column $j$, and $c$ and $s$ with a subscript are the cosine and sine of $t_y$ or $t_z$:

$$
\theta_x = \mathrm{asin}(-m_{23}) = -12.169^\circ, \qquad
\theta_y = \mathrm{atan2}(m_{13},\, m_{33}) = 174.291^\circ, \qquad
\theta_z = \mathrm{atan2}(m_{21},\, m_{22}) = 1.212^\circ.
\tag{2.5}
$$

The right shoulder frame {L12} has the orientation of the torso frame, and the right arm at rest lies along its $+x$ axis. The upper-arm and forearm vectors in that frame are the {Camera'} differences carried into the torso basis:

$$
{}^{\mathrm{L12}}v = {}^{\mathrm{Camera}'}_{\mathrm{L24}}R^{T}\,({}^{\mathrm{Camera}'}P_{14} - {}^{\mathrm{Camera}'}P_{12}), \qquad
{}^{\mathrm{L12}}f = {}^{\mathrm{Camera}'}_{\mathrm{L24}}R^{T}\,({}^{\mathrm{Camera}'}P_{16} - {}^{\mathrm{Camera}'}P_{14}).
\tag{2.6}
$$

The shoulder rotation is a swing followed by a twist about the arm axis $+x$, $R_{sh} = R_y(t_y)\,R_z(t_z)\,R_x(t_t)$, and the swing takes the rest direction to the unit upper-arm direction $\hat{a} = v / \lVert v \rVert = (c_y c_z,\ s_z,\ -s_y c_z)^T$, so that, with the forearm un-swung by $f' = R_z(-t_z)\,R_y(-t_y)\,f$,

$$
t_z = \mathrm{asin}(a_y) = -59.224^\circ, \qquad t_y = \mathrm{atan2}(-a_z,\ a_x) = -7.915^\circ, \qquad t_t = \mathrm{atan2}(-f'_y,\ f'_z) = 52.746^\circ.
\tag{2.7}
$$

The elbow frame {L14} carries the shoulder rotation, ${}^{\mathrm{Camera}'}_{\mathrm{L14}}R = {}^{\mathrm{Camera}'}_{\mathrm{L24}}R\,R_{sh}$, and the unit forearm direction in it, $\hat{g} = (0.663, 0, 0.748)^T$, is read like the upper arm at the shoulder, the out-of-plane angle being zero by construction since the twist put the forearm in the $x$-$z$ plane of the elbow frame:

$$
e_z = \mathrm{asin}(g_y) = 0, \qquad e_y = \mathrm{atan2}(-g_z,\ g_x) = -48.434^\circ.
\tag{2.8}
$$

The left arm rests along $-x$ and is solved as the mirror image of a right arm, (2.7) and (2.8) being applied to its torso-basis vectors ${}^{\mathrm{L11}}v$ and ${}^{\mathrm{L11}}f$ reflected by $M = \mathrm{diag}(-1,1,1)$, which gives $t_z = -66.319^\circ$, $t_y = -45.758^\circ$, $t_t = 30.377^\circ$, $e_y = -29.721^\circ$ and $e_z = 0$.

| Angle | Torso | Right shoulder | Right elbow | Left shoulder | Left elbow |
| --- | --- | --- | --- | --- | --- |
| first | $\theta_x = -12.169$ | $t_y = -7.915$ | $e_y = -48.434$ | $t_y = -45.758$ | $e_y = -29.721$ |
| second | $\theta_y = 174.291$ | $t_z = -59.224$ | $e_z = 0$ | $t_z = -66.319$ | $e_z = 0$ |
| third | $\theta_z = 1.212$ | $t_t = 52.746$ | | $t_t = 30.377$ | |

Table 2. The thirteen angles in the left-handed convention, in degrees.

## 3. The right-handed convention

This convention works in the sensor frame {Camera} itself, and a star marks its frames. The torso frame {L24*} has its origin at the right hip, its $x$ axis along the hip line from the right hip to the left hip, the subject's left, as a right-handed triad with up and forward as its second and third axes requires, and the same forward and up construction, which for the worked-example frame gives:

$$
{}^{\mathrm{Camera}}\hat{X}_{\mathrm{L24*}} = \frac{{}^{\mathrm{Camera}}P_{23} - {}^{\mathrm{Camera}}P_{24}}{\lVert {}^{\mathrm{Camera}}P_{23} - {}^{\mathrm{Camera}}P_{24} \rVert}, \qquad
{}^{\mathrm{Camera}}s = {}^{\mathrm{Camera}}P_{12} - {}^{\mathrm{Camera}}P_{24},
\tag{3.1}
$$

$$
{}^{\mathrm{Camera}}\hat{Z}_{\mathrm{L24*}} = \frac{{}^{\mathrm{Camera}}\hat{X}_{\mathrm{L24*}} \times {}^{\mathrm{Camera}}s}{\lVert {}^{\mathrm{Camera}}\hat{X}_{\mathrm{L24*}} \times {}^{\mathrm{Camera}}s \rVert}, \qquad
{}^{\mathrm{Camera}}\hat{Y}_{\mathrm{L24*}} = {}^{\mathrm{Camera}}\hat{Z}_{\mathrm{L24*}} \times {}^{\mathrm{Camera}}\hat{X}_{\mathrm{L24*}}, \qquad
{}^{\mathrm{Camera}}_{\mathrm{L24*}}R = \begin{pmatrix} {}^{\mathrm{Camera}}\hat{X}_{\mathrm{L24*}} & {}^{\mathrm{Camera}}\hat{Y}_{\mathrm{L24*}} & {}^{\mathrm{Camera}}\hat{Z}_{\mathrm{L24*}} \end{pmatrix}.
\tag{3.2}
$$

$$
{}^{\mathrm{Camera}}_{\mathrm{L24*}}R =
\begin{pmatrix} 0.995 & 0.000 & 0.097 \\ 0.021 & -0.977 & -0.211 \\ 0.095 & 0.212 & -0.973 \end{pmatrix}.
\tag{3.3}
$$

The torso angles follow from the same decomposition $R = R_y(\theta_y)\,R_x(\theta_x)\,R_z(\theta_z)$:

$$
\theta_x = \mathrm{asin}(-m_{23}) = 12.169^\circ, \qquad
\theta_y = \mathrm{atan2}(m_{13},\, m_{33}) = 174.291^\circ, \qquad
\theta_z = \mathrm{atan2}(m_{21},\, m_{22}) = 178.788^\circ.
\tag{3.4}
$$

The right shoulder frame {L12*} has the orientation of the torso frame, and the right arm at rest lies along its $-x$ axis. The upper-arm and forearm vectors in that frame are:

$$
{}^{\mathrm{L12*}}v = {}^{\mathrm{Camera}}_{\mathrm{L24*}}R^{T}\,({}^{\mathrm{Camera}}P_{14} - {}^{\mathrm{Camera}}P_{12}), \qquad
{}^{\mathrm{L12*}}f = {}^{\mathrm{Camera}}_{\mathrm{L24*}}R^{T}\,({}^{\mathrm{Camera}}P_{16} - {}^{\mathrm{Camera}}P_{14}).
\tag{3.5}
$$

The shoulder rotation is a swing followed by a twist about the arm axis $-x$, which is a rotation by $-t_t$ about $+x$, $R_{sh} = R_y(t_y)\,R_z(t_z)\,R_x(-t_t)$, and the swing takes the rest direction $(-1,0,0)^T$ to $\hat{a} = (-c_y c_z,\ -s_z,\ s_y c_z)^T$, so that, with $f' = R_z(-t_z)\,R_y(-t_y)\,f$,

$$
t_z = -\mathrm{asin}(a_y) = 59.224^\circ, \qquad t_y = \mathrm{atan2}(a_z,\ -a_x) = 7.915^\circ, \qquad t_t = \mathrm{atan2}(f'_y,\ f'_z) = -52.746^\circ.
\tag{3.6}
$$

The elbow frame {L14*} carries the shoulder rotation, ${}^{\mathrm{Camera}}_{\mathrm{L14*}}R = {}^{\mathrm{Camera}}_{\mathrm{L24*}}R\,R_{sh}$, and the unit forearm direction in it, $\hat{g} = (-0.663, 0, 0.748)^T$, is read with the same $-x$ rest direction:

$$
e_z = -\mathrm{asin}(g_y) = 0, \qquad e_y = \mathrm{atan2}(g_z,\ -g_x) = 48.434^\circ.
\tag{3.7}
$$

The left arm rests along $+x$ and uses the $+x$ forms $t_z = \mathrm{asin}(a_y)$, $t_y = \mathrm{atan2}(-a_z, a_x)$, $t_t = \mathrm{atan2}(-f'_y, f'_z)$, $e_z = \mathrm{asin}(g_y)$ and $e_y = \mathrm{atan2}(-g_z, g_x)$, which give $t_z = -66.319^\circ$, $t_y = -45.758^\circ$, $t_t = 30.377^\circ$, $e_y = -29.721^\circ$ and $e_z = 0$.

| Angle | Torso | Right shoulder | Right elbow | Left shoulder | Left elbow |
| --- | --- | --- | --- | --- | --- |
| first | $\theta_x = 12.169$ | $t_y = 7.915$ | $e_y = 48.434$ | $t_y = -45.758$ | $e_y = -29.721$ |
| second | $\theta_y = 174.291$ | $t_z = 59.224$ | $e_z = 0$ | $t_z = -66.319$ | $e_z = 0$ |
| third | $\theta_z = 178.788$ | $t_t = -52.746$ | | $t_t = 30.377$ | |

Table 3. The thirteen angles in the right-handed convention, in degrees.

## 4. Results

| Angle | Symbol | Left-handed (deg) | Right-handed (deg) |
| --- | --- | --- | --- |
| torso pitch | $\theta_x$ | -12.169 | 12.169 |
| torso yaw | $\theta_y$ | 174.291 | 174.291 |
| torso roll | $\theta_z$ | 1.212 | 178.788 |
| right shoulder azimuth | $t_y$ | -7.915 | 7.915 |
| right shoulder elevation | $t_z$ | -59.224 | 59.224 |
| right shoulder twist | $t_t$ | 52.746 | -52.746 |
| right elbow flexion | $e_y$ | -48.434 | 48.434 |
| right elbow out-of-plane | $e_z$ | 0 | 0 |
| left shoulder azimuth | $t_y$ | -45.758 | -45.758 |
| left shoulder elevation | $t_z$ | -66.319 | -66.319 |
| left shoulder twist | $t_t$ | 30.377 | 30.377 |
| left elbow flexion | $e_y$ | -29.721 | -29.721 |
| left elbow out-of-plane | $e_z$ | 0 | 0 |

Table 4. The thirteen joint angles in the two conventions, in the pipeline's output order.

![Figure 3](figures/fk_reconstruction.png)

Figure 3. Forward kinematics from the joint angles. Panel (a) shows the measured landmarks of Table 1 on the colour image, panel (b) the skeleton rebuilt from the left-handed angles, dashed, over the measured one, panel (c) the skeleton rebuilt from the right-handed angles over the measured one, and panel (d) the three as stick figures in {Camera}. They coincide in every panel.

Each set of angles, with the torso position, torso offsets and segment lengths measured on the same frame, rebuilds the landmarks of Table 1 to below $10^{-11}$ m, at most $2.98 \times 10^{-12}$ m from the left-handed angles and $5.95 \times 10^{-12}$ m from the right-handed angles, so the two rebuilt skeletons coincide to the same order, as Figure 3 shows. The full note [2] carries six decimals, every intermediate quantity, the error tables, the relation between the angle sets and the choice of convention.

## References

[1] Lanqing Luo. Tracking and Reconstruction of Bi-Manual Object Handling Task Using RGB-D Sensing. Thesis, Simon Fraser University, 2026.

[2] Lanqing Luo. Joint angles from eight body landmarks in two frame conventions. Technical note, 8 October 2026.
