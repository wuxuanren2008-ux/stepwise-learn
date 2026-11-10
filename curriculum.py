# -*- coding: utf-8 -*-
"""课程包：知识点、分步揭示、常见错步、检查站、测验。

数据结构（后续模块依赖，勿改字段名）：
COURSES: list[dict] = [{
  id, title, description, icon,
  topics: list[dict] = [{
    id, title, goal, cue,
    steps: list[dict] = [{board, say, misconception}],
    checkpoint: {question, options:list[str], answer:int, why:str, wrong_step:int},
    quiz: list[dict] = [{question, options:list[str], answer:int, why:str}]
  }]
}]
"""
from __future__ import annotations

COURSES: list[dict] = [
    {
        "id": "academic-writing",
        "title": "学术英语写作",
        "description": "给留学生：从论点句到段落衔接，写出能拿分的英文论文",
        "icon": "✎",
        "topics": [
            {
                "id": "thesis-statement",
                "title": "论点句 Thesis Statement",
                "goal": "能写出一个可辩论、可展开、位置正确的论点句",
                "cue": "先别急着写句子。看这句话：「This essay will discuss climate change.」它到底算不算论点句？它缺了什么？",
                "steps": [
                    {"board": "① 论点句 ≠ 话题", "say": "「discuss climate change」只说了要谈什么，没说你要证明什么。读者看完不知道你站哪边。", "misconception": "把话题当成论点"},
                    {"board": "② 三要素：立场 + 范围 + 理由", "say": "立场 = 你主张什么；范围 = 限定到哪个人群/时期/地区；理由 = 凭什么。三者缺一，段落就会散。", "misconception": "只写立场不写理由"},
                    {"board": "③ 可辩论性检验", "say": "问自己：一个理性的人能否反对这句话？能，才是论点；人人同意的事实不是论点。", "misconception": "用无可争议的事实当论点"},
                    {"board": "④ 改写示范", "say": "话题句 →「This essay discusses climate change.」；论点句 →「Because urban heat islands amplify nighttime temperatures, Malaysian cities should mandate reflective roofing in new housing by 2030.」注意它给了人群、措施、理由。", "misconception": "改写后仍没有限定范围"},
                ],
                "checkpoint": {
                    "question": "下面哪一句是合格的论点句？",
                    "options": [
                        "Many students use AI tools for study.",
                        "Because retrieval practice strengthens long-term retention, USM freshmen should replace rereading with weekly self-quizzing in their first semester.",
                        "AI is changing education around the world.",
                        "This essay will talk about study methods.",
                    ],
                    "answer": 1,
                    "why": "第 2 句同时给了立场（应改用自测）、范围（USM 大一第一学期）、理由（提取练习增强长期记忆），且可被理性反对。其余三句都只是话题或事实。",
                    "wrong_step": 0,
                },
                "quiz": [
                    {"question": "「Students should study harder.」缺了哪一步？", "options": ["缺立场", "缺范围与理由，且不可辩论", "缺句号", "什么都不缺"], "answer": 1, "why": "它有立场但没限定人群/场景，也没给理由，且几乎没人会反对，不构成论点。"},
                    {"question": "检验论点句最快的自问是？", "options": ["句子够不够长", "有没有高级词汇", "一个理性的人能否反对它", "有没有引用文献"], "answer": 2, "why": "可辩论性是论点与事实的分界线。"},
                ],
            },
            {
                "id": "paragraph-coherence",
                "title": "段落衔接 Coherence",
                "goal": "让段落之间靠逻辑推进，而不是靠 Firstly/Secondly 硬串",
                "cue": "把三段话的 First/Second/Third 全删掉，段落还连得上吗？如果连不上，问题出在哪？",
                "steps": [
                    {"board": "① 连接词 ≠ 逻辑", "say": "Firstly/Secondly 只是编号，不表达因果、转折或递进。删掉它们就散，说明段落之间没有真正的推理关系。", "misconception": "靠连接词制造连贯"},
                    {"board": "② 旧信息 → 新信息", "say": "英文段落习惯：句首承接上一段的旧信息，句尾抛出本段的新信息。这叫 given-new contract。", "misconception": "每句都开新话题"},
                    {"board": "③ 三种真实关系", "say": "因果（therefore / as a result）、转折（however / yet）、递进（moreover / more importantly）。先判断关系，再选词。", "misconception": "先选词再想关系"},
                    {"board": "④ 改写示范", "say": "「Second, students forget.」→「Because rereading creates only a feeling of familiarity, that apparent mastery fades within days; spaced retrieval interrupts the decay.」上句承接 familiarity，下句引出 retrieval。", "misconception": "改写后仍是并列罗列"},
                ],
                "checkpoint": {
                    "question": "两段之间真正的关系是「前一段的结论被后一段的证据推翻」，该用哪类连接？",
                    "options": ["递进 Moreover", "因果 Therefore", "转折 However / Yet", "编号 Secondly"],
                    "answer": 2,
                    "why": "推翻属于转折/让步关系。用编号或因果都会把逻辑写反。",
                    "wrong_step": 2,
                },
                "quiz": [
                    {"question": "given-new contract 说的是？", "options": ["先给新信息再补旧信息", "句首承接旧信息、句尾抛出新信息", "每段必须有个新单词", "旧信息要全部删掉"], "answer": 1, "why": "这是英文段落推进的默认节奏。"},
                    {"question": "删掉所有连接词后段落就散，说明？", "options": ["连接词用得太少", "段落之间缺少真实逻辑关系", "段落太长", "词汇不够高级"], "answer": 1, "why": "连接词无法替代推理。"},
                ],
            },
            {
                "id": "citation",
                "title": "引用整合 Source Integration",
                "goal": "把文献织进自己的论证，而不是贴一句引文就结束",
                "cue": "一段里引了一句话，然后直接写下一段。读者会问什么？",
                "steps": [
                    {"board": "① 引文不是论据的终点", "say": "贴完 quote 不解释，读者会问：所以呢？这条证据支持的是我哪一步主张？", "misconception": "drop quote（掉引文）"},
                    {"board": "② 三明治：引入 → 引用 → 解读", "say": "引入说明来源与语境；引用给原话或数据；用自己的话点明它如何支撑本段主张。", "misconception": "缺少解读层"},
                    {"board": "③ 转述优先", "say": "除非原文措辞本身关键，否则 paraphrase 更能证明你读懂了，也更容易保持自己的行文语气。", "misconception": "过度直接引用"},
                    {"board": "④ 示范", "say": "「…(Author, 2022, p.14).」之后补一句：「This matters here because the same decay curve appears in our quiz data, so the mechanism is not limited to lab settings.」", "misconception": "解读仍只是复述引文"},
                ],
                "checkpoint": {
                    "question": "「掉引文 drop quote」最典型的表现是？",
                    "options": ["引用了但没写页码", "引文之后没有自己的解读，直接换段", "用了太多转述", "把引用放在段首"],
                    "answer": 1,
                    "why": "问题不在格式，在缺了「这条证据支持我哪一步」的解释。",
                    "wrong_step": 0,
                },
                "quiz": [
                    {"question": "三明治结构的中间层是？", "options": ["自己的主张", "引用本身", "文献列表", "反方观点"], "answer": 1, "why": "引入—引用—解读。"},
                    {"question": "何时才该用直接引语？", "options": ["任何时候都该", "原文措辞本身是分析对象时", "段落太短时", "找不到转述词时"], "answer": 1, "why": "其余情况转述更稳。"},
                ],
            },
        ],
    },
    {
        "id": "calculus",
        "title": "微积分基础",
        "description": "用「先认结构、再动笔」的方式过掉最常卡住的三类题",
        "icon": "∫",
        "topics": [
            {
                "id": "chain-rule",
                "title": "链式法则 Chain Rule",
                "goal": "看到复合函数先拆层，再逐层求导相乘",
                "cue": "求 d/dx sin(x²)。别急着套公式，先说清楚：哪一层是「外面」，哪一层是「里面」？",
                "steps": [
                    {"board": "① 先分层，不先求导", "say": "外层 sin(·)，内层 x²。写下来：f(u)=sin u，u=x²。分层错了，后面全错。", "misconception": "直接对 sin(x²) 整体下手"},
                    {"board": "② 外层求导（保持内层不动）", "say": "d/du sin u = cos u，代回 u=x² 得 cos(x²)。注意这里内层原封不动。", "misconception": "把内层也一起求了导"},
                    {"board": "③ 乘上内层导数", "say": "u'=2x。链式法则就是「外层导数 × 内层导数」：cos(x²)·2x。", "misconception": "漏乘内层导数"},
                    {"board": "④ 答案与自检", "say": "结果 2x·cos(x²)。自检：x=0 时导数应为 0（因为内层 2x=0），符合函数在该点附近的行为。", "misconception": "不做特殊值自检"},
                ],
                "checkpoint": {
                    "question": "求 d/dx e^(3x²)，第一步应该做什么？",
                    "options": ["直接写出 6x·e^(3x²)", "先分层：外层 e^u，内层 u=3x²", "先算 e 的近似值", "先对 3x² 积分"],
                    "answer": 1,
                    "why": "先分层是这一整套方法的起点；直接写答案属于跳步，遇到多层复合极易出错。",
                    "wrong_step": 0,
                },
                "quiz": [
                    {"question": "d/dx ln(x³+1) = ?", "options": ["1/(x³+1)", "3x²/(x³+1)", "3x²·ln(x³+1)", "1/(3x²)"], "answer": 1, "why": "外层 ln u 导数为 1/u，乘内层 3x²。"},
                    {"question": "漏乘内层导数，本质上是忘了？", "options": ["乘积法则", "链式法则的乘法规律", "极限定义", "积分常数"], "answer": 1, "why": "链式法则 = 外层导数 × 内层导数。"},
                ],
            },
            {
                "id": "limits",
                "title": "极限与 0/0",
                "goal": "识别不定式后选对化简手段，而不是乱套洛必达",
                "cue": "lim(x→2) (x²-4)/(x-2)。直接代入得到 0/0。这时候 0/0 告诉你什么？",
                "steps": [
                    {"board": "① 0/0 不是答案，是信号", "say": "它说明分子分母有公共的 (x-2) 因子，函数在该点有个可去间断点。", "misconception": "把 0/0 当成 0 或无定义就结束"},
                    {"board": "② 先因式分解", "say": "x²-4=(x-2)(x+2)，约去 (x-2) 得 x+2。这一步比洛必达更快也更不容易错。", "misconception": "一上来就用洛必达"},
                    {"board": "③ 再代值", "say": "x→2 时 x+2 → 4。极限是 4，注意原函数在 x=2 处本身无定义。", "misconception": "混淆极限值与函数值"},
                    {"board": "④ 洛必达的位置", "say": "只有当因式分解/有理化都麻烦时才用；且必须确认仍是 0/0 或 ∞/∞。", "misconception": "对非不定式也用洛必达"},
                ],
                "checkpoint": {
                    "question": "lim(x→0) sin x / x 属于哪种情况？",
                    "options": ["直接代入即可", "0/0 不定式，需要化简或用已知极限", "∞/∞", "极限不存在且无法处理"],
                    "answer": 1,
                    "why": "代入得 0/0；这是经典不定式，可用夹逼/几何或洛必达处理，值为 1。",
                    "wrong_step": 0,
                },
                "quiz": [
                    {"question": "约去 (x-2) 后得到 x+2，原函数在 x=2 处？", "options": ["等于 4", "无定义，但极限是 4", "等于 0", "等于 ∞"], "answer": 1, "why": "可去间断点：极限存在而函数值不存在。"},
                    {"question": "使用洛必达前必须确认？", "options": ["函数可导且仍为 0/0 或 ∞/∞", "x 是整数", "分母为正", "题目来自考试"], "answer": 0, "why": "条件不成立时洛必达会给出错误结果。"},
                ],
            },
            {
                "id": "integration-by-parts",
                "title": "分部积分 Integration by Parts",
                "goal": "用 LIATE 选 u，避免越积越复杂",
                "cue": "∫ x·eˣ dx。两个函数相乘，先回答：把谁选作 u？为什么不是另一个？",
                "steps": [
                    {"board": "① 公式来自乘积法则", "say": "∫u dv = uv − ∫v du。目标不是记住它，是让 ∫v du 比原式更简单。", "misconception": "死记公式不看目标"},
                    {"board": "② LIATE 选 u", "say": "优先顺序：Log / Inverse trig / Algebraic / Trig / Exponential。x 是代数，eˣ 是指数，所以 u=x。", "misconception": "把 eˣ 选作 u"},
                    {"board": "③ 代入", "say": "u=x, dv=eˣdx → du=dx, v=eˣ。于是 x·eˣ − ∫eˣdx。", "misconception": "du / v 求错"},
                    {"board": "④ 收尾 +C", "say": "结果 x·eˣ − eˣ + C = eˣ(x−1)+C。自检：对结果求导应回到 x·eˣ。", "misconception": "漏掉积分常数 C"},
                ],
                "checkpoint": {
                    "question": "∫ x·ln x dx，按 LIATE 应选？",
                    "options": ["u = x", "u = ln x", "dv = ln x dx", "无法用分部积分"],
                    "answer": 1,
                    "why": "Log 排在 Algebraic 之前，u=ln x；选 u=x 会让 ∫v du 变得更复杂。",
                    "wrong_step": 1,
                },
                "quiz": [
                    {"question": "分部积分的核心目标是？", "options": ["把式子变长", "让 ∫v du 比原式更简单", "消去所有 x", "避免使用导数"], "answer": 1, "why": "这是选 u 的唯一判据。"},
                    {"question": "不定积分最后一步常忘的是？", "options": ["写 dx", "+C", "化简", "代入上下限"], "answer": 1, "why": "不定积分代表一族函数。"},
                ],
            },
        ],
    },
    {
        "id": "study-skills",
        "title": "学习方法（元技能）",
        "description": "先学会怎么学，再把方法用在前面两门课上",
        "icon": "◎",
        "topics": [
            {
                "id": "active-recall",
                "title": "主动回忆 Active Recall",
                "goal": "把「看懂了」换成「能不看书说出来」",
                "cue": "合上书，用 30 秒写出刚才那节的三个要点。写不出来说明什么？",
                "steps": [
                    {"board": "① 熟悉感 ≠ 掌握", "say": "重读会让大脑产生「我懂了」的错觉，因为它只是在识别，不是在提取。", "misconception": "把重复阅读当复习"},
                    {"board": "② 提取才是练习", "say": "合上材料、先自己答、再对照。哪怕答错，提取动作本身就在加固记忆通路。", "misconception": "一看不会就立刻翻书"},
                    {"board": "③ 最小可行形式", "say": "每节结束写 3 条要点 + 1 个自问题；下次课开头先答这道题再翻笔记。", "misconception": "把笔记抄得更漂亮"},
                    {"board": "④ 与错题配合", "say": "答不出来的那一句就是错步，单独记进复习队列，几天后再考一次。", "misconception": "只复习已经会的部分"},
                ],
                "checkpoint": {
                    "question": "下面哪种行为真正用到主动回忆？",
                    "options": ["把重点用荧光笔标出来", "合上书默写本节三个要点再对照", "把课件重看一遍", "把板书拍照存好"],
                    "answer": 1,
                    "why": "只有「先自己提取、后对照」产生了检索动作；其余都是再输入。",
                    "wrong_step": 0,
                },
                "quiz": [
                    {"question": "重读带来的主要风险是？", "options": ["太慢", "熟悉感被误判为掌握", "伤眼睛", "记不住页码"], "answer": 1, "why": "fluency illusion。"},
                    {"question": "答错时最该做的是？", "options": ["跳过", "把该错步单独排进复习", "重抄整章", "换一门课"], "answer": 1, "why": "错步才是提分点。"} ,
                ],
            },
            {
                "id": "spaced-repetition",
                "title": "间隔复习 Spaced Repetition",
                "goal": "在快要忘的那一刻复习，而不是当天刷五遍",
                "cue": "同一个知识点，今天连着看 5 遍 vs 今天 1 遍、3 天后 1 遍、7 天后 1 遍——哪个更久？为什么？",
                "steps": [
                    {"board": "① 遗忘曲线", "say": "记忆在学完后衰减最快；每次成功提取会把曲线拉平一点，衰减变慢。", "misconception": "认为复习越密集越好"},
                    {"board": "② 理想时机", "say": "在「有点吃力但还能想起来」时复习收益最大；太早等于重读，太晚等于重学。", "misconception": "当天重复刷"},
                    {"board": "③ 简化 SM-2", "say": "答对 → 间隔按 1→3→7→16 天推进；答错 → 退回 1 天并标记错步。本应用就是这么排队的。", "misconception": "答错也继续拉长间隔"},
                    {"board": "④ 每天只做到期项", "say": "首页的「今日复习」只列 due 的知识点，做完即止，不制造额外负担。", "misconception": "把全部知识点每天过一遍"},
                ],
                "checkpoint": {
                    "question": "某知识点答错后，间隔应该怎么变？",
                    "options": ["继续拉长到 7 天", "保持 7 天", "退回 1 天并标记错步", "直接移出队列"],
                    "answer": 2,
                    "why": "答错说明提取失败，需要更近的再次尝试；本应用用这条规则驱动复习队列。",
                    "wrong_step": 2,
                },
                "quiz": [
                    {"question": "间隔复习里「最佳复习时机」是？", "options": ["刚学完立刻", "有点吃力但仍能提取时", "完全忘光后", "考试前一晚"], "answer": 1, "why": "desirable difficulty。"},
                    {"question": "本应用答对后的间隔序列是？", "options": ["1→2→3→4", "1→3→7→16", "1→5→10→20", "固定 3 天"], "answer": 1, "why": "简化 SM-2，见 ③。"},
                ],
            },
            {
                "id": "feynman",
                "title": "费曼式讲解法 Feynman",
                "goal": "用「讲给新生听」暴露自己以为懂了的地方",
                "cue": "试着不用课本里的术语，把链式法则讲给刚入学的新生。卡在哪一句？",
                "steps": [
                    {"board": "① 选一个概念，写在纸顶", "say": "只写一个，越具体越好；「微积分」太大，「链式法则」刚好。", "misconception": "一次讲一整章"},
                    {"board": "② 讲给完全不懂的人", "say": "禁用行话。被迫换成日常语言时，含糊处会立刻现形。", "misconception": "靠术语掩盖空白"},
                    {"board": "③ 卡住就回材料", "say": "卡住的那句就是错步，回到对应步骤重学，再讲一遍。", "misconception": "卡住就跳过"},
                    {"board": "④ 压缩成类比", "say": "例如「先拆洋葱，一层一层各自处理，再把结果乘起来」——能讲出类比，通常就真懂了。", "misconception": "只把原文缩短"},
                ],
                "checkpoint": {
                    "question": "费曼法里「卡住」应该被当成？",
                    "options": ["失败，换题", "定位错步的信号，回材料重学", "记性差", "术语不够"],
                    "answer": 1,
                    "why": "卡住正是这个方法的价值所在。",
                    "wrong_step": 2,
                },
                "quiz": [
                    {"question": "讲解时禁用术语的目的是？", "options": ["显得更专业", "暴露含糊处", "缩短时间", "方便背诵"], "answer": 1, "why": "换不出日常语言 = 没真懂。"},
                    {"question": "⑤ 里「压缩成类比」主要验证？", "options": ["字数变少", "能否脱离原句重建结构", "记忆速度", "排版好看"], "answer": 1, "why": "重建而非复述。"},
                ],
            },
        ],
    },
]


def list_courses() -> list[dict]:
    """给前端的课程清单（不含题目内容，避免提前泄答案）。"""
    return [
        {
            "id": c["id"], "title": c["title"], "description": c["description"],
            "icon": c["icon"],
            "topics": [
                {"id": t["id"], "title": t["title"], "goal": t["goal"],
                 "step_count": len(t["steps"])}
                for t in c["topics"]
            ],
        }
        for c in COURSES
    ]


def get_topic(topic_id: str) -> dict | None:
    for c in COURSES:
        for t in c["topics"]:
            if t["id"] == topic_id:
                return {**t, "course_id": c["id"], "course_title": c["title"]}
    return None


def all_topic_ids() -> list[str]:
    return [t["id"] for c in COURSES for t in c["topics"]]
