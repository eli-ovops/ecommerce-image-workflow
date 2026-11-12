import AppKit
import CoreImage
import Foundation
let dir=URL(fileURLWithPath:CommandLine.arguments[1],isDirectory:true)
let base=CIImage(contentsOf:dir.appendingPathComponent("实拍主体_暖白合成验证.jpg"))!
let retouch=CIImage(contentsOf:dir.appendingPathComponent("实拍回源_按键手柄修饰候选.jpg"))!
let w=base.extent.width, h=base.extent.height
let overlay=retouch.transformed(by:CGAffineTransform(scaleX:w/retouch.extent.width,y:h/retouch.extent.height))
let mask=NSImage(size:NSSize(width:w,height:h)); mask.lockFocus()
NSColor.black.setFill(); NSRect(x:0,y:0,width:w,height:h).fill()
NSColor.white.setFill()
NSBezierPath(roundedRect:NSRect(x: w*0.436,y:h*0.212,width:w*0.09,height:h*0.36),xRadius:18,yRadius:18).fill()
mask.unlockFocus()
let m=CIImage(data:mask.tiffRepresentation!)!.applyingFilter("CIGaussianBlur",parameters:[kCIInputRadiusKey:5]).cropped(to:base.extent)
let result=overlay.applyingFilter("CIBlendWithMask",parameters:[kCIInputBackgroundImageKey:base,kCIInputMaskImageKey:m])
let ctx=CIContext();let rep=NSBitmapImageRep(cgImage:ctx.createCGImage(result,from:base.extent)!)
try rep.representation(using:.jpeg,properties:[.compressionFactor:0.96])!.write(to:dir.appendingPathComponent("实拍主体_按键手柄修饰_无字.jpg"))
