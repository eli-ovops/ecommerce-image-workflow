# D06本地分层水流首候选

底图 before-water/D06.png 未重绘，SHA256：9222db0321db291160281eebf831b659fb951601f17d6f84550fb759c244a1bb。

当前有效文件：composite.png、water-layer.png、water-allow-mask.png、diagnostic-ports.jpg、port-coordinates.json、pixel-protection-evidence.json、build_d06.py。

当前坐标上40/下12，限实看能可靠追踪的前排白孔；已有密水遮挡部分保留底图原水。不能声称所有白孔逐孔覆盖验收已完成，需独立QA给仍缺水的清晰孔位坐标。首次检测的upper-port-check.png/lower-port-check.png保留为失败定位诊断，含水线交叠假孔，不能作为当前坐标证据；当前诊断只认diagnostic-ports.jpg。

验证：水层以外像素变化0；上红钮核心变化0；上场景水层不越y1094、y1095—1189水层非零数0。图中商品没有重新生成或变形。水层在红钮及外圈微孔区被屏蔽，不从镀铬、按钮、黑微孔起水。此证据不替代独立视觉检查。

水层采用透明双细丝、轻微波动和断续高光，不使用不透明机械白杆。底图已有水不删，不覆盖final或exports。

独立QA定点续修：实际孔中心(713,1229)，并非非孔位置(696,1229)，与下方(715,1240)为不同孔；新增一根透明细水线。原候选保存为composite-v1.png等-v1文件。变化仅x710—718、y1228—1477共1038像素，上场景变化0。当前合成SHA256：7d4b331f9d04e15e2c547699c9f11e3129b4369eccb3d96967a8a8d22c21e14d。前后12倍裁图及QA-target-resolution.json为定点证据。
