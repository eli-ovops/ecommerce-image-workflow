# 造型重做批次独立QA

当前仅准备接收候选，reviews为空，不预填通过。旧32及旧24包不计本轮几何合格。

逐张实际查看新图、本SKU实拍及对应原始参考，分别记录：头/颈/柄连续曲率、头面与柄轴关系、浅背弧、侧壁厚度分布；参考五轴；商品细节/文案/水根水型/人物皮肤及手部；SHA与实际尺寸。近正面不可见的深度几何明确LIMITED_VIEW/UNKNOWN，不冒充完整3D核验。

保留兼容reviews数组，每图id/revision/image_path/sha256/actual_dimensions/overall_status/reference_fidelity五项和merged_tasks_coverage；四项合并D01→D02、D07→D10、D11→D09、V01→V07须实际核子段。74参考全读复用本批记录，每张仅定向相关原图。不把旧QA通过继承为新几何通过。

用户验收PENDING；实际模型/effort UNKNOWN。QA Owner只写本文件与qa-review.json，不改manifest/生成文件。

## 首批三SKU及清洁身份母版
实际看三成品、各自89/102/106实拍和A002/003/004原参考；K01/K02/K03均PWL，1254²，完整SHA见JSON。头颈柄可见缓曲/厚度连续，近正面背弧与全夹角仍LIMITED_VIEW；三色光泽、下键及裸纹对应正确，未见明确长白柱。蓝弧台/左白字右完整品保留，参数/6档/附件等删为SKU低密度适配。
M001-clean-v1实看三格及脸颈放大，PWL可作为身份/肤质输入，无明显旧密集闭合鳞网；只记support_asset_reviews，不计32成品。后续逐张人物仍需新核。用户验收PENDING。

## D12 / D15 / V03 v1新几何QA
实际对照新侧照/银89–92及A022/A027/R027/R029。D12 PWL：正背完整同尺度，几何深度LIMITED_VIEW。D15 PWL：纯侧小窗/浅背弧/壳颈可见连续曲率，四窗是外观适配；背面整体标签漏渲染已报root。V03 NEEDS_FIX仅前面板红钮右上约255,716封闭暗灰伪孔（3x内存核实），三视几何及黑金参考层次可用，定向清伪孔不重做。
三图完整SHA/五轴及局限见JSON，不继承旧几何通过。

## 六张新人物图集中QA
M06/D04 PWL，当前可见曲率/厚度过渡、皮肤及水源可用，不借旧QA作为新几何通过。
D01 NEEDS_FIX仅上面板一圈白孔破碎/灰闭合圈；D11 NEEDS_FIX仅下段右柄尾画内裸口流水；V01/V02 NEEDS_FIX额颊闭合多边鱼鳞重复，需要fresh。均已集中报root，不反复扩大修复。
D01合并D02、D11合并D09、V01合并V07，已实际核对应独立子段完整，状态与tasks保留。全SHA/尺寸/五轴/局限见JSON。其他detail已由独立water QA接管，已有D12/D15/V03记录保留，不重复。

## qa_closeout增量独立核验

继承本批74全读记录，实际查看本张原生、相关参考原图及银色实拍89/91/92/95/99、新侧照三张与feedback02。完整3D未核，不降低商品孔位/水流/人物门槛。

- M01 `rebuild-main/M01-v1.png`：PASS_WITH_LIMITATIONS — 低白环、红钮与银下键完整，未见明确碎裂/灰伪孔；当前正斜投影不验证全背弧。
- M02 `rebuild-main/M02-v1.png`：NEEDS_FIX — 主面板红钮右上及左下各有暗灰闭合伪孔，必须清除。
- M03 `rebuild-main/M03-v1.png`：PASS_WITH_LIMITATIONS — 背壳无圆patch，银裸牙、连续颈收腰可读，白孔不见明确增构；按压窗不证明清洁效果。
- M04 `rebuild-main/M04-v2.png`：NEEDS_FIX — 喷雾与混合六点被画成明显加大白环及黑色凸套，偏离feedback02普通孔根部；常规右边仍有连续干白孔。
- M05 `rebuild-main/M05-v1.png`：PASS_WITH_LIMITATIONS — 短小红点局部伸出，白孔为低环未见长白柱，红钮手动动作合理；柄背投影LIMITED_VIEW。
- M07 `rebuild-main/M07-v2.png`：PASS_WITH_LIMITATIONS — 白孔可见连续水束覆盖，无明显半面干孔；红钮只是前景水束掠过，无明确从中心喷出，柄端出框。
- M08 `rebuild-main/M08-v3.png`：NEEDS_FIX — 左常规面板右侧多排白孔无水，存在半面干孔。
- D01 `rebuild-people/D01-root-v2.png`：NEEDS_FIX — 上面板白孔碎裂粘连、灰伪孔成簇仍在，尤其红钮左上及周边。
- D11 `rebuild-people/D11-root-v2.png`：NEEDS_FIX — 上下常规头右侧/上缘存在大片连续干白孔，3x放大确认；下柄已自然出右框，仅此点修复通过。
- V02 `rebuild-people/V02-rebuild-v2.png`：NEEDS_FIX — 商品红钮上方的白孔多处断裂并混入灰伪孔，需修面板。
- D06 `rebuild-detail/D06-v2.png`：PASS_WITH_LIMITATIONS — 主面板全范围白孔可见水根，红钮无明确出水；底低角度银侧壁厚度与颈缓曲可读，水束高光不当塑料柱，仍不测精确孔数。
- D16 `rebuild-detail/D16-v2.png`：NEEDS_FIX — 左主面板右上可见灰伪孔；底常规索引窗孔位碎裂/灰点明显，需修对应面板。
- V03 `rebuild-detail/V03-v2.png`：NEEDS_FIX — 约255,716处暗灰闭合伪孔依然可见，旧问题未消除。
- V04 `rebuild-detail/V04-v2.png`：PASS_WITH_LIMITATIONS — 低白环带少量短红点，中央手按，底三步无过长针/自动效果；当前头部近景LIMITED_VIEW全柄深度。
- D14 `rebuild-detail/D14-v1.png`：PASS_WITH_LIMITATIONS — 红点/短针只少量孔伸出，不做长针；低白环与外孔圈保留，非精确针数量核验。
- V05 `rebuild-detail/V05-v1.png`：PASS_WITH_LIMITATIONS — 白孔低环，黑面细微高光不见明确闭合灰伪孔，银裸牙及侧窗缓曲可读；正斜主图全3D未知。
- V01 `rebuild-people/V01-rebuild-v2.png`：NEEDS_FIX — 持品尾端出现编织软管，不符不售配件；额颊有可见闭合细纹网络，肤质需改善。

## qa_closeout增量独立核验

继承本批74全读记录，实际查看本张原生、相关参考原图及银色实拍89/91/92/95/99、新侧照三张与feedback02。完整3D未核，不降低商品孔位/水流/人物门槛。

- D03 `rebuild-detail/D03-v2.png`：NEEDS_FIX — 三色面板均有暗灰闭合伪孔与白孔断裂，需分别清除，不能银色一键换色。
- D05 `rebuild-detail/D05-v2.png`：PASS_WITH_LIMITATIONS — 白孔连续低环、水束可见跨全面覆盖；底侧背浅S过渡、无背圆patch、银裸牙正确；不测精确孔数。
- D07 `rebuild-detail/D07-v3.png`：NEEDS_FIX — 主面板红钮右上白孔粘连断裂/灰闭合伪孔，需修主面板。
- D08 `rebuild-detail/D08-v2.png`：NEEDS_FIX — 第二喷雾窗除六锥雾外还从多普通孔连续发出直水束，成为混合，与喷雾档不符。
- D13 `rebuild-detail/D13-v2.png`：PASS_WITH_LIMITATIONS — 主及三窗白孔低环无明确灰伪孔或长柱，银裸牙可读，正斜角LIMITED_VIEW全背弧。
- D17 `rebuild-detail/D17-v2.png`：NEEDS_FIX — 主面板上部多处暗灰闭合伪孔，定向2x放大明确，不是高光阴影。
- D18 `rebuild-detail/D18-v2.png`：NEEDS_FIX — 主面板红钮左下及右上多暗灰伪孔/白孔碎裂。
- V06 `rebuild-detail/V06-v2.png`：NEEDS_FIX — 六格左下面板孔位窗大量白孔碎裂及灰伪孔，左上正面小窗同类。

## 增量3：面板修复及连带检查

- M02 `rebuild-main/M02-v2.png` PASS_WITH_LIMITATIONS — 主面板两个灰伪孔消除，低白孔黑底连续；双细节窗/银裸牙/版式保留。
- D01 `rebuild-people/D01-root-v3.png` PASS_WITH_LIMITATIONS — 上面板重建规则低白孔，碎孔与灰伪孔消除；人物肤质及下独立风发段保留。
- V02 `rebuild-people/V02-root-v3.png` PASS_WITH_LIMITATIONS — 面板清晰低白孔黑底，不见先前碎裂伪孔；肤质复用上次PWL。
- V03 `rebuild-detail/V03-v3.png` NEEDS_FIX — 255,716处闭合暗灰圈仍明确保留；其他若干灰圈变金棕面板斑，与黑底不连续。
- D16 `rebuild-detail/D16-v3.png` PASS_WITH_LIMITATIONS — 主面板与底三个索引窗低白孔规整，灰伪孔碎孔修复；干态三档仅索引。
- D18 `rebuild-detail/D18-v3.png` NEEDS_FIX — 红钮左下约434,417仍有明显灰白立体伪孔，定向3x放大确认，其他灰圈有部分残留。
- V06 `rebuild-detail/V06-v3.png` PASS_WITH_LIMITATIONS — 主品及正面/孔位窗重建低白孔，灰伪孔碎孔消除；顶部由背面变正面持品为可见适配，夜蓝大景、六格与问答任务保留。
- D08 `rebuild-detail/D08-v3.png` NEEDS_FIX — 第二窗普通孔根仍有连片短直水线残留，长直束虽减少，六雾根以外孔根未完全干净，需只清孔根残线。
- D03 `rebuild-detail/D03-v3.png` NEEDS_FIX — 三个SKU主面板多处暗灰伪孔仍留，孔根周边白碎点未全去。
- D07 `rebuild-detail/D07-v4.png` PASS_WITH_LIMITATIONS — 主面板重建低白孔黑底，未见灰伪孔/碎孔，完整侧面浅S与底双操作窗保留。
- D17 `rebuild-detail/D17-v3.png` PASS_WITH_LIMITATIONS — 上下两品面板均规则低白环黑底，闭合灰伪孔消除，石材静物双段和银裸牙保留。

## 增量4

- D18 `rebuild-detail/D18-v4.png` PASS_WITH_LIMITATIONS — 434417伪孔替换正常白孔；其余为相邻低环的自然投影，未见明确独立伪孔。
- D08 `rebuild-detail/D08-v4.png` PASS_WITH_LIMITATIONS — 第二窗普通孔根短直残线清除，仅六点锥雾、红钮干；上下常规与混合保留。
- D03 `rebuild-detail/D03-v4.png` NEEDS_FIX — 黑约329447/银约592292/枪灰约865664等仍有独立暗灰闭合圈，并非每颗白环统一投影。

## Additional native incremental QA

- M08 `rebuild-main/M08-v4.png` PASS_WITH_LIMITATIONS - 左窗右侧连续孔根已见水束，无大片干孔；其余两卡保持。
- D03 `rebuild-detail/D03-fresh-v5.png` PASS_WITH_LIMITATIONS - 新三SKU面板低白环规则，无明确灰伪孔碎裂；实看银89/黑102/枪灰106本色核对，光泽色差合理；浅蓝越框三完整品任务保留，三色标签位置稍改。
- V01 `rebuild-people/V01-fresh-v3.png` NEEDS_FIX - 中左细节窗中央红钮误为无中孔平红圆，白孔右边缘碎裂；主场景肌肤为水滴水膜，无明显闭合鱼鳞；无软管，主水根充分，侧颈自然，三窗与V07桥完整。
- M04 `rebuild-main/M04-v3.png` NEEDS_FIX - 六雾根仍有明显黑色凸套环与约普通孔1.5至2倍白口，新增硬件感；需普通白孔根雾化。
- D11 `rebuild-people/D11-root-v3.png` NEEDS_FIX - 上头右上约三分之一可见面板连续白孔仍无水，3x确认，不能用微光代水束；下柄已出框。
- V03 `rebuild-detail/V03-v4.png` NEEDS_FIX - 同255716暗灰闭合圈仍清楚保留，3x确认非相邻白环统一阴影。

## Additional native incremental QA

- V01 `rebuild-people/V01-root-v4.png` NEEDS_FIX - Red-button center aperture restored. Left detail window still has disconnected white fragments and merged lower-row outlets, confirmed native and 3x; not consistent oblique ellipse projection. Only this detail window needs repair; portrait skin/water/geometry/other windows/V07 bridge retain prior PWL.

## Additional native incremental QA

- V03 `rebuild-detail/V03-fresh-v5.png` PASS_WITH_LIMITATIONS - Fresh original-source rebuild: regular low white eyelets and black face, no explicit false gray holes; red annular center and lower silver key retained. Complete front/side/back with silver threads, continuous shallow S neck and clean shallow back. R027/R029 black-gold diagonal light, blue edge and three-view task retained; layout positions changed slightly. Side leader endpoint has a small visible gap, no structural or factual claim. Full 3D remains unverified.

## Additional native incremental QA

- M04 `rebuild-main/M04-fresh-v4.png` PASS_WITH_LIMITATIONS - Fresh ordinary eyelet mist roots without enlarged black collars; six separated cones in middle and mixed cones plus regular streams below, regular flow visible across white outlet field. Red center has no explicit source stream. Warm brown right handheld/left three windows preserved; gold outlined card labels replace earlier white labels, visible styling adaptation within R002 task.
- D11 `rebuild-people/D11-root-v4.png` PASS_WITH_LIMITATIONS - Only heads changed to narrow oblique side view. Visible narrow outlet field has continuous regular-flow roots without a dry half; hidden holes cannot be verified (LIMITED_VIEW). Continuous shallow back/neck/handle curve, no abrupt L. Both independent woman scenes and lower handle exiting right remain; skin previous PWL retained.

## Additional native incremental QA

- V01 `rebuild-people/V01-root-v5.png` PASS_WITH_LIMITATIONS - Left window now a tight central red annulus with open center and about six surrounding low white eyelets; no fragmented eyelets. Main portrait water-film contrast changed despite lock request, so unchanged pixels are NOT claimed. Native and 3x collateral review shows irregular water drops/film flow-lines of varied sizes rather than regular closed fishscale repeats; PWL. Main regular water roots, continuous curved neck, no hose, other two windows and independent V07 bridge remain.


## 2026-10-23 视频校准增量

D04、D06、D11按新视频及本SKU实拍修订，原生同SHA独立核验通过且保留限制。D04/D11为原M001新生成，未复用损坏人物场景。其余29张JPG未改；M03/D15/V01/V06仍待客户核对。当前不是客户最终验收。详见video-geometry-review及video-geometry-repair独立记录。
