# B面板清洁

仅清理用户红圈的3处面板水渍，沿B修订版保持标题、布局、商品比例和孔位。标注截图保存于sources/user-circles.png；查看截图、原339及B最终图后，目标定位约(520,905)、(653,1085)、(548,1285)。具体范围与取样位移见patches.json、clean-mask.svg。

一次内置imagegen生成候选，但第一处水渍仍在且纹理偏平，弃用，保留sources/candidate-native.png和prompt.txt。工具未提供硬mask，不称硬inpaint。经root授权改为SVG局部邻域原照纹理取样：仅3个小椭圆、2.1px羽化，保留黑色颗粒；无AI商品像素进入最终图。首次邻域取样误带入白孔缘，已纠正取样源并逐块放大检查，当前3处没有新增白孔。

B-clean-editable.svg内嵌原B及3块取样，build.js可重做，patches.json记录源到目标平移。不移动或重画孔口、红钮、外边；不磨平整张面板。sources/1/2/3-before.png与对应after.png是各110px区域4倍放大检查，候选检查也保留。最终图经历JPG编码，不宣称字节级全图不变。

后续同类实拍近景必须在出图前检查黑色面板水渍、指纹、灰尘与放大后显露的污斑；发现后只做保留孔位/纹理的局部清洁，再查取样源和目标是否混入孔缘、重复纹或接缝。清洁完成不能仅凭整体缩略判定。项目流程固化由root处理，本目录不修改全局或父级文件。

静态画面不证明按压动作或除垢效果。仅写本B清洁目录，原版及其他JPG不改。请求gpt-6-astra/medium，实际model/effort UNKNOWN。规则PERMISSIONS-2026-10-14-v1、ROUTING-2026-10-27-v7、TOKEN-BUDGET-2026-10-25-v2。

最终：B_红钮细节_清洁版.jpg，1440×1440；root核三块放大前后后一次导出，已实际打开最终JPG。合成前后差分见verification.json，JPG重编码差异另行区分。
