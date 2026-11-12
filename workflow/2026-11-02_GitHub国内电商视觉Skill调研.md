# GitHub 国内电商图片与视觉 Skill 定向调研

日期：2026-11-02。用户要求寻找淘宝、拼多多电商图审美相关 Skill；本次只读检索、视觉查看公开示例，没有安装、运行第三方技能、上传用户素材或重新作图。

## 问题与证据

用户希望保持所给13张同款同行参考图的广告风格、构图与光影，替换商品和模特。当前顶喷图的用户反馈是字体不行、商品像实拍抠贴、缺少电商感；用户认可部分场景可复用。图中的喷孔、盲点、叶片纹和银色主体应以本品实拍为准，用户确认约30×20×2厘米；示意水流不代表实测水量。

## 实际检查的项目

### 1. QIYU Codex 电商生图工作流：优先参考拆图规则

- [项目说明](https://github.com/QIYU-JACKMAN/codexQIYU-image-workflow)；[一比一复刻 Skill](https://github.com/QIYU-JACKMAN/codexQIYU-image-workflow/blob/main/ecommerce-image-workflow%202/skills/ecommerce-exact-replication/SKILL.md)；仓库内MIT许可证。
- 实读Skill全文和README：Image 1为参考构图，其他图为商品事实；分别拆镜头、光色、版式、标题层级、主体比例，生成后同时检查参考相似度及商品真实性。此仓库树中没有检索到成图示例，本次未实测；“一比一”为作者对工作流的命名，并非已证明逐孔硬锁。
- 与本项目已有 `ecommerce-image-workflow` 名称冲突，不直接覆盖或安装。其确认提示词/计划的步骤不覆盖用户在当前项目已明确授权的常规自主制作；返修回源规则优先于其重画说法。

### 2. 电商美工技能包：优先参考视觉诊断和拆图

- [仓库](https://github.com/along-ai-tech/ecommerce-design-skill-pack)；[竞品主图与详情诊断 Skill](https://github.com/along-ai-tech/ecommerce-design-skill-pack/blob/master/skills/01_%E5%93%81%E7%89%8C%E4%B8%8E%E8%A7%86%E8%A7%89%E5%AE%9A%E4%BD%8D/%E7%AB%9E%E5%93%81%E8%AF%A6%E6%83%85%E9%A1%B5%E8%A7%86%E8%A7%89%E6%8B%86%E8%A7%A3/SKILL.md)；[主图 Skill](https://github.com/along-ai-tech/ecommerce-design-skill-pack/blob/master/skills/05_%E8%AF%A6%E6%83%85%E9%A1%B5%E6%8B%BC%E5%90%88%E5%88%B6%E4%BD%9C/%E4%B8%BB%E5%9B%BE%E5%A5%97%E7%89%88%E6%8E%92%E7%89%88/SKILL.md)。MIT。
- 实读两份Skill。前者要求看主体、卖点、缩略图、分屏和图序；后者强调不同图有不同任务和单变量比较。该包有外部 dLazy API 以及上传本地文件/积分的路径，本次未使用。其预设的主体比例、标题组数和评分是作者经验，不是用户指定版式或平台规则；不以虚构点击率/客观分数替代目视验收。
- GitHub树未发现该仓库内展示的图片成果，本次仅核文本和仓库说明，未验证其生图质量。

### 3. KeRo SKU Skill：平台任务与产品事实检查

- [仓库](https://github.com/Youks7/SKU-skill)；[淘宝](https://github.com/Youks7/SKU-skill/blob/main/skills/sku-taobao/SKILL.md)；[拼多多](https://github.com/Youks7/SKU-skill/blob/main/skills/sku-pinduoduo/SKILL.md)；[9:16淘宝示例](https://github.com/Youks7/SKU-skill/blob/main/examples/taobao-9-16-detail-page.md)。
- 实读产品事实、两平台技能和示例。它区分主图、轮播、SKU、详情等任务，并强调不同视角及产品事实一致；检查的淘宝示例是文字示例，不是实际展示的电商图。许可证文件为CC BY-NC 4.0，对商业用途适配需另行确认；不安装或直接复制规则用于商业成品。项目现有流程已有类似事实保护与构图对应原则。

### 4. dLazy 电商视觉技能库：提供公开示例，但风格不是本品标准

- [仓库](https://github.com/dlazy-ai/ecommerce-skills)；[商品卖点主图Skill](https://github.com/dlazy-ai/ecommerce-skills/blob/main/skills/item-selling-point/skill.md)。MIT；作者的执行示例通过dLazy账号与积分调用外部生图服务。仅阅读与查看，不运行、不上传素材。
- 实际打开作者三张图片：鞋子卖点主图、毛衣详情图、服装咖啡馆场景；前两张的产品、标题、卖点分区清晰，第三张场景光色统一，但画风偏简洁棚拍/服装，与用户给的顶喷黑金/蓝色浴室、强水幕、中文促销字效不是同一视觉目标。不能将作者声称的参考细节完全一致当作本品逐孔证据。
- 链接：[鞋子主图示例](https://github.com/dlazy-ai/ecommerce-skills/blob/main/docs/item-selling-point/example-output.jpg)、[毛衣详情示例](https://github.com/dlazy-ai/ecommerce-skills/blob/main/docs/item-detail/example-output.jpg)、[服装场景示例](https://github.com/dlazy-ai/ecommerce-skills/blob/main/docs/creative-scene/example-output.jpg)。项目还包括与本次无关的水印处理技能，本次不使用。

### 5. 其他筛选

- [Beatra product-photo-studio](https://github.com/beatra-ai/ai-product-photography-skill)：作者展示原图到商品摄影方案，但实际渲染需Beatra账户/积分，本次不调用。
- [E-commerce Detail Page Generator](https://github.com/Gayaya999/ecommerce-detail-page-generator)：详情页叙事、独立文字排版、切片与交付检查；本次阅读README，未运行。平台规则表属于项目自述，未核验当前后台，不作为平台规定。
- [ecommerce-visual-planning](https://github.com/forest-USTC/ecommerce-visual-planning-skill)：策划与证据/风格锁；与本地现有 `ecommerce-visual-copywriting` 职责高度重叠，不因再装一份就具备新的渲染或审美能力。

## 对当前13图的具体改变

不是再选一个统一模板：按参考图逐张建立视觉对应与比例卡，用户确认的产品实拍负责身份，参考负责镜头、光色、字效和商品摆放，复用已认可的现有场景层。

以388为例：参考主体是顶部横向大顶喷、水帘占画面中部、中央大号白字红描边、左下斜放商品、底部浅米色信息带；当前返修顶部仰角和细线水流与参考不同，左下主体轮廓、对比与接地感不足，文字和小窗比例也应与原参考同尺度检查。水流不得再用密集白线当完成；商品真实喷孔的照片/模型层与水流层分别可审阅。

以392/395为例：参考以大斜置面板、密集短针的提拉状态、主标题与局部功能放大为叙事重点；已有图实际只是静态面板加实拍细节小窗。真实针长与位置应以382实拍为准，不能将长红锥及未知内部剖面当作事实。真实完整提拉素材不足时明确该画面尚未验证。

以391/394为例：参考是大幅仰拍安装、水幕与人物共同参与；当前图水线覆盖人物但无真实接触，且多个安装图重复同一机位。场景认可只代表背景方向认可，不代表产品和水流通过。

实际生产时先做逐张参考与成图并排，以产品轮廓/喷孔及动作真实为底线，同时检查文字对比、水流与人物遮挡、环境光、移动端缩略图；不以文件齐全或主观分数宣称审美合格。不做未证实的AIR结构、360度、增压倍数或厂家孔数承诺。

## 检索记录与限制

`agent-reach doctor --json` 显示GitHub `gh CLI`可用。实际检索词包括：`淘宝 电商 主图 skills`、`拼多多 电商 设计 skill`、`电商 图片 生成 skill`、`ecommerce product image design agent skill`、`taobao product image prompt skill`，以及网页搜索的 `github 电商 主图 详情页 设计 skill 淘宝 图片 生成 SKILL.md` 等。检查了7个项目的仓库元数据，实际阅读上列Skill与相关文档、查看3张dLazy示例图。`gh api` 下载二进制图像出现 `transform: short source buffer`，后通过公开仓库 raw 图片读取成功；未遇权限拒绝。

GitHub项目、作者示例和星标不证明在本商品的效果；没有实跑、没有独立验证目标平台规范或任何商业转化结果，也不能保证逐孔一致。本次只给出可借鉴的方法，不改原项目规范和图组。
