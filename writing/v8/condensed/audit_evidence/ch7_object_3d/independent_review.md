# Independent review of Chapter 7 object waypoint figures

STATUS: PASS

Scope: bounded review of the final `make_ch7_object_waypoint_figures.py` and its two PNG outputs against baseline commit `b52235513477f5d44a4b790d52858b12a934b4b9`. The final presentation refresh increases the source canvas from 10.2 x 4.8 inches to 10.2 x 7.2 inches and moves the W4 annotation to avoid the y=80 tick. No generator, builder, source data, or image was edited during this review.

## Verified findings

- Accepted-sample and waypoint semantics are preserved. The current and baseline abstract syntax trees are identical for `floor_translation`, `scene_samples`, and `waypoints`. Their SHA256 hashes are, respectively, `a101ee738dece00563615b9264faf446a1c72037e52c8dc9b39b9fd6c6f38c45`, `424b112bfd8795659a4bb49d8493d74cdde51fa46c4d61fa427ba8975f0e5d11`, and `07b410f176c9be4a3515f84e0b60e93b271e854f93dd8a28d7ca63db2e41f903`. The complete baseline generator blob has SHA256 `ef04239992cddeccb203b62050d88391ca3621f33c5e1bc10f0f313412787b1c`.
- The pinned accepted-frame and Scene-coordinate hashes remain `c82326cbaa7c9fdba57ea580ba02f1bab690191a990f10050906b5bb468f417b` and `c11ae1e39f0a52cda6b8ad2814bbf6a9e72175ea0c0280d115bbf2948c9ac574` for R6b (889 samples), and `544423cbe90f4626c11f2c0847e6109efc7648cd5db7a6dd8c6247c4f2db6c2c` and `8dfc8a963ce4be40f456805383b771c8b70a0597fb8cdf0c5c19f6a342e982f1` for R7 (1,487 samples).
- Recomputed waypoint coordinates match the pinned values to floating-point precision. The maximum absolute differences for W1-W4 are `7.105427357601002e-15`, `1.4210854715202004e-14`, `0`, and `1.4210854715202004e-14` cm for R6b, and `2.842170943040401e-14`, `1.4210854715202004e-14`, `0`, and `2.842170943040401e-14` cm for R7.
- Panel geometry is truthful. The upper-left view draws Scene x horizontally and Scene y vertically. The lower-left view draws Scene x horizontally and Scene z vertically. The 3D call maps Scene `(x, y, z)` to graphics `(x, z, y)`, so the graphics vertical axis is Scene y; its axis labels and waypoint label offsets use the same mapping.
- Equal metric axis scaling is implemented for the x-z and 3D views. The x-z axes use an equal data aspect; in the final taller layout, measured displayed inches per centimetre are `0.050731226181613805` horizontally and vertically for R6b, and `0.0525930011385575` horizontal and `0.052593001138557485` vertical for R7. Each 3D data axis has the same span (`46.423000847890314` cm for R6b and `48.25772463251584` cm for R7) and the 3D box aspect is `(1, 1, 1)`. Normal perspective foreshortening does not alter that data-axis scaling claim.
- The final source image is 10.2 x 7.2 inches. At 6.1 inches embedded width it is 4.305882352941177 inches high; its 13.5-point smallest source labels become 8.073529411764707 points. The final W4 Scene-coordinate label offset is `(-5.0, 4.0, 0.0)` cm.
- No physical reference path was introduced. The views draw only accepted reconstructed samples and reconstructed waypoint markers; the captions do not claim registration to a physical tape or route.

## Final artifact hashes

- Generator: `a0209284bcdaa090f96a8ac980c02484fe8a5657b0a3cd08571cb789bf0cc9c9`
- R6b PNG, 2244 x 1584: `85c2cce666c7c15a42828f1698b3df9b82f1dd9b64500469621778755ba07d08`
- R7 PNG, 2244 x 1584: `e17006f3a4a5a344e923f0ea8aac1dfe459fc83d4a8bc3145bfdfb16bb4222c6`
- Generator provenance: `09858a4082931d7e271b0f947dfe95c96c5ada4e62008ca9d2d179ad4e931e40`

Concerns: none within the requested scope.
