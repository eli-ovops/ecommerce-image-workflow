# 圆形花洒三维电商续图（审阅样图）
新增 D/E/F，合并已交 A/B/C 共六张 1600×1600 JPG。旧三张字节不变。

商品来自 sources/baseline.blend（已确认材质精修资产），完整 Blender 场景渲染，无 AI 像素、实拍抠层、人物或水流。未修改商品网格/孔位/局部比例；E 为共同刚体翻面与落地平移，D/F 仅相机与场景。白接口以机位出画/前景石台遮挡，几何保留。

复现：Blender 5.2.2 `-b --python render.py -- final`；`swift outline.swift <本目录绝对路径>`；`node layout.js final`；Blender `-b --python audit.py`；`python3 package.py`。layout.js 依赖现有 Sharp，路径见脚本，字形已以 SVG 路径保存，正常导出无需字体。修改文字后重新运行 Swift（macOS PingFangSC-Semibold）。最终 scene.blend 可独立打开，SVG 内嵌渲染底图。

来源、SHA 与检查范围见 manifest.json / saved-model-audit.json。当前仅样图：背面大反射梯度已有改善，颈部仍有源曲面分段高光，整体有 CG 感；实拍参考未相机标定，模型不是尺寸或精密几何真值。F 仅静态控件，不表示按压测试或清洁效果已验证。未扩完整套图，用户/客户接受 UNKNOWN。
