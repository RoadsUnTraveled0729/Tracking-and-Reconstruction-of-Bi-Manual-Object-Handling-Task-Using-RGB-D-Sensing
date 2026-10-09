# 证据清单：逐条核对我之前的说法

日期：2026-10-07。本清单对每条说法都先列证据，再给结论。凡是没有证据、只是判断的地方，都会直接写明。

证据等级的含义：

- "有直接证据"：已抓取的原始页面或本地原文直接写明了这件事。
- "部分证据"：只有一部分被证实，或者需要加限定条件才成立。
- "无证据只是判断"：没有任何来源能证实这件事。
- "被证据推翻"：来源写的与我之前的说法相反。

关于"已核实"：

- 对网页来说，"已核实"指本任务中抓取成功（HTTP 200），并在页面中找到了引语。
- 对本地文件来说，"已核实"只表示该行确实存在于本地文件中。本地研究记录（领域地图、痛点卡片、导师报告）是代理生成的文件。其中对论文的描述多为转述，论文原文在本任务中没有逐一重新核对。

## 1. 一页结论

| 编号 | 我之前的说法 | 证据等级 | 修正后的说法 |
| --- | --- | --- | --- |
| L1 | 手、手臂与被握物体之间的相互遮挡是领域自己写明的痛点，有多个顶会、来自不同团队的论文为证 | 部分证据 | 手与物体之间的遮挡，确实被 ARCTIC（CVPR 2023）、MOHO（CVPR 2024）、BIGS（CVPR 2025）、MagicHOI（ICCV 2025）写进了问题陈述。没有任何已抓取的论文写到"被握物体遮挡手臂"。"不同团队"没有按作者单位逐一核对，已删去。 |
| L2 | 领域地图把"以物体为证据恢复被遮挡的手臂或手"列为一个方向 | 有直接证据（排名本身是判断） | 代理生成的领域地图（2026-10-02）把它排在 8 个方向中的第 4 位。排名、试点时长、去留阈值和"领先几个月"都是代理的判断，没有外部来源。 |
| L3 | 论文自身的局限包括抓握偏移过时、扭转不可观测、手臂沿光轴时肘部敏感 | 有直接证据 | 三点论文都写了，但措辞不同：偏移"frozen with the estimator's lag"；手臂完全伸直时扭转为"unobservable"，接近伸直时扭转对噪声敏感；手臂指向相机时腕部深度不确定，肘部会偏移很远。证据只来自少数几帧，右臂 n = 4，左臂没有改善。 |
| L4 | 导师的研究领域是机器人与估计，所以论文的运动学与估计部分在他的专长内 | 部分证据 | 他在 SFU 页面列出的兴趣包括 robotics 和 multi-view tracking，没有 estimation。他 2025 年与 Dong 合作的 Applied Sciences 文章（Crossref 已核实）构建了基于 RGB-D 关键点的手部运动学模型。"在他的专长内"是判断。 |
| L5 | Furukawa 曾任导师的 MASc 学生 Michael Foo（RGB-D 人体姿态跟踪，2025）的委员会成员 | 有直接证据 | 已由 SFU Summit 论文 PDF 的委员会页证实。但这是硕士委员会的先例，不能说明本科论文委员会的规则。 |
| B1 | HaMeR 被广泛用作三维手部姿态的基线 | 部分证据 | HaMeR 发表于 CVPR 2024。至少三个互相独立的团队把它作为对比基线：Imperial 相关的一组论文、UNIST 的 BIGS、CMU 的 Hamba。"广泛"没有经过测量。 |
| B2 | HaMeR 在手持物体或被遮挡时变差，并且作者承认 | 部分证据（"作者承认"被推翻） | 作者自己的 Table 3 显示，被遮挡关节的精度明显低于可见关节。差距在最严阈值下约 2.2 倍，最宽阈值下约 1.2 倍，所有基线也都下降。手持物体的情形没有单独测量。作者没有承认这一点，反而声称 HaMeR "particularly robust"。 |
| B3 | 4D Humans 在遮挡下变差，并且作者承认 | 被证据推翻（"作者承认"） | 作者声称对 "partial occlusions" 稳健。"遮挡下变差"本身在本任务中既没有被证实，也没有被否定。HMR 2.0 使用 SMPL，不输出手部姿态。 |
| B4 | HMR 是第一个被广泛使用的这类端到端方法 | 被证据推翻（"第一个"） | HMR 是早期且被大量引用的方法（Semantic Scholar 2148 次，2026-10-07）。它自己的相关工作部分引用了更早的 Tan et al.（BMVC 2017）和同期的 Tung et al.。 |
| A1 | ARCTIC 提供 SMPL-X、MANO 和物体位姿，由动捕系统采集，没有深度图 | 部分证据 | 前半句成立。数据说明中没有列出采集的深度数据，但作者提供由三维真值渲染出的深度图，所以"没有深度图"说得太绝对。 |
| A2 | ARCTIC 论文说手与物体的遮挡是重建任务的主要挑战 | 有直接证据（删去"主要"） | 论文把遮挡与深度歧义等一起列为挑战之一，并写明手与物体交互时遮挡更严重。 |
| A3 | OakInk2 发布了双手桌面任务的多视角图像、SMPL-X、MANO 和物体位姿 | 部分证据 | 这些内容都有发布。场景是四种桌面场景（厨房、书房、演示化学实验室、浴室）。"没有深度"是推断，原文没有直接说。 |
| A4 | CVPR、ICCV、ECCV 2024-2026 的论文仍把手物遮挡列为未解决问题 | 部分证据 | CVPR 2024、CVPR 2025 和 ICCV 2025 的手物论文仍在问题陈述中把遮挡当作核心挑战。没有核对 ECCV 和 2026 年的论文。已抓取的局限性段落都没有把遮挡列为仍未解决的问题。 |
| N1 | 没有已发表工作用被握物体的实测位姿作为观测来恢复被遮挡的手臂自由度，并做可观测性分析 | 宽泛版被证据推翻；窄版无证据只是判断 | 用手持物或佩戴物的位姿恢复手臂，已有 AvatarPoser 和 ArmTrak 等工作。5 次检索内没有找到同时具备 (a)(b)(c) 三项的论文，但检索没找到不能证明不存在。 |
| N2 | 已知腕或手的完整 6 自由度位姿时，7 自由度手臂只剩肘部摆角（swivel angle）一个自由度，这是已知结果 | 有直接证据（需加条件） | 成立的前提是：一般构型、肩中心已知且固定、连杆长度已知、忽略肩胛骨和锁骨的运动。手臂完全伸直时摆角退化。 |
| V1 | CVPR 和 ICCV 大约四篇收一篇 | 有直接证据 | CVPR 2024 为 23.6%，CVPR 2025 约 22%，ICCV 2025 为 24%。这是对所有投稿统计的基准率，不是任何一篇论文的录取概率。 |
| V2 | 3DV 录取比例更高，并且偏好几何类论文 | 前半部分证据；后半无证据只是判断 | 3DV 2025 录取率约 34% 到 40%，分母来自第三方或推断。"偏好几何"没有任何来源支持。 |
| V3 | ICCV 2027 截稿大约在 2027 年 3 月，7 月左右出结果 | 部分证据（是预测） | 估计 3 月上旬截稿、6 月下旬出结果，依据是 ICCV 2023 和 2025 的日期。截至 2026-10-07，官方还没有公布 2027 年的日期。 |
| V4 | TPAMI 和 IJCV 要求比一篇会议论文更大的贡献 | 部分证据 | TPAMI 只对"基于会议论文的投稿"要求实质性修改（一般认为 30%，按个案处理）。IJCV 当前政策未核实。"期刊要求更多"只是社区惯例，属于判断。 |
| K1 | Berkeley EECS 不招独立的研究型硕士，外校申请者只能选 PhD 或一年制 MEng | 被证据推翻 | M.S.-only 项目存在，但规模很小（通常少于 10 人），偶尔录取有研究经验的优秀申请者。系里建议想做研究的人申请 MS/PhD 或 PhD。 |
| K2 | EECS PhD 申请截止在 12 月初 | 有直接证据 | 2027 年秋季入学一轮的截止日是 2026 年 12 月 1 日。页面没有写具体时刻，请在申请系统中确认。 |
| K3 | Kanazawa、Malik 是 Berkeley EECS 教员，团队出了 HMR、4D Humans、HaMeR；Pavlakos 曾在 Berkeley 做博士后，现在 UT Austin；Tulsiani 在 Berkeley 读博，现在 CMU；Fouhey 在 NYU | 有直接证据 | 全部证实。两处修正：Tulsiani 的主页写的是"graduated from UC, Berkeley"，没有写 PhD；Fouhey 2026-09 至 2027-09 在 Polymathic AI 学术休假。 |
| K4 | Berkeley 的机器人团队（Abbeel、Levine、Goldberg、Malik）在做"从人类视频学习操作" | 部分证据 | 每人都有一篇 2024-2025 年的相关论文。Levine 那篇署名单位是 Physical Intelligence，不是 Berkeley。这不能说明这是他们团队的主要方向。 |
| S1 | Payandeh 的方向是机器人、触觉、遥操作和估计 | 部分证据 | 机器人和触觉有直接证据。遥操作只出现在实验室"近期"项目和 2002 年的论文中。估计没有列为研究方向。 |
| S2 | 第一作者期刊论文，无论期刊档次，都是 PhD 申请中的强项 | 无证据只是判断（来源倾向相反方向） | 没有来源支持"无论档次"。来源说的是：发表不是必需条件；委员会熟不熟悉、看不看重发表渠道，会影响这篇论文的分量。 |

## 2. 逐条证据

### (a) 领域自己写明的遮挡问题

#### L1

我之前的说法：手、手臂与被握物体之间的相互遮挡，是领域自己写明的痛点，有多个顶会、来自不同团队的论文为证。

证据（已抓取的论文原文）：

1. 引语："Capturing dexterous manipulation while maintaining the quality of 3D annotation is extremely challenging due to fast motion and heavy occlusion during the interaction. In particular, the joints of a hand often have significant self-occlusion. The occlusion is even more severe when a hand interacts with objects and when there are multiple hands [44]."
   来源：Fan et al., ARCTIC, CVPR 2023, arXiv 2204.13662, Sec. 3.1。
   URL：https://arxiv.org/pdf/2204.13662
   核实：已核实。

2. 引语："The bimanual interaction reconstruction exhibits severe occlusions introduced by complex interactions between two hands and an object."
   来源：BIGS, CVPR 2025（UNIST）, arXiv 2504.09097，摘要。
   URL：https://arxiv.org/html/2504.09097
   核实：已核实。

3. 引语："This work has presented MOHO for single-view reconstruction of the hand-held object with multi-view occlusion-aware supervision from hand-object videos, tackling two predominant challenges of hand-induced occlusion and object's self-occlusion."
   来源：Zhang et al., MOHO, CVPR 2024, arXiv 2310.11696，Sec. 5 Conclusion。
   URL：https://arxiv.org/html/2310.11696
   核实：已核实（采集者抓取，复核者没有再查）。

4. 引语："Consequently, they struggle with occlusions, leading to incomplete object surfaces in cases of hand-induced or self-occlusions."
   来源：Wang et al., MagicHOI, ICCV 2025, arXiv 2508.05506，讲的是先前的方法。
   URL：https://arxiv.org/html/2508.05506
   核实：已核实（采集者抓取，复核者没有再查）。

辅助证据（本地代理记录，论文原文在本任务中没有重新抓取）：

5. 引语："| P04 | 操作过程中手持物体的位姿 | core | 53 | research | YES | MEDIUM-HIGH | rising | 0 | 6.8 | 是 | MAYBE |"
   来源：本地领域地图 FIELD_MAP_2026-10-02.md 第 3 节表格。
   URL：research/FIELD_MAP_2026-10-02.md:238
   核实：已核实（仅本地行）。

6. 引语："| P15 | 遮挡下握持手的手指姿态 | core | 35 | research | YES | HIGH | rising | 0 | 6.7 | 是 | MAYBE |"
   来源：同上。
   URL：research/FIELD_MAP_2026-10-02.md:249
   核实：已核实（仅本地行）。

7. 引语："| P11 | 遮挡、自遮挡与截断下不可见的身体部位 | core | 38 | research | PARTLY | HIGH | rising | 0 | 6.2 | 是 | MAYBE |"
   来源：同上。P11 涵盖所有遮挡物（家具、他人、自遮挡、截断），并不专指被握物体遮挡手臂。
   URL：research/FIELD_MAP_2026-10-02.md:245
   核实：已核实（仅本地行）。

8. 引语："每节的证据行是步骤 2b 记录对论文原文的转述，不是原文引语。"
   来源：领域地图第 3 节的前言。
   URL：research/FIELD_MAP_2026-10-02.md:281
   核实：已核实（仅本地行）。

9. 引语："our pipeline occasionally fails to detect the occluded hand entirely."
   来源：本地 JSON 中为 SHOW3D（CVPR 2026）记录的引语，由代理提取。
   URL：research/field_painpoints_2026-10-01.json:8627
   核实：本地行已核实，论文原文未核实。

10. 引语："Direct visual tracking of the object is infeasible throughout the manipulation because the human hand persistently occludes the object."
    来源：本地 JSON 中为 CosmoH2G（SIGGRAPH Asia 2026）记录的引语，由代理提取。
    URL：research/field_painpoints_2026-10-01.json:16663
    核实：本地行已核实，论文原文未核实。

怀疑者的反驳：

- 本地记录中的论文描述多为转述，没有重新抓取原文。
- 在"物体遮挡手"这一侧，只有 SHOW3D 有一句匹配的记录引语。卡片 P15 把 Ego-Exo4D 标为未核实。InterCap 关于 OpenPose 遮挡的那句话来自 failure_modes 字段，不在它的引语里。[1543] 和 [1534] 是研讨会论文。
- P16 的三条证据（BEHAVE、OMOMO、BEDLAM）讲的是传感器噪声和数据覆盖，与遮挡无关，已从本条删去。
- "不同团队"没有按作者单位逐一核对。
- 没有任何记录写到"被握物体遮挡手臂"。

修正后的说法：手与物体之间的遮挡是领域自己写明的难点。ARCTIC（CVPR 2023）写明，手与物体交互时遮挡"even more severe"。MOHO（CVPR 2024）把手造成的遮挡列为两个主要挑战之一。BIGS（CVPR 2025）写明双手与物体交互时存在"severe occlusions"。MagicHOI（ICCV 2025）写明先前的方法"struggle with occlusions"。这四篇的作者单位没有逐一核对，所以我不再说"不同团队"。没有任何已抓取的论文写到"被握物体遮挡手臂或前臂"，这一部分是你的论文自己的框定。

#### A2

我之前的说法：ARCTIC 论文说手与物体的遮挡是重建任务的主要挑战。

证据：

1. 引语："This task has several challenges: (1) Spatio-temporal consistency requires precise hand-object 3D alignment for all frames; (2) This precision is hard to achieve due to depth ambiguity and severe occlusions during dexterous manipulation;"
   来源：ARCTIC, CVPR 2023, arXiv 2204.13662, Introduction。
   URL：https://arxiv.org/pdf/2204.13662
   核实：已核实。

2. 引语："The occlusion is even more severe when a hand interacts with objects and when there are multiple hands [44]."
   来源：同上，Sec. 3.1。
   URL：https://arxiv.org/pdf/2204.13662
   核实：已核实。

3. 引语："Future work should expand the number and complexity of objects to further study the problems of depth ambiguity and occlusion."
   来源：同上，局限性与讨论段。
   URL：https://arxiv.org/pdf/2204.13662
   核实：已核实。

怀疑者的反驳：论文把遮挡与深度歧义、时空一致性等一起列为挑战之一，没有说它是"主要"挑战。

修正后的说法：ARCTIC 写明，精确的手物三维对齐"hard to achieve due to depth ambiguity and severe occlusions during dexterous manipulation"；手与物体交互时遮挡"even more severe"；并把深度歧义和遮挡列为未来工作。我删去"主要"二字。

#### A4

我之前的说法：CVPR、ICCV、ECCV 2024-2026 年的论文仍把手物遮挡列为未解决问题。

证据：

1. MOHO（CVPR 2024）：引语见 L1 第 3 条。会议信息来自 arXiv 评论栏 "CVPR 2024"。
   URL：https://arxiv.org/abs/2310.11696
   核实：已核实。

2. 引语："When two hands are involved, occlusion patterns of two hands and an object become dramatic and hand-object pixels cannot be properly reconstructed due to the severe occlusions."
   来源：BIGS, CVPR 2025（arXiv 评论栏 "Accepted to CVPR 2025"）, Introduction。
   URL：https://arxiv.org/html/2504.09097
   核实：已核实。

3. 引语："Limitations and future work: Although our method achieves reliable bimanual category-agnostic reconstruction, our reconstruction is limited to articulated hands, where their LBS is known, or rigid objects."
   来源：BIGS 的局限性段。这一段没有提到遮挡。
   URL：https://arxiv.org/html/2504.09097
   核实：已核实。

4. 引语："Most RGB-based hand-object reconstruction methods rely on object templates, while template-free methods typically assume full object visibility. This assumption often breaks in real-world settings, where fixed camera viewpoints and static grips leave parts of the object unobserved, resulting in implausible reconstructions."
   来源：MagicHOI, ICCV 2025，摘要。会议信息由 CVF open access 页面证实。
   URL：https://arxiv.org/abs/2508.05506
   核实：已核实。

5. 引语："Furthermore, our reliance on raw RGB data for supervision may hinder the reconstruction of rarely observed object regions."
   来源：Fan et al., HOLD, arXiv 2311.18448 的局限性段。会议信息没有在任何已抓取的页面上确认。
   URL：https://arxiv.org/html/2311.18448
   核实：已核实。

怀疑者的反驳：

- 这些引语都是摘要或引言里的问题陈述，作用是引出作者自己的解决方法，并不说明这些论文发表之后问题仍未解决。
- 没有核对任何 ECCV 论文或 2026 年的论文。
- HOLD 的会议没有确认。

修正后的说法：CVPR 2024、CVPR 2025 和 ICCV 2025 的手物论文仍在问题陈述中把遮挡当作核心挑战。已抓取的 BIGS 和 HOLD 的局限性段落都没有把遮挡列为仍未解决的问题。MOHO 的局限性写在补充材料里，没有抓取。ECCV 和 2026 年的论文没有核对，我删去 ECCV。

#### A1

我之前的说法：ARCTIC（CVPR 2023）提供双手操作铰接物体的 SMPL-X、MANO 和物体位姿，由动捕系统采集，没有深度图。

证据：

1. 引语："It includes 3D groundtruth for SMPL-X, MANO, articulated objects."
   来源：ARCTIC GitHub README。
   URL：https://raw.githubusercontent.com/zc-alexfan/arctic/master/README.md
   核实：已核实。

2. 引语："It is captured in a MoCap setup using 54 high-end Vicon cameras."
   来源：同上。
   URL：同上
   核实：已核实。

3. 引语："Images are from 8x 3rd-person views and 1x egocentric view (for mixed-reality setting)."
   来源：同上。
   URL：同上
   核实：已核实。

4. 引语："`arctic_data/data/raw_seqs [215M]`: raw GT sequences in world coordinate (e.g., MANO, SMPLX parameters, egocentric camera trajectory, object poses)"
   来源：ARCTIC 数据说明 docs/data/README.md。
   URL：https://raw.githubusercontent.com/zc-alexfan/arctic/master/docs/data/README.md
   核实：已核实。

5. 引语："Depth images of the two hands, the human body, and objects can be rendered from ARCTIC (see SupMat)."
   来源：ARCTIC 论文 Sec. 3。
   URL：https://arxiv.org/pdf/2204.13662
   核实：已核实。

6. 引语："This is a repository for preprocessing, splitting, visualizing, and rendering (RGB, depth, segmentation masks) the ARCTIC dataset."
   来源：ARCTIC GitHub README 开头一段。
   URL：https://raw.githubusercontent.com/zc-alexfan/arctic/master/README.md
   核实：已核实。

7. 引语："booktitle = {Proceedings IEEE Conference on Computer Vision and Pattern Recognition (CVPR)}, year = {2023}"
   来源：ARCTIC 项目页的 BibTeX。
   URL：https://arctic.is.tue.mpg.de
   核实：已核实。

怀疑者的反驳：采集者修正版里的"与 RGB 相机同步"和"可选的 Kinect 式噪声"两句，证据中没有对应的引语，已删除。"没有使用深度传感器"是从页面没写推断出来的。

修正后的说法：ARCTIC（CVPR 2023）发布 8 个第三人称视角和 1 个第一人称视角的 RGB 图像，以及包含 MANO、SMPL-X 参数、第一人称相机轨迹和铰接物体位姿的真值序列。真值来自 54 台 Vicon 相机的动捕系统。数据说明的下载列表中没有采集的深度数据，但作者明确提供由三维真值渲染出的深度图。所以准确的说法是"没有传感器采集的深度，有渲染深度"。

#### A3

我之前的说法：OakInk2（CVPR 2024）发布了双手桌面任务的多视角图像、SMPL-X、MANO 和物体位姿。

证据：

1. 引语："OAKINK2 dataset provides multi-view image streams and precise pose annotations for the human body, hands and various interacting objects."
   来源：Zhan et al., OakInk2, arXiv 2403.19417，摘要页。评论栏写的是 "To be appeared in CVPR 2024. 26 pages"。
   URL：https://arxiv.org/abs/2403.19417
   核实：已核实。

2. 引语："'obj_transf': dict[str, dict[int, np.ndarray]], # object transformation matrix [4, 4] / 'raw_smplx': ... # raw smplx data / 'raw_mano': ... # raw mano data"（省略号为本清单所删）
   来源：OakInk2 GitHub README，Dataset Format 部分。
   URL：https://raw.githubusercontent.com/oakink/OakInk2/master/README.md
   核实：已核实。

3. 引语："The MoCap system uses 12 Optitrack Prime 13W infrared cameras to track the surface markers affixed to the subject's upper body, left and right hand, and interacting objects. The multi-camera system consists of 4 commodity RGB cameras, 3 of which are from allocentric views and 1 is from the egocentric view."
   来源：OakInk2 论文 Sec. 3.2.1。
   URL：https://arxiv.org/pdf/2403.19417
   核实：已核实。

4. 引语："These scenarios are: 1) kitchen table; 2) study room table; 3) demo chem lab; 4) bathroom table."
   来源：OakInk2 论文 Sec. 3.1。
   URL：同上
   核实：已核实。

5. 转述：论文说身体网格用 SMPL-X 重建，MANO 等表示由这个结果导出。
   来源：OakInk2 论文 Sec. 4。
   URL：同上
   核实：已核实。

怀疑者的反驳：

- 采集者写的"30 fps"没有引语支持，已删除。
- "没有深度"是推断，原文没有直接说。
- "桌面任务"说得比较松。

修正后的说法：OakInk2 发布 4 台普通 RGB 相机（3 个第三人称视角、1 个第一人称视角）的多视角图像流，以及 SMPL-X、MANO（由 SMPL-X 拟合导出）和物体 4x4 变换的标注。标注由 12 台 OptiTrack 相机的标记式动捕系统获得。场景是四种桌面场景：厨房、书房、演示化学实验室、浴室。采集设置和数据格式中都没有提到深度相机，"没有深度"是推断。

### (b) Berkeley 的模型及其弱点

#### B1

我之前的说法：HaMeR 被广泛用作三维手部姿态的基线。

证据：

1. 引语："booktitle = {Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)}"
   来源：CVF open access 上 HaMeR 的 CVPR 2024 页面。
   URL：https://openaccess.thecvf.com/content/CVPR2024/html/Pavlakos_Reconstructing_Hands_in_3D_with_Transformers_CVPR_2024_paper.html
   核实：已核实。

2. 引语："\"citationCount\": 448"
   来源：Semantic Scholar API，采集者于 2026-10-07 抓取。复核者和本清单作者再查时都返回 HTTP 429，数值没有复核成功。
   URL：https://api.semanticscholar.org/graph/v1/paper/arXiv:2312.05251?fields=title,citationCount,venue,year
   核实：已核实（采集时），数值没有复核。

3. 引语："To compare the proposed method we employ with state-of-the-art methods including METRO [43], Mesh Graphormer [44], AMVUR [32], MobRecon [11], HaMeR [63] and SimpleHand [103]."
   来源：WiLoR, CVPR 2025, arXiv 2409.12259。
   URL：https://arxiv.org/html/2409.12259
   核实：已核实。

4. 引语："In particular, we use state-of-the-art performing methods for hand pose estimation, namely HaMeR [31], WiLoR [32] and HandDGP [40], coupled with DROID-SLAM [38], to recover the world-space hand and camera motion."
   来源：HaWoR, arXiv 2501.02973（会议没有确认）。
   URL：https://arxiv.org/html/2501.02973
   核实：已核实。

5. 引语："state-of-the-art 3D hand reconstruction methods like HaMeR [38], IntagHand [26] and ACR [54] fail to do so since they cannot disentangle the sources of motion."
   来源：Dyn-HaMR, arXiv 2412.12861。
   URL：https://arxiv.org/pdf/2412.12861
   核实：已核实。

6. 转述：BIGS（CVPR 2025，UNIST）在双手实验表中把 "HaMeR [47]" 列为一行基线。
   来源：BIGS, arXiv 2504.09097。
   URL：https://arxiv.org/html/2504.09097
   核实：已核实（复核者核实）。

7. 引语："Meanwhile, for a fair comparison with HaMeR [70], we trained Hamba on the same datasets as HaMeR [70] for all other comparisons."
   来源：Dong et al., Hamba, NeurIPS 2024（arXiv 评论栏 "NeurIPS 2024"），作者单位为 Carnegie Mellon University，arXiv 2407.09646。它的 FreiHAND、HO3Dv3 和 HInt 结果表中都有 HaMeR 一行。引语中的空格为 HTML 提取后整理。
   URL：https://arxiv.org/html/2407.09646
   核实：已核实（本清单作者于 2026-10-07 抓取，HTTP 200）。

8. 转述：GitHub 仓库 geopavlakos/hamer 显示约 1.2k 星。这个数字经过工具摘要，不是原始页面文本。
   URL：https://github.com/geopavlakos/hamer
   核实：未核实。

怀疑者的反驳：WiLoR、HaWoR 和 Dyn-HaMR 三篇都有 Imperial College London 的作者，而且彼此共享作者，所以不能用它们证明"广泛"。引用数没有复核成功。

修正后的说法：HaMeR 发表于 CVPR 2024。至少三个互相独立的团队把它作为对比基线：一组有 Imperial 作者的论文（WiLoR、HaWoR、Dyn-HaMR）、UNIST 的 BIGS（CVPR 2025）、CMU 的 Hamba（NeurIPS 2024）。Semantic Scholar 在采集时显示 448 次引用，复核时被限流（HTTP 429）。"广泛使用"没有经过测量，等级为部分证据。

#### B2

我之前的说法：HaMeR 在手持物体或被遮挡时变差，并且作者承认。

证据：

1. 引语："HaMeR is particularly robust and can gracefully handle cases with heavy occlusion and interactions with objects or other hands."
   来源：HaMeR, CVPR 2024, arXiv 2312.05251, Figure 4 图注。
   URL：https://arxiv.org/html/2312.05251
   核实：已核实。

2. 引语："Our approach is robust to different viewpoints, different skin tones or hand appearance (e.g. wearing different types of gloves) as well as different objects of interaction that can create various degrees of occlusion."
   来源：同上，定性结果部分。
   URL：https://arxiv.org/pdf/2312.05251
   核实：已核实。

3. 转述：HaMeR 的 Table 3（HInt 基准，PCK）分别报告可见关节和被遮挡关节的结果。三列数据集依次为 New Days / VISOR / Ego4D。
   - 可见关节：@0.05 为 60.8 / 56.6 / 52.0；@0.15 为 94.4 / 94.7 / 91.3。
   - 被遮挡关节：@0.05 为 27.2 / 25.9 / 23.0；@0.15 为 78.9 / 80.7 / 76.3。
   - 所有基线在被遮挡关节上也都下降，并且都低于 HaMeR。

   来源：HaMeR Table 3。
   URL：https://arxiv.org/pdf/2312.05251
   核实：已核实（复核者逐项核对）。

4. 转述：Hamba 的 HInt 结果表中，HaMeR 一行与上面的数字一致，并给出 @0.10 的值。可见关节为 87.9 / 88.0 / 83.2，被遮挡关节为 60.8 / 60.8 / 56.9。
   来源：Hamba, NeurIPS 2024, arXiv 2407.09646。
   URL：https://arxiv.org/html/2407.09646
   核实：已核实。

5. 引语："This strategy often leads to results that align better with the image evidence, but it is more prone to failure in cases of occlusions and truncations."
   来源：HaMeR 的相关工作部分。这句话讲的是其他方法，不是 HaMeR 本身。
   URL：https://arxiv.org/html/2312.05251
   核实：已核实。

怀疑者的反驳：

- "约 2 倍"只在最严的阈值下成立。
- Table 3 没有按遮挡物类型（物体、自身、另一只手）区分。
- 所有方法在被遮挡关节上都下降，所以这说明被遮挡关节更难，并不是 HaMeR 特有的弱点，也不是专门针对手持物体的结论。
- "作者承认"不是部分成立，而是被推翻。

修正后的说法，分三部分：

1. 被遮挡关节的精度更低：成立，依据是作者自己的 Table 3。以 New Days 为例，可见与被遮挡之比在 @0.05 为 60.8 比 27.2（约 2.2 倍），@0.10 为 87.9 比 60.8（约 1.4 倍），@0.15 为 94.4 比 78.9（约 1.2 倍）。所有基线也有同样的下降。
2. 手持物体的情形：论文没有单独测量。
3. 作者是否把这一点写成局限：没有。作者声称 HaMeR "particularly robust"。

#### B3

我之前的说法：4D Humans 在遮挡下变差，并且作者承认。

证据：

1. 引语："In ICCV 2023. Project Webpage:"
   来源：arXiv 2305.20091 摘要页的评论栏。
   URL：https://arxiv.org/abs/2305.20091
   核实：已核实。

2. 引语："We are robust to extreme poses and partial occlusions."
   来源：4D Humans，定性结果部分。
   URL：https://arxiv.org/pdf/2305.20091
   核实：已核实。

3. 引语："For example, the use of the SMPL model [45] creates certain limitations, and leveraging improved models would allow us to model hand pose and facial expressions [56], or even capture greater age variation, e.g., infants [26] and kids [55, 70]."
   来源：4D Humans，结论中的局限部分。
   URL：https://arxiv.org/html/2305.20091
   核实：已核实。

4. 引语："Moreover, since we consider each person independently, our reconstructions are less successful at capturing the fine-grained nature of people in close proximity, e.g., contact [19, 52]."
   来源：同上。
   URL：同上
   核实：已核实。

5. 引语："Despite the increased robustness of our method, we observe that HMR 2.0 occasionally recovers erroneous reconstructions in cases with very unusual articulation (first row), heavy person-person interaction (second row), and very challenging depth ordering for the different body parts (third row)."
   来源：4D Humans 补充材料 Figure S.3 图注。
   URL：https://arxiv.org/pdf/2305.20091
   核实：已核实。

怀疑者的反驳："作者承认"这一半被推翻。"遮挡下变差"这一半本任务没有去查按遮挡划分的指标，所以既没有证实也没有推翻。

修正后的说法：作者没有说 4D Humans 在遮挡下变差，反而声称对 "partial occlusions" 稳健。作者写明的局限是：SMPL 没有手部姿态和面部表情；近距离或接触的人重建较差；低分辨率影响质量。补充材料中的失败案例是罕见姿态、严重的人与人交互，以及身体部位深度顺序难以判断的情形。遮挡下是否变差，本任务既没有证实也没有推翻。因为 HMR 2.0 不输出手部姿态，它也不是手部遮挡问题的对比基线。

#### B4

我之前的说法：HMR（CVPR 2018）是第一个被广泛使用的这类端到端方法。

证据：

1. 引语："CVPR 2018, Project page with code:"
   来源：arXiv 1712.06584 摘要页的评论栏。
   URL：https://arxiv.org/abs/1712.06584
   核实：已核实。

2. 引语："\"citationCount\": 2148"
   来源：Semantic Scholar API，2026-10-07 采集时的数据。复核时返回 429。
   URL：https://api.semanticscholar.org/graph/v1/paper/arXiv:1712.06584?fields=title,citationCount,venue,year
   核实：已核实（采集时），数值没有复核。

3. 引语："Concurrently Tung et al. [46] predict SMPL parameters from an image and a set of 2D joint heatmaps."
   来源：HMR 的相关工作部分。
   URL：https://arxiv.org/html/1712.06584
   核实：已核实。

4. 转述：HMR 在相关工作中把 Tan et al.（BMVC 2017）列为更早从图像推断 SMPL 参数的工作。
   来源：同上。
   URL：同上
   核实：已核实。

5. 转述：GitHub 仓库 akanazawa/hmr 显示约 1.7k 星。
   URL：https://github.com/akanazawa/hmr
   核实：未核实。

怀疑者的反驳：对等级没有异议。"第一个"被 HMR 自己的相关工作推翻。

修正后的说法：HMR 是早期且被大量引用的、从单张 RGB 图像直接回归 SMPL 参数的方法（Semantic Scholar 2148 次，2026-10-07）。它不是第一个，我删去"第一个"。

### (c) 课题的新意与已知的摆角结果

#### N1

我之前的说法：没有已发表工作用被握物体的实测位姿作为观测，来恢复被遮挡的手臂或腕部自由度，并做可观测性分析。

证据：

1. 引语："To obtain accurate full-body motions that resemble motion capture animations, we refine the arm joints' positions using an optimization routine with inverse kinematics to match the original tracking input."
   来源：Jiang et al., AvatarPoser, ECCV 2022, arXiv 2207.13784，摘要页（评论栏 "Accepted by ECCV 2022"）。
   URL：https://arxiv.org/abs/2207.13784
   核实：已核实。

2. 引语："Our novel Transformer-based method AvatarPoser takes as input only the positions and orientations of one headset and two handheld controllers (or hands), and generates a full-body avatar pose over 22 joints."
   来源：同上，Introduction。
   URL：https://arxiv.org/pdf/2207.13784
   核实：已核实。

3. 引语："In robotics, a human arm is often modeled using 7 rotational degrees of freedom (DoF) [22] - 3 for the shoulder, 2 for the elbow, and 2 for the wrist. Since the watch is worn on the forearm near the wrist, the DoFs of the wrist are not manifested in the watch's sensor data. The remaining 5 DoFs define the state of the watch"
   来源：Shen, Wang, Roy Choudhury, ArmTrak, MobiSys 2016。
   URL：https://sinrg.csl.illinois.edu/papers/ArmTrak_Mobisys.pdf
   核实：已核实。

4. 引语："Abstract- According to the seven degrees of freedom (DOFs) human arm model composed of the shoulder, elbow, and wrist joints, positioning of the wrist in space and orientating the palm is a task requiring only six DOFs."
   来源：Kim, Li, Milutinovic, Rosen, ICRA 2012。这篇由给定的腕部位姿预测摆角，用来驱动外骨骼；手的位姿是给定的。
   URL：https://users.wpi.edu/~zli11/papers/C2012_ICRA_Rosen_KinematicRedundancy.pdf
   核实：已核实。

5. 引语："Second, human and object motion from visible frames provides valuable information to infer the occluded object."
   来源：Xie et al., VisTracker, CVPR 2023, arXiv 2303.16479。推断方向相反：由人推断被遮挡的物体。
   URL：https://arxiv.org/abs/2303.16479
   核实：已核实。

6. 引语："We introduce a probabilistic real-time approach that leverages the human hand as a prior to mitigate these uncertainties."
   来源：A Helping (Human) Hand in Kinematic Structure Estimation, ICRA 2025, arXiv 2503.05301。推断方向同样相反。
   URL：https://arxiv.org/abs/2503.05301
   核实：已核实。

7. 引语："It includes 3D groundtruth for SMPL-X, MANO, articulated objects."
   来源：ARCTIC GitHub README。复核者认为，SMPL-X 真值中包含手臂关节，所以 ARCTIC 可以用来评测手臂。真值在手臂上的质量没有核对。
   URL：https://raw.githubusercontent.com/zc-alexfan/arctic/master/README.md
   核实：已核实。

怀疑者的反驳：

- 这是一个"不存在"的说法，5 次检索不可能证明"没有已发表工作"。
- 宽泛的读法已被证据推翻：AvatarPoser 用手持控制器的 6 自由度位姿，通过 IK 恢复手臂关节；ArmTrak 写明了腕戴传感器观测不到哪些手臂自由度。
- 采集者列出的第 (d) 项（在 ARCTIC 上评测）是计划中的实验，不是前人工作的空白，应删除。
- 没有检索的领域包括：AvatarPoser 之外基于控制器位姿的 VR 上身 IK、遥操作、带运动学约束的 RGB-D 手物方法。

修正后的说法：用手持物或佩戴物的位姿恢复手臂，已有发表工作。在 5 次检索中，没有找到同时具备以下三项的论文：

- (a) 以视觉跟踪的手持刚体，作为视觉上被遮挡的手臂的观测；
- (b) 未知或需要估计的 6 自由度抓握变换；
- (c) 显式的可观测性分析。

最接近的工作是 AvatarPoser（ECCV 2022）、ArmTrak（MobiSys 2016）和 Kim et al.（ICRA 2012）。"这个组合是新的"属于判断，已移到第 3 节。

#### N2

我之前的说法：已知腕或手的完整 6 自由度位姿时，7 自由度手臂只剩一个自由度，即肘部摆角，这是逆运动学和生物力学中的已知结果。

证据：

1. 引语："Due to this redundancy, a given task can be completed by multiple arm configurations, and there is no unique mathematical solution to the inverse kinematics."
   来源：Kim et al., ICRA 2012，摘要。
   URL：https://users.wpi.edu/~zli11/papers/C2012_ICRA_Rosen_KinematicRedundancy.pdf
   核实：已核实。

2. 引语："The redundancy of the arm is expressed mathematically by defining the swivel angle: the rotation angle of the plane including the upper and lower arm around a virtual axis connecting the shoulder and wrist joints which are fixed in space."
   来源：同上。
   URL：同上
   核实：已核实。

3. 引语："In the previous section, we showed that the redundancy of the human arm is defined as the swivel angle."
   来源：同上，Section III。
   URL：同上
   核实：已核实。

4. 引语："The redundant DOF of the human arm can be constrained by specifying the elbow position"
   来源：Li, Kim, Milutinovic, Rosen, LNEE 57（Springer）, 2013。
   URL：https://users.wpi.edu/~zli11/papers/B2013_Rosen_SynthesizingRedundancy.pdf
   核实：已核实。

5. 引语："For upper-limb applications, elbow flexion is solved first, based on the target distance from wrist joint center to shoulder joint center. Then, the elbow joint position is limited on a circle in Fig. 1(b). In order to parameterize the elbow position, the swivel angle phi is defined to evaluate the rotation of arm"
   来源：Chen and Li, Robotica 40 (2022)。原文中 phi 是希腊字母。
   URL：https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/7ACD0EE648A2C9210540D813590802ED/S0263574722000789a.pdf/determining-human-upper-limb-postures-with-a-developed-inverse-kinematic-method.pdf
   核实：已核实。

6. 引语："Additionally, unlike conventional numerical algorithms, our methods allow the user to interactively explore all possible solutions using an intuitive set of parameters that define the redundancy of the system."
   来源：Tolani, Goswami, Badler, Graphical Models 2000，只读到了摘要元数据，全文没有读。
   URL：https://repository.upenn.edu/server/api/core/items/69aeafa4-5400-4ddb-93dc-9b839bf01528
   核实：已核实（仅摘要）。

7. 转述：Kallmann 2008（CAVW）没有取得全文。
   URL：https://zendy.io/title/10.1002/cav.176
   核实：未核实。

怀疑者的反驳："恰好一个"只在以下条件下成立：一般构型；肩中心已知且固定（Kim et al. 写的是 "shoulder and wrist joints which are fixed in space"）；连杆长度已知；忽略肩胛骨和锁骨的运动。手臂完全伸直时，肘部所在的圆退化为一点，摆角没有定义，这正是你的论文在 Section 3.4.3 标记的奇异情形。在你的设置中，肩中心本身也要从相机估计。

修正后的说法：在一般构型、肩中心已知且固定、连杆长度已知、忽略肩胛骨和锁骨运动的条件下，已知 6 自由度腕部位姿时，7 自由度手臂只剩一个冗余自由度，即摆角；手臂完全伸直时这一结论退化。经过核实的一手来源是 Kim et al.（ICRA 2012），另有 Li et al.（2013）和 Chen and Li（Robotica 2022）。Tolani et al.（2000）只是被其他论文引用的经典出处，本任务没有读到全文。

#### L2

我之前的说法：领域地图把"以物体为证据恢复被遮挡的手臂或手"列为一个方向。

证据：

1. 引语："| 4 | 以被握物体为证据恢复被遮挡的手、腕与前臂 | P11、P15、P16 | 0/6.2；0/6.7；0/5.7 | CVPR、ICCV、ECCV | 2-3 个月 |"
   来源：本地领域地图第 1 节排名表。
   URL：research/FIELD_MAP_2026-10-02.md:32
   核实：已核实（本地行）。

2. 引语："这个方向拥挤（P11、P15 为 HIGH），新意必须来自\"物体作为证据\"加校准，而不能是又一个遮挡鲁棒网络。"
   来源：同上，第 1 节。
   URL：research/FIELD_MAP_2026-10-02.md:94
   核实：已核实（本地行）。

3. 引语："3. 在全身视频中，手持刚体的 6-DoF 轨迹能否作为第三个锚点，修正前臂扭转和腕部平移（P16 卡片）？"
   来源：同上，第 5.4 节。
   URL：research/FIELD_MAP_2026-10-02.md:955
   核实：已核实（本地行）。

4. 引语："风险与退路。主要风险有六个：经典 RGB-D 跟踪器早用过自由空间项，新意受质疑；评审偏好纯 RGB 方法；真值噪声限制可测增益；共形方法只给边际覆盖；ECCV 2026 的相关团队可能同期推出类似工作；铰接物体会破坏刚性附着假设。"
   来源：同上，第 5.4 节。
   URL：research/FIELD_MAP_2026-10-02.md:976
   核实：已核实（本地行）。

5. 引语："但 28 段单受试者、单相机录制没有隐藏部位真值，ArUco 只能作 oracle 消融，正式结果应改用 FoundationPose。"
   来源：同上，第 5.4 节。
   URL：research/FIELD_MAP_2026-10-02.md:980
   核实：已核实（本地行）。

怀疑者的反驳：领域地图本身是代理生成的。第 4 名的排名、2-3 个月的试点、去留阈值（20%、30%、2 个百分点、10%）、"领先几个月"都是代理的判断，没有外部来源。

修正后的说法：代理生成的领域地图（2026-10-02）把这个方向排在 8 个方向中的第 4 位，依托 P11、P15、P16 三个痛点，三者都没有被驳倒。排名、阈值、时长、拥挤程度和领先时间都是判断，见第 3 节。我之前关于录制数量（28 段与论文中评测的 3 段）的推测没有核对，已删除。

### (d) 会议、期刊与录取率

#### V1

我之前的说法：CVPR 和 ICCV 大约四篇收一篇。

证据：

1. 引语："This year, the CVPR Program Committee received 11,532 paper submissions—a 26% increase over 2023—but only 2,719 were accepted, resulting in an acceptance rate of just 23.6%."
   来源：CVPR 2024 官方新闻。
   URL：https://cvpr.thecvf.com/Conferences/2024/News/Oral_Papers
   核实：已核实。

2. 引语："This year, the CVPR Program Committee received 13,008 paper submissions—a 13% increase over 2024—but only 2,872 were accepted, signaling a highly competitive acceptance rate of just 22%."
   来源：CVPR 2025 官方新闻。
   URL：https://cvpr.thecvf.com/Conferences/2025/News/Technical_Program
   核实：已核实。

3. 引语："A total of 2,701 papers were accepted, resulting in an acceptance rate of 24%, a figure that was not pre-determined and is consistent with historical ICCV rates."
   来源：ICCV 2025 官方大会手册。同一处还写明 "ICCV 2025 received 11,239 valid paper submissions"。
   URL：https://media.eventhosts.cc/Conferences/ICCV2025/iccv25_main_program.pdf
   核实：已核实。

4. 引语："Ultimately, 2,878 papers were accepted, resulting in a 22.1% acceptance rate"
   来源：Voxel51 博客对 CVPR 2025 开幕式的报道。
   URL：https://voxel51.com/blog/opening-remarks-from-cvpr-2025
   核实：已核实。

怀疑者的反驳："四篇收一篇"把 CVPR 的录取率稍微向上取整了。ICCV 只查了一年。对所有投稿统计的录取率只是基准率，不是某一篇论文的录取概率。

修正后的说法：CVPR 2024、CVPR 2025 和 ICCV 2025 的录取率在 22% 到 24% 之间。这是基准率。

#### V2

我之前的说法：3DV 录取比例更高，并且偏好几何类论文。

证据：

1. 转述：3DV 2025 官方的录用论文日程文件共 142 行，其中 121 篇 "Accept (Poster)"、21 篇 "Accept (Oral)"，最大投稿编号为 420。
   URL：https://3dvconf.github.io/2025/schedule_updated2.csv
   核实：已核实。

2. 引语："3DV 2025 Pages Loading... 353 142 (40.23%) 121 (34.28%) 21 (5.95%) Singapore, Singapore openreview"
   来源：Paper Copilot（第三方统计站）。
   URL：https://papercopilot.com/statistics/3DV-statistics/
   核实：已核实。

3. 引语："Since 2013, under the name 3DV, this event has been a platform for disseminating research results covering a broad variety of topics in 3D computer vision and graphics, from novel optical sensors, signal processing, geometric modeling, representations, to reconstruction, visualization, analysis, rendering, interaction, and a variety of applications."
   来源：3DV 2025 征稿启事。
   URL：https://3dvconf.github.io/2025/call-for-papers/
   核实：已核实。

4. 转述：征稿主题分五组。其中 ANALYSIS 组包括 "Motion and tracking" 和 "Body, face and gesture"，APPLICATIONS 组包括 "Robotics"。
   来源：同上。
   URL：同上
   核实：已核实。

怀疑者的反驳："更高"这一半依赖第三方的分母（353），或者把最大编号 420 当作投稿数的推断，而且只有一年的数据。"偏好几何"没有任何证据。

修正后的说法：

- 3DV 2025 录取 142 篇。按 Paper Copilot 统计的 353 篇投稿算，录取率为 40.2%（第三方数据）；按最大编号 420 算约为 34%（推断）。两个数字都高于 CVPR 和 ICCV 的 22% 到 24%。
- "偏好几何"没有证据支持。征稿启事中也包括运动与跟踪，以及身体、面部与手势。

#### V3

我之前的说法：ICCV 2027 截稿大约在 2027 年 3 月，7 月左右出结果。

证据：

1. 引语："var papersubmissiondeadline_1 = \"2025/03/08 09:59:59 UTC\";"
   来源：ICCV 2025 官方日期页。
   URL：https://iccv.thecvf.com/Conferences/2025/Dates
   核实：已核实。

2. 引语："var mainconferenceauthornotification_1 = \"2025/06/26 09:59:59 UTC\";"
   来源：同上。
   URL：同上
   核实：已核实。

3. 引语："Paper submissions will close on March 8, 2023 (23:59 GMT)"
   来源：ICCV 2023 官方日期页。
   URL：https://iccv2023.thecvf.com/important.dates-71.php
   核实：已核实。

4. 转述：ICCV 2027 主页写明会议在香港会议展览中心举行，日期为 2027 年 10 月 2-8 日。
   URL：https://iccv.thecvf.com/Conferences/2027
   核实：已核实。

5. 引语："The biennial conference takes place Tue. Oct 19th through Sat the 23rd, 2027 at the ."
   来源：ICCV 2027 日期页。这一页没有任何截稿日期，内容与主页矛盾，看起来是没有填写的模板。
   URL：https://iccv.thecvf.com/Conferences/2027/Dates
   核实：已核实。

怀疑者的反驳：2027 年的截稿日期是从两届推算出来的。ICCV 2025 在 6 月 26 日（UTC）发出结果，与"7 月左右"不符。

修正后的说法：这只是预测。参照 ICCV 2023 和 2025，估计 2027 年 3 月上旬截稿、6 月下旬出结果。截至 2026-10-07，官方还没有公布 2027 年的日期。由于会期比 2025 年提前，实际日期也可能更早。

#### V4

我之前的说法：TPAMI 和 IJCV 要求比一篇会议论文更大的贡献。

证据：

1. 引语："When a TPAMI submission is based on a previous conference paper, IEEE requires that the journal paper be a "substantial revision" of the previous publication (30 percent is generally considered "substantial"). TPAMI interprets and applies this requirement on a case-by-case basis with appropriate deference to the author's viewpoint."
   来源：IEEE Computer Society, TPAMI Author Information。
   URL：https://www.computer.org/csdl/api/v1/periodical/wp-content/15083?idPrefix=tp
   核实：已核实。

2. 引语："Regular paper – 12 double column pages (Submissions may be up to 18 pages in length, subject to MOPC. All regular paper page limits include references and author biographies.)"
   来源：同上。
   URL：同上
   核实：已核实。

3. 引语："Manuscripts based on previously published conference papers must be extended substantially."
   来源：2012 年 IJCV 特刊征稿传单。这不是 IJCV 当前的投稿指南。
   URL：https://lists.cs.ucsb.edu/pipermail/ilab-users/attachments/20121120/90317f8e/attachment-0001.pdf
   核实：已核实。

4. 转述：Springer 上 IJCV 当前的投稿指南页面返回了验证页面，没有读到正文。
   URL：https://link.springer.com/journal/11263/submission-guidelines
   核实：未核实。

怀疑者的反驳：TPAMI 的这段文字是对"基于会议论文的投稿"的修改要求，并不是说每篇 TPAMI 论文都必须超过一篇会议论文的贡献量。IJCV 只有 2012 年的特刊传单为证。

修正后的说法：

- TPAMI：基于会议论文的投稿必须是"substantial revision"，一般认为修改 30% 算实质性，按个案处理。
- IJCV：当前政策未核实。
- "期刊普遍要求比会议论文更多的贡献"只是社区惯例，属于判断。

### (e) Berkeley 的录取与人员

#### K1

我之前的说法：Berkeley EECS 不招独立的研究型硕士，外校申请者只能选 PhD 或一年制 MEng。

证据：

1. 引语："Occasionally we admit exceptional applicants with research experience, but the cohort generally is limited to less than 10. Students interested in a research oriented degree should consider applying directly to the MS/PhD program."
   来源：Berkeley EECS 研究型项目招生页。
   URL：https://eecs.berkeley.edu/academics/graduate/research-programs/admissions/
   核实：已核实。采集者用 curl 得到 200；复核者用 curl 得到 403，改用 WebFetch 确认了内容。

2. 引语："The 2-year M.S. degree in EECS is intended primarily for registered UC Berkeley Ph.D. students who want to add the degree."
   来源：Berkeley EECS 研究生页。
   URL：https://eecs.berkeley.edu/academics/graduate/
   核实：已核实。

3. 引语："This program is available only to Berkeley EECS and CS Undergraduates."
   来源：5th Year M.S. 页面。
   URL：https://eecs.berkeley.edu/academics/graduate/industry-programs/5yrms/
   核实：已核实。

4. 引语："Completed in one academic year — Fall and Spring only"
   来源：MEng 页面。
   URL：https://eecs.berkeley.edu/academics/graduate/industry-programs/meng/
   核实：已核实。

5. 引语："Applicants who already hold a master's degree in Electrical Engineering, Computer Science, or any field closely related are not eligible for the two-year MS or MS/PhD degrees in our department."
   来源：研究型项目 FAQ。
   URL：https://eecs.berkeley.edu/academics/graduate/faq-3/
   核实：已核实。

怀疑者的反驳：按原话，这条说法是错的。

修正后的说法：Berkeley EECS 有 M.S.-only 研究型项目，外校申请者可以申请。但项目规模很小（通常少于 10 人），主要面向本校博士生，偶尔录取有研究经验的优秀申请者。系里建议想做研究的申请者改投 MS/PhD 或 PhD。实际上，外校申请者现实可行的选择是 MS/PhD 或 PhD（研究型），或者一年制的 MEng（职业型）。

#### K2

我之前的说法：EECS PhD 申请截止在 12 月初。

证据：

1. 引语："Application Deadline December 1, 2026"
   来源：Berkeley 研究生院 EECS - Computer Science PhD 项目页。
   URL：https://grad.berkeley.edu/program/eecs-computer-science-phd/
   核实：已核实。

2. 引语："Application Deadline December 1, 2026"
   来源：Berkeley 研究生院 EECS PhD 项目页。
   URL：https://grad.berkeley.edu/program/eecs-electrical-engineering-and-computer-sciences-phd/
   核实：已核实。

3. 引语："The next available application cycle will be for Fall 2027. The application will reopen in September 2026."
   来源：EECS 招生页顶部的横幅。
   URL：https://eecs.berkeley.edu/academics/graduate/research-programs/admissions/
   核实：已核实。

怀疑者的反驳：页面没有写截止的具体时刻和时区。

修正后的说法：2027 年秋季入学的 EECS PhD 申请截止日是 2026 年 12 月 1 日。MS/PhD 项目页（https://grad.berkeley.edu/program/eecs-computer-science-ms-phd/）写的也是这一天。具体时刻请在申请系统中确认。

#### K3

我之前的说法：Kanazawa 和 Malik 是 Berkeley EECS 教员，他们的团队产出了 HMR、4D Humans、HaMeR；Pavlakos 曾在 Berkeley 做博士后，现在 UT Austin；Tulsiani 在 Berkeley 读博，现在 CMU；Fouhey 在 NYU。

证据：

1. 引语："Angjoo Kanazawa is an Associate Professor in the Department of Electrical Engineering and Computer Sciences at the University of California, Berkeley."
   URL：https://www2.eecs.berkeley.edu/Faculty/Homepages/kanazawa.html
   核实：已核实。

2. 引语："Jitendra Malik is Arthur J. Chick Professor in the Department of Electrical Engineering and Computer Science at the University of California at Berkeley"
   URL：https://www2.eecs.berkeley.edu/Faculty/Homepages/malik.html
   核实：已核实。

3. 三篇论文的作者行：
   - HMR："Authors:Angjoo Kanazawa, Michael J. Black, David W. Jacobs, Jitendra Malik"，URL：https://arxiv.org/abs/1712.06584
   - 4D Humans："Authors:Shubham Goel, Georgios Pavlakos, Jathushan Rajasegaran, Angjoo Kanazawa, Jitendra Malik"，URL：https://arxiv.org/abs/2305.20091
   - HaMeR："Authors:Georgios Pavlakos, Dandan Shan, Ilija Radosavovic, Angjoo Kanazawa, David Fouhey, Jitendra Malik"，URL：https://arxiv.org/abs/2312.05251

   核实：已核实。

4. 引语："Before that, I was a Postdoctoral Researcher at UC Berkeley, advised by Angjoo Kanazawa and Jitendra Malik."
   来源：Pavlakos 个人主页。
   URL：https://geopavlakos.github.io/
   核实：已核实。

5. 引语："I started as an Assistant Professor of Computer Science at UT Austin in January 2024!"
   来源：同上。
   URL：同上
   核实：已核实（复核者核实）。

6. 引语："I am an Assistant Professor at Carnegie Mellon University in the Robotics Institute, where I am a part of the Computer Vision group."
   来源：Tulsiani 个人主页。同一页还写："I previously graduated from UC, Berkeley where I was advised by Jitendra Malik"。
   URL：https://shubhtuls.github.io/
   核实：已核实。

7. 引语："I am an Institute Associate Professor of Computer Science and Electrical and Computer Engineering at NYU."
   来源：Fouhey 的 NYU 主页。同一页还写："Between Sept. 3 2026 and Sept 1. 2027, I am on sabbatical at Polymathic AI."
   URL：https://cs.nyu.edu/~fouhey/
   核实：已核实。

怀疑者的反驳：Tulsiani 的主页没有出现 PhD 一词。

修正后的说法：

- Kanazawa（副教授）和 Malik（Arthur J. Chick 讲席教授）是 Berkeley EECS 教员，两人以 Berkeley 单位署名了 HMR、4D Humans 和 HaMeR。HaMeR 还有 Michigan 和 NYU 的合作者，Fouhey 是其中之一。
- Pavlakos 曾在 Berkeley 做博士后，2024 年 1 月起任 UT Austin 计算机系助理教授。
- Tulsiani 毕业于 UC Berkeley，导师是 Malik，现任 CMU 机器人研究所助理教授。
- Fouhey 在 NYU，2026 年 9 月至 2027 年 9 月学术休假。
- "团队产出"只有作者和单位行支持，页面没有说哪个实验室主导了每篇论文。

#### K4

我之前的说法：Berkeley 的机器人团队（Abbeel、Levine、Goldberg、Malik）在做"从人类视频学习操作"。

证据：

1. 引语："We present an approach to learn general robot manipulation priors from 3D hand-object interaction trajectories."
   来源：HOP, arXiv 2409.08273（2024），作者包括 Abbeel 和 Malik。HTML 版写明 "All authors are affiliated to UC Berkeley."
   URL：https://arxiv.org/abs/2409.08273 ；https://arxiv.org/html/2409.08273
   核实：已核实。

2. 引语："This work develops Robot See Robot Do (RSRD), a method for imitating articulated object manipulation from a single monocular RGB human demonstration given a single static multi-view object scan."
   来源：arXiv 2409.18121（2024），作者包括 Goldberg 和 Kanazawa，单位为 UC Berkeley。
   URL：https://arxiv.org/abs/2409.18121
   核实：已核实。

3. 引语："We introduce a simple co-training recipe, and find that human-to-robot transfer emerges once the VLA is pre-trained on sufficient scenes, tasks, and embodiments."
   来源：arXiv 2512.22414（2025），作者包括 Levine。HTML 版中 Levine 的单位是 "Physical Intelligence"。
   URL：https://arxiv.org/abs/2512.22414 ；https://arxiv.org/html/2512.22414v1
   核实：已核实。

4. 引语："He joined the UC Berkeley faculty in 1995 and is Professor of Industrial Engineering and Operations Research, with secondary appointments in EECS"
   来源：Goldberg 的 EECS 主页。
   URL：https://www2.eecs.berkeley.edu/Faculty/Homepages/goldberg.html
   核实：已核实。

怀疑者的反驳：每人一篇论文只能说明他们参与过这方面的工作，不能说明这是他们团队的主攻方向。

修正后的说法：Abbeel 和 Malik 合作的 HOP（2024，全体作者为 Berkeley 单位）从野外的人类手物视频中学习机器人操作先验。Goldberg 与 Kanazawa 合作的 RSRD（2024，Berkeley）从单目人类示范视频中模仿铰接物体操作。Levine 是 2025 年一篇人类到机器人迁移论文的作者，但署名单位是 Physical Intelligence。这些论文不能说明"从人类视频学习"是这些团队的主要方向。

#### S2

我之前的说法：第一作者期刊论文，无论期刊档次，都是 PhD 申请中的强项。

证据：

1. 引语："For the top Ph.D. programs in CS, the most important component is your prior research experience and what your recommendation letters and personal statement have to say about your prior research experience."
   来源：Harchol-Balter, CMU, 2014。
   URL：https://www.cs.cmu.edu/~harchol/gradschooltalk.pdf
   核实：已核实。

2. 引语："Note that prior research experience does not mean that you need to have published a paper."
   来源：同上。
   URL：同上
   核实：已核实。

3. 引语："If your publications appear in conferences/journals which we are not familiar with and have no access to, then we cannot evaluate the quality of your work. In my experience, this usually leads us to discount such publications."
   来源：同上。
   URL：同上
   核实：已核实。

4. 引语："Competitive students will be able to demonstrate their research potential through their application materials, supported by letters of recommendation that reinforce this information."
   来源：UW Allen School PhD 招生 FAQ。
   URL：https://www.cs.washington.edu/academics/graduate/phd-program/phd-admissions/faq/
   核实：已核实。

5. 引语："Research experience: You did successful research before. Measured in publications, first-authorship, and prestige of conference where you published."
   来源：Tim Dettmers 博客，2018。
   URL：https://timdettmers.com/2018/11/26/phd-applications/
   核实：已核实。

怀疑者的反驳：CMU 指南讲的是委员会"不熟悉、无法获取"的发表渠道，这是知名度问题，不是档次问题。Dettmers 讲的是机器学习会议，不是期刊。两者都没有讨论"知名的中档期刊"这种情况，而且来源分别写于 2014 年和 2018 年。

修正后的说法：没有来源支持"无论档次"。来源说的是：发表不是必需条件；推荐信和研究经验是关键；发表渠道的知名度或声望会影响论文的分量。第一作者论文是研究经验的正面信号，尤其当推荐信说明了你在其中的角色时。

### (f) 导师与委员会先例

#### S1

我之前的说法：Payandeh 的研究方向是机器人、触觉、遥操作和估计。

证据：

1. 引语："Research Interests / Robotics, geometrical robotics / Networked dynamical systems / Multi-view tracking / Haptic devices and haptic rendering / Multi-modal interaction in serious games / Medical robotics"
   来源：SFU 工程科学学院教员页（斜杠表示原页面的换行）。
   URL：https://www.sfu.ca/fas/schools/engineering-science/faculty/faculty-members/shahram-payandeh.html
   核实：已核实。

2. 引语："Recent Research and Developments: / Visual Tracking in Conventional Minimally Invasive Surgery / Design of a Multi-Modal Dexterity Training Interface for Medical and Biological Sciences / Haptic Teleoperation Systems: Signal Processing Perspective / Opportunistic Model for Multi-Robot Coordination"
   来源：Networked Robotics and Sensing Laboratory 主页。
   URL：https://erl.ensc.sfu.ca/
   核实：已核实。

3. 引语："Networked Robotics | Multi-Modal Tracking | Visual Reconstruction | Aging-in-Place"
   来源：Google Scholar 个人页的研究兴趣。同一页显示总引用 5642，h-index 35（2026-10-07）。
   URL：https://scholar.google.com/citations?hl=en&user=LkDWOTkAAAAJ&sortby=citedby
   核实：已核实（采集者抓取，复核者没有再查）。

4. 转述：他被引最多的前五项依次是：1998 年的缝合器械美国专利（1053 次）；2000 年 J. MEMS 的触觉传感器论文（293 次）；1996 年的内窥镜手术任务分析（252 次）；2002 年的虚拟夹具遥操作论文（199 次）；2002 年的腹腔镜视觉跟踪论文（164 次）。
   来源：同上。
   URL：同上
   核实：已核实。

修正后的说法：

- 机器人和触觉有直接证据。
- 遥操作只出现在实验室的"近期"项目和 2002 年的论文中，不在他列出的研究兴趣里。
- 估计没有在任何页面上列为研究方向。
- 他列出的 multi-view tracking、Visual Reconstruction 与你的论文主题更接近。

#### L4

我之前的说法：导师的研究领域是机器人与估计，所以论文的运动学与估计部分在他的专长内。

证据：

1. 引语：见 S1 第 1 条。研究兴趣包括 robotics 和 multi-view tracking，没有 estimation。
   URL：https://www.sfu.ca/fas/schools/engineering-science/faculty/faculty-members/shahram-payandeh.html
   核实：已核实。

2. 引语："This paper presents a method for constructing a 3D kinematic model of the human hand using calibrated 2D landmark-tracking data augmented with depth information."
   来源：Dong and Payandeh, Hand Kinematic Model Construction Based on Tracking Landmarks, Applied Sciences 15(16), 8921, 2025。作者单位为 Networked Robotics and Sensing Laboratory, SFU。
   URL：https://api.crossref.org/works/10.3390/app15168921
   核实：已核实（本清单作者于 2026-10-07 抓取，HTTP 200）。MDPI 原始页面返回 403。

3. 引语："These solutions are then used in a visualization framework to qualitatively assess the accuracy of the reconstructed hand motion. As a future work, the proposed model offers a foundation for model-based hand kinematic estimation and has utility in scenarios involving occlusion or missing data."
   来源：同上，摘要。
   URL：同上
   核实：已核实。

4. 引语："- Bayesian Estimation of Hand Kinematics from Spatially Tracked Landmarks（Journal of Intelligent Systems and Control, Acadlore, 2025；Dong, Payandeh）。"
   来源：本地导师报告 advisor_payandeh_report.md。这篇论文本身没有抓取。
   URL：本地文件（会话临时目录）advisor_payandeh_report.md:7
   核实：本地行已核实，论文未核实。

5. 引语："直接回答你"想发顶会顶刊"的问题：2020-2026 年没有找到该实验室在顶级计算机视觉渠道（CVPR、ICCV、ECCV、TPAMI）或顶级机器人渠道（ICRA、IROS、RSS、T-RO、RA-L）上的论文，2022 年以后也没有任何 IEEE 或 ACM 会议论文。"
   来源：同上。
   URL：本地文件 advisor_payandeh_report.md:63
   核实：本地行已核实，底层来源没有重新抓取。

怀疑者的反驳：L4 原来的证据全部来自本地报告。官方页面没有列出 estimation。"在他的专长内"是对一个人的判断，无法证明。

修正后的说法：他列出的研究兴趣包括 robotics 和 multi-view tracking。他 2025 年与 Dong 合作的 Applied Sciences 文章用 RGB-D 关键点构建手部运动学模型，用正逆运动学求关节角，精度只做了定性评估，并把基于模型的估计和遮挡场景列为未来工作。贝叶斯估计那篇是否属实没有核实。他的专长是否覆盖你这篇论文，是判断。

#### L5

我之前的说法：Furukawa 曾任导师的 MASc 学生 Michael Foo（RGB-D 人体姿态跟踪，2025）的委员会成员。

证据：

1. 转述：SFU Summit 上 Michael Foo 论文 PDF 的 Declaration of Committee 页写明：Master of Applied Science；Chair 为 Craig Scratchley；Supervisor 为 Shahram Payandeh；Committee Member 为 Yasutaka Furukawa（Associate Professor, Computing Science）；Examiner 为 Jie Liang。题名页写 Fall 2025, School of Engineering Science。致谢中感谢 Furukawa "for agreeing to serve as part of my committee"。
   URL：https://summit.sfu.ca/_flysystem/fedora/2026-01/etd24098.pdf
   核实：已核实（复核者抓取，HTTP 200）。

2. 引语："- 答辩委员会：导师 Shahram Payandeh，委员会成员 Yasutaka Furukawa，Examiner Jie Liang，Chair Craig Scratchley。"
   来源：本地报告 furukawa_report.md。
   URL：本地文件（会话临时目录）furukawa_report.md:141
   核实：已核实（本地行）。

修正后的说法：已证实。Michael Foo 的工程科学 MASc 论文 "Toward Precision Body Pose Tracking and Reconstruction in a Network of RGB-D Sensors"（2025 年秋）的委员会由 Payandeh 任导师，Furukawa（计算科学系副教授）任委员会成员。这是硕士委员会的先例。工程科学的本科论文委员会能否邀请计算科学系的教员，没有核实。

### (g) 论文自身的局限

#### L3

我之前的说法：论文自身的局限包括抓握偏移过时、扭转不可观测、手臂沿光轴时肘部敏感。

证据（来源是 V9 论文文本，按章节和表号引用）：

1. 引语："When the arm is straight, the forearm is parallel to the upper arm, its perpendicular component vanishes, and no algebra can recover a roll about an axis from two collinear segments."，以及 "flags the twist as unobservable; later stages hold the last valid value. A nearly straight elbow leaves the flexion well conditioned but makes the twist sensitive to noise"
   来源：论文 Section 3.4.3。
   核实：已核实（本地文本）。

2. 引语："Using the object to place a hidden hand helped on one side and not on the other. The stored hand-to-object distance is learned while the hand is visible and updates slowly, so it lags behind a changing grip and freezes when tracking fails. An arm pointing straight at the camera leaves the wrist depth uncertain, so a small error there moves the elbow a long way, and a twist held through a gap is kept by the frames that follow."
   来源：论文 Chapter 9。
   核实：已核实（本地文本）。

3. 引语："Finally, values carried between frames, such as a stored hand-to-object distance or a held angle, can be out of date."
   来源：论文 Chapter 9。
   核实：已核实（本地文本）。

4. 转述（表格分栏重排）：Table 9.1 第 5 行。局限为 "Recovery helps on one occluded window and not on the other"。原因为 "Hand-object offset frozen with the estimator's lag; a nearly straight arm along the optical axis"。证据为 Loop 录制的右臂，物体辅助的结果与手工腕部标注相差 5.2 cm，对照值为 11.4 和 17.6，只有四个保留帧（Section 7.4.2）。
   核实：已核实（本地文本）。

5. 转述：Table 7.9（Section 7.4.2）中，右臂物体辅助 n = 4，中位数 5.2 cm。左臂物体辅助的中位数为 13.1 cm，而普通求解为 12.3 cm。
   核实：已核实（本地文本）。

6. 引语："It works only under the right conditions: the stored hand-to-object distance must still be current and the arm must not point straight at the camera, and even then the evidence is a handful of frames rather than a general rule."
   来源：论文 Section 10.1。
   核实：已核实（本地文本）。

怀疑者的反驳："抓握偏移过时"是我的转述，不是论文原话。"不可观测"只适用于手臂完全伸直的情形，接近伸直时论文说的是对噪声敏感，这是两种不同的条件。

修正后的说法：论文三点都写了，原文措辞如下。

1. 手物偏移 "frozen with the estimator's lag"、"lags behind a changing grip"、"can be out of date"（Table 9.1，Chapter 9）。
2. 手臂完全伸直时扭转被标记为 "unobservable"；接近伸直时扭转 "sensitive to noise"（Section 3.4.3）。
3. 手臂指向相机时腕部深度不确定，"a small error there moves the elbow a long way"（Chapter 9）。

支撑证据只有少数几帧：右臂 n = 4，左臂没有改善（Table 7.9，Section 10.1）。

## 3. 仍然只是判断的说法

下面每一项都没有任何证据能直接回答，只能用基准率和影响因素来估计。

### 1. 你的论文被 CVPR 或 ICCV 录用的概率（例如我之前说的"三成左右"）

- 基准率：所有投稿的录取率为 22% 到 24%。CVPR 2024 是 2,719/11,532，CVPR 2025 是 2,872/13,008，ICCV 2025 是 2,701/11,239。来源见 V1。这个基准率没有按论文质量分层。"三成"高于基准率，我没有任何证据支持把它往上调。
- 可能往上调的因素：在公开基准 DexYCB 上达到领域地图设定的试点阈值；正式结果改用 FoundationPose 而不是 ArUco（领域地图第 5.4 节的建议）。
- 可能往下调的因素：
  - 方向拥挤（P11、P15 标为 HIGH）；
  - 摆角冗余是已知结果（N2）；
  - 已有 AvatarPoser 和 ArmTrak 这样的近邻工作（N1）；
  - 现有录制是单受试者、单相机，没有被遮挡部位的真值（领域地图第 980 行）；
  - 领域地图列出了"评审偏好纯 RGB 方法"的风险。
- 没有任何证据能确定这个概率。

### 2. 被 3DV 录用的概率

- 基准率：3DV 2025 录取 142 篇。按第三方统计的 353 篇投稿算是 40.2%，按最大编号 420 推断约为 34%（见 V2）。
- 上下调整的因素与第 1 项相同。征稿主题中包括 motion and tracking，以及 body, face and gesture，这只说明题目符合征稿范围，不是 3DV 偏好这类论文的证据。
- 没有证据能确定这个概率。

### 3. 被 Berkeley EECS PhD 或同类项目录取的概率

- 基准率：本任务没有收集到任何录取率数据，所以我不给出数字。
- 影响因素（来自定性来源）：研究经验和推荐信最关键；发表不是必需条件；委员会不熟悉的发表渠道通常会被打折扣（CMU 指南 2014、UW FAQ、Dettmers 2018）。
- 没有证据能确定这个概率。

### 4. 一篇第一作者期刊论文能否显著加强你这份申请

- 基准率：没有定量数据，只有定性来源（见 S2）。
- 可能往上调的因素：推荐信说明了你在论文中的角色。
- 可能往下调的因素：期刊不为委员会所熟悉。
- 没有证据能确定。

### 5. "以被握物体为观测恢复手臂，并做可观测性分析"是否算新

- 依据：5 次检索。最接近的工作是 AvatarPoser（ECCV 2022）、ArmTrak（MobiSys 2016）和 Kim et al.（ICRA 2012）。单自由度摆角的结论本身是已知的（N2）。
- 往下调的风险：还有几个领域没有检索，分别是基于控制器位姿的 VR 上身 IK、遥操作、带运动学约束的 RGB-D 手物方法。在这些领域里可能会找到同类工作。
- 检索没有找到，不能证明不存在。

### 6. 导师的专长是否覆盖这篇论文

- 依据：
  - SFU 页面列出的研究兴趣；
  - 2025 年的 Applied Sciences 手部运动学文章；
  - 本地报告称近五年约 21 篇论文，2020-2026 年没有顶级视觉或机器人渠道的论文（这一数字没有重新核实）。
- 这是对一个人的判断，无法用证据确定。

### 7. 领域地图中的若干判断

这些判断包括：第 4 名的排名、"拥挤"标签、2-3 个月的试点、20% / 30% / 2 个百分点 / 10% 的去留阈值，以及"领先几个月"。

- 依据：都由代理生成，依托 P11、P15、P16 的驳倒数和平均分（0/6.2、0/6.7、0/5.7）。没有外部来源。

### 8. ICCV 2027 的截稿和出结果日期

- 依据：ICCV 2023 的截稿日是 3 月 8 日；ICCV 2025 的截稿是 3 月 8 日（UTC），出结果是 6 月 26 日（UTC）。
- 在官方公布之前，这只是预测。

### 9. "HaMeR 被广泛使用"和"期刊要求比会议论文更多的贡献"

- 依据：前者有三个独立团队把它当基线（B1），后者有 TPAMI 对会议扩展稿的规定（V4）。
- "广泛"和"普遍惯例"都没有经过测量，仍然是判断。

## 4. 对课题的影响

1. 已知腕部 6 自由度位姿时，手臂只剩摆角一个冗余自由度，这在 Kim et al.（ICRA 2012）等文献中已有明确表述。所以"由手的位姿推出其余手臂自由度"这一步推导本身不新。
2. 用手持控制器或腕戴传感器的位姿恢复手臂，也已有 AvatarPoser 和 ArmTrak。论文可以主张的新意只剩三处：以视觉跟踪的被握物体作为观测；抓握变换未知或需要估计；物体或手只被部分观测时，哪些自由度可辨识、哪些永远不可辨识的分析。
3. 你的论文已经写明，手臂完全伸直时扭转不可观测，手臂指向相机时腕部深度不确定。这两种情形正是摆角退化和观测不足的情形，应当作为可观测性分析的核心案例写出来，而不是只放在局限里。
4. HaMeR 自己的数据显示，被遮挡关节的精度明显低于可见关节，但所有方法都有这种下降，而且没有单独测量手持物体的情形。所以论文要用按遮挡物类型划分的评测来证明物体证据的作用，不能直接引用"HaMeR 在手持物体时失败"。
5. ARCTIC 提供 SMPL-X 全身真值，可以作为手臂评测的候选基准，但它的手臂真值质量和没有采集深度这两点都需要先核对。OakInk2 同样没有深度相机，所以基于 RGB-D 的评测需要渲染深度，或者另找数据。
6. 你现有的证据是单受试者、少数几帧，右臂 n = 4，左臂没有改善。领域地图也指出这些录制没有被遮挡部位的真值。所以投稿所需的结果必须来自公开基准，而不是现有录制。
7. 投稿目标方面，CVPR 和 ICCV 的基准率为 22% 到 24%，3DV 约为 34% 到 40%（分母不是官方数据）。ICCV 2027 的截稿日期目前只能估计在 2027 年 3 月上旬。

## 5. 来源

网页来源：

1. https://arxiv.org/pdf/2204.13662 （已核实）
2. https://arxiv.org/abs/2204.13662 （已核实）
3. https://raw.githubusercontent.com/zc-alexfan/arctic/master/README.md （已核实）
4. https://raw.githubusercontent.com/zc-alexfan/arctic/master/docs/data/README.md （已核实）
5. https://arctic.is.tue.mpg.de （已核实）
6. https://github.com/zc-alexfan/arctic （未核实，HTTP 403）
7. https://arxiv.org/html/2504.09097 （已核实）
8. https://arxiv.org/abs/2504.09097 （已核实）
9. https://arxiv.org/html/2310.11696 （已核实）
10. https://arxiv.org/abs/2310.11696 （已核实）
11. https://arxiv.org/abs/2508.05506 （已核实）
12. https://arxiv.org/html/2508.05506 （已核实）
13. https://openaccess.thecvf.com/content/ICCV2025/html/Wang_MagicHOI_Leveraging_3D_Priors_for_Accurate_Hand-object_Reconstruction_from_Short_ICCV_2025_paper.html （已核实）
14. https://arxiv.org/html/2311.18448 （已核实）
15. https://arxiv.org/abs/2403.19417 （已核实）
16. https://arxiv.org/pdf/2403.19417 （已核实）
17. https://raw.githubusercontent.com/oakink/OakInk2/master/README.md （已核实）
18. https://openaccess.thecvf.com/content/CVPR2024/html/Pavlakos_Reconstructing_Hands_in_3D_with_Transformers_CVPR_2024_paper.html （已核实）
19. https://api.semanticscholar.org/graph/v1/paper/arXiv:2312.05251?fields=title,citationCount,venue,year （已核实；采集时 HTTP 200，复核时 HTTP 429，数值没有复核）
20. https://github.com/geopavlakos/hamer （未核实）
21. https://arxiv.org/html/2409.12259 （已核实）
22. https://arxiv.org/abs/2409.12259 （已核实）
23. https://arxiv.org/html/2501.02973 （已核实）
24. https://arxiv.org/abs/2501.02973 （已核实）
25. https://arxiv.org/pdf/2412.12861 （已核实）
26. https://arxiv.org/abs/2412.12861 （已核实）
27. https://arxiv.org/abs/2407.09646 （已核实）
28. https://arxiv.org/html/2407.09646 （已核实）
29. https://arxiv.org/html/2312.05251 （已核实）
30. https://arxiv.org/pdf/2312.05251 （已核实）
31. https://arxiv.org/abs/2312.05251 （已核实）
32. https://arxiv.org/abs/2305.20091 （已核实）
33. https://arxiv.org/html/2305.20091 （已核实）
34. https://arxiv.org/pdf/2305.20091 （已核实）
35. https://openaccess.thecvf.com/content/ICCV2023/html/Goel_Humans_in_4D_Reconstructing_and_Tracking_Humans_with_Transformers_ICCV_2023_paper.html （已核实）
36. https://arxiv.org/abs/1712.06584 （已核实）
37. https://arxiv.org/html/1712.06584 （已核实）
38. https://openaccess.thecvf.com/content_cvpr_2018/html/Kanazawa_End-to-End_Recovery_of_CVPR_2018_paper.html （已核实）
39. https://api.semanticscholar.org/graph/v1/paper/arXiv:1712.06584?fields=title,citationCount,venue,year （已核实；采集时 HTTP 200，数值没有复核）
40. https://github.com/akanazawa/hmr （未核实）
41. https://arxiv.org/pdf/2207.13784 （已核实）
42. https://arxiv.org/abs/2207.13784 （已核实）
43. https://sinrg.csl.illinois.edu/papers/ArmTrak_Mobisys.pdf （已核实）
44. https://users.wpi.edu/~zli11/papers/C2012_ICRA_Rosen_KinematicRedundancy.pdf （已核实）
45. https://users.wpi.edu/~zli11/papers/B2013_Rosen_SynthesizingRedundancy.pdf （已核实）
46. https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/7ACD0EE648A2C9210540D813590802ED/S0263574722000789a.pdf/determining-human-upper-limb-postures-with-a-developed-inverse-kinematic-method.pdf （已核实）
47. https://repository.upenn.edu/server/api/core/items/69aeafa4-5400-4ddb-93dc-9b839bf01528 （已核实，仅摘要）
48. https://zendy.io/title/10.1002/cav.176 （未核实）
49. https://arxiv.org/abs/2303.16479 （已核实）
50. https://arxiv.org/abs/2503.05301 （已核实）
51. https://arxiv.org/abs/2204.02445 （已核实）
52. https://arxiv.org/abs/2609.08806 （已核实）
53. https://cvpr.thecvf.com/Conferences/2024/News/Oral_Papers （已核实）
54. https://cvpr.thecvf.com/Conferences/2024/News/Wrap_Release （已核实）
55. https://cvpr.thecvf.com/Conferences/2025/News/Technical_Program （已核实）
56. https://voxel51.com/blog/opening-remarks-from-cvpr-2025 （已核实）
57. https://media.eventhosts.cc/Conferences/ICCV2025/iccv25_main_program.pdf （已核实）
58. https://research.charlotte.edu/2025/08/27/6-papers-accepted-in-iccv-2025/ （已核实）
59. https://papercopilot.com/statistics/ICCV-statistics/ （已核实）
60. https://3dvconf.github.io/2025/schedule_updated2.csv （已核实）
61. https://papercopilot.com/statistics/3DV-statistics/ （已核实）
62. https://3dvconf.github.io/2025/call-for-papers/ （已核实）
63. https://iccv.thecvf.com/Conferences/2025/Dates （已核实）
64. https://iccv2023.thecvf.com/important.dates-71.php （已核实）
65. https://iccv.thecvf.com/Conferences/2027 （已核实）
66. https://iccv.thecvf.com/Conferences/2027/Dates （已核实）
67. https://www.thecvf.com/?page_id=100 （已核实）
68. https://www.computer.org/csdl/api/v1/periodical/wp-content/15083?idPrefix=tp （已核实）
69. https://lists.cs.ucsb.edu/pipermail/ilab-users/attachments/20121120/90317f8e/attachment-0001.pdf （已核实）
70. https://link.springer.com/journal/11263/submission-guidelines （未核实）
71. https://eecs.berkeley.edu/academics/graduate/research-programs/admissions/ （已核实；复核时 curl 返回 403，改用 WebFetch 确认）
72. https://eecs.berkeley.edu/academics/graduate/ （已核实）
73. https://eecs.berkeley.edu/academics/graduate/industry-programs/5yrms/ （已核实）
74. https://eecs.berkeley.edu/academics/graduate/industry-programs/meng/ （已核实）
75. https://eecs.berkeley.edu/academics/graduate/faq-3/ （已核实）
76. https://grad.berkeley.edu/program/eecs-computer-science-phd/ （已核实）
77. https://grad.berkeley.edu/program/eecs-electrical-engineering-and-computer-sciences-phd/ （已核实）
78. https://grad.berkeley.edu/program/eecs-computer-science-ms-phd/ （已核实）
79. https://www2.eecs.berkeley.edu/Faculty/Homepages/kanazawa.html （已核实）
80. https://www2.eecs.berkeley.edu/Faculty/Homepages/malik.html （已核实）
81. https://people.eecs.berkeley.edu/~kanazawa/index.html （已核实）
82. https://geopavlakos.github.io/ （已核实）
83. https://shubhtuls.github.io/ （已核实）
84. https://cs.nyu.edu/~fouhey/ （已核实）
85. https://arxiv.org/abs/2409.08273 （已核实）
86. https://arxiv.org/html/2409.08273 （已核实）
87. https://arxiv.org/abs/2409.18121 （已核实）
88. https://arxiv.org/abs/2512.22414 （已核实）
89. https://arxiv.org/html/2512.22414v1 （已核实）
90. https://www2.eecs.berkeley.edu/Faculty/Homepages/svlevine.html （已核实）
91. https://www2.eecs.berkeley.edu/Faculty/Homepages/abbeel.html （已核实）
92. https://www2.eecs.berkeley.edu/Faculty/Homepages/goldberg.html （已核实）
93. https://www.sfu.ca/fas/schools/engineering-science/faculty/faculty-members/shahram-payandeh.html （已核实）
94. https://erl.ensc.sfu.ca/ （已核实）
95. https://scholar.google.com/citations?hl=en&user=LkDWOTkAAAAJ&sortby=citedby （已核实，复核者没有再查）
96. https://api.crossref.org/works/10.3390/app15168921 （已核实）
97. https://summit.sfu.ca/_flysystem/fedora/2026-01/etd24098.pdf （已核实）
98. https://www.cs.cmu.edu/~harchol/gradschooltalk.pdf （已核实）
99. https://www.cs.washington.edu/academics/graduate/phd-program/phd-admissions/faq/ （已核实）
100. https://timdettmers.com/2018/11/26/phd-applications/ （已核实）

本地来源（代理生成的记录或论文文本；"已核实"只表示该行存在）：

- research/FIELD_MAP_2026-10-02.md，第 32、94、238、245、249、281、955、976、980 行
- research/field_painpoints_2026-10-01.json，第 8627、16663 行
- 会话临时目录中的 advisor_payandeh_report.md，第 7、63 行
- 会话临时目录中的 furukawa_report.md，第 141 行
- 会话临时目录中的 thesis_v9.txt，即 V9 论文文本提取件，对应 Section 3.4.3、Table 7.9、Table 9.1、Chapter 9 和 Section 10.1
