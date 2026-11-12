# 银色商品层来源与制作范围

2026-10-24。本轮源几何为用户已接受并授权使用的v010a；外观取银色SIL001–005。本目录只制作实际3D商品层，背景与最终中文排版由root另行合成。PNG与mask是内部透明生产层，最终用户交付由root导出JPG。

当前可编辑模型：`silver_product_v004.blend`。v001过亮、v002共享材质误染下按钮，均保留为过程；选定层为front3q/buttonclose-v004和不受影响的back3q/strictside-v003；以render-receipt.json为准。

## 真实来源

已实际打开银色manifest所列SIL001正面89、SIL002背面90、SIL003/004侧面91/92、SIL005近照93。源文件SHA与当前副本校验在`saved-model-verification-v004.json`；未使用旧生成商品图作为几何或孔位来源。

面板来自SIL001真实照片：先按EXIF正向缩放至1368×1824工作坐标，用已记录四个边缘锚点做平面投影校正至2048²。根据图中白色环的连通区域识别144处，逐点保存原投影坐标和映射后的面板位置，见`face-source-and-holes.json`与`hole-detection-evidence.jpg`。在这些真实位置增加浅白色环形几何，未随机或按预设规则造孔阵；外围密集暗孔沿用实拍纹理。144是本次识别的可见白环数，不作为商品规格宣称。

照片中的旧红按钮像素和原底影从面板纹理中央有限区域移除，当前由独立3D红色按压件显示；区域为校正图中心(1042,1065)、半径183像素，未覆盖周围白环位置。最初红像素清除与最终区域见prepare_face.py/finalize_appearance.py及两个版本纹理；v003过程曾因均匀清除区留下假黑底盘，最终face-photo-rectified-v003.png采用邻近实拍黑面48×48纹理补齐并14px羽化；供体与范围见central-cleanup-provenance.json，已打包入当前blend。

银色材质只是按实拍的银色反光进行视觉着色，不证明金属、不锈钢、镀层或工艺。黑色前颈饰面采用连续材质遮罩，银色下按钮材质独立。中央红件仍为除垢按压件，下方银键为切换三档。裸螺纹按用户明确的银色制作简化外观，不声称螺纹标准、精确牙形或通用适配。

## 保留与验证

主体几何与世界变换在保存重开后对照v010a；具体hash及body_geometry_unchanged见`saved-model-verification-v004.json`。没有改头部圆柱边、头颈曲率或下柄主网格，不把跨SKU物理同模具作为已验证事实。

Cycles、Metal GPU、96采样、去噪，2000×2000 RGBA16bit内部商品层。四个面光源与中性略冷环境实际照明；不是Workbench白壳。首帧Metal编译加渲染约2分48秒，后续暖缓存约十几秒。相机与每层hash由`render-receipt.json`绑定；`render-layers.json`记录alpha范围、商品像素包围盒与mask路径。灰底-review.jpg仅为审查预览，不是最终排版图。

本批均为干态单品，无软管、支架、人物或水流；水流、肤质检查不适用，不记为PASS。没有安装、上传、付费或imagegen调用。未修改已冻结v010a或root管理的文件。

路由沿用目标gpt-6-astra/high；实际model/effort/speed UNKNOWN。全部过程、脚本、源投影证据保留；render-process-sample.txt为首帧Metal编译等待的实际诊断记录，仍用于追溯，不删除。
