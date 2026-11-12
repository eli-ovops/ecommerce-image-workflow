# 单张水流 imagegen 实验（待审，真实感未通过）

本轮只尝试独立水层及单图合成，未改13张原包。主看 water-study.jpg；393-water-experiment.jpg 为回填原393布局的版本。water-study-before-after.jpg 左旧曲线、右生成水层；study-origins / study-droplets 的200pct文件是局部对照。

实际方法：原391 Blender场景隐藏水曲线，重新渲染干燥产品与管件；喷面继续使用原372实拍纹理。94个候选起点从原生场景投影，排除项沿用原记录，不是实测总孔数。将原生起点引导图和原393参考送入内置 imagegen，仅生成透明水幕（一次调用），未把任何上轮AI成品送回模型。prompt.txt为完整提示词。imagegen原生输出1254×1254 RGBA；water-generated-original.png完整保留。

原水素材偏密并有灰雾/暖色杂点，原生合成时统一去饱和、抑制灰雾、降低透明度，并按候选孔下方窄通道遮罩，得到water-masked.png。没有以新画直线替代生成水形。背景为此前获准复用的原始场景层，仅在本地合成，未再送模型。

产品保护范围：原生1200像素层上，99,153个不透明产品像素位于水通道外且逐像素不变。水通道内允许透明水层遮挡产品；因此不声称整件像素完全不变。模型银壳/红钮本来就是三维，非整件实拍像素。遮罩约束起点附近范围，不等于生成水流逐孔对齐；没有逐孔验证通过。

实际审图：下半段出现自然程度较高的断续水珠，较旧直线水幕明显丰富；但起点与水束仍有断接、部分水束偏粗和贴图感，喷面/金属仍有CG感。真实水型、流量、增压或AIR功能均未验证。当前结果只能作为方法实验，不是可直接交付客户的广告成品。

可编辑：water-study-editable.ora为背景/干产品/水三层；393-water-editable.ora为原布局全部层。dry-product.blend为可打开的本轮原生干模型，贴图已内嵌。water-origin-gate.png、product-protected-mask.png、projected-origins.json为遮罩和起点证据。prepare.py重渲染依赖项目原391源；compose.py依赖原393分层，独立打开ORA不依赖脚本。sources内有实际输入副本与哈希清单。未删除文件，全部为继续审阅所需。
