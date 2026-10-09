<!-- Step 2a of the field-first study (2026-10-01). Produced by workflow wf_6a1ac7f0-566:
two analysts per subfield (problem-centric and method-centric lenses) over the 1563-row
inventory in research/field_papers_2026-10-01.json, one reconciler per subfield, a
cross-subfield synthesis, a critic pass and a final revision (24 agents, no network).
The seven reconciled subfield maps are in field_themes_maps_2026-10-01.json. The master
session checked that every subfield's theme counts sum to its row count (354, 149, 207,
439, 269, 496, 254), that twelve representative titles named here exist in the inventory,
and that the critic's HIGH findings (coverage exclusions in section 6) were applied.
This file answers only "what are the venues doing"; the pain points from the papers'
own limitations sections are step 2b, and the ranked field map is step 3. -->

# 2024-2026 顶会领域地图（上半部分）：顶会在做什么、在说什么

本文只回答一个问题：2024-2026 年，CVPR、ICCV、ECCV、NeurIPS、ICLR、SIGGRAPH、CoRL、RSS、ICRA、IROS、T-RO、TPAMI 和 IJCV 在"人手持物体操作的 3D 跟踪与重建"及相邻问题上发表了什么，这些论文各自说在解决什么问题。文中的计数全部取自七份子领域地图（S1-S7）经调和后的主题分配，本步没有重新给清单行分类。论文局限部分里的痛点放到下一步处理；本文只记录清单中少见或缺席的内容。括号里的三个数字依次是 2024、2025、2026 年的行数，2026 年数据不完整。

## 1. 一页总览

**计数规则。** 七份子领域地图读取的行数合计 2168 行：S1 354 行，S2 149 行，S3 207 行，S4 439 行，S5 269 行，S6 496 行，S7 254 行。清单本身只有 1563 篇论文，说明不少论文同时带有多个子领域标签。例如 HaMeR 同时是 S1、S3、S4 的代表论文。所以下面每条主线只把各子领域主题的原始计数并排列出，不做跨子领域加总。

**总体格局。** 按体量看，机器人一侧最大。S6 有 496 行；S3 的 207 行里，机器人相关主题占 100 行。估计一侧在 2025-2026 年向单目或第一人称 RGB 视频收敛。S1 的两位分析者读贡献文本后得出相同判断：到 2026 年，事实上的前端是一组冻结的基础模型。HaMeR、WiLoR 或 HaWoR 负责手；DUSt3R、VGGT、MoGe 或 CUT3R 负责相机与深度；SAM 或 SAM3D 负责物体；另外再配上图像到 3D 的模型。深度传感器和标定多相机系统大多退到了真值采集和机器人端。

**主线 1：单视图手部与人体网格回归，已成为下游的默认前端。**
- 势头：S4 单图相机系人体网格主题 56 行（23/23/6），仍是 S4 最大的主题，但标为下降。S4 视觉手部姿态主题 40 行（14/11/15），标为上升；2026 年的增量集中在第一人称、世界坐标方向的 arXiv 与研讨会论文。S1 仅手部主题 30 行（10/10/10），稳定。S3 双手无物体主题 17 行（7/5/4），下降。
- 覆盖：CVPR 2024 和 ECCV 2024 两轮筛选部分排除了通用单目 HMR，所以 S4 单图主题的 56 行是下限，其下降趋势可能部分来自筛选，而不是领域本身（见第 6 节）。
- 载体：以视觉会议为主。S4 单图主题中 CVPR 16 行、NeurIPS 10 行、ECCV 7 行、ICCV 6 行、TPAMI 6 行。S1 仅手部主题中 CVPR 10 行。
- 输入：单张单目 RGB。合成渲染数据已成为主要监督来源，S4 单图主题没有一行使用深度。
- 代表论文：Reconstructing Hands in 3D with Transformers（HaMeR, CVPR 2024）；WiLoR（CVPR 2025）；SAM 3D Body: Robust Full-Body Human Mesh Recovery（CVPR 2026）。

**主线 2：移动相机和第一人称视角下的世界坐标 4D 运动。**
- 势头：S4 世界坐标人体运动 29 行（10/6/11），上升。S4 第一人称佩戴者姿态 31 行（11/7/9），稳定。S3 第一人称双手运动 14 行（4/5/4），上升。S1 世界坐标手与手-物体运动 8 行（0/4/4），是新主题。S7 头显相机追踪 16 行（6/3/5），上升。
- 三点信号的变化：同期基于头显加手柄三点信号的全身估计，在 S7 中为 16 行（11/4/1），标为下降；在 S4 中为 14 行（7/4/3），标为稳定。S7 地图据此认为 XR 身体追踪正在转向头显自带的相机；但 S4 把三点追踪和第一人称佩戴者姿态都标为稳定，所以这一判断只来自 S7 地图。
- 载体：几乎全在视觉会议。S4 世界坐标主题有 CVPR 15 行。S1 世界坐标主题只有 CVPR 5 行、ECCV 1 行、arXiv 2 行，没有机器人会议，尽管机器人学习是这些论文自述的动机。
- 输入：单目（多为头戴）RGB 视频加 SLAM 相机位姿。度量尺度来自 SLAM 或深度基础模型，推理时不用深度传感器。
- 代表论文：WHAM（CVPR 2024）；HaWoR（CVPR 2025）；Estimating Body and Hand Motion in an Ego-sensed World（EgoAllo, CVPR 2025）。

**主线 3：手与物体、人与物体的联合重建。**
- 势头：S1 单帧手-物体联合估计 23 行（8/9/6）。S1 单目视频无模板手-物体重建 25 行（8/8/9）。S3 双手加物体 12 行（3/6/3），上升。S5 人手与手持物体联合 24 行（6/7/11），上升。S2 单图人-物重建 16 行（3/6/7），上升。S2 单目视频 4D 人-物重建 8 行（0/1/7），是新主题。
- 载体：以 CVPR 为主。S1 视频主题、S5 手-物体主题、S2 单图主题中，CVPR 分别为 8 行、9 行、8 行。
- 输入：S1 视频主题的 25 行里，23 行是静态相机拍的单目 RGB 视频，只有 PickScan 一行用 RGB-D。除 PickScan 外没有一行用度量深度，尺度来自手部尺寸先验，或者干脆不定。
- 方法：从逐序列的神经 SDF 优化，转向 3D 高斯泼溅加基础模型初始化。
- 代表论文：HOLD（CVPR 2024）；BIGS（CVPR 2025）；CARI4D: Category Agnostic 4D Reconstruction of Human-Object Interaction（CVPR 2026）。

**主线 4：物体 6D 位姿估计与跟踪。**
- 势头（均来自 S5）：基于 CAD 的未见物体 26 行（9/13/4）；实例级 24 行（9/10/5），下降；无 CAD 的参考视图位姿 25 行（6/10/9），上升；类别级 20 行（8/12/0），下降；在线建模跟踪 14 行（2/6/6），上升；跟踪鲁棒层 11 行（1/5/5），上升。S1 另有物体侧跟踪与铰接恢复 9 行（0/5/4）。
- 增长去向：四个单帧主题合计 32/45/18 行，在当年 S5 总行数（74/107/74）中的占比下降，增长转向了视频跟踪。
- 载体分化：CAD 未见物体主题有 CVPR 11 行；跟踪鲁棒层是机器人会议 5 行、arXiv 5 行，几乎不出现在 CVPR、ICCV、ECCV。
- 输入：以单帧静态 RGB 或 RGB-D 为主。2025-2026 年出现一组不用深度传感器的单目 RGB 跟踪器。
- 代表论文：FoundationPose（CVPR 2024）；SAM-6D（CVPR 2024）；Any6D（CVPR 2025）。

**主线 5：生成式交互合成与交互预测。**
- 势头：S2 运动学 HOI 生成 33 行（12/16/5）。S1 HOI 运动序列合成 30 行（9/13/8）。S1 静态抓取合成 23 行（12/8/3），下降。S1 手-物体图像与视频生成 25 行（5/10/10），上升。S3 双手生成 17 行（4/9/4）。S6 交互预测与世界模型 22 行（5/6/11），上升。
- 覆盖：S2 方法检索排除了纯文本到 HOI 的生成，CVPR 2024 一轮排除了文本到动作，所以 S2 生成主题的 33 行是下限（见第 6 节）。
- 载体：横跨三个社区。以 S1 运动合成主题为例，CVPR 5 行、SIGGRAPH 4 行、SIGGRAPH Asia 2 行、NeurIPS 3 行、ICLR 3 行，没有机器人会议。
- 输入：多数推理时没有传感器输入，训练数据来自标记动捕，如 GRAB、ARCTIC、OMOMO。
- 代表论文：Text2HOI（CVPR 2024）；Controllable Human-Object Interaction Synthesis（CHOIS, ECCV 2024）；HOIGPT（CVPR 2025）。

**主线 6：物理、生物力学与临床运动评估。**
- 势头：S1 物理感知精化 9 行（5/1/3）。S2 物理仿真人形 HOI 控制 14 行（5/7/2）。S4 物理与生物力学 28 行（8/15/4），上升。S7 生物力学 17 行（5/8/3），上升。S7 临床、康复与包容性人群 28 行（6/11/9），上升。
- 载体：较为混合。S4 物理主题含 NeurIPS 5 行、图形学 4 行、arXiv 7 行（多为临床论文）。S2 物理控制主题没有机器人会议。
- 输入：多为单目 RGB 视频，包括智能手机拍摄。监督来自动捕加测力台，以及仿真得到的力矩和肌肉激活。
- 代表论文：PhysPT（CVPR 2024）；InterMimic（CVPR 2025）；Reconstructing Humans with a Biomechanically Accurate Skeleton（CVPR 2025）。

**主线 7：接触、压力与力的估计。**
- 势头：S1 接触、压力与力主题 17 行（2/4/11），在 S1 估计类主题中，2026 年的行数最多。S2 稠密接触与可供性 11 行（5/3/2）。
- 载体：S1 主题中 NeurIPS 3 行、CVPR 2 行、ECCV 2 行，HANDS 研讨会与挑战报告 4 行。
- 输入：测试时是单张 RGB 或单目视频，17 行中有 12 行是第一人称。真值来自压力垫、触觉手套、sEMG、力传感器或装有传感器的物体。
- 代表论文：EgoPressure（CVPR 2025）；Learning Dense Hand Contact Estimation from Imbalanced Data（HACO, NeurIPS 2025）；InteractVLM（CVPR 2025）。

**主线 8：可穿戴与非 RGB 传感。**
- 势头：S4 身体穿戴稀疏传感 36 行（10/19/7），2025 年达峰。S4 手与手臂可穿戴传感 17 行（5/8/4）。S4 第三人称非 RGB 传感 38 行（9/13/9）。S1 非 RGB 手部估计 14 行（4/3/7）。S5 机器人手内视触觉 22 行（3/9/10）。
- 载体按传感器分化：
  - IMU 全身捕捉主要在视觉与图形学会议（CVPR 13 行，图形学 7 行）。
  - sEMG、手套与外骨骼主要在机器人会议（17 行中 11 行）。
  - 视触觉几乎全在机器人会议（22 行中 20 行）。
- 代表论文：Ultra Inertial Poser（SIGGRAPH 2024）；emg2pose（NeurIPS 2024）；V-HOP: Visuo-Haptic 6D Object Pose Tracking（RSS 2025）。

**主线 9：采集系统、数据集与基准。**
- 势头：S1 采集与数据集 35 行（12/10/4），另有 9 行早于 2024 年。S2 采集 26 行（9/8/2）。S3 固定装置数据集 19 行（5/7/1）。S5 刚体位姿数据集 29 行（8/4/6）。S6 手-物体采集数据集 26 行（7/10/5）。
- 关于 S1 的下降：有一部分是覆盖造成的。S1 地图说明，2026 年的数据集行多数是机器人学习语料，已计入机器人迁移主题。另外，清单中 NeurIPS 2026 为 0 行，所以 NeurIPS 2026 Datasets and Benchmarks 的论文都不在清单中。
- 载体：S1 数据集主题 35 行中 CVPR 占 17 行。S6 数据集主题 26 行中视觉会议占 15 行，是 S6 唯一以视觉会议为主的主题。
- 输入：S1 的 35 行里，28 行用多视角或多相机采集。
- 代表论文：OAKINK2（CVPR 2024）；HOT3D（CVPR 2025）；HO-Cap（NeurIPS 2025）。

**主线 10：示范采集硬件与遥操作。**
- 势头：S6 遥操作与 XR 接口 71 行（22/35/14），占当年 S6 行数的比例从约 20% 降到约 8%。S6 无机器人手持与穿戴设备 57 行（9/22/26），占比从约 8% 升到约 15%。S3 遥操作与穿戴示范设备 23 行（8/7/8）。
- 载体：S6 遥操作主题 71 行中 64 行来自机器人会议，没有 CVPR、ICCV、ECCV 的论文。
- 输入：VR 头显手部追踪、外骨骼编码器、带腕部鱼眼相机和视觉惯性 SLAM 的手持夹爪、手套。S6 手持主题 57 行中有 26 行带触觉、力或 EMG 通道。
- 代表论文：Universal Manipulation Interface（UMI, RSS 2024）；DexCap（RSS 2024）；Open-TeleVision（CoRL 2024）。

**主线 11：从人类视频和第一人称数据学习机器人操作。**
- 势头：
  - S1 人到机器人迁移 61 行（11/25/25），是 S1 最大、增长最快的主题。
  - S6 第一人称人类数据协同训练 41 行（0/12/29），是新主题。
  - S6 一或少个视频的模仿 60 行（22/25/12），占比从约 20% 降到约 7%。
  - S6 物理仿真灵巧跟踪 20 行（3/12/5）。
  - S6 人形与角色 40 行（12/16/12）。
  - S3 人类视频到双臂机器人 18 行（3/9/6）。
  - 相邻子线人机交接：S3 中 21 行（6/12/2），S6 中 14 行（3/8/1）。
- 载体：S1 迁移主题有 ICRA 13 行、CoRL 9 行、RSS 9 行、arXiv 12 行。
- 输入：单目 RGB 人类视频。手和物体的状态由现成估计器组合得到。评估看的是作者自有任务上的成功率，而不是位姿误差。
- 代表论文：OKAMI（CoRL 2024）；ManipTrans（CVPR 2025）；EgoDex（ICLR 2026）。

**主线 12：数字人化身、渲染与实时远程呈现。**
- 势头（均来自 S7）：单目视频逐人化身 35 行（13/16/6）；前馈单图化身 19 行（3/11/5），上升；工作室 codec 化身 21 行（5/10/5）；实时远程呈现 20 行（8/8/4）；手部化身 10 行（5/2/3）。
- 载体：前馈化身有 ICLR 7 行；codec 化身有 CVPR 8 行、SIGGRAPH 3 行、SIGGRAPH Asia 3 行。
- 输入：使用时是单目视频、单张图像或单个网络摄像头。codec 与远程呈现主题都没有深度输入。
- 表征：3D 高斯基本取代了 NeRF。S7 中提到高斯的行数约为 19/33/21（关键词约数）。
- 代表论文：3DGS-Avatar（CVPR 2024）；LHM（ICCV 2025）；URHand: Universal Relightable Hands（CVPR 2024）。

## 2. 分子领域地图

各子领域的中文名称是本文根据其主题内容所作的概括，地图本身只给出 S1-S7 编号。

### S1 手与手-物体的 3D 估计

S1 共 354 行，2024/2025/2026 年分别为 99/128/117 行，另有 10 行早于 2024 年。

| 主题 | 行数（24/25/26） | 趋势 | 代表论文 |
| --- | --- | --- | --- |
| 仅手部 RGB 姿态与网格 | 30（10/10/10） | 稳定 | HaMeR (CVPR 2024); WiLoR (CVPR 2025); Hamba (NeurIPS 2024) |
| 单帧手与手持物体联合估计 | 23（8/9/6） | 稳定 | HOISDF (CVPR 2024); D-SCo (ECCV 2024); EasyHOI (CVPR 2025) |
| 单目视频无模板手-物体重建 | 25（8/8/9） | 稳定 | HOLD (CVPR 2024); BIGS (CVPR 2025); ForeHOI (CVPR 2026) |
| 世界坐标手与手-物体运动 | 8（0/4/4） | 新 | Dyn-HaMR (CVPR 2025); HaWoR (CVPR 2025); WHOLE (CVPR 2026) |
| 物理感知精化与跟踪 | 9（5/1/3） | 稳定 | GeneOH Diffusion (ICLR 2024); HOIC (SIGGRAPH 2024); PAD-Hand (CVPR 2026) |
| 深度/事件/惯性/手套/触觉手部估计 | 14（4/3/7） | 上升 | HandDiff (CVPR 2024); FSGlove (IROS 2025); MGDHand (CVPR 2026) |
| 接触、压力与力估计 | 17（2/4/11） | 上升 | EgoPressure (CVPR 2025); HACO (NeurIPS 2025); EgoPHI (ECCV 2026) |
| 物体侧 6-DoF 跟踪与铰接恢复 | 9（0/5/4） | 新 | POGS (ICRA 2025); Articulated Object Estimation in the Wild (ArtiPoint, CoRL 2025); FunREC (CVPR 2026) |
| 采集系统与数据集 | 35（12/10/4） | 下降 | OAKINK2 (CVPR 2024); HOT3D (CVPR 2025); SHOW3D (CVPR 2026) |
| 静态抓取合成 | 23（12/8/3） | 下降 | SemGrasp (ECCV 2024); UGG (ECCV 2024); DexVLG (ICCV 2025) |
| 手-物体运动序列合成 | 30（9/13/8） | 稳定 | Text2HOI (CVPR 2024); BimArt (CVPR 2025); TOUCH (ICLR 2026) |
| 手-物体图像与视频生成 | 25（5/10/10） | 上升 | HOIDiffusion (CVPR 2024); ManiVideo (CVPR 2025); SViMo (NeurIPS 2025) |
| 手部化身与外观 | 11（4/4/3） | 稳定 | URHand (CVPR 2024); FLASHand (SIGGRAPH 2026) |
| 第一人称手轨迹与目标预测 | 15（3/7/5） | 上升 | Diff-IP2D (IROS 2025); MADiff (TPAMI 2026); EggHand (CVPR 2026) |
| 人到机器人迁移 | 61（11/25/25） | 上升 | DexCap (RSS 2024); ManipTrans (CVPR 2025); EgoDex (ICLR 2026) |
| 其他 | 19（6/7/5） | 稳定 | HOIST-Former (CVPR 2024); Multi-View 3D Point Tracking (MVTracker, ICCV 2025) |

**数据集。** 按数据集字段子串匹配，出现最多的是：ARCTIC 24 行，DexYCB 22 行，HO3D 22 行，GRAB 16 行，OakInk/OakInk2 16 行，H2O 14 行，FreiHAND 9 行，HOT3D 9 行，Ego-Exo4D 8 行，HOI4D 7 行。约 107 行（30%）没有写明数据集。
- 单图估计主要用 FreiHAND、DexYCB 和 HO3D。
- 无模板视频重建主要在 HO3D 和 HANDS 2024/2025 的 ARCTIC 类别无关赛道上竞争。按行内描述，该赛道只有 9 个刚体物体测试片段，以手相对的 Chamfer 距离 CD_h 计分。

**自述问题。** 手与物体互相遮挡；没有 CAD 模板的未见物体；实验室外的泛化；头戴相机下手的绝对位置；穿透与漂浮接触；遮挡下接触不可见，且没有力的真值；机器人数据成本高，以及人与机器人之间的具身差异。

**估计与消费的划分。** 估计核心约 135 行，加上数据集约 170 行。另有约 114 行（静态抓取、运动合成、机器人迁移）是使用手-物体位姿，而不是估计它。

### S2 全身人-物交互

S2 共 149 行，其中 2024-2026 年 140 行（44/56/40），另有 9 行早于 2024 年。

| 主题 | 行数（24/25/26） | 趋势 | 代表论文 |
| --- | --- | --- | --- |
| 运动学 HOI 生成（推理无传感器） | 33（12/16/5） | 稳定 | CG-HOI (CVPR 2024); CHOIS (ECCV 2024); InterDreamer (NeurIPS 2024) |
| 采集装置与身体-物体真值数据集 | 26（9/8/2） | 稳定 | InterCap (IJCV 2024); HOI-M^3 (CVPR 2024); ParaHome (CVPR 2025) |
| 单图人与物体联合重建 | 16（3/6/7） | 上升 | Joint Reconstruction of 3D Human and Object via Contact-Based Refinement Transformer (CONTHO, CVPR 2024); PICO (CVPR 2025); Reconstructing Humans and Objects in Interaction using Large Reconstruction Models (MILO, ECCV 2026) |
| 物理仿真人形执行或模仿 HOI | 14（5/7/2） | 稳定 | Omnigrasp (NeurIPS 2024); MaskedMimic (SIGGRAPH Asia 2024); InterMimic (CVPR 2025) |
| 稠密接触、可供性与交互场 | 11（5/3/2） | 稳定 | LEMON (CVPR 2024); EgoChoir (NeurIPS 2024); InteractVLM (CVPR 2025) |
| 单目视频 4D HOI 重建 | 8（0/1/7） | 新 | CARI4D (CVPR 2026); RHINO (CVPR 2026); HAT-4D (ECCV 2026) |
| 人与物体的高斯泼溅与神经渲染 | 8（0/3/4） | 上升 | GASPACHO (arXiv 2025); PhysHO (CVPR 2026) |
| 全身示范到机器人与人形 | 8（2/4/2） | 稳定 | OKAMI (CoRL 2024); VideoMimic (CoRL 2025); OmniRetarget (ICRA 2026) |
| 人与静态场景联合重建 | 7（1/2/4） | 上升 | HSR (ECCV 2024); HAMSt3R (ICCV 2025); Human3R (ICLR 2026) |
| HOI 预测、意图与动作识别 | 6（4/2/0） | 下降 | Forecasting of 3D Whole-body Human Poses with Grasping Objects (CVPR 2024); FIction (CVPR 2025) |
| 身体穿戴与非相机 HOI 感知 | 5（2/0/3） | 上升 | I'M HOI (CVPR 2024); IMU-HOI (CVPR 2026); ECHO (ECCV 2026) |
| 2D HOI 视频生成 | 3（0/1/2） | 新 | HOMA (SIGGRAPH Asia 2025); SparseCtrl-HOI (ECCV 2026) |
| 其他 | 4（1/3/0） | 稳定 | 两篇综述等 |

**数据集。** BEHAVE 被提及最多（12 行），其次是 InterCap 7 行、OMOMO 6 行、GRAB 4 行、DAMON 4 行。149 行中有 53 行没有写明数据集。

**真值来源，分三类：**
- 在多视角 RGB(-D) 或 RGB 穹顶上拟合 SMPL 和物体模板，例如 BEHAVE、InterCap、CHAIRS、HODome。这类真值本身的误差很少报告。
- 光学标记动捕，例如 OMOMO、GRAB、HIMO、HUMOTO。
- 野外伪真值，例如 DAMON、PICO-db、Open3DHOI、Open4DHOI。

**自述问题。** 严重互遮挡与深度歧义；依赖已知物体模板；穿透和漂浮；文本与 HOI 的配对数据稀缺；移动相机下的度量尺度；为人形仿真提供可用的参考动作。

**其他事实。** 生成、物理控制和视频生成三类合计 50 行，推理时都不用传感器。生成主题的 33 行是下限，因为 S2 方法检索排除了纯文本到 HOI 的生成（见第 6 节）。

### S3 双手操作

S3 共 207 行（62/86/47），另有 12 行早于 2024 年。

| 主题 | 行数（24/25/26） | 趋势 | 代表论文 |
| --- | --- | --- | --- |
| 两只交互手的姿态与外观（无物体） | 17（7/5/4） | 下降 | HaMeR (CVPR 2024); InterHandGen (CVPR 2024); WiLoR (CVPR 2025) |
| 双手加操作物体联合重建 | 12（3/6/3） | 上升 | QORT-Former (AAAI 2025); BIGS (CVPR 2025); GHOST (CVPR 2026) |
| 第一人称与移动相机双手运动 | 14（4/5/4） | 上升 | Dyn-HaMR (CVPR 2025); HaWoR (CVPR 2025); StableHand (arXiv 2026) |
| 固定装置双手-物体数据集 | 19（5/7/1） | 稳定 | OAKINK2 (CVPR 2024); TACO (CVPR 2024); GigaHands (CVPR 2025) |
| 第一人称、可穿戴与野外采集 | 8（2/2/4） | 上升 | Ego-Exo4D (CVPR 2024); HOT3D (CVPR 2025); SHOW3D (CVPR 2026) |
| 双手运动与图像视频生成 | 17（4/9/4） | 上升 | DiffH2O (SIGGRAPH Asia 2024); HOIGPT (CVPR 2025); HandX (CVPR 2026) |
| 物理仿真跟踪与灵巧手重定向 | 9（3/3/3） | 稳定 | ArtiGrasp (3DV 2024); ManipTrans (CVPR 2025); DexMachina (ICML 2026) |
| 从人类视频学双臂机器人技能 | 18（3/9/6） | 上升 | ScrewMimic (RSS 2024); You Only Teach Once (RSS 2025); DemoBot (ICRA 2026) |
| 遥操作与穿戴示范设备 | 23（8/7/8） | 稳定 | UMI (RSS 2024); Open-TeleVision (CoRL 2024); AirExo-2 (CoRL 2025) |
| 双臂策略、仿真基准与示范增广 | 29（9/14/5） | 稳定 | ALOHA Unleashed (CoRL 2024); RDT-1B (ICLR 2025); RoboTwin (CVPR 2025) |
| 人机交接与物理协作 | 21（6/12/2） | 稳定 | GenH2R (CVPR 2024); DexH2R (ICCV 2025); Stereo Hand-Object Reconstruction for Human-to-Robot Handover (IROS 2025) |
| 双手动作理解 | 11（4/5/1） | 稳定 | On the Utility of 3D Hand Poses for Action Recognition (ECCV 2024); 2HandedAfforder (ICCV 2025) |
| 双手技能表演 | 8（4/2/2） | 稳定 | FurElise (SIGGRAPH Asia 2024); PianoMotion10M (ICLR 2025) |
| 其他 | 1（0/0/0） | 稳定（唯一一行为 2023 年综述） | 一篇 IJCV 2023 综述 |

**结构。** 机器人相关主题合计 100 行；前三个人手估计主题合计 43 行；另有 27 行是数据集。

**数据集。**
- ARCTIC 出现在 14 行，承载 HANDS 2023-2025 的赛道，也是物理重定向最主要的人类动作来源。
- InterHand2.6M 出现在 11 行，仍是无物体双手问题唯一的标准数据集。
- 消费级设备追踪也被当作真值，例如 EgoDex 用 Vision Pro，但行内没有报告独立的精度核查。

**自述问题。** 两手之间的遮挡和左右混淆；未知物体形状；相机运动与手运动纠缠在一起；双臂协调；示范数据成本高；交接中的遮挡和透明物体。

**深度的位置。** 按关键词匹配，提到深度的有 31 行（11/9/8，另有 3 行早于 2024 年），但视觉侧的双手估计方法中没有一行以深度为输入。

### S4 人体姿态与运动捕捉

S4 共 439 行（149/157/109），另有 24 行早于 2024 年。

| 主题 | 行数（24/25/26） | 趋势 | 代表论文 |
| --- | --- | --- | --- |
| 单图相机系人体姿态与网格 | 56（23/23/6） | 下降（下限） | TokenHMR (CVPR 2024); SMPLest-X (TPAMI 2025); SAM 3D Body (CVPR 2026) |
| 单目视频世界坐标人体运动 | 29（10/6/11） | 上升 | WHAM (CVPR 2024); TRAM (ECCV 2024); OnlineHMR (CVPR 2026) |
| 多人与近距离交互 | 24（10/7/5） | 稳定 | Multi-HMR (ECCV 2024); Harmony4D (NeurIPS 2024); CoMotion (ICLR 2025) |
| 头戴相机的佩戴者姿态 | 31（11/7/9） | 稳定 | EventEgo3D (CVPR 2024); Nymeria (ECCV 2024); UniEgoMotion (ICCV 2025) |
| AR/VR 三点追踪 | 14（7/4/3） | 稳定 | HMD-Poser (CVPR 2024); EgoPoser (ECCV 2024); FisherPoser (CVPR 2026) |
| 身体穿戴稀疏传感 | 36（10/19/7） | 上升 | DynaIP (CVPR 2024); Ultra Inertial Poser (SIGGRAPH 2024); Ground Reaction Inertial Poser (CVPR 2026) |
| 手与手臂可穿戴关节角估计 | 17（5/8/4） | 上升 | emg2pose (NeurIPS 2024); FSGlove (IROS 2025); Robust Hand Tracking from Visual-Inertial Fusion (ICRA 2026) |
| 第三人称非 RGB 传感 | 38（9/13/9） | 稳定 | LiveHPS (CVPR 2024); X-Fi (ICLR 2025); RAPTR (NeurIPS 2025) |
| 视觉 3D 手部姿态与网格 | 40（14/11/15） | 上升 | HaMeR (CVPR 2024); HandDiff (CVPR 2024); HaWoR (CVPR 2025) |
| 物理与生物力学有效性 | 28（8/15/4） | 上升 | PhysPT (CVPR 2024); ImDy (ICLR 2025); OpenCap Monocular (arXiv 2026) |
| 人与场景或操作物体联合重建 | 20（3/6/10） | 上升 | I'M HOI (CVPR 2024); InterCap (IJCV 2024); Human3R (ICLR 2026) |
| 多视角工作室与光学动捕处理 | 20（8/8/4） | 稳定 | FreeMan (CVPR 2024); RoMo (SIGGRAPH Asia 2024); DAMO (SIGGRAPH 2025) |
| 遮挡下的着装人体表面与化身 | 11（4/4/3） | 稳定 | ANIM (CVPR 2024); OccFusion (NeurIPS 2024); CHROME (ICCV 2025) |
| 欠代表人群与临床场景 | 14（4/6/4） | 上升 | SignAvatars (ECCV 2024); AJAHR (ICCV 2025); Care-PD (NeurIPS 2025) |
| 人体姿态作为机器人输入 | 36（18/10/8） | 稳定 | HumanPlus (CoRL 2024); HARPER Dataset (IROS 2024); VideoMimic (CoRL 2025) |
| 其他 | 25（5/10/7） | 稳定 | DPoser-X (ICCV 2025); VolumetricSMPL (ICCV 2025) |

**数据集。** 约 199 行没有写明数据集。
- 3DPW 约出现在 19-20 行。
- EMDB 与 RICH 是世界坐标方向的基准；"EMDB 是事实标准"这一说法出自分析者的知识，不是清单行。
- AMASS 是运动先验和合成 IMU/VR 信号的通用训练来源。
- 合成渲染已成为回归器的主要监督。

**数据集行的分布。** 71 行类型为数据集，另有 7 行为基准，集中在非 RGB 传感（14 行）、欠代表人群（10 行）、第一人称（8 行）和物理（6 行）。专门针对遮挡的数据集只有 VOccl3D（合成）、OcMotion、3DPW-OC 和 OCHuman（只有 2D 标签），所以物体遮挡下的真实 3D 真值很少。

**自述问题。** 遮挡与截断；深度歧义；移动相机下人与相机运动纠缠；稀疏 IMU 的漂移；头显视野之外的下半身；相机看不到时的手与手臂；隐私与远距离。

**与物体相关的部分。** 只有 5 行同时估计人和物体的位姿：I'M HOI、IMU-HOI、ECHO、EgoGrasp、InterCap。

### S5 物体 6D 位姿与跟踪

S5 共 269 行（74/107/74），另有 14 行早于 2024 年。

| 主题 | 行数（24/25/26） | 趋势 | 代表论文 |
| --- | --- | --- | --- |
| 实例级单图 6D | 24（9/10/5） | 下降 | 6D-Diff (CVPR 2024); HiPose (CVPR 2024); CLOSURE (RSS 2024) |
| 基于 CAD 的未见物体单图位姿 | 26（9/13/4） | 稳定 | SAM-6D (CVPR 2024); GigaPose (CVPR 2024); FoundPose (ECCV 2024) |
| 无 CAD 的参考视图或代理模型位姿 | 25（6/10/9） | 上升 | NOPE (CVPR 2024); Any6D (CVPR 2025); UnPose (CoRL 2025) |
| 类别级 6D/9D 位姿 | 20（8/12/0） | 下降 | SecondPose (CVPR 2024); Diff9D (TPAMI 2025); RFMPose (NeurIPS 2025) |
| 在线建模的视频跟踪 | 14（2/6/6） | 上升 | FoundationPose (CVPR 2024); 6DOPE-GS (ICCV 2025); KV-Tracker (CVPR 2026) |
| 跟踪鲁棒层 | 11（1/5/5） | 上升 | RGBTrack (IROS 2025); DynamicPose (IROS 2025); RRTrack (arXiv 2026) |
| 事件相机高速跟踪 | 8（2/2/4） | 上升 | EDOPT (ICRA 2024); Event6D (CVPR 2026) |
| 机器人手内视触觉位姿 | 22（3/9/10） | 上升 | V-HOP (RSS 2025); ViTa-Zero (ICRA 2025); TwinTrack (ICRA 2026) |
| 人手与手持物体联合位姿与 4D 重建 | 24（6/7/11） | 上升 | HOISDF (CVPR 2024); WHOLE (CVPR 2026); ComPose (arXiv 2026) |
| 从视频提取物体轨迹供机器人学习 | 21（4/11/6） | 上升 | Robot See Robot Do (CoRL 2024); 6D Object Pose Tracking in Internet Videos for Robotic Manipulation (ICLR 2025); Real2Render2Real (CoRL 2025) |
| 多物体持久性与物理一致性 | 9（2/3/4） | 上升 | Object Permanence Filter (ICRA 2024); Lost & Found (IROS 2025); Picasso (RSS 2026) |
| 铰接物体部件位姿与结构 | 10（3/5/2） | 稳定 | EfficientCAPER (NeurIPS 2024); A Helping (Human) Hand in Kinematic Structure Estimation (ICRA 2025) |
| 稠密 3D 点与可变形物体跟踪 | 6（4/2/0） | 稳定 | TAPVid-3D (NeurIPS 2024); Multi-View 3D Point Tracking (ICCV 2025) |
| 基准标记、光学标记与设备跟踪 | 6（3/3/0） | 稳定 | CopperTag (ICRA 2024); Encoded Marker Clusters (SIGGRAPH 2025) |
| 手-物体操作数据集 | 14（4/5/2） | 稳定 | TACO (CVPR 2024); HOT3D (CVPR 2025); EgoXtreme (CVPR 2026) |
| 刚体位姿数据集、基准与综述 | 29（8/4/6） | 稳定 | PACE (ECCV 2024); BOP Challenge 2024 (arXiv 2025); XYZ-IBD (ECCV 2026) |

**基准与真值。**
- 单帧位姿用 BOP 核心七个数据集计分，在 22 行中出现。真值是 CAD 模型与静态 RGB-D 的对齐，这里的"遮挡"指物体之间的杂乱堆放。
- 手持物体跟踪依赖两个基准：HO3D（8 行）和 YCBInEOAT（7 行）。说它们规模小，依据是分析者知识，不是清单行。
- HOT3D 被 BOP 2024 采纳为 BOP-H3，这是手持物体第一次进入标准位姿基准。
- 2025-2026 年有几个遮挡与快速运动基准，是被评估跟踪器的作者自建的合成集。
- 机器人手内触觉方向没有共享基准，22 行中有 14 行只有作者自己的实验。
- 269 行中有 122 行没有写明数据集。

**自述问题。** 遮挡与杂乱；物体对称；没有 CAD 模型；只有单个参考视图；跟踪漂移以及全遮挡后跟丢；被手或夹爪挡住；快速运动；透明物体；亚毫米级精度；位姿误差与抓取成功率之间的关系。

### S6 人类示范到机器人

S6 共 496 行（110/206/172），另有 8 行早于 2024 年。

| 主题 | 行数（24/25/26） | 趋势 | 代表论文 |
| --- | --- | --- | --- |
| 遥操作与 XR 示范接口 | 71（22/35/14） | 占比下降 | GELLO (IROS 2024); Mobile ALOHA (CoRL 2024); Open-TeleVision (CoRL 2024) |
| 无机器人的手持与穿戴设备 | 57（9/22/26） | 上升 | UMI (RSS 2024); ForceMimic (ICRA 2025); DexUMI (CoRL 2025) |
| 第一人称人类数据协同训练与语料 | 41（0/12/29） | 新 | EgoMimic (ICRA 2025); EgoDex (ICLR 2026); EgoVerse (RSS 2026) |
| 一或少个人类视频模仿特定任务 | 60（22/25/12） | 占比下降 | Track2Act (ECCV 2024); OKAMI (CoRL 2024); MimicFunc (CoRL 2025) |
| 无动作视频表征、潜在动作与奖励 | 35（8/17/10） | 稳定 | GR-1 (ICLR 2024); Latent action pretraining from videos (ICLR 2025); Moto (ICCV 2025) |
| 手-物体采集数据集 | 26（7/10/5） | 稳定 | OAKINK2 (CVPR 2024); GigaHands (CVPR 2025); HO-Cap (NeurIPS 2025) |
| 随手视频手-物体感知与数据引擎 | 22（0/7/15） | 新 | HaWoR (CVPR 2025); RoboWheel (CVPR 2026); DexImit (RSS 2026) |
| 物理仿真 RL 灵巧跟踪 | 20（3/12/5） | 稳定 | DexTrack (ICLR 2025); ManipTrans (CVPR 2025); DexMachina (ICML 2026) |
| 人体到人形机器人与仿真角色 | 40（12/16/12） | 稳定 | OmniH2O (CoRL 2024); InterMimic (CVPR 2025); OmniRetarget (ICRA 2026) |
| 机器人手抓取与可供性 | 28（7/13/8） | 稳定 | Grasp as You Say (NeurIPS 2024); DexVLG (ICCV 2025); GLOVER++ (CoRL 2025) |
| 交互预测与世界模型生成 | 22（5/6/11） | 上升 | Dreamitate (CoRL 2024); TASTE-Rob (CVPR 2025); ObjectForesight (ECCV 2026) |
| 像素级具身转换 | 11（0/4/7） | 新 | Phantom (CoRL 2025); Masquerade (ICRA 2026); HuRo (CoRL 2026) |
| 人机交接 | 14（3/8/1） | 下降 | GenH2R (CVPR 2024); SynH2R (ICRA 2024); MobileH2R (CVPR 2025) |
| 示范倍增与 real-to-sim-to-real | 14（1/6/7） | 上升 | CyberDemo (CVPR 2024); DexMimicGen (ICRA 2025); Video2Robo (CVPR 2026) |
| 机器人侧双臂策略、基准与语料 | 24（8/13/2） | 下降 | RDT-1B (ICLR 2025); RoboTwin (CVPR 2025); AgiBot World Colosseo (IROS 2025) |
| 其他 | 11（3/0/8） | 残余 | Robot Learning from Human Videos: A Survey (arXiv 2026) |

**评估方式。** 以作者自有任务上的真实机器人成功率为主，不同论文之间无法比较。上游感知输出被当作真值使用。

**数据集。**
- 约 98 行引入了数据集。按问题视角统计，约 132 行只用作者自有数据，约 125 行没有写明数据集。
- 常被引用的外部数据：UMI 格式数据约 12 行，Ego4D 约 10 行，EPIC-KITCHENS 7 行，OakInk/OakInk2、TACO、HOT3D 各 6 行。

**真值分两类。**
- 感知数据集用光学标记或稠密多视角拟合。
- 2025-2026 年的机器人学习语料依赖设备追踪或单目伪标签，例如 EgoDex 829 小时、EgoVerse 1,362 小时、EgoScale 20,854 小时。这些语料在行内都没有报告动作标签相对动捕的验证。

**自述问题。** 遥操作数据难以扩展；人与机器人在动作空间和视角上的差异；视频里缺少触觉和力；手持设备的位姿精度与同步；人类数据何时有助于协同训练、何时有害。

### S7 化身、XR、远程呈现与应用

S7 共 254 行，其中 2024-2026 年 239 行，另有 15 行早于 2024 年。

| 主题 | 行数（24/25/26） | 趋势 | 代表论文 |
| --- | --- | --- | --- |
| 单目视频或手机扫描的逐人化身 | 35（13/16/6） | 稳定 | 3DGS-Avatar (CVPR 2024); GoMAvatar (CVPR 2024); Vid2Avatar-Pro (CVPR 2025) |
| 单图或少图前馈化身 | 19（3/11/5） | 上升 | HumanSplat (NeurIPS 2024); LHM (ICCV 2025); FastAvatar (ICLR 2026) |
| 工作室 codec 化身 | 21（5/10/5） | 稳定 | Relightable Gaussian Codec Avatars (CVPR 2024); URAvatar (SIGGRAPH Asia 2024); SqueezeMe (SIGGRAPH 2025) |
| 实时自由视点与 3D 远程呈现 | 20（8/8/4） | 稳定 | GPS-Gaussian (CVPR 2024); VoluMe (ICCV 2025); Tele360 (arXiv 2026) |
| 实时单目网格回归 | 5（1/1/3） | 上升 | ProxyCap (CVPR 2024); WiLoR (CVPR 2025); OnlineHMR (CVPR 2026) |
| 手部化身 | 10（5/2/3） | 稳定 | URHand (CVPR 2024); OHTA (CVPR 2024); FLASHand (SIGGRAPH 2026) |
| 稀疏 XR 追踪器与穿戴传感 | 16（11/4/1） | 下降 | HMD-Poser (CVPR 2024); MANIKIN (ECCV 2024); EnvPoser (CVPR 2025) |
| 头显相机身体与手部追踪 | 16（6/3/5） | 上升 | EgoBody3M (ECCV 2024); FRAME (CVPR 2025); XR-Poser (CVPR 2026) |
| 生物力学姿态、动力学与肌肉 | 17（5/8/3） | 上升 | AddBiomechanics Dataset (ECCV 2024); Muscles in Time (NeurIPS 2024); SKEL-CF (ECCV 2026) |
| 临床、康复与包容性人群 | 28（6/11/9） | 上升 | TULIP (CVPR 2024); Care-PD (NeurIPS 2025); InclusiveVidPose (ICLR 2026) |
| 操作者动作映射到机器人或虚拟体 | 14（5/7/2） | 稳定 | Learning Human-to-Humanoid Real-Time Whole-Body Teleoperation (IROS 2024); OmniH2O (CoRL 2024); Lucid-XR (CoRL 2025) |
| 呈现远端场景的沉浸式遥操作界面 | 10（6/2/2） | 稳定 | Radiance Fields for Robotic Teleoperation (IROS 2024); Tele-GS (IROS 2025) |
| 物体与场景数字孪生 | 14（5/4/4） | 稳定 | Reconciling Reality through Simulation (RSS 2024); DTTDNet (CVPR Workshops 2025); FunREC (CVPR 2026) |
| 人或手与物体、场景联合重建 | 8（0/3/5） | 新 | ODHSR (CVPR 2025); Towards Dynamic 3D Reconstruction of Hand-Instrument Interaction in Ophthalmic Surgery (NeurIPS 2025); PhysHO (CVPR 2026) |
| 多视角工作室语料 | 15（4/2/1） | 稳定 | MVHumanNet (CVPR 2024); Codec Avatar Studio (NeurIPS 2024); HumanOLAT (ICCV 2025) |
| 其他 | 6（3/3/0） | 稳定 | Casper DPM (SIGGRAPH Asia 2024); AvatarGO (ICLR 2025) |

**数据与评估。**
- 单目化身拟合仍用小而旧的 ZJU-MoCap、PeopleSnapshot、NeuMan。
- 前馈方法用扫描语料，大型工作室语料提供先验和重光照真值。以 PSNR、SSIM、LPIPS 计分是分析者的知识，不是行内信息。
- 稀疏 XR 追踪在 AMASS 合成信号上训练和测试。
- 临床方向每年都有新的小数据集，真值来自临床评分或标记动捕，部分队列不公开。
- 覆盖：CVPR 2024 一轮排除了只做头部的化身，所以 S7 中与头部化身相关的计数是下限（见第 6 节）。

**自述问题。** 被遮挡区域的补全；头显或手机上的延迟与内存；头显视野之外的肢体；单相机得到临床可用的运动学；对截肢者等人群，估计器会失效。

**与物体相关的部分。** 只有 8 行重建人或手与物体或场景；其中只有 OphNet-3D（即上表中的 Towards Dynamic 3D Reconstruction of Hand-Instrument Interaction in Ophthalmic Surgery, NeurIPS 2025）输出度量尺度的双手与 6-DoF 物体位姿。

## 3. 传感与数据的变化

**单目 RGB 视频成为默认输入。**
- S1 以视频为输入的行，按分析者一的规则为 26/99、47/128、56/117（年份对应 2024/2025/2026）；分析者二用更窄的规则得到 24/40/48 行，方向一致。
- S4 单目视频在两种关键词规则下分别为 21/27/30 和 31/37/38 行，2026 年约占三分之一；单图输入从约 15-16% 降到约 11%。
- S2 单目视频 4D HOI 的 8 行中有 7 行是 2026 年的。
- S5 的增长来自视频跟踪（在线建模加鲁棒层合计 3/11/11 行），以及手-物体 4D 重建（6/7/11 行）。
- 缺失的几何改由基础模型提供。S2 的例子：MILO 用 Hunyuan3D 和 SAM 3D Objects，HAMSt3R 和 Human3R 用 MASt3R 和 CUT3R。

**第一人称采集快速增长。**
- S1 第一人称行数为 17/34/41，S6 为 11/41/53（约 10%、20%、31%）。
- S3 第一人称占比从约 18% 升到约 30%，是近似的关键词计数。
- 头戴相机从静态的胸前相机变成带 SLAM 的头显（Aria、Quest 3、Vision Pro）。
- S4 的第一人称研究从合成的下视鱼眼装置转向真实的头显 SLAM 相机。
- 消费级头显本身成了采集设备，设备上的手部追踪结果被直接当作标签，例如 EgoDex（Vision Pro）。S1 地图在此处还列出了 HOT3D 和 SHOW3D；其中 HOT3D 与 S3、S5、S6 地图冲突，这三份地图把 HOT3D 记为光学标记动捕真值，本文按后者处理。

**RGB-D 从方法输入退到真值采集和机器人端。**
- S1 中 RGB-D 的占比约从 11% 降到 7%（分析者一；分析者二的行数为 14/17/10）。测试时用深度的估计行只有约 9 行；深度主要留在数据集主题（35 行中 11 行）和机器人迁移主题（61 行中 16 行）。
- S2 提到 RGB-D 的有 10 行；2024-2026 年的方法中，只有 OKAMI 在运行时使用 RGB-D，而且只用于机器人模仿。
- S3 中提到深度的 31 行全部不在视觉侧估计方法里。
- S4 中以深度为主要输入的方法行约 8 行。
- S6 中提到 RGB-D 的行为 14/24/20，约占当年行数的 13%、12%、12%，大致持平。2024 年，单目第三人称 RGB-D 是一次性模仿的默认配置。
- S7 中约 27 行涉及深度或 LiDAR，集中在遥操作的机器人端和数字孪生。
- 在估计类主题中，深度输入只在两处仍常见：S5 物体位姿（基于 CAD 的未见物体主题约 10-11/26 行用 RGB-D）和 S1 物体侧主题（9 行中 5 行用双目或 RGB-D）。
- 机器人侧主题也常规使用 RGB-D：S6 一次性模仿约 16 行；S6 抓取与可供性约 11 行用 RGB-D 或点云；S7 遥操作界面 10 行中 5 行用深度或 LiDAR；S5 机器人手内主题的触觉通常配一台 RGB-D 相机。
- 同期 S5 出现了一组不用深度的单目跟踪器，而且没有一行在测试时用多台 RGB-D 跟踪手持刚体。

**多视角从测试输入变成采集工具。**
- S1 多视角占比约从 13% 降到 7%（分析者一；分析者二的行数为 21/21/14）。
- S3 工作室多视角占比约从 34% 降到 13%（近似）。
- 稠密无标记多视角正在取代标记：GigaHands 用 51 个视角，ParaHome 用 70 个相机，HODome 用 76 个视角。
- S5 中测试时用多视角的只有 AlignPose、MVTracker、可变形物体相关的行和一行料箱抓取。

**可穿戴、接触与非 RGB 传感在上升；在手-物体工作中多用于真值或机器人端。**
- S4 身体 IMU 行在 2025 年达峰（10/19/7），设备从 6 个 IMU 转向 3-4 个消费设备，再加 UWB、ToF、气压计或鞋垫。
- S4 中毫米波雷达在 2025 年形成约 10 行的集群，2026 年几乎消失；LiDAR 保持平稳。
- S1 中提到 IMU、触觉、压力、力或 sEMG 的行约为 11/15/18。
- S6 中手套为 2/3/10 行，手持设备为 4/8/13 行，接触类通道为 5/24/19 行，其中单纯触觉为 3/14/14 行。
- S5 中触觉出现在机器人手内主题 22 行中的 15 行，事件相机为 2/2/4 行。
- 在 S1 和 S6 的手-物体工作中，这些传感器主要提供接触与压力的真值、被遮挡的手指姿态，或者机器人端的观测，很少作为人手估计的推理输入。S4 则不同：身体穿戴稀疏传感主题（36 行）在推理时以 IMU、UWB 和鞋垫估计全身姿态，手与手臂可穿戴主题（17 行）在推理时以 sEMG、FMG、EIT 和手套估计手与手臂的关节角。

**仿真与生成替代部分采集。**
- S1 中没有相机、只用 3D 输入的行为 18/17/8（分析者二）。
- S4 的回归器主要靠合成渲染监督。
- S6 的像素级具身转换（0/4/7 行）和生成视频，开始替代真实采集。

**表征的变化。** S7 中提到高斯的行约为 19/33/21（关键词约数）。S7 地图把它记为表征上的变化，不是传感或采集的变化。

**数据集的变化。** ARCTIC、DexYCB、HO3D 仍是手-物体评估的中心；HOT3D 迅速成为第一人称的新中心。2024-2026 年新出现的数据集朝四个方向扩展：双手长任务（OakInk2、TACO、GigaHands）、野外与第一人称（SHOW3D、Ego-Exo4D）、多人与铰接物体（HOI-M3、ParaHome、HUMOTO）、力与触觉（EgoPressure、HT-Bench、FEEL）。机器人一侧的语料则以采集小时数作为规模指标。

**真值来源。** 汇总各地图，真值有以下几类：
1. 光学标记动捕加多视角 RGB，例如 ARCTIC、OakInk2、TACO、HOT3D、OMOMO、GRAB。精度高，但标记会改变物体外观。
2. 稠密无标记多视角拟合，例如 GigaHands、ParaHome、FurElise。精度是自报的，并继承 2D 检测器的偏差；"检测器常为 HaMeR 类"一说出自分析者知识。
3. Kinect 类多视角 RGB-D 优化拟合，例如 BEHAVE、InterCap、Dense Hand-Object(HO) GraspNet with Full Grasping Taxonomy and Dynamics（HOGraspNet, ECCV 2024）、HO-Cap、OphNet-3D、ADL4D、EgoPressure。拟合误差很少报告。
4. 头显设备追踪，或 HaMeR/HaWoR 类伪标签，主要用于机器人语料。S1 地图指出，越来越多的训练数据是由该领域正在评估的同一批估计器标注的，误差没有量化。
5. 穿戴式 EM 或惯性套装，例如 EMDB、Nymeria、EgoBody3M。
6. 合成渲染，例如 ObMan、BEDLAM、AnyHand。
7. 测力台、压力垫、触觉手套与仿真，用于接触和动力学。
8. 临床评分，以及临床标记动捕。

## 4. 社区差异

**视觉会议（CVPR、ICCV、ECCV、TPAMI、IJCV）重视把状态当作输出来估计，并发布带真值的数据集。** S1 数据集主题 35 行中 CVPR 占 17 行。S1 世界坐标主题只出现在视觉会议。S2 单图人-物重建也只出现在视觉会议。S5 基于 CAD 的未见物体主题有 CVPR 11 行。人体和手的评估使用公共基准上的 MPJPE 或 Chamfer 误差；物体侧常用 ADD 类误差，这一点出自分析者知识，不是清单行。

**机器学习会议（NeurIPS、ICLR）重视生成建模、规模化与表征学习，并通过 Datasets and Benchmarks 赛道发布数据。**
- S6 无动作视频主题有 ICLR 6 行。
- S7 前馈化身主题有 ICLR 7 行。
- S2 生成主题有 NeurIPS 4 行、ICLR 3 行。
- S4 毫米波雷达集群由 NeurIPS 和 ICLR 推动。
- S1 数据集主题有 NeurIPS Datasets and Benchmarks 4 行，S4 欠代表人群主题有 3 行。

**图形学会议（SIGGRAPH、SIGGRAPH Asia）重视外观、动画、物理角色控制和动捕解算。**
- S4 多视角与光学动捕主题 20 行中，图形学占 6 行。
- S4 身体 IMU 主题中，图形学占 7 行。
- S1 运动合成主题中，图形学占 6 行。
- S3 双手表演主题中，图形学占 4 行。
- S7 实时远程呈现主题中，SIGGRAPH Asia 占 5 行。

需要注意，SIGGRAPH 2024 在清单中只是下限（7 行，低置信）；SIGGRAPH 2025 和 2026 经过交叉核对；SIGGRAPH Asia 2026 只有 1 行。

**机器人会议（ICRA、IROS、CoRL、RSS、T-RO）重视硬件、数据采集、策略和任务成功率，并且在不断加入新传感器。**

| 主题 | 机器人会议行数 / 主题总行数 |
| --- | --- |
| S6 遥操作 | 64 / 71 |
| S6 手持设备 | 42 / 57 |
| S6 一次性模仿 | 51 / 60 |
| S5 手内视触觉 | 20 / 22 |
| S5 事件相机 | 6 / 8 |
| S4 手臂可穿戴 | 11 / 17 |
| S4 人体姿态作为机器人输入 | 36 / 36 |

**同一问题上的分歧：**
1. **手-物体 3D 状态。**
   - 视觉侧把它当作输出，在 HO3D 或 ARCTIC 上用位姿误差或 CD_h 评估。
   - 机器人侧把 HaMeR、WiLoR、HaWoR 加上 6-DoF 物体跟踪器当作黑盒，只报告自有任务上的成功率。S6 指出，这些上游估计的误差很少被测量。
   - S1 和 S3 地图都写到：没有论文测量手部姿态误差如何传到下游成功率。物体位姿一侧有一个例外，见 5.2 的 W8。
2. **传感方向相反。** S5 地图明确写到，视觉侧转向单目 RGB 和基础模型几何，机器人侧反而在加传感器（触觉、事件、IMU）。
3. **人形与 HOI。**
   - S2 物理仿真人形 HOI 控制 14 行，没有一行来自机器人会议，尽管它们以人形为框架。
   - S6 人形与角色 40 行中，机器人会议占 28 行。
   - 前者在仿真角色上重现交互，后者在真实人形上做遥操作和动作跟踪。
4. **数据与真值。** 视觉侧用动捕或稠密多视角给出真值，以发布数据集为贡献。机器人侧以小时数衡量语料，标签没有验证。
5. **以机器人为动机，但不在机器人会议发表。** S1 的世界坐标、图像与视频生成、运动合成三个主题都没有机器人会议论文，S3 的第一人称主题也没有，尽管其中不少论文以机器人学习为动机。反过来，S2 中来自机器人会议的 15 行（CoRL 3、RSS 2、ICRA 3、IROS 7）几乎不做 HOI 采集或重建。
6. **物体跟踪的工程层。** 失效检测、恢复、平滑和 CPU 跟踪几乎只出现在 IROS、ICRA 和 arXiv，单帧位姿基准则在视觉会议。
7. **交汇点。** S6 的无动作视频主题会议分布最均衡：机器人 17 行、机器学习 7 行、视觉 7 行。S6 的物理仿真灵巧跟踪主题则是机器人学习主题中最偏视觉与机器学习的：机器人 7 行、视觉 5 行、机器学习 4 行、图形学 1 行。

## 5. 饱和与稀缺

### 5.1 拥挤或增量化的区域

1. **单图人体与手部网格回归。** S4 单图主题 56 行（下限，因为部分轮次排除了通用 HMR，见第 6 节）。很多论文只更换输出参数化或对齐技巧，在 3DPW 和 Human3.6M 上取得很小的 MPJPE 提升；其中约 15 行是 Human3.6M 上的 2D 到 3D 提升。S1 和 S3 的手部论文多在 FreiHAND、DexYCB、HO3D 或 InterHand2.6M 上更换骨干网络。
2. **生成式抓取与 HOI 合成。** 包括 S1 的 53 行（静态抓取 23 行加运动合成 30 行）、S2 的 33 行（下限，因为纯文本到 HOI 的生成在 S2 方法检索中被排除）和 S3 的 17 行。各论文基本是同一配方：先预测接触或关键状态，再生成姿态或运动，最后可选地做物理修正，并在同一批动捕集上评估。S1 静态抓取在当年 S1 行数中的占比从 12% 降到 6% 再到 3%。
3. **静态基准上的单帧 6D 位姿。** S5 中这类论文有 70/269 行（26%），加上无 CAD 主题为 95 行（35%）。类别级在 2026 年没有一行；ICCV 只在奇数年举办，这是一个混杂因素，但 CVPR 和 ECCV 2026 同样没有类别级的行。
4. **ARCTIC 和 HO3D 上的无模板手-物体视频重建。** 这一方向收敛到高斯泼溅加基础模型初始化，有 5 篇 HANDS 挑战报告，BIGS 和 GHOST 各自有会议版和挑战版。
5. **第一人称手轨迹预测。** 有多个潜扩散变体。
6. **稀疏 IMU 与三点追踪。** S4 中有 16 个以"Inertial Poser"命名的标题。三点追踪长期在 AMASS 合成信号上评估；S4 地图注明，这一近乎通用的 AvatarPoser 协议出自分析者知识。
7. **世界坐标单目 HMR。** 趋向 WHAM、TRAM、GVHMR 的模板。
8. **机器人侧。**
   - 遥操作接口 71 行，加上一系列 UMI 衍生设备。
   - 第一人称协同训练配方，以及 2026 年的 arXiv 语料，报告的是小时数，而不是标签精度。
   - 潜在动作预训练，都在 CALVIN、LIBERO、SIMPLER 上评估。
   - 人形重定向，以及一系列 mimic 变体。
   - 人到机器人的感知流水线已趋于模板化，而且没有共享基准。
9. **化身。** 单目高斯化身 35 行，在 ZJU-MoCap 或 PeopleSnapshot 上取得很小的图像指标提升；前馈单图化身收敛到同一配方。只做头部的化身在 CVPR 2024 一轮中被排除，所以 S7 的头部化身计数是下限。

### 5.2 清单中少见或缺席的内容

下面各项只说明清单中少见，不说明它重要，也不说明没有人做过。清单对 ICRA 2024 和 T-RO 的覆盖不完整，IROS 2026 只有 1 行，CoRL 2026 只有 3 行。按分析者的判断（不是清单行），这类工作较可能发表在机器人会议和期刊上，所以部分缺席可能来自覆盖。稀缺也可能意味着社区把它当作旧范式；本步无法区分这两种情况，留给下一步。

- **W1：测试时以深度为输入的手加物体联合估计，尤其是双手。** 证据：S1 只有约 9 行估计方法；S2 只有 OKAMI；S3 视觉侧为零；S4 约 8 行；S7 只有 4 行用于人体重建；S5 手-物体主题有 3 行用单台深度或 RGB-D（HOIC、PickScan、透明物体深度修复）。S2 地图指出，BEHAVE 2022 的单目 RGB-D 跟踪器是清单中最后一个这类度量 HOI 跟踪器。只跟踪物体的 RGB-D 跟踪器是存在的：S5 在线建模跟踪主题 14 行中约 8 行用 RGB-D 视频（FoundationPose 一系），这也是在手持或夹持基准（HO3D、YCBInEOAT）上评估的主题。
- **W2：在线的标定多视角 RGB-D 系统本身作为方法。** 这类系统只以离线标注装置的形式出现（HO-Cap、HOGraspNet、InterCap、ADL4D、OphNet-3D）。S2 指出，多深度相机之间的标定、同步和遮挡处理在 2024-2026 年没有被当作研究问题。S6 地图指出，机器人学习论文不验证采集精度。
- **W3：双手之间的物体传递，以及手-手-物体近距离接触。** S3 中自我交接只有一篇分类学论文。S5 中没有方法在手到手的传递上评估。HANDS23 把两手与物体的近距离接触列为未解决的失败模式。S6 指出，双手传递中重度遮挡下的手内物体位姿基本缺席。
- **W4：固定世界坐标下的度量精度，以及与独立参考的比对。** 多数论文报告根相对 MPJPE 或手相对 Chamfer，视频物体重建只到尺度不定为止。S4 几乎没有按可见度划分的逐关节误差。S7 的化身与远程呈现主题只用图像指标；S7 的生物力学与临床主题则使用动捕参考。
- **W5：长时因果跟踪及其漂移、恢复和延迟。** S1 只有 ComPose、MGS-Track、POGS。S3 只有 QORT-Former 和 WiLoR 强调实时。S2 只有 THO 和 Human3R。S5 没有共同的评估协议。
- **W6：真值本身的误差，以及用标记来验证学习型跟踪器。** S1 中 FLiPo、FSGlove、SHOWMe 是例外。S5 的 6 行标记论文没有一行与学习型跟踪器比较。S2 中没有出现 ArUco 或 AprilTag。S6 的语料标签没有与动捕比对。
- **W7：随时间传递的不确定性与失效检测。** S5 的 6 行不确定性论文都是单帧的；在这 6 行之外，UA-Pose、UniTac2Pose 和 Temporally Consistent Object 6D Pose 三行做了随时间的传递。S4 约 5 行，S7 只有 3-4 行。
- **W8：上游手部姿态与手-物体估计误差对下游机器人成功率的影响。** S1 和 S3 中没有论文测量，S6 很少测量。物体位姿一侧有一个例外：第 836 行 Benchmarking the Effects of Object Pose Estimation and Reconstruction on Robotic Grasping Success（ICRA 2026，S5 刚体数据集主题）；S5 地图也把位姿误差与抓取成功率之间的关系列为自述问题。
- **W9：系统层面的评估变量。** 以下变量在清单行中少见或没有出现：
  - 标定误差和跨相机时间同步（S4 地图：几乎没有行报告）；
  - 消费级深度噪声，即 S4 列出的红外干扰、肢体边缘飞点和近距离空洞（S5 只有 DTTDNet 一行涉及，S4 中没有出现）；
  - 把采集到的动作在游戏引擎或数字孪生中回放，作为评估目标（S4 中没有出现）。
- **W10：人体穿戴传感与深度融合用于手-物体跟踪，以及可穿戴设备用于物体位姿。** 在 S1 和 S4 中，人体穿戴的 IMU、触觉或 sEMG 与深度相机融合来跟踪手-物体的组合都没有出现。S5 中相近的只有 Dynamic Reconstruction of Hand-Object Interaction with Distributed Force-aware Contact Representation（ViTaM-D, ICCV 2025）和 IMU-HOI。机器人一侧的 RGB-D 加触觉融合在 S5 中很常见：机器人手内主题 22 行中 15 行用触觉，通常配一台 RGB-D 相机。DynamicPose（IROS 2025，第 1285 行）融合 RGB-D 与 IMU 做物体跟踪。EgoEMG（第 1180 行）同时记录外部 RGB-D、EMG 与 IMU，但它只是数据集。
- **W11：上肢与手的耦合运动学，以及坐姿桌面的上半身捕捉。** S1 只有 EgoForce 和 Enhancing Hands in 3D Whole-Body Pose Estimation with Conditional Hands Modulator（Hand4Whole++, CVPR 2026）。S4 在 VR 三点追踪之外没有这类工作，被手持物体遮挡的手臂也很少被单独研究。
- **W12：难处理的物体与场景。**
  - 可变形或铰接的手持物体：S5 只有 ArtHOI 和 ViTaM-D。
  - 透明或反光物体：S5 有 3 行（交接深度修复、SilRef、双目交接），S1 有 2 行。
  - 外科与工业场景：S3 各只有一行。
  - 临床上肢的真实物体操作：S7 只有少数 arXiv 和 ICRA 论文。
- **W13：评估实践本身。** 包括：
  - 跨数据集泛化与负面结果（S1 只有一篇 CVPR 2025 的合成到真实差距分析）；
  - 共享的真实世界人到机器人基准；
  - 重复试验的方差；
  - 估计论文中的物理有效性指标；
  - 遮挡感知指标（S5 只有 WALDO 和 TAPVid-3D）。

## 6. 方法说明

**清单的构建。** 清单从各会议的录用论文列表构建，共 1563 篇。每行包含标题、会议、年份、类型、传感方式、一句话贡献和数据集字段，这些字段都来自摘要层面。

**子领域地图的产生。** 每篇论文可带多个子领域标签，七份地图的行数合计 2168。每个子领域由两名分析者分别从问题视角和方法视角分类，再由一名调和者读该子领域的行，把每行分到唯一一个主题。有两个例外：S6 的问题视角分配没有保存，无法逐行核对；S5 的合并以分析者 B 的分配为起点。地图中的主题计数和分年数对这次分配是精确的。传感、数据集与会议的分项数多来自关键词或子串匹配，地图标注为约数的，本文同样写"约"。

**本文的做法。** 本文没有重新阅读或分类任何行，所有数字都直接取自地图。主题名称和子领域名称的中文是本文的概括。跨子领域的同名主题边界不完全一致，各地图注释记录了调和时的重新切分。

**覆盖范围（按会议与年份）。**
- 在筛选范围内接近完整：CVPR、ICCV、ECCV 2024-2025，NeurIPS 2024-2025，ICLR，CoRL 2024，以及 RSS（2024 高置信，2026 较高置信）。ICRA 2025 置信度高；ICRA 2026 来自 2,951 条的完整日程；IROS 2024 和 2025 也较完整。
- 中等：CVPR 2026（官方列表被拦截，几篇未确认的论文没有收入）；ICRA 2024；CoRL 2025 中 PMLR v305 以外的论文（CoRL 2025 只覆盖了 PMLR v305）。
- 只能视为下限：SIGGRAPH 2024（低置信，7 行；SIGGRAPH 2025 和 2026 经过交叉核对）；T-RO（估计 2024 年有 25-40% 未核查）；IJCV；TPAMI（约 2025 年 9 月至 2026 年 6 月首次在线发表的论文可能缺失）。
- 2026 年基本缺席：NeurIPS 2026 为 0 行，IROS 2026 为 1 行，CoRL 2026 为 3 行，SIGGRAPH Asia 2026 为 1 行。ICCV 只在奇数年举办。
- 主题筛选规则在各会议轮次和各主题检索之间并不一致。CVPR 2024 一轮排除了通用 3D 人体姿态与 HMR 骨干（例如 TokenHMR、AiOS）、HOI 检测、文本到动作、不含采集的人-场景生成，以及只做头部的化身。ECCV 2024 一轮排除了通用单目 HMR，除非论文针对遮挡或世界坐标。S2 方法检索排除了纯文本到 HOI 的生成和物理控制。S6 数据集检索有意排除了方法论文。TokenHMR 仍出现在 S4，是因为后来的一次检索把它加了进来。因此 S4 单图主题（56 行）、S2 生成主题（33 行）和 S7 头部化身的计数都是下限，这些主题的年度趋势可能反映的是筛选规则，而不是领域本身。
- 构建过程受 200 次检索调用的预算限制，并且部分学术网站被代理拦截。
- 清单还收入了检索中碰到的非目标会议论文、研讨会论文和 arXiv 预印本。例如 S1 有 48 行 arXiv、15 行研讨会或挑战报告；S6 的 arXiv 行从 3 行增至 26 行再到 51 行。

**如何阅读这些计数。**
1. 2026 年的下降不能直接解读为衰退，应参照占比。例如 S1 静态抓取的占比下降是真实的，而数据集主题的下降有一部分来自覆盖不足。
2. 以 arXiv 为主的上升主题（S6 第一人称语料、数据引擎、像素转换；S1 视频重建与世界坐标）有一部分是清单构建方式带来的。
3. 关于机器人会议和图形学会议"很少做某事"的判断，涉及 ICRA 2024、T-RO、SIGGRAPH 2024 以及 2026 年的 IROS、CoRL 时，可信度低于关于 CVPR 2024-2025 的同类判断。
4. 数据集字段的缺失率很高：S1 约 30%，S2 为 53/149，S4 约 199/439，S5 为 122/269。因此数据集排名只是软排名。
5. 清单中有重复行，例如 OakInk2、PACE、InterCap、VideoMimic、Codec Avatar Studio、Muscles in Time。也有部分行只有标题信息，这些行的归类置信度较低。

**依据分析者知识而非清单行的陈述。** 本文转述这些陈述时已在正文标注，包括：
- EMDB 是世界坐标方向的事实标准；
- 三点追踪长期以 AMASS 合成信号为评估协议（AvatarPoser 协议）；
- HO3D 与 YCBInEOAT 规模小；
- 物体侧常用 ADD 类误差；
- 稠密多视角真值中的 2D 检测器常为 HaMeR 类；
- 化身方向以 PSNR、SSIM、LPIPS 为评估惯例；
- 5.2 中所列的工作较可能发表在机器人会议和期刊上。

NeurIPS 2026 不在清单中这一点，已改为按行数核实（0 行），不再依据分析者知识。