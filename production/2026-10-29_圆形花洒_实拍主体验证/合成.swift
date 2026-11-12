import AppKit
import CoreImage
import Foundation
let dir=URL(fileURLWithPath:CommandLine.arguments[1],isDirectory:true)
let base=CIImage(contentsOf:dir.appendingPathComponent("AI外围背景.png"))!
let photo=CIImage(contentsOf:dir.appendingPathComponent("原始实拍_359.jpg"),options:[.applyOrientationProperty:true])!
let w=base.extent.width, h=base.extent.height
let scaled=photo.transformed(by:CGAffineTransform(scaleX:w/photo.extent.width,y:h/photo.extent.height))
let mask=NSImage(size:NSSize(width:w,height:h)); mask.lockFocus()
NSColor.black.setFill(); NSRect(x:0,y:0,width:w,height:h).fill()
NSColor.white.setFill()
let p=NSBezierPath(roundedRect:NSRect(x:w*0.12,y:h*0.10,width:w*0.75,height:h*0.84),xRadius:140,yRadius:140);p.fill();mask.unlockFocus()
let maskCI=CIImage(data:mask.tiffRepresentation!)!.applyingFilter("CIGaussianBlur",parameters:[kCIInputRadiusKey:40]).cropped(to:base.extent)
let blended=scaled.applyingFilter("CIBlendWithMask",parameters:[kCIInputBackgroundImageKey:base,kCIInputMaskImageKey:maskCI])
let context=CIContext(); let cg=context.createCGImage(blended,from:base.extent)!
let rep=NSBitmapImageRep(cgImage:cg);let jpg=rep.representation(using:.jpeg,properties:[.compressionFactor:0.95])!
try jpg.write(to:dir.appendingPathComponent("实拍主体_暖白合成验证.jpg"))
