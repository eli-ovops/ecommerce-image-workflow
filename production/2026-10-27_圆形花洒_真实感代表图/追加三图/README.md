# 圆形花洒｜追加细节图

2026-10-27，延续已认可暖白石材、铜棕标题带及实拍分层方向。本轮新图供用户审阅；前一张获认可不代表新图客户验收。

| JPG | 内容 | 实际商品像素来源 |
|---|---|---|
| A_下键切档.jpg | 下方切档键，普通／喷雾／混合 | 350原照轮廓、黑面板及孔位；银面内部和按键银面用单次imagegen反射候选局部合成 |
| B_红钮细节.jpg | 中央红钮与真实孔口微距 | 348原照等比裁切，没有生成商品像素、按压动作或虚构红针 |
| C_圆盘厚边.jpg | 斜正面完整圆头、圆柱银边 | 345原照头部整体等比旋转与裁切，全部可见商品来自原照，无反射重绘；下柄自然出画 |

均为1440×1440，每张选定JPG仅导出一次。只交上述JPG；源PNG是内部制作资料。统一四张总览与包由root处理，本目录不另建包。

## 可编辑源与复做

A/B/C-editable.svg内嵌背景、商品、mask与独立中文文字。A-product-mask.svg保存轮廓；A-reflection-mask.svg保存反射替换区，合成时2px羽化；B的矩形微距窗口在SVG内。C345-product-mask.svg保存当前C商品轮廓。C-product-mask.svg和C-reflection-mask.svg属于弃用342路线，不能用于当前C。

build.js只生成A/B；build-C.js生成当前345版本C。export.js带防覆盖保护，已有JPG不再导出。使用已有Node、Sharp、Heiti SC字体，没有安装依赖或Python像素编辑。商品没有镜像、拉长或分开改变头柄比例。

sources/original-*.jpg为原件副本；A-photo.png、B-photo.png及C345-photo.png仅规范EXIF方向和等比尺寸。sources/A-retouch.png是A所选反射候选。sources/background.png复用前一张的独立AI背景；没有新生成背景。prompts.json保留本轮调用文本，manifest.json记录原生路径、源哈希、检查和限制。

## 弃用证据

343整件侧视下沿粉红条经原照局部放大证实是实际手指遮挡；没有重绘被遮挡几何。相关源、反射候选及预览保留为sources/C343-rejected-*，证据为C-edge-inspection.png。

342局部窗口虽然避开遮挡，但形成狭窄银条、头颈识别弱，root未放行；保留sources/C342-rejected-*和旧C-photo.png/C-retouch.png。以上两次角度各一次imagegen候选均未进入当前C，停止该路线后采用345原照，无新增调用。

## 检查与边界

实际查看350、351、348、342、343、345及各选定预览与360px手机缩略。A按root意见恢复完整下键与周围黑边；A/B最终JPG已实际打开并经root复核。C原照外手部排除，头部完整，黑面板、孔序、红钮和银边均来自345。C仅展示头部与厚边，不代表完整侧面、全柄或新的几何验收。

A有窄小原暖色边缘反光。C银边保留真实房间彩色反射及下段暖肤色镜面反射，未声称已消除环境；可见镜面内容是本图局限。B是静态结构，不证明按压、红针伸出或除垢效果。所有实拍层都经历缩放、插值和JPG编码，A还有明确反射重绘区，不称整件原像素硬锁。

此前认可主图字节保持，SHA256为66ed25f685db7bd1a9523a6a25c501ecb336dead7f957e4cc1ed362a55c2bea4。原件、模型、父级成果未修改；未删除、发布或外发。只写本子目录。

规则PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-27-v7 / TOKEN-BUDGET-2026-10-25-v2。请求gpt-6-astra / medium；实际运行model/effort为UNKNOWN。

收口：root已实开C345预览放行供用户审阅；C最终JPG随后一次导出并实际打开检查。三张均完成，客户接受仍UNKNOWN。
