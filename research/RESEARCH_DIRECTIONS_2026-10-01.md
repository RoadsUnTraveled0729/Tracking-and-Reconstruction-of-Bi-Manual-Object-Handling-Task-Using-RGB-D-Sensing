<!-- Produced 2026-10-01 by a multi-agent workflow (8 lens-specific topic generators,
one merge step, 3 adversarial skeptics per topic with web literature checks, one
synthesis, one critic pass, one revision; 69 agents). The master session verified
the thesis numbers quoted in Section 1 against writing/v9/Thesis_V9.pdf (Tables
7.7 and 7.9, the 7.0/2.7/6.3 cm grip-offset spread, the 25/35 cm hysteresis, the
15/25 degree twist rule, the 41/40 marker-loss frames, Chapter 8 frames 7-24) and
spot-checked four key citations ([1] ComPose, [2] IMU-HOI CVPR 2026, [4] AKC,
[45] MANIKIN ECCV 2024) by web search on 2026-10-01. The per-topic verdicts are in
RESEARCH_DIRECTIONS_2026-10-01_verdicts.md. Skeptics were instructed to refute by
default when uncertain, so the absolute scores are low by construction; read them
as a ranking, not as a probability of acceptance. -->

**说明（2026-10-02）**：本备忘录以论文为出发点。作者随后要求改为领域优先：先看顶会在做什么、它们自述的痛点是什么，再决定方向。那项研究的结论在 FIELD_MAP_2026-10-02.md，其第 6 节说明了本备忘录的哪些方向与领域痛点重合、哪些不重合。本文保留为记录。

# 研究方向备忘录：从《Tracking and Reconstruction of Bi-Manual Object Handling Task Using RGB-D Sensing》出发

日期：2026-10-01。读者：论文作者。

## 1. 论文的核心资产

论文里有四类东西可以拿来做研究，而且带有这篇论文自己的特色。

第一，一个度量世界坐标系。物体的 6-DoF 位姿由 ArUco 分支测得，不依赖人体检测器。有了这一点，"用物体反推被遮挡的手臂"可以写成一个严格的估计问题，不再只是启发式技巧。

第二，object-conditioned recovery 本身，以及论文如实记下的失败模式：
- 握持偏移只用了平移部分，物体朝向被丢掉了。
- 握持本身不刚性。论文 5.1 节之后写道，在 loop 录制里，手是包裹着立方体的，并且会在立方体上移动。左手握持期间，逐帧偏移观测在三个标记轴上的标准差为 7.0 / 2.7 / 6.3 cm。这是"非刚性握持"这一失败模式的证据。
- 估计器有滞后，这是另一种失败模式。偏移跟随握持变化时有增益决定的滞后，失效时冻结下来的偏移仍带着最后几帧干净数据的值，也就是"偏移过期"。论文把非刚性握持和估计器滞后列为两种不同的条件，二者都会让物体提供的约束本身出错。
- 自然遮挡下的结果是混合的（表 7.9）：
  - 右腕只有 4 帧，物体辅助的中位误差为 5.2 cm，对比纯求解 11.4 cm、hold-last 17.6 cm；
  - 左腕 16 帧，物体辅助反而更差，13.1 cm，对比纯求解 12.3 cm、hold-last 12.7 cm。
- 悬垂手臂的扭转、沿光轴方向的肘部深度都不可观测。
- 桌面挡住髋部时，两侧髋部一起偏移，所有检测器都发现不了。

这些都可以直接拿来写问题陈述。

第三，评测工具：
- measured / held / constrained 三种诚实标签；
- v3 的 S 型合成遮挡场景；
- teleport 预算和 false_measured 指标；
- v3 grade 脚本；
- Unity 传感器视角孪生。

第四，工程底座：
- 单位四元数 swing-twist 核心，与 v1 吻合到 1e-9 度；
- 切空间 Kalman 平滑器；
- RTMPose ONNX，p99 低于 11 ms；
- 约 30 fps 的因果合并链。

不能当作研究证据的部分要说清楚：
- 只有一名受试者、28 段录制，没有动捕，也没有用实时相机验证过。
- 人工腕部标注很少。在干净帧上，标注与检测点的中位距离就有 2.1-4.5 cm。
- 手臂表示只有 4 个自由度，腕部没有朝向，审稿人会觉得不标准。
- 论文里的数字只能算试点数据。

有几处"证据"容易被误用，需要更正：
- V3 D-017 中 0.818 对 0.789 的置信度差，来自一个已被否决的弱标签（右腕 898 帧中有 889 帧被标记）。它不能说明遮挡时检测器置信度更高。
- 第 8 章 12 cm 的因果-离线分歧只发生过一次。原因是两套手写门控规则在同一窗口里触发的帧不同，并不是因果估计本身的现象。
- 合成遮挡下"中位 1.7 cm，hold-last 一秒内漂到 21 cm"不是论文正文的结果。它来自 eval 轨道（README 中的 E-014，eval/reports/r5_object_conditioned_recovery.md），协议是人为遮蔽运动中的测量段（R5 masked outages），再与被遮蔽前的数据比较，真值的确切定义以该报告为准。
- 论文自己的合成评测（表 7.7）以未遮蔽的模型重建为参照，不是以真值为参照。在低、中、高三个运动窗口上（每窗 n=45）：
  - 物体辅助的腕部中位误差为 1.2 / 1.2 / 1.9 cm；
  - hold-last 为 0.7 / 1.2 / 1.5 cm；
  - direction memory 为 0.4 / 1.9 / 2.5 cm。

  论文的结论是：结果"支持依赖窗口的比较，而不是一个通用的恢复方法排名"。也就是说，基础方法的证据比"已经证明有效"弱得多。

## 2. 推荐方向

19 个候选题目都经过新颖性、可行性、投稿去向三位怀疑者评审（满分 10）。按原样，没有一个通过，单项平均分在 3.0 到 4.5 之间。共同的否决理由有三条：
- 机制大多是已有方法的组合；
- 单受试者、无动捕的数据撑不起结论；
- 一篇论文里塞了太多贡献。

下面 5 个方向，是把同一研究线上的题目合并，再按评审的收窄建议重构得到的。方向编号沿用初稿，推荐次序以下表为准。

**排序标准**（按权重从高到低）：
1. 是否用到论文独有的资产，即独立测得的物体位姿和度量世界坐标系；
2. 能否用几天到几周、低成本的决定性试点尽早判定成败；
3. 与你"顶刊顶会"目标的距离；
4. 怀疑者评分。

| 推荐次序 | 方向 | 组成题目的平均分（新颖性 / 可行性 / 投稿去向三项均值） | 未被否决的评审视角 |
| --- | --- | --- | --- |
| 1 | 方向一：物体作为被遮挡前臂的传感器 | I01 4.0；I05 4.0；I06 3.0 | 0/3（三个题目都被三个视角否决） |
| 2 | 方向二：可观测性、可检测性与弃权 | I07 4.5；I04 3.8 | I07 的可行性视角未被否决（6/10，全场最高）；I04 材料未记录 |
| 3 | 方向四：深度归属与非模态深度 | I02 4.2 | 可行性视角未被否决（5.5/10） |
| 4 | 方向三：公开数据上的诚实性评测协议 | I10 3.7；I03 3.7；I09 3.7；I11 3.2；I08 3.0 | 0（每个视角都否决） |
| 5 | 方向五：康复评估测量仪器 | I16 3.3；I17 3.7；I18 3.3 | 材料未逐项记录 |

方向一的评分最弱，却排在第一，需要说明理由。它是唯一直接建立在论文独有资产上的方向。收窄之后，它针对的正是三个被否决的理由：数据、范围和机制新颖性。而且它的决定性试点（第 3 节任务 1 的解析可辨识性检查）只要几天。如果解析检查不成立，第一篇就改为方向二（可观测性那部分本来就是 I07），这也是评分和可行性最好的选择。如果你更看重评审分数而不是论文特色，应当直接把方向二放在第一位。方向四排在方向三之前，是因为它的评分和可行性都更好，试点也更小。

旁支选项：I14 和 I19 的平均分都是 3.8，可行性视角都未被否决，而且都不需要新硬件，可以与主线并行（见第 4 节）。

### 关于投稿去向

坦白讲，按现有设备和数据，现实的第一站是 IEEE RA-L、ICRA、IROS、3DV 或 TNSRE。这些在各自领域是顶刊顶会，但不是你说的 CVPR、ICCV、CoRL 主会。有可能走到那一级的路径只有三条：
- 方向一：需要做到无标记物体、5 名以上受试者，在公开数据上有结果，并有下文列出的强基线，才能冲 CVPR 或 ICCV；再加上下游机器人任务结果，才能冲 CoRL。
- 方向三：如果名次反转被多数据集证实，可以投 NeurIPS Datasets and Benchmarks。
- 方向四：只有在增益很大时才考虑 CVPR。

其余方向没有通往这几个主会的现实路径。

### 关于文献核实

本轮网络检索额度已经用完。复核改用 GitHub 上的 arXiv 镜像和论文列表仓库，核对了大部分 2024-2026 年的条目，结果见第 5 节。但"是否已有人做过同样的事"这一新颖性问题还没有系统检索，正式投入之前必须补做。

### 方向一：把被握持的物体当作被遮挡前臂的传感器（合并 I01、I05、I06，吸收 I07 的可辨识性分析）

- **研究方向**：在单视角度量 RGB-D 下做因果的手臂恢复。用独立测得的物体位姿，通过全 SE(3) 握持闭合约束，反推被遮挡的腕位置、前臂旋前旋后和腕部朝向；握持模式作为离散隐变量来推断。主张限定在"握持手本身被遮挡、物体位姿仍可测"的帧上，并报告这类帧所占的比例。

- **为什么值得做**：手-物交互重建正在从离线逐序列优化走向因果、抗遮挡的跟踪。已核实的近作要么方向相反，要么传感条件不同：
  - ComPose [1] 研究的是什么时候该用手的线索来跟踪物体；
  - IMU-HOI [2] 依赖穿戴式 IMU；
  - HOLD [5] 和 BIGS [6] 都是离线优化。

  基础证据要如实说明。eval 轨道在 R5 人为遮蔽协议下给出了中位 1.7 cm 对 hold-last 一秒内 21 cm（E-014）。但论文表 7.7 显示，排名随窗口变化；表 7.9 显示，左臂上物体辅助更差（13.1 对 12.3 cm，n=16），只在右腕 4 帧上更好。所以起点只是"有时有效的平移版本"，并没有被证明普遍有效。

  平移版本丢掉了物体朝向，而在手被遮挡时，物体朝向是腕部朝向的重要线索。手部可见时，手部关键点和手部网格（RTMPose-wholebody、MediaPipe Hands、WiLoR、HaMeR）本身就能测量手的朝向，所以物体并不是唯一的扭转线索。评审认为因子图机制是标准做法，因此卖点必须是一个可辨识性结论，加上在强基线之上的实测增益。

- **手臂与腕部模型**（必须在论文里明确写出）：肩 3 自由度、肘屈曲 1、前臂旋前旋后 1、腕屈伸和尺桡偏 2，共 7 自由度，是一条冗余链。直接推论有两条：
  - 手的 6-DoF 位姿已知时，肘外摆角（swivel，arm angle）正好是剩下的那个零空间自由度。这是经典的冗余臂自运动结论。所以全 SE(3) 闭合本身不能让外摆角可观测。
  - 肘伸直时，肩内旋和前臂旋前旋后绕同一根轴转动，闭合只能约束二者之和。这正是推动本研究的"悬垂手臂"情形。

  初稿只在论文 4 自由度手臂上加了一个前臂轴向自由度，相当于默认腕部刚性。这样做会让闭合过度约束手臂链，人为制造出可观测性，真实的腕屈伸会被吸收成扭转误差。评审一眼就会看出来，所以必须改用 7 自由度模型。"末端朝向确定外摆角"只对 6 自由度手臂成立。

- **扭转的定义**：估计器和参照都要分别报告两个量：肱骨内外旋（肩内旋）和桡尺旋前旋后。肘伸直时，再额外报告二者之和。不能把两者混称为"扭转"。

- **具体研究问题**：
  1. 在 7 自由度模型下：已知手的 SE(3)（来自物体闭合）、腕位置，以及可见或部分可见的肘、肩关键点时，旋前旋后和腕部两个角是否可辨识？在哪些构型下退化（例如肘伸直）？外摆角在只有关节限位和舒适度先验时，能恢复到什么程度？能否胜过 MANIKIN [45] 式的学习式外摆角回归？
  2. 加入四状态握持模式隐变量（free / L / R / LR），并在每次新握持时重新估计握持变换，能否把交接后 0-2 s 的腕部误差相对论文的常数偏移基线降低 30% 以上？闭合残差的 NIS 能否在腕误差超过 5 cm 之前，检测出过期或滑动的握持？

- **最接近的已有工作与差异**：
  - ComPose [1]：根据手部线索决定何时信任手，基于 RGB 视频做 6-DoF 物体跟踪，没有手臂链，也没有交接模式。本方向是从物体到手臂的反向，而且在度量深度中做。
  - IMU-HOI [2]（CVPR 2026）：6 个身体 IMU 加 1 个物体 IMU，把接触作为概率信号来融合，依赖穿戴式 IMU。据摘要未见滑动和换握模式，这一点未完全确认。
  - VisTracker [3]（CVPR 2023）：用人体离线补全被遮挡的物体，方向相反，也不用度量深度。
  - AKC [4]：用恒定臂长几何约束修正被遮挡手臂的深度，不用物体，也不建模握持。
  - MANIKIN [45]（ECCV 2024）：学习式生物力学逆运动学，会预测外摆角，是外摆角主张最直接的基线。

- **可能的解决方法**：
  - **状态**：
    - 躯干 SE(3)；
    - 两条 7 自由度手臂链（v3 swing-twist 核心扩展出旋前旋后和两个腕部角）；
    - 物体 SE(3)；
    - 两个握持变换 G_L、G_R；
    - 离散的握持模式。
  - **估计器**：GTSAM 固定滞后平滑器，滞后 2-3 帧（与论文的因果合并器一致），15 帧作为消融。每帧约有 20 ms 的 CPU 预算。
  - **因子**：
    - RTMPose 关键点的重投影和深度残差，用 Cauchy 鲁棒核；
    - 手部可见时加入手部关键点，作为直接的手部朝向测量；
    - 个体骨长先验；
    - 关节限位和外摆角舒适度先验；
    - 物体位姿观测；
    - 只在当前模式下激活的 6-DoF 闭合因子 Log(T_obj^-1 * FK_hand(q) * G)。

    只保留平移的闭合等价于论文的方法，作为关键消融。
  - **握持动力学**：非刚性握持和估计器滞后分开处理。
    - G 的过程噪声根据实测的握持偏移散布来设定（loop 录制左手握持时，三轴标准差为 7.0 / 2.7 / 6.3 cm），不取"很紧的随机游走"。另一种做法是把包裹式握持建成滑动约束：只约束手到物体表面的法向距离和部分朝向。
    - 每次新握持开始时，从手和物体同时可见的帧重新初始化 G，这一步针对滞后和过期。
    - 预先登记：如果滑动模式在大部分握持帧中处于激活状态（比例阈值在试录后、正式录制前写定），主结果改为报告滑动约束版本，全刚性闭合降为消融。
  - **模式推断**：四状态 HMM，发射量用手-物距离、速度一致性和闭合残差。论文的 25/35 cm 滞回状态机作为基线。在手可见的帧上，对闭合残差做 NIS 加 CUSUM，用来检测过期握持。
  - **理论部分**（借用 I07，分两步）：
    - 第一步是解析可辨识性。对外摆角、肩内旋、旋前旋后、腕部两个角，写出堆叠雅可比，在下面几种测量组合下求秩，并找出退化构型：
      - 已知手的位姿；
      - 已知腕位置；
      - 已知肘关键点或部分关键点。

      这一步只需几天。
    - 第二步只在解析结果支持时进行：在 Unity 中、在 D435 噪声模型下，做逐自由度的 Fisher 信息扫描，比较无物体、仅平移闭合、全 SE(3) 闭合三种设定。
  - **与论文代码的关系**：论文的 object-conditioned recovery 加两连杆 IK，是"固定模式、冻结平移 G"的特例，同时用作初值和基线。
  - **第一篇论文里删掉的内容**：扳手可行性 QP、学习式握持动力学、共形风险控制、多视角 iSAM2。评审认为这些都会稀释主张。

- **实验与评估**：
  - **真值**：真值是这个方向最大的短板，需要新增以下装置。
    - 第二台 D435，作为参照视角。
    - 前臂远端和上臂各一个袖带，只对参照相机可见。袖带只能作为位置的廉价参照。它作为轴向旋转参照是否可信，必须先验证：前臂袖带会混入旋前旋后，上臂袖带有软组织伪影，二者误差都在轴向旋转上最大，正好是要测的量。文献中皮肤固定的上臂轴向旋转伪影常被报告为较大，可能与 10 度判据同量级（具体量级需查文献核实）。
    - 验证办法有两种：借用一天光学动捕，或用刚性夹板加触诊肱骨上髁作为参照，报告袖带的轴向误差。如果这个误差大于目标效应，扭转主张就只在 ARCTIC 和合成数据上做，袖带只用于位置。
    - 六面都贴标记的立方体。loop 录制中丢失标记的 41 帧里，有 40 帧恰好落在双手交接段。
  - **最小可行实验**：
    - 3 名受试者，每人约 20 次左右手交接、10 次换握、10 次人为滑动，另外加入刻意遮挡和手臂沿光轴的姿态。
    - 每人的次数由功效分析确定。分析单位是事件（交接、遮挡、滑动），不是帧，因为同一事件内的帧高度相关。按受试者聚类做 bootstrap 或混合效应模型。所需事件数用作者本人试录得到的方差来估算，用于检验预先登记的 10 度和 30% 效应。
    - 只有 3 人时，结论限定为受试者内效应。
  - **比较的方法**：
    - (a) 论文的常数偏移加两连杆 IK；
    - (b) 仅平移闭合的平滑器；
    - (c) 全 SE(3) 闭合；
    - (d) (c) 加 HMM；
    - (e) hold-last；
    - (f) 切空间 Kalman；
    - (g) 由手部关键点或手部网格测手部朝向：逐帧 WiLoR 或 HaMeR 加 Kalman 平滑，以及 RTMPose-wholebody 手部关键点。这是投稿评审点名的主要基线；
    - (h) MANIKIN [45] 式外摆角回归；
    - (i) 一个全身接触耦合的手-物交互拟合基线（VisTracker [3]、CHORE、BEHAVE [29] 式拟合，双手都加接触）；
    - (j) 一个视频人体网格恢复基线（WHAM [30] 或 GVHMR）；
    - 另加 AKC 和 ComPose 式单向变体。
  - **指标**：
    - 遮挡帧上和交接后 0-2 s 的腕、肘位置误差（cm）；
    - 旋前旋后、肩内旋、腕部角和外摆角误差（度），手部被遮挡的帧和手部可见的帧分开报告；
    - 模式 F1 和交接时刻误差；
    - 过期握持的检测延迟和每分钟误报次数；
    - p99 延迟。
  - **公开数据**：
    - ARCTIC [9] 有动捕身体和物体真值，可以检验旋前旋后的主张，取一个子集即可。它只有 RGB，没有传感器深度。主协议从真值网格渲染深度，并叠加 D435 噪声模型；单目度量深度作为消融。
    - OakInk2 [27]、GRAB 和 FullBodyManip（OMOMO [7]）也有身体和物体 6-DoF 真值，只是真实图像较少或没有图像。可以用 z-buffer 构造单视角遮挡，得到真值精确的合成划分。
    - HO-Cap [10] 没有身体和手臂真值，只用来统计"手不可见而物体可见"的帧比例。

- **下游任务**（从 RA-L 走向 CoRL 的条件）：设计一个有实测任务结果的用例。例如用恢复出的双臂轨迹做示教采集或遥操作，再比较有无诚实标签和握持闭合时的重定向误差或任务成功率。前提是能用到机械臂（如 I12 提到的 SO-101）。这部分放在第二篇，第一篇不承诺。

- **目标会议或期刊**：首选 IEEE RA-L（附 ICRA 或 IROS 宣讲），备选 IROS 或 3DV。冲 ICCV 或 CVPR 的条件是：做到无标记物体（FoundationPose [11]）、5 名以上受试者、在公开数据上有结果，并胜过基线 (g) 到 (j)。再加上下游机器人任务结果，才能投 CoRL。

- **风险与对策**：
  - 解析检查显示主张不成立：立刻转到方向二，不买硬件。
  - 被看成"拼装得很好的因子图"：用可辨识性分析加消融，证明增益来自闭合因子和模式隐变量。
  - 场景太窄：先在 28 段已有录制和公开数据上统计"握持手被遮挡而物体可测"的出现频率。这一步不需要新硬件，放在第一季度之前完成。
  - 只胜过自己的弱基线：基线 (g) 到 (j) 是必做项。
  - ComPose 作者可能先做反向：尽快完成最小可行实验。
  - 包裹式握持可能让滑动模式一直开着：录制时同时包含捏取和包裹两类握持，并按上面预先登记的规则处理。
  - HO-Cap 的物体真值部分由 FoundationPose 生成：如实披露，自录数据的物体真值以标记为准。
  - 数据伦理：受试者知情同意书必须明确是否允许公开可识别的 RGB-D，不允许时只发布骨架和物体位姿。ARCTIC、BEHAVE、InterCap、OakInk2 多为非商业许可，并需要注册，以各自条款为准，这限制了可以发布的内容。

- **后续扩展**：I05 的"物体对隐藏手臂的信息增益"分析，可以作为这条线上的第二篇。在 OakInk2 [27]、ARCTIC 和 GRAB 上做 z-buffer 单视角遮挡，按握持类型、握持时长、遮挡时长和手臂与光轴的夹角分别报告。生成式补全只有在肘部误差上比"IK 加学习式外摆角回归"好 1.5 倍以上时，才值得做。

- **Skeptic scores（新颖性 / 可行性 / 投稿去向）**：I01 4 / 3.5 / 4.5；I05 4 / 4 / 4；I06 3 / 3 / 3。

### 方向二：单视角 RGB-D 运动学跟踪的可观测性、故障可检测性与弃权（合并 I07、I04）

- **研究方向**：在传感器噪声模型下，逐自由度判断"这一帧这个关节能不能被看到"；只沿不可观测的方向施加先验；不可观测期间保留多个假设，或者直接弃权。同时分析两件事：哪些相关故障在只用人体内部一致性检查时根本无法检测，哪些场景参照能让它们重新可检测。

- **为什么值得做**：论文现在用手设阈值处理这些情况：肘屈曲低于 15 度时冻结扭转、高于 25 度时释放；伸展到 98% 臂长时启用方向记忆。退化感知估计在 LiDAR 配准里已经很成熟（X-ICP [13]、Informed, Constrained, Aligned [14]）。但还没有人回答：学习式不确定性模型（HuManiFlow [15]、HuProSO3 [16]）是否恰好在低可观测区间过度自信。I07 的可行性得分是全场最高（6/10）。不过单目关节链的奇异性分析已有经典工作（[43][44]，未核实），所以贡献必须落在实证发现和传感器噪声模型上。如果方向一的解析检查不成立，这个方向就成为第一篇。

- **具体研究问题**：
  1. 用实测的 D435 量程相关噪声计算的逐自由度可观测性分数，能否提前预测扭转误差超过 10 度、肘深度误差超过 3 cm 的帧？AUROC 能否明显高于检测器置信度和论文的手设规则？
  2. 共模髋部偏移、肘落到手上、深度取自错误表面，这几类故障中哪些落在人体内部不变量的零空间里？加入桌面平面、重力和握持物体约束之后，每类故障的最小可检测偏差是多少？

- **最接近的已有工作与差异**：
  - X-ICP [13] 和 Informed, Constrained, Aligned [14]：做的是刚体扫描匹配。后者比较了 TSVD、不等式约束和 Tikhonov 正则化。本方向把思路迁移到带深度噪声的关节链上。
  - HuManiFlow [15] 和 HuProSO3 [16]：能定性地表现扭转的歧义，但不做逐自由度的决策，也不是因果跟踪器。
  - Protection Levels for Vision-Based Pose Estimation [17]：针对刚体 PnP 关键点流程的 6-DoF 位姿（据第三方信息发表于航电会议 DASC 2026），不涉及关节链上的相关故障。
  - Detecting Pose Estimation Failures via Keypoint Self-Consistency [18]：据摘要是刚体位姿的失效检测，细节未完全确认。

- **可能的解决方法**：
  - **噪声模型**：用一天时间，以平板和桌面拟合 D435 噪声模型（深度标准差随距离平方增长，外加边缘飞点）。像素噪声从论文中干净窗口的残差估计。
  - **可观测性分数**：在扩展到 7 自由度的 v3 四元数核心上求测量雅可比，在短因果窗口内计算 I(q) = J^T Sigma^-1 J，特征分解后投影到外摆角、肩内旋、旋前旋后、肘屈曲各自由度，再用卡方检验定阈值。
  - **估计器**：只沿低特征值方向注入先验，软投影和硬锁定两种方式都试。先验来源包括关节限位、方向记忆和方向一的握持闭合。扭转用 K 个假设的高斯和滤波。
  - **离群点**：Fisher 信息在错误的测量处同样"自信"，所以必须加鲁棒核，处理落到错误身体部位的关键点。
  - **故障部分**：对手臂链、论文的六个检测器和新的场景不变量计算奇偶空间，给出每种故障的最小可检测偏差。然后把这些故障注入真实的 R4-R7 数据流，得到精确的故障标签。
  - **Unity 扫描**：Unity 孪生在手臂构型与相机位姿的网格上给出精确真值，副产品是相机摆放建议。

- **实验与评估**：
  - **最小可行实验**（约 8-10 周，不需要新硬件）：
    - 在 Unity 扫描数据上，比较三种失效预测信号的 AUROC：可观测性分数、检测器置信度、论文的 15/25 度规则；
    - 按可观测性分箱，比较四种估计器：论文的保持规则、各向同性 Tikhonov、投影先验、投影先验加多假设；
    - 检查分数是否在已知失败窗口触发，例如第 8 章第 7-24 帧和手臂沿光轴的窗口。
  - **故障部分**：报告固定误报率下的漏检率，以及"只用人体不变量"与"加场景不变量"的对比。
  - **真实验证**：用第二台 D435 三角化 2-3 名受试者的关节位置。风险水平只报告 1e-1 到 1e-2，不声称 1e-3。轴向旋转的真实验证受方向一所述袖带问题的限制。

- **目标会议或期刊**：首选 IEEE RA-L、ICRA 或 IROS。能证明一般性的可检测性定理时可投 T-RO；如果有临床合作，并用量角器或动捕做验证，可投 TNSRE。

- **风险与对策**：
  - 思想是经典的：主动引用经典工作，贡献只主张实证发现。
  - 真实扭转真值偏弱（前臂袖带混入旋前旋后，上臂有软组织伪影）：主结果放在仿真里；真实数据中，袖带只在验证过轴向误差后才用于旋转。
  - 慢速桌面任务上增益可能很小：刻意设计伸直、沿光轴、悬垂这几类构型。
  - 在仿真上标定、在真实数据上测试，会破坏可交换性：如实报告。

- **Skeptic scores**：I07 3.5 / 6 / 4；I04 4 / 4 / 3.5。

### 方向三：跟踪器知不知道自己错了：基于公开多视角数据的诚实性评测协议与校准信任模型（合并 I10、I03、I09、I11、I08）

- **研究方向**：在已有的多视角手-物数据上，建立"留一视角"评测协议。按遮挡时长和遮挡原因分层，对身体、手、物体跟踪器的以下行为打分：
  - 静默失败；
  - 不确定区间的覆盖率；
  - 重新捕获时的跳变；
  - 因果结果与离线结果不收敛。

  方法部分是一个小型的校准信任模型。

- **为什么值得做**：
  - 现有的遮挡基准只给误差打分（VOccl3D [21]、[22]）；
  - TAPVid-3D [20] 对点同时评价位置和可见性，但不适用于关节链；
  - CUPS [23] 和 CHAMP [24] 只做逐帧或逐序列的共形；
  - Conformalized Kalman Filters [25] 已包含用高斯混合后验得到多模态、非凸置信区域的构造，以及轨迹级的保证，但据摘要没有模式切换动力学、没有流形状态（SO(3) 或 swing-twist）、也没有按遮挡时长调节，这一点需读全文确认；
  - Adaptive Geodesic CP [26] 已经显示，边际覆盖会掩盖最难的那部分样本：名义 90% 总体覆盖下，最难四分位只有约 60%。

  论文的诚实标签和 false_measured 正好是这样一个协议的雏形。改用公开数据后，硬件成本几乎为零。

- **具体研究问题**：
  1. 单视角因果运行时，按"错标为已测量"的比例、风险-覆盖曲线和按遮挡时长分层的覆盖率排出的名次，是否与按 MPJPE 排出的名次显著不同？判断标准：Kendall tau 明显小于 1，并且在长遮挡分箱里出现名次反转。
  2. 边际有效的区间在保持状态持续 k 帧之后会欠覆盖多少？以遮挡时长和可观测性为协变量做条件共形，能否在区间宽度仍然可用的前提下，把各分箱的覆盖率恢复到名义水平？

- **最接近的已有工作与差异**：
  - HO-Cap [10]：多台 RealSense，含交接，但没有手臂链、身体真值和弃权评分。
  - TAPVid-3D [20]：本方向把它扩展到关节组，并加入三态来源标签。
  - VOccl3D [21]：只评误差，而且它的视频是 3DGS 渲染的合成数据。
  - Adaptive Geodesic CP [26]：不涉及遮挡时长和携带状态。
  - Conformalized Kalman Filters [25]：差异如上，限于模式切换、流形状态和遮挡时长调节。

- **可能的解决方法**：
  - **数据与跟踪器分配**：每个跟踪器只放在能为它打分的数据集上。
    - 身体跟踪器（WHAM [30]、RTMPose 身体加深度）放在 ARCTIC [9] 和 BEHAVE [29] 上。ARCTIC 没有传感器深度，RGB-D 跟踪器在它上面只能用渲染深度，需要披露。
    - 手和物体跟踪器（WiLoR 或 HaMeR、FoundationPose [11]）放在 HO-Cap [10]、OakInk2 [27]、GigaHands [28] 上。
    - HO-Cap 没有身体和手臂真值，不能评身体跟踪器。
    - 用一台真实相机作测试视角，其余视角和网格作真值。
    - 有传感器深度的数据集，逐关节可见性和遮挡物类别由真值网格的 z-buffer 与传感器深度比较得到。ARCTIC 只能用网格之间的 z-buffer。
  - **公平性**：对每个跟踪器，在标定集上拟合一个事后的选择性预测头或共形头，让排名反映跟踪器本身，而不是手写的适配器。同时报告排名对适配器选择的敏感程度。
  - **评测维度**：
    - 主指标用不依赖阈值的风险-覆盖曲线和条件覆盖率；
    - 关节组上的 Average Jaccard 作为次要指标；
    - I08 的不收敛问题作为一个维度，报告声明滞后 0-30 帧时的持续发散率和重收敛时间；
    - I11 的合成遮挡与自然遮挡的排名一致性，作为一项分析。
  - **方法部分**：一个参数量低于 0.5M 的因果 GRU。输入检测分数、运动学残差、相对预测深度残差和与物体的关系，输出"测量 / 由物体估计 / 弃权"三选一，然后做分组共形校准。
  - **论文代码**：v3 grade 脚本和 S 型场景直接复用，论文的流水线只是排行榜上的一行。

- **实验与评估**：
  - **试点**（6-8 周，与可行性评审的估计一致）：
    - 第 0 周：完成 ARCTIC、BEHAVE、HO-Cap 等数据集的注册和许可申请，并为数百 GB 的下载预留存储；
    - 之后：安装和适配 4-5 个跟踪器，构建 z-buffer 可见性标签。
    - 只有当名次反转在自助法和阈值扫描下都成立时，才继续做下去。
  - **基线**：检测器置信度、集成模型、边际 split 共形、Conformalized Kalman Filters [25]、CCNet [35]。
  - 如果名次不反转，就放弃基准这条主张，只发表信任模型。

- **目标会议或期刊**：多数据集、多方法都齐全时投 NeurIPS Datasets and Benchmarks；方法部分在新指标上稳定胜出时可投 CVPR 或 ECCV；备选 3DV、WACV，或以安全遥操作为框架投 ICRA。

- **风险与对策**：
  - 名次不反转：由试点闸门提前止损。
  - 共形部分新颖性低（[46][47]，未核实）：只当作一个便宜的修复，不当作贡献。
  - 数据许可：多为非商业许可并需要注册，只发布脚本和派生指标；下载体积大，需提前规划存储。

- **Skeptic scores**：I10 3.5 / 4 / 3.5；I03 3.5 / 4 / 3.5；I09 3 / 4 / 4；I11 3.5 / 3 / 3；I08 3 / 3 / 3。

### 方向四：传感器深度何时仍优于单目度量基础模型：深度归属与非模态深度（I02，以 I17 的桌面遮挡髋部为案例）

- **研究方向**：在手-物遮挡和桌面遮挡下，判断关键点处的深度属于哪一类：身体、被握的物体、场景遮挡物，还是无效值。然后估计身体表面的非模态深度，再通过显式运动学链求解。

- **为什么值得做**：单目度量基础模型正在削弱深度相机的价值，"传感器深度什么时候仍然有用、怎么用才不会被骗"值得认真测一测。现有工作各有空缺：
  - AnyHand [31] 只做手，而且是隐式融合；
  - PromptHMR [32] 不用传感器深度；
  - AKC [4] 是确定性规则。

  论文实测到了腕部取到立方体深度、髋部取到桌面深度这类失败。可行性评审没有否决这个方向（5.5/10），因为用公开 RGB-D 数据就能直接生成真实图像上的归属伪标签。

- **具体研究问题**：
  1. 按关键点朴素采样的传感器深度，有多大比例其实属于遮挡物？各关节因此产生多少世界坐标误差？
  2. 在留出视角的真值下，"显式归属加非模态偏移加骨长约束"能否明显超过"分割掩码加点云模型拟合"这个强基线，以及单目度量方法？

- **最接近的已有工作与差异**：
  - AnyHand [31]：大规模合成 RGB(-D) 手部数据，隐式融合，只做手。
  - PromptHMR [32]：只有 RGB 的度量放置。
  - Pyramid Deep Fusion [33]：没有显式的遮挡推理。
  - HOMAE [34]：处理手-物遮挡，但不处理深度归属。

- **可能的解决方法**：
  1. **伪标签**：在 BEHAVE [29]、InterCap [48]（未核实）和 HO-Cap [10] 的单个视角上，把真值网格渲染进相机，与传感器深度比较，得到每个关键点的归属和非模态深度。
     - BEHAVE 和 InterCap 发布的拟合结果已经用到了包括测试视角在内的全部视角。要避免循环评测，就得用其余 n-1 台 Kinect 重新拟合 SMPL 和物体，这是一个独立的子项目，需要单独预算时间。
     - 替代方案是改用逐视角评测已成惯例的 RealSense 数据集，如 DexYCB 和 HO-3D（均未核实）。
     - 这些数据集的下载量很大（可达数百 GB），需要提前规划存储，并完成注册和许可申请。
  2. **基线对比**：按归属类别比较朴素采样、掩码内中值、掩码点云 SMPL/MANO 拟合、AKC 和单目度量方法。
  3. **方法**：用现有合成数据（AnyHand、BEDLAM [49]，后者未核实）预训练一个逐关键点的小网络，输出归属类别和带方差的深度偏移；然后在 v3 链上做骨长和关节限位约束求解。两侧髋部都被判为属于桌面时，用双肩加坐姿先验来求躯干根节点。

  自录的 D435 数据只作定性案例。

- **实验与评估**：最小可行实验 4-6 周，不含留出视角重拟合；如果做重拟合，另加时间。在 3-5 段 BEHAVE 序列和少量 RealSense 手-物序列上，报告：
  - 遮挡物占据深度的频率；
  - 归属 AUROC；
  - 与掩码拟合相比的逐关节世界坐标 MPJPE。

  如果不能明显超过掩码拟合，就停止。

- **目标会议或期刊**：首选 3DV，备选 WACV；以遥操作为框架时投 RA-L 或 IROS；只有在增益很大时才考虑 CVPR。

- **风险与对策**：
  - 掩码拟合可能吃掉全部增益：用最小可行实验作为闸门。
  - Kinect 和 D435 的噪声不同：分传感器报告。
  - 公开数据里很少有桌面遮挡髋部的情况：如实说明这类失败是桌面场景特有的。
  - 留出视角重拟合的工作量被低估：先用 DexYCB 或 HO-3D 类数据跑通。

- **Skeptic scores**：I02 3.5 / 5.5 / 3.5。

### 方向五：面向康复评估的单 RGB-D 测量仪器：以物体为事件时钟，带校准区间和弃权（合并 I16、I17、I18）

- **研究方向**：用被测物体的运动来确定抓取、运送、释放的时间点；对少数能测的临床运动学指标给出逐试次的校准区间；测不准时弃权。

- **为什么值得做**：这属于康复工程社群，那里的顶刊是 TNSRE、JNER，不是 CVPR。
  - 共识指标默认使用实验室动捕（[51]，未核实）；
  - 无标记方案只给点估计，没有逐试次的不确定性（[52]，未核实）；
  - 只靠手部关键点的分割，在手-物互相遮挡时最容易出错。

  这个领域已有大量 Kinect 方案（[53]，未核实），所以新意只能来自"物体时钟加诚实弃权"。

- **具体研究问题**：
  1. 以物体运动的瞬态作为事件时钟，单 RGB-D 能否把抓取和释放时刻定到与接触传感器相差 50 ms 以内，并且优于只用手部速度的分割？
  2. 肘伸展和躯干屈曲的留一受试者共形区间，能否达到名义 90% 覆盖？由诚实标签驱动的弃权，能否恰好剔除误差超过 MDC 的那些试次？

- **最接近的已有工作与差异**：
  - CUPS [23] 和 CHAMP [24]：共形 3D 姿态，不面向临床指标。
  - Conformal Risk Control [19]：只是阈值工具。
  - WHAM [30]：没有在桌面遮挡下的坐姿躯干上验证过，可以作为基线。

- **可能的解决方法**：
  - **任务**：采用共识推荐的饮水任务，在杯子上贴一个不显眼的标记，不用自定义的立方体。
  - **事件**：由物体 6-DoF 轨迹的速度和加速度瞬态确定。不用论文的 25/35 cm 滞回，因为交接时两只手腕都在 25 cm 以内，滞回分不出重叠的时长。
  - **躯干**：用胸骨或两肩中点的位移，加上胸部平面拟合和座椅先验（I17），不依赖被桌面挡住的髋部。
  - **区间**：D435 噪声经 swing-twist 链传播，再做留一受试者的 split 共形；测量帧比例不够时弃权。

- **实验与评估**：
  - **最小可行实验**（3-5 个月）：10-12 名健康成人，佩戴肘部支具来诱发代偿。
  - **真值**：接触垫加 LED 同步、3 个 IMU、侧面相机观察的胸骨 ArUco 板。
  - **报告**：Bland-Altman、ICC、SEM、MDC、覆盖率和弃权曲线。
  - **患者试点**：必须等有了临床合作方和伦理批准之后再做。

- **目标会议或期刊**：TNSRE、JNER、IEEE JBHI；备选 EMBC 或 ICORR；有患者队列之后再考虑 npj Digital Medicine。

- **风险与对策**：
  - 没有临床合作方：先发一篇健康人的方法学论文。
  - 支具只是卒中代偿的弱替代：不做临床效度方面的主张。
  - 带传感器的物体自己就能测事件，相机显得多余：主张只放在相机独有的指标上（伸手起始、躯干、肘角）。
  - 受试者影像的公开：知情同意书单列是否允许公开可识别的 RGB-D。

- **Skeptic scores**：I16 3 / 3.5 / 3.5；I17 3 / 5 / 3；I18 4 / 3 / 3。

## 3. 第一篇论文建议

建议把方向一的收窄版作为第一篇，方向二的可辨识性和可观测性分析作为它的理论部分。暂定题目：The Held Object as a Sensor for the Occluded Forearm: Identifiability of Pronation and Wrist Orientation under Grasp Closure, and Causal Switching-Grasp Smoothing from One RGB-D View。

选它的理由：
- 它直接建立在论文最有特色的资产和最清楚的已知缺陷之上；
- 决定成败的解析可辨识性检查只要几天，问题能在买硬件之前暴露；
- 三位评审给出的收窄方案一致。

它的评审分并不是最高的，见第 2 节的排序说明。如果解析检查不成立，第一篇改为方向二。

现实目标是 IEEE RA-L（附 ICRA 2028 宣讲）。投 CVPR 或 ICCV 还需要：无标记物体、5 名以上受试者、公开数据上的结果，并胜过手部朝向、外摆角回归、全身手-物交互拟合和视频人体网格恢复这四类基线。

**预先登记的继续或止损标准**：

0. 解析闸门：在 7 自由度模型下，已知手的位姿、腕位置和肘关键点时，堆叠雅可比对旋前旋后和两个腕部角满秩（退化构型除外），而且全 SE(3) 闭合相对仅平移闭合增加了这些自由度上的秩。不满足就停下，转到方向二。
1. 在握持手被遮挡、物体位姿可测的帧上，全 SE(3) 闭合的旋前旋后误差中位数比仅平移闭合低 10 度以上，并且不差于逐帧手部网格加 Kalman 的基线。测量所用的参照，其轴向误差必须已验证明显小于 10 度；否则这一条只在 ARCTIC 和合成数据上判定。外摆角只有在先验方法胜过 MANIKIN 式回归时，才写进主张。
2. 加入模式隐变量后，在 3 名受试者上都把交接后的腕误差降低至少 30%。事件数要满足功效分析的要求。
3. CUSUM 在多数人为滑动中，于腕误差超过 5 cm 之前报警。

第 0 或第 1 条不成立时，转向方向二（不需要新硬件）；方向二也不成立时，转向方向四。

**12 个月计划**：

- **2026 年第四季度**（全部闸门放在这一季，不依赖受试者）：
  - 补做文献检索，重点查：ComPose 的后续工作、MANIKIN 之后的外摆角预测、把 CHOIS 当作估计器用的工作、手部网格恢复近作；
  - 用几天时间完成解析可辨识性检查（任务 1）；
  - 用 28 段已有录制统计"握持手被遮挡而物体可测"的帧比例，这一步不需要硬件；
  - 在 R5 人为遮蔽协议上复现约 1.7 cm，并对照表 7.7 和表 7.9；
  - 解析检查通过后，再做 Unity Fisher 扫描（2-3 周）；
  - 准备第二台 D435、六面标记立方体和袖带；
  - 验证袖带：如果所在机构允许自我实验，由作者本人先做；借用一天光学动捕，或用夹板加触诊作参照；
  - 提交最低风险伦理申请；
  - 申请 ARCTIC、OakInk2 许可（数据量大，提前规划存储）。
- **2027 年第一季度**：
  - 实现平滑器，以及 (a) 到 (j) 全部基线；
  - 在 ARCTIC 渲染深度和 OakInk2 或 GRAB 的 z-buffer 合成划分上做旋前旋后实验；
  - 在公开数据上统计遮挡场景出现的频率；
  - 由作者本人试录，确定滑动比例阈值和功效分析所需的事件数。
- **2027 年第二季度**：
  - 伦理批准后录制 3 名受试者（审批通常需要 2-3 个月，这里留了余量）；
  - 加入 HMM 和 NIS 加 CUSUM；
  - 评估换用 FoundationPose 的可行性；
  - 6 月底前做出继续或止损的决定；
  - 写初稿。
- **2027 年第三季度**：
  - 补齐消融：滞后长度、平移闭合对全位姿闭合、有无模式隐变量、刚性闭合对滑动约束；
  - 投 RA-L 并选 ICRA 2028 宣讲。这个选项的截稿通常在 9 月中旬前后，具体日期需要核实；如果录制延误，改投 IROS 或下一轮 RA-L；
  - 视进度启动方向三的 6-8 周试点（第 0 周先办数据许可）。

**前三项具体任务**：

1. **解析可辨识性检查与频率统计（1-2 周，零硬件）**：
   - 对 7 自由度手臂（外摆角、肩内旋、旋前旋后、腕屈伸、尺桡偏），写出各种测量组合下的堆叠雅可比：已知手的位姿、已知腕位置、已知或缺失肘和肩关键点。求秩，标出退化构型，尤其是肘伸直。
   - 同时在 28 段录制上，统计握持手腕部失效而标记仍被测得的帧比例。
   - 解析结果支持时，再用 v3 四元数核心在 Unity 采样构型和 D435 噪声模型下做 Fisher 扫描（2-3 周）。不支持时，在投入硬件之前停下。
2. **平滑器与复现（3-4 周）**：
   - 在 GTSAM 中先把模式固定、把 G 冻结为只有平移，在同一个 R5 人为遮蔽协议上复现约 1.7 cm 的中位误差。v3 S 型场景以角度（E_occ）计分，不能拿来对比厘米数。
   - 同时在论文表 7.7 的三个窗口上报告结果，确认窗口依赖性是否仍然存在。
   - 之后再依次加入：7 自由度链、全 SE(3) 闭合、按实测散布设定的握持过程噪声、每次握持重新初始化，以及握持偏移注入场景。
3. **真值装置与袖带验证（3-4 周）**：
   - 把第二台 D435 标定到桌面世界坐标系；
   - 用六面标记立方体解决交接时标记丢失的问题；
   - 袖带只对参照相机可见；
   - 借用光学动捕，或用夹板加触诊肱骨上髁作参照，分别测出袖带的位置误差和轴向旋转误差，只有轴向误差明显小于 10 度时才把袖带用于旋转；
   - 由作者本人先完成一轮交接、换握、滑动的试录。

## 4. 已否决、降级或保留为旁支的想法

- **I06 双手闭环与躯干共模诊断**：腕部是在世界坐标里直接测量的，闭合残差对髋部的共模偏移不敏感，而且绕两腕连线的旋转不可观测。降级为方向一里的一个消融。
- **I08 因果-离线发散**：唯一的证据是两套门控规则不一致造成的一次事件；方法与 MHT、Diffusion Forcing [36] 高度重合。降级为方向三里的一个评测维度。
- **I05 物体条件生成式补全**：本质上是 OMOMO [7]、CHOIS [8]、RoHM [12] 和 MANIKIN [45] 的重组，现有真值也分辨不出它声称的 2 倍增益。只保留信息增益分析，作为方向一的后续。
- **I09 学习式测量信任**：学习式测量协方差已有成熟工作（KalmanNet [42]），动机又依赖被误读的 D-017 结果。并入方向三。
- **I03 与 I04 作为独立方法论文**：Mondrian 共形、自适应共形和 RAIM 都是现成工具，1e-3 级的完整性风险用现有数据无法验证。分别并入方向三和方向二。
- **I11 合成遮挡有效性**：这个元问题在分类领域已有结论（[50]，未核实），用自录数据统计效力也不够。并入方向三。
- **I10 新采集基准数据集**：10-15 人的实验室数据集无法与 HO-Cap 竞争，而且袖带会改变检测器看到的输入。改为方向三的公开数据协议。
- **I12 来源感知的人到机器人数据**：按维度屏蔽损失已是常规做法（[54]，未核实）；SO-101 只有 5 个自由度，逐关节可观测性在上面没有意义；相对 CUPID [38]、OKAMI [39] 的增量很小。它的下游任务思路保留为方向一的 CoRL 扩展。
- **I13 自交接学习**：ALOHA 的 Transfer Cube（[55]，未核实）和 RoboTwin 2.0 [37] 已经覆盖了这个任务；论文的流水线没有手部朝向；可达性规划会压过人类示范提供的先验。
- **I14 自标定多相机**（平均 3.8，可行性视角未被否决）：作为一般的自标定论文，这个领域很拥挤（HumanCalib [40]、EF-Calib [41]、CasCalib [56]），而且带标记的立方体本身就是标定靶。保留为低成本旁支：重构为"在线标定完整性监测"，即检测相机或世界坐标系在录制中途发生漂移。可以复用论文的度量世界坐标系，不需要新硬件，能与方向一并行，目标 RA-L。
- **I15 诚实性渲染用户研究**：主要结论是可以预期的，三类受众又稀释了主张。只有单做观察者实验，才可能投 IEEE VR。
- **I16、I17、I18 作为独立的临床论文**：缺临床合作方、缺动捕、缺患者。合并为方向五。
- **I19 运动学流去标识化**（平均 3.8，可行性视角未被否决）：运动的可识别性已经确立（[57]，未核实），防御手段也常规，与论文核心贡献的关联最弱。保留为低成本旁支：改用公开骨架数据 NTU RGB+D 120（未核实）重新表述，不需要新硬件和新受试者。优先级低于 I14。
- **通用提醒**：不要再用"遮挡时检测器置信度更高"作为动机证据；不要把 eval 轨道的 1.7 cm 和 21 cm 说成论文正文已经证明的结果。

## 5. 参考文献

**说明**：
- "已核实"指条目存在、标题与出处已由检索结果或 GitHub 上的官方仓库、arXiv 镜像、论文列表确认。本轮网络检索额度已耗尽，复核主要通过 GitHub 完成；个别条目的出处只有二手来源，已逐条注明。
- "未核实"的条目来自评审者的记忆，投稿前必须逐条查证。

**已核实**

- [1] ComPose: When to Trust Hands for Object Pose Tracking. arXiv 2026（2605.23523）. https://arxiv.org/abs/2605.23523
- [2] IMU-HOI: A Symbiotic Framework for Coherent Human-Object Interaction and Motion Capture via Contact-Conscious Inertial Fusion. CVPR 2026. https://arxiv.org/abs/2606.28604
- [3] Visibility Aware Human-Object Interaction Tracking from Single RGB Camera (VisTracker). CVPR 2023. https://openaccess.thecvf.com/content/CVPR2023/html/Xie_Visibility_Aware_Human-Object_Interaction_Tracking_From_Single_RGB_Camera_CVPR_2023_paper.html
- [4] Seeing Through Occlusion: Deterministic Arm Kinematic Correction for Robot Teleoperation (AKC). arXiv 2026（2606.19240）. https://arxiv.org/abs/2606.19240
- [5] HOLD: Category-agnostic 3D Reconstruction of Interacting Hands and Objects from Video. CVPR 2024. https://arxiv.org/abs/2311.18448
- [6] BIGS: Bimanual Category-agnostic Interaction Reconstruction from Monocular Videos via 3D Gaussian Splatting. CVPR 2025. https://openaccess.thecvf.com/content/CVPR2025/papers/On_BIGS_Bimanual_Category-agnostic_Interaction_Reconstruction_from_Monocular_Videos_via_3D_CVPR_2025_paper.pdf
- [7] Object Motion Guided Human Motion Synthesis (OMOMO; dataset FullBodyManip). SIGGRAPH Asia 2023 (ACM TOG). https://arxiv.org/abs/2309.16237
- [8] Controllable Human-Object Interaction Synthesis (CHOIS). ECCV 2024. https://github.com/lijiaman/chois_release
- [9] ARCTIC: A Dataset for Dexterous Bimanual Hand-Object Manipulation. CVPR 2023. https://openaccess.thecvf.com/content/CVPR2023/html/Fan_ARCTIC_A_Dataset_for_Dexterous_Bimanual_Hand-Object_Manipulation_CVPR_2023_paper.html
- [10] HO-Cap: A Capture System and Dataset for 3D Reconstruction and Pose Tracking of Hand-Object Interaction. NeurIPS 2025 Datasets and Benchmarks. https://arxiv.org/abs/2406.06843
- [11] FoundationPose: Unified 6D Pose Estimation and Tracking of Novel Objects. CVPR 2024. 材料中未给出 URL。
- [12] RoHM: Robust Human Motion Reconstruction via Diffusion. CVPR 2024. https://arxiv.org/abs/2401.08570
- [13] X-ICP: Localizability-Aware LiDAR Registration for Robust Localization in Extreme Environments. IEEE T-RO 2024. https://www.researchgate.net/publication/375903094_X-ICP_Localizability-Aware_LiDAR_Registration_for_Robust_Localization_in_Extreme_Environments
- [14] Informed, Constrained, Aligned: A Field Analysis on Degeneracy-Aware Point Cloud Registration in the Wild. IEEE Transactions on Field Robotics 2025. https://arxiv.org/abs/2408.11809
- [15] HuManiFlow: Ancestor-Conditioned Normalising Flows on SO(3) Manifolds for Human Pose and Shape Distribution Estimation. CVPR 2023. https://arxiv.org/abs/2305.06968
- [16] Normalizing Flows on the Product Space of SO(3) Manifolds for Probabilistic Human Pose Modeling (HuProSO3). CVPR 2024. https://arxiv.org/abs/2404.05675
- [17] Protection Levels for Vision-Based Pose Estimation. arXiv 2026（2608.10023；据第三方信息被 AIAA/IEEE DASC 2026 接收，未从官方来源确认）. https://arxiv.org/abs/2608.10023
- [18] Robin Chan. Detecting Pose Estimation Failures via Keypoint Self-Consistency. arXiv 2026（2608.03516）. https://arxiv.org/abs/2608.03516
- [19] Conformal Risk Control. ICLR 2024. https://arxiv.org/abs/2208.02814
- [20] TAPVid-3D: A Benchmark for Tracking Any Point in 3D. NeurIPS 2024 Datasets and Benchmarks. https://arxiv.org/html/2407.05921v1
- [21] VOccl3D: A Video Benchmark Dataset for 3D Human Pose and Shape Estimation under Real Occlusions. ICCV 2025. https://arxiv.org/abs/2508.06757
- [22] Benchmarking 3D Human Pose Estimation Models under Occlusions. arXiv 2025. https://arxiv.org/abs/2504.10350
- [23] CUPS: Improving Human Pose-Shape Estimators with Conformalized Deep Uncertainty. ICML 2025 (PMLR v267). https://arxiv.org/abs/2412.10431
- [24] CHAMP: Conformalized 3D Human Multi-Hypothesis Pose Estimators. ICLR 2025. https://arxiv.org/abs/2407.06141
- [25] Conformalized Kalman Filters for State Estimation with Trustworthy Confidence Regions. arXiv 2026（2609.27506；摘要含高斯混合多模态置信区域与轨迹级保证）. https://arxiv.org/abs/2609.27506
- [26] Adaptive Geodesic Conformal Prediction for Egocentric Camera Pose Estimation. arXiv 2026（2605.00233）. https://arxiv.org/abs/2605.00233
- [27] OAKINK2: A Dataset of Bimanual Hands-Object Manipulation in Complex Task Completion. CVPR 2024. https://arxiv.org/abs/2403.19417
- [28] GigaHands: A Massive Annotated Dataset of Bimanual Hand Activities. CVPR 2025. https://arxiv.org/abs/2412.04244
- [29] BEHAVE: Dataset and Method for Tracking Human Object Interactions. CVPR 2022. https://arxiv.org/abs/2204.06950
- [30] WHAM: Reconstructing World-grounded Humans with Accurate 3D Motion. CVPR 2024. https://github.com/yohanshin/WHAM
- [31] AnyHand: A Large-Scale Synthetic Dataset for RGB(-D) Hand Pose Estimation. arXiv 2026（2603.25726）. https://arxiv.org/abs/2603.25726
- [32] PromptHMR: Promptable Human Mesh Recovery. CVPR 2025（官方仓库存在；会议出处只见于二手论文列表，未从官方 README 确认）. https://arxiv.org/abs/2504.06397
- [33] Pyramid Deep Fusion Network for Two-Hand Reconstruction from RGB-D Images. arXiv 2023. https://arxiv.org/pdf/2307.06038
- [34] Occlusion-Aware 3D Hand-Object Pose Estimation with Masked AutoEncoders (HOMAE). arXiv 2025（2506.10816，v2 为 2026-07；IEEE TMM 2026 的出处未找到来源，按 arXiv 引用）. https://arxiv.org/abs/2506.10816
- [35] On the Calibration of Human Pose Estimation (CCNet). ICML 2024. https://proceedings.mlr.press/v235/gu24a.html
- [36] Diffusion Forcing: Next-token Prediction Meets Full-Sequence Diffusion. NeurIPS 2024（材料注明仓库页面写为 2025）. https://github.com/buoyancy99/diffusion-forcing
- [37] RoboTwin 2.0: A Scalable Data Generator and Benchmark with Strong Domain Randomization for Robust Bimanual Robotic Manipulation. arXiv 2025. https://arxiv.org/abs/2506.18088
- [38] CUPID: Curating Data your Robot Loves with Influence Functions. CoRL 2025. https://arxiv.org/html/2506.19121
- [39] OKAMI: Teaching Humanoid Robots Manipulation Skills through Single Video Imitation. CoRL 2024. https://arxiv.org/abs/2410.11792
- [40] HumanCalib: markerless extrinsic camera calibration using human motion（代码仓库，2026-03 创建，无论文）. GitHub 2026. https://github.com/flodelaplace/HumanCalib
- [41] EF-Calib: Spatiotemporal Calibration of Event- and Frame-Based Cameras Using Continuous-Time Trajectories. IEEE RA-L 2024. https://github.com/ShaoanWang/EF-Calib
- [42] KalmanNet: Neural Network Aided Kalman Filtering for Partially Known Dynamics. IEEE TSP 2022（arXiv 2021）. https://github.com/KalmanNet/KalmanNet_TSP
- [45] Jiang, Streli, Luo, Gebhardt, Holz. MANIKIN: Biomechanically Accurate Neural Inverse Kinematics for Human Motion Estimation. ECCV 2024. https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/194_ECCV_2024_paper.php

**未核实**

- [43] 未核实：Morris, Rehg. Singularity Analysis for Articulated Object Tracking. CVPR 1998.
- [44] 未核实：Sminchisescu, Triggs. Covariance Scaled Sampling for Monocular 3D Body Tracking, CVPR 2001; Kinematic Jump Processes for Monocular 3D Human Tracking, CVPR 2003.
- [46] 未核实：Gibbs, Cherian, Candes. Conformal Prediction with Conditional Guarantees. JRSSB 2025. https://arxiv.org/abs/2305.12616
- [47] 未核实：Gibbs, Candes. Adaptive Conformal Inference Under Distribution Shift. NeurIPS 2021. https://arxiv.org/abs/2106.00170
- [48] 未核实：InterCap: Joint Markerless 3D Tracking of Humans and Objects in Interaction. GCPR 2022.
- [49] 未核实：BEDLAM: A Synthetic Dataset of Bodies Exhibiting Detailed Lifelike Animated Motion. CVPR 2023.
- [50] 未核实：Taori et al. Measuring Robustness to Natural Distribution Shifts in Image Classification. NeurIPS 2020. https://arxiv.org/abs/2007.00644
- [51] 未核实：Kwakkel et al. Standardized measurement of quality of upper limb movement after stroke (SRRR consensus). Neurorehabilitation and Neural Repair 2019.
- [52] 未核实：OpenCap: Human movement dynamics from smartphone videos. PLOS Computational Biology 2023.
- [53] 未核实：Dolatabadi et al. The Toronto Rehab Stroke Pose Dataset to detect compensation during stroke rehabilitation therapy. 约 2017.
- [54] 未核实：Octo: An Open-Source Generalist Robot Policy. RSS 2024. https://arxiv.org/abs/2405.12213
- [55] 未核实：Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT / ALOHA). RSS 2023. https://arxiv.org/abs/2304.13705
- [56] 部分核实：CasCalib: Cascaded Calibration for Motion Capture from Sparse Unsynchronized Cameras. arXiv 2405.06845 已确认存在；3DV 2024 的出处未核实.
- [57] 未核实：Nair et al. Unique Identification of 50,000+ Virtual Reality Users from Head and Hand Motion Data. USENIX Security 2023.
- [58] 未核实：WiLoR: End-to-end 3D Hand Localization and Reconstruction in-the-wild. CVPR 2025.
- [59] 未核实：HaMeR: Reconstructing Hands in 3D with Transformers. CVPR 2024.
- [60] 未核实：RTMPose（含 RTMW / wholebody 模型）. arXiv 2023.
- [61] 未核实：MediaPipe Hands: On-device Real-time Hand Tracking. arXiv 2020.
- [62] 未核实：GVHMR: World-Grounded Human Motion Recovery via Gravity-View Coordinates. SIGGRAPH Asia 2024.
- [63] 未核实：CHORE: Contact, Human and Object REconstruction from a Single RGB Image. ECCV 2022.
- [64] 未核实：GRAB: A Dataset of Whole-Body Human Grasping of Objects. ECCV 2020.
- [65] 未核实：DexYCB: A Benchmark for Capturing Hand Grasping of Objects. CVPR 2021.
- [66] 未核实：HO-3D / HOnnotate: A Method for 3D Annotation of Hand and Object Poses. CVPR 2020.
- [67] 未核实：NTU RGB+D 120: A Large-Scale Benchmark for 3D Human Activity Understanding. IEEE TPAMI 2020.